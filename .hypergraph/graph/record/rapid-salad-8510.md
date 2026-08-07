---
node_id: 42747f38-817c-542c-9561-5966c8c96cf0
slug: rapid-salad-8510
title: 'REP-1 — 3D structural-geometry planes: neighbor-count / distance-to-surface / face-type [novel rep, cheap train]'
created_at: '2026-06-18T11:52:26.049144+00:00'
parents:
- proud-king-2753
summary: '3D boards have structurally distinct cells the net is blind to: an interior cell has 6 neighbors, a face has 5, an edge 4, a corner 3 — vs 2D''s flat 4/3/2. Encode neighbor-count (max-liberty ceiling) and distance-to-nearest-surface as static input planes. Hypothesis: handing the net the board geometry it can''t infer lifts strength like liberties did.'
flywheel:
  node_id: 42747f38-817c-542c-9561-5966c8c96cf0
  slug: rapid-salad-8510
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 588e8a2beea9beede1b46f1b01a92e6eea4ca138691c58b7fbc489d133f96cf2
---
# REP-1 — 3D structural-geometry planes (neighbor-count / distance-to-surface)

## Objective
Add static input planes encoding each cell's 3D geometry: (a) neighbor-count / max-liberty ceiling (3 for corner … 6 for interior), (b) distance-to-nearest-surface, optionally (c) a one-hot face/edge/corner/interior type. These are board-fixed (no per-position compute) but the convolutional net cannot recover absolute position from a translation-equivariant trunk without them.

## Why it matters (which finding it extends)
3D Go's defining difference from 2D is that interior cells have 6 liberties — capture/life-and-death economics differ wildly between center and surface. Liberty planes (ARCH-3 `bcf93cd3`) helped by exposing tactical state; geometry planes expose the *structural* prior that should make a group's liberty count interpretable in context (1 liberty on a corner vs interior means different things). The ~uniform-opening finding (`853d7c2c`) hints the net has no positional sense — geometry planes are the cheapest fix.

## Implementation route
Add geometry channels to `input_planes` (computed once per board size, broadcast). New CONFIG entries `geom`, `libs+geom`. Reuse collect/train/screen_nvn unchanged (just new channel indices). Cheap GPU train (same ~20-min budget) + net-vs-net screen vs `libs` and `base`.

## Decision criterion (CI-based, n≥128)
net-vs-net: `libs+geom` CI-separated above `libs` at n≥128/3-seeds ⇒ geometry adds signal on top of liberties; or `geom`-alone above `base` ⇒ structural prior alone helps. Negative is also informative (net already infers geometry from board edges).

## Preconditions / risks
Train-side; GPU free. Risk: static planes are constant across positions, so the net might learn them as bias quickly with little gain — pairs best with liberties. Low implementation risk (no per-cell loop).

## Cost · value
CHEAP train. Value: tests whether the 5³ gain generalizes from tactical (liberties) to structural (geometry) input — a distinct, untried representation axis.

## Expected artifacts
Geometry-plane builder + unit test, `geom`/`libs+geom` checkpoints, net-vs-net screen JSON vs libs/base.

## Inspiration source
KataGo's on-board location features; the 6-neighbor interior unique to 3D. Extends ARCH-3 `bcf93cd3`, opening-uniformity `853d7c2c`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20. Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*