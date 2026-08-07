---
node_id: 0b9fe131-8eff-543e-a6c7-42c24615c0b1
slug: spring-brook-4774
title: SEARCH-1 — Score-aware utility + dynamic komi at play time [MED]
created_at: '2026-06-09T07:00:08.334010+00:00'
parents:
- shrill-union-9485
- throbbing-unit-0557
- proud-king-2753
summary: Once AUX-2 lands, make MCTS optimize a blend of win-prob and expected score, and adjust komi during self-play so games aren't blowout-dominated. Unlocks honest komi/handicap evaluation and could make S4-style big-board comparisons meaningful. Extends Q9 komi 9a106027; depends on the AUX-2 score head.
flywheel:
  node_id: 0b9fe131-8eff-543e-a6c7-42c24615c0b1
  slug: spring-brook-4774
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 196b2d8506960112b7a33b1723bb8369330585d8e661f526a11e27cd0249e9b3
---
# SEARCH-1 — Score-aware utility + dynamic komi at play time [MED]

## Objective
Change the MCTS leaf utility from pure win-prob to a **blend of win-prob and expected score** (from the AUX-2 head), and apply **dynamic komi** during self-play / evaluation so games stay competitive instead of blowouts. Enables honest komi- and handicap-controlled comparisons.

## Why it matters (which finding it extends)
Our games are **blowout-dominated** — that is *why* win-rate can't see komi (`2a2ca6b9`) and why a pure-win-prob agent plays slack moves once ahead. KataGo's score-aware utility keeps the agent maximizing margin (sharper play, denser training signal); dynamic komi keeps self-play near 50% so the value head trains on *decided-but-close* games. Together they unlock the honest komi/handicap evaluation Q9 `9a106027` could only approximate, and could make big-board strength comparisons meaningful where blowouts currently wash them out.

## Implementation route
Add an expected-score term to the PUCT leaf value (`az.py`), weight swept; implement dynamic komi (shift komi toward the running mean margin per game). Requires the AUX-2 score head live. Validate that self-play margins concentrate near 0 and that score-aware play beats pure-win-prob at matched search.

## Decision criterion (CI-based, n≥128)
At n≥128: score-aware MCTS beats the pure-win-prob agent head-to-head with CI lower bound > 0.5 at matched sims, AND self-play margin distribution narrows toward 0 (komi competitiveness restored). SPRT-gate.

## Preconditions / risks
**Depends on AUX-2** (score head). Search-side change in `az.py`; CPU/GPU as today. Risk: score weight can over-trade safety for points (sweep); dynamic-komi instability (clip the komi shift). Enables fair komi/handicap eval and SCI-1 work.

## Cost · value
MED build. Value: sharper play + competitive self-play data + the first honest komi/handicap evaluation harness.

## Expected artifacts
Score-aware PUCT + dynamic-komi code, a self-play-margin-distribution before/after figure, an A/B (score-aware vs win-prob) at n≥128, komi/handicap eval table.

## Inspiration source
KataGo score-aware utility + dynamic komi. Builds on AUX-2; extends Q9 komi `9a106027`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
