---
node_id: 4d8fb650-a223-53fb-802e-fc37880c86ed
slug: noisy-bonus-3509
title: 'distill->self-play: warm net beats distilled 0.75 head-to-head & random 0.91 but is WORSE vs classical (0.333->0.222) — self-play improvement actively misleads without an external anchor'
created_at: '2026-06-07T21:27:32.014229+00:00'
parents:
- round-wave-9279
- lively-meadow-0948
summary: 'Warm-started AZ self-play from the distilled net (annealed Dirichlet + gating, 5 promos/10 gens) improved every self-referential metric (beats distilled 0.75, random 0.91, old self-play net 0.64) yet DROPPED absolute strength vs classical from 0.333 to 0.222. Net-vs-net gating let the net drift off the classical-quality target. Fix: anchor the gate to classical MCTS. Distillation-alone remains the best 4^3 lever.'
flywheel:
  node_id: 4d8fb650-a223-53fb-802e-fc37880c86ed
  slug: noisy-bonus-3509
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: b3871574b846d2c3a8a62fcbc6a743a4764d61b5a3fc4958803b16123dbfd6b9
---
# distill -> self-play (autogo pipeline): self-play IMPROVES every self-referential metric but DEGRADES absolute strength vs classical

Following the distillation result (distilled net beats classical 0.333) [4c377ef1], we ran autogo's distill->self-play pipeline: warm-start AZ self-play from the distilled net, with **annealed Dirichlet noise** (0.25->0.05, autogo's anti-collapse fix) and **best-net gating**, sims=64, 10 gens x 80 games on 4^3.

## Self-play metrics: clear, fast improvement
5 promotions/10 gens (first promotion at gen 1, vs gen-4 for cold-start). loss 1.68->0.92. The final warm net:
- beats uniform random **0.91**
- beats its distilled init **0.75** head-to-head (N=200)
- beats the PASS-3 from-scratch self-play net **0.638**

By every self-referential measure it is the strongest net in the campaign.

## Absolute strength vs the classical anchor: it got WORSE
| net | vs classical MCTS, equal 48v48 | 95% CI |
|---|---|---|
| from-scratch self-play (P3) | 0.085 | [0.034, 0.199] |
| **distilled from classical** | **0.333** | [0.217, 0.475] |
| distill + self-play (warm) | **0.222** | [0.125, 0.363] |

The warm net beats the distilled net 75% head-to-head, yet is WORSE than it against classical (0.333 -> 0.222).

## The finding (sharpens the Pass-4 lesson)
**Self-play improvement is self-referential and here actively MISLEADS.** With net-vs-net gating, self-play optimized a within-population objective: the net learned to beat its own lineage and random, drifting AWAY from the classical-quality policy it was distilled from. The self-play ladder rose while absolute strength fell — the exact inverse ordering. This is not 'self-play WR is a noisy proxy' (Pass 4); it's 'self-play WR moved opposite to truth.'

## Actionable correction
The drift happened because **gating was self-referential**. Anchor promotion to the EXTERNAL baseline: promote a candidate only if it beats classical MCTS at least as often as the current best does (or mix classical-anchored eval into the gate). Equivalently, keep distilling from an ever-stronger classical teacher rather than letting unanchored self-play set the target. On 4^3, **distillation-from-classical alone is the best lever to date** (0.333), and is far more compute-efficient than self-play (192 classical games + supervised vs 960 self-play games).

## autogo cross-check
Consistent with autogo's 'self-play optimized for one objective can degrade another' (their Dirichlet-across-iterations collapse). Annealed noise + gating did NOT prevent absolute-strength drift here, because the gate itself was the unanchored objective.

Artifacts: train_batched_warm.json (curve), experiments_warm_vs_classical.json, experiments_warm_vs_nets.json.