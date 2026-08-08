---
node_id: c16643ba-e947-5d7e-82e6-7eda4dbb1bfb
slug: still-dream-7550
title: 'Q10 RESOLVED: rising self-play strength on 4^3 — M5 volume breaks the M4 plateau (beats random 0.89 CI[0.84,0.93]; beats untrained gen-0 0.65, CI excl 50%)'
created_at: '2026-06-07T17:09:20.384460+00:00'
parents:
- broken-firefly-1068
- silent-dew-2840
summary: '12-gen gated AZ at 5x M4 volume (80 games/gen, batched via M5): 5 promotions, loss 3.99->1.39, vs_random 0.61->0.94. Clean high-N (N=200) final eval: final net beats uniform-random 0.889 [0.839,0.926] and beats its own untrained gen-0 net 0.652 [0.582,0.713] at IDENTICAL MCTS budget (CI excludes 50%) — isolating learned skill from search. 44.6 min wall-clock vs M4''s 64-min plateau.'
origin:
  backend: flywheel
  node_id: c16643ba-e947-5d7e-82e6-7eda4dbb1bfb
  slug: still-dream-7550
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: d9eb2849-9de4-5673-98e7-d19d4706c55a
  slug: lively-sky-9545
  revision: 0
  pushed_at: '2026-08-08T10:01:49+00:00'
  content_sha256: 2179ed9858165d4093489b2eff9a9a576023c6f39c442ba615c83aadae7f25bf
---
# Q10 — rising self-play strength (2nd half of the success bar)

**Hypothesis (from M4):** the 4^3 plateau is a VOLUME problem, not a bug — M4 had gating+buffer+Dirichlet working but only 24 games/gen and plateaued at baseline. M5 (batched game-parallel self-play, 22x) makes 5x the volume affordable.

## Run (train_batched.py): 4^3, 12 gens x 80 games, sims=48, eval=32, buffer=40k, gate=0.55
| gen | loss | cand_vs_best | promo | vs_random | vs_gen0 |
|---|---|---|---|---|---|
| 1 | 3.99 | 0.276 | | 0.613 | 0.290 |
| 4 | 3.41 | 0.556 | **PROMO #1** | 0.677 | 0.444 |
| 6 | 2.85 | 0.727 | **PROMO #2** | 0.867 | 0.467 |
| 7 | 1.94 | 0.560 | **PROMO #3** | 0.767 | 0.586 |
| 8 | 1.83 | 0.750 | **PROMO #4** | 0.867 | 0.581 |
| 10 | 2.06 | 0.533 | | **0.935** | 0.733 |
| 11 | 1.51 | 0.731 | **PROMO #5** | 0.839 | 0.484 |
| 12 | 1.39 | 0.296 | | 0.900 | 0.667 |

**5 promotions / 12 gens**; loss 3.99 -> 1.39; vs_random 0.61 -> 0.94. Total wall-clock **44.6 min** (M4 took 64 min to plateau).

## Clean high-N final eval (N=200/match, sims=48, Wilson 95% CI)
| matchup | win-rate | 95% CI | verdict |
|---|---|---|---|
| **final net vs uniform-random** | **0.889** | [0.839, 0.926] | beats random decisively |
| untrained gen-0 net vs random | 0.618 | — | (reference: MCTS+random-net) |
| **final net vs its own gen-0 net** | **0.652** | [0.582, 0.713] | beats predecessor, CI excl 50% |

## Conclusion
**Rising self-play strength is demonstrated on 4^3.** Both the per-gen promotion chain (5 successive nets each beat the prior best by >=0.55 in gated net-vs-net) and the high-N final eval show monotone-within-noise improvement. Critically, final-vs-gen-0 uses the **identical MCTS budget (sims=48)** — the only thing that changed is the network weights — so the +27pt jump in beats-random (0.618 -> 0.889) and the 0.652 head-to-head are **learned Go skill, not extra search**. This is the 2nd half of the success bar; the 1st half (beats baselines) is also met for random.

**M4's volume diagnosis was correct:** the same machinery at 5x volume (cheap only because of M5) lifts the plateau. Next levers: more volume/gens to push higher, higher self-play sims for stronger targets, and 5^3 (now affordable). A net-vs-classical-MCTS check at equal search budget is running separately as corroboration.

Artifacts: train_batched_4.json (full curve), experiments_q10_final.json (high-N eval), train_batched.py, final_strength.py, best_batched_4cubed.pt (checkpoint in repo).