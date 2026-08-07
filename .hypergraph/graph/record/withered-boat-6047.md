---
node_id: 3925fffd-6e43-5179-84ca-a2d415c02f91
slug: withered-boat-6047
title: Q2 — Which board sizes are interesting & tractable
created_at: '2026-06-07T11:32:46.638758+00:00'
parents:
- purple-fog-6345
summary: 'Open question: which N³ sizes to focus on?'
flywheel:
  node_id: 3925fffd-6e43-5179-84ca-a2d415c02f91
  slug: withered-boat-6047
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: a0c20c3d30f9fb6e7824e3858a1c24abae5d79c58ede9f8fdf9fa69d8f099c3a
---
# Q2 — Board sizes

Candidates: 3³, 4³, 5³, 7³, 9³.

## What to answer
- Which are trivial / near-solved, which are decisive vs draw-prone?
- How does game length scale with N?
- Which are **computationally tractable** for self-play on this hardware (games/s)?
- Recommend the size(s) the campaign should focus on.

## Method
MCTS self-play (komi 0) across sizes; report avg |margin|, draw rate, avg moves, and games/s (throughput). Triviality cross-checked against Q1 komi-sensitivity.

Status: open.