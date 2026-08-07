---
node_id: 897fb2e0-d11a-5a49-8cdf-3d086d42c1ca
slug: polished-snow-4561
title: '3D does NOT make life easier per volume: minimal unconditional eye-space life = straight-four in both 2D and 3D; compact vol-4 shapes (square-four, 3D tripod) dead'
created_at: '2026-06-07T13:06:22.680586+00:00'
parents:
- icy-rain-9864
summary: 'Extended the exact life/death solver to compact 3D shapes (vol 4-8). Every shape''s 3D verdict equals its 2D analogue: straight-4 alive, square-four & 3D-tripod-4 dead, straight-5/cross-5/octahedron-7/cube-8 alive. 6-connectivity does not lower the minimal-life threshold. Seki (two-group) deferred to its own careful sub-pass.'
flywheel:
  node_id: 897fb2e0-d11a-5a49-8cdf-3d086d42c1ca
  slug: polished-snow-4561
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 7130165cd468040a0f29fff0b8f0ddd1795d3789ec223a8c40285cdf4c1bee25
---
# Q6 — Does 6-connectivity change minimal life? **No (per-volume).**

## Method
Extended `exp_lifedeath.ts` (the validated attacker-moves-first kill-search) with compact 3D shapes and their 2D analogues. Same exact memoized minimax; all searches completed within the 4M-node budget.

## Result (additions to the Q4 table)
| shape | dims | vol | verdict | nodes |
|---|---|---|---|---|
| 3D tripod-4 (pt + 1 step/axis) | 3D | 4 | **DEAD** | 32 |
| straight-5 | 2D | 5 | ALIVE | 305 |
| straight-5 | 3D | 5 | ALIVE | 305 |
| planar cross-5 (+) | 3D | 5 | ALIVE | 367 |
| 3D octahedron-7 (pt + 6 nbrs) | 3D | 7 | ALIVE | 2025 |
| 2x2x2 cube | 3D | 8 | ALIVE | 5255 |

(with Q4's earlier rows: straight-4 ALIVE both dims; square-four & all vol-3 DEAD both dims.)

## Finding
**Across every shape tested, the 3D verdict equals the 2D verdict**, and the minimum unconditionally-alive single eye space is the **straight-four (vol 4)** in both dimensionalities. Crucially, the *compact* vol-4 3D shape (tripod: a point plus one step along each axis) is **DEAD**, exactly like the compact 2D vol-4 (square-four) — only the *straight* four lives. So extra dimensions do **not** make life easier per unit volume; the 'killer takes the vital point' logic carries directly into 3D. This is a mildly surprising negative result (one might expect more liberties to aid the defender — they do not at small volume).

## Why it connects
Consistent with the ladders result and the geometry node: 6-connectivity helps the *attacker/escapee* dynamics (more liberties when extending) but does not hand the defender cheaper life. Eye-space shape, not raw connectivity, governs life as in 2D.

## Deferred (recorded, not rushed)
**Seki** (two-group mutual life) needs a dedicated two-group race harness — the single-group solver can't represent it. Per L&D discipline, this is its own careful sub-pass (does seki exist in 3D; is the 2-shared-liberty threshold preserved under 6-connectivity?). Tracked on the agenda.

## Reproduce
`OUT=experiments/lifedeath_v2.json npx tsx src/selfplay/experiments/exp_lifedeath.ts` (deterministic). Artifact attached.