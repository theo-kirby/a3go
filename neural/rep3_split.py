"""REP-3 — my/opp liberty split (PROBE-1's recommended refinement). The winning
`libs` config marks a stone's liberty bucket (1/2/>=3) but NOT whose stone; the
correct move is opposite for my-group-in-atari (defend) vs opp-group-in-atari
(capture). PROBE-1 found the net leans on the >=3-lib (group-health) plane, and
ownership is the dropped bit — so split each liberty bucket by side-to-move.

Key efficiency: the split planes are DERIVABLE from the stored 10-plane stack
(black/white/stm + the 3 liberty buckets), so NO re-collection is needed — we
train on the exact same games/positions as plain libs, changing only the input.

  9 planes: [black, white, stm, my1,my2,my3, opp1,opp2,opp3]

Trains 3 seeds (same soft-target/trunk as ARCH-3) and screens net-vs-net vs the
plain libs net. A clean A/B: only the liberty-ownership split differs.

    uv run python rep3_split.py [mode]   mode: train | screen | all (default all)
"""
from __future__ import annotations
import os, sys, json, time, random
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
import torch
import torch.nn.functional as F

from a3go_engine import Board, BLACK, WHITE, EMPTY, other
from net_arch3 import A3GoNetIn, param_count
from train_softpolicy import build_targets
from input_planes import config_planes, n_planes, rich_planes

NPZ = "distill_arch3_5cubed.npz"
SEEDS = [0, 1, 2]
IN_PLANES = 9


def split_from_stack(X):
    """Derive (N,9,n,n,n) my/opp liberty-split planes from the stored (N,10,...) stack."""
    blk = X[:, 0:1]; wht = X[:, 1:2]; stm = X[:, 2:3]
    my = blk * stm + wht * (1.0 - stm)
    opp = wht * stm + blk * (1.0 - stm)
    b1, b2, b3 = X[:, 4:5], X[:, 5:6], X[:, 6:7]   # 1-lib, 2-lib, >=3-lib
    out = np.concatenate([blk, wht, stm,
                          b1 * my, b2 * my, b3 * my,
                          b1 * opp, b2 * opp, b3 * opp], axis=1)
    return np.ascontiguousarray(out.astype(np.float32))


def split_planes(board: Board) -> np.ndarray:
    """Live encoder for MCTS: 9 my/opp liberty-split planes for the side to move."""
    w, h, d = board.w, board.h, board.d
    grid = board.grid
    color = board.player
    out = np.zeros((9, w, h, d), dtype=np.float32)
    out[0] = grid == BLACK
    out[1] = grid == WHITE
    out[2] = 1.0 if color == BLACK else 0.0
    visited = np.zeros((w, h, d), dtype=bool)
    for x, y, z in np.argwhere(grid != EMPTY):
        x, y, z = int(x), int(y), int(z)
        if visited[x, y, z]:
            continue
        grp, libs = board._group(x, y, z)
        bucket = 0 if len(libs) == 1 else (1 if len(libs) == 2 else 2)
        is_mine = grid[x, y, z] == color
        ch = (3 + bucket) if is_mine else (6 + bucket)
        for sx, sy, sz in grp:
            visited[sx, sy, sz] = True
            out[ch, sx, sy, sz] = 1.0
    return out


def _selftest():
    """Live encoder must equal derive-from-stack on random positions."""
    rng = random.Random(0)
    for t in range(30):
        b = Board(5)
        for _ in range(rng.randint(0, 30)):
            mv = b.legal_moves()
            if not mv:
                break
            b.play(*rng.choice(mv))
        live = split_planes(b)
        derived = split_from_stack(rich_planes(b)[None])[0]
        if not np.allclose(live, derived):
            print("SELFTEST FAIL at", t); return False
    print("rep3 split selftest: PASS (live == derived-from-stack)")
    return True


