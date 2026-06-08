"""Verify the fast legal_moves fast-path is exactly equivalent to a brute-force
reference (every empty point checked via clone+apply), over many random
positions across board sizes. Guards the M5 engine optimization."""
from __future__ import annotations
import random
from a3go_engine import Board, EMPTY


def brute_legal(board: Board):
    out = []
    for x in range(board.w):
        for y in range(board.h):
            for z in range(board.d):
                if board.grid[x, y, z] == EMPTY and board._is_legal(x, y, z):
                    out.append((x, y, z))
    return out


def main():
    rng = random.Random(12345)
    mismatches = 0
    positions = 0
    for n in (3, 4, 5):
        for trial in range(200 if n < 5 else 60):
            b = Board(n)
            steps = rng.randint(0, n * n * n)
            for _ in range(steps):
                mv = b.legal_moves()
                if not mv:
                    break
                # occasionally pass to vary side-to-move / superko history
                if rng.random() < 0.1:
                    b.pass_move()
                    continue
                x, y, z = rng.choice(mv)
                try:
                    b.play(x, y, z)
                except Exception:
                    pass
            fast = sorted(b.legal_moves())
            brute = sorted(brute_legal(b))
            positions += 1
            if fast != brute:
                mismatches += 1
                if mismatches <= 3:
                    from a3go_engine import _NEI, other, IllegalMove
                    print(f"MISMATCH n={n} trial={trial} player={b.player}")
                    for p in sorted(set(fast) - set(brute)):
                        x, y, z = p
                        nbrs = [int(b.grid[x+dx, y+dy, z+dz])
                                for dx, dy, dz in _NEI
                                if 0 <= x+dx < n and 0 <= y+dy < n and 0 <= z+dz < n]
                        b.grid[x, y, z] = b.player
                        ph = b.grid.tobytes()
                        b.grid[x, y, z] = 0
                        reason = "ok"
                        try:
                            b._is_legal_probe = b._is_legal(x, y, z)
                        except Exception as e:
                            reason = repr(e)
                        print(f"  fast-only {p}: nbr_colors={nbrs} "
                              f"ph_in_hist={ph in b.history} is_legal={b._is_legal(x,y,z)}")
                    print("  only in brute:", sorted(set(brute) - set(fast)))
    print(f"positions checked: {positions}  mismatches: {mismatches}")
    print("PASS" if mismatches == 0 else "FAIL")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
