---
node_id: 55b62936-d579-5b44-a636-b05d62e0f1c6
slug: keen-tower-2320
title: Neural stack
created_at: '2026-08-07T20:33:57+00:00'
parents:
- royal-comet-4977
summary: Distill-then-scale is the proven path (0.085→0.612 on 4^3); liberty planes decisive on 5^3; capacity saturates past 96x8; aux heads learn but do not lift strength.
flywheel:
  node_id: 2ae256a3-7d30-502f-88fb-4a3364a9058c
  slug: delicate-thunder-5530
  revision: 0
  pushed_at: '2026-08-07T20:39:47+00:00'
  content_sha256: b650ef5432a0238b9abe5a638675a664ccbd94c7a35cddbd56412e5ade76e0ab
---
Status: working

## Current

- The proven path to strength is distill-then-scale, not cold-start self-play: 0.085 → 0.333 vs classical by distilling the classical teacher into the same 32×3 net [rec: round-wave-9279]; → 0.458 with a stronger 192-playout teacher [rec: winter-water-4984]; → 0.612 [0.533,0.686] (n=160) by raising capacity 32×3→64×6 on the same 29.6k examples — the first net to beat classical on 4³ [rec: soft-waterfall-3492].
- Input representation is the biggest post-capacity lever: liberty planes are decisively positive on 5³ (+0.144, 0.449 [0.400,0.499], CI-separated, every seed above the baseline's best seed) and beat the 10-plane kitchen sink (0.411) — focused features beat a feature dump [rec: polished-field-7944].
- Capacity saturates on the liberty net: libs96×8 ≈ libs64×6 (Elo 78.6 vs 70.9), and libs128×10 rates below the 3-plane baseline (−11.0) at the fixed training budget — libs@64×6 remains the strongest 5³ net [rec: bitter-pine-2861].
- Aux heads learn their targets but do not move strength while policy supervision binds (5³ holdout policy acc ~0.06): ownership own_acc 0.983–0.986, per-voxel sign agreement 0.927, strength +6.5pp with overlapping CIs [rec: proud-star-4959]; soft policy target positive on all 3 seeds but pooled CIs overlap [rec: snowy-brook-3358]; BN-free nested-bottleneck is strength-parity, 20% fewer params, 13% slower [rec: purple-field-4026].
- Cross-board scaling law (4³/5³/7³): value gets easier (MSE 0.044→0.019→0.006, big boards are all-decisive), policy gets harder (argmax acc 0.12→0.07→0.05 as actions grow 65→126→344), required sims grow (48→512→≫512) [rec: delicate-breeze-7763].
- My/opp liberty split (REP-3) is directionally positive but under-powered (0.5585 [0.459,0.658], n=96); the finer-bucket arm needs one re-collection [rec: small-mountain-7064].

## Negative knowledge

- [scope: lifting 5³ absolute strength via supervision-side tweaks (aux heads, soft targets, BN-free reshaping) | confidence: high | evidence: proud-star-4959, snowy-brook-3358, purple-field-4026] Target/architecture tweaks at fixed scale do not move absolute strength while policy supervision is the binding constraint — and the "cheap-tweak cluster exhausted" meta-conclusion drawn from them was overturned one pass later by the liberty planes (polished-field-7944).
- [scope: ko-ban input plane on boards ≤5³ | confidence: high | evidence: polished-field-7944, spring-sea-3008] The KataGo-inspired ko-ban plane is falsified on 5³ (the only negative arm, −0.027): ko-ban density is under 0.1% of cells, and the ~98% ko-ubiquity prior it rested on measured 18–32% in play.
- [scope: ReZero-style gamma=0 init on this stack | confidence: medium | evidence: purple-field-4026] gamma=0 residual gating fails to converge (top1 stuck ~0.05 after 10 epochs); gamma0=0.3 restored convergence — BN-free training is not free.

## Provenance

- lively-orchard-3365 — adoption distillation
- round-wave-9279 — distillation 4x lift
- winter-water-4984 — stronger teacher to near-parity
- soft-waterfall-3492 — capacity crosses the line, 0.612
- polished-field-7944 — ARCH-3 liberty planes decisive
- bitter-pine-2861 — SCALE-libs capacity null
- proud-star-4959 — AUX-1 ownership: learns, strength flat
- snowy-brook-3358 — AUX-3 soft policy marginal
- purple-field-4026 — ARCH-2 BN-free parity, slower
- delicate-breeze-7763 — cross-board scaling law
- small-mountain-7064 — REP-3 my/opp split, under-powered
