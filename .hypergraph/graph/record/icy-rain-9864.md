---
node_id: 9e7efc62-1eef-5f98-b4a4-097eba7a552c
slug: icy-rain-9864
title: Q6 — Seki in 3D, and does 6-connectivity change minimal life?
created_at: '2026-06-07T12:52:29.560477+00:00'
parents:
- green-queen-4645
summary: 'Follow-up to Q4: does seki (mutual life) occur in 3D and how often, and is there any compact 3D eye-shape that lives at a volume where the 2D analogue dies? Needs a two-group shared-liberty harness.'
flywheel:
  node_id: 9e7efc62-1eef-5f98-b4a4-097eba7a552c
  slug: icy-rain-9864
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: fc6785677bcbbc970ae0c08d8c4b944398aa5ac3f94fca648f46ae9d0eb824e0
---
# Q6 — Seki & whether 3D changes minimal life (← Q4)

Surfaced by the Q4 life & death result (which found two-eye life holds and small-volume verdicts match 2D).

## What to answer
- Does **seki** (mutual life: two enemy groups sharing liberties, neither able to approach without dying) occur on a 6-neighbor lattice? How common / how many shared liberties does it need vs 2D?
- Is there any **compact 3D eye-space** (vol 5–7: octahedron, 2×2×2-minus-corner, cross) that is unconditionally alive where its 2D-projected analogue is dead — i.e. does 3D ever make life *easier* per unit volume?

## Method
Extend the deterministic kill-search to **two groups** (attacker/defender both as real groups sharing the contested region); add seki detection (terminal where neither side can capture and both have liberties). Enumerate compact 3D shapes for the minimal-life question. Deterministic, cheap.

Status: OPEN (cheap deterministic win; highest value-per-cost non-neural branch).