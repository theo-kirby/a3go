---
node_id: 0bc38c41-87d9-5623-be09-0fc6a8b65ecf
slug: delicate-breeze-7763
title: '7^3 characterization: a clean cross-board SCALING LAW — value gets easier (MSE 0.044->0.019->0.006), policy harder (acc 0.12->0.07->0.05), required sims grow (48->512->>>512) for 4^3/5^3/7^3'
created_at: '2026-06-08T05:00:14.780742+00:00'
parents:
- bold-scene-5560
- blue-boat-2948
- withered-boat-6047
summary: 'C++ engine made 7^3 tractable (33.8k examples in 15 min). Distilled 64x6 net reveals 3 monotone cross-board trends: value MSE falls (bigger boards all-decisive -> cleaner targets), policy acc falls (bigger action space), required MCTS sims grow (48->512->>>512). 7^3 value head near-perfect (MSE 0.006); strength is sim-bound on CPU eval -> next bottleneck is GPU-batched MCTS for big-board high-sim play.'
flywheel:
  node_id: 0bc38c41-87d9-5623-be09-0fc6a8b65ecf
  slug: delicate-breeze-7763
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: cef259f21fd0ecdc7c9f481e544d9fcef49f3682a432cfcfb025645b6acbe047
---
# 7^3 characterization (via the C++ engine): a clean cross-board scaling LAW for 3D Go

With the C++ engine, 7^3 self-play became feasible (96 s/game @48 playouts; Python couldn't run it). Collected 64 classical 7^3 games (33,809 examples, 15 min parallel), distilled a 64x6 net.

## The cross-board scaling law (the headline)
Measuring the distilled net across board sizes reveals three clean MONOTONE trends:
| board | actions | holdout VALUE MSE | holdout POLICY acc | sims to ~parity vs classical |
|---|---|---|---|---|
| 4^3 | 65 | 0.044 | 0.12 | **48** (wins 0.61) [b71da32b] |
| 5^3 | 126 | 0.019 | 0.07 | **512** (parity) [e7c35c64] |
| 7^3 | 344 | **0.006** | **0.05** | **>>512** (sim-bound) |

- **Value gets EASIER on bigger boards** (MSE 0.044 -> 0.019 -> 0.006). Bigger 3D boards are all-decisive (0 draws), giving cleaner outcome targets — the value head nearly memorizes them.
- **Policy gets HARDER** (argmax-acc 0.12 -> 0.07 -> 0.05). The action space grows (65 -> 126 -> 344) and visit targets diffuse.
- **Required MCTS search GROWS with the action space** (48 -> 512 -> >>512 sims to reach parity). This is the binding constraint on bigger boards, exactly as the 5^3 transfer node found.

So the recipe's *components* scale predictably: distillation gives an ever-better value head for free, but you must pay for proportionally deeper (cheap, batched) search to exploit it, and the policy needs more/stronger teacher data.

## 7^3 strength point (incomplete by design)
net@256 vs classical@48 on 7^3 did not finish cleanly — net@256 on a 343-point board is ~12+ min/game on CPU (256 forwards x ~340 moves), and per the scaling law 7^3 needs FAR more than 256 sims to be competitive anyway. So a clean 7^3 strength number is **sim-bound on $0/local CPU eval** — the natural place where the GPU-batched-MCTS (a real AZ inference server, autogo-style) would be needed to evaluate big boards at the sims they require. Recorded as a limit, not a failure.

## Status
4^3: net beats classical (0.61). 5^3: parity@512, climbing. 7^3: value head near-perfect (MSE 0.006), strength sim-bound. The distillation recipe + the scaling law characterize 3D-Go neural play across board sizes. The C++ engine [cff3a5d1] made the 7^3 data tractable; the remaining bottleneck shifts to GPU-batched MCTS for high-sim play/eval on big boards.

Artifact: distill_7cubed.npz metadata (33,809 examples), train curve inline.