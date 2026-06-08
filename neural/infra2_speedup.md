# INFRA-1/2 — GPU-batched MCTS bottleneck analysis & engine speedup

Local, $0, RTX 5090 + 16c/32t. Net = `best_distill7_7cubed.pt` (64×6) etc.
Benchmark harness: `neural/bench_infra1.py`. Raw data: `bench_infra1.json`.

## INFRA-1 finding — the GPU was never the wall
`BatchedMCTS` (M5) already batches all leaf evaluations across concurrent game
trees into one GPU forward per sim round. Profiling shows the GPU forward is only
**3–11 %** of move time; the rest is per-node Python **engine** cost. PASS-11's
"7³ sim-bound" slowness came from the *eval harness* running the net on CPU
(`net_vs_classical_mp.py`), not from a missing GPU server. So INFRA-1's premise
("build a GPU-batched server") was already satisfied; the real keystone is the
engine → INFRA-2.

## INFRA-2 — vectorized legal mask + Zobrist superko
Two changes to the a3go-authored Python engine (`a3go_engine.py`):
1. **Vectorized legal-move generation** — the per-cell Python neighbor scan
   (profiled at ~90 % of MCTS time on 7³) replaced by boundary-safe numpy shifts;
   the engine exposes a native `legal_move_mask()` returning the `(n,n,n)` mask,
   and `az.legal_action_mask` flattens it instead of rebuilding it from a tuple
   list cell-by-cell.
2. **Zobrist incremental hashing** for positional superko — `current ^ Z[cell,color]`
   tested for all fast-path candidates at once with `np.isin`, replacing a
   `grid.tobytes()` whole-board serialization per candidate. History is now a set
   of 64-bit ints; hash maintained incrementally through `play`/`_apply`/`play_fast`.

## Throughput (aggregate MCTS sims/s, batched on GPU)
| board | before | after | speedup |
|------:|-------:|------:|--------:|
| 4³ (B256,S256) | 10 148 | 13 556 | 1.33× |
| 5³ (B256,S256) |  6 447 | 12 398 | 1.92× |
| 7³ (B128,S512) |  2 747 |  9 688 | **3.53×** |
| 7³ (B128,S128) |  2 742 |  9 767 | 3.56× |

Profiled run (64 games × 256 sims, 7³): **11.85 s → 3.14 s (3.8×)**. GPU
utilization on 7³ rose 4.2 % → 14.7 %. The win scales with board size because
`legal_moves` cost scales with cells. 7³@512 is now ~53 ms/move/game amortized
vs PASS-11's ~12 min/game on CPU.

After the change the profile is flat (no single >15 % wall): `_group`/`_neighbors`
(floodfill for enemy-adjacent legality + captures), `_apply` (child expansion),
`_select` (PUCT). The remaining lever — incremental union-find liberties — is
diminishing returns and was deferred.

## Correctness (re-run after every change)
- `test_engine_fast.py` brute-force equivalence: **460/460**, 0 mismatches.
- Vectorized mask vs brute `_is_legal` across n=3,4,5,7: **485/485**.
- Incremental Zobrist == recompute-from-grid: **485/485**.
- `legal_action_mask` (mask path) == tuple-built mask: **0 mismatches**.
- Cross-validation vs TS engine: **60/60** (3³) and **60/60** (4³).
- `npm test` (TS engine, untouched): **48/48**.
