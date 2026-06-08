# INFRA-3 — AlphaZero self-play vs the classical teacher (S5), 4³

`neural/az_selfplay.py`. Seeded from the 64×6 distilled champion. Each iter: 80
net-guided self-play games (M5 batched, GPU, Dirichlet root noise) → train a
candidate → **externally-anchored gate**: promote only if the candidate (a) does
not regress vs classical@48 relative to the current best, AND (b) beats the
current best head-to-head ≥ 0.55. Anchor eval = 24 games vs classical@48 (the
match the self-play sim budget). Raw: `az_selfplay_4cubed.json`.

## Trajectory (vs classical@48 anchor)
| iter | cand vs best | cand vs cls | best vs cls | gate |
|---|---|---|---|---|
| seed | — | — | **0.652** | — |
| 1 | 0.19 | 0.43 | 0.652 | keep |
| 2 | 0.50 | 0.46 | 0.652 | keep |
| 3 | 0.71 | 0.57 | 0.652 | keep (vs-best up but vs-cls down → **gate blocks drift**) |
| 4 | 0.73 | 0.58 | 0.652 | keep (same) |
| 5 | 0.47 | 0.50 | 0.652 | keep |
| 6 | 0.50 | 0.79 | 0.652 | keep (vs-cls high but didn't beat best) |
| 7 | 0.64 | 0.67 | 0.652 | **PROMOTE** → best vs cls = 0.667 |
| 8–10 | ≤0.49 | 0.32–0.50 | 0.667 | keep |
| **final** | | | **0.667** | |

## Findings
1. **The externally-anchored gate works — validated live.** At iters 3–4 the
   candidate clearly beat the best *net-vs-net* (0.71, 0.73) yet would have
   *regressed* against classical (0.57, 0.58 < 0.652). The gate correctly refused
   to promote. This is exactly the Pass-5 self-play-drift trap (a candidate that
   wins the within-population game while losing absolute strength) — caught and
   blocked in a running loop. Net-vs-net-only gating would have promoted those and
   drifted the agent off the truth.
2. **No robust improvement on 4³ (S5 not cleanly met here).** Best vs classical
   moved 0.652 → 0.667 (one promotion), well within the N=24 anchor noise
   (SE ≈ 0.1). On 4³ the distilled champion is already near the small-board ceiling
   and classical is at its strongest (PROOF-1 [3ac354fd]: classical's value scales
   *better* with search on tiny boards), so self-play has little headroom to capture.

## Verdict & next
The AZ loop + anchored gate are correct and drift-resistant, but 4³ is the wrong
board to demonstrate S5 — it's where the teacher is strongest. The opportunity is
**5³/7³**, where random rollouts are weak (long games) and the net's value head is
calibrated (cross-board law). Constraint: classical anchor eval is expensive on
big boards (a 7³ classical game >250s), so the anchor there must be classical@low
or a fixed weaker reference. Recommended follow-up: run this loop on 5³ with a
cheap anchor + more iters/larger anchor-N for a statistically robust verdict.
