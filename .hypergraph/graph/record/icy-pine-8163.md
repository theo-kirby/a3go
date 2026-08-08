---
node_id: e3615791-6e33-54cf-989d-445e2c857aad
slug: icy-pine-8163
title: 'SEARCH-5 — Self-play exploration/efficiency: playout-cap randomization + shaped Dirichlet + root softmax temp [MED]'
created_at: '2026-06-09T07:00:11.533838+00:00'
parents:
- lively-meadow-0948
- billowing-dew-3640
- proud-king-2753
summary: Improve self-play *data quality* (not absolute strength) with KataGo's playout-cap randomization (cheap moves + a fraction expensive), legal-move-scaled Dirichlet, and root softmax temperature — replacing az.py's flat Dirichlet(0.5). Value is better aux-head training data, since PASS-15 showed self-play does not lift absolute 5³ strength. Extends INFRA-3 8a724b1c and autogo b4fd8252.
origin:
  backend: flywheel
  node_id: e3615791-6e33-54cf-989d-445e2c857aad
  slug: icy-pine-8163
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: f1284625-3512-586a-85a4-bdc3dbd72a43
  slug: broken-hill-3418
  revision: 0
  pushed_at: '2026-08-08T10:03:07+00:00'
  content_sha256: 54387066d8e5898d70de69397587738b169cfb3719c6c57446b15f3f8bdc69a5
---
# SEARCH-5 — Self-play exploration/efficiency: playout-cap randomization + shaped Dirichlet + root softmax temp [MED]

## Objective
Upgrade self-play generation with **playout-cap randomization** (most moves cheap, a small fraction full-strength + full noise — KataGo gets more data per FLOP without degrading targets), **shaped Dirichlet** (concentration scaled to legal-move count, not a flat 0.5), and a **root softmax temperature** schedule.

## Why it matters (which finding it extends)
PASS-15 `b3ea0b95` proved plain self-play does **not** lift absolute 5³ strength — so the value here is **data quality and quantity for the aux-head retrains (AUX-1/2/3/4)**, not more self-improvement iterations. `az.py` uses a flat `Dirichlet(0.5)` regardless of board size; KataGo's shaped noise + playout-cap give cheaper, better-distributed exploration, and autogo `b4fd8252` independently warns that *fixed* noise compounds badly (anneal it). Better self-play data is the substrate every aux-head experiment trains on.

## Implementation route
In `az.py` / the self-play driver: implement playout-cap randomization (per-move cheap/expensive coin-flip; only record targets on expensive moves, KataGo-style); replace flat Dirichlet with α scaled to legal-move count; add a root softmax temperature schedule. Measure games/sec and downstream net quality from data generated each way.

## Decision criterion (CI-based, n≥128)
At n≥128 on a *downstream* metric: a net trained on the new self-play data beats one trained on equal-compute old-style data (vs classical, CI separation), OR equal net quality at materially higher games/sec (throughput CI). Not gated on self-play win-rate (PASS-15 lesson).

## Preconditions / risks
Self-play-side; CPU/GPU as today. Risk: chasing self-play win-rate again (explicitly avoided — gate on downstream net quality). Lower standalone priority; high as the data feeder for AUX-*.

## Cost · value
MED build. Value: better/cheaper training data for the whole aux-head cluster; directly applies the PASS-15 + autogo lessons.

## Expected artifacts
Upgraded self-play driver, a games/sec + downstream-net-quality comparison JSON, a noise/temperature schedule doc.

## Inspiration source
KataGo playout-cap randomization + shaped Dirichlet + root softmax temp; autogo anneal-don't-fix `b4fd8252`. Extends INFRA-3 `8a724b1c`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
