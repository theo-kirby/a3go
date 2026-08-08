---
node_id: 4842d305-9e69-52f7-bf02-c9926031a385
slug: broad-hall-8962
title: AUX-4 — Short-term value / score targets (bias-variance) [MED]
created_at: '2026-06-09T07:00:07.689724+00:00'
parents:
- gentle-glitter-1363
- billowing-dew-3640
- proud-king-2753
summary: Add KataGo-style short-term value/score targets (predict value/score a few plies ahead, not only the final outcome) as a bias-variance lever for value calibration — and the variance estimate that uncertainty-weighted search (SEARCH-3) needs. Extends ALGO-2 792c4ec2 and INFRA-3 self-play 8a724b1c.
origin:
  backend: flywheel
  node_id: 4842d305-9e69-52f7-bf02-c9926031a385
  slug: broad-hall-8962
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 644608a3-ff7f-5af0-b67f-ce46243f163f
  slug: weathered-poetry-6330
  revision: 0
  pushed_at: '2026-08-08T10:03:07+00:00'
  content_sha256: c73900ca1bc08210a07b6613db9c894c04b18b78c5ca61840bc140ea6a54e0f1
---
# AUX-4 — Short-term value / score targets (bias-variance) [MED]

## Objective
Add auxiliary heads predicting **near-term** value and score (the outcome/margin a fixed few plies ahead, e.g. via TD/n-step bootstrap), alongside the long-term final-outcome head. Lower-variance, better-calibrated value — and an explicit short-horizon signal that feeds uncertainty-aware search.

## Why it matters (which finding it extends)
Deeper PUCT *amplifies* a miscalibrated value head — we saw it directly (search hurt the weak net, `9605fb9a`) and capacity fixed it (`b71da32b`). Short-term targets are KataGo's bias-variance knob: the final-outcome label is unbiased but high-variance; a few-ply-ahead target is lower-variance and trains faster. It is also the **prerequisite for variance-scaled cPUCT + uncertainty-weighted playouts (SEARCH-3)**, which needs a per-node value-variance estimate. Extends ALGO-2 `792c4ec2` (better value targets) and INFRA-3 `8a724b1c` (self-play data).

## Implementation route
Add short-horizon value/score heads; compute targets by n-step bootstrap (e.g. value at t+k from the search/value at t+k, or TD(λ)) over stored trajectories. Train jointly (λ-weighted); track value MSE / calibration (reliability curves) vs the pure-outcome baseline.

## Decision criterion (CI-based, n≥128)
At n≥128: value-head calibration improves (lower MSE / better reliability) with CI separation, AND no strength regression vs baseline at matched search — OR the head's variance estimate measurably improves SEARCH-3 (decided there). SPRT-gate.

## Preconditions / risks
Train-side; needs trajectory (not just terminal) storage — self-play already keeps per-move records. GPU free. Risk: bootstrap targets can chase a moving net (use the frozen champion's value, as PASS-14 taught about anchors). Enables SEARCH-3.

## Cost · value
MED build. Value: calibration + the variance signal SEARCH-3 (~+75 Elo) depends on; pairs with AUX-1/2 in the shared aux loss.

## Expected artifacts
Short-term heads + n-step target code, value-calibration/reliability JSON + figure, per-node variance estimate exposed for SEARCH-3.

## Inspiration source
KataGo short-term value/score targets. Maps to ALGO-2 `792c4ec2`, INFRA-3 `8a724b1c`; feeds SEARCH-3.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
