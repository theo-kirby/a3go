---
node_id: 884663c8-410f-55d3-9122-1f493ac9b419
slug: tiny-rain-6373
title: SCALE-1 — Extend the recipe & scaling law to 9^3 and non-cube boards [MED-HIGH]
created_at: '2026-06-08T06:51:15.100804+00:00'
parents:
- delicate-breeze-7763
- mute-cloud-4824
summary: Run the distillation recipe on 9^3 (the most genuinely-3D board yet) and on non-cube shapes (e.g. NxNx2 slabs, 4x4x7 prisms) to test whether the cross-board scaling law (value easier, policy harder, sims grow) extends, and to quantify how the third dimension's extent changes the game. Depends on INFRA-1/2 for tractable big-board search. Directly feeds S4.
origin:
  backend: flywheel
  node_id: 884663c8-410f-55d3-9122-1f493ac9b419
  slug: tiny-rain-6373
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: dec6716d-86c8-560c-af65-06497d3ff111
  slug: cool-shadow-2796
  revision: 0
  pushed_at: '2026-08-08T10:03:07+00:00'
  content_sha256: cca46714df194214ecf7457f83bc4b81cb78c475d582b87b27e5e8f35ae0f629
---
# SCALE-1 — 9^3 and non-cube boards (extend the scaling law) [MED-HIGH]

## Why
The cross-board scaling law [0bc38c41] is fit on 4^3/5^3/7^3 — three points. **9^3** (729 cells) is the next genuinely-3D rung and tests whether the law (value MSE keeps falling, policy acc keeps falling, required sims keep growing) holds or bends. **Non-cube boards** (NxNx2 slabs, 4x4x7 prisms, NxNx1 = genuine 2D control) isolate *the third dimension's effect*: how does extent-in-z change komi, game length, capturing, and the value/policy difficulty curves? The engine already supports `shape=(w,h,d)` [a3go_engine.py].

## Approach
- Collect classical teacher data on each shape via the C++ engine [cff3a5d1] (data-gen already solved).
- Distill (size-appropriate capacity), eval at board-scaled sims using INFRA-1.
- Plot all shapes on the scaling-law axes; add the NxNx1 genuine-2D control to quantify the "cost/benefit of the 3rd dimension" directly.

## Decision criterion
Either the scaling law extends cleanly to 9^3 + non-cube (a stronger, more general law — a real result), OR it bends and we characterize where/why. For S4-adjacent: a decisive or parity result on 9^3 at affordable sims.

## Preconditions / risks
**Depends on INFRA-1** (9^3 high-sim eval is otherwise CPU-bound, same wall as 7^3) and benefits from INFRA-2. Risk = 9^3 needs ">>512" sims (law extrapolation) that only INFRA-1 makes affordable. $0/local. Continues [0bc38c41].