---
node_id: c017760b-671f-54f1-951d-50887754dad7
slug: snowy-brook-3358
title: 'AUX-3 — Soft policy target (T=4, x8 weight, prune) [RESOLVED: small consistent gain, NOT decisive]'
created_at: '2026-06-09T07:00:06.703712+00:00'
parents:
- delicate-breeze-7763
- gentle-glitter-1363
- proud-king-2753
summary: 'RESOLVED. Soft policy target (prune + visits^(1/4) + 8x weight) vs hard argmax, 5^3, 3 seeds, 52901-ex data. Soft beats hard on ALL 3 seeds (+2.9pp pooled, 0.269->0.298) and has lower value-MSE on all 3 seeds, but Wilson CIs OVERLAP -> consistent-but-NOT-decisive; neither beats classical at 5^3. Meta-finding with AUX-1: two target/aux-representation changes both give small consistent non-decisive gains -> the 5^3 strength ceiling is NOT the supervision target; pivot to input representation (ARCH-3) + capacity (ARCH-2/ALGO-2).'
origin:
  backend: flywheel
  node_id: c017760b-671f-54f1-951d-50887754dad7
  slug: snowy-brook-3358
  revision: 3
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: e86b70d4-28bf-582a-9bb8-9b4332ca4e6b
  slug: raspy-star-4294
  revision: 0
  pushed_at: '2026-08-08T10:03:17+00:00'
  content_sha256: 0c6502487a103e4a62b8ae93c7c3c9e6136f1808f28b8417ea365299aadafb5b
---
# AUX-3 — Soft policy target (T=4, x8 weight, prune) [RESOLVED: small consistent gain, NOT decisive]

*Executed in PASS 17 (rolling EXPANSION campaign, $0/local), picked over AUX-2 because AUX-1 localized the 5^3 bottleneck to the starved POLICY head (acc trending the wrong way as boards grow).*

## What was built (train-only; no engine change)
- `collect_softpolicy.py` — distill collector that stores **raw MCTS visit counts V** per position (move selection keeps the campaign's temp anneal so the X-distribution matches existing data; only the stored target differs). Regenerated 5^3 data: **52,901 examples**, classical@128 teacher.
- `train_softpolicy.py` — plain `A3GoNet`, builds the policy target two ways from the same V/Z/seed: **HARD** = one-hot argmax(visits), policy weight 1x; **SOFT** = prune actions < 2% of max visits, target ∝ visits^(1/T) with T=4, policy loss up-weighted **8x** (KataGo recipe). Clean A/B (identical architecture + init).

## Result (5^3, net_sims=512 vs classical@48 cap50, n=128, 3 seeds, pooled)
| arm | wins/decided | winrate | Wilson 95% | holdout value-MSE |
|---|---|---|---|---|
| HARD (argmax, 1x) | 103/383 | 0.269 | [0.227, 0.316] | 0.048-0.055 |
| SOFT (T=4, 8x, prune) | 114/383 | **0.298** | [0.254, 0.345] | **0.033-0.041** |

**Per-seed (paired):** soft beats hard on **all 3 seeds** (+0.047, +0.023, +0.015) and has **lower value-MSE on all 3 seeds**. But pooled Wilson CIs **OVERLAP** (0.316 vs 0.254) → the +2.9pp strength edge is **consistent in direction but NOT decisive**. **Neither arm beats classical at 5^3** (both ~0.27-0.30, well under 0.5).

*(Holdout top1/top3-vs-argmax favors HARD by construction — argmax IS its training objective — so it is not a fair policy-quality metric. The meaningful, unbiased signals are strength and value-MSE, both of which favor SOFT consistently but marginally.)*

## Verdict vs decision criterion
Criterion: soft beats hard with **CI separation** on >=1 board size, OR holdout policy accuracy improves with CI separation with no strength regression.
- Strength: soft > hard every seed but pooled **CIs overlap** → not decisive.
- A fair policy-accuracy CI-win was not obtained (the argmax metric is hard's own objective).
- Value-MSE consistently better for soft (no CI computed).

**=> Criterion NOT decisively met. Result = consistent-but-marginal POSITIVE (softer, up-weighted policy target helps value calibration and slightly helps strength on every seed), not a decisive lever.**

## Meta-finding (AUX-1 + AUX-3 together) — feeds the replan
Two independent target/auxiliary-representation changes — dense ownership (AUX-1) and softened+weighted policy (AUX-3) — each yield **small, consistent, but non-decisive** gains, and **neither makes the 64x6 net beat classical at 5^3**. The 5^3 absolute-strength ceiling is **not** set by how the net is *supervised* (target representation); it is deeper. Remaining untried levers: **input representation** (ARCH-3 richer planes — what the net can SEE) and **raw capacity / capacity-per-flop** (ARCH-2 / ALGO-2). The campaign should pivot from target-tweaks to those.

## Artifacts
- `aux3_ab_summary.json` — pooled Wilson CIs, per-seed paired strength + value-MSE, verdict.
- `train_softpolicy.py`, `collect_softpolicy.py` — implementation + raw-visit data-gen.
- Data: `distill_softpol_5cubed.npz` (52,901 ex; in working tree).

*RESOLVED in PASS 17. stop_reason (branch) = objective_met (clean answer; consistent-but-marginal positive, not decisive).*