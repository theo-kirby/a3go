---
node_id: 23ef7556-518f-5d58-8fa1-2827cf39985c
slug: floral-river-3044
title: 'Q8 — Positional value: corner vs edge vs face vs interior'
created_at: '2026-06-07T12:52:31.027423+00:00'
parents:
- frosty-bread-3825
summary: 'Follow-up to Q5/Q2: what is the first-move / occupancy value of the four position classes (degree 3/4/5/6) the geometry node identified? Does the high-degree interior or the boundary hold more value?'
origin:
  backend: flywheel
  node_id: 23ef7556-518f-5d58-8fa1-2827cf39985c
  slug: floral-river-3044
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 18bcdeda-bd3e-5c51-9b8b-9b2a7dcccdba
  slug: crimson-thunder-5354
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: 9c9c073469d9d088f1b3535af1be1e6760659de92b537d720e49e38b4091205c
---
# Q8 — Positional value of the four classes (← Q5, Q2)

The geometry node (Q5) classified every point by degree (3 corner / 4 edge / 5 face / 6 interior). This asks what those classes are *worth*.

## What to answer
- First-move advantage by class: does opening on an interior (degree-6) point beat a corner/edge, or the reverse (more liberties = harder to make eyes)?
- Final-territory ownership rate by class in self-play.

## Method
Constrained self-play where Black's first move is fixed to each class (or compare value-net evaluations once neural exists); measure win-rate / ownership by class. Medium cost (self-play via parallel harness).

Status: OPEN.