"""Collect distillation data by classical-MCTS self-play (autogo transfer:
bootstrap the net from a stronger teacher; we have no human 3D-Go games, but
classical random-rollout MCTS beats our net, so it IS our teacher).

Each move records (encoded_state, classical-MCTS visit policy, side-to-move);
z is filled from the game outcome. Pure CPU + engine (no torch/GPU in workers),
parallelized one game per core.

    uv run python collect_classical.py [n] [games] [playouts] [rollout_cap] [out.npz]
"""
from __future__ import annotations
import sys, os, random
import multiprocessing as mp
import numpy as np

from a3go_engine import Board, BLACK, WHITE
from classical_mcts import ClassicalMCTS
from az import action_to_move, move_to_action


def encode(board: Board) -> np.ndarray:
    n = board.w
    planes = np.zeros((3, n, n, n), dtype=np.float32)
    planes[0] = board.grid == BLACK
    planes[1] = board.grid == WHITE
    planes[2] = 1.0 if board.player == BLACK else 0.0
    return planes


def _play_one(arg):
    g, n, playouts, cap, temp_moves = arg
    rng = random.Random(31337 + g)
    mcts = ClassicalMCTS(playouts=playouts, seed=g, max_rollout=cap)
    board = Board(n)
    passes = 0
    rows = []  # (enc, pi, player)
    for t in range(n * n * n * 2):
        temp = 1.0 if t < temp_moves else 0.3
        mv, pi = mcts.move_and_policy(board, passes, temp=temp)
        rows.append((encode(board), pi, board.player))
        if mv == "pass":
            board.pass_move(); passes += 1
            if passes >= 2:
                break
        else:
            board.play(*mv); passes = 0
    s = board.score_tromp_taylor()
    winner = 0 if s["winner"] == "draw" else (1 if s["winner"] == "black" else 2)
    X, P, Z = [], [], []
    for enc, pi, player in rows:
        z = 0.0 if winner == 0 else (1.0 if winner == player else -1.0)
        X.append(enc); P.append(pi); Z.append(np.float32(z))
    return X, P, Z, winner


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    games = int(sys.argv[2]) if len(sys.argv) > 2 else 192
    playouts = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    out = sys.argv[5] if len(sys.argv) > 5 else "distill_4cubed.npz"
    workers = min(14, os.cpu_count() or 8)

    args = [(g, n, playouts, cap, 8) for g in range(games)]
    X, P, Z = [], [], []
    bw = ww = dr = 0
    done = 0
    with mp.Pool(workers) as pool:
        for xs, ps, zs, winner in pool.imap_unordered(_play_one, args):
            X.extend(xs); P.extend(ps); Z.extend(zs)
            bw += winner == 1; ww += winner == 2; dr += winner == 0
            done += 1
            if done % 16 == 0:
                print(f"  {done}/{games} games, {len(X)} examples (B/W/draw {bw}/{ww}/{dr})", flush=True)
    X = np.stack(X); P = np.stack(P); Z = np.array(Z, dtype=np.float32)
    np.savez_compressed(out, X=X, P=P, Z=Z)
    print(f"saved {out}: X{X.shape} P{P.shape} Z{Z.shape}  games={games} "
          f"playouts={playouts} B/W/draw={bw}/{ww}/{dr}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
