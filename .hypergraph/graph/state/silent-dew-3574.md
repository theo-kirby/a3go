---
node_id: cedaf6bd-f982-59e6-a167-81434dbf3d14
slug: silent-dew-3574
title: Engine & classical stack
created_at: '2026-08-07T20:33:39+00:00'
parents:
- royal-comet-4977
summary: Three validated engines (TS 48/48, Python vectorized+Zobrist 3.5x on 7^3, C++ generator 60x) + classical self-play; C++ teacher untuned and weaker than Python.
flywheel:
  node_id: 5e0cc3ae-8dd1-5c8d-a576-c888b84f00de
  slug: hidden-base-6660
  revision: 1
  pushed_at: '2026-08-07T21:11:50+00:00'
  content_sha256: 83fbc79f285c5ccd3ec9f3a7bac058f0d1d2f75c7d808dbc18a48670dee5d1e7
---
Status: working

## Current

- Three validated engines. TS reference (vendored from goban at commit c7b8266, positional superko, Tromp-Taylor scoring): `npm test` 48/48 [rec: lively-orchard-3365]. Python port `neural/a3go_engine.py`: cross-validated 60/60 vs TS on 3³ and 4³ [rec: restless-meadow-9547]; after INFRA-2 (vectorized legal-move mask + Zobrist incremental superko) throughput rose 1.33×/1.92×/3.53× on 4³/5³/7³, with correctness re-gated 460/460 brute-force + 485/485 mask/Zobrist + 60/60 crossval [rec: spring-cell-3370]. C++ generator: 60/60 crossval, ~60× classical self-play on 4³ and ~7× wall on 5³, unblocking 7³ data collection [rec: blue-boat-2948].
- Depth-1 boards are exactly 2D Go: Topology3D(n,n,1) ≡ Topology2D(n,n) exhaustively (n ≤ 19, 646 points) and 16/16 known-answer 2D rule checks (liberties, capture, suicide, ko/positional superko, hand-scored Tromp-Taylor) pass — no d=1 edge cases exist; probe at `src/selfplay/experiments/exp_2d_boundary.ts`, evidence `experiments/2d_boundary.json` [rec: icy-fjord-0022].
- Classical self-play stack (UCT MCTS, color-balanced match harness with CIs, parallel workers) drives all teacher-data collection and the experiment scripts for the science questions [rec: lively-orchard-3365].
- Caveat: the C++ MCTS teacher plays weaker than the Python one (downstream net 0.25 vs 0.417 point estimate, CIs overlap; ~194 vs 136 examples/game) and was never tuned — it silently caps every C++-generated dataset, including the 7³ scaling-law data [rec: blue-boat-2948].
- Doc drift: `src/engine/VENDORED.md` divergence log is empty because the hot-path optimization happened in the Python engine, outside that rule's scope [rec: lively-orchard-3365].

## Negative knowledge

- [scope: engine optimization on this stack | confidence: high | evidence: wild-poetry-7539, bold-pine-0367] Never trust an engine optimization without the brute-force equivalence gate — the M5 fast-path cached a stale self.grid and only the 460-case gate caught it (5 mismatches); a non-capturing move can still hit superko, so the hash check is mandatory, not optional.
- [scope: GPU-batched MCTS serving on this stack | confidence: high | evidence: broken-tree-4527] The GPU was never the wall — the batched forward is 3–11% of move time; the earlier 7³ sim-bound reading was a CPU eval-harness artifact. Profile before you build.

## Provenance

- lively-orchard-3365 — adoption distillation from repo docs + imported graph
- restless-meadow-9547 — Python engine port, 60/60 crossval
- spring-cell-3370 — INFRA-2 vectorized mask + Zobrist superko speedups
- blue-boat-2948 — C++ engine + generator; weaker-teacher caveat
- broken-tree-4527 — INFRA-1 falsified-premise profiling
- icy-fjord-0022 — 2D-boundary validation: (n,n,1) ≡ 2D Go, 16/16 checks
