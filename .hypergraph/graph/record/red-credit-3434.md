---
node_id: 1b196886-c68a-5e19-81ca-c1c771d32e8c
slug: red-credit-3434
title: STRAT-1 — Center vs surface opening value on 5³/7³ (follow-up to the 4³ uniform-opening scar) [engine, cheap]
created_at: '2026-06-18T12:25:08.180655+00:00'
parents:
- proud-king-2753
summary: On 4³ the champion net had NO positional opening preference (~uniform corner/edge/face/interior, node 853d7c2c) — unlike 2D Go. Does that uniformity hold on bigger boards, or does the 6-neighbour interior become decisively strong on 5³/7³? Measure first-stone value by cell-type via short classical playouts. Engine-only, cheap.
flywheel:
  node_id: 1b196886-c68a-5e19-81ca-c1c771d32e8c
  slug: red-credit-3434
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 0ab3970740273bd29f8ea85e30d2d46d8229a5a23807ab719b58287b005105c0
---
# STRAT-1 — Center vs surface opening value on 5³/7³

## Objective
Quantify the value of the first stone as a function of cell type — corner (3 neighbours), edge (4), face (5), interior (6) — on 5³ and 7³, by fixed-opening classical playouts / net value. Test whether the 4³ "no opening preference" result (`853d7c2c`) is a small-board artefact or a genuine feature of 3D Go.

## Why it matters (which finding it extends)
One of the campaign's most surprising findings is that, unlike 2D Go (where corners/sides are worth more early), the 4³ champion played the opening ~uniformly (`853d7c2c`). 3D changes the economics: an interior cell has 6 liberties and radiates influence in 3 dimensions, so on a bigger board the center may become decisively strong (or the surface, for territory). This is the core of 3D opening/strategy science and directly informs SCI-1's opening explorer.

## Implementation route
Engine-only (+ optional net value). For each cell type, force the first move there, then evaluate the resulting position by (a) classical short-playout win-rate and/or (b) the trained net's value, averaged over symmetric cells (cube_symmetry dedupe). Compare across cell types and board sizes.

## Decision criterion (CI-based, n≥128)
n≥128 playouts/cell-type: first-move value by cell type with CIs, per board size. Decisive = a cell type CI-separated as best on 5³/7³ (preference emerges with size), or confirmation that uniformity persists. Either way resolves the `853d7c2c` open question at scale.

## Preconditions / risks
Engine validated; classical playout cheap (short). Risk: classical short-playouts are weak estimators — corroborate with the trained net's value head. Uses cube_symmetry for cell-type canonicalization.

## Cost · value
CHEAP (engine + forward-pass). High value: answers a named open question (`853d7c2c`) at scale; the empirical basis of 3D opening theory and SCI-1.

## Expected artifacts
`strat_opening.py`, first-move-value-by-cell-type JSON (per board size), a center-vs-surface curve vs board size.

## Inspiration source
2D Go opening theory (corner > side > center) vs the 3D uniformity surprise. Extends `853d7c2c`, feeds SCI-1 `5b0393b7`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-2 (3D tactical/positional knowledge axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*