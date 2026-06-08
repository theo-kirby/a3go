"""Q10 baseline leg — does the trained neural net beat the classical (random-
rollout) MCTS baseline? Color-balanced, sequential games. Net plays via batched
MCTS (batch of 1 here); classical via ClassicalMCTS playout budget.

    uv run python net_vs_classical.py [ckpt] [n] [games] [net_sims] [cls_playouts] [out]
"""
from __future__ import annotations
import json
import math
import random
import sys

import torch

from a3go_engine import Board
from net import A3GoNet
from batched_az import BatchedMCTS
from classical_mcts import ClassicalMCTS


def wilson_ci(wins, total, z=1.96):
    if total == 0:
        return (0.0, 0.0, 0.0)
    p = wins / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = (z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))) / denom
    return (p, max(0.0, center - half), min(1.0, center + half))


def main() -> int:
    ckpt = sys.argv[1] if len(sys.argv) > 1 else "best_batched_4cubed.pt"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    net_sims = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    cls_playouts = int(sys.argv[5]) if len(sys.argv) > 5 else 128
    out = sys.argv[6] if len(sys.argv) > 6 else "experiments_net_vs_classical.json"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    net = A3GoNet(n).to(device)
    net.load_state_dict(torch.load(ckpt, map_location=device))
    net.eval()
    nmcts = BatchedMCTS(net, device, sims=net_sims, seed=0)

    rng = random.Random(12345)
    net_wins = decided = draws = 0
    for g in range(games):
        net_is_black = g % 2 == 0
        cls = ClassicalMCTS(playouts=cls_playouts, seed=999 + g, max_rollout=64)
        board = Board(n)
        passes = 0
        for _ in range(n * n * n * 2):
            if passes >= 2:
                break
            net_turn = (board.player == 1) == net_is_black
            if net_turn:
                pi = nmcts.run_policies([board], [passes], [1e-3])[0]
                a = int(pi.argmax())
                from az import action_to_move
                mv = action_to_move(a, n)
            else:
                mv = cls.select_move(board, passes)
            if mv == "pass":
                board.pass_move(); passes += 1
            else:
                board.play(*mv); passes = 0
        s = board.score_tromp_taylor()
        if s["winner"] == "draw":
            draws += 1
            continue
        decided += 1
        if (s["winner"] == "black") == net_is_black:
            net_wins += 1
        print(f"  game {g+1}/{games}: net={'B' if net_is_black else 'W'} "
              f"winner={s['winner']} diff={s['diff']} (net_wins={net_wins}/{decided})",
              flush=True)

    p, lo, hi = wilson_ci(net_wins, decided)
    result = {
        "experiment": "Q10 neural net vs classical random-rollout MCTS",
        "ckpt": ckpt, "boardSize": n, "games": games, "decided": decided, "draws": draws,
        "net_sims": net_sims, "classical_playouts": cls_playouts,
        "net_wins": net_wins, "net_winrate": round(p, 3),
        "winrate_ci95": [round(lo, 3), round(hi, 3)],
        "beats_classical_decisively": lo > 0.5,
    }
    print(json.dumps(result, indent=2))
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
