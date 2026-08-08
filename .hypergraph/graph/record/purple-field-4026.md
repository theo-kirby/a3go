---
node_id: 8cecf366-472e-5450-89c6-b149b3ed36f3
slug: purple-field-4026
title: 'ARCH-2 — BN-free nested-bottleneck + fixed-variance init [RESOLVED: strength parity, no efficiency win]'
created_at: '2026-06-09T07:00:13.180990+00:00'
parents:
- gentle-glitter-1363
- shrill-morning-5745
- proud-king-2753
summary: 'RESOLVED. BN-free nested-bottleneck net (A3GoNetBR, 1.13M, ~20% fewer params) vs BN-64x6 baseline, same 5^3 data+soft-target, 3 seeds. STRENGTH PARITY (0.303 [0.259,0.351] vs 0.298 [0.254,0.345], CIs overlap; neither beats classical) but 13% SLOWER per CPU eval game (more sequential layers) + weaker policy-top1 (value head carries parity). ReZero gamma=0 too slow -> gamma0=0.3 needed (init risk confirmed). Criterion NOT met. THIRD consecutive non-decisive branch -> 5^3 ceiling resists target-rep (AUX-1,AUX-3) AND capacity-reshaping (ARCH-2). Next real levers: richer INPUT planes (ARCH-3), raw SCALE-UP (net+data), or the C++ engine.'
origin:
  backend: flywheel
  node_id: 8cecf366-472e-5450-89c6-b149b3ed36f3
  slug: purple-field-4026
  revision: 3
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: c89cab89-9432-5f21-ac15-6cad04e172e3
  slug: steep-term-3573
  revision: 0
  pushed_at: '2026-08-08T10:03:07+00:00'
  content_sha256: aae0c359faef38b7cf36bdb86908c47aa87c1eb98e66bc9907fc79da3d565fd3
---
# ARCH-2 — BN-free nested-bottleneck + fixed-variance init [RESOLVED: strength parity, no efficiency win]

*Executed in PASS 17 (rolling EXPANSION campaign, $0/local), picked as PRIMARY after AUX-1+AUX-3 showed target-representation is exhausted and the campaign's evidence pointed to capacity as the S1 lever (32x3->64x6 was the move that first beat classical, `b71da32b`).*

## What was built (train-only, additive; net.py UNCHANGED -> 48/48 + cross-vals safe)
- `net_arch2.py` — `A3GoNetBR`: identical I/O to A3GoNet (3 planes in; policy logits + tanh value out; `forward(x)->(p,v)` so BatchedMCTS/eval run unchanged). Trunk replaced with **nested-bottleneck blocks** (1x1 reduce c->cb -> inner residual of two 3x3 convs at cb -> 1x1 expand) and **NO BatchNorm anywhere** (stem, tower, heads). Config used: c=64, cb=48, 8 blocks -> **1.13M params (vs BN-64x6 = 1.41M, ~20% fewer).**
- `train_arch2.py` / `eval_arch2.py` — train on the **same** AUX-3 raw-visit data with the **same soft target** (T=4, x8, prune 0.02) so ONLY the architecture differs vs AUX-3's BN-soft arm; eval records games/sec.

## Fixed-variance init — the node-flagged risk, confirmed
ReZero-style **gamma=0** gate (identity at init) converged **far too slowly** — the deep trunk stays gated off and only stem+heads train (smoke: top1 stuck ~0.05 after 10 epochs). Fixing **gamma0=0.3** (per-block residual variance ~O(1/L)) restored convergence in comparable epochs. BN-free training of this net is **not free** — it needs init care.

## Result (5^3, net@512 vs cls@48, n=128, 3 seeds, pooled; identical data+target)
| net | strength | Wilson 95% | params | clean games/sec | holdout policy top1 |
|---|---|---|---|---|---|
| **ARCH-2** BN-free nested-bottleneck | **0.303** | [0.259, 0.351] | 1.13M | 0.041 | ~0.078 |
| BN-64x6 baseline (AUX-3 soft) | 0.298 | [0.254, 0.345] | 1.41M | 0.047 | ~0.11 |

- **Strength: PARITY** (Δ=+0.5pp, CIs almost fully overlap; per-seed 0.328/0.268/0.312). **Neither beats classical at 5^3.**
- **Value-MSE matches** (curves artifact); **policy top-1/top-3 LAGS** BN (top3 ~0.14 vs ~0.21) — yet strength held parity, so the **value head + soft target carry play strength**, not policy top-1.
- **Speed: 0.87x — ARCH-2 is 13% SLOWER per CPU eval game** despite 20% fewer params, because nested bottlenecks add sequential conv layers (8x4 vs 6x2); fewer FLOPs/params != faster wall-clock on the CPU inference path. (An earlier "faster" reading was contention artifact; this is uncontended.)

## Verdict vs decision criterion
Criterion: at matched wall-clock the nested-bottleneck net beats BN with CI separation, OR matches strength at lower FLOPs (efficiency CI).
- Strength CIs overlap -> no win. Param/FLOP reduction is real (~20%) but wall-clock is SLOWER, so no per-wallclock efficiency win either.

**=> Criterion NOT met. ARCH-2 = strength parity at fewer params but no wall-clock or strength advantage; BN-free conversion needs init tuning and regresses the policy head.**

## Meta-conclusion (AUX-1 + AUX-3 + ARCH-2) — THREE non-decisive branches
Three independent cheap levers — dense ownership target (AUX-1), softened+weighted policy target (AUX-3), and BN-free capacity-per-FLOP architecture (ARCH-2) — **all fail to move the 5^3 absolute ceiling past classical**, each landing parity-to-marginal. The 5^3 strength wall is **robust to target-representation AND to capacity-reshaping at fixed scale**. Remaining genuinely-different levers: **(1) richer INPUT planes (ARCH-3)** — change what the net SEES, not how it's supervised/shaped; **(2) raw SCALE-UP** (more channels/blocks + more teacher data — the literal 32x3->64x6 move, now 96x8/128x10, gated on slower data-gen); **(3) stronger teacher/search** (data ceiling); **(4) the C++ engine** for 7^3+ scale. *Recommend surfacing to the human: the cheap-tweak cluster is exhausted; the next real leap likely needs scale (net+data) or the C++ engine — a larger discrete effort.*

## Artifacts
- `arch2_ab_summary.json` — pooled 3-seed strength, clean speed, param table, verdict.
- `arch2_bn_vs_fixedvar_curves.png` — BN-free vs BN training curves (value matches, policy lags).
- `net_arch2.py` — A3GoNetBR implementation. (`train_arch2.py`/`eval_arch2.py` in working tree.)

*RESOLVED in PASS 17. stop_reason (branch) = objective_met (clean answer; parity, not a win).*