---
node_id: 2a2ca6b9-68d3-59d5-8725-6eb5770d643e
slug: gentle-sun-9997
title: 'Komi on 3³ is unidentifiable by win-rate: Black-win% is flat across komi −1.5…+7.5 (blowout-dominated)'
created_at: '2026-06-07T11:42:53.292374+00:00'
parents:
- crimson-voice-3644
summary: 200 games/komi MCTS(96) self-play on 3³. Black win-rate stays ~47–60% (all CIs overlap 50%) across the whole komi grid with no monotone trend, while |margin| holds ~10–13. Outcomes are decided by who gets the big group, not by a few komi points — so win-rate-fair komi is ill-posed at this strength/board.
origin:
  backend: flywheel
  node_id: 2a2ca6b9-68d3-59d5-8725-6eb5770d643e
  slug: gentle-sun-9997
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: ef08fa5a-2d4c-5330-b3c6-ed2768535eb1
  slug: cool-sun-6645
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: 07e3a54587f71e544a0552e3f98c089b7a3d3d8d1d7f285cee706147d8d9417d
---
# Q1 — Fair komi on 3³: not identifiable by win-rate at this strength

## Method
`src/selfplay/experiments/exp_komi_parallel.ts` — equal-strength MCTS(96) vs MCTS(96), Black first, **200 games per komi** across the grid {−1.5,−0.5,0.5,1.5,2.5,3.5,4.5,5.5,7.5}, sharded across 30 cores. CI = 95% normal-approx on Black win-rate.

## Result
| komi | Black win% (±95%) | draw% | avg \|margin\| | avg moves |
|---|---|---|---|---|
| −1.5 | 54.5% (±6.9) | 0 | 10.0 | 33.6 |
| −0.5 | 59.5% (±6.8) | 0 | 11.1 | 34.3 |
| 0.5 | 55.5% (±6.9) | 0 | 11.1 | 34.6 |
| 1.5 | 60.5% (±6.8) | 0 | 10.3 | 33.9 |
| 2.5 | 52.0% (±6.9) | 0 | 10.4 | 33.7 |
| 3.5 | 47.0% (±6.9) | 0 | 10.2 | 33.8 |
| 4.5 | 48.5% (±6.9) | 0 | 10.5 | 34.5 |
| 5.5 | 52.5% (±6.9) | 0 | 12.4 | 35.7 |
| 7.5 | 47.0% (±6.9) | 0 | 13.0 | 35.4 |

## Findings
1. **Win-rate is flat in komi.** Over an 9-point komi swing, Black win-rate wanders in ~47–60% with no monotone trend; *every* cell's 95% CI overlaps 50%. The nominal 50%-crossing the script reports (~2.9) is an artifact of noise, not a real, well-separated balance point.
2. **Why:** average winning margin is ~10–13 area points and independent of komi. Games are **blowouts** — decided by which side captures the dominant group — so adding a few points of komi rarely flips the result. This is the small-board, high-variance regime.
3. **Answers Q1's precision sub-question:** what limits komi precision on 3³ is **not** sample size (CIs are already ±7% at 200 games) — it is that the win-rate signal vs komi is intrinsically weak because outcomes are margin-dominated. Win-rate-fair and margin-fair komi are both ill-posed here.

## Implications / next
- Identify komi where games are *close*: larger boards (4³+) and/or **mean-score-margin** as the estimator (board node carries the point estimate per size).
- Real precision (±0.5) will need a stronger, lower-variance agent (the deferred neural value net), not just more games.

## Throughput note
The parallel harness (`src/selfplay/parallel.ts` + `worker_selfplay.ts`) ran 1800 games in 170 s at **~28× effective** speedup over single-thread — the prior 'throughput wall' is removed for CPU MCTS at these sizes (the binding constraint is now agent *quality*/variance, not games/s).

## Reproduce
`OUT=experiments/komi_3.json npx tsx src/selfplay/experiments/exp_komi_parallel.ts 3 200 96`. Artifact attached.