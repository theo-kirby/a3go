---
node_id: 7390a76f-efa7-56c6-9052-a7513eb57030
slug: still-recipe-4954
title: 'GEO-1 — The 2D→3D dimensionality ladder: Go on (n,n,d) for d=1..n [edge science, engine, cheap]'
created_at: '2026-06-18T13:58:05.434703+00:00'
parents:
- proud-king-2753
summary: The engine supports non-cube (w,h,d) boards, so Go on (n,n,1)=pure 2D up to (n,n,n)=full 3D is a free interpolation no one has run. Map how komi, first-move value, capture economics, and net/classical strength change as the 3rd dimension grows from a slab to a cube — turning '2D vs 3D Go' from a dichotomy into a measured continuum.
origin:
  backend: flywheel
  node_id: 7390a76f-efa7-56c6-9052-a7513eb57030
  slug: still-recipe-4954
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 51158c87-2169-560f-8fce-5b0c65c8bf79
  slug: winter-bonus-7652
  revision: 1
  pushed_at: '2026-08-08T10:06:14+00:00'
  content_sha256: 1df4a627d1037606d20d0a9d3a61894d6c1ddcf0ab8e934fcd3f54dac3ffe570
---
# GEO-1 — The 2D→3D dimensionality ladder

## Objective
Characterize Go as a function of the 3rd dimension: play/evaluate on boards (n,n,d) for d = 1, 2, …, n (d=1 is exactly 2D 4-connectivity; d=n is the full cube). Measure how core quantities — fair komi, first-move advantage, capture/atari frequency, game length, and classical/net strength — vary along the ladder.

## Why it matters (which finding it extends)
The whole campaign treats "3D Go" as one thing, but the engine's `shape=(w,h,d)` support means 3D-ness is a DIAL. The dimensionality ladder is the cleanest possible experiment for *which* phenomena are intrinsically 3D vs continuous with depth — e.g. does the uniform-opening surprise (`853d7c2c`) appear only past some d? does fair komi grow with d? It reframes every board-size finding as a 2-parameter (area × depth) surface and is genuinely novel science (2D Go is the d=1 boundary condition).

## Implementation route
Engine-only + optional small nets. Reuse `Board(n, shape=(w,h,d))` (already shape-agnostic). For each (n,d): classical self-play for komi/first-move/motif stats (reuse motif_census.py, STRAT-1), optionally distill a small net per slab. No new engine work; the ladder is a loop over shapes.

## Decision criterion (CI-based, n≥128)
n≥128 games per (n,d): report komi, first-move value, motif rates, and strength vs the ladder, each with CIs. Decisive = at least one quantity with a clean monotone or threshold trend in d (CI-separated endpoints), identifying what the 3rd dimension actually changes.

## Preconditions / risks
Engine validated and already shape-agnostic (verify (n,n,1) reproduces a 2D engine on a known 2D position first). Cheap. Risk: d=1 superko/scoring edge cases — cross-check against a 2D reference.

## Cost · value
CHEAP (engine + small nets). Very high value: a single unifying experiment that contextualizes the entire campaign and yields a citable 2D→3D continuum result.

## Expected artifacts
`dim_ladder.py`, a (n,d)-surface JSON (komi/first-move/motifs/strength), ladder plots, a 2D-boundary validation note.

## Inspiration source
Dimensional interpolation / the engine's native (w,h,d) support. Unifies `853d7c2c`, STRAT-1 `1b196886`, the scaling law `0bc38c41`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-3 (geometry / dimensionality-ladder / search-structure axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*