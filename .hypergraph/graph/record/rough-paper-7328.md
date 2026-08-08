---
node_id: b3ea0b95-d37f-5c6e-94e2-b43d26633cae
slug: rough-paper-7328
title: 'INFRA-3 RUN 3 — classical-anchored self-play on 5^3: apparent absolute lift was SMALL-SAMPLE NOISE; S5-absolute NOT met (n=128 A/B: champion == seed)'
created_at: '2026-06-08T21:28:49.294488+00:00'
parents:
- billowing-dew-3640
- mute-cloud-4824
summary: 'INFRA-3 RUN 3: classical-anchored self-play on 5^3 (gate on cand-vs-classical, the OOD objective PASS-14 said was missing). In-loop n=32 anchor reported a 0.194->0.406 lift (1 promotion) — but well-powered n=128 A/B OVERTURNS it: champion 0.262@48 / 0.402@512 is statistically identical to the seed (0.234@48 / 0.414@512); CIs fully overlap. S5-absolute NOT met on 5^3 by either gate. The apparent gains (and the 0.594@512 n=32 reading) were small-sample noise; the gate promoted on a 32-game fluctuation. Lesson: gate/claim on n>=128 — even the seed''s ''parity@512=0.50'' [e7c35c64,n32] is 0.414 [0.332,0.501] at n128. $0/local.'
origin:
  backend: flywheel
  node_id: b3ea0b95-d37f-5c6e-94e2-b43d26633cae
  slug: rough-paper-7328
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 1297cdff-d9ed-50dc-a004-52d0806811fe
  slug: summer-mountain-6648
  revision: 0
  pushed_at: '2026-08-08T10:03:07+00:00'
  content_sha256: 1ba9fb9f46ec18020fc348b5dcd94b96d045d6cae05729c16cfad950abe6b859
---
# INFRA-3 RUN 3 — classical-anchored self-play on 5³: the gain was small-sample NOISE (S5-absolute NOT met)

**Direct A/B test of the PASS-14 hypothesis** [INFRA-3 `8a724b1c`]. PASS-14 found a
frozen-*net*-anchored self-play champion beat its own distilled seed 0.735
head-to-head yet did NOT beat classical any better than the seed, and conjectured
the gate was optimizing the wrong proxy. PASS-15 swaps the gate to anchor on the OOD
objective — **cand-vs-CLASSICAL** — same seed (`best_distill5strong_5cubed.pt`,
64×6), same board (5³), same sims (48), same iters (8×80 games).
`neural/az_selfplay_clsmp.py` (the in-loop classical anchor runs through the parallel
`net_vs_classical_mp` harness, ~4 min/eval; the sequential in-loop path stalled
>40 min/eval on 5³ — why RUN 2 used a frozen net).

## What the loop reported (and why it was misleading)
1 promotion: **it1 cand-vs-classical@48 = 0.406** vs the seed's in-loop anchor 0.194
→ looked like a ~2× absolute lift. it2–it8 all failed the net-vs-best gate (≥0.55)
and were kept (the it1 net dominates the in-family population; buffer capped at 400).
A first n=32 translation of the it1 champion at 512 sims read **0.594 [0.423, 0.745]**
— apparently above parity. Both numbers were from **n=32** evals.

## Well-powered re-measurement (n=128) — the lift vanishes
Re-running the translation at **128 games** (CI half-width ~0.08 vs ~0.16 at n=32):

| vs classical | @48 sims (n=128) | @512 sims (n=128) |
|---|---|---|
| distilled seed | 0.234 [0.168, 0.316] | 0.414 [0.332, 0.501] |
| cls-anchored champion | 0.262 [0.193, 0.345] | **0.402 [0.32, 0.489]** |

- **The champion is statistically indistinguishable from the seed at both sim levels** — CIs fully overlap; both differences are well within noise.
- The it1 promotion's 0.406@48 collapses to **0.262** at n=128; the 0.594@512 collapses to **0.402** (CI *upper* 0.489 < 0.5). **The gate promoted on a 32-game noise fluctuation.**
- **S5-absolute is NOT met on 5³.** Combined with PASS-14 (frozen-net gate, also no absolute lift), **neither self-play variant beats classical any better than plain distillation on 5³.**

## The deeper finding: the campaign's n≈24–32 evals are under-powered
A win-rate eval at n=32 has a 95% CI half-width of ~0.16 — too wide for the
distinctions repeatedly drawn from such evals (parity@512, 0.735 "gains", 0.406
"lifts", single-promotion gates). Concretely, the seed's headline **"5³ reaches
parity with classical @512 = 0.50" [e7c35c64] was n=32; at n=128 it is 0.414
[0.332, 0.501]** — i.e. the distilled 5³ net sits *just below* parity, not at it.
Two independent n=32 measurements of THIS champion (0.406@48, 0.594@512) both landed
high and both regressed to ~0.40 at n=128 — random, not systematic, but enough to
trigger a spurious promotion. **Lesson: gate promotions and any "beats/ties
classical" claim on ≥n=128; treat all prior n≤32 win-rates as point estimates with
±0.16 error bars.**

## Verdict
- **Relative S5** (beat your own seed in-family): met in PASS-14 (0.735) but is not a
  valid strength signal — see methodology node `dcd0a5db`.
- **Absolute S5** (beat the classical teacher): **NOT met on 5³**, well-powered. The
  distilled net ≈ self-play champion ≈ **~0.40–0.41 vs classical@512** (just below
  parity). Self-play on 5³, by either gate, adds no absolute strength over distillation.

**Reproduce:** `cd neural && A3GO_CH=64 A3GO_BLK=6 uv run python az_selfplay_clsmp.py 5 8 80 48`;
A/B `... net_vs_classical_mp.py {best_az_cls5_5cubed.pt,best_distill5strong_5cubed.pt} 5 128 {48,512} 48 50 <out>`.
$0/local, RTX 5090 free, ~3.5h total. Artifacts: az_cls5_5cubed.json,
experiments_azcls5_vs_cls_s48_n128.json, experiments_azcls5_vs_cls_s512_n128.json,
experiments_seed5_vs_cls_s48_n128.json, experiments_seed5_vs_cls_s512_n128.json.

**Stop reason: `objective_met`** — the probe decisively answered the question
(negative: classical-anchored self-play does not beat classical on 5³; the apparent
gain was small-sample noise). Highest-value next step shifts from "more self-play" to
the capacity lever (ALGO-2) and re-powering the campaign's key win-rate claims at n≥128.
