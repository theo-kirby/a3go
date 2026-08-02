"""ARCH-3: collect distill data storing the FULL rich input-plane stack (10
planes, see input_planes.rich_planes) per position, alongside raw MCTS visit
counts V and outcome Z.

This reruns the SAME deterministic classical-teacher self-play games as AUX-3's
collect_softpolicy (identical seeds 31337+g, mcts seed=g, temp anneal 8 plies @1.0
then 0.3, raw-visit targets) — only the stored *features* differ (10-plane stack
vs 3-plane encode). So every ARCH-3 input-ablation trains/evaluates on the exact
positions AUX-3/ARCH-2 used; the only experimental variable is the input
representation. ko-ban / liberty / history planes are computed live here, where
the board carries its full superko history + last-move state.

    uv run python collect_arch3.py [n] [games] [playouts] [rollout_cap] [out.npz]
"""
from __future__ import annotations
import sys, os
import multiprocessing as mp
import numpy as np

from a3go_engine import Board
from classical_mcts import ClassicalMCTS
from input_planes import rich_planes, NUM_PLANES
from az import move_to_action, action_to_move


def _visit_vec(root, n):
    v = np.zeros(n * n * n + 1, dtype=np.float32)
    if not root.children:
        v[n * n * n] = 1.0
        return v
    for ch in root.children:
        v[move_to_action(ch.move, n)] = ch.N
    return v


def _select(v, temp, rng):
    if temp <= 1e-3:
        a = int(v.argmax())
    else:
        p = v ** (1.0 / temp)
        s = p.sum()
        p = p / s if s > 0 else None
        a = int(rng.choice(len(v), p=p)) if p is not None else int(v.argmax())
    return a


def _play_one(arg):
    g, n, playouts, cap, temp_moves = arg
    rng = np.random.default_rng(31337 + g)
    mcts = ClassicalMCTS(playouts=playouts, seed=g, max_rollout=cap)
    board = Board(n)
    passes = 0
    rows = []  # (rich_enc, raw_visits, player)
    for t in range(n * n * n * 2):
        root, _ = mcts._search(board, passes)
        v = _visit_vec(root, n)
        rows.append((rich_planes(board), v, board.player))
        temp = 1.0 if t < temp_moves else 0.3
        a = _select(v, temp, rng)
        mv = action_to_move(a, n)
        if mv == "pass":
            board.pass_move(); passes += 1
            if passes >= 2:
                break
        else:
            board.play(*mv); passes = 0
    s = board.score_tromp_taylor()
    winner = 0 if s["winner"] == "draw" else (1 if s["winner"] == "black" else 2)
    X, V, Z = [], [], []
    for enc, v, player in rows:
        z = 0.0 if winner == 0 else (1.0 if winner == player else -1.0)
        X.append(enc); V.append(v); Z.append(np.float32(z))
    return X, V, Z, winner


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    games = int(sys.argv[2]) if len(sys.argv) > 2 else 384
    playouts = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    out = sys.argv[5] if len(sys.argv) > 5 else "distill_arch3_5cubed.npz"
    workers = min(14, os.cpu_count() or 8)

    args = [(g, n, playouts, cap, 8) for g in range(games)]
    X, V, Z = [], [], []
    bw = ww = dr = done = 0
    with mp.Pool(workers) as pool:
        for xs, vs, zs, winner in pool.imap_unordered(_play_one, args):
            X.extend(xs); V.extend(vs); Z.extend(zs)
            bw += winner == 1; ww += winner == 2; dr += winner == 0
            done += 1
            if done % 32 == 0:
                print(f"  {done}/{games} games, {len(X)} examples (B/W/draw {bw}/{ww}/{dr})", flush=True)
    X = np.stack(X); V = np.stack(V); Z = np.array(Z, dtype=np.float32)
    assert X.shape[1] == NUM_PLANES, X.shape
    np.savez_compressed(out, X=X, V=V, Z=Z)
    print(f"saved {out}: X{X.shape} V{V.shape} Z{Z.shape}  games={games} "
          f"playouts={playouts} planes={NUM_PLANES} B/W/draw={bw}/{ww}/{dr}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
