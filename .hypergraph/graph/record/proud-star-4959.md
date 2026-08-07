---
node_id: 665706e4-f3f0-5331-8031-f9b98412b79a
slug: proud-star-4959
title: 'AUX-1 — Per-voxel ownership head [RESOLVED: predictor works, strength lever weak/non-decisive]'
created_at: '2026-06-09T07:00:04.893070+00:00'
parents:
- gentle-glitter-1363
- delicate-breeze-7763
- proud-king-2753
summary: 'RESOLVED. Ownership aux head learns the territory map excellently (holdout own_acc 0.983-0.986, fresh-game sign-agreement 0.927 >> 0.8 bar) but does NOT decisively lift 5^3 strength (pooled 3-seed s512: baseline 0.328 vs ownership 0.393, +6.5pp, Wilson CIs OVERLAP; 1/3 seeds reverses) and value-MSE is only mixed/weakly favorable (s1 0.0248->0.0177, s2 0.0252->0.0228, but seed0 0.0144->0.0173). Decision criterion NOT met. Verdict: NEGATIVE for the strength/calibration hypothesis on 5^3, POSITIVE deliverable (a working ownership predictor that unblocks TOOL-3 heatmap + SCIENCE-2 life&death). Consistent with the campaign scar: the 5^3 bottleneck is the policy head (acc ~0.06) + absolute capacity, not aux regularization.'
flywheel:
  node_id: 665706e4-f3f0-5331-8031-f9b98412b79a
  slug: proud-star-4959
  revision: 4
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: dac420e068b9d4b2464fb13d0795b761262a1ef3821d9325d92ad9bde0a8391a
---
# AUX-1 — Per-voxel ownership / territory head [RESOLVED]

*Executed in PASS 17 (rolling EXPANSION campaign, $0/local). First branch picked off the menu — KataGo's single biggest early accelerator.*

## What was built (additive; logged in VENDORED.md)
- `Board.ownership_map()` — per-voxel Tromp-Taylor owner in {-1,0,+1}, reusing the `score_tromp_taylor` flood-fill (validated exact vs area counts).
- `collect_ownership.py` — distill data WITH per-voxel ownership labels signed to side-to-move (matching Z).
- `net_ownership.py` — `A3GoNetOwn`: A3GoNet's stem/tower/policy/value **byte-for-byte**, plus an ownership head (conv->tanh, per-voxel). `forward()` keeps the `(p,v)` signature so BatchedMCTS/eval run unchanged; `forward_own()` adds the `(B,N,N,N)` map. The A/B baseline is the **same class trained with lambda=0** (ownership head gets no gradient; trunk identical) vs lambda>0 — same architecture, same init seed, only difference = whether the dense signal flows into the trunk.
- `train_ownership.py` — joint loss `policy CE + value MSE + lambda*ownership-MSE`, lambda swept {0, 1.0, 1.5}.

## Result (4^3 + 5^3, n>=128, parallel, equal budget vs classical@48)

### Ownership head learns the map — strongly (the deliverable)
| lambda | holdout own_acc | holdout own_MSE | holdout value_MSE |
|---|---|---|---|
| 0.0 (baseline) | ~0.50 (random) | ~0.978 | 0.0144-0.0252 |
| 1.0 | **0.983-0.986** | **0.044-0.052** | 0.0173-0.0228 |
| 1.5 | 0.986 | 0.041 | 0.0156 |

Fresh played-game check (5^3, classical self-play, held out of training): predicted-vs-true per-voxel **sign-agreement = 0.927** on decided cells (see heatmap artifact). The dense spatial target is clearly learnable on 3D boards — this is a usable ownership/territory predictor.

### Strength — NOT decisively lifted (pooled 3 seeds, 5^3, net_sims=512)
| variant | wins/decided | winrate | Wilson 95% |
|---|---|---|---|
| baseline lambda=0 | 125/381 | 0.328 | [0.282, 0.377] |
| ownership lambda=1.0 | 149/379 | **0.393** | [0.346, 0.443] |

+6.5pp for ownership, but the **CIs overlap** (0.377 vs 0.346) and seed1 actually reverses it (l00 0.365 vs l10 0.312). 4^3@48 is flat (0.472/0.463/0.472, all overlapping). **Neither variant beats classical at 5^3** (both < 0.5).

### Value-calibration — mixed, not decisive
Ownership improves holdout value-MSE on 2 of 3 seeds (s1 0.0248->0.0177; s2 0.0252->0.0228) but not seed0 (0.0144->0.0173). No CI on value-MSE -> the "value-MSE drops with CI separation" leg is not satisfied.

## Verdict vs decision criterion
Criterion: ownership net beats baseline with non-overlapping strength CIs **OR** (value-MSE drops with CI separation **AND** own_acc > 0.8). 
- Strength CIs **overlap** -> first leg fails.
- own_acc 0.985 >> 0.8 **passes**, but value-MSE drop is not CI-separated -> second leg fails.

**=> Criterion NOT met. NEGATIVE for the strength/value-calibration hypothesis on 5^3; POSITIVE deliverable (a working per-voxel ownership predictor).** This sharpens the recurring campaign scar (PASS-15 `b3ea0b95`, scaling-law `0bc38c41`): the 5^3 ceiling is set by the **starved policy head** (holdout policy_acc ~0.06) and absolute trunk capacity, not by lack of an auxiliary dense target. An aux head alone does not move absolute strength when policy supervision is the binding constraint.

## So what / next levers (feeds replan)
- The ownership predictor is delivered -> **TOOL-3** (ownership heatmap) and **SCIENCE-2** (`777d5c9e`, life&death) are now unblocked with a real signal.
- Strength-wise, evidence now points harder at the **policy head**: AUX-3 soft/temperature policy targets, and capacity/input-plane levers (ARCH-2/ARCH-3). AUX-2 (score-margin head) is the next aux probe but, given AUX-1, expect a similar 'learns-fine, strength-flat' outcome unless paired with a policy-side fix.
- Recommend next pick: **AUX-3 (soft policy targets)** to attack the binding constraint directly, OR **AUX-2 (score head)** to complete the aux-cluster characterization cheaply. See control node replan.

## Artifacts
- `aux1_ab_summary.json` — pooled Wilson CIs + per-seed train metrics + heatmap sign-agreement.
- `aux1_ownership_heatmap.png` — true vs net-predicted ownership across all 5 z-slices.
- `net_ownership.py`, `train_ownership.py` — implementation.
- (data-gen `collect_ownership.py` + engine `Board.ownership_map()` live in the repo working tree; ownership_map logged in VENDORED.md.)

*RESOLVED in PASS 17. stop_reason (branch) = objective_met (experiment ran to a clean answer; hypothesis result negative-with-deliverable).*