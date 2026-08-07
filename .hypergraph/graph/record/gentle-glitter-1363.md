---
node_id: 792c4ec2-6cc6-51eb-a115-f44fe5dc0ff9
slug: gentle-glitter-1363
title: 'ALGO-2 — Architecture & value-target scaling: push the capacity lever [MED]'
created_at: '2026-06-08T06:51:19.006287+00:00'
parents:
- dawn-block-6253
- soft-waterfall-3492
- mute-cloud-4824
summary: 'Net capacity (32x3 -> 64x6) was THE lever that crossed the line vs classical by fixing the value head deeper search amplifies. Push further: deeper/wider resnets, 3D-lattice attention, better value targets (MCTS-value bootstrapping / TD(lambda) instead of pure game outcome), and auxiliary heads (ownership/score). Systematically find the capacity & target recipe that maximizes value-head calibration per board size.'
flywheel:
  node_id: 792c4ec2-6cc6-51eb-a115-f44fe5dc0ff9
  slug: gentle-glitter-1363
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: c46246f769ee19a70ed2bdcc44ef9efd356ac4faff9078c8da3d5d011862959b
---
# ALGO-2 — Architecture & value-target scaling (push the capacity lever) [MED]

## Why
The single move that beat classical was **net capacity**: 32x3 -> 64x6 jumped 0.484 -> 0.612 by fixing the value head that deeper PUCT was *amplifying* [b71da32b, 9605fb9a]. Capacity is a proven lever and the scaling law says value-head quality is the crux on big boards [0bc38c41]. This node systematically pushes it: how far does more capacity + better value targets raise the ceiling, per board size?

## Approach
- **Capacity sweep** (already A/B-able via `A3GO_CH`/`A3GO_BLK`): deeper/wider resnet towers; find the strength-vs-params curve per board size and where it saturates.
- **3D-lattice attention / global context** blocks (Go is long-range; pure local convs may bottleneck big-board value).
- **Better value targets:** MCTS-value bootstrapping / TD(lambda) / n-step returns instead of pure final game outcome — lower-variance, better-calibrated value (the thing deeper search amplifies).
- **Auxiliary heads:** ownership / final-score prediction (KataGo-style) as a value-head regularizer — often a large strength/calibration win.

## Decision criterion
A committed strength-vs-capacity curve per board size and an identified value-target/arch recipe that beats the current 64x6 + pure-outcome baseline at matched search (CI separation), especially on 5^3/7^3 where value calibration is the crux.

## Preconditions / risks
Train-side independent (GPU is free for the tiny nets); strength eval benefits from INFRA-1 + PROOF-1's ladder. Risk = bigger nets slow per-sim eval (tension with the sim-bound bottleneck) — measure strength *per wall-clock*, not just per sim. Keep VRAM small (don't disturb the external vLLM). $0/local. Continues [b71da32b, 9605fb9a, 0bc38c41].