"""ARCH-3: richer KataGo-style input planes for the policy/value net.

The campaign's baseline net sees only 3 planes (black stones, white stones,
side-to-move). This module builds a fuller stack of features the net currently
must (and largely can't) infer from those 3 planes:

  ch 0  black stones                         } the original 3-plane encoding,
  ch 1  white stones                         } byte-for-byte identical to
  ch 2  side-to-move (1.0 if black to move)  } net.encode / collect_classical.encode
  ch 3  ko-ban: empty points where the side-to-move's play is superko-forbidden
  ch 4  liberty bucket: stones whose group has exactly 1 liberty (atari)
  ch 5  liberty bucket: stones whose group has exactly 2 liberties
  ch 6  liberty bucket: stones whose group has >= 3 liberties
  ch 7  capture: empty points where the side-to-move's play captures >=1 enemy stone
  ch 8  last move location (one-hot; all-zero if pass / game start)
  ch 9  2nd-last move location (one-hot)

Why these: 3D Go is saturated with ko (~98% of single-stone captures trigger a
superko ban, node `31dae43b`) yet the net is blind to it; liberties hand the net
the atari/capture signal directly; history planes give move context (superko
makes value history-dependent, PROOF-3 `22d59c45`). KataGo uses exactly these.

The SAME builder is used at data-collection time (where the board carries its
full superko history + last-move) and at inference inside MCTS (clones carry the
same state), so the ko-ban / history planes are consistent across train and play.

`CONFIG_CHANNELS` maps an ablation config name to the channel indices it uses;
`base` is exactly the original 3 planes, so the base net reproduces the existing
campaign baseline. Collectors store the FULL 10-plane stack; training/inference
select a config's channels, so every ablation runs on identical games/positions.
"""
from __future__ import annotations

import numpy as np

from a3go_engine import Board, BLACK, WHITE, EMPTY, other

# Full canonical stack width and per-config channel selections.
NUM_PLANES = 10
CONFIG_CHANNELS = {
    "base":    [0, 1, 2],
    "koban":   [0, 1, 2, 3],
    "libs":    [0, 1, 2, 4, 5, 6],
    "capture": [0, 1, 2, 7],
    "history": [0, 1, 2, 8, 9],
    "all":     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
}


def n_planes(cfg: str) -> int:
    return len(CONFIG_CHANNELS[cfg])


def rich_planes(board: Board) -> np.ndarray:
    """Full (NUM_PLANES, w, h, d) float32 feature stack for the side to move."""
    w, h, d = board.w, board.h, board.d
    grid = board.grid
    color = board.player
    opp = other(color)
    planes = np.zeros((NUM_PLANES, w, h, d), dtype=np.float32)

    # 0,1,2 — original encoding (identical to net.encode for a clean A/B baseline)
    planes[0] = grid == BLACK
    planes[1] = grid == WHITE
    planes[2] = 1.0 if color == BLACK else 0.0

    Z = board._zob
    hist = board.history

    # 4,5,6 — per-stone liberty buckets (1 / 2 / >= 3 liberties).
    visited = np.zeros((w, h, d), dtype=bool)
    for x, y, z in np.argwhere(grid != EMPTY):
        x, y, z = int(x), int(y), int(z)
        if visited[x, y, z]:
            continue
        grp, libs = board._group(x, y, z)
        bucket = 4 if len(libs) == 1 else (5 if len(libs) == 2 else 6)
        for sx, sy, sz in grp:
            visited[sx, sy, sz] = True
            planes[bucket, sx, sy, sz] = 1.0

    # 3 — ko-ban and 7 — capture, computed per empty cell so both are CAPTURE-AWARE.
    # The dominant 3D ko is a recapture: the move that recreates a prior position
    # captures the stone just played, so the true resulting hash must remove the
    # captured group(s) — a naive `zobrist ^ Z[cell, color]` (no capture) would
    # MISS exactly the prime-suspect ko bans. For each empty p with `color` to move
    # we find enemy groups it puts in atari (sole liberty == p, captured), set the
    # capture plane, fold the captured stones into the resulting hash, and flag
    # ko-ban iff that hash is already in the superko history. No suicide guard is
    # needed: a suicidal (0-liberty) resulting position is never realizable, so its
    # hash can never be in `history` and it is never flagged.
    for x, y, z in np.argwhere(grid == EMPTY):
        x, y, z = int(x), int(y), int(z)
        rh = board.zobrist ^ int(Z[x, y, z, color])
        captured_any = False
        seen_grp: set = set()
        for nx, ny, nz in board._neighbors(x, y, z):
            v = grid[nx, ny, nz]
            if v == opp and (nx, ny, nz) not in seen_grp:
                grp, libs = board._group(nx, ny, nz)
                seen_grp |= grp
                if len(libs) == 1:  # sole liberty is necessarily this cell
                    captured_any = True
                    for sx, sy, sz in grp:
                        rh ^= int(Z[sx, sy, sz, opp])
        if captured_any:
            planes[7, x, y, z] = 1.0
        if rh in hist:
            planes[3, x, y, z] = 1.0

    # 8,9 — last and 2nd-last move locations (one-hot; pass/start leaves all-zero)
    lm = getattr(board, "last_move", None)
    if lm is not None:
        planes[8, lm[0], lm[1], lm[2]] = 1.0
    lm2 = getattr(board, "last_move2", None)
    if lm2 is not None:
        planes[9, lm2[0], lm2[1], lm2[2]] = 1.0

    return planes


