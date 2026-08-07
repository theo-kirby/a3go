---
node_id: 230df7de-636c-5960-85b4-f07ef8f7a02f
slug: square-lodge-0776
title: Evaluation & statistics
created_at: '2026-08-07T20:34:19+00:00'
parents:
- royal-comet-4977
summary: Anchored Elo ladder + SPRT gate + GPU net-vs-net screen; standing n>=128 discipline born from the n=32 promotion scar.
---
Status: working

## Current

- The anchored Elo ladder is the S2 instrument: Bradley-Terry MLE with a weak symmetric prior, bootstrap 95% CIs, random pinned at Elo 0; full 4³ ladder delivered (cls@128 849 > net@256 784 > net@128 656 > cls@48 638 > net@48 611 > cls@16 396 > random 0) [rec: empty-lab-3357].
- SPRT gate built and validated live: Wald SPRT (H0 0.50 / H1 0.55, α=β=0.05) returned not_a_winner at n=98 for libs@64 vs classical, CI-consistent with the fixed-n measurement — near-parity is SPRT's hardest case, so savings are modest there [rec: dawn-pond-0204].
- GPU net-vs-net screening (~36 min) replaced ~3 h/seed CPU net-vs-classical for exploratory A/Bs, with an SPRT classical anchor reserved for confirmed winners; lazy plane encoding validated byte-identical and 4.5×–119× faster [rec: bitter-pine-2861].
- Standing discipline: gate promotions and any beats/ties-classical claim on n≥128; treat all n≤32 win-rates as point estimates with ±0.16 error bars [rec: rough-paper-7328].

## Negative knowledge

- [scope: gating promotions or headline claims on n≤32 evaluations | confidence: high | evidence: rough-paper-7328, bold-pine-0367] The n=32 scar: two independent n=32 reads of the same champion both landed high and both collapsed at n=128 (0.406→0.262, 0.594→0.402), firing a spurious promotion; the 5³ parity@512 headline collapsed to 0.414 [0.332,0.501] the same way.
- [scope: net-vs-net or self-play metrics as absolute-strength proxies | confidence: high | evidence: noisy-bonus-3509, billowing-dew-3640] Self-referential metrics can move opposite to truth (0.333→0.222 vs classical while every internal metric improved); a frozen anchor cures gate drift but net-vs-net still overstates strength against an out-of-distribution baseline.
- [scope: rating ladders over deterministic argmax agents | confidence: high | evidence: empty-lab-3357] Pure-argmax play degenerates the ladder (40/40 results, intransitive cycles) and Bradley-Terry diverges under perfect separation — sample opening plies and regularize the fit; a CUDA-initialized parent cannot fork (use spawn, pin threads).

## Provenance

- lively-orchard-3365 — adoption distillation
- empty-lab-3357 — PROOF-1 ladder + its three methodology fixes
- dawn-pond-0204 — EVAL-1 SPRT built + validated
- bitter-pine-2861 — GPU net-vs-net screening pivot
- rough-paper-7328 — n=32 artifact + n>=128 rule
- noisy-bonus-3509 — unanchored gate moves opposite to truth
