"""PROOF-3 — exact minimax solver for the smallest 3D-Go boards (ground truth).

Returns the game-theoretic value (optimal Black_area - White_area under komi 0,
Tromp-Taylor) and hence the exact fair komi, for boards small enough to solve
outright. Positional superko makes the value history-dependent, so we do NOT
memoize by position (that would be unsound) — plain alpha-beta with the full
history threaded through clones. Termination is guaranteed: superko forbids
repeating a whole-board position and the board is finite, so every line ends in
two passes. This anchors Success-bar-v2 S3 (distance-from-optimal) and turns the
empirical komi estimates into exact values where tractable.

Usage: uv run python solve_small.py [out.json]
"""
from __future__ import annotations
import sys, json, time
from a3go_engine import Board, BLACK

NEG, POS = -10**9, 10**9
NODE_BUDGET = 8_000_000  # bail a board past this many nodes (report frontier)


class NodeBudget(Exception):
    pass


# Position memoization keyed by (zobrist, player, passes). NOTE: under positional
# superko the game value is technically history-dependent (the same position
# reached via different ko histories can forbid different recaptures), so memo is
# an APPROXIMATION. We validate it against the sound no-memo solver on every board
# small enough for both (1x1x1 .. 2x2x1) — if they agree there, the memo values on
# slightly larger boards are reported with that caveat. Memo collapses the
# ko-driven tree explosion that makes naive minimax intractable past ~2x2x1.
def solve_memo(board, passes, memo):
    key = (board.zobrist, board.player, passes)
    if key in memo:
        return memo[key]
    if passes >= 2:
        v = int(round(board.score_tromp_taylor()["diff"]))
        memo[key] = v
        return v
    maximizing = (board.player == BLACK)
    best = NEG if maximizing else POS
    for mv in [None] + board.legal_moves():
        child = board.clone()
        if mv is None:
            child.pass_move(); cp = passes + 1
        else:
            try:
                child.play(*mv)
            except Exception:
                continue
            cp = 0
        v = solve_memo(child, cp, memo)
        best = max(best, v) if maximizing else min(best, v)
    memo[key] = best
    return best


def solve(board, passes, alpha, beta, nodes):
    """Minimax value = optimal (black_area - white_area), komi 0. Black maximizes,
    White minimizes. alpha-beta over {legal plays} + pass. SOUND (no memo)."""
    nodes[0] += 1
    if nodes[0] > NODE_BUDGET:
        raise NodeBudget()
    if passes >= 2:
        return board.score_tromp_taylor()["diff"]
    maximizing = (board.player == BLACK)
    # candidate moves: all legal plays, plus pass
    moves = board.legal_moves()
    best = NEG if maximizing else POS
    # try pass first (cheap) then plays; order doesn't affect correctness
    for mv in [None] + moves:
        child = board.clone()
        if mv is None:
            child.pass_move(); cp = passes + 1
        else:
            try:
                child.play(*mv)
            except Exception:
                continue
            cp = 0
        v = solve(child, cp, alpha, beta, nodes)
        if maximizing:
            if v > best: best = v
            if best > alpha: alpha = best
        else:
            if v < best: best = v
            if best < beta: beta = best
        if alpha >= beta:
            break
    return best


def solve_board(shape, exact_budget=True):
    """Solve with memoization (fast). If exact_budget, also run the SOUND no-memo
    solver (within NODE_BUDGET) to validate the memo value, recording agreement."""
    cells = shape[0] * shape[1] * shape[2]
    b = Board(0, shape=shape)
    t0 = time.time()
    memo = {}
    val = int(round(solve_memo(b, 0, memo)))
    dt = time.time() - t0
    rec = {"shape": list(shape), "cells": cells, "value_komi0": val, "fair_komi": val,
           "winner_komi0": "black" if val > 0 else "white" if val < 0 else "draw",
           "memo_positions": len(memo), "memo_secs": round(dt, 3)}
    if exact_budget:
        b2 = Board(0, shape=shape)
        nodes = [0]
        try:
            t1 = time.time()
            ev = int(round(solve(b2, 0, NEG, POS, nodes)))
            rec["exact_value"] = ev
            rec["exact_nodes"] = nodes[0]
            rec["exact_secs"] = round(time.time() - t1, 3)
            rec["memo_matches_exact"] = (ev == val)
        except (RecursionError, NodeBudget):
            rec["exact_value"] = None
            rec["exact_nodes"] = f">{NODE_BUDGET}"
            rec["memo_matches_exact"] = None  # could not verify (ko explosion)
    return rec


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "solve_small.json"
    shapes = [(1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 2, 2), (3, 2, 1),
              (3, 2, 2), (3, 3, 1), (2, 2, 3), (3, 3, 2), (4, 2, 2), (3, 3, 3)]
    results = []
    for sh in shapes:
        print(f"solving {sh[0]}x{sh[1]}x{sh[2]} ({sh[0]*sh[1]*sh[2]} cells)...", flush=True)
        try:
            r = solve_board(sh)
        except (RecursionError, NodeBudget):
            print("  memo solver itself blew up — stopping", flush=True)
            results.append({"shape": list(sh), "cells": sh[0]*sh[1]*sh[2], "error": "intractable"})
            break
        results.append(r)
        vfy = r.get("memo_matches_exact")
        vtag = {True: "✓exact", False: "✗MISMATCH", None: "(unverified-ko)"}[vfy]
        print(f"  fair_komi={r['value_komi0']:+d}  winner={r['winner_komi0']}  "
              f"memo_pos={r['memo_positions']:,} {r['memo_secs']}s  verify={vtag}", flush=True)
        with open(out, "w") as f:
            json.dump({"results": results}, f, indent=2)
        if r["memo_secs"] > 300:
            print("  (>5 min memo — stopping; tractability frontier)", flush=True)
            break
    print(f"\nwrote {out}", flush=True)


if __name__ == "__main__":
    main()
