"""ARCH-2 eval: net-vs-classical for A3GoNetBR checkpoints. Identical protocol to
net_vs_classical_mp.py / eval_ownership.py (parallel games, net on CPU, classical
random-rollout MCTS at fixed budget); loads A3GoNetBR so the BN-free trunk params
load cleanly. Reports games/sec so strength-per-wall-clock is comparable.

    A3GO_BR_CH=64 A3GO_BR_BLK=8 A3GO_BR_CB=48 uv run python eval_arch2.py \
        best_arch2_s0.pt 5 128 512 48 50 experiments_arch2_s0.json
"""
from __future__ import annotations
import json, math, os, sys, time
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
    g, ckpt, n, net_sims, cls_playouts, cls_cap, ch, blk, cb = arg
    import torch
    torch.set_num_threads(1)
    from net_arch2 import A3GoNetBR
    from batched_az import BatchedMCTS, action_to_move
    from classical_mcts import ClassicalMCTS
    from a3go_engine import Board

    net = A3GoNetBR(n, channels=ch, blocks=blk, bottleneck=cb)
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
    ckpt = sys.argv[1] if len(sys.argv) > 1 else "best_arch2.pt"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    net_sims = int(sys.argv[4]) if len(sys.argv) > 4 else 512
    cls_playouts = int(sys.argv[5]) if len(sys.argv) > 5 else 48
    cls_cap = int(sys.argv[6]) if len(sys.argv) > 6 else 50
    out = sys.argv[7] if len(sys.argv) > 7 else "experiments_arch2.json"
    ch = int(os.environ.get("A3GO_BR_CH", "64")); blk = int(os.environ.get("A3GO_BR_BLK", "8"))
    cb = int(os.environ.get("A3GO_BR_CB", "48"))
    workers = min(14, os.cpu_count() or 8)

    args = [(g, ckpt, n, net_sims, cls_playouts, cls_cap, ch, blk, cb) for g in range(games)]
    t0 = time.time()
    with mp.Pool(workers) as pool:
        results = pool.map(_play_one, args)
    secs = time.time() - t0

    net_wins = decided = draws = 0
    for net_is_black, winner, diff in results:
        if winner == "draw":
            draws += 1; continue
        decided += 1
        if (winner == "black") == net_is_black:
            net_wins += 1
    p, lo, hi = wilson(net_wins, decided)
    res = {"experiment": "ARCH-2 BN-free nested-bottleneck net vs classical (equal budget)",
           "ckpt": ckpt, "arch": "nested-bottleneck-BNfree-rezero",
           "channels": ch, "blocks": blk, "bottleneck": cb, "boardSize": n, "games": games,
           "decided": decided, "draws": draws, "net_sims": net_sims,
           "classical_playouts": cls_playouts, "classical_rollout_cap": cls_cap, "workers": workers,
           "net_wins": net_wins, "net_winrate": round(p, 3), "winrate_ci95": [round(lo, 3), round(hi, 3)],
           "eval_secs": round(secs, 1), "games_per_sec": round(games / secs, 3),
           "beats_classical_decisively": lo > 0.5}
    print(json.dumps(res, indent=2))
    json.dump(res, open(out, "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
