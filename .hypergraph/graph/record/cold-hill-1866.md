---
node_id: 1cb25477-1a78-525e-a8aa-8e0d1b0c27ab
slug: cold-hill-1866
title: LD-2 — 3D nakade / dead-shape taxonomy (which enclosed volumes are killable) [edge science, engine/solver]
created_at: '2026-06-18T12:25:06.741740+00:00'
parents:
- proud-king-2753
summary: 2D Go has a famous finite catalogue of nakade ('dead shapes' — enclosed regions that are one big eye and thus killable). The 3D catalogue is unknown. Enumerate small enclosed volumes and solve whether the surrounding group lives or dies, producing the first 3D nakade table. Pure engine/solver, cheap.
origin:
  backend: flywheel
  node_id: 1cb25477-1a78-525e-a8aa-8e0d1b0c27ab
  slug: cold-hill-1866
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 5c624059-0ecc-5ddc-a653-4c7e419b6a22
  slug: sparkling-cell-4654
  revision: 0
  pushed_at: '2026-08-08T10:02:40+00:00'
  content_sha256: fd9ebab558ed0d568791a0f532631bbbd38866613a4cf874b7a12aef6952bc76
---
# LD-2 — 3D nakade / killable-shape taxonomy

## Objective
Build the 3D analogue of the 2D nakade catalogue: enumerate small enclosed empty volumes (3–8 cells) and determine, via kill-search, which are a single big eye (killable — the defender cannot make two eyes) versus which yield two eyes (alive). Output the first taxonomy of 3D dead shapes.

## Why it matters (which finding it extends)
Nakade ("placement inside to kill") is how most Go life-and-death is actually decided, and the set of vital points is a small finite table in 2D. In 3D the enclosed volumes and their vital points are unknown — this directly characterizes which captured regions are real territory vs killable, sharpening Tromp-Taylor scoring intuition and the capture/seki economics the campaign keeps hitting (`31dae43b`, seki `2a2ca6b9` neighbourhood). Builds on LD-1's eye condition.

## Implementation route
Engine-only. For each enclosed volume shape, place the defender's wall, give the attacker the move, and exhaustively search (bounded minimax / EVAL-2 solver `ebff5f9f`) whether the attacker can reduce it to one eye. Record vital points (the killing placement). Canonicalize shapes under the cube group (cube_symmetry, 48-fold) to dedupe.

## Decision criterion
A taxonomy table: for each enclosed volume up to K cells, alive/dead verdict + vital point(s), with engine-witnessed kill/live lines. Constructive.

## Preconditions / risks
Depends on LD-1 (eye condition) + the cube-symmetry canonicalizer (`cube_symmetry.py`, built PASS-20). Risk: combinatorial blow-up — bound volume size to where exhaustive search terminates; report coverage honestly.

## Cost · value
CHEAP (engine/solver). High value: a reusable 3D dead-shape table; the practical core of 3D life-and-death and of any future tsumego/teaching tool.

## Expected artifacts
`ld_nakade.py`, a nakade taxonomy JSON (shape -> alive/dead + vital points), symmetry-deduped shape catalogue.

## Inspiration source
2D nakade theory (the "rabbity six" et al.). Extends LD-1, uses cube_symmetry; feeds EVAL-2 `ebff5f9f`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-2 (3D tactical/positional knowledge axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*