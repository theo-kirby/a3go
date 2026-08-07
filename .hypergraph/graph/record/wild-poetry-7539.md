---
node_id: 427f4188-31d9-5302-9ec3-78985791c344
slug: wild-poetry-7539
title: 'M5 DONE: batched game-parallel self-play = 22x throughput (0.05->1.1 games/s on 4^3); the GPU wall is broken'
created_at: '2026-06-07T15:56:02.521635+00:00'
parents:
- crimson-frog-9812
- broken-firefly-1068
summary: 'Game-parallel MCTS with a single batched GPU forward per sim round lifts 4^3 self-play from 0.05 to 1.11 games/s (22x). Engine legal_moves fast-path adds ~13%. Verified: 460/460 legal-move equivalence, 60/60 TS crossval. Unblocks Q9/Q10.'
flywheel:
  node_id: 427f4188-31d9-5302-9ec3-78985791c344
  slug: wild-poetry-7539
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 0a186964be147fe32666a27dc78c41bcc17a99273aa2370c2117d91bedb7e085
---
# M5 — batched / game-parallel MCTS self-play

**The wall (from M4):** classical az.MCTS does one GPU forward per tree-node expansion (batch=1), so the RTX 5090 idle-waits on Python. Measured baseline: **0.05 self-play games/s on 4^3** (train_gated_4.json = 192 games / 3867 s, sims=32). M4 concluded the net plateaus at baseline because *volume* is the bottleneck, not a bug.

## What was built (`batched_az.py`)
Many independent game-trees run in lockstep. Each simulation round, every live tree descends by PUCT to exactly one leaf; ALL leaves needing evaluation across all trees are evaluated in a **single batched forward pass**, then expanded + backed up. Trees are independent so there is no in-tree leaf collision (no virtual loss needed). Same PUCT / priors / backup-sign convention as `az.py`. Covers self-play AND evaluation (`match_vs_random_batched`, `match_net_vs_net_batched`).

## Microbench (4^3, eval ms/pos)
| batch | 1 | 8 | 32 | 128 | 256 | 512 |
|---|---|---|---|---|---|---|
| ms/pos | 0.254 | 0.031 | 0.0079 | 0.0020 | 0.0012 | 0.0008 |

batch=256 is **210x** cheaper per position than batch=1. After batching, the residual wall is pure-Python `legal_moves` (0.199 ms/call, floodfill x64 cells).

## Engine fast-path (`a3go_engine.legal_moves`)
An empty point with an empty orthogonal neighbour and **no adjacent enemy** cannot be suicide and captures nothing, so it can only be illegal by **positional superko** — tested by a cheap board-hash check (set cell, hash, restore) instead of the capture/suicide floodfill. **Subtlety that bit me:** a non-capturing move CAN still hit superko (intervening captures mean adding a stone can recreate an earlier whole-board position), so the hash check is required, not optional.

## Result
**0.05 -> 1.11 games/s on 4^3 (22.2x).** legal_moves fast-path contributes ~13% on top of the batched-eval win.

## Correctness (non-negotiable — engine is cross-validated)
- `test_engine_fast.py`: **460/460** positions match a brute-force legal-move reference across 3^3/4^3/5^3.
- `crossval.py`: **60/60** games match the TS reference on both 3^3 and 4^3 after all changes.
- **Lesson:** my first fast-path cached `self.grid` in a local — but `_is_legal` rebinds `self.grid` to a fresh snapshot, leaving the cached ref stale/dirty and corrupting later iterations. The equivalence test caught 5/460 mismatches before I trusted it. Test the engine before believing an optimization.

## Decision
M5 met its bar: a large, verified throughput multiple sufficient to run volume training. Did NOT pursue GPU-multiprocessing across CPU cores — an external vLLM process holds 28/32 GB VRAM, leaving ~4 GB; spawning many CUDA contexts risks OOM-ing a critical process. Single-process batched is the safe, sufficient win.

Artifacts: experiments_m5_throughput.json (numbers), batched_az.py / bench_batched.py / bench_hotpath.py / test_engine_fast.py (code is in the repo at the commit below).