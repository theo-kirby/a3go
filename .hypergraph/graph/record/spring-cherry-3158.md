---
node_id: 5d318812-9ce7-5e3e-a6dc-360091ee8413
slug: spring-cherry-3158
title: '5^3 neural self-play: TRACTABLE via M5 (0.122 g/s, 12x classical, all-decisive) but strength is volume-gated — 224-game run stayed below 4^3''s ~320-game ignition threshold (0 promotions)'
created_at: '2026-06-07T18:33:13.525554+00:00'
parents:
- withered-boat-6047
- broken-firefly-1068
summary: 'M5 makes 5^3 neural self-play feasible: 0.122 games/s (12x pass-1 classical), 0 draws (less degenerate than 3^3/4^3). But an 8-gen x 28-game (224 total) gated run got 0 promotions — below 4^3''s first-promotion volume (~320 games). 5^3 strength is volume-gated; binding constraint is wall-clock (~9x slower/game). Follow-up: a >=960-game 5^3 run.'
origin:
  backend: flywheel
  node_id: 5d318812-9ce7-5e3e-a6dc-360091ee8413
  slug: spring-cherry-3158
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: d7b281bf-b3ad-5e2e-ae05-2aa1219be35e
  slug: patient-glitter-4462
  revision: 0
  pushed_at: '2026-08-08T10:01:49+00:00'
  content_sha256: e87b685660b6e521283d880de7248125bf8f45b3646ecbc976aa61b902c848be
---
# 5^3 neural self-play — tractability (Q2) and a volume-gated strength attempt (Q10)

Pass 1 flagged 5^3 as 'tractable-but-expensive' for classical TS MCTS (~0.01 games/s/core). With M5 batched self-play we can now ask: is 5^3 tractable for NEURAL self-play, and does rising strength appear?

## Tractability (Q2): YES
Batched game-parallel self-play on 5^3 runs at **0.122 games/s** (16 games / 131 s, sims=48) — ~**12x** the pass-1 single-core classical rate. Games are **all-decisive (0 draws)** on 5^3, unlike the draw-prone 3^3/4^3 — the bigger board is less degenerate. So 5^3 neural self-play is feasible for the first time.

## Rising strength (Q10) attempt: NOT achieved in this run (volume-gated)
Gated training, 8 gens x 28 games, sims=48, eval=16 (kept small to bound wall-clock — 5^3 self-play is ~9x slower per game than 4^3). Result: **0 promotions / 8 gens**; cand_vs_best stayed 0.0-0.21 (never near the 0.55 gate); vs_random bounced 0.50-0.81 (noisy gen-0 baseline, N=16). 68 min total.

| gen | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| loss | 3.68 | 3.46 | 3.37 | 2.47 | 3.20 | 2.77 | 2.70 | 3.24 |
| cand_vs_best | 0.20 | 0.15 | 0.00 | 0.13 | 0.15 | 0.07 | 0.21 | 0.13 |

## Why — and the honest framing
This is the **pre-ignition cold-start regime**, NOT evidence that 5^3 can't learn. On 4^3, the FIRST promotion came at gen-4 = ~**320 buffered self-play games**; this 5^3 run reached only **224 games total** (8x28), below that ignition threshold. The candidate-trained-from-best loop needs enough diverse buffer before a candidate can beat the (gen-0) best — 4^3 showed exactly this lag before igniting. So:

**5^3 strength is volume-gated, and the binding constraint is WALL-CLOCK**: igniting the flywheel needs 4^3-level volume (>~320 games, ideally 80+ games/gen as on 4^3), which at 0.122 g/s is ~9x more wall-clock than 4^3 (a full 4^3-style run, 80x12=960 games, would be ~2.2 hr of self-play alone on 5^3, plus eval). M5 makes 5^3 tractable per-game; it does not make a full 5^3 campaign cheap.

## Recommended follow-up (frontier)
A proper 5^3 run at ignition volume: >=80 games/gen, >=12 gens (>=960 games), sims>=64 for stronger targets, eval>=30 for a clean gate. Budget the wall-clock (~3-5 hr, still \$0/local). Then re-measure rising strength + fair komi on 5^3 (komi may be larger than 4^3's ~0.5 given the all-decisive games and bigger first-move value).

Artifacts: train_batched_5.json (curve), best_batched_5cubed.pt (= gen-0, since no promotion), bench result inline (0.122 g/s).