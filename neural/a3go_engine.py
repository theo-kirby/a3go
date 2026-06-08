"""Minimal 3D-Go engine (NumPy) for neural self-play — a port of the validated
TypeScript reference engine in ../src/engine. Identical rules over the 6-neighbor
N^3 lattice: liberties, capture (capture-takes-priority over suicide), suicide
rejection, positional superko (PSK, side-to-move excluded), and Tromp-Taylor area
scoring with komi to White.

Equivalence to the TS engine is checked by crossval.py, which replays move lists
dumped from the TS engine and compares the final Tromp-Taylor breakdown.
"""

from __future__ import annotations

import numpy as np

EMPTY, BLACK, WHITE = 0, 1, 2
_NEI = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))

# INFRA-2: Zobrist tables for O(1) incremental positional-superko hashing. The
# per-candidate `grid.tobytes()` superko check was profiled as the dominant cost
# after the legal_moves vectorization (bench_infra1); a Zobrist hash lets us test
# a candidate position as `current ^ Z[cell, color]` (one XOR) instead of
# serializing the whole board. One table per board shape, fixed seed so the hash
# is deterministic and shared across clones / re-created boards of the same shape.
_ZOB_CACHE: dict = {}


def _zob_table(w: int, h: int, d: int) -> np.ndarray:
    key = (w, h, d)
    t = _ZOB_CACHE.get(key)
    if t is None:
        rng = np.random.default_rng(0xA3603D)
        t = rng.integers(1, 1 << 63, size=(w, h, d, 3), dtype=np.int64)
        t[:, :, :, EMPTY] = 0  # empty cells contribute nothing to the hash
        _ZOB_CACHE[key] = t
    return t


def other(c: int) -> int:
    return BLACK if c == WHITE else WHITE


class IllegalMove(Exception):
    pass


