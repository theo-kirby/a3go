"""ARCH-3 eval: net-vs-classical for A3GoNetIn checkpoints with a given input
config. Identical protocol to net_vs_classical_mp.py / eval_arch2.py (parallel
games, net on CPU, classical random-rollout MCTS at fixed budget), except the net
sees the config's richer input planes. A thin BatchedMCTS subclass overrides only
the batched encoder to use input_planes.config_planes(board, cfg) — keeping
batched_az.py untouched and the search logic identical.

    A3GO_CFG=all A3GO_CH=64 A3GO_BLK=6 uv run python eval_arch3.py \
        best_arch3_all_s0.pt 5 128 512 48 50 experiments_arch3_all_s0.json
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
    g, ckpt, n, net_sims, cls_playouts, cls_cap, ch, blk, cfg = arg
    import numpy as np
    import torch
    torch.set_num_threads(1)
    from net_arch3 import A3GoNetIn
    from batched_az import BatchedMCTS, action_to_move
    from classical_mcts import ClassicalMCTS
    from a3go_engine import Board
    from input_planes import config_planes, n_planes

    class _RichMCTS(BatchedMCTS):
        def _eval_batch(self, boards):
            if not boards:
                return None, None
            X = torch.from_numpy(np.stack([config_planes(b, cfg) for b in boards])).to(self.device)
            with torch.no_grad():
                logits, v = self.net(X)
            return logits.float().cpu().numpy(), v.float().cpu().numpy()

    net = A3GoNetIn(n, in_planes=n_planes(cfg), channels=ch, blocks=blk)
    net.load_state_dict(torch.load(ckpt, map_location="cpu"))
    net.eval()
    nmcts = _RichMCTS(net, "cpu", sims=net_sims, seed=g)
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
    ckpt = sys.argv[1] if len(sys.argv) > 1 else "best_arch3.pt"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    net_sims = int(sys.argv[4]) if len(sys.argv) > 4 else 512
    cls_playouts = int(sys.argv[5]) if len(sys.argv) > 5 else 48
    cls_cap = int(sys.argv[6]) if len(sys.argv) > 6 else 50
    out = sys.argv[7] if len(sys.argv) > 7 else "experiments_arch3.json"
    cfg = os.environ.get("A3GO_CFG", "all")
    ch = int(os.environ.get("A3GO_CH", "64")); blk = int(os.environ.get("A3GO_BLK", "6"))
    workers = min(14, os.cpu_count() or 8)

    args = [(g, ckpt, n, net_sims, cls_playouts, cls_cap, ch, blk, cfg) for g in range(games)]
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
    res = {"experiment": "ARCH-3 richer-input net vs classical (equal budget)",
           "ckpt": ckpt, "cfg": cfg, "channels": ch, "blocks": blk, "boardSize": n, "games": games,
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
