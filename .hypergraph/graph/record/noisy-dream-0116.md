---
node_id: 3f5b8ced-032d-5faa-b7b7-6490aca088c7
slug: noisy-dream-0116
title: GEO-3 — Does 2D-Go knowledge climb the ladder? Cross-depth transfer (d=1→2→3) [edge hypothesis, eval]
created_at: '2026-06-18T13:58:06.971346+00:00'
parents:
- proud-king-2753
summary: 'Edge hypothesis along the depth axis: train a size-agnostic net on (n,n,1)=2D Go and evaluate it zero-shot on (n,n,2)/(n,n,3). If 2D tactics transfer to thin 3D slabs, the vast body of 2D Go knowledge becomes a warm-start for 3D, and a depth-curriculum (d=1→n) could bootstrap full 3D cheaply. The depth-axis analogue of TRANSFER-1.'
origin:
  backend: flywheel
  node_id: 3f5b8ced-032d-5faa-b7b7-6490aca088c7
  slug: noisy-dream-0116
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: b832ff19-57d5-5004-b216-512e7ec1694d
  slug: red-wood-1870
  revision: 0
  pushed_at: '2026-08-08T10:02:40+00:00'
  content_sha256: c40852661cdb4a8fc9b724b06a12591ab7c9797eab3c0426a8d4e15ec9d496f3
---
# GEO-3 — Cross-depth transfer (does 2D knowledge climb the ladder?)

## Objective
Test whether Go knowledge transfers ALONG the depth axis: train a depth-agnostic net on (n,n,1) (pure 2D) and evaluate zero-shot on (n,n,2), (n,n,3), …, then a depth curriculum d=1→n. Quantify retained strength vs the depth gap.

## Why it matters (which finding it extends)
2D Go is the most-studied game in AI; if its tactics transfer to thin 3D slabs, that is an enormous free prior for the 3D program and a cheap bootstrap for the 7³ wall. This is the depth-axis sibling of TRANSFER-1 (`0bbe92d5`, cross-area transfer) and operationalizes the GEO-1 ladder as a curriculum. A clean positive would reframe 3D Go as "2D Go + depth fine-tuning."

## Implementation route
Needs a depth-agnostic net (global-pool over the depth axis, or the ARCH-1 size-agnostic head `5f4399f0` extended to (w,h,d)). Train on d=1 slabs, eval on d=2/3 via net-vs-net vs a native-depth net + vs random (absolute). Then a d=1→n curriculum vs from-scratch.

## Decision criterion (CI-based, n≥128)
n≥128: zero-shot d=1→d=2 net beats random (CI-lower>0.5) and its Elo gap to native-depth; curriculum vs from-scratch at matched compute. Even weak positive transfer justifies the curriculum bootstrap.

## Preconditions / risks
Depends on ARCH-1 `5f4399f0` (depth/size-agnostic head) and GEO-1 (the ladder). Eval-heavy but cheap once the head exists. Risk: policy action-space differs by depth — global-pool or fully-conv policy.

## Cost · value
CHEAP-MED (mostly eval). High value: if positive, makes the full-3D / 7³ program affordable by importing 2D knowledge.

## Expected artifacts
Depth-agnostic checkpoint, cross-depth transfer JSON (d=1→2→3), curriculum-vs-scratch comparison.

## Inspiration source
Curriculum learning; KataGo multi-size training. Depth-axis analogue of TRANSFER-1 `0bbe92d5`; depends on ARCH-1 `5f4399f0`, GEO-1.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-3 (geometry / dimensionality-ladder / search-structure axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*