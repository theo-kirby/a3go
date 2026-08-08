---
node_id: 7ae71a3a-10de-51a6-afaf-17065ada97d8
slug: lucky-wave-5153
title: LD-3 — Generated 3D tsumego + does the net read life-and-death? [forward-pass probe, cheap]
created_at: '2026-06-18T12:25:07.574745+00:00'
parents:
- proud-king-2753
summary: 'Use LD-1/LD-2 to auto-generate solved 3D life-and-death problems, then test whether the EXISTING trained nets read them: does the policy find the vital point, does the value head know alive-vs-dead? A forward-pass interpretability probe connecting tactical ground truth to net behaviour — cheap, and a hard-position source for DATA mining.'
origin:
  backend: flywheel
  node_id: 7ae71a3a-10de-51a6-afaf-17065ada97d8
  slug: lucky-wave-5153
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 9463c221-954a-5d9f-a8d4-6827ffa73e82
  slug: young-cloud-6399
  revision: 0
  pushed_at: '2026-08-08T10:02:40+00:00'
  content_sha256: ebc21a3c4739905f68c80c92ca00c24153631d98477e1e00b4506f4608b8135f
---
# LD-3 — Generated 3D tsumego + net life-and-death reading accuracy

## Objective
Turn the LD-1/LD-2 solved shapes into a benchmark of 3D life-and-death problems with known answers, and measure whether the trained nets read them: (a) does the policy place the vital point (kill/live move)? (b) does the value head correctly rate the position alive vs dead? Forward-pass only on existing checkpoints.

## Why it matters (which finding it extends)
PROBE-1/PROBE-2 (PASS-20) probe the net on self-play positions; this probes it on TACTICAL ground truth, where right/wrong is unambiguous. If the net misreads basic life-and-death, that localizes the strength ceiling far more sharply than aggregate win-rate, and tells us whether to add L&D features or L&D training data. The solved problems are also a ready-made hard-position set for the data-quality axis.

## Implementation route
Generate problem positions from LD-1/LD-2 (defender wall + enclosed volume, attacker to move). For each, forward the net (config_planes encoder), check policy top-k for the vital point and value-head sign vs the solved verdict. No training; reuse the PROBE-1 harness.

## Decision criterion (CI-based, n≥128)
n≥128 generated problems: report vital-point top-1/top-3 accuracy and value-head alive/dead AUC, per net (base vs libs). Decisive contrast = libs net CI-separated above base on L&D reading (does the liberty feature specifically help tactics?).

## Preconditions / risks
Depends on LD-1/LD-2 for solved problems. Forward-pass only, cheap. Risk: generated problems may be off-distribution for nets trained on full-board self-play — interpret as a stress test; complement with near-terminal self-play L&D.

## Cost · value
CHEAP (forward-pass). High value: ties the net's strength to unambiguous tactics; produces a reusable L&D benchmark + hard-position mine for DATA work.

## Expected artifacts
`ld_tsumego.py`, a solved-problem benchmark JSON, per-net L&D accuracy table (vital-point top-k + value AUC).

## Inspiration source
KataGo's tsumego/benchmark suites; 2D L&D problem sets. Extends PROBE-1 `67169cf2`, LD-1/LD-2.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-2 (3D tactical/positional knowledge axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*