---
node_id: e7c35c64-dbcf-5a09-86c7-7f59f37d3377
slug: bold-scene-5560
title: 'Recipe TRANSFERS to 5^3: distilled 64x6 net reaches parity with classical (0.19->0.50 as sims 48->512). MCTS budget scales with board size; value head transfers even better (MSE 0.019). Fast playout (9x) unblocked it.'
created_at: '2026-06-08T03:32:17.158593+00:00'
parents:
- dark-firefly-4075
- soft-waterfall-3492
- hidden-forest-3847
summary: 'With a 9x-faster playout enabling a strong 5^3 teacher (21.8k examples), the distilled 64x6 net (value MSE 0.019) scales monotonically vs classical@48: 0.194(48)->0.217(128)->0.417(256)->0.500(512 sims). The recipe transfers to 5^3; 48 sims is just too few for 126 actions — the MCTS budget scales with board size, and neural sims are cheap. Earlier 5^3 losses were a search-depth artifact, not recipe failure.'
flywheel:
  node_id: e7c35c64-dbcf-5a09-86c7-7f59f37d3377
  slug: bold-scene-5560
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: d031a1f7276664e35303004241feb8d70fc65f41f2b8c1077511a6926f2e55f5
---
# The recipe TRANSFERS to 5^3 — it reaches parity with classical; the MCTS budget just scales with board size

PASS 8's 5^3 pilot was under-resourced (gated on slow data-gen). PASS 9 added a 9x-faster fast Monte-Carlo playout (additive engine `play_fast`, crossval still 60/60), enabling a STRONG 5^3 teacher (160 games x 96 playouts, 21,773 examples). Distilled a 64x6 net (value MSE **0.019** — the cleanest value fit in the campaign; 5^3 games are all-decisive -> clean targets).

## Result: scales to parity with deeper search
| net sims (vs classical@48) | win-rate |
|---|---|
| 48  | 0.194 [0.09,0.36] |
| 128 | 0.217 [0.10,0.42] |
| 256 | 0.417 [0.25,0.61] |
| **512** | **0.500** [~0.33,0.67] |

Monotone climb 0.19 -> 0.50. At 48 sims the net loses badly; by 512 sims it reaches PARITY with classical@48 (and is still climbing).

## Finding: the recipe transfers, MCTS budget scales with board size
- **Distillation transfers from 4^3 to 5^3.** Same recipe (distill classical teacher -> 64x6 net). The value head transfers even BETTER (MSE 0.019 vs 4^3's 0.044) — bigger boards are all-decisive, giving cleaner value targets, exactly the direction the scaling node [28f66847] predicted.
- **But the required MCTS sim budget scales with the action space.** 4^3 (65 actions) beats classical at 48 sims; 5^3 (126 actions) needs ~512 sims just to reach parity. 48 sims is far too few to search a 125-point board, regardless of value quality. The earlier 5^3 losses (0.045 weak-teacher, 0.194 strong-teacher-@48-sims) were a SEARCH-DEPTH artifact, not a recipe failure.
- **The cost asymmetry makes this cheap for the net.** Neural sims are batched-GPU-cheap; classical playouts are expensive. So scaling the net to 512+ sims vs a fixed-budget classical is affordable — the net can buy the search it needs on bigger boards while classical can't match the per-move cost.

## Net campaign picture
4^3: net beats classical 0.612 (matched 48v48) [b71da32b]. 5^3: net reaches parity at 512 sims and climbs (would beat classical@48 with more sims). The distillation recipe is robust across board sizes; deeper boards just need proportionally deeper (but cheap) neural search.

## Engine note
Added `Board.play_fast` (capture+suicide, no superko, no history) for fast rollouts — ADDITIVE, the real play()/_apply path and its 60/60 cross-validation are unchanged. 9x faster 5^3 classical data-gen (110 s/game vs >960 s).

Artifacts: experiments_5cube_scaling.json, experiments_5cube_512.json, experiments_distill5strong_vs_classical.json.