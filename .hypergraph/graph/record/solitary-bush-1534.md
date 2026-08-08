---
node_id: 298467fd-58f6-58b6-bbd4-702291415d9b
slug: solitary-bush-1534
title: Q3 — Do 2D tactics survive 6-connectivity
created_at: '2026-06-07T11:32:47.242714+00:00'
parents:
- purple-fog-6345
summary: 'Open question: do ladders/tactics work in 3D?'
origin:
  backend: flywheel
  node_id: 298467fd-58f6-58b6-bbd4-702291415d9b
  slug: solitary-bush-1534
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: baa2a2b8-efec-5e71-99be-ac25f6d79cb7
  slug: super-hill-7291
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: b6e59b1fb651528e338d970e5e8c8cce04b523ed22210f550f5fa4709b39e18a
---
# Q3 — Tactics under 6-connectivity

The **ladder** is the canonical case: a forced capture that keeps the victim pinned at exactly 2 liberties while chasing it to an edge. Whether it survives is open, because the liberties gained by extending depend on local connectivity (4-neighbor 2D vs 6-neighbor 3D).

## What to answer
- Does the ladder work in genuinely-2D topology (depth=1 control) vs a 3D surface vs the open 3D interior?
- Crux metric: liberties after the first forced atari+extend — if it climbs past the escape cap, atari cannot be maintained.

## Method
Exact bounded minimax ladder solver on identical setups across topologies; per-scenario WORKS? verdict.

Status: open.