---
node_id: 14377685-99ff-581d-8208-e4d8519b2b28
slug: spring-cell-3370
title: 'INFRA-2 — vectorized legal mask + Zobrist superko [RESOLVED: 3.5x MCTS throughput on 7^3]'
created_at: '2026-06-08T06:51:10.606780+00:00'
parents:
- blue-boat-2948
- mute-cloud-4824
summary: RESOLVED. Vectorized legal-move mask (numpy shifts + native legal_move_mask) + Zobrist incremental superko (np.isin, no tobytes) -> 3.53x on 7^3 / 1.9x 5^3 / 1.3x 4^3; profiled 11.85s->3.14s (3.8x), GPU util 7^3 4%->15%. Validated 460/460 brute, 485/485 vec+zobrist invariants, 60/60 crossval, npm 48/48. Unblocks PROOF-1/S4/PROOF-2/INFRA-3. Union-find liberties deferred (diminishing). $0/local.
origin:
  backend: flywheel
  node_id: 14377685-99ff-581d-8208-e4d8519b2b28
  slug: spring-cell-3370
  revision: 3
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 9f44c087-b204-584f-8323-eda5ebb272ed
  slug: billowing-firefly-1877
  revision: 0
  pushed_at: '2026-08-08T10:03:07+00:00'
  content_sha256: ebf0dc3d88b1496a04b4b9bb151e7d2eb73fa8938d5e5713c4b33e8b57506e9e
---
# INFRA-2 — Incremental engine (vectorized legal mask + Zobrist superko) [RESOLVED — 3.5x on 7^3]

## Result: ~3.5x MCTS throughput on 7^3 (the S4 board), fully validated.
INFRA-1 profiling showed per-node `legal_moves` was ~90% of MCTS time on 7^3. Two
changes to the a3go-authored Python engine (`a3go_engine.py`):
1. **Vectorized legal-move generation** — the per-cell Python neighbor scan
   replaced by boundary-safe numpy shifts; engine now exposes a native
   `legal_move_mask()` returning the (n,n,n) mask, and `az.legal_action_mask`
   flattens it (C-order) instead of rebuilding it cell-by-cell from a tuple list.
2. **Zobrist incremental superko hashing** — candidate position hash = `zob ^
   Z[cell,color]`, tested for all fast-path candidates at once via `np.isin`,
   replacing a `grid.tobytes()` whole-board serialization per candidate. History
   is now a set of int64; hash maintained through play/_apply/play_fast/clone.

## Throughput (batched GPU MCTS, sims/s)
| board | before | after | speedup |
|---|---|---|---|
| 4^3 | 10148 | 13556 | 1.33x |
| 5^3 | 6447 | 12398 | 1.92x |
| 7^3 | 2747 | 9688 | **3.53x** |

Profiled (64 games x 256 sims, 7^3): **11.85s -> 3.14s (3.8x)**. GPU util on 7^3
4.2% -> 14.7%. The win scales with board size (legal_moves cost ~ cells). 7^3@512
now ~53ms/move/game amortized (PASS-11: ~12 min/game on CPU). Post-change profile
is flat — no single >15% wall — so the remaining lever (incremental union-find
liberties) is diminishing returns and was DEFERRED.

## Correctness — re-validated after every edit (the Pass-3 'test before trusting' scar)
- Brute-force equivalence `test_engine_fast.py`: **460/460**.
- vec mask vs brute `_is_legal` (n=3,4,5,7): **485/485**.
- incremental Zobrist == recompute-from-grid: **485/485**.
- mask path == tuple-built mask: **0 mismatch**.
- Cross-validation vs TS engine: **60/60** (3^3), **60/60** (4^3). seki3d OK.
- `npm test` (TS engine untouched): **48/48**.

## Engine divergence note
All changes are in the a3go-authored Python port (`neural/a3go_engine.py`,
`neural/az.py`), NOT the vendored TS `src/engine` — so VENDORED.md is unaffected.
Original pure-Python `legal_moves` kept as `legal_moves_loop` for reference.

## Unblocks: PROOF-1 (Elo ladder eval), S4 (7^3 decisive), PROOF-2 (high-sim sweeps), INFRA-3 (AZ self-play) — all now ~2-3.5x cheaper. Stop reason: objective_met.