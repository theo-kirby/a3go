---
node_id: d1a8d69c-8881-5967-9976-85a7f143c191
slug: crimson-rice-4497
title: ROBUST-1 — Does a cube-trained net generalize to slabs & odd shapes? [forward-pass probe, cheap]
created_at: '2026-06-18T13:58:09.247432+00:00'
parents:
- proud-king-2753
summary: 'A cheap robustness probe: take the existing 5³ net and evaluate it (via global-pool inference or as-is) on non-cube shapes the engine supports — slabs (5,5,2), bricks (5,4,3), bigger faces. Does cube-trained knowledge survive shape shift, or is it brittle? Tells us whether one net can serve the whole geometry family or each shape needs its own. Forward-pass/eval only.'
flywheel:
  node_id: d1a8d69c-8881-5967-9976-85a7f143c191
  slug: crimson-rice-4497
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: added42095f38e88bd44260ca5c8b740997877a309ea8626b8408ef41db3e9b4
---
# ROBUST-1 — Non-cube shape generalization of a cube-trained net

## Objective
Measure how the existing 5³-trained net behaves on the non-cube shapes the engine supports — slabs (n,n,2), bricks (n,m,d), larger single faces — to see whether cube-trained knowledge is shape-robust or brittle. Requires a shape-agnostic inference path (global pooling) since the current heads are fixed-size.

## Why it matters (which finding it extends)
The geometry axis (GEO-1/2/3) assumes knowledge can span shapes; ROBUST-1 tests the cheap end of that assumption directly with the net we already have. If a cube net degrades gracefully on slabs, one net can serve the whole (w,h,d) family (huge for the dimensionality ladder + 7³ program); if it shatters, each shape needs dedicated training and ARCH-1 size/shape-agnostic heads become a hard prerequisite. A fast reality check before investing in GEO-3 transfer.

## Implementation route
Forward-pass/eval. Needs a global-pool wrapper so the fixed FC heads accept arbitrary (w,h,d) (or restrict to shapes matching the trunk's spatial reduction). Evaluate net-vs-random and policy sanity (does it find captures/atari?) on each shape; compare degradation vs the cube baseline.

## Decision criterion (CI-based, n≥128)
n≥128 games/shape: net-vs-random win-rate and basic-tactic accuracy per shape vs the cube baseline. Decisive = graceful degradation (still ≫ random on slabs) vs collapse — a clear go/no-go for the one-net-many-shapes hypothesis.

## Preconditions / risks
Needs the global-pool inference path (shares with ARCH-1 `5f4399f0`). Cheap, no training. Risk: the fixed-size heads can't run other shapes without pooling — implement the wrapper first or restrict to compatible shapes.

## Cost · value
CHEAP (forward-pass). High value: a fast go/no-go on shape generalization that de-risks the entire geometry axis and the curriculum bootstrap.

## Expected artifacts
Global-pool inference wrapper, per-shape net-vs-random + tactic-accuracy JSON, a degradation-vs-shape plot.

## Inspiration source
Robustness / distribution-shift testing; KataGo's single-net-many-sizes. Gateways GEO-1/3, depends on ARCH-1 `5f4399f0`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-3 (geometry / dimensionality-ladder / search-structure axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*