---
node_id: 0844658b-97b8-5040-b6ec-4ee3c03a73e3
slug: cold-sun-4675
title: SEARCH-3 — Variance-scaled cPUCT + uncertainty-weighted playouts [MED, ~75 Elo]
created_at: '2026-06-09T07:00:09.555981+00:00'
parents:
- divine-thunder-7666
- empty-lab-3357
- broad-hall-8962
- proud-king-2753
summary: 'Implement KataGo''s dynamic exploration: scale cPUCT by observed value variance and weight playouts by uncertainty (~75 Elo claimed). Needs the per-node variance estimate from AUX-4. Extends ALGO-1 Gumbel 4cf07501 and PROOF-1 ladder 3ac354fd.'
flywheel:
  node_id: 0844658b-97b8-5040-b6ec-4ee3c03a73e3
  slug: cold-sun-4675
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: bbea8edb656b5f78bb5fb3b8fb8177fef5400a68dc526a604630574427281a80
---
# SEARCH-3 — Variance-scaled cPUCT + uncertainty-weighted playouts [MED, ~75 Elo]

## Objective
Replace the fixed exploration constant with a **variance-scaled cPUCT** (exploration grows where value estimates are uncertain) and **weight playouts by uncertainty** (spend more visits on high-variance subtrees). KataGo's dynamic-exploration package.

## Why it matters (which finding it extends)
Our MCTS uses a flat cPUCT and equal-weight playouts; KataGo reports **~+75 Elo** from making exploration *uncertainty-aware*. It directly improves search efficiency at low sims — the regime where our net's win is currently bounded (PROOF-1 `3ac354fd`: net loses to classical at high budget, wins at matched/low). A better low-sim search is the cheapest path toward S1 budget-dominance that doesn't require a bigger net. It needs a per-node value-variance signal, which **AUX-4** provides.

## Implementation route
In `az.py`: cPUCT_eff = f(running value-variance at the node); scale each child's playout contribution by its uncertainty. Tune the variance→exploration mapping. A/B on the PROOF-1 ladder across sim budgets (8/16/32/64/128).

## Decision criterion (CI-based, n≥128)
At n≥128 on the ladder: variance-scaled search gains ≥ +50 Elo over fixed-cPUCT at matched low sims with CI separation, and does not regress at high sims. SPRT-gate.

## Preconditions / risks
**Depends on AUX-4** (per-node variance estimate). Search-side only otherwise. Risk: variance estimates are noisy early in a tree (floor/clip them); interacts with Dirichlet noise (hold the noise schedule fixed during the A/B). Pairs with SEARCH-2.

## Cost · value
MED build. Value: KataGo's single largest search-time Elo item (~75); attacks the low-sim regime where our net is strongest, pushing toward S1.

## Expected artifacts
Variance-aware MCTS variant, an Elo-vs-sims JSON on the ladder (n≥128), a cPUCT-vs-variance tuning curve.

## Inspiration source
KataGo dynamic variance-scaled cPUCT + uncertainty-weighted playouts (~75 Elo). Needs AUX-4; extends ALGO-1 `4cf07501`, PROOF-1 `3ac354fd`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
