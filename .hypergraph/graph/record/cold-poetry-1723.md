---
node_id: 8c790338-cbbd-598c-ac01-d8f6d95fc321
slug: cold-poetry-1723
title: EVAL-3 — Train-time × test-time scaling-law characterization (strength surface) [MED]
created_at: '2026-06-09T07:00:16.181180+00:00'
parents:
- delicate-breeze-7763
- rapid-hat-7732
- proud-king-2753
summary: 'Reframe the campaign''s cross-board law as autogo''s central scaling thesis: map strength as a joint surface over training compute (net size × data) × test-time search × board size. A strong ''science'' headline once the aux/capacity nets exist. Extends scaling-law 0bc38c41 and PROOF-2 search-scaling 75615ad2.'
flywheel:
  node_id: 8c790338-cbbd-598c-ac01-d8f6d95fc321
  slug: cold-poetry-1723
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 733212d47276b930ed03514d56dcafbe868b42697fb25bd4e522c1c81e04dddc
---
# EVAL-3 — Train-time × test-time scaling-law characterization (strength surface) [MED]

## Objective
Characterize a3go strength as a **joint scaling surface**: strength (vs a fixed anchor) as a function of **train-time compute** (net capacity × data volume) **× test-time search** (sims) **× board size** — autogo's central train-time + test-time scaling-law study, instantiated for 3D Go.

## Why it matters (which finding it extends)
We already have the two marginal slices: the cross-board law `0bc38c41` (value easier / policy harder / sims grow with size) and PROOF-2 `75615ad2` (test-time search scaling *amplifies* with board size). autogo's thesis is that the *joint* train×test surface is the real object of study. Mapping it turns our scattered findings into one quantitative law and tells us **where compute is best spent** per board size (more net vs more search vs more data) — a strong, legible science headline. Best run *after* the aux/capacity nets (AUX-1/2, ARCH-1/2) exist so the train-time axis spans a meaningful capacity range.

## Implementation route
Grid: {net sizes} × {data volumes} × {sim budgets} × {board sizes}, each evaluated vs a fixed classical/frozen anchor at n≥128 (SPRT-gated, EVAL-1). Fit strength = f(train_flops, sims, size); identify iso-strength contours and the compute-optimal allocation per board.

## Decision criterion (CI-based, n≥128)
Deliverable is a fitted strength surface with CIs + the compute-optimal frontier per board size. Criterion: the joint law either extends cleanly (a stronger, more general result than the two marginals) or bends, with the bend characterized — reported with n≥128 anchored measurements.

## Preconditions / risks
Eval-heavy (many matchups) but each is cheap post-INFRA-2; SPRT (EVAL-1) keeps it affordable. **Best after** AUX-1/2 + ARCH-1/2 so the capacity axis is real. GPU for nets, CPU for classical anchor. Risk: combinatorial blowup — sample the grid, don't enumerate; log what's skipped (no silent caps).

## Cost · value
MED-HIGH build (mostly orchestration + compute). Value: a flagship science result that unifies the campaign's scaling findings and guides compute allocation.

## Expected artifacts
Strength-surface dataset + fitted law, iso-strength/compute-optimal figures, a scaling-law writeup tying `0bc38c41` + `75615ad2` into one surface.

## Inspiration source
autogo train-time + test-time scaling-law thesis `b4fd8252`. Extends scaling-law `0bc38c41`, PROOF-2 `75615ad2`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
