---
node_id: 1f59266a-efca-539e-afab-be1f88c1f4d5
slug: tiny-term-8854
title: 'TOOL-1 — Visualization & figures [DELIVERED: 3D board renderer (slices+voxels) + JSON->PNG figure pipeline]'
created_at: '2026-06-08T12:15:36.496326+00:00'
parents:
- mute-cloud-4824
summary: DELIVERED. viz.py renders an N^3 position as z-slice goban layers + 3D voxels (policy/last-move overlays); figures.py turns each result JSON into a PNG. Benchmark figures attached to PROOF-1/2, INFRA-2, ALGO-1 nodes. matplotlib via uv. $0/local.
flywheel:
  node_id: 1f59266a-efca-539e-afab-be1f88c1f4d5
  slug: tiny-term-8854
  revision: 2
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 1a429baa329913af00389484d436309b3e9c248482a682987692f50da0c9cddf
---
# TOOL-1 — Visualization & figures [DELIVERED]

Built `viz.py` (3D board renderer: z-slice goban layers + 3D voxels, with last-move/policy/territory overlays) and `figures.py` (figure pipeline that turns each result JSON into a committed PNG). Figures attached to their result nodes: PROOF-1 Elo ladder, PROOF-2 scaling curves, INFRA-2 speedup, ALGO-1 Gumbel A/B; INFRA-3 self-play curve auto-generates once that run lands. Board-render samples attached here.

## Delivered
- `viz.render_slices(grid,...)` — the practical 3D view (one w×h plane per z), stones as goban stones, optional policy heatmap + last-move marker.
- `viz.render_voxels(grid,...)` — 3D voxel view.
- `figures.py` — ladder / scaling / engine / gumbel / az figures from JSON, one command.
- matplotlib(Agg) added to the uv project.

$0/local. Artifacts: sample board (slices + voxels) + a benchmark figure sample.