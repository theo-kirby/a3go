"""WS1 — GPU net-vs-net strength screen for A3GoNetIn checkpoints.

The campaign's strength signal was net-vs-classical (eval_arch3.py): classical's
CPU random rollouts + the net forward on CPU make it ~3h/seed, so every check was
a multi-hour blocking wait. This screen replaces it for *relative* ordering:
both sides are the trained nets, batched on the GPU (no classical rollouts), so a
full round-robin over the lever family finishes in minutes.

Each agent is one input/capacity config; we own 3 seed checkpoints per config and
play every config-pair across the 3 matching-seed pairings (seed s of A vs seed s
of B) to fold seed variance into the win counts — answering the PASS-15
small-sample scar by driving decided games per pair >= 128. Ratings are the same
Bradley-Terry / Elo fit as ladder.py (anchor = `base`, so Elo reads as relative
strength over the 3-plane baseline), with bootstrap CIs over games.

The net's MCTS uses the eval_arch3 `_RichMCTS` pattern: a BatchedMCTS subclass that
overrides only `_eval_batch` to encode with input_planes.config_planes(board, cfg),
keeping batched_az.py and the search logic untouched. Opening plies sample at
temp=1 with root noise (like ladder.NetAgent) so games VARY instead of collapsing
to one deterministic line per color; later plies sample at low temp.

Resolves SCALE-libs `faddae67` (does scaling the liberty net lift *relative*
strength?) and yields an anchored Elo ordering of the lever family.

Usage:
  uv run python screen_nvn.py [n] [games_per_seedpair] [sims] [out.json]
  # default: 5 48 96 screen_nvn_5cubed.json
"""
from __future__ import annotations
import os, sys, json, time, random

# Single-thread BLAS before numpy/torch (we are GPU-bound; CPU threads only churn).
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import torch
torch.set_num_threads(1)

from a3go_engine import Board
from batched_az import BatchedMCTS, action_to_move, _apply_action
from net_arch3 import A3GoNetIn
from input_planes import config_planes, n_planes
from ladder import fit_bt

# (label, cfg, channels, blocks, ckpt-pattern) — one agent per config.
CONFIGS = [
    ("base",       "base", 64,  6,  "best_arch3_base_s{}.pt"),
    ("libs",       "libs", 64,  6,  "best_arch3_libs_s{}.pt"),
    ("all",        "all",  64,  6,  "best_arch3_all_s{}.pt"),
    ("libs96x8",   "libs", 96,  8,  "best_libs_96x8_s{}.pt"),
    ("libs128x10", "libs", 128, 10, "best_libs_128x10_s{}.pt"),
]
SEEDS = [0, 1, 2]
LOW_TEMP = 0.3
TEMP_MOVES = 6


class RichMCTS(BatchedMCTS):
    """BatchedMCTS that encodes with a config's richer input planes (eval_arch3)."""
    def __init__(self, net, device, cfg, sims, seed=0):
        super().__init__(net, device, sims=sims, seed=seed)
        self.cfg = cfg

    def _eval_batch(self, boards):
        if not boards:
            return None, None
        X = torch.from_numpy(np.stack([config_planes(b, self.cfg) for b in boards])).to(self.device)
        with torch.no_grad():
            logits, v = self.net(X)
        return logits.float().cpu().numpy(), v.float().cpu().numpy()


def load_agent(cfg, ch, blk, ckpt, n, device, sims, seed):
    net = A3GoNetIn(n, in_planes=n_planes(cfg), channels=ch, blocks=blk)
    net.load_state_dict(torch.load(ckpt, map_location=device))
    net.to(device).eval()
    return RichMCTS(net, device, cfg, sims=sims, seed=seed)


