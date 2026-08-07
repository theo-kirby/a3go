---
node_id: f35f453b-4ae8-5522-820e-81a1be7ca48c
slug: gentle-lake-8649
title: 'AZ regresses on 4³ even with Dirichlet noise — strength falls as loss drops (loses to its own init): needs replay buffer + best-net gating'
created_at: '2026-06-07T13:28:53.258029+00:00'
parents:
- crimson-frog-9812
- broken-firefly-1068
summary: 'Second AZ run: 4³, Dirichlet root noise, 6 gens. Draws dropped (4³ less drawish) but the agent gets WORSE — vs_random 0.74→0.57, vs_gen0→0.00 while loss falls 3.55→2.33. Classic catastrophic-forgetting signature from training on latest-gen-only + always-promote. Fix = replay buffer across gens + best-net gating (M4).'
flywheel:
  node_id: f35f453b-4ae8-5522-820e-81a1be7ca48c
  slug: gentle-lake-8649
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: ef4262b82c6bb4479525e25b09b7296c73594bc3da31d4d6dbecb83b8c698de0
---
# Phase 2 — AZ on 4³ with Dirichlet noise (second honest result)

## Change from M3
Added **Dirichlet root-exploration noise** (0.25 weight) to self-play and moved to **4³** (genuinely 3D, less draw-prone), low-temp *sampling* for net-vs-net eval.

## Result
| gen | vs random | vs gen0 | loss | self-play B/W/draw |
|---|---|---|---|---|
| 1 | 0.74 | 0.54 | 3.55 | 12/7/1 |
| 2 | 0.78 | 0.39 | 3.50 | 1/4/15 |
| 3 | 0.64 | 0.37 | 2.95 | 4/13/3 |
| 4 | 0.72 | 0.03 | 2.51 | 3/12/5 |
| 5 | 0.48 | 0.00 | 2.31 | 1/15/4 |
| 6 | 0.57 | 0.00 | 2.33 | 3/15/2 |

## Reading
- **Draw collapse fixed** by 4³ (draws now mostly low) — confirms 3³ was the wrong board (Q5: 3³≈2D, draw-prone).
- **But strength REGRESSES:** vs_random drifts down toward 0.5 and vs_gen0 falls to **0.00** — the trained net loses every (sampled) game to its *untrained initialization* — while training loss decreases. Self-play is strongly White-biased (e.g. 1/15 B/W), a degenerate-policy tell.

## Diagnosis (confident)
Loss↓ while strength↓ and losing to the init is the **catastrophic-forgetting + no-gating** signature:
1. **No replay buffer** — each generation trains only on its own ~20 self-play games, overfitting to a tiny, skewed sample and forgetting prior knowledge; the broad untrained prior generalizes better.
2. **Always-promote** — a bad generation permanently corrupts the self-play net; there is no check that the new net is actually stronger.
(Dirichlet noise was necessary but not sufficient.)

## Next milestone (M4, executing)
Proper AZ stability: **(a) replay buffer** spanning multiple generations; **(b) best-net gating** — only promote a new net if it beats the current best (≥55%); (c) more self-play volume/sims. Then re-measure the rising-strength curve (Q10) and net-vs-classical-MCTS.

## Reproduce
`uv run --directory neural python train.py 4 6 20 32 train_result_4.json 30`. Artifact attached.