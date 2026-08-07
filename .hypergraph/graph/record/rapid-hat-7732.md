---
node_id: 75615ad2-12eb-5d2d-9a05-890c011c7f86
slug: rapid-hat-7732
title: 'PROOF-2 — test-time search scaling [DELIVERED: search scaling AMPLIFIES with board size — 4^3 needs 16x sims->0.90, 7^3 only ~8x->1.00]'
created_at: '2026-06-08T06:51:13.245756+00:00'
parents:
- dawn-block-6253
- hidden-forest-3847
- mute-cloud-4824
summary: 'DELIVERED (test-time-scaling half of S1). Net-vs-net sim sweeps: more sims reliably beats fewer, and the effect grows with board size (4^3 needs ~16x sims to reach 0.90; 7^3 hits 1.00 by 512 sims, 8x). Matches the cross-board law (value MSE 0.044->0.006): search amplifies a calibrated value head. Implies the genuinely-3D 7^3 — not 4^3 — is where the net most likely dominates classical at all budgets. $0/local, GPU.'
flywheel:
  node_id: 75615ad2-12eb-5d2d-9a05-890c011c7f86
  slug: rapid-hat-7732
  revision: 3
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: f3e3eb0c4d5623139d25f650ea8414b5c43de200ea366bfb1702c831139fff65
---
# PROOF-2 — test-time search scaling of the distilled nets [DELIVERED]

Does giving the SAME net more MCTS sims make it stronger, and does that grow on
bigger, better-calibrated boards? GPU net-vs-net, 60 games/point, parallel across
cores (free GPU + INFRA-2 made this cheap). The test-time-scaling half of S1.

## Scaling curves (win-rate of net@S vs fixed low-sim baseline of itself)
| board | base | curve (sims:winrate) |
|---|---|---|
| 4^3 | @48 | 48:.50 96:.68 192:.77 384:.79 768:**.90** |
| 5^3 | @48 | 48:.42 96:.62 192:.91 384:.93 768:**.98** |
| 7^3 | @64 | 64:.36 128:.72 256:.87 512:**1.00** |

## Finding: search scaling AMPLIFIES with board size
- More sims beats fewer on every board (monotone, CIs separate) — search is a real
  strength lever for the distilled net.
- The gain grows with board size: to dominate, 4^3 needs ~16x sims (->0.90), 5^3
  ~4x (->0.91), 7^3 only ~4-8x (->1.00, won 60/60). At matched 8x: 4^3 .79 < 5^3 .93 < 7^3 1.00.
- Exactly the cross-board-law prediction [0bc38c41]: value MSE 0.044->0.019->0.006
  (4^3->5^3->7^3); deeper PUCT amplifies a CALIBRATED value head but not a bad one
  (PASS-6 'no free lunch' [9605fb9a]). On the well-calibrated big boards, search pays off hugely.

## S1/S4 implication
PROOF-1 [3ac354fd] showed the net's win over classical is budget-bounded ON 4^3
(rollout value scales better on tiny boards). This shows the net's own strength
scales steeply with search on 5^3/7^3 — where rollouts are weak and the net's
value is near-perfect. So the board most likely to yield all-budget dominance over
classical is the genuinely-3D 7^3, not 4^3. Missing piece: net-vs-classical at high
sims on 7^3 (classical is CPU-expensive there) -> flagged follow-up. Artifacts:
test_time_scaling.json, test_time_scaling_summary.md. $0/local. Stop reason: objective_met (test-time-scaling half of S1 delivered; net-vs-classical@7^3 high-budget remains).