---
node_id: 1e58a424-54f6-5dfa-bf50-75d842f7dcda
slug: bitter-unit-9524
title: SCALE-2 — Size-agnostic single net (fully-convolutional) across board sizes [MED]
created_at: '2026-06-08T06:51:15.909978+00:00'
parents:
- lively-meadow-0948
- mute-cloud-4824
summary: Train ONE fully-convolutional net (no size-locked dense layers) on a mixture of board sizes so it plays any N^3, and test cross-size transfer/zero-shot generalization. autogo uses size-agnostic nets; it amortizes training and probes whether 3D-Go skill is scale-invariant. Pairs naturally with SCALE-3 (curriculum).
origin:
  backend: flywheel
  node_id: 1e58a424-54f6-5dfa-bf50-75d842f7dcda
  slug: bitter-unit-9524
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: ef8b9f00-9399-518e-becc-49f585e928db
  slug: old-leaf-4385
  revision: 0
  pushed_at: '2026-08-08T10:01:49+00:00'
  content_sha256: 9e3716a875e52da8173e04f336153424ed583266269fa7f837756e028c24284c
---
# SCALE-2 — Size-agnostic single net (fully-conv) across sizes [MED]

## Why
Today each board size trains a fresh net with a size-locked policy/value head. A **fully-convolutional, size-agnostic** net (global-pool value head, conv policy head emitting per-cell logits + a pass) plays *any* N^3 and lets us ask: **is 3D-Go skill scale-invariant?** Does a net trained on {4,5}^3 zero-shot to 7^3? autogo [b4fd8252] uses size-agnostic nets; this amortizes training and is a prerequisite for clean curriculum transfer (SCALE-3).

## Approach
- Re-architect `net.py`: replace dense heads with conv policy head (1x1x1 -> per-cell logit, plus a learned pass logit) and a global-average-pooled value head, so weights are shape-independent.
- Train on a **mixture** of board sizes (distilled targets from each), padding/masking as needed.
- Eval: per-size strength vs classical, and **zero-shot** to a held-out size (train {4,5}, test 7).

## Decision criterion
The single mixed net matches within noise the per-size dedicated nets on trained sizes, AND shows measurable (>random) zero-shot strength on a held-out size — evidence that 3D-Go skill partly transfers across scale.

## Preconditions / risks
Mostly independent (CPU/GPU train); high-sim eval on big sizes wants INFRA-1. Risk = mixed training underperforms specialists (negative transfer); if so, report the per-size capacity trade-off. Must keep value/policy target encoding consistent across sizes. $0/local. autogo precedent [b4fd8252].