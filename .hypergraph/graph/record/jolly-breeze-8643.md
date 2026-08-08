---
node_id: fdb07ec9-ee87-55bf-997c-b30c1c5998ca
slug: jolly-breeze-8643
title: Success bar v2 — what 'strong & provable' means for a 3D-Go agent [GATE]
created_at: '2026-06-08T06:51:08.915547+00:00'
parents:
- mute-cloud-4824
summary: 'Operational definition of the Phase-3 target. Five criteria S1-S5: (S1) dominate classical at ALL search budgets, not just matched; (S2) anchored Elo ladder with the net''s gap over strongest classical reported in rating points; (S3) near-optimal vs exactly-solved small boards; (S4) decisive win on genuinely-3D 7^3; (S5) self-play that escapes the classical-teacher ceiling. Current status: only a weak form of S1 met (4^3 matched-budget).'
origin:
  backend: flywheel
  node_id: fdb07ec9-ee87-55bf-997c-b30c1c5998ca
  slug: jolly-breeze-8643
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: c429fe41-8c0b-53f7-bbbe-bf5d7eca8bb2
  slug: crimson-voice-8429
  revision: 0
  pushed_at: '2026-08-08T10:01:49+00:00'
  content_sha256: 407031e3a494d1cbb40f81d246ac28e0a7e87865c16fec03bd83cd6f94cdb32b
---
# Success bar v2 — 'strong AND provable' [GATE node]

Phase-2's bar ("beats uniform-random AND a fixed classical MCTS, plus rising self-play strength") was an *existence* bar and is **met** on 4^3 [b71da32b]. To claim a *strong* agent and *prove* it, Phase 3 adopts this stricter, multi-pronged bar. These are the acceptance targets the other Phase-3 nodes are designed to hit.

## Criteria
- **S1 — Budget dominance.** The net beats classical MCTS at *every* search budget, not just matched/low. Concretely: plot win-rate vs sims for net and for classical; the net's curve sits at/above 0.5 across the whole sweep (today it dips below as classical@128 > net on 4^3 [a0e8a3f6, 28f66847]). *Owner: PROVE-BUDGET.*
- **S2 — Anchored rating.** A calibrated Elo/Glicko ladder over a fixed cast {random, classical@{16,48,128,512}, net generations}. Report the champion net's rating gap over the strongest classical with a CI. Gives one comparable, absolute strength number. *Owner: PROVE-ELO.*
- **S3 — Near-optimal on solved boards.** On exactly-solved small boards (3^3, possibly thin slabs / small N), the agent matches the game-theoretic optimal move in >=X% of solved positions and never loses a theoretically-won game. Distance-from-perfect, not just relative wins. *Owner: PROVE-SOLVE.*
- **S4 — Genuinely-3D decisive win.** A win with CI-lower > 0.5 against classical on **7^3** (where 6-connectivity actually bites) at an *affordable* sim budget — currently sim-bound on CPU [0bc38c41]. *Owner: INF1 (server) + SCALE-9.*
- **S5 — Escape the teacher ceiling.** An AZ self-play loop (externally anchored gate) that produces a net **stronger than the classical teacher it distilled from** — distillation alone is capped at the teacher's quality. *Owner: INF-AZ.*

## Current status (2026-06)
| | criterion | status |
|---|---|---|
| S1 | budget dominance | ❌ only matched-budget win on 4^3 |
| S2 | anchored Elo ladder | ❌ not built |
| S3 | near-optimal vs solved | ❌ no solver / no exact baseline |
| S4 | 7^3 decisive win | ❌ sim-bound on CPU |
| S5 | beat the teacher | ❌ distillation-only so far |

**"Strong & proven" = S1+S2 met on 4^3/5^3 AND (S3 or S4) met AND S5 demonstrated at least once.** Revisit/relax explicitly if a criterion proves intractable at $0/local; record the relaxation here.
