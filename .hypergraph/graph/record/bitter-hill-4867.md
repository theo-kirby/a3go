---
node_id: 9867fdd6-8970-5ddb-a1cb-702155d96774
slug: bitter-hill-4867
title: 'PROBE-2 — Value-head calibration [RESOLVED: already well-calibrated (ECE~0.008), mildly under-confident; free temp≈0.65 halves ECE]'
created_at: '2026-06-18T11:52:24.838391+00:00'
parents:
- proud-king-2753
summary: RESOLVED. 3D value heads are already well-calibrated (ECE 0.007–0.009), mildly under-confident; temperature≈0.65 halves ECE as a free no-retrain inference fix. Not a scar. Implies MCTS is doing real look-ahead, not denoising a biased value (sharpens SEARCHX-1).
origin:
  backend: flywheel
  node_id: 9867fdd6-8970-5ddb-a1cb-702155d96774
  slug: bitter-hill-4867
  revision: 2
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 02fe2636-14d3-5c97-b524-cf364f56fc90
  slug: quiet-resonance-2535
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: 6110925a52c54cc4bfe776f9efdecef53c19566c8ec423df60d34786314bd018
---
# PROBE-2 — value-head calibration vs Tromp-Taylor outcome (5³) [RESOLVED]

Reliability of the trained value heads on a held-out split, with realized game outcomes Z. Forward-pass only.

## Result (held-out, 3-seed ensemble value)
- base (3-plane): MSE=0.0206 ECE=0.007 T*=0.625 ECE_after_T=0.0025
- libs (lib planes): MSE=0.0195 ECE=0.0093 T*=0.725 ECE_after_T=0.0041

## Findings
1. **Both 3D value heads are already well-calibrated** — ECE ≈ 0.007–0.009 (near-perfect), so the value head is NOT a calibration scar.
2. **Mild UNDER-confidence:** the optimal temperature T*≈0.63–0.73 (<1 ⇒ sharpen), and temperature scaling roughly HALVES ECE (→0.0025–0.0041) — a free, no-retrain inference tweak.
3. The richer `libs` input trades a hair of calibration (slightly higher ECE) for lower value MSE vs `base`.

## Why it matters
Sharpens SEARCHX-1: because the value head is well-calibrated, MCTS is doing genuine look-ahead, not merely denoising a biased value — so "more sims" buys search, not calibration. The cheap temperature fix can be A/B'd in net-vs-net.

## Artifact
`probe2_calibration.json` (reliability bins + ECE + temperature per cfg). Code: `probe_calibration.py`.

*Resolved PASS-20 (breadth pass, cheap-first). Budget $0/local. Engine/tests untouched (additive probe scripts only).*