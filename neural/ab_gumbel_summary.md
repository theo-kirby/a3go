# ALGO-1 — Gumbel AlphaZero vs PUCT (A/B), 4³

Faithful Gumbel AlphaZero root selection (Gumbel-top-k without replacement +
Sequential Halving, PUCT inside the tree), `neural/gumbel_az.py`. A/B harness
`neural/ab_gumbel.py`, per-game CPU sharding, net on GPU, 40 games/matchup,
`max_considered` tuned to the sim budget. Net = 64×6 champion. Raw: `ab_gumbel_4cubed.json`.

## Results (win-rate of the Gumbel side)
| matchup | Gumbel win-rate | 95% CI |
|---|---|---|
| gumbel@8 vs puct@8 | 0.378 | [0.24, 0.54] |
| gumbel@16 vs puct@16 | 0.359 | [0.23, 0.52] |
| gumbel@32 vs puct@32 | 0.556 | [0.40, 0.71] |
| gumbel@64 vs puct@64 | 0.538 | [0.39, 0.68] |
| gumbel@16 vs puct@32 | 0.462 | [0.32, 0.61] |

## Finding (honest negative / inconclusive on 4³)
- **No clear strength-per-sim win over PUCT on 4³.** Matched-sim: Gumbel is behind
  at very low budgets (8, 16) and roughly even/slightly ahead at 32/64. CIs straddle
  0.5 at the higher budgets.
- The one suggestive point: gumbel@16 ≈ puct@32 (0.46, CI includes 0.5) hints at
  ~2× sim-efficiency there, but it is not robust.
- **Likely reason:** Gumbel's advantage is designed for *large action spaces* and
  *weak/low-sim policies*. 4³ has only 65 actions and a strong distilled policy, so
  PUCT is already near-optimal and there is little room for Gumbel's exploration-
  without-replacement to help. At very low sims (8) with the considered set tuned
  down (max_considered≈2), Sequential Halving has almost no rounds.

## Verdict & follow-up
The implementation is correct and runs, but Gumbel does not pay off on 4³. Its
premise is strongest on **large action spaces** — the natural fair test is 7³
(344 actions) at low sims, where PUCT's prior is weaker and Sequential Halving has
room to work. Recorded so the lever isn't re-tried blindly on small boards; whether
to adopt Gumbel for INFRA-3 self-play should be decided by the 7³ test, not this one.
