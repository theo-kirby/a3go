"""Fast net-vs-classical comparison: parallelize games across CPU cores with the
(tiny) net on CPU. PASS 3 ran this sequentially on GPU at ~3 min/game; here each
worker plays one full game on its own core, so ~16 games complete in the time of
one. Net on CPU also leaves the GPU free for a concurrent 5^3 training branch.

Closes the success bar's 2nd baseline leg: does the trained net beat a fixed
classical (random-rollout) MCTS at equal/fixed search budget?

    uv run python net_vs_classical_mp.py [ckpt] [n] [games] [net_sims] [cls_playouts] [cls_rollout_cap] [out]
"""
from __future__ import annotations
import json, math, os, sys
import multiprocessing as mp


def wilson(wins, total, z=1.96):
    if total == 0:
        return (0.0, 0.0, 0.0)
    p = wins / total
    d = 1 + z*z/total
    c = (p + z*z/(2*total)) / d
    h = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / d
    return (round(p, 3), round(max(0, c-h), 3), round(min(1, c+h), 3))


def _play_one(arg):
    g, ckpt, n, net_sims, cls_playouts, cls_cap = arg
    import torch
    torch.set_num_threads(1)
    from net import A3GoNet
    from batched_az import BatchedMCTS, action_to_move
    from classical_mcts import ClassicalMCTS
    from a3go_engine import Board

    import os
    _ch=int(os.environ.get('A3GO_CH','32')); _bl=int(os.environ.get('A3GO_BLK','3'))
    net = A3GoNet(n, channels=_ch, blocks=_bl)  # CPU
    net.load_state_dict(torch.load(ckpt, map_location="cpu"))
    net.eval()
    nmcts = BatchedMCTS(net, "cpu", sims=net_sims, seed=g)
    cls = ClassicalMCTS(playouts=cls_playouts, seed=999 + g, max_rollout=cls_cap)

    net_is_black = g % 2 == 0
    board = Board(n)
    passes = 0
    for _ in range(n * n * n * 2):
        if passes >= 2:
            break
        if (board.player == 1) == net_is_black:
            pi = nmcts.run_policies([board], [passes], [1e-3])[0]
            mv = action_to_move(int(pi.argmax()), n)
        else:
            mv = cls.select_move(board, passes)
        if mv == "pass":
            board.pass_move(); passes += 1
        else:
            board.play(*mv); passes = 0
    s = board.score_tromp_taylor()
    return (net_is_black, s["winner"], float(s["diff"]))


def main() -> int:
    ckpt = sys.argv[1] if len(sys.argv) > 1 else "best_batched_4cubed.pt"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 48
    net_sims = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    cls_playouts = int(sys.argv[5]) if len(sys.argv) > 5 else 128
    cls_cap = int(sys.argv[6]) if len(sys.argv) > 6 else 80
    out = sys.argv[7] if len(sys.argv) > 7 else "experiments_net_vs_classical.json"
    workers = min(14, os.cpu_count() or 8)

    args = [(g, ckpt, n, net_sims, cls_playouts, cls_cap) for g in range(games)]
    with mp.Pool(workers) as pool:
        results = pool.map(_play_one, args)

    net_wins = decided = draws = 0
    for net_is_black, winner, diff in results:
        if winner == "draw":
            draws += 1
            continue
        decided += 1
        if (winner == "black") == net_is_black:
            net_wins += 1
    p, lo, hi = wilson(net_wins, decided)
    res = {
        "experiment": "Q10 neural net vs classical random-rollout MCTS (parallel, equal budget)",
        "ckpt": ckpt, "boardSize": n, "games": games, "decided": decided, "draws": draws,
        "net_sims": net_sims, "classical_playouts": cls_playouts, "classical_rollout_cap": cls_cap,
        "workers": workers,
        "net_wins": net_wins, "net_winrate": round(p, 3), "winrate_ci95": [round(lo, 3), round(hi, 3)],
        "beats_classical_decisively": lo > 0.5,
    }
    print(json.dumps(res, indent=2))
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
