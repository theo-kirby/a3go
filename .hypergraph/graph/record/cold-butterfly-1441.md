---
node_id: 312d9495-eee2-552f-8fe8-3730840814fb
slug: cold-butterfly-1441
title: SEARCH-4 — Optimistic policy head [MED, ~40–90 Elo]
created_at: '2026-06-09T07:00:10.286629+00:00'
parents:
- gentle-glitter-1363
- snowy-brook-3358
- proud-king-2753
summary: Add KataGo's optimistic policy head — a second policy biased toward moves that historically over-performed their prior — to widen useful search at low sims (40–90 Elo claimed). Needs the soft-policy target machinery (AUX-3). Extends ALGO-2 792c4ec2.
origin:
  backend: flywheel
  node_id: 312d9495-eee2-552f-8fe8-3730840814fb
  slug: cold-butterfly-1441
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 831ce2e0-402e-5c38-a141-55f9f489fd92
  slug: polished-cloud-3109
  revision: 0
  pushed_at: '2026-08-08T10:03:17+00:00'
  content_sha256: 7af2952888f904bb197da9f2270b2b805821a7f77a530b67c42db49f35fd3298
---
# SEARCH-4 — Optimistic policy head [MED, ~40–90 Elo]

## Objective
Add a second **optimistic policy head** trained toward moves whose search value *exceeded* their policy prior (the moves the net under-rates but search likes), and blend it into root/selection priors. KataGo reports **+40–90 Elo**.

## Why it matters (which finding it extends)
Our policy is the weak head and *narrows* search prematurely on big boards (`0bc38c41`). An optimistic head explicitly counteracts that by up-weighting under-explored over-performers — exactly the moves a too-confident weak policy prunes. It compounds with AUX-3's softer target (which exposes the full preference ordering the optimistic head reweights). Extends ALGO-2 `792c4ec2` (head architecture) and the policy-weakness scaling law.

## Implementation route
Add an optimistic policy head; its target is built from the gap between MCTS visit share and net prior (over-performers). At play, mix optimistic and standard priors (KataGo blends at root). Requires AUX-3's visit-distribution targets in the trainer. A/B on the ladder.

## Decision criterion (CI-based, n≥128)
At n≥128: the optimistic-head agent gains ≥ +30 Elo over the standard-policy agent at matched sims with CI separation (KataGo claims 40–90). SPRT-gate.

## Preconditions / risks
**Depends on AUX-3** (soft-policy / visit-distribution targets). Train + search change. GPU free. Risk: optimism can waste visits on genuinely bad moves at high sims (blend weight sweep; decay with visit count). Pairs with SEARCH-3.

## Cost · value
MED build. Value: another large KataGo search-time item; directly widens the too-narrow big-board search.

## Expected artifacts
Optimistic policy head + blend logic, an Elo-delta JSON on the ladder (n≥128), blend-weight sweep.

## Inspiration source
KataGo optimistic policy (40–90 Elo). Needs AUX-3; extends ALGO-2 `792c4ec2`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