class Board:
    def __init__(self, n: int, komi: float = 0.0, shape: tuple | None = None):
        # Default: cubic n^3 board. `shape=(w,h,d)` overrides for non-cube boards
        # (e.g. a thin (w,h,1) slice is genuine 2D 4-connectivity) — additive, the
        # rest of the engine is already shape-agnostic via self.w/self.h/self.d.
        if shape is None:
            self.w = self.h = self.d = n
        else:
            self.w, self.h, self.d = shape
        self.grid = np.zeros((self.w, self.h, self.d), dtype=np.int8)
        self.player = BLACK
        self.komi = float(komi)
        self._zob = _zob_table(self.w, self.h, self.d)
        self.zobrist = 0  # incremental positional hash (empty board = 0)
        self.history: set = {self._hash()}

    # --- topology -----------------------------------------------------------
    def in_bounds(self, x: int, y: int, z: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d

    def _neighbors(self, x: int, y: int, z: int):
        for dx, dy, dz in _NEI:
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < self.w and 0 <= ny < self.h and 0 <= nz < self.d:
                yield nx, ny, nz

    def _group(self, x: int, y: int, z: int):
        """Return (stones, liberties) for the group at (x,y,z)."""
        color = self.grid[x, y, z]
        stack = [(x, y, z)]
        seen = {(x, y, z)}
        libs: set[tuple[int, int, int]] = set()
        while stack:
            cx, cy, cz = stack.pop()
            for nx, ny, nz in self._neighbors(cx, cy, cz):
                v = self.grid[nx, ny, nz]
                if v == EMPTY:
                    libs.add((nx, ny, nz))
                elif v == color and (nx, ny, nz) not in seen:
                    seen.add((nx, ny, nz))
                    stack.append((nx, ny, nz))
        return seen, libs

    def _hash(self) -> int:
        # Positional superko: Zobrist hash of the board only (excl. side-to-move).
        # Recomputes from the grid AND syncs self.zobrist — used in __init__ and by
        # callers that build a position by writing self.grid directly (e.g. seki3d);
        # the move path maintains self.zobrist incrementally and does not call this.
        z = 0
        Z = self._zob
        for x, y, zc in np.argwhere(self.grid != EMPTY):
            z ^= int(Z[x, y, zc, self.grid[x, y, zc]])
        self.zobrist = z
        return z

    # --- moves --------------------------------------------------------------
    def legal_moves(self):
        """List of legal (x,y,z) plays for the side to move (excludes pass).

        Fast path: an empty point with an empty orthogonal neighbor and NO
        adjacent enemy stone cannot be suicide (immediate liberty) and captures
        nothing (no adjacent enemy group), so the only way it can be illegal is
        positional superko. We therefore skip the expensive capture/suicide
        floodfill and test legality by the cheap superko hash alone (set one
        cell, hash, restore). Note: a non-capturing move CAN still hit superko —
        intervening captures mean adding a stone can recreate an earlier whole-
        board position — so the hash check is required, not optional. Points
        adjacent to an enemy (possible capture) or fully enclosed fall back to
        the full clone+apply check. Equivalence to the brute-force checker is
        verified in test_engine_fast.py.

        INFRA-2: the per-cell neighbor scan that used to live here was profiled
        (bench_infra1) as ~90% of MCTS time on 7^3, so the body now delegates to
        the numpy-vectorized legal_moves_vec. The original loop is preserved as
        legal_moves_loop for reference; both match brute force in
        test_engine_fast.py."""
        return self.legal_moves_vec()

    def legal_moves_loop(self):
        """Original pure-Python legal_moves (pre-INFRA-2), kept as reference."""
        out = []
        w, h, d = self.w, self.h, self.d
        color = self.player
        opp = other(color)
        history = self.history
        # NB: do NOT cache `self.grid` in a local — `_is_legal` rebinds self.grid
        # to a fresh snapshot on every call, so a cached reference goes stale.
        for x in range(w):
            for y in range(h):
                for z in range(d):
                    grid = self.grid
                    if grid[x, y, z] != EMPTY:
                        continue
                    has_empty = has_enemy = False
                    for dx, dy, dz in _NEI:
                        nx, ny, nz = x + dx, y + dy, z + dz
                        if 0 <= nx < w and 0 <= ny < h and 0 <= nz < d:
                            v = grid[nx, ny, nz]
                            if v == EMPTY:
                                has_empty = True
                            elif v == opp:
                                has_enemy = True
                    if has_empty and not has_enemy:
                        # captures nothing, not suicide -> only superko can forbid
                        if (self.zobrist ^ int(self._zob[x, y, z, color])) not in history:
                            out.append((x, y, z))
                    elif self._is_legal(x, y, z):
                        out.append((x, y, z))
        return out

    def legal_move_mask(self):
        """(w,h,d) boolean mask of legal plays for the side to move (INFRA-2).

        This is the engine's native MCTS interface: it returns the mask directly,
        with NO per-cell Python tuple building (legal_action_mask in az.py used to
        rebuild exactly this mask from a tuple list — the dominant MCTS cost on
        7^3 per `bench_infra1`). Logic: the per-cell neighbor scan is vectorized
        with boundary-safe numpy shifts; a fast-path point (empty neighbor, no
        enemy neighbor) captures nothing and isn't suicide, so only positional
        superko can forbid it — tested for ALL candidates at once via Zobrist
        (`zob ^ Z[cell,color]`) + np.isin against the history (no whole-board
        serialization, no Python loop). The few enemy-adjacent / enclosed points
        fall back to the exact clone+apply `_is_legal`. Equivalence to the
        brute-force checker is verified in test_engine_fast.py."""
        grid = self.grid
        w, h, d = self.w, self.h, self.d
        color = self.player
        opp = other(color)
        empty = grid == EMPTY
        enemy = grid == opp
        has_empty = np.zeros((w, h, d), dtype=bool)
        has_enemy = np.zeros((w, h, d), dtype=bool)
        # +/- along each axis, boundary-safe (no wraparound): a cell's neighbor in
        # +x is grid[x+1]; contribute it to cells 0..w-2, and the -x neighbor to 1..w-1.
        has_empty[:-1] |= empty[1:];   has_enemy[:-1] |= enemy[1:]
        has_empty[1:]  |= empty[:-1];  has_enemy[1:]  |= enemy[:-1]
        has_empty[:, :-1] |= empty[:, 1:];  has_enemy[:, :-1] |= enemy[:, 1:]
        has_empty[:, 1:]  |= empty[:, :-1]; has_enemy[:, 1:]  |= enemy[:, :-1]
        has_empty[:, :, :-1] |= empty[:, :, 1:];  has_enemy[:, :, :-1] |= enemy[:, :, 1:]
        has_empty[:, :, 1:]  |= empty[:, :, :-1]; has_enemy[:, :, 1:]  |= enemy[:, :, :-1]

        fast = empty & has_empty & ~has_enemy   # captures nothing, has a liberty -> only superko can forbid
        full = empty & ~fast                    # enemy-adjacent or enclosed -> exact check
        cand = self.zobrist ^ self._zob[:, :, :, color]   # (w,h,d) int64 candidate hashes
        if self.history:
            hist = np.fromiter(self.history, dtype=np.int64, count=len(self.history))
            banned = np.isin(cand, hist)
        else:
            banned = np.zeros((w, h, d), dtype=bool)
        legal = fast & ~banned
        if full.any():
            for x, y, z in np.argwhere(full):
                x, y, z = int(x), int(y), int(z)
                if self._is_legal(x, y, z):
                    legal[x, y, z] = True
        return legal

    def legal_moves_vec(self):
        """List form of legal_move_mask (the (x,y,z) tuples, sorted)."""
        return [(int(x), int(y), int(z)) for x, y, z in np.argwhere(self.legal_move_mask())]

    def _is_legal(self, x: int, y: int, z: int) -> bool:
        snapshot = self.grid.copy()
        zsnap = self.zobrist
        try:
            self._apply(x, y, z)
            ok = True
        except IllegalMove:
            ok = False
        self.grid = snapshot
        self.zobrist = zsnap  # _apply may have committed self.zobrist on success
        return ok

    def _apply(self, x: int, y: int, z: int) -> bytes:
        """Mutate grid for a play; raise IllegalMove (leaving grid dirty — caller
        must snapshot/restore on failure). Returns the new position hash."""
        if self.grid[x, y, z] != EMPTY:
            raise IllegalMove("occupied")
        color = self.player
        opp = other(color)
        Z = self._zob
        self.grid[x, y, z] = color
        new_zob = self.zobrist ^ int(Z[x, y, z, color])
        # Capture opponent groups with no liberties (priority over suicide).
        for nx, ny, nz in self._neighbors(x, y, z):
            if self.grid[nx, ny, nz] == opp:
                grp, libs = self._group(nx, ny, nz)
                if not libs:
                    for sx, sy, sz in grp:
                        self.grid[sx, sy, sz] = EMPTY
                        new_zob ^= int(Z[sx, sy, sz, opp])
        # Suicide check on the played group.
        _, libs = self._group(x, y, z)
        if not libs:
            raise IllegalMove("suicide")
        # Positional superko (Zobrist). Commit the incremental hash only on success;
        # raises above leave self.zobrist untouched (caller restores the grid).
        if new_zob in self.history:
            raise IllegalMove("superko")
        self.zobrist = new_zob
        return new_zob

    def play(self, x: int, y: int, z: int) -> None:
        snapshot = self.grid.copy()
        try:
            h = self._apply(x, y, z)
        except IllegalMove:
            self.grid = snapshot
            raise
        self.history.add(h)
        self.player = other(self.player)

    def pass_move(self) -> None:
        # Pass changes only the side to move; positions are not added to superko
        # history (no stone placed).
        self.player = other(self.player)

    def play_fast(self, x: int, y: int, z: int) -> bool:
        """Rollout-only move: capture + suicide rejection, but NO positional-superko
        check and NO history maintenance (Monte-Carlo playouts don't need superko;
        it only ever forbids a few moves and costs a whole-board hash each step).
        Returns True if played, False if the point was illegal (occupied/suicide);
        on False the grid is restored. ADDITIVE — does not touch play()/_apply, so
        the 60/60 cross-validation of the real move path is unaffected."""
        if self.grid[x, y, z] != EMPTY:
            return False
        snapshot = self.grid.copy()
        color = self.player
        opp = other(color)
        Z = self._zob
        self.grid[x, y, z] = color
        new_zob = self.zobrist ^ int(Z[x, y, z, color])
        for nx, ny, nz in self._neighbors(x, y, z):
            if self.grid[nx, ny, nz] == opp:
                grp, libs = self._group(nx, ny, nz)
                if not libs:
                    for sx, sy, sz in grp:
                        self.grid[sx, sy, sz] = EMPTY
                        new_zob ^= int(Z[sx, sy, sz, opp])
        _, libs = self._group(x, y, z)
        if not libs:
            self.grid = snapshot
            return False
        self.player = opp
        self.zobrist = new_zob  # keep the hash consistent for any later real play()
        return True

    def clone(self) -> "Board":
        b = Board.__new__(Board)
        b.w, b.h, b.d = self.w, self.h, self.d
        b.grid = self.grid.copy()
        b.player = self.player
        b.komi = self.komi
        b._zob = self._zob  # shared read-only table (same shape)
        b.zobrist = self.zobrist
        b.history = set(self.history)
        return b

    # --- scoring ------------------------------------------------------------
    def score_tromp_taylor(self):
        black_stones = int(np.count_nonzero(self.grid == BLACK))
        white_stones = int(np.count_nonzero(self.grid == WHITE))
        visited = np.zeros_like(self.grid, dtype=bool)
        black_terr = white_terr = neutral = 0
        for x in range(self.w):
            for y in range(self.h):
                for z in range(self.d):
                    if visited[x, y, z] or self.grid[x, y, z] != EMPTY:
                        continue
                    stack = [(x, y, z)]
                    visited[x, y, z] = True
                    region = 0
                    borders: set[int] = set()
                    while stack:
                        cx, cy, cz = stack.pop()
                        region += 1
                        for nx, ny, nz in self._neighbors(cx, cy, cz):
                            v = self.grid[nx, ny, nz]
                            if v == EMPTY:
                                if not visited[nx, ny, nz]:
                                    visited[nx, ny, nz] = True
                                    stack.append((nx, ny, nz))
                            else:
                                borders.add(int(v))
                    if borders == {BLACK}:
                        black_terr += region
                    elif borders == {WHITE}:
                        white_terr += region
                    else:
                        neutral += region
        black_area = black_stones + black_terr
        white_area = white_stones + white_terr + self.komi
        diff = black_area - white_area
        winner = "black" if diff > 0 else "white" if diff < 0 else "draw"
        return {
            "black_stones": black_stones,
            "white_stones": white_stones,
            "black_territory": black_terr,
            "white_territory": white_terr,
            "neutral": neutral,
            "diff": diff,
            "winner": winner,
        }
