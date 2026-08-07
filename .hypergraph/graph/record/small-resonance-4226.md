---
node_id: 2f9033d9-42b9-5b75-bc40-d1309fc85e37
slug: small-resonance-4226
title: 'M4: gating fixes the regression (no more forgetting) but the net plateaus at baseline — rising strength now needs self-play VOLUME (batched inference), not a bug fix'
created_at: '2026-06-07T14:35:43.833469+00:00'
parents:
- crimson-frog-9812
- broken-firefly-1068
summary: 'AZ + replay buffer + best-net gating on 4³ (8 gens, 64 min). Gating prevented all regression: candidate never beat best (cand_vs_best 0.24-0.48 < 0.55), so best stayed = gen0 and best_vs_random held 0.58-0.79. But training never surpassed the untrained-MCTS baseline. Method is now correct+stable; the binding constraint is self-play data volume (un-batched per-node GPU calls are too slow). Next: batched/vectorized self-play.'
flywheel:
  node_id: 2f9033d9-42b9-5b75-bc40-d1309fc85e37
  slug: small-resonance-4226
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: e52238b0abc7ae46a8e5d8aa5f602d42720f0b183faae48df7a1924d3a2b5727
---
# Phase 2 milestone 4 — replay buffer + best-net gating (stability achieved; scale is the new wall)

## Change from M3b
Added the two missing AZ stability ingredients: a **multi-generation replay buffer** (deque, 12k examples) and **best-net gating** (a trained candidate replaces the self-play net only if it beats it ≥55%). Kept Dirichlet root noise. 4³, 8 generations, 24 self-play games/gen, 32 sims, 64 min on RTX 5090.

## Result
| gen | cand_vs_best | promoted | best_vs_random | best_vs_gen0 | loss |
|---|---|---|---|---|---|
| 1 | 0.29 | no | 0.67 | 0.30 | 4.41 |
| 2 | 0.24 | no | 0.67 | 0.59 | 3.56 |
| 3 | 0.25 | no | 0.79 | 0.52 | 3.64 |
| 4 | 0.33 | no | 0.58 | 0.18 | 3.88 |
| 5 | 0.48 | no | 0.71 | 0.38 | 3.43 |
| 6 | 0.40 | no | 0.62 | 0.54 | 3.60 |
| 7 | 0.37 | no | 0.79 | 0.70 | 3.45 |
| 8 | 0.39 | no | 0.71 | 0.36 | 3.44 |

## Findings
1. **Regression eliminated.** With gating, the self-play net never gets worse: best_vs_random stays 0.58-0.79 across all 8 gens (vs M3b where it decayed toward 0.5 and vs_gen0 hit 0.00). The M3/M3b failure was indeed catastrophic forgetting + always-promote, now fixed. best_vs_gen0 ~0.5 confirms best stayed = gen0.
2. **But no improvement either.** The trained candidate **never beats the untrained-net MCTS baseline** (cand_vs_best peaks at 0.48 < 0.55), so nothing promotes. Loss drops (4.4→3.4) without translating to playing strength: at 32 sims, MCTS with a random-prior net + value≈0 is already a decent player, and the small net trained on only ~24 games/gen can't add enough signal to surpass it.
3. **The binding constraint is self-play VOLUME, and it is a throughput problem.** Un-batched MCTS does one GPU forward per tree node → 64 min bought only 8×24=192 self-play games. Neural training needs orders of magnitude more data.

## Next milestone (M5) — the clear lever
**Batched / vectorized self-play:** run many games concurrently and batch the net evaluations into single GPU calls (and/or larger sims, bigger net, more games/gen). This is exactly the 'fast enough to generate self-play data at volume' goal in neural/README. It is /bin/bash/local (GPU is free) but a real engineering build; the per-call Python MCTS is the bottleneck, not the GPU. Only after that can the rising-strength curve (Q10) and value-head komi (Q9) be fairly tested.

## Honest status of the neural kickoff
Pipeline: correct (engine cross-validated 60/60), stable (gating, no regression), end-to-end on GPU. What it has NOT yet shown: a net stronger than classical MCTS or a rising-strength curve — both gated on self-play volume (M5). This is a clean, well-characterized checkpoint.

## Reproduce
`uv run --directory neural python train_gated.py 4 8 24 32 train_gated_4.json 24`. Artifact attached.