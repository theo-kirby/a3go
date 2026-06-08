"""Q9 — pin fair komi on 4^3 using the trained net. Pass 1 found win-rate vs
komi is degenerate on small blowout-dominated boards, and that the MEAN SIGNED
AREA MARGIN is the better estimator. So: play many net self-play games at komi=0,
record the final area diff (black_area - white_area, pre-komi), and estimate

    fair_komi = mean(diff),  SE = std(diff) / sqrt(N).

The decision criterion (control node) is SE <= 0.5 on 4^3. We also report the
win-rate at a few candidate komi values for cross-checking the crossing.

    uv run python komi_neural.py [ckpt] [n] [games] [sims] [out]
"""
from __future__ import annotations
import json
import math
import random
import sys

import numpy as np
import torch

from a3go_engine import Board
from net import A3GoNet
from batched_az import BatchedMCTS, action_to_move


def main() -> int:
    ckpt = sys.argv[1] if len(sys.argv) > 1 else "best_batched_4cubed.pt"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 256
    sims = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    out = sys.argv[5] if len(sys.argv) > 5 else "experiments_komi_neural.json"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    net = A3GoNet(n).to(device)
    net.load_state_dict(torch.load(ckpt, map_location=device))
    net.eval()
    mcts = BatchedMCTS(net, device, sims=sims, seed=0)

    # Play `games` net self-play games in lockstep at komi=0, low-temp sampling
    # for variety, recording the pre-komi area diff of each finished game.
    rng = random.Random(2024)
    boards = [Board(n, komi=0.0) for _ in range(games)]
    passes = [0] * games
    done = [False] * games
    temp_moves = 8
    max_moves = n * n * n * 2
    for t in range(max_moves):
        live = [i for i in range(games) if not done[i]]
        if not live:
            break
        temp = 1.0 if t < temp_moves else 0.4  # keep some sampling to vary games
        pis = mcts.run_policies([boards[i] for i in live], [passes[i] for i in live],
                                [temp] * len(live))
        for k, i in enumerate(live):
            pi = pis[k]
            a = rng.choices(range(len(pi)), weights=pi)[0]
            mv = action_to_move(a, n)
            if mv == "pass":
                boards[i].pass_move(); passes[i] += 1
                if passes[i] >= 2:
                    done[i] = True
            else:
                boards[i].play(*mv); passes[i] = 0

    diffs = np.array([b.score_tromp_taylor()["diff"] for b in boards], dtype=np.float64)
    mean = float(diffs.mean())
    std = float(diffs.std(ddof=1))
    se = std / math.sqrt(len(diffs))
    # win-rate at candidate integer/half komi values (komi added to White).
    komi_winrates = {}
    for komi in [0.0, mean - 1, round(mean), mean, mean + 1]:
        bw = int((diffs - komi > 0).sum())
        ww = int((diffs - komi < 0).sum())
        dr = int((diffs - komi == 0).sum())
        dec = bw + ww
        komi_winrates[round(float(komi), 2)] = {
            "black_winrate": round(bw / dec, 3) if dec else None, "B": bw, "W": ww, "draws": dr}

    result = {
        "experiment": "Q9 fair komi on 4^3 via trained net (mean signed margin)",
        "ckpt": ckpt, "boardSize": n, "games": int(len(diffs)), "sims": sims,
        "mean_area_diff_black_minus_white": round(mean, 3),
        "std_area_diff": round(std, 3),
        "se_of_mean": round(se, 3),
        "fair_komi_estimate": round(mean, 2),
        "se_le_0p5": se <= 0.5,
        "diff_histogram": {int(v): int((diffs == v).sum()) for v in np.unique(diffs)},
        "komi_winrates": komi_winrates,
    }
    print(json.dumps(result, indent=2))
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
