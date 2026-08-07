---
node_id: 67169cf2-5124-58f2-b3c3-f43baa726d78
slug: square-heart-9657
title: 'PROBE-1 — Input-plane ablation attribution [RESOLVED: net relies MOST on the ≥3-lib group-health plane, NOT atari; liberties act as a partially-redundant set]'
created_at: '2026-06-18T11:52:24.188368+00:00'
parents:
- proud-king-2753
summary: 'RESOLVED. Forward-pass reliance: the libs net depends most on the ≥3-LIBERTY (group-health) plane (KL 0.155, 76% top1-flip ≈ ablating all liberties), NOT the atari/1-lib plane (KL 0.04) — overturns the KataGo atari-prime-suspect prior. Strength (net-vs-net, low power): removing ALL liberties costs most (0.618); single planes recoverable/not CI-separated → liberties are a redundant set. Points refinement to REP-3 finer buckets/group-health over atari.'
flywheel:
  node_id: 67169cf2-5124-58f2-b3c3-f43baa726d78
  slug: square-heart-9657
  revision: 2
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: b1d46007e4518950d1e8727b85a37bf0df9a86b607c671bf876dcaa5398fedd9
---
# PROBE-1 — input-plane ablation attribution (libs net, 5³) [RESOLVED]

Which liberty plane carries the ARCH-3 +0.144 gain? Forward-pass reliance (Part A) + net-vs-net strength cost (Part B), no retraining. libs planes: 1-lib (atari) / 2-lib / ≥3-lib.

## Part A — forward-pass reliance (zero one plane, measure shift; pooled 3 seeds)
- ablate 1-lib (atari): KL=0.0423 valMAE=0.0055 top1flip=0.1747
- ablate 2-lib:         KL=0.0306 valMAE=0.0084 top1flip=0.2763
- **ablate ≥3-lib:      KL=0.155 valMAE=0.0916 top1flip=0.7628**
- ablate ALL liberties: KL=0.1756 valMAE=0.086 top1flip=0.7721

## Part B — strength cost (full net vs ablated net, net-vs-net, gp=12/seed)
- full vs ablate-1lib:   full-wr=0.5758 [0.4071, 0.7444] (33 dec)
- full vs ablate-2lib:   full-wr=0.4412 [0.2743, 0.6081] (34 dec)
- full vs ablate-3plus:  full-wr=0.5484 [0.3732, 0.7236] (31 dec)
- **full vs ablate-ALL:  full-wr=0.6176 [0.4543, 0.781] (34 dec)**

## Findings
1. **Counter-intuitive: the net relies MOST on the ≥3-liberty (group-health) plane, NOT the atari/1-lib plane** that KataGo lore would predict. Ablating ≥3-lib shifts policy (KL 0.155) and value (MAE 0.092) almost as much as ablating ALL liberty planes (0.176 / 0.086), and flips 76% of top-1 moves — vs KL 0.04 / 0.03 and 17–28% flips for the 1-lib / 2-lib planes.
2. **At the strength level the liberty planes are a partially-redundant SET, not separable at this power.** Removing ALL liberties costs the most strength (full-wr 0.618, approaching CI separation at n≈34); single-plane removals are recoverable and not CI-separated (the net compensates when only one plane is zeroed). So the decision criterion ("one plane CI-separated") is not met — the actionable signal is Part A's reliance ranking.

## Implication for refinement
The carrier is the **liberty-magnitude / "healthy group" signal (≥3 libs)**, not binary atari. This argues for **REP-3 (finer liberty buckets / group-health) and my-opp split** over an atari-centric feature, and de-prioritizes pure self-atari emphasis. Note Part A is OOD (the net never trained on a zeroed plane) so reliance is an upper bound; a retrain-without-plane control (cheap) would confirm.

## Artifact
`probe1_ablation.json`. Code: `probe_ablation.py` (ablation hook in the config_planes encoder; reuses screen_nvn match).

*Resolved PASS-20 (breadth pass, cheap-first). Budget $0/local. Engine/tests untouched (additive probe scripts only).*