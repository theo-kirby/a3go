---
node_id: c4091781-dc84-5196-aa7f-b253ece0db28
slug: dark-firefly-4075
title: '5^3 distillation pilot: under-resourced net loses to classical (0.045); strong-teacher 5^3 data-gen is too slow on the Python engine -> C++ engine is the prerequisite for the bigger-board recipe'
created_at: '2026-06-08T02:22:59.113150+00:00'
parents:
- hidden-forest-3847
- withered-boat-6047
summary: 'Applying the 4^3 recipe to 5^3 is gated on classical data-gen speed: 96-playout 5^3 self-play was >16 min/game (killed); a minimal 40-playout pilot (6.7k examples) gave a near-random policy and the net lost 0.045 to classical. NOT a refutation (under-resourced). Hint: 5^3 value MSE 0.027 < 4^3''s 0.045 (all-decisive games). Bigger-board program needs the C++ engine.'
flywheel:
  node_id: c4091781-dc84-5196-aa7f-b253ece0db28
  slug: dark-firefly-4075
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 020dad7b608bedf7cf2875c519ccc17fb3a41b070cc77dd5732c07ce7cca667d
---
# 5^3 distillation pilot: under-resourced net loses to classical (0.045) — extending the recipe to 5^3 is GATED on classical data-gen speed (the C++ engine)

The scaling node [28f66847] predicted 5^3 should favor neural value (rollouts noisier on a bigger board). Tried to apply the 4^3 winning recipe to 5^3.

## What happened: classical 5^3 data-gen is the wall
A strong-teacher 5^3 collection (96 playouts) was **>16 min/GAME** on the Python engine (killed). A *minimal* pilot (40 playouts, cap 30, 48 games -> 6,717 examples) was tractable (~18 min) but a WEAK, SMALL teacher over a 126-action space.

## Result: net loses (under-resourced, NOT a refutation)
| metric | 5^3 pilot |
|---|---|
| net (64x6, 48 sims) vs classical@40 | **0.045 [0.008, 0.218]** (1/22) |
| distilled holdout policy-acc | 0.064 (near-random over 126 actions) |
| distilled holdout value MSE | **0.027** (lower than 4^3's ~0.045) |

The policy prior is essentially random (6.7k examples, weak 40-playout teacher), so 48-sim MCTS is weak and loses. This is **massively under-resourced vs the 4^3 winning recipe** (128+192-playout teachers, 29.6k examples, 64x6 net) — not a test of the bigger-board hypothesis.

## The decision-relevant finding
**Intriguing hint:** the 5^3 value head fit BETTER than 4^3's (MSE 0.027 vs ~0.045) — consistent with 5^3 being all-decisive (0 draws) and giving cleaner value targets, the direction the scaling node predicted. But the POLICY needs far more + stronger teacher data to make MCTS strong, and **classical 5^3 self-play at strong-teacher fidelity is prohibitively slow on the Python engine** (same wall as 256-playout 4^3, ~30 min/game).

**Conclusion: extending the distillation recipe to 5^3 (and 7^3/9^3) is GATED on faster classical data-gen -> the C++ engine + leaf-parallelism (autogo [b4fd8252], agenda frontier #2) is now the prerequisite for the bigger-board program.** This is a large, discrete build (a go/continue decision), not a cheap probe.

Artifact: experiments_distill5_vs_classical.json.