def play_match(a, b, n, games, seed):
    """A vs B, color-balanced, lockstep so net turns batch. Opening plies sample at
    temp=1 + root noise for variety; later plies low-temp. Returns (a_wins, decided)."""
    rng = random.Random(seed)
    boards = [Board(n) for _ in range(games)]
    passes = [0] * games
    done = [False] * games
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
    gp = int(sys.argv[2]) if len(sys.argv) > 2 else 48     # games per seed-pair per config-pair
    sims = int(sys.argv[3]) if len(sys.argv) > 3 else 96
    out = sys.argv[4] if len(sys.argv) > 4 else f"screen_nvn_{n}cubed.json"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    labels = [c[0] for c in CONFIGS]
    m = len(CONFIGS)
    print(f"# net-vs-net screen n={n}^3 sims={sims} gp/seedpair={gp} "
          f"({len(SEEDS)} seeds -> {gp*len(SEEDS)} games/pair) device={device}", flush=True)

    # Pre-load every (config, seed) agent once.
    t0 = time.time()
    agents = {}
    for (lab, cfg, ch, blk, pat) in CONFIGS:
        for s in SEEDS:
            agents[(lab, s)] = load_agent(cfg, ch, blk, pat.format(s), n, device, sims, seed=100 + s)
    print(f"  loaded {len(agents)} agents in {time.time()-t0:.0f}s", flush=True)

    wins = [[0] * m for _ in range(m)]
    games = [[0] * m for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            aw_tot = dec_tot = 0
            for s in SEEDS:
                aw, dec = play_match(agents[(labels[i], s)], agents[(labels[j], s)],
                                     n, gp, seed=1000 + i * 131 + j * 17 + s)
                aw_tot += aw; dec_tot += dec
            wins[i][j] += aw_tot; wins[j][i] += (dec_tot - aw_tot)
            games[i][j] += dec_tot; games[j][i] += dec_tot
            print(f"  {labels[i]:11s} vs {labels[j]:11s}: {aw_tot:3d}/{dec_tot:3d} "
                  f"({aw_tot/max(1,dec_tot):.3f})  ({time.time()-t0:.0f}s)", flush=True)

    anchor = labels.index("base")
    elo = fit_bt(wins, games, anchor_idx=anchor)
    # bootstrap CIs over games
    rng = np.random.default_rng(0)
    flat = [(i, j, wins[i][j], games[i][j]) for i in range(m) for j in range(i + 1, m)]
    boot = []
    for _ in range(300):
        bw = [[0] * m for _ in range(m)]; bg = [[0] * m for _ in range(m)]
        for (i, j, w, g) in flat:
            if g == 0:
                continue
            bwij = rng.binomial(g, w / g)
            bw[i][j] = bwij; bw[j][i] = g - bwij; bg[i][j] = g; bg[j][i] = g
        boot.append(fit_bt(bw, bg, anchor_idx=anchor))
    boot = np.array(boot)
    lo = np.percentile(boot, 2.5, axis=0); hi = np.percentile(boot, 97.5, axis=0)

    order = list(np.argsort(-elo))
    table = []
    print(f"\n=== net-vs-net Elo (n={n}^3, anchor base=0), {time.time()-t0:.0f}s ===", flush=True)
    for r in order:
        table.append({"agent": labels[r], "elo": round(float(elo[r]), 1),
                      "ci95": [round(float(lo[r]), 1), round(float(hi[r]), 1)]})
        print(f"  {labels[r]:11s}  {elo[r]:7.1f}  [{lo[r]:7.1f}, {hi[r]:7.1f}]", flush=True)

    # sanity: libs must outrank base (matches ARCH-3 classical result libs 0.449 > base 0.305)
    libs_gt_base = elo[labels.index("libs")] > elo[anchor]
    result = {"experiment": "WS1 net-vs-net GPU strength screen (A3GoNetIn lever family)",
              "n": n, "sims": sims, "games_per_seedpair": gp, "seeds": SEEDS,
              "labels": labels, "configs": [list(c[:4]) for c in CONFIGS],
              "wins": wins, "games": games,
              "elo": [round(float(x), 2) for x in elo],
              "ci95_lo": [round(float(x), 2) for x in lo], "ci95_hi": [round(float(x), 2) for x in hi],
              "ranking": table, "sanity_libs_gt_base": bool(libs_gt_base),
              "secs": round(time.time() - t0, 1)}
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nsanity libs>base: {libs_gt_base}\nwrote {out}", flush=True)


if __name__ == "__main__":
    main()
