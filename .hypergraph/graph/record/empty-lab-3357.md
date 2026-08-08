---
node_id: 3ac354fd-ff3a-5e3a-be95-876b6c503d40
slug: empty-lab-3357
title: 'PROOF-1 — anchored Elo ladder [DELIVERED on 4^3: cls@128 849 > net@256 784 > net@128 656 > cls@48 638 > net@48 611 > cls@16 396 > random 0]'
created_at: '2026-06-08T06:51:12.526391+00:00'
parents:
- hidden-forest-3847
- mute-cloud-4824
summary: 'DELIVERED (S2 first instance). Regularized Bradley-Terry Elo ladder on 4^3, 7 agents, bootstrap CIs, random=0. Headline: the net''s win over classical is BUDGET-BOUNDED on an anchored scale — net beats classical at 48 sims but cls@128 (849 Elo) beats net@128 (656) 27/30 and edges net@256 (784); classical''s sim-scaling is steeper on 4^3. Quantifies the S1 gap PROOF-2 must close. Fixed two methodology bugs (argmax degeneracy, BT divergence). $0/local.'
origin:
  backend: flywheel
  node_id: 3ac354fd-ff3a-5e3a-be95-876b6c503d40
  slug: empty-lab-3357
  revision: 3
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 04344acf-a728-591f-82e5-71dddfaca352
  slug: patient-shadow-0718
  revision: 0
  pushed_at: '2026-08-08T10:03:07+00:00'
  content_sha256: 58769ade3c2716d909f492a99d7f4d8ca1c4c561383753ff2ba7d722a432f98f
---
# PROOF-1 — anchored Elo ladder [first instance DELIVERED on 4^3]

Bradley-Terry/Elo rating ladder over a fixed cast, random pinned to 0, bootstrap
95%% CIs. Harness `neural/ladder.py` (regularized BT fit, per-game CPU sharding
across 14 cores). This is the first concrete instance of Success-bar-v2 **S2**
(an anchored rating with CIs) and the measurement backbone for S1/S5.

## Ratings — 4^3, G=30/pair, net = 64x6 champion (best_distill_big_4cubed.pt)
| rank | agent | Elo | 95%% CI |
|---|---|---|---|
| 1 | cls@128 | **849** | [789, 920] |
| 2 | net@256 | 784 | [736, 848] |
| 3 | net@128 | 656 | [611, 716] |
| 4 | cls@48 | 638 | [592, 689] |
| 5 | net@48 | 611 | [569, 659] |
| 6 | cls@16 | 396 | [365, 430] |
| 7 | random | 0 | anchor |

## Findings (decision-relevant)
- **The net's win over classical is budget-bounded — now on one anchored scale (S1).**
  Matched-budget head-to-heads: net@48 beat cls@48 17/27 (~0.63, consistent with
  the PASS-6 0.612 headline [b71da32b]); but cls@128 beat net@128 **27/30 (~0.90)**.
- **Classical's sim-scaling is STEEPER than the net's on 4^3**: classical +211 Elo
  over 16->128 sims vs the net +45 over 48->128. Random rollouts to terminal give
  cheap well-calibrated value on a tiny board; the net's value head doesn't keep
  pace as search deepens. This is exactly why S1 (budget dominance) is still open
  and quantifies the gap PROOF-2 must close: cls@128 (849) is ~65 Elo above
  net@256 (784).
- Both curves monotonic (net 611->656->784; classical 396->638->849) — the ladder
  is internally consistent.

## Methodology lessons (the FIRST run was broken; fixes recorded)
1. **Pure-argmax play => degenerate ladder.** Deterministic net-vs-net games gave
   40/40 / 0/40 results and an intransitive cycle. Fix: sample opening plies
   (temp=1 + Dirichlet root noise, first 6 moves), argmax after.
2. **Bradley-Terry diverges on perfect separation** (random won 0/180 -> all Elo
   pinned at the +/-4800 clamp). Fix: weak symmetric prior (reg virtual wins/pair);
   verified sane ordering at reg in {0.5,1,2}.
3. **Process-pool eval must pin threads** (14 workers x 32 intra-op threads stalled
   the box): torch.set_num_threads(1)+OMP=1; and a CUDA-initialized parent can't
   fork() workers -> use spawn.

## Status / next
- DELIVERED: a working, regularized, CI'd ladder on 4^3 (S2, first instance).
- Cheap follow-ups (now that INFRA-2 made big-board eval ~2-3.5x cheaper): add
  cls@256/512 + net@512 to map the full S1 crossover (-> PROOF-2 `75615ad2`); run
  the ladder on 5^3/7^3 for cross-board S2. Artifacts: ladder_4cubed.json,
  ladder_4cubed_summary.md. $0/local. Stop reason: objective_met (first ladder).