---
node_id: 777d5c9e-70ce-588f-98e2-4f2a80dfebb6
slug: proud-tree-3638
title: SCIENCE-2 — 3D life & death and tactical motifs at scale (net-discovered) [MED]
created_at: '2026-06-08T06:51:17.705020+00:00'
parents:
- mute-cloud-4824
- proud-star-4959
summary: 'Go beyond the solver-proven basics (two-eye life=straight-four, seki exists & survives 6-connectivity) to catalog 3D-specific tactics the STRONG net discovers in real games: snapback frequency, seki frequency, minimal living shapes by volume, and whether 6-connectivity creates motifs with no 2D analog. Mines the agent''s games as a microscope on 3D Go''s structure.'
flywheel:
  node_id: 777d5c9e-70ce-588f-98e2-4f2a80dfebb6
  slug: proud-tree-3638
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: bda5047fef85e5fa36d1827af95da3e57d90cb7c3c380d89a58c5e31b9ad3e51
---
# SCIENCE-2 — 3D life & death and tactics at scale [MED]

## Why
Phase-2 nailed the *exact* basics with solvers: two-eye life = straight-four [897fb2e0], seki exists and survives 6-connectivity [5f10c19e], ladders break in 3D [01d82e67], ko is ubiquitous (~98% of single captures hit superko [31dae43b]). What's missing is the *statistical/emergent* tactical picture from a **strong agent's actual play**: how often do seki/snapback/ko-fights occur, what minimal living shapes appear, and are there motifs with **no 2D analog**? This is the thesis's "mechanical oddities" question answered at the level of real play, not just toy solvers.

## Approach
- **Mine strong self-play games** (once the strength track produces them): detect & count seki, snapback, ko/superko bans, eye-shapes, and life/death outcomes per game.
- **Targeted solvers** for the open Phase-2 tails: snapback (the ~2% of single-captures that aren't ko [Q7]), seki *frequency* and minimal seki *volume*, minimal unconditional life by volume across N.
- Compare motif frequencies to a 2D control (NxNx1 slab via SCALE-1) to isolate genuinely-3D tactics.

## Decision criterion
A committed catalog: frequencies (with CIs) of seki/snapback/ko in strong play, minimal-shape tables, and at least one identified motif with no clean 2D analog (or a principled statement that 3D tactics are 2D tactics + connectivity bookkeeping).

## Preconditions / risks
The statistical half needs strong-agent games (strength track); the solver half is cheap and can run now (extends `seki3d.py`). Risk = rare events need many games for tight frequencies — size the sample, and report what was undersampled. $0/local. Continues [5f10c19e, 897fb2e0, 31dae43b, 01d82e67].