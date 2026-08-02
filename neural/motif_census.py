"""3DSCI-2 — tactical-motif census across board sizes (engine-only, no GPU/net).

Plays classical-teacher self-play games and instruments every PLAYED move to
count the tactical motifs that drive 3D-Go feature design:

  - capture events + sizes (stones removed per capturing move)
  - single-stone captures that create an immediate ko-ban for the opponent
    (the direct test of the campaign's '~98% of single-stone captures trigger a
     superko ban' claim, node 31dae43b)
  - self-atari moves (played group left with exactly 1 liberty)
  - atari-giving moves (puts an enemy group into atari)
  - superko-ban DENSITY per position (empty cells whose capture-aware resulting
    hash is already in the superko history -> a forbidden recapture)
  - terminal neutral/dame region census (a coarse seki/mutual-life proxy)

Pure engine; parallel across CPU cores. Reuses the capture-aware ko logic that
input_planes uses for the koban plane, so the counts are consistent with the
feature the net actually sees.

    uv run python motif_census.py [games_per_size] [playouts] [sizes_csv] [out.json]
"""
from __future__ import annotations
import sys, os, json, time
import multiprocessing as mp
import numpy as np

from a3go_engine import Board, EMPTY, other
from classical_mcts import ClassicalMCTS


def _koban_count(board: Board) -> tuple[int, int]:
    """(#empty cells forbidden by superko for the side to move, #empty cells).
    Capture-aware, mirrors input_planes.rich_planes koban logic."""
    grid = board.grid
    color = board.player
    opp = other(color)
    Z = board._zob
    hist = board.history
    empties = np.argwhere(grid == EMPTY)
    banned = 0
    for x, y, z in empties:
        x, y, z = int(x), int(y), int(z)
        rh = board.zobrist ^ int(Z[x, y, z, color])
        seen: set = set()
        for nx, ny, nz in board._neighbors(x, y, z):
            if grid[nx, ny, nz] == opp and (nx, ny, nz) not in seen:
                grp, libs = board._group(nx, ny, nz)
                seen |= grp
                if len(libs) == 1:  # sole liberty is this cell -> captured
                    for sx, sy, sz in grp:
                        rh ^= int(Z[sx, sy, sz, opp])
        if rh in hist:
            banned += 1
    return banned, len(empties)


def _ko_after_single_capture(board: Board, cell) -> bool:
    """After the side to move just captured exactly one stone at `cell`, would the
    opponent's immediate recapture at `cell` recreate a prior position (ko-ban)?
    board.player is already the opponent here."""
    color = board.player  # opponent of the capturer
    opp = other(color)
    Z = board._zob
    x, y, z = cell
    rh = board.zobrist ^ int(Z[x, y, z, color])
    seen: set = set()
    for nx, ny, nz in board._neighbors(x, y, z):
        if board.grid[nx, ny, nz] == opp and (nx, ny, nz) not in seen:
            grp, libs = board._group(nx, ny, nz)
            seen |= grp
            if len(libs) == 1:
                for sx, sy, sz in grp:
                    rh ^= int(Z[sx, sy, sz, opp])
    return rh in board.history


