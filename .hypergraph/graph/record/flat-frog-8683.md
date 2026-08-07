---
node_id: dacc5f7d-c7c5-587f-abb6-69956af8f2a0
slug: flat-frog-8683
title: 'Board characterization 3³/4³/5³: 4³ is the sweet spot; 5³ tractable-but-expensive; length scales 35→74→138 moves'
created_at: '2026-06-07T11:56:28.264354+00:00'
parents:
- withered-boat-6047
- crimson-voice-3644
summary: MCTS(96) self-play, komi 0, 60 games/size. Game length 35→74→138 moves; draws <5%; |margin| grows with N. Throughput 0.37→0.04→0.01 games/s/core (5³ ~37× slower than 3³ but still feasible in parallel). Mean-margin fair-komi estimates are noisy/blowout-dominated, agreeing with the komi node.
flywheel:
  node_id: dacc5f7d-c7c5-587f-abb6-69956af8f2a0
  slug: flat-frog-8683
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 7b860e48315604c4aeb3385aad325fa19d816a6456ec2385cc8070322337522d
---
# Q2 — Which board sizes are interesting and tractable?

## Method
`src/selfplay/experiments/exp_boards_parallel.ts` — MCTS(96) self-play at komi 0, 60 games/size, sharded across 30 cores. fairKomi≈ is the mean signed (blackArea−whiteArea) at komi 0 (a point estimate of fair komi); ±SE reflects per-game variance.

## Result
| size | blackWin% | draw% | avg moves | avg \|margin\| | fairKomi≈ (±SE) | games/s/core |
|---|---|---|---|---|---|---|
| 3³ | 50.0% | 1.7% | 34.9 | 11.8 | −0.03 (±1.95) | 0.37 |
| 4³ | 56.7% | 5.0% | 74.5 | 12.8 | +2.10 (±2.82) | 0.04 |
| 5³ | 43.3% | 3.3% | 138.4 | 14.6 | −5.68 (±3.59) | 0.01 |

## Findings
1. **Game length scales steeply with volume:** ~35 → 74 → 138 moves for 3³ → 4³ → 5³ (roughly linear in the number of points, 27→64→125).
2. **Tractability (CPU MCTS in TS):** per-core throughput falls 0.37 → 0.04 → 0.01 games/s — 5³ is ~37× slower than 3³. With the parallel harness, 60 games of 5³ still finished in ~6 min wall, so **5³ is tractable but expensive**; 7³/9³ would need a faster engine or the neural value net to be practical (a compute/engineering call, reported not spent).
3. **All sizes are blowout-prone:** draws stay <5% and |margin| (12–15) dwarfs komi granularity, so outcomes are decided by large territory swings — consistent with the Q1 komi node (komi hard to pin by win-rate).
4. **Fair-komi point estimates are noisy and not yet trustworthy:** 3³≈0, 4³≈+2.1, 5³≈−5.7 but with SEs of ±2–3.6 and even a sign flip at 5³ — a small-sample/high-variance artifact, not evidence White is favored on 5³. Tightening these needs lower-variance (stronger) agents, not just more games.

## Recommendation
**Focus the campaign on 4³** (and 5³ as the stretch): 3³ is, by the geometry node, essentially a 2D game (mean degree 4.0, one interior point) and borderline-trivial/blowout-prone; 4³ is genuinely 3D-flavored (12.5% interior), decisive (draws low), and cheap; 5³ is more strongly 3D (21.6% interior) and where the interesting bulk effects (ladders, life) live, at higher cost. 7³/9³ are deferred pending a faster engine / neural phase.

## Reproduce
`OUT=experiments/boards.json npx tsx src/selfplay/experiments/exp_boards_parallel.ts 60 96 "3,4,5"`. Artifact attached.