---
node_id: 8fca18c1-0657-5330-a005-58253fa27535
slug: green-queen-4645
title: Q4 — Life & death in 3D Go
created_at: '2026-06-07T11:32:47.865152+00:00'
parents:
- purple-fog-6345
summary: 'Open question: what is life on a 6-neighbor lattice?'
origin:
  backend: flywheel
  node_id: 8fca18c1-0657-5330-a005-58253fa27535
  slug: green-queen-4645
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: db3ca53d-050d-539b-8805-4eba1a55ed37
  slug: square-river-6565
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: e3fa69c8b1299d468e77bada35cf8db1bfe2437a89aa2f07dd44d4f7c137ca17
---
# Q4 — Life & death

In 2D, two eyes = unconditional life. The analogue on a 6-neighbor lattice is open.

## What to answer
- Minimum eye space for life in 3D; is two-eye life still the sufficient condition?
- Does **seki** (mutual life) occur, and how often?
- Is life & death harder or easier to read than in 2D?

## Method
Constructive engine search: build candidate eye shapes / groups and verify (un)conditional life by exhaustive bounded search on whether the opponent can kill; enumerate small eye spaces. Deterministic, cheap.

Status: open (no probe yet).