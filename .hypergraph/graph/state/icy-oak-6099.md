---
node_id: e4224f5a-fd88-5de9-b821-2bf9561f6e90
slug: icy-oak-6099
title: Strength program (success bar)
created_at: '2026-08-07T20:34:44+00:00'
parents:
- royal-comet-4977
summary: 'v1 cleared on 4^3 (0.612 vs classical); v2 gate unmet: S4 (7^3 decisive win) never attempted, S5 unmet everywhere, S3 stuck at 4 cells, 5^3 just below parity.'
flywheel:
  node_id: 71064143-ff3b-5efa-a567-53e6db82e819
  slug: morning-wood-2636
  revision: 0
  pushed_at: '2026-08-07T20:39:47+00:00'
  content_sha256: 20bb17d8ee1df9c49b60df684ddd6089e2fc49dc8fc52a5ca5784295dda9fa1f
---
Status: open

## Current

- Success bar v1 CLEARED on 4³: MCTS beats uniform-random 100%/98% (3³/4³) [rec: silent-dew-2840]; the 64×6 net beats classical 0.612 [0.533,0.686] at equal 48v48, n=160 [rec: soft-waterfall-3492]; rising self-play strength shown [rec: still-dream-7550].
- Gap: success bar v2 (S1–S5) is the live bar [rec: jolly-breeze-8643] and is NOT met as a compound. S2 delivered (anchored Elo ladder) [rec: empty-lab-3357]. S1 half-delivered: the test-time half exists [rec: rapid-hat-7732] but budget dominance fails — cls@128 beats net@128 ~0.90 and sits ~65 Elo above net@256 on 4³ [rec: empty-lab-3357].
- Gap: S3 (near-optimal on solved boards) is stuck at ≤4-cell degenerate boards pending the superko-aware exact solver (EVAL-2, staged) [rec: shrill-moon-6110] [rec: soft-thunder-1632].
- Gap: S4 (decisive win on the genuinely-3D board) was never attempted — the highest-value open measurement. PROOF-2 shows 7³ is the most favorable board (search scaling amplifies there; net@512 = 60/60 vs its low-sim self) and INFRA-1's falsification removed the stated blocker, yet net-vs-classical at high sims on 7³ has never been run [rec: rapid-hat-7732] [rec: broken-tree-4527].
- Gap: S5 (escape the teacher ceiling) unmet at every scale: 4³ within anchor noise (0.652→0.667, N=24) [rec: billowing-dew-3640]; 5³ relative-yes (beats frozen seed 0.735) but absolute-no (identical to seed vs classical) [rec: billowing-dew-3640]; the classical-anchored gate variant promoted on an n=32 fluctuation that vanished at n=128 [rec: rough-paper-7328].
- The 5³ ceiling: best net (libs@64×6) is 0.449 [0.400,0.499] vs classical — one hair from parity [rec: polished-field-7944]; the distilled net's "parity@512" was an n=32 artifact, re-measured at 0.414 [0.332,0.501] [rec: rough-paper-7328]; SPRT confirms sub-parity [rec: dawn-pond-0204]. The control node's diagnosis: the cheap unblock at 5³ is more games per A/B, not new levers [rec: shiny-term-3012].

## Negative knowledge

- [scope: more plain frozen-net self-play for absolute strength on this stack | confidence: high | evidence: rough-paper-7328, billowing-dew-3640] Self-play does not lift absolute 5³ strength: relative gains over the seed (0.735) do not translate against classical (statistically identical before/after), and both gate variants are exhausted — the remaining levers are signal richness and capacity, not more search or self-play.

## Provenance

- lively-orchard-3365 — adoption distillation
- silent-dew-2840 — success bar v1 leg 1 cleared
- soft-waterfall-3492 — net beats classical 0.612 on 4³
- still-dream-7550 — rising self-play strength on 4³
- jolly-breeze-8643 — success bar v2 S1–S5 definition (GATE)
- empty-lab-3357 — S2 delivered; S1 budget-dominance gap quantified
- rapid-hat-7732 — S1 test-time half; 7³ named the favorable board
- broken-tree-4527 — S4 blocker premise falsified
- shrill-moon-6110 — S3 bounded at 4 cells
- billowing-dew-3640 — S5 runs 1–2 split verdict
- rough-paper-7328 — S5 run 3 artifact; parity headline re-powered
- polished-field-7944 — 5³ ceiling 0.449
- dawn-pond-0204 — SPRT sub-parity confirmation
- shiny-term-3012 — control-node diagnosis: more games per A/B
