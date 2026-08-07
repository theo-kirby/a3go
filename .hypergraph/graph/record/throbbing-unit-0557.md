---
node_id: d971bf0e-673d-5b30-a686-5acca18f2316
slug: throbbing-unit-0557
title: AUX-2 — Score-margin + score-distribution head [MED, high-value]
created_at: '2026-06-09T07:00:06.071360+00:00'
parents:
- shrill-union-9485
- gentle-sun-9997
- gentle-glitter-1363
- proud-king-2753
summary: Add a KataGo-style score head (predict final area margin + its distribution), giving a dense, komi-sensitive target where win-rate alone is flat. Directly attacks komi-unidentifiable-on-3³ 2a2ca6b9 and feeds Q9 fair-komi 9a106027 and score-aware play (SEARCH-1) + dynamic komi. Extends ALGO-2 792c4ec2.
flywheel:
  node_id: d971bf0e-673d-5b30-a686-5acca18f2316
  slug: throbbing-unit-0557
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: a398074a46b906d828004723d8c40e6fc6bfaada13565f3f1c00fdba5dca9559
---
# AUX-2 — Score-margin + score-distribution head [MED, high-value]

## Objective
Add a score head to `A3GoNet` predicting the final **area margin** (and a small histogram over plausible margins, KataGo-style), trained jointly as an auxiliary target. A dense, signed, komi-sensitive signal where binary win/loss is blowout-saturated.

## Why it matters (which finding it extends)
Our sharpest komi scar: **on 3³ win-rate is flat across komi −1.5…+7.5** (`2a2ca6b9`) because games are blowout-dominated — the binary outcome carries almost no komi information. A **margin** target is dense and monotone in komi, so it can pin fair komi where win-rate can't (Q9 `9a106027` got komi only via a bespoke margin estimator; a score head makes it native). It is also the prerequisite for **score-aware play + dynamic komi (SEARCH-1)** and honest handicap eval. Extends ALGO-2 `792c4ec2` (better value targets).

## Implementation route
Final margin is computable from stored end positions (Tromp-Taylor in `a3go_engine.py`). Add a scalar (or small-histogram) score head; loss += λ·score-Huber (+ optional distribution CE). Normalize margin by board volume so the target scales across sizes. Retrain distilled nets; read off implied fair komi (margin=0 crossing) and compare to `9a106027`.

## Decision criterion (CI-based, n≥128)
At n≥128: (a) the score head recovers fair komi on 4³ within ±0.5 area pts of the `9a106027` value (SE-overlapping), AND (b) on 3³ the margin target is non-degenerate (monotone in komi) where win-rate was flat — i.e. it *identifies* komi the binary head can't. Strength side-check: no regression vs baseline (CI).

## Preconditions / risks
Train-side only; GPU free. Risk: margin variance is high on big boards (Huber/clip + volume-normalize). Pairs with AUX-1 (shared spatial trunk). Enables SEARCH-1 and SCI-1 komi/handicap work.

## Cost · value
MED build. High value: turns komi from a flat, unidentifiable signal into a dense one — the lever for every komi/handicap/score question the campaign deferred.

## Expected artifacts
Score head + score-distribution loss, retrained checkpoints, a komi-identifiability JSON (margin-vs-komi curve on 3³/4³ at n≥128), fair-komi readout vs `9a106027`.

## Inspiration source
KataGo final-score + score-distribution heads. Maps to komi-flat `2a2ca6b9`, Q9 komi `9a106027`, ALGO-2 `792c4ec2`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
