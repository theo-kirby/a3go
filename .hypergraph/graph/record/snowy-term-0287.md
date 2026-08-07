---
node_id: 6148c5c0-0a22-5e1e-96c9-5212982fda2e
slug: snowy-term-0287
title: Research agenda & frontier (LIVING)
created_at: '2026-06-07T12:52:28.077844+00:00'
parents:
- purple-fog-6345
summary: 'Living frontier. PHASE 3: 9 nodes delivered (INFRA-1/2/3, PROOF-1/2/3, ALGO-1, TOOL-1/2). Engine 3.5x; net win budget-bounded on 4^3 but search scaling amplifies w/ board size (7^3 saturates); exact small-board truth + memo-unsound; Gumbel no-win 4^3; AZ anchored-gate validated (no robust 4^3 gain). Viz+play tooling built. Next: INFRA-3 on 5^3 (S5 retry), ALGO-2, SCALE, SCIENCE. Living frontier. PHASE 3 EXECUTING. PASS-13 delivered 6 frontier nodes (INFRA-1/2, PROOF-1/2/3, ALGO-1). Ignition list complete. Key results'
flywheel:
  node_id: 6148c5c0-0a22-5e1e-96c9-5212982fda2e
  slug: snowy-term-0287
  revision: 16
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 0955bb9e96a3bf63f1320d3904e6c6d83bdfc6e9368ec1106dda42cf034b9835
---
**P16 (frontier EXPANSION — seeding, not executed):** widened the Phase-3 frontier with **17 STAGED direction nodes** mined from **KataGo / autogo / online-go** — aux ownership/score/soft-policy heads, search Elo levers (optimistic policy, value-bias correction, variance-cPUCT), size-agnostic global-pooling + nested-bottleneck architecture, richer input planes (ko-ban for ubiquitous-3D-ko `31dae43b`), SPRT gate + n≥128 re-power audit, superko-aware exact solver (past PROOF-3's 2×2×2), train×test scaling-law surface, 3D game-review UI — under a new **EXPANSION index** `f9f2bf74-2ce6-5488-b471-dc0b6c422b99` + `docs/DIRECTIONS.md`. Recommended order: **aux targets first** (hit the komi-flat `2a2ca6b9` + policy-weak `0bc38c41` scars), then input-planes/capacity, SPRT alongside everything. No experiments run; no `neural/` code touched. [refs: KataGo `365b153f-75e1-54ee-9344-4794604da3a4`, online-go `ba69d0a3-f344-5413-8b0f-e4d65aa947bc`, autogo `b4fd8252`]

**P13 final:** INFRA-3 AZ self-play RUN 1 (4^3) — externally-anchored gate VALIDATED live (correctly blocked drift candidates it3/it4); but no robust gain (0.652->0.667 vs classical@48, within noise) -> S5 redirected to 5^3/7^3 where there's headroom [8a724b1c]. TOOL-1 (viz.py + figures.py) & TOOL-2 (play.py) DELIVERED; benchmark figures attached across result nodes [1f59266a,742a0aab]. **SESSION: 9 Phase-3 nodes delivered. Open frontier: INFRA-3 on 5^3 (S5 retry); ALGO-2 arch/value-target; SCALE-1/2/3; SCIENCE-1/2; superko-aware exact solver (S3).**

**P13 cont:** ALGO-1 Gumbel IMPLEMENTED + A/B'd — honest negative on 4^3 (no clear win vs PUCT; behind at low sims, ~even at 32/64); Gumbel's premise (large action space) untested -> 7^3 follow-up [4cf07501]. Also: classical MCTS is IMPRACTICAL on 7^3 (rollout cost ~ board fill; a single net@256-vs-cls@64 game >250s) -> classical isn't a viable big-board baseline, redirecting S4 toward net self-improvement (INFRA-3). **Ignition list COMPLETE. Next marquee: INFRA-3 AZ self-play (S5, beat the teacher) — big build; ALGO-2 arch/value-target; SCALE/SCIENCE.**

**P13 cont (GPU freed by user):** PROOF-2 DELIVERED — test-time search scaling AMPLIFIES with board size (4^3 needs ~16x sims->0.90; 7^3 hits 1.00 by 512 sims); matches the cross-board value-calibration law -> the genuinely-3D 7^3 is where the net most likely dominates classical at all budgets [75615ad2]. PROOF-3 DELIVERED — exact ground truth for <=4-cell boards (2x2x1 fair komi +1); position-memoization PROVEN unsound for 3D Go; 2x2x2 is the exact-solving frontier (ko, not cell count) [22d59c45]. **Next: net-vs-classical on 7^3 at high sims (S4 headline — the missing measurement); INFRA-3 AZ self-play (S5); ALGO-1 Gumbel.**

**P13 cont:** PROOF-1 DELIVERED — anchored Elo ladder on 4^3 (cls@128 849 > net@256 784 > net@128 656 > cls@48 638 > net@48 611 > cls@16 396 > random 0); the net's win over classical is BUDGET-BOUNDED on one scale (S1 gap quantified) [3ac354fd]. INFRA-2 made the eval ~2-3.5x cheaper. **Next: ALGO-1 (Gumbel, cheap CPU) / PROOF-3 (solver) / PROOF-2 (extend ladder to cls@256/512 + 5^3/7^3 for the full crossover).**

**P13 (executing Phase 3):** INFRA-1 RESOLVED — premise falsified, the GPU was never the wall (batched forward 3-11%% of MCTS time; M5 BatchedMCTS already IS the GPU server; PASS-11 7^3 slowness was the CPU eval harness) [f6343208]. INFRA-2 RESOLVED — vectorized legal mask + Zobrist superko = **3.5x MCTS throughput on 7^3** (11.85s->3.14s profiled), validated 460/460 + 60/60 + npm 48/48 [14377685]. The real keystone was the ENGINE, not the GPU. 7^3@512 now ~53ms/move/game (was ~12min on CPU) -> S4/PROOF-2/PROOF-1/INFRA-3 all 2-3.5x cheaper. **Next: PROOF-1 (Elo ladder) — cheap now.**

**>> PHASE 3 OPENED (frontier re-expanded `e917c9e4-fe12-5f0a-8e0d-1965c906f5a6`).** The existence thesis is answered; Phase 3 raises the bar to a *provably strong* agent (dominate classical at ALL budgets, anchored Elo, near-optimal vs exact solve, decisive 7^3 win, beat the teacher). 14 staged direction nodes under the hub across Infra/Proof/Scale/Science/Algorithms; keystone enabler = GPU-batched MCTS server. See the hub for the status index + recommended ignition order. Awaiting human pick of start point.

**P11:** 7^3 characterized via C++ engine — clean cross-board SCALING LAW (value MSE 0.044->0.019->0.006; policy acc 0.12->0.07->0.05; sims 48->512->>>512) [0bc38c41]. Strength on big boards is now SIM-BOUND -> next bottleneck is GPU-batched MCTS.

# Research agenda & frontier (LIVING)

**Entry point for autonomous continuation.** Read latest `[control]` -> read this -> pick highest value-per-cost branch whose preconditions hold -> run + commit empirical node w/ artifacts -> update this node.

## Open frontier (prioritized; updated after Pass 6 — SUCCESS BAR MET on 4^3)
| # | direction | node | cost | value | status |
|---|---|---|---|---|---|
| 1 | **Apply the winning recipe to 5^3** — distill classical 5^3 MCTS into a (bigger) net; on 5^3 random rollouts are weaker so neural value should win MORE easily than on 4^3. Self-play was volume-gated [5d318812]; distillation may not be. | Q2/Q10 | med-high ($0, slow classical) | high | OPEN — best next |
| 2 | **C++ engine + MCTS + leaf-parallelism (autogo)** — beyond Python ceiling; unlocks 5^3/7^3 classical-data-gen (the 256-playout wall) + bigger nets | Q2 | high (build) | high | OPEN [b4fd8252] |
| 3 | Re-characterize test-time scaling with the GOOD 64x6 net (does a calibrated net now scale with sims?) | Q10 | low | med | OPEN |
| 4 | Push 4^3 further: even stronger teacher (256-playout via C++) / bigger net -> how far above classical? | Q10 | med | med | OPEN |
| 5 | Q8 positional value corner/edge/face/interior | Q8 | med | med | OPEN |
| 6 | Seki frequency + minimal 3D seki volume | Q6 | med | med | OPEN |
| 7 | Snapback tail (~2% single-captures not ko) | Q7 | low | low-med | OPEN |

## Resolved
**P1:** success bar leg-1 (classical MCTS beats random); ladders break; two-eye life; komi degenerate-3^3; 4^3 sweet spot; 3^3~=2D; parallel ~28x.
**P2:** toolchain+GPU; engine 60/60; AZ pipeline; gating+buffer; M4 plateau (volume=wall).
**P3:** M5 batched self-play 22x [dark-poetry-2083]; Q10 rising self-play strength [c16643ba]; Q9 komi ~0.5 [9a106027]; Q6 seki [5f10c19e].
**P4:** net loses to classical 0.085 [a0e8a3f6]; 5^3 tractable but volume-gated [5d318812].
**P5 (autogo):** distillation = best lever 0.085->0.333 [4c377ef1]; self-play degrades vs-classical, anchor the gate [4d8fb650]; autogo ref [b4fd8252].
**P10:** **C++ engine + self-play generator built — 60/60 cross-validated, ~60x faster (4^3)/~7x (5^3)** [cff3a5d1]; bigger-board data-gen wall REMOVED (C++ classical teacher needs minor strength tuning).
**P9:** fast playout (9x, additive play_fast, crossval 60/60); **distillation recipe TRANSFERS to 5^3 — parity with classical, 0.19->0.50 as sims 48->512; MCTS budget scales with board size** [e7c35c64].
**P7-8:** scaling re-characterized (good net scales) [28f66847]; 5^3 pilot gated on data-gen [c4091781]; Q8 no opening preference [853d7c2c].
**P6 (BEAT CLASSICAL):** test-time scaling no free lunch [9605fb9a]; stronger-teacher distillation -> parity 0.458 [f490a174]; **bigger net (64x6) BEATS classical 0.612 [0.533,0.686] -> SUCCESS BAR MET** [b71da32b].

## Standing rules
Budget $0/local unless changed; report (don't spend) for managed compute. To beat a strong search baseline w/o expert data: DISTILL it, then scale teacher-strength + net capacity. Anchor strength to a non-self baseline (classical), and the promotion gate too. Capacity fixes a value head that deeper search amplifies. Right-size expensive collection (256-playout classical = ~30min/game). Close a question -> add the next here.