---
node_id: 4c377ef1-b3e8-5019-bc3c-a57424692b83
slug: round-wave-9279
title: Distilling classical MCTS into the net (autogo transfer) quadruples win-rate vs classical (0.085->0.333) and beats the self-play net 0.722 — but not yet parity
created_at: '2026-06-07T20:28:23.280017+00:00'
parents:
- frosty-grass-9317
- lively-meadow-0948
summary: 'autogo teacher-bootstrap, adapted: distill 192 classical self-play games (14.5k examples) into the 32x3 net via supervised learning. Result: distilled net beats the PASS-3 self-play net 0.722 head-to-head, beats random 0.889, and lifts vs-classical from 0.085 to 0.333 [0.217,0.475] at equal budget. Far more compute-efficient than cold-start self-play; not yet classical parity. Warm-start self-play running.'
flywheel:
  node_id: 4c377ef1-b3e8-5019-bc3c-a57424692b83
  slug: round-wave-9279
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 39e28d2ca35829e8b53b97406c7fa30616cf14adc4472495b9847845d452989c
---
# Distilling classical MCTS into the net (autogo transfer) — closes most of the gap

PASS 4 found the from-scratch self-play net loses ~92% to classical MCTS at equal budget (wins 0.085) [a0e8a3f6]. autogo [b4fd8252] bootstraps from a stronger teacher via supervised learning. We have no human 3D-Go games — but **classical MCTS is a teacher that beats our net**, so we distill IT.

## Method
1. **collect_classical.py** (CPU-parallel, 14 cores, no GPU): 192 classical-MCTS self-play games on 4^3 at 128 playouts -> 14,476 examples of (state, classical visit-count policy, game outcome z). Black-favored at komi 0 (104/79/9 B/W/draw).
2. **train_distill.py**: supervised-train the SAME 32x3 A3GoNet (isolating distillation from architecture) on (policy KL + value MSE), 40 epochs, 90/10 holdout. Tracks holdout policy accuracy (autogo's non-self metric).

## Results
| metric | distilled net | PASS-3 self-play net |
|---|---|---|
| **vs classical MCTS (equal 48v48)** | **0.333 [0.217, 0.475]** (16/48) | 0.085 [0.034, 0.199] |
| vs uniform random (N=200) | 0.889 | 0.889 |
| **head-to-head vs the self-play net (N=200)** | **0.722** | — |
| holdout policy accuracy | 0.129 (diffuse 128-playout targets over 65 actions) | n/a |
| holdout value MSE | 0.048 (value head learned well) | n/a |

## Interpretation
**Distillation works and is far more compute-efficient than cold-start self-play on 4^3.** 192 classical games + supervised training produced a net that (a) **beats the 12-generation/960-game self-play net 72%** head-to-head and (b) **quadruples** the win-rate vs classical (0.085 -> 0.333). It does NOT fully reach classical parity (CI upper 0.475 < 0.5): on a tiny board, classical MCTS's terminal random rollouts remain a strong value signal, and a 48-sim neural search guided by a 32x3 net can't quite match a 48-playout classical search. The value head distilled well (MSE 0.048); the low policy-argmax accuracy reflects diffuse visit targets, not failed learning (play strength jumped regardless — confirming again that holdout-argmax != strength).

## Next (running)
Warm-start AZ self-play from the distilled net (annealed Dirichlet, sims=64) — autogo's distill->self-play pipeline — to test whether self-play improvement on top of the strong prior can push past classical. Result in a child node.

Artifacts: experiments_distill_4.json (training curve + holdout metrics), experiments_distill_vs_classical.json, experiments_distill_vs_nets.json, collect_classical.py, train_distill.py.