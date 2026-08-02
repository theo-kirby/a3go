"""Pin the lazy config_planes encoder to the reference rich_planes.

input_planes.config_planes computes ONLY the channels a config selects (skipping
the expensive per-empty-cell ko/capture zobrist loop for configs that need neither),
the key speedup for net-vs-net screening. This guards that the lazy path is
byte-identical to rich_planes(board)[CONFIG_CHANNELS[cfg]] across board sizes,
many random positions (stones / captures / ko / history), and all six configs.
"""
from __future__ import annotations
import random
import numpy as np

from a3go_engine import Board
import input_planes as IP


def random_board(n: int, plies: int, seed: int) -> Board:
    rng = random.Random(seed)
    b = Board(n)
    passes = 0
    for _ in range(plies):
        mv = b.legal_moves()
        if not mv or rng.random() < 0.03:
            b.pass_move(); passes += 1
            if passes >= 2:
                break
            continue
        b.play(*rng.choice(mv)); passes = 0
    return b


def main() -> int:
    configs = list(IP.CONFIG_CHANNELS)
    checks = mismatches = 0
    for n in (3, 4, 5, 7):
        for seed in range(40):
            b = random_board(n, n * n * n, seed)
            for cfg in configs:
                ref = IP.rich_planes(b)[IP.CONFIG_CHANNELS[cfg]]
                fast = IP.config_planes(b, cfg)
                checks += 1
                if not np.array_equal(ref, fast):
                    mismatches += 1
                    print(f"MISMATCH n={n} seed={seed} cfg={cfg}")
    if mismatches:
        print(f"FAIL — {mismatches}/{checks} mismatched")
        return 1
    print(f"PASS — config_planes == rich_planes-slice on {checks} (board,seed,cfg) cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
