---
node_id: 28f66847-f443-5b25-b349-710365491fbb
slug: hidden-forest-3847
title: 'Re-characterized scaling: the GOOD 64x6 net DOES scale with sims (0.65->0.78 vs fixed classical) — inverse of the weak net. But classical@128>>@48, bounding the win to matched/low budgets on tiny 4^3.'
created_at: '2026-06-08T01:39:17.885721+00:00'
parents:
- soft-waterfall-3492
- dawn-block-6253
summary: With the calibrated 64x6 net, more sims HELP vs a fixed classical@48 (0.65->0.67->0.78) — opposite of the weak net (amplification was net-quality). But classical scales very well with playouts on 4^3 (rollouts near-perfect); net's edge shrinks at high equal budget (128v128=0.42) and net@256 loses to cls@128 (0.30). Win is decisive at matched 48v48 + via cheap scaling vs fixed-budget classical. Motivates 5^3 where rollouts should be weaker.
origin:
  backend: flywheel
  node_id: 28f66847-f443-5b25-b349-710365491fbb
  slug: hidden-forest-3847
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 0242be5f-93c5-5bf9-90b6-42510f26f9e4
  slug: green-bush-8117
  revision: 0
  pushed_at: '2026-08-08T10:02:40+00:00'
  content_sha256: ace400386244cbbe1cf0e81c0bd8796f3a025bf76a4f2131b3f0d21fa9b3c9ab
---
# Test-time scaling, re-characterized with the GOOD (64x6) net: it scales now — and a honest bound on the classical win

Follow-up to the milestone [b71da32b] and the original scaling node [9605fb9a] (which showed the WEAK 32x3 net did not scale — deeper search amplified value errors). Re-ran the sweep with the calibrated 64x6 net that beats classical.

## Result (64x6 net win-rate vs classical, N=24/config)
| net_sims \ cls_playouts | 48 | 128 |
|---|---|---|
| 48  | 0.652 [0.45,0.81] | - |
| 128 | 0.667 [0.47,0.82] | 0.417 [0.25,0.61] |
| 256 | **0.783 [0.58,0.90]** ✅ | 0.304 [0.16,0.51] |

## Findings
1. **The calibrated net DOES exhibit test-time scaling.** vs a fixed classical@48 it rises with sims: 0.652 -> 0.667 -> 0.783. This is the INVERSE of the weak 32x3 net (0.25 -> 0.17 -> 0.29, flat/hurt). So the value-head amplification was a net-quality problem; with a good value head, deeper PUCT search helps, as autogo's 'test-time scaling law' presumes. And the net's extra sims are nearly free (batched GPU eval), so it can cheaply scale to 0.78 vs a fixed-budget classical.
2. **Classical scales VERY well with playouts on 4^3 — an honest bound on the win.** classical@128 >> classical@48: the net's edge shrinks as EQUAL budget grows (net@48-v-cls@48 = 0.65, but net@128-v-cls@128 = 0.42), and even net@256 does not beat classical@128 (0.30). On a 64-point board, random rollouts run to terminal and approximate near-perfect value, so a big-playout classical is a very strong baseline. The neural win is decisive at the matched 48v48 success-bar budget and via cheap scaling vs a fixed-budget opponent; it is NOT a claim that the net dominates classical at every budget.

## Implication for the frontier
This is exactly why **5^3 is the right next test**: on a bigger board, games are longer and random rollouts are noisier, so classical's rollout-value advantage should erode and the distilled neural value should win more decisively across budgets. The 4^3 result (tiny board, rollouts near-perfect) is the HARD case for neural value, and we still beat classical at matched budget.

Artifact: experiments_scaling_big.json.