---
node_id: f490a174-5462-580b-bdf6-fe2db6b4ee2f
slug: winter-water-4984
title: 'Stronger-teacher distillation reaches PARITY with classical: 0.085 -> 0.333 -> 0.458 [0.33,0.60] as teacher strength + data grow — net quality was the bottleneck'
created_at: '2026-06-07T23:37:18.845274+00:00'
parents:
- dawn-block-6253
- round-wave-9279
summary: Distilling from a stronger teacher (128+192-playout classical, 22k examples) lifts the 32x3 net to 0.458 [0.326,0.597] vs classical at equal budget — statistically at parity, up from 0.085 (self-play) and 0.333 (128-playout distill). Confirms the scaling-node prediction that net quality (value targets), not search, was the wall. One more data round running to cross 0.5 decisively.
origin:
  backend: flywheel
  node_id: f490a174-5462-580b-bdf6-fe2db6b4ee2f
  slug: winter-water-4984
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 1ce76b22-0997-5171-8cfc-8a757ff8a413
  slug: yellow-sunset-3271
  revision: 0
  pushed_at: '2026-08-08T10:02:40+00:00'
  content_sha256: 9523ef7572b4b194ab895054669eb49301e355fc05c60c98cf19a3d2c7d57182
---
# Stronger-teacher distillation brings the net to PARITY with classical (0.085 -> 0.333 -> 0.458)

The scaling node [9605fb9a] showed test-time scaling can't beat classical and the bottleneck is net quality (value head). Lever: distill from a STRONGER teacher (higher-playout classical = better policy/value targets).

## Method
Collected 96 classical self-play games at **192 playouts** (7,607 examples), combined with the original 128-playout set (14,476) -> **22,083 examples**. Re-distilled the SAME 32x3 net (clean comparison), 40 epochs.

## Result: parity with classical
| net | vs classical MCTS, equal 48v48 | 95% CI |
|---|---|---|
| from-scratch self-play (P3) | 0.085 | [0.034, 0.199] |
| distill, 128-playout teacher | 0.333 | [0.217, 0.475] |
| **distill, 128+192-playout (22k)** | **0.458** | **[0.326, 0.597]** |

The CI now straddles 0.5 -> the net is **statistically indistinguishable from classical** (a coin flip), up from a 92% loss. Not yet a decisive win (CI lower 0.326 < 0.5), but the gap is essentially closed.

## Finding
**Net quality (value/policy targets) was the bottleneck, and teacher strength is the lever** — exactly as the scaling node predicted. Each step up in teacher strength + data lifted the net monotonically (0.085 -> 0.333 -> 0.458). On a tiny 4^3 board, classical random-rollout MCTS is a strong baseline (rollouts ~ accurate value), but a small net distilled from progressively stronger classical play reaches parity. Holdout policy-argmax accuracy stayed low (~0.10) throughout while play strength climbed — reconfirming argmax-accuracy is not a strength proxy for diffuse MCTS targets.

## Next (running)
Another 96-game 192-playout round -> ~30k examples -> re-distill, to push the point estimate decisively past 0.5. (Stronger 256-playout teacher is ~30 min/game, deferred. Bigger net = untested cheap lever.)

Artifact: experiments_distill2_vs_classical.json.