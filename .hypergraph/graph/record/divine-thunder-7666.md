---
node_id: 4cf07501-9a4f-5aad-adf7-21c04d6d3709
slug: divine-thunder-7666
title: ALGO-1 — Gumbel AlphaZero [IMPLEMENTED; honest negative on 4^3 — no clear win vs PUCT; fair test is 7^3 large action space]
created_at: '2026-06-08T06:51:18.352210+00:00'
parents:
- lively-meadow-0948
- mute-cloud-4824
summary: 'IMPLEMENTED + A/B''d. Faithful Gumbel (top-k + Sequential Halving). On 4^3 vs PUCT: behind at very low sims (8/16 -> 0.36-0.38), ~even at 32/64 (0.54-0.56); gumbel@16~puct@32 within noise. No clear strength-per-sim win — expected, since Gumbel targets large action spaces/weak policies and 4^3 (65 actions, strong distilled net) is the wrong regime. Correct impl; fair test = 7^3 (344 actions). Recorded to avoid re-trying on small boards. $0/local.'
origin:
  backend: flywheel
  node_id: 4cf07501-9a4f-5aad-adf7-21c04d6d3709
  slug: divine-thunder-7666
  revision: 3
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 39ab8668-01f8-5940-b0c8-46353befbee5
  slug: broken-lab-7631
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: 842972d8135e459723f7b3f24bdef3525491b757b8ffb70e9cbb83de22c28678
---
# ALGO-1 — Gumbel AlphaZero [IMPLEMENTED; honest negative on 4^3]

Faithful Gumbel AlphaZero root selection (Gumbel-top-k without replacement +
Sequential Halving; PUCT inside the tree) in `neural/gumbel_az.py`; A/B vs PUCT in
`neural/ab_gumbel.py` (per-game sharding, net on GPU, 40 games/matchup, max_considered
tuned to the sim budget).

## A/B results (win-rate of the Gumbel side, 4^3, 64x6 champion net)
| matchup | Gumbel WR | 95% CI |
|---|---|---|
| @8 vs @8 | 0.378 | [.24,.54] |
| @16 vs @16 | 0.359 | [.23,.52] |
| @32 vs @32 | 0.556 | [.40,.71] |
| @64 vs @64 | 0.538 | [.39,.68] |
| @16 vs @32 | 0.462 | [.32,.61] |

## Finding (honest negative on 4^3)
- **No clear strength-per-sim advantage over PUCT on 4^3:** behind at very low sims
  (8/16), ~even at 32/64. gumbel@16~puct@32 (CI includes 0.5) hints at ~2x efficiency
  but isn't robust.
- **Why:** Gumbel's edge targets LARGE action spaces / weak low-sim policies. 4^3 has
  only 65 actions and a strong distilled policy where PUCT is already near-optimal; at
  sims=8 Sequential Halving barely runs.
- **Implementation is correct** (validated: works, varies via Gumbel noise, gumbel@high
  ~ puct@high). The premise is just not exercised on small boards.

## Verdict / follow-up
Don't adopt Gumbel for small-board work. Its fair test is **7^3 (344 actions) at low
sims**, where PUCT's prior is weaker and Sequential Halving has room — that test should
gate whether INFRA-3 self-play uses Gumbel. Recorded to avoid re-trying the lever
blindly on small boards. Artifacts: ab_gumbel_4cubed.json, ab_gumbel_summary.md.
$0/local. Stop reason: objective_met (implemented + fairly tested; negative-on-4^3 with a clear next test).