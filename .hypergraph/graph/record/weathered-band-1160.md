---
node_id: 2119a00c-2218-54c8-b955-d74a21df8f2e
slug: weathered-band-1160
title: Neural pipeline runs end-to-end (beats random, loss↓) but rising-strength NOT clean on 3³ — policy collapses to draws (~70%)
created_at: '2026-06-07T13:08:37.993298+00:00'
parents:
- crimson-frog-9812
- broken-firefly-1068
summary: 'Milestone 3/4. Full AZ self-play→train→eval loop runs on the RTX 5090: 6 gens on 3³, loss 2.90→1.78, net beats uniform-random 76-93%. BUT self-play draw rate ~70% and the trained net loses to the untrained gen0 net (vs_gen0 0.06-0.20) — a policy collapse to drawing. Pipeline proven; rising-strength (Q10) needs fixes (root Dirichlet noise, komi/larger board, more sims).'
origin:
  backend: flywheel
  node_id: 2119a00c-2218-54c8-b955-d74a21df8f2e
  slug: weathered-band-1160
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: be752eec-0f0f-5b42-9f3c-ab77aa1a3990
  slug: jolly-thunder-8172
  revision: 0
  pushed_at: '2026-08-08T10:01:49+00:00'
  content_sha256: b7897b61124f607ef5f7553336ed4997b863a869ec2d580f8829a965df712c6b
---
# Phase 2 milestone 3 — end-to-end AZ loop (honest first result)

## What was done
Implemented the full AlphaZero loop in Python: `net.py` (3D-conv policy/value resnet), `az.py` (PUCT MCTS guided by the net + self-play + evaluation), `train.py` (self-play → train → evaluate per generation). Ran **6 generations on 3³**, 30 self-play games/gen, 32 sims/move, on the RTX 5090 (534 s).

## Result
| gen | vs random | vs gen0 | loss | self-play B/W/draw |
|---|---|---|---|---|
| 1 | 0.86 | 0.52 | 2.90 | 13/10/7 |
| 2 | 0.79 | 0.12 | 2.49 | 4/5/21 |
| 3 | 0.81 | 0.06 | 2.44 | 4/3/23 |
| 4 | 0.76 | 0.20 | 2.03 | 4/3/23 |
| 5 | 0.93 | 0.06 | 1.84 | 4/7/19 |
| 6 | 0.78 | 0.12 | 1.78 | 6/4/20 |

## Reading (what worked / what didn't)
- **Works:** the pipeline is real and end-to-end on GPU — training loss falls monotonically (2.90→1.78) and the net **beats uniform-random 76–93%** at every generation. Milestone 3 (pipeline proven) is met.
- **Doesn't (yet):** **no clean rising-strength curve.** From gen 2 on, **~70% of self-play games are draws**, and the trained net **loses to the untrained gen0 net** (vs_gen0 0.06–0.20 ≪ 0.5). The net has collapsed onto a drawing/over-cautious policy that a near-uniform net actually exploits.

## Diagnosis (likely causes, all standard)
1. **No root exploration noise** — canonical AZ adds Dirichlet noise to the root prior during self-play; without it the policy collapses and self-play loses diversity.
2. **3³ is draw-prone and near-2D** (Q5: mean degree 4.0; Q1: blowout/komi-degenerate) — a poor board to learn rich strategy; komi 0 makes balanced fills draw.
3. **Draws give a weak value signal** (z=0), so the value head learns ≈0 and stops discriminating.

## Next (replan, executing)
- Add **Dirichlet root noise** + keep low-temp self-play exploration.
- Move to **4³** (genuinely 3D, far fewer draws) and/or set a komi to break symmetry; raise sims.
- Re-measure the gen-over-gen curve and net-vs-classical-MCTS (Q10), then value-head komi (Q9).

## Reproduce
`uv run --directory neural python train.py 3 6 30 32 train_result_3.json`. Artifact attached (full history JSON).