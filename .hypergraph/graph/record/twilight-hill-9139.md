---
node_id: f70cb8c1-b1d7-5aa9-b063-b86c3bc90762
slug: twilight-hill-9139
title: 'TOOL-3 — 3D game-review UI: ownership heatmap + score-estimate bar + win-rate graph + SGF-equiv record [MED, after aux heads]'
created_at: '2026-06-09T07:00:17.715596+00:00'
parents:
- tiny-term-8854
- frosty-bar-2241
- throbbing-unit-0557
- proud-star-4959
- proud-king-2753
summary: 'Build an online-go-style 3D game-review UI: per-voxel ownership heatmap (from AUX-1), live score-estimate bar (from AUX-2), per-move win-rate graph, move-by-move review with variations, over an SGF-equivalent 3D record. Extends TOOL-1 1f59266a, TOOL-2 742a0aab; consumes AUX-1, AUX-2.'
flywheel:
  node_id: f70cb8c1-b1d7-5aa9-b063-b86c3bc90762
  slug: twilight-hill-9139
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 42abb12645282ec7a86ab5ec9d12cb28e39e8a1e819eb69f5aaa907b27667195
---
# TOOL-3 — 3D game-review UI: ownership heatmap + score-estimate bar + win-rate graph + SGF-equiv record [MED, after aux heads]

## Objective
Build a 3D **game-review / analysis UI** on top of the existing renderer: per-voxel **ownership heatmap** (AUX-1), live **score-estimate bar** + fair-komi readout (AUX-2), per-move **win-rate graph**, **move-by-move review with variation branches**, all over an **SGF-equivalent 3D game record**.

## Why it matters (which finding it extends)
TOOL-1 `1f59266a` (voxel/slice renderer) and TOOL-2 `742a0aab` (`play.py` with live policy/value) already render boards and read out the net; the missing layer is *review/analysis* — the thing that makes games legible to a human and exposes what the net understands. The ownership and score overlays are **free once AUX-1/AUX-2 exist** (their head outputs *are* the overlays), so this node is the natural consumer of the aux-head cluster and the payoff for SCIENCE/legibility work. An SGF-analogue also makes games shareable/replayable (none exists yet).

## Implementation route
Define an SGF-equivalent 3D record (coords + captures + komi + per-move value/ownership/score); extend `viz.py`/`figures.py` to render ownership as a per-voxel heatmap and score/win-rate as time-series; add a review navigator (step/branch, re-analyze a position with the net). Drive overlays from AUX-1/AUX-2 head outputs.

## Decision criterion (CI-based, n≥128)
Deliverable is a working review tool: load a game, scrub moves, see ownership/score/win-rate overlays, fork a variation and have the net analyze it. Criterion: renders real self-play games end-to-end with overlays sourced from the live aux heads (qualitative gate; not a strength A/B). Validate overlays against final scored ownership/margin.

## Preconditions / risks
**Depends on AUX-1 + AUX-2** (overlay sources). Tooling/viz only; matplotlib via uv (as TOOL-1/2). Risk: 3D ownership is hard to read — use slice + voxel views (TOOL-1's approach); keep it a research tool, not a product. After-aux-heads priority.

## Cost · value
MED build. Value: legibility + science payoff; turns the aux heads into a human-facing analysis loop; reusable for SCI-1's opening explorer.

## Expected artifacts
3D review UI (`review.py`), the SGF-equivalent record format + a sample recorded game, ownership/score/win-rate overlay figures on a real game.

## Inspiration source
online-go.com game-review UI (ownership/score overlays, win-rate graph, opening explorer, SGF record). Extends TOOL-1 `1f59266a`, TOOL-2 `742a0aab`; consumes AUX-1/AUX-2.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
