---
node_id: 48ef927d-c321-5140-8ebe-c5f9311917c3
slug: wild-glade-7676
title: STRAT-2 — How far does a stone radiate? 3D influence/territory-correlation function [science, engine, cheap]
created_at: '2026-06-18T12:25:09.086664+00:00'
parents:
- proud-king-2753
summary: 'Measure the empirical ''influence'' of a stone in 3D: from many self-play games, the correlation between a stone at cell c and final ownership at distance r. 2D Go influence falls off in 2 dimensions; 3D''s 6-connectivity should spread it differently. Quantifies the reach that any influence-based feature or evaluation must capture. Engine/stats, cheap.'
origin:
  backend: flywheel
  node_id: 48ef927d-c321-5140-8ebe-c5f9311917c3
  slug: wild-glade-7676
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: d4414910-aa78-5bf1-ab6c-fcba4276524b
  slug: wispy-river-8363
  revision: 0
  pushed_at: '2026-08-08T10:02:40+00:00'
  content_sha256: 743109af42b86cb8c1e084e8542d2319645947a9fcbedff2dd5399e6e4139e09
---
# STRAT-2 — 3D influence / ownership-correlation function

## Objective
Empirically characterize a stone's "influence" in 3D: from a corpus of self-play games, estimate P(final owner = mover | a mover-stone at cell c, Manhattan/Euclidean distance r) as a function of r and cell type. The 3D analogue of 2D Go influence/territory functions.

## Why it matters (which finding it extends)
Influence — how far a stone projects control — underlies territory, frameworks, and positional judgement. In 2D it decays over a 2D neighbourhood; in 3D the 6-connectivity and larger surface-to-volume ratio should change both the reach and the decay shape. This gives a quantitative, model-free picture of 3D positional value (complementing STRAT-1's opening result and the AUX-1 ownership head `665706e4`), and tells feature designers the spatial scale a conv trunk must cover.

## Implementation route
Engine/stats only. Reuse the AUX-1 ownership maps (`board.ownership_map`) over a set of self-play games; for each placed stone, accumulate the ownership outcome at each distance shell r; normalize to an influence-vs-distance curve, split by cell type and game phase. No training.

## Decision criterion
An influence-vs-distance curve with CIs (per cell type / board size), and the characteristic decay length. Descriptive science; "decisive" = a clean, interpretable decay-length estimate and at least one CI-separated contrast (e.g. interior radiates further than surface).

## Preconditions / risks
Needs a self-play game corpus (the existing distill games or fresh classical games) + ownership maps (already in the engine). Cheap. Risk: confounding by game length/strength — condition on phase; report the estimator clearly.

## Cost · value
CHEAP (stats over existing games). High value: a first quantitative map of 3D positional influence; informs receptive-field/feature-scale choices and the review-UI overlays (TOOL-3).

## Expected artifacts
`strat_influence.py`, an influence-vs-distance curve JSON + plot (per cell type / board size), a decay-length estimate.

## Inspiration source
2D Go influence functions / territory heuristics; KataGo ownership. Extends AUX-1 `665706e4`, feeds SCI-1 `5b0393b7`, TOOL-3 `f70cb8c1`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-2 (3D tactical/positional knowledge axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*