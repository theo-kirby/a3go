---
node_id: e917c9e4-fe12-5f0a-8e0d-1965c906f5a6
slug: mute-cloud-4824
title: Phase 3 — Toward a provably strong 3D-Go agent (frontier map, LIVING)
created_at: '2026-06-08T06:47:46.330488+00:00'
parents:
- purple-fog-6345
- shiny-term-3012
summary: 'New chapter: raise the bar from ''a strong agent CAN exist'' (proven on 4^3/5^3) to ''a strong agent that DOMINATES at all budgets, on genuinely-3D boards, and is PROVEN via an anchored rating ladder + exact-solve checks''. Organizes the Phase-3 frontier into Bar / Infra / Proof / Scale / 3D-science / Algorithms. Keystone enabler = GPU-batched MCTS server. $0/local.'
flywheel:
  node_id: e917c9e4-fe12-5f0a-8e0d-1965c906f5a6
  slug: mute-cloud-4824
  revision: 2
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 59bad44ea657ef7836b1c1672f1ee3b85c22a3ed3e8bc4272d18989a4212504b
---
# Phase 3 — Toward a *provably strong* 3D-Go agent (frontier map, LIVING)

**This opens a new chapter.** Phases 1-2 (passes 1-11) answered the existence thesis: a strong 3D-Go agent *can* be trained — distill the classical random-rollout MCTS teacher, scale net capacity, and scale cheap search with board size. We beat classical on 4^3 (0.61), reached parity on 5^3 (@512 sims), and characterized a clean cross-board scaling law (value easier, policy harder, sims grow) up to 7^3. See control `62ab093f`, agenda `6148c5c0`, methodology `dcd0a5db`.

**Phase 3 raises the bar from *exists* to *strong + proven*.** Two gaps remain:
1. **Strength is still bounded** — on 4^3 the net only beats classical at *matched/low* budget; classical@128 still wins. We have never produced an agent that dominates at *all* budgets, on a *genuinely 3D* board, or that escapes the classical teacher's ceiling.
2. **The proof is thin** — "beats classical 0.61" is one comparison. A *strong* claim needs an anchored rating ladder, a near-optimal check against exactly-solved boards, and a decisive big-board win.

The bottleneck has shifted from *data-gen* (solved by the C++ engine `cff3a5d1`) to **high-sim neural play/eval throughput on big boards** — which is why the GPU-batched MCTS server is the keystone enabler.

## How the frontier is organized (children of this node)
- **Bar:** Success bar v2 — the operational definition of "strong + provable".
- **Infra (enablers):** GPU-batched MCTS server · incremental engine · full AZ self-play at scale.
- **Proof:** anchored Elo ladder · beat-classical-at-all-budgets · exact small-board solve.
- **Scale & generalization:** 9^3 + non-cube · size-agnostic net · curriculum transfer.
- **3D science:** opening theory / value-of-center · life-&-death & tactics at scale.
- **Algorithms:** Gumbel AlphaZero · architecture & value-target scaling.

## How to use this map
Each child is a STAGED plan node: objective, why-it-matters, implementation route(s), decision criterion, preconditions, cost/value, expected artifacts. They are scaffolding for a human go/continue decision — none are executed yet. Pick the highest value-per-cost branch whose preconditions hold; the **GPU-batched MCTS server** unblocks most of the strength/scale work, so it is the natural first keystone. Budget remains **$0/local** unless explicitly changed.

## Status index (children — all STAGED, none executed; pick a start point)
| theme | node | id | cost | depends on |
|---|---|---|---|---|
| **Bar** | Success bar v2 [GATE] | `fdb07ec9-ee87-55bf-997c-b30c1c5998ca` | — | — |
| Infra | INFRA-1 GPU-batched MCTS server **(keystone)** | `f6343208-8fd7-5f07-b265-e88f7f653c1b` | high | — |
| Infra | INFRA-2 incremental engine (union-find + Zobrist) | `14377685-99ff-581d-8208-e4d8519b2b28` | med | — |
| Infra | INFRA-3 full AZ self-play (escape teacher) | `8a724b1c-c666-5571-87fc-e078c55a0223` | high | INFRA-1 |
| Proof | PROOF-1 anchored Elo/Glicko ladder | `3ac354fd-ff3a-5e3a-be95-876b6c503d40` | med | — |
| Proof | PROOF-2 beat classical at ALL budgets | `75615ad2-12eb-5d2d-9a05-890c011c7f86` | high | INFRA-1 |
| Proof | PROOF-3 exact-solve small boards | `22d59c45-09a2-5524-9943-b2687e52cb94` | med | — |
| Scale | SCALE-1 9^3 + non-cube boards | `884663c8-410f-55d3-9122-1f493ac9b419` | med-high | INFRA-1/2 |
| Scale | SCALE-2 size-agnostic single net | `1e58a424-54f6-5dfa-bf50-75d842f7dcda` | med | — |
| Scale | SCALE-3 curriculum small->big | `adb11193-0501-5e63-98a6-101ea8bc591e` | med | SCALE-2 |
| Science | SCIENCE-1 3D opening theory / center value | `5e34766d-c790-54a6-a98c-29b2fdbf7bbb` | med | strong net |
| Science | SCIENCE-2 3D life&death & tactics at scale | `777d5c9e-70ce-588f-98e2-4f2a80dfebb6` | med | (solver half: none) |
| Algo | ALGO-1 Gumbel AlphaZero (low-sim) | `4cf07501-9a4f-5aad-adf7-21c04d6d3709` | med-high | — |
| Algo | ALGO-2 architecture & value-target scaling | `792c4ec2-6cc6-51eb-a115-f44fe5dc0ff9` | med | — |
| **Expansion** | **EXPANSION index — KataGo/autogo/online-go branches (17 STAGED)** [LIVING] | `f9f2bf74-2ce6-5488-b471-dc0b6c422b99` | — | hub |

**PASS-16 — frontier widened.** The frontier was expanded with **17 KataGo/autogo/online-go-inspired STAGED branches** (auxiliary ownership/score/soft-policy heads, search Elo levers, size-agnostic + nested-bottleneck architecture, richer input planes, SPRT gate + superko-aware solver, train×test scaling-law, 3D review UI). The campaign's evidence (PASS-15 `b3ea0b95`) says the S1/S5 lever is signal richness + capacity, not more search/self-play; KataGo sharpens this into an explicit order. See the EXPANSION index `f9f2bf74-2ce6-5488-b471-dc0b6c422b99` and the human-readable companion `docs/DIRECTIONS.md`.


**Recommended ignition order:** Success-bar-v2 (read first) -> **INFRA-1** (keystone, unblocks S4/PROOF-2/INFRA-3/SCALE) in parallel with the cheap-now wins **PROOF-1** (ladder), **PROOF-3** (solver), **ALGO-1** (Gumbel) and **INFRA-2** (engine) which need no new infra. Then INFRA-3 (beat the teacher) + the scale/science tracks once the server lands.

