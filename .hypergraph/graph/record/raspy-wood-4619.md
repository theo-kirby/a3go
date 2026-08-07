---
node_id: 6ac526b8-9f9b-586e-b746-68db41b0390e
slug: raspy-wood-4619
title: REP-2 — Liberty-after-move (pseudo-liberty) planes [WS2 refinement, cheap train]
created_at: '2026-06-18T11:52:26.618948+00:00'
parents:
- proud-king-2753
summary: For each legal empty cell, encode the liberty count the side-to-move's stone WOULD have after playing there (self-atari detection, ladder reading). The current libs planes only describe stones already on the board; this gives the net look-ahead tactics KataGo bakes in. Flagged in the PASS-19 frontier; cheap GPU train + net-vs-net screen.
flywheel:
  node_id: 6ac526b8-9f9b-586e-b746-68db41b0390e
  slug: raspy-wood-4619
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: b9a614f5885a33798ff50d4ddb261c466a1e4432ad29603bf9e6dd9f1f11a9d0
---
# REP-2 — Liberty-after-move (pseudo-liberty) planes

## Objective
Add per-empty-cell planes giving the liberty count the side-to-move's stone would have immediately after playing there (bucketed 1 / 2 / ≥3), i.e. pseudo-liberties / self-atari detection. Extends the static stone-liberty planes with a one-ply tactical look-ahead the net otherwise must learn implicitly.

## Why it matters (which finding it extends)
ARCH-3 `bcf93cd3` showed STONE liberties carry the +0.144 gain; PROBE-1 will say which bucket matters. The natural next refinement (named in the PASS-19 frontier, control `62ab093f`) is MOVE liberties: self-atari avoidance and atari-creation are the core tactics of capture-rich 3D Go, and a pseudo-liberty plane hands them over directly — KataGo includes exactly this.

## Implementation route
In `input_planes`, for each empty cell legal for `color`, simulate the play on a scratch group-union (reuse the capture-aware logic already in `config_planes`) and bucket resulting liberties. Reuse the per-empty-cell loop already there (capture/ko-ban) so marginal cost is low. New CONFIG `libsmv` / `libs+libsmv`. Cheap train + net-vs-net.

## Decision criterion (CI-based, n≥128)
net-vs-net `libs+libsmv` CI-separated above `libs` at n≥128/3-seeds. Cross-check: does it specifically reduce self-atari blunders (behavioral count) vs the plain libs net?

## Preconditions / risks
Train-side; GPU free. Risk: per-empty-cell simulate adds encode cost in the net's own MCTS — keep it in the lazy `config_planes` path and benchmark; only ship if net-vs-net wall-clock stays minutes.

## Cost · value
CHEAP-MED train. High value: the most KataGo-aligned, most likely-to-work liberty refinement; directly tests "tactical look-ahead in the input" on the proven liberty lever.

## Expected artifacts
Pseudo-liberty builder + identity/edge unit test, `libsmv` checkpoints, net-vs-net screen JSON, self-atari behavioral delta.

## Inspiration source
KataGo move-liberty / self-atari features. Extends ARCH-3 `bcf93cd3`, PASS-19 liberty-refinement frontier.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20. Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*