def train_seed(seed, X, P, Z, best_action, n, epochs=40, batch=256, lr=1e-3, device="cuda"):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(X))
    Xp, Pp, Zp, bap = X[perm], P[perm], Z[perm], best_action[perm]
    nh = max(1, int(0.1 * len(Xp)))
    Xh, Zh, bah = Xp[:nh], Zp[:nh], bap[:nh]
    Xt, Pt, Zt = Xp[nh:], Pp[nh:], Zp[nh:]
    net = A3GoNetIn(n, in_planes=IN_PLANES, channels=64, blocks=6).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=1e-4)
    t = lambda a: torch.from_numpy(a).to(device)
    Xt_t, Pt_t, Zt_t = t(Xt), t(Pt), t(Zt)
    Xh_t, Zh_t, bah_t = t(Xh), t(Zh), torch.from_numpy(bah).to(device)
    m = Xt_t.shape[0]; best = -1.0; best_stats = None
    for ep in range(1, epochs + 1):
        net.train(); pm = torch.randperm(m, device=device)
        for i in range(0, m, batch):
            idx = pm[i:i+batch]
            logits, v = net(Xt_t[idx])
            loss = 8.0 * -(Pt_t[idx] * F.log_softmax(logits, 1)).sum(1).mean() + F.mse_loss(v, Zt_t[idx])
            opt.zero_grad(); loss.backward(); opt.step()
        net.eval()
        with torch.no_grad():
            lo, vo = net(Xh_t)
            top1 = (lo.argmax(1) == bah_t).float().mean().item()
            vmse = F.mse_loss(vo, Zh_t).item()
        if top1 > best:
            best = top1; best_stats = {"epoch": ep, "top1": round(top1, 4), "vmse": round(vmse, 4)}
            torch.save(net.state_dict(), f"best_rep3_split_s{seed}.pt")
    return best, best_stats


def do_train(device):
    d = np.load(NPZ)
    X_full, V, Z = d["X"], d["V"], d["Z"]
    n = X_full.shape[2]
    X = split_from_stack(X_full)
    P = build_targets(V, "soft", 4.0, 0.02)
    ba = V.argmax(1)
    pc = param_count(A3GoNetIn(n, in_planes=IN_PLANES, channels=64, blocks=6))
    print(f"# REP-3 train: in_planes={IN_PLANES} params={pc} examples={len(X)} device={device}", flush=True)
    res = {}
    t0 = time.time()
    for s in SEEDS:
        best, st = train_seed(s, X, P, Z, ba, n, device=device)
        res[s] = {"best_top1": round(best, 4), "best": st}
        print(f"  seed {s}: best holdout top1={best:.4f} {st} ({time.time()-t0:.0f}s)", flush=True)
    return res, pc


# ---- net-vs-net screen: split vs plain libs ----
from batched_az import BatchedMCTS, _apply_action, _winrate
LOW_TEMP, TEMP_MOVES = 0.3, 6


class EncMCTS(BatchedMCTS):
    def __init__(self, net, device, encoder, sims, seed=0):
        super().__init__(net, device, sims=sims, seed=seed)
        self.encoder = encoder

    def _eval_batch(self, boards):
        if not boards:
            return None, None
        X = torch.from_numpy(np.stack([self.encoder(b) for b in boards])).to(self.device)
        with torch.no_grad():
            logits, v = self.net(X)
        return logits.float().cpu().numpy(), v.float().cpu().numpy()


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


def do_screen(device, gp=32, sims=48):
    enc_split = split_planes
    enc_libs = lambda bd: config_planes(bd, "libs")
    wtot = 0.0; per = []
    t0 = time.time()
    for s in SEEDS:
        sp = A3GoNetIn(5, in_planes=IN_PLANES, channels=64, blocks=6)
        sp.load_state_dict(torch.load(f"best_rep3_split_s{s}.pt", map_location=device)); sp.to(device).eval()
        lb = A3GoNetIn(5, in_planes=n_planes("libs"), channels=64, blocks=6)
        lb.load_state_dict(torch.load(f"best_arch3_libs_s{s}.pt", map_location=device)); lb.to(device).eval()
        A = EncMCTS(sp, device, enc_split, sims=sims, seed=100 + s)
        B = EncMCTS(lb, device, enc_libs, sims=sims, seed=200 + s)
        wr = play_match(A, B, 5, gp, seed=1000 + s)  # A = split
        per.append(round(wr, 4)); wtot += wr
        print(f"  seed {s}: split-vs-libs winrate={wr:.4f} ({time.time()-t0:.0f}s)", flush=True)
    wr = wtot / len(SEEDS)
    se = (wr * (1 - wr) / (gp * len(SEEDS))) ** 0.5
    return {"split_winrate_vs_libs": round(wr, 4), "per_seed": per,
            "ci95": [round(wr - 1.96 * se, 4), round(wr + 1.96 * se, 4)],
            "games_per_seed": gp, "sims": sims}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    assert _selftest()
    out = {"experiment": "REP-3 my/opp liberty split (group-health), 5^3, vs plain libs"}
    if mode in ("train", "all"):
        out["train"], out["params"] = do_train(device)
    if mode in ("screen", "all"):
        out["screen"] = do_screen(device)
        s = out["screen"]
        print(f"\nsplit-vs-libs pooled = {s['split_winrate_vs_libs']} {s['ci95']} "
              f"(>0.5 => ownership split helps)", flush=True)
    json.dump(out, open("rep3_split.json", "w"), indent=2)
    print("wrote rep3_split.json", flush=True)


if __name__ == "__main__":
    main()
