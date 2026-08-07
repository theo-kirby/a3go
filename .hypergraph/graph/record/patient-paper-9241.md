---
node_id: 2341cdd9-1006-5043-bf76-5a6c19883925
slug: patient-paper-9241
title: 'LD-1 — Minimal living shape: how many points to make two eyes in 3D? [edge science, engine/solver, cheap]'
created_at: '2026-06-18T12:25:05.724416+00:00'
parents:
- proud-king-2753
summary: 'The most basic unknown of 3D Go: what is the smallest living group? In 2D, two eyes = life and the minimal living shapes are catalogued; in 3D (6-connectivity) the eye/false-eye/life conditions are unstudied. Enumerate small enclosed shapes and solve life/death with the engine — a foundational science result the whole campaign rests on but never measured.'
flywheel:
  node_id: 2341cdd9-1006-5043-bf76-5a6c19883925
  slug: patient-paper-9241
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 7ad6fd2c6a29b6df5852eca7f9e58f38d8b9aa892fc5b27e13489616fadebc17
---
# LD-1 — Minimal living shape / two-eye condition in 3D

## Objective
Determine the smallest group(s) that live unconditionally in 3D Go, and the 3D analogue of the "two eyes = life" rule. Enumerate small enclosed empty regions ("eyes"), classify true vs false eyes under 6-connectivity, and compute the minimal stone count for an unconditionally alive group on 5³/7³.

## Why it matters (which finding it extends)
Life-and-death is the bedrock of Go strength, and the entire a3go campaign (capture economics, seki, scoring) implicitly depends on 3D life — yet what "alive" even costs in 3D is unmeasured. In 2D a single point fully surrounded is an eye and two eyes are unconditional life; in 3D a cell has 6 neighbours and "eyes" are volumes, so the false-eye/diagonal conditions are different and unknown. This is a genuine science result and a precondition for LD-2/LD-3, SCI-1, and any L&D feature.

## Implementation route
Engine-only. Generate candidate shapes (small connected stone shells around 1–2 empty interior cells), use the existing capture/suicide/superko engine + an exhaustive search (the EVAL-2 superko-aware solver `ebff5f9f` when available, else minimax to a small depth) to decide whether the opponent can kill. Classify eyes by interior connectivity and shared-neighbour rules. No GPU, no net.

## Decision criterion
Deliver (a) the minimal living stone count on 5³/7³ with a witnessed living shape, and (b) a stated 3D two-eye / false-eye condition validated against engine kill-search on an enumerated shape set. Binary/constructive, not CI-based.

## Preconditions / risks
Engine validated (60/60). Best paired with EVAL-2 `ebff5f9f` (exact superko-aware solver) for deep kills; a bounded minimax suffices for tiny shapes. Risk: search depth for "unconditional" life — restrict to small enclosed shapes where exhaustive search terminates.

## Cost · value
CHEAP (engine/solver, no GPU). Very high value: a foundational, citable 3D-Go result the campaign has never had; unlocks the entire L&D axis.

## Expected artifacts
`ld_eyespace.py`, a catalogue of minimal living/dead shapes (engine traces), a stated 3D two-eye condition note.

## Inspiration source
2D Go life-and-death theory (eyes, false eyes, Benson's unconditional life). Foundational for SCI-1 `5b0393b7`, EVAL-2 `ebff5f9f`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-2 (3D tactical/positional knowledge axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*