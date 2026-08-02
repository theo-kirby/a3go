"""SYMM-1 arm A — test-time augmentation: average the EXISTING libs net over the
order-48 cube-symmetry group at every MCTS leaf, with NO retraining. If 3D Go's
big symmetry group denoises the policy/value the way dihedral-8 does in 2D, the
symmetry-averaged net should beat the plain net head-to-head — a free strength
gain attacking the 0.449->0.5 parity gap that capacity scaling could not close.

The libs config's planes are all spatial, geometric features (stones, stm,
liberty buckets), so they are exactly equivariant under the cube group — a
position and its 48 images are the same game state, so averaging is sound.

    uv run python symm_tta.py [n] [games_per_seedpair] [sims] [k_symms] [out.json]
    # k_symms <= 48 random group elements per eval (default 8); 0 => all 48
"""
from __future__ import annotations
import os, sys, json, time, random
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
import torch
torch.set_num_threads(1)

from a3go_engine import Board
from batched_az import BatchedMCTS, _apply_action, _winrate
from net_arch3 import A3GoNetIn
from input_planes import config_planes, n_planes
from cube_symmetry import GROUP, transform_planes, action_perm

CFG = "libs"
SEEDS = [0, 1, 2]
LOW_TEMP = 0.3
TEMP_MOVES = 6


class PlainMCTS(BatchedMCTS):
    def __init__(self, net, device, sims, seed=0):
        super().__init__(net, device, sims=sims, seed=seed)

    def _eval_batch(self, boards):
        if not boards:
            return None, None
        X = torch.from_numpy(np.stack([config_planes(b, CFG) for b in boards])).to(self.device)
        with torch.no_grad():
            logits, v = self.net(X)
        return logits.float().cpu().numpy(), v.float().cpu().numpy()


class SymmMCTS(BatchedMCTS):
    """Symmetry-averaged eval over k cube-group elements (per-board)."""
    def __init__(self, net, device, sims, seed=0, k=8):
        super().__init__(net, device, sims=sims, seed=seed)
        self.k = k
        self.n = None
        self._aperm = None

    def _ensure(self, n):
        if self.n != n:
            self.n = n
            self._aperm = {gi: action_perm(g, n) for gi, g in enumerate(GROUP)}

    def _eval_batch(self, boards):
        if not boards:
            return None, None
        n = boards[0].w
        self._ensure(n)
        gi_all = list(range(len(GROUP)))
        # choose k group elements (shared across the batch this round)
        if self.k and self.k < len(GROUP):
            gis = list(self.nprng.choice(gi_all, size=self.k, replace=False))
        else:
            gis = gi_all
        base = [config_planes(b, CFG) for b in boards]  # B x (C,n,n,n)
        B = len(boards)
        # Build batch B*len(gis) of transformed planes.
        stack = []
        for X in base:
            for gi in gis:
                stack.append(transform_planes(X, GROUP[gi]))
        Xt = torch.from_numpy(np.stack(stack)).to(self.device)
        with torch.no_grad():
            lg, v = self.net(Xt)
        lg = lg.float().cpu().numpy()
        v = v.float().cpu().numpy()
        A = lg.shape[1]
        out_logits = np.zeros((B, A), dtype=np.float32)
        out_v = np.zeros(B, dtype=np.float32)
        row = 0
        for bi in range(B):
            probs = np.zeros(A, dtype=np.float64)
            vacc = 0.0
            for gi in gis:
                l = lg[row]
                l = l - l.max()
                p = np.exp(l); p /= p.sum()
                probs += p[self._aperm[gi]]   # map g-frame policy back to orig frame
                vacc += v[row]
                row += 1
            probs /= len(gis); vacc /= len(gis)
            out_logits[bi] = np.log(probs + 1e-12).astype(np.float32)
            out_v[bi] = vacc
        return out_logits, out_v


def load_net(n, seed, device):
    net = A3GoNetIn(n, in_planes=n_planes(CFG), channels=64, blocks=6)
    net.load_state_dict(torch.load(f"best_arch3_{CFG}_s{seed}.pt", map_location=device))
    return net.to(device).eval()


def play_match(a, b, n, games, seed):
    rng = random.Random(seed)
    boards = [Board(n) for _ in range(games)]
    passes = [0] * games; done = [False] * games
    a_black = [g % 2 == 0 for g in range(games)]
    for ply in range(n * n * n * 2):
        for mcts, isa in ((a, True), (b, False)):
            turn = [i for i in range(games) if not done[i]
                    and ((boards[i].player == 1) == (a_black[i] == isa))]
            if not turn:
                continue
            temp = 1.0 if ply < TEMP_MOVES else LOW_TEMP
            noise = 0.25 if ply < TEMP_MOVES else 0.0
            pis = mcts.run_policies([boards[i] for i in turn], [passes[i] for i in turn],
                                    [temp] * len(turn), root_noise=noise)
            for k, i in enumerate(turn):
                _apply_action(boards[i], rng.choices(range(len(pis[k])), weights=pis[k])[0], n, passes, done, i)
        if all(done):
            break
    return _winrate(boards, a_black)


def wr_ci(wr, ndec):
    se = (wr * (1 - wr) / max(1, ndec)) ** 0.5
    return [round(wr - 1.96 * se, 4), round(wr + 1.96 * se, 4)]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    gp = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    sims = int(sys.argv[3]) if len(sys.argv) > 3 else 48
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    out = sys.argv[5] if len(sys.argv) > 5 else "symm1_tta.json"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    t0 = time.time()
    print(f"# SYMM-1 TTA n={n}^3 sims={sims} k={k or 48} gp/seed={gp} device={device}", flush=True)

    wtot = dtot = 0
    per_seed = []
    for s in SEEDS:
        symm = SymmMCTS(load_net(n, s, device), device, sims=sims, seed=100 + s, k=k)
        plain = PlainMCTS(load_net(n, s, device), device, sims=sims, seed=200 + s)
        wr = play_match(symm, plain, n, gp, seed=1000 + s)  # A = symm
        per_seed.append(round(wr, 4))
        wtot += wr; dtot += 1
        print(f"  seed {s}: symm-vs-plain winrate={wr:.4f} ({time.time()-t0:.0f}s)", flush=True)
    wr = wtot / max(1, dtot)
    result = {"experiment": "SYMM-1 arm-A cube-symmetry TTA inference (libs 5^3, no retrain)",
              "n": n, "sims": sims, "k_symms": k or 48, "games_per_seed": gp, "seeds": SEEDS,
              "symm_winrate_vs_plain": round(wr, 4), "per_seed": per_seed,
              "ci95": wr_ci(wr, gp * len(SEEDS)), "secs": round(time.time() - t0, 1)}
    json.dump(result, open(out, "w"), indent=2)
    print(f"symm-vs-plain pooled winrate = {wr:.4f} {result['ci95']}  (>0.5 => free strength)\nwrote {out}", flush=True)


if __name__ == "__main__":
    main()
