---
node_id: 8efebfc4-92a1-5a96-982a-e1aa07da7302
slug: tiny-night-5466
title: Q7 — Ko / superko frequency & dynamics in 3D
created_at: '2026-06-07T12:52:30.324881+00:00'
parents:
- frosty-bread-3825
summary: 'Follow-up to Q5: how often do ko / superko situations arise in 3D self-play and how do they resolve? Positional-superko is implemented in the engine; measure its real-game incidence.'
flywheel:
  node_id: 8efebfc4-92a1-5a96-982a-e1aa07da7302
  slug: tiny-night-5466
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: d4ac901d2e4a4ee2e83168b37f5226ec542986d5933203c15817ebd5ed42e7c4
---
# Q7 — Ko / superko frequency & dynamics (← Q5)

## What to answer
- How frequently do single-point ko recaptures and positional-superko violations arise in 3D self-play, vs intuition from 2D?
- Are there 3D-specific repetition patterns (the engine uses positional superko / hashPosition excludes side-to-move)?

## Method
Instrument self-play (or a dedicated probe) to count superko-illegal move attempts and ko-shaped recaptures per game across board sizes; construct minimal ko/superko positions deterministically to confirm engine behavior. Cheap-to-medium.

Status: OPEN.