---
node_id: 649b9f00-afee-56f2-800b-118f933c951a
slug: loyal-sun-5797
title: Search
created_at: '2026-08-07T20:33:57+00:00'
parents:
- royal-comet-4977
summary: 'Search carries the strength: scaling amplifies with board size; M5 batched MCTS 22x; Gumbel negative on small boards; policy head is the headroom.'
flywheel:
  node_id: 70e627eb-b742-572c-9b8e-cb5adddbf3a8
  slug: patient-rain-1986
  revision: 0
  pushed_at: '2026-08-07T20:39:47+00:00'
  content_sha256: 1f7aee2b66686b5a467f40d6eefb6132779e0555b02a309d758ddef9f14416ed
---
Status: working

## Current

- Both classical UCT and the net scale monotonically with sims, but classical's slope is steeper on 4³ (+211 Elo over 16→128 sims vs the net's +45 over 48→128); cls@128 sits ~65 Elo above net@256 — the net's win is budget-bounded [rec: empty-lab-3357].
- Test-time search scaling amplifies with board size: to dominate its own low-sim self, the net needs ~16× sims on 4³, ~4× on 5³, only ~4–8× on 7³ (60/60 at @512) — deeper PUCT amplifies a calibrated value head, and value calibration improves with board size [rec: rapid-hat-7732].
- Net-vs-search decomposition on 5³: the raw net is weak (policy-only 0.61 vs random, 0.15 vs full search); MCTS carries the strength; the policy head is the identified headroom [rec: rapid-sun-7882].
- M5 batched game-parallel MCTS is the throughput backbone: 0.05→1.11 games/s on 4³ (22.2×); batch=256 is 210× cheaper per position than batch=1 [rec: dark-poetry-2083].
- Value heads are well-calibrated (ECE ≤0.01); a free temperature ≈0.65 halves ECE with no retrain but was never strength-A/B'd [rec: bitter-hill-4867].

## Negative knowledge

- [scope: Gumbel AlphaZero on small boards (≤4³: 65 actions, strong distilled policy) | confidence: high | evidence: divine-thunder-7666] No strength-per-sim win over PUCT — behind at low sims, even at 32/64; the premise (large action space, weak policy) is not exercised there. The fair test (7³, 344 actions, low sims) was never run.
- [scope: test-time search scaling on a miscalibrated value head | confidence: high | evidence: dawn-block-6253] Deeper search amplifies the value head, good or bad — the weak 32×3 net collapsed to 0.042 at net@256 vs cls@128; scaling presumes a calibrated net.

## Provenance

- lively-orchard-3365 — adoption distillation
- empty-lab-3357 — anchored ladder: budget-bounded win, steeper classical slope
- rapid-hat-7732 — PROOF-2 scaling amplifies with board size
- rapid-sun-7882 — SEARCHX-1 net-vs-search decomposition
- dark-poetry-2083 — M5 batched game-parallel MCTS 22x
- bitter-hill-4867 — PROBE-2 calibration + free temperature
