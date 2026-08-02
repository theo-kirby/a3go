"""AUX-3: collect distill data storing RAW MCTS visit counts V (not a temperature-
baked policy), so soft targets at any T and a hard (argmax) target can both be
built from the same data for a clean A/B.

Move *selection* uses the same temperature anneal as collect_ownership (temp=1.0
for the first 8 plies, then 0.3) so the X distribution matches the campaign's
existing distill data; only the stored target differs (raw visits V).

    uv run python collect_softpolicy.py [n] [games] [playouts] [rollout_cap] [out.npz]
"""
from __future__ import annotations
import sys, os
import multiprocessing as mp
import numpy as np

from a3go_engine import Board
from classical_mcts import ClassicalMCTS
from collect_classical import encode
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
    rows = []  # (enc, raw_visits, player)
    for t in range(n * n * n * 2):
        root, _ = mcts._search(board, passes)
        v = _visit_vec(root, n)
        rows.append((encode(board), v, board.player))
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
    out = sys.argv[5] if len(sys.argv) > 5 else "distill_softpol_5cubed.npz"
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
    np.savez_compressed(out, X=X, V=V, Z=Z)
    print(f"saved {out}: X{X.shape} V{V.shape} Z{Z.shape}  games={games} "
          f"playouts={playouts} B/W/draw={bw}/{ww}/{dr}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
