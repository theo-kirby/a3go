---
node_id: 189adb1d-471a-5756-9cb3-27f29e9185df
slug: lively-sun-0512
title: 'GEO-2 — Value of the 3rd dimension: slab anisotropy & depth-2 tactics [science, engine, cheap]'
created_at: '2026-06-18T13:58:06.411038+00:00'
parents:
- proud-king-2753
summary: 'Zoom in on the bottom of the dimensionality ladder: how do tactics and territory change from a (n,n,1) sheet to a (n,n,2) bilayer to (n,n,3)? Depth-2 is the minimal 3D — stones gain exactly one cross-layer liberty. Quantify how that single extra dimension changes capture economics, connection, and life, where 3D-ness first switches on.'
origin:
  backend: flywheel
  node_id: 189adb1d-471a-5756-9cb3-27f29e9185df
  slug: lively-sun-0512
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 0c078be2-7afa-5cef-981a-b5c9b1a3a8e4
  slug: proud-firefly-5461
  revision: 0
  pushed_at: '2026-08-08T10:02:40+00:00'
  content_sha256: 513d106f8c94841ce790100e5d58ff5274836fef11e67c5f9d5f65b5df7d613e
---
# GEO-2 — Value of the 3rd dimension (slab anisotropy, depth-2 tactics)

## Objective
Study the low-depth regime of the dimensionality ladder in detail: (n,n,1) → (n,n,2) → (n,n,3). Depth-2 is the minimal genuine 3D board (each cell gains exactly one out-of-plane neighbour). Measure how connection, capture, eye-shape, and territory differ between a sheet, a bilayer, and a tri-layer, and on anisotropic boards (e.g. 5×5×2 vs 5×2×5).

## Why it matters (which finding it extends)
The most interpretable place to see "what the 3rd dimension does" is where it first appears. Going from d=1 to d=2 adds one liberty per cell and a whole new connection mode (cross-layer); this likely changes life-and-death (eyes can be 3D), ladders (PROOF on ladders), and the capture frequencies measured in 3DSCI-2. Anisotropy isolates whether it's depth per se or just more cells. Complements GEO-1 (the coarse ladder) with the fine structure at the 2D/3D boundary.

## Implementation route
Engine-only. Reuse `shape=(w,h,d)`; run motif census (3DSCI-2 harness), ladder/L&D probes, and small-net strength on d∈{1,2,3} and anisotropic shapes. Compare cross-layer vs in-layer capture/connection rates.

## Decision criterion (CI-based, n≥128)
n≥128 games/shape: CI-separated contrasts between d=1/2/3 and isotropic vs anisotropic on capture economics, eye-shape, and strength. Decisive = identify the specific tactic(s) the 2nd layer introduces.

## Preconditions / risks
Engine shape-agnostic (validated). Cheap. Risk: distinguishing depth effects from cell-count effects — anisotropic controls handle this.

## Cost · value
CHEAP (engine). High value: the fine structure of where 3D Go diverges from 2D; informs L&D (LD-1/2) and feature design.

## Expected artifacts
`slab_tactics.py`, a depth/anisotropy contrast JSON, cross-layer-vs-in-layer capture/connection stats.

## Inspiration source
Layered-board / quasi-2D physics intuition. Extends GEO-1, 3DSCI-2 `a9982d50`, LD-1 `2341cdd9`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-3 (geometry / dimensionality-ladder / search-structure axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*