def _play_one(arg):
    g, n, playouts = arg
    mcts = ClassicalMCTS(playouts=playouts, seed=g, max_rollout=n * n * n)
    board = Board(n)
    passes = 0
    KSTRIDE = 6  # sub-sample the O(empties) koban-density scan every KSTRIDE moves
    c = {  # counters
        "moves": 0, "stone_plays": 0, "passes": 0,
        "capture_moves": 0, "stones_captured": 0,
        "single_captures": 0, "single_capture_ko": 0,
        "multi_captures": 0,
        "self_atari_moves": 0, "atari_giving_moves": 0,
        "koban_cells": 0, "empty_cells_scored": 0, "positions_with_koban": 0,
    }
    cap_sizes = []
    for t in range(n * n * n * 3):
        # superko-ban density at this position (before the move) — sub-sampled,
        # the O(empties) scan dominates cost at n>=5.
        if t % KSTRIDE == 0:
            banned, n_empty = _koban_count(board)
            c["koban_cells"] += banned
            c["empty_cells_scored"] += n_empty
            c["positions_with_koban"] += (banned > 0)
            c["koban_positions_scored"] = c.get("koban_positions_scored", 0) + 1

        mv = mcts.select_move(board, passes)
        c["moves"] += 1
        if mv == "pass":
            board.pass_move(); passes += 1; c["passes"] += 1
            if passes >= 2:
                break
            continue
        passes = 0
        c["stone_plays"] += 1
        opp = other(board.player)
        before = board.grid == opp
        board.play(*mv)
        after = board.grid == opp
        captured_mask = before & ~after  # opp cells that became empty
        ncap = int(captured_mask.sum())
        if ncap:
            c["capture_moves"] += 1
            c["stones_captured"] += ncap
            cap_sizes.append(ncap)
            if ncap == 1:
                c["single_captures"] += 1
                cell = tuple(int(v) for v in np.argwhere(captured_mask)[0])
                if _ko_after_single_capture(board, cell):
                    c["single_capture_ko"] += 1
            else:
                c["multi_captures"] += 1
        # self-atari: played group (board.player is now opp; the played stone is `mv`)
        grp, libs = board._group(*mv)
        if len(libs) == 1:
            c["self_atari_moves"] += 1
        # atari-giving: any adjacent enemy (now == board.player) group at 1 lib
        gives = False
        seen: set = set()
        for nx, ny, nz in board._neighbors(*mv):
            if board.grid[nx, ny, nz] == board.player and (nx, ny, nz) not in seen:
                ggrp, glibs = board._group(nx, ny, nz)
                seen |= ggrp
                if len(glibs) == 1:
                    gives = True
        if gives:
            c["atari_giving_moves"] += 1

    s = board.score_tromp_taylor()
    c["terminal_neutral"] = int(s["neutral"])
    c["game_len"] = c["moves"]
    return c, cap_sizes


def main() -> int:
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    playouts = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    sizes = [int(x) for x in (sys.argv[3].split(",") if len(sys.argv) > 3 else "3,4,5,7".split(","))]
    out = sys.argv[4] if len(sys.argv) > 4 else "motif_census.json"
    workers = min(14, os.cpu_count() or 8)
    t0 = time.time()
    report = {"experiment": "3DSCI-2 tactical-motif census (classical self-play, engine-only)",
              "games_per_size": games, "playouts": playouts, "sizes": sizes, "by_size": {}}

    for n in sizes:
        agg = None
        all_caps = []
        with mp.Pool(workers) as pool:
            for c, caps in pool.imap_unordered(_play_one, [(g, n, playouts) for g in range(games)]):
                if agg is None:
                    agg = {k: 0 for k in c}
                for k, v in c.items():
                    agg[k] += v
                all_caps.extend(caps)
        sp = max(1, agg["stone_plays"])
        npos = max(1, agg["empty_cells_scored"])
        sc = max(1, agg["single_captures"])
        row = {
            "games": games,
            "mean_game_len": round(agg["moves"] / games, 1),
            "stone_plays": agg["stone_plays"],
            "capture_rate_per_play": round(agg["capture_moves"] / sp, 4),
            "stones_captured": agg["stones_captured"],
            "mean_capture_size": round(np.mean(all_caps), 3) if all_caps else 0.0,
            "single_capture_share": round(agg["single_captures"] / max(1, agg["capture_moves"]), 4),
            "single_capture_ko_rate": round(agg["single_capture_ko"] / sc, 4),
            "self_atari_rate_per_play": round(agg["self_atari_moves"] / sp, 4),
            "atari_giving_rate_per_play": round(agg["atari_giving_moves"] / sp, 4),
            "koban_density_per_empty": round(agg["koban_cells"] / npos, 5),
            "positions_with_koban_share": round(agg["positions_with_koban"] / max(1, agg.get("koban_positions_scored", 0)), 4),
            "mean_terminal_neutral": round(agg["terminal_neutral"] / games, 2),
            "_raw": agg,
        }
        report["by_size"][str(n)] = row
        print(f"n={n}^3: cap/play={row['capture_rate_per_play']} single-cap-ko={row['single_capture_ko_rate']} "
              f"self-atari={row['self_atari_rate_per_play']} koban/empty={row['koban_density_per_empty']} "
              f"neutral={row['mean_terminal_neutral']} ({time.time()-t0:.0f}s)", flush=True)
        report["secs"] = round(time.time() - t0, 1)
        json.dump(report, open(out, "w"), indent=2)  # checkpoint per size

    report["secs"] = round(time.time() - t0, 1)
    json.dump(report, open(out, "w"), indent=2)
    print(f"wrote {out} ({report['secs']}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