def config_planes(board: Board, cfg: str) -> np.ndarray:
    """Inference-time encoder: the channels of `cfg` only, in canonical order.

    Lazily computes ONLY the planes `cfg` selects, producing output byte-identical
    to rich_planes(board)[CONFIG_CHANNELS[cfg]]. The dominant cost in rich_planes is
    the per-empty-cell ko-ban/capture zobrist loop (planes 3 & 7); configs that need
    neither (base, libs, history) skip it entirely — the key speedup for the net's
    own MCTS, where this runs once per expanded leaf. `test_input_planes.py` pins
    identity to rich_planes across board sizes and all six configs.
    """
    chans = CONFIG_CHANNELS[cfg]
    cset = set(chans)
    w, h, d = board.w, board.h, board.d
    grid = board.grid
    color = board.player
    opp = other(color)
    out = {}

    if 0 in cset:
        out[0] = (grid == BLACK).astype(np.float32)
    if 1 in cset:
        out[1] = (grid == WHITE).astype(np.float32)
    if 2 in cset:
        out[2] = np.full((w, h, d), 1.0 if color == BLACK else 0.0, dtype=np.float32)

    # Liberty buckets (4/5/6) — single stone-group sweep, no empty-cell loop.
    if cset & {4, 5, 6}:
        lib = np.zeros((3, w, h, d), dtype=np.float32)  # rows -> buckets 4,5,6
        visited = np.zeros((w, h, d), dtype=bool)
        for x, y, z in np.argwhere(grid != EMPTY):
            x, y, z = int(x), int(y), int(z)
            if visited[x, y, z]:
                continue
            grp, libs = board._group(x, y, z)
            row = 0 if len(libs) == 1 else (1 if len(libs) == 2 else 2)
            for sx, sy, sz in grp:
                visited[sx, sy, sz] = True
                lib[row, sx, sy, sz] = 1.0
        for ch, row in ((4, 0), (5, 1), (6, 2)):
            if ch in cset:
                out[ch] = lib[row]

    # Ko-ban (3) and capture (7) — the expensive per-empty-cell zobrist loop; only
    # run it when this config actually needs one of them. Logic mirrors rich_planes.
    if cset & {3, 7}:
        Z = board._zob
        hist = board.history
        koban = np.zeros((w, h, d), dtype=np.float32)
        cap = np.zeros((w, h, d), dtype=np.float32)
        for x, y, z in np.argwhere(grid == EMPTY):
            x, y, z = int(x), int(y), int(z)
            rh = board.zobrist ^ int(Z[x, y, z, color])
            captured_any = False
            seen_grp: set = set()
            for nx, ny, nz in board._neighbors(x, y, z):
                v = grid[nx, ny, nz]
                if v == opp and (nx, ny, nz) not in seen_grp:
                    grp, libs = board._group(nx, ny, nz)
                    seen_grp |= grp
                    if len(libs) == 1:
                        captured_any = True
                        for sx, sy, sz in grp:
                            rh ^= int(Z[sx, sy, sz, opp])
            if captured_any:
                cap[x, y, z] = 1.0
            if rh in hist:
                koban[x, y, z] = 1.0
        if 3 in cset:
            out[3] = koban
        if 7 in cset:
            out[7] = cap

    # History planes (8/9) — last and 2nd-last move one-hot.
    if 8 in cset:
        p8 = np.zeros((w, h, d), dtype=np.float32)
        lm = getattr(board, "last_move", None)
        if lm is not None:
            p8[lm[0], lm[1], lm[2]] = 1.0
        out[8] = p8
    if 9 in cset:
        p9 = np.zeros((w, h, d), dtype=np.float32)
        lm2 = getattr(board, "last_move2", None)
        if lm2 is not None:
            p9[lm2[0], lm2[1], lm2[2]] = 1.0
        out[9] = p9

    return np.stack([out[c] for c in chans])


def slice_stack(X_full: np.ndarray, cfg: str) -> np.ndarray:
    """Select a config's channels from a stored full (N, NUM_PLANES, ...) stack."""
    return np.ascontiguousarray(X_full[:, CONFIG_CHANNELS[cfg]])
