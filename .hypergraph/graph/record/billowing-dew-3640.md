---
node_id: 8a724b1c-c666-5571-87fc-e078c55a0223
slug: billowing-dew-3640
title: 'INFRA-3 — AZ self-play to beat the teacher (S5) [RUN 1: 4^3 validated gate; RUN 2: 5^3 relative-S5 met but does NOT translate to beating classical]'
created_at: '2026-06-08T06:51:11.686379+00:00'
parents:
- soft-waterfall-3492
- lively-meadow-0948
- mute-cloud-4824
summary: 'RUN 1 (4^3): anchored gate validated live (blocks drift) but no robust gain. RUN 2 (5^3, frozen-distilled-champion anchor): SPLIT VERDICT — self-play champion beats its own distilled seed 0.735 net-vs-net (relative S5 met, CI-lo~0.64) BUT is statistically identical to the seed vs classical (0.219@48, 0.50@512 — unchanged) → the relative gain does NOT translate to absolute strength vs the OOD baseline. Methodology: net-vs-net self-improvement overstates strength vs classical. $0/local.'
flywheel:
  node_id: 8a724b1c-c666-5571-87fc-e078c55a0223
  slug: billowing-dew-3640
  revision: 4
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: bde6f881e0b0945fb0d312ba5b1bc32190b3e9a16fd77ace4fba5fe660d6d1f0
---
# INFRA-3 — AZ self-play to beat the teacher (S5) [RUN 1: 4³ · RUN 2: 5³]

Net-guided self-play (M5 batched, GPU) → train candidate → **externally-anchored
gate** → promote only if the candidate does not regress against a fixed anchor AND
beats the current best head-to-head. Seeded from the distilled champion.
`neural/az_selfplay.py` (run 1), `neural/az_selfplay_frozen.py` (run 2).

## RUN 1 (4³) — anchored gate VALIDATED; no robust strength gain
- Seed champion vs classical@48 = **0.652**; final = **0.667** (one promotion @it7).
  Gain within N=24 anchor noise (SE~0.1) → S5 NOT cleanly met on 4³.
- **The anchored gate works (validated live).** At iters 3–4 the candidate beat the
  best NET-VS-NET (0.71, 0.73) but would have REGRESSED vs classical (0.57, 0.58 <
  0.652) → the gate correctly refused to promote — the Pass-5 self-play-drift trap
  (within-population win, absolute-strength loss) caught and blocked in a live loop.
- Why 4³ is the wrong board: classical is STRONGEST there (PROOF-1 [3ac354fd]) and
  the distilled champion is near the small-board ceiling, so self-play has almost no
  headroom. PROOF-2 [75615ad2] → the net's strength scales steeply with search on
  5³/7³ → that is where S5 should be attempted.
- Artifacts: az_selfplay_4cubed.json, az_selfplay_summary.md, infra3_az_selfplay_4cubed.png; checkpoint best_az_4cubed.pt.

## RUN 2 (5³) — frozen-distilled-champion anchor [the S5 retry]
**Design fix.** Per-iter classical eval is too slow on 5³ (~15–25 min). The gate is
instead anchored to the **FROZEN distilled champion** the run was seeded from
(net-vs-net, GPU-cheap, drift-free because the reference never moves — the Pass-5
drift came from anchoring to the MOVING best). Gate: promote iff
cand_vs_best ≥ 0.55 AND cand_vs_ref ≥ best_vs_ref − 1/EVAL. Seed
`best_distill5strong_5cubed.pt` (64×6, the 5³ net at parity with classical
[e7c35c64]); 48 sims, 80 games/iter, EVAL=80. `az_frozen_5cubed.json`.

### Result — split verdict: relative S5 YES, absolute S5 NO
- **Relative (beats its own distilled seed): MET.** 2 promotions (it1, it2) then a
  plateau; the run stopped after 4 of a planned 8 iters. Final champion
  (`best_az_frozen_5cubed.pt`, the it2 net) beats the frozen distilled seed
  **0.735 over 80 games** (it2 cand_vs_ref) → 95% CI lower ≈ 0.64 > 0.5. This is the
  first clean net-vs-net self-improvement-beyond-distillation signal — absent on 4³.
  Per-iter: it1 0.700→promote, it2 0.735→promote, it3 0.667→keep, it4 0.457→keep.
- **Absolute (the classical "teacher" translation): NOT MET — the gain did not
  translate.** Measured the final champion vs classical at the seed's two matched
  points (`net_vs_classical_mp.py`, 32 color-balanced games each, A3GO_CH=64 BLK=6):

  | sims | seed (distilled champ) | self-play champion |
  |---|---|---|
  | net@48 vs cls@48 | 0.194 [0.092, 0.363] | **0.219 [0.11, 0.388]** |
  | net@512 vs cls@48 | 0.50 [0.336, 0.664] | **0.50 [0.332, 0.668]** (2 draws) |

  Despite a decisive 0.735 net-vs-net win over its own seed, the champion is
  statistically **identical to the seed against classical** — still parity at 512,
  still losing at 48. The relative improvement is real but opponent-specific.

### Interpretation (methodology)
A frozen, drift-proof anchor prevents the gate from being fooled by a *moving*
reference, but it does NOT make net-vs-net a valid proxy for absolute strength: the
self-play family shares systematic blind spots that the out-of-distribution
classical baseline (random rollouts, different style) exploits identically before
and after. **Net-vs-net self-improvement overstates strength vs an OOD baseline; the
absolute claim must be measured against the OOD opponent, not inferred from the
in-family gate.** S5 on 5³ via plain self-play is therefore inconclusive-to-negative
in absolute terms — closing the gap likely needs the gate's promotion signal to
include the classical baseline (hybrid anchor) and/or more capacity/search, not just
more self-play iterations against a frozen net.

**Reproduce:** `cd neural && uv run python az_selfplay_frozen.py 5 8 80 48` (seed
defaults to best_distill5strong_5cubed.pt); translation
`A3GO_CH=64 A3GO_BLK=6 uv run python net_vs_classical_mp.py best_az_frozen_5cubed.pt 5 32 {48,512} 48 50 <out>`.
$0/local, RTX 5090 free. Artifacts: az_frozen_5cubed.json,
experiments_azfrozen5_vs_cls_s48.json, experiments_azfrozen5_vs_cls_s512.json;
checkpoint best_az_frozen_5cubed.pt.

**Stop reason: `objective_met`** for the probe (the question is answered: relative
self-improvement yes, absolute translation no). Next frontier = hybrid
classical-anchored self-play on 5³ (gate on cand_vs_classical, not cand_vs_frozen-net)
to test whether optimizing the right objective lifts absolute strength — staged as
the graph-local continuation.
