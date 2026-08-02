"""PROBE-1 — input-plane ablation attribution: WHICH liberty plane carries the
ARCH-3 +0.144 gain? Forward-pass + net-vs-net, no retraining.

The winning `libs` config feeds planes [0,1,2, 4,5,6] = black, white, stm, and the
three liberty buckets 1-lib (atari), 2-lib, >=3-lib. We take the trained libs nets
and, at INFERENCE only, zero one liberty plane at a time, measuring:

  Part A (no games, fast): on a held-out position set, the policy KL-divergence
  (ablated || full) and value MAE induced by each ablation -> how much the net
  *relies* on each plane.

  Part B (net-vs-net): full libs net vs ablated libs net, color-balanced, 3 seeds
  -> the strength cost of removing each plane (win rate of the full net).

Ablating 'all-libs' (zero 4,5,6 together) should reproduce the `base` net's
behaviour direction (libs gain removed); per-bucket ablations localize it.

    uv run python probe_ablation.py [n] [games_per_seedpair] [sims] [out.json]
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
from batched_az import BatchedMCTS, _apply_action
from net_arch3 import A3GoNetIn
from input_planes import config_planes, n_planes, CONFIG_CHANNELS, slice_stack

CFG = "libs"
SEEDS = [0, 1, 2]
LOW_TEMP = 0.3
TEMP_MOVES = 6
# stacked-row index of each ablatable channel within config_planes(libs) output.
# CONFIG_CHANNELS['libs'] = [0,1,2,4,5,6]; rows 3,4,5 are buckets 1-lib/2-lib/>=3-lib.
ABLATIONS = {
    "none":   [],
    "1lib":   [3],     # atari plane (ch4)
    "2lib":   [4],     # ch5
    "3plus":  [5],     # ch6
    "alllib": [3, 4, 5],
}


class AblMCTS(BatchedMCTS):
    def __init__(self, net, device, cfg, sims, seed=0, ablate=()):
        super().__init__(net, device, sims=sims, seed=seed)
        self.cfg = cfg
        self.ablate = list(ablate)

    def _eval_batch(self, boards):
        if not boards:
            return None, None
        X = np.stack([config_planes(b, self.cfg) for b in boards])
        if self.ablate:
            X[:, self.ablate] = 0.0
        Xt = torch.from_numpy(X).to(self.device)
        with torch.no_grad():
            logits, v = self.net(Xt)
        return logits.float().cpu().numpy(), v.float().cpu().numpy()


def load_net(n, seed, device):
    net = A3GoNetIn(n, in_planes=n_planes(CFG), channels=64, blocks=6)
    net.load_state_dict(torch.load(f"best_arch3_{CFG}_s{seed}.pt", map_location=device))
    return net.to(device).eval()


def part_a(n, device, npz="distill_arch3_5cubed.npz", n_pos=4000):
    """Forward-pass attribution: policy-KL + value-MAE per ablation, pooled over seeds."""
    d = np.load(npz)
    X_full = slice_stack(d["X"], CFG)
    rng = np.random.default_rng(0)
    idx = rng.permutation(len(X_full))[:n_pos]
    X = torch.from_numpy(np.ascontiguousarray(X_full[idx])).to(device)
    rows = {}
    for seed in SEEDS:
        net = load_net(n, seed, device)
        with torch.no_grad():
            base_logits, base_v = net(X)
            base_lp = torch.log_softmax(base_logits, 1)
            base_p = base_lp.exp()
        for name, abl in ABLATIONS.items():
            Xa = X.clone()
            if abl:
                Xa[:, abl] = 0.0
            with torch.no_grad():
                la, va = net(Xa)
                lpa = torch.log_softmax(la, 1)
            kl = (base_p * (base_lp - lpa)).sum(1).mean().item()  # KL(full || ablated)
            vmae = (va - base_v).abs().mean().item()
            top1_flip = (la.argmax(1) != base_logits.argmax(1)).float().mean().item()
            r = rows.setdefault(name, {"kl": [], "vmae": [], "top1_flip": []})
            r["kl"].append(kl); r["vmae"].append(vmae); r["top1_flip"].append(top1_flip)
    return {name: {"policy_kl": round(float(np.mean(v["kl"])), 4),
                   "value_mae": round(float(np.mean(v["vmae"])), 4),
                   "top1_flip_rate": round(float(np.mean(v["top1_flip"])), 4)}
            for name, v in rows.items()}


def play_match(a, b, n, games, seed):
    rng = random.Random(seed)
    boards = [Board(n) for _ in range(games)]
    passes = [0] * games; done = [False] * games
    a_black = [g % 2 == 0 for g in range(games)]
    for ply in range(n * n * n * 2):
        for mcts, is_a in ((a, True), (b, False)):
            turn = [i for i in range(games) if not done[i]
                    and ((boards[i].player == 1) == (a_black[i] == is_a))]
            if not turn:
                continue
            if ply < TEMP_MOVES:
                pis = mcts.run_policies([boards[i] for i in turn], [passes[i] for i in turn],
                                        [1.0] * len(turn), root_noise=0.25)
            else:
                pis = mcts.run_policies([boards[i] for i in turn], [passes[i] for i in turn],
                                        [LOW_TEMP] * len(turn))
            for k, i in enumerate(turn):
                act = rng.choices(range(len(pis[k])), weights=pis[k])[0]
                _apply_action(boards[i], act, n, passes, done, i)
        if all(done):
            break
    aw = dec = 0
    for i, bd in enumerate(boards):
        s = bd.score_tromp_taylor()
        if s["winner"] == "draw":
            continue
        dec += 1
        if (s["winner"] == "black") == a_black[i]:
            aw += 1
    return aw, dec


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    gp = int(sys.argv[2]) if len(sys.argv) > 2 else 48
    sims = int(sys.argv[3]) if len(sys.argv) > 3 else 96
    out = sys.argv[4] if len(sys.argv) > 4 else "probe1_ablation.json"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    t0 = time.time()
    print(f"# PROBE-1 ablation n={n}^3 sims={sims} gp/seedpair={gp} device={device}", flush=True)

    aA = part_a(n, device)
    print("Part A (forward-pass reliance, pooled 3 seeds):", flush=True)
    for name in ABLATIONS:
        r = aA[name]
        print(f"  ablate {name:7s}: policyKL={r['policy_kl']:.4f} valueMAE={r['value_mae']:.4f} "
              f"top1flip={r['top1_flip_rate']:.4f}", flush=True)

    # Part B: full net vs ablated net, per ablation (skip 'none').
    partB = {}
    for name, abl in ABLATIONS.items():
        if not abl:
            continue
        fw_tot = dec_tot = 0
        for s in SEEDS:
            full = AblMCTS(load_net(n, s, device), device, CFG, sims, seed=100 + s, ablate=[])
            ab = AblMCTS(load_net(n, s, device), device, CFG, sims, seed=200 + s, ablate=abl)
            fw, dec = play_match(full, ab, n, gp, seed=1000 + s * 7 + len(abl))
            fw_tot += fw; dec_tot += dec
        wr = fw_tot / max(1, dec_tot)
        # binomial 95% CI
        se = (wr * (1 - wr) / max(1, dec_tot)) ** 0.5
        ci = [round(wr - 1.96 * se, 4), round(wr + 1.96 * se, 4)]
        partB[name] = {"full_winrate_vs_ablated": round(wr, 4), "ci95": ci,
                       "full_wins": fw_tot, "decided": dec_tot}
        print(f"  full vs ablate-{name:7s}: {fw_tot}/{dec_tot} full-wr={wr:.4f} {ci} ({time.time()-t0:.0f}s)",
              flush=True)

    result = {"experiment": "PROBE-1 input-plane ablation attribution (libs net, 5^3)",
              "n": n, "sims": sims, "games_per_seedpair": gp, "seeds": SEEDS,
              "ablations": {k: v for k, v in ABLATIONS.items()},
              "part_a_forward_reliance": aA, "part_b_strength_cost": partB,
              "secs": round(time.time() - t0, 1)}
    json.dump(result, open(out, "w"), indent=2)
    print(f"wrote {out} ({result['secs']}s)", flush=True)


if __name__ == "__main__":
    main()
