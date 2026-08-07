---
node_id: b71da32b-c518-5a78-8a4f-0b6feaa6c82d
slug: soft-waterfall-3492
title: 'MILESTONE: neural agent BEATS classical MCTS 0.612 [0.533,0.686] at equal budget — recipe = distill teacher + stronger data + bigger net (64x6). Success bar''s classical leg CLEARED.'
created_at: '2026-06-08T01:10:47.495376+00:00'
parents:
- silent-dew-2840
- winter-water-4984
- frosty-grass-9317
summary: 'The trained net beats classical random-rollout MCTS at equal 48v48 budget, 0.612 [0.533,0.686] (N=160, decisive). Journey: 0.085 (self-play) -> 0.333 (distill 32x3) -> 0.484 (more/stronger teacher) -> 0.612 (64x6 net). Two levers: teacher-strength+data get to parity, net CAPACITY crosses the line. Success bar fully met on 4^3.'
flywheel:
  node_id: b71da32b-c518-5a78-8a4f-0b6feaa6c82d
  slug: soft-waterfall-3492
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 5521e921bd0249021d2cac3f06f3121eab27d718f610c3b9cc1a131ad4f038eb
---
# MILESTONE: the neural agent now BEATS classical MCTS (0.612 [0.533,0.686] at equal budget)

The success bar's classical-baseline leg — unmet since Pass 4 (the from-scratch self-play net lost 92%, 0.085) — is now **cleared**. The trained net beats classical random-rollout MCTS at EQUAL search budget (net 48 sims vs classical 48 playouts), **0.612 [0.533, 0.686]** over N=160 color-balanced games (93/152 decided, CI lower bound 0.533 > 0.5 = decisive).

## The full journey vs classical (equal 48v48)
| approach | win-rate vs classical |
|---|---|
| from-scratch self-play (P3, 960 games) | 0.085 |
| distill 32x3, 128-playout teacher (P5) | 0.333 |
| distill 32x3, +192-playout (22k examples) | 0.458 |
| distill 32x3, 29.6k examples | 0.484 |
| **distill 64x6, 29.6k examples** | **0.612** ✅ |

## The recipe that worked (two independent levers, both needed)
1. **Distill the teacher you have.** No human 3D-Go games exist, but classical MCTS beats the net — so distill classical self-play (state -> visit-policy, outcome) by supervised learning. This is the foundation (0.085 -> 0.333).
2. **Stronger + more teacher data.** Higher-playout classical (192 vs 128) + more games (29.6k examples from 128+192+192-playout rounds) lifted 32x3 from 0.333 to ~0.48 (parity), with diminishing returns.
3. **Net capacity.** Swapping the 32ch x 3block net for **64ch x 6block** on the SAME 29.6k data jumped 0.484 -> 0.612. The small net was capacity-bound on the value head; the scaling node [9605fb9a] had shown deeper search amplified value errors — more capacity fixed the value head, and the win followed.

So: distillation provides the foundation, teacher-strength + data get to parity, and **net capacity crosses the line**. Test-time sims scaling did NOT help (separate finding [9605fb9a]) — it's a net-quality problem, solved by better targets + more capacity, not more search.

## Success bar status
- **Beats uniform random:** YES (0.89-0.91+).
- **Beats fixed classical MCTS:** YES (0.612 at equal budget) — NEWLY CLEARED.
- **Rising self-play strength:** YES (Pass 3 [c16643ba]).
The operational success bar from THESIS.md is now fully met by the neural agent on 4^3.

## Method notes
- Net-on-CPU parallel eval (net_vs_classical_mp.py) across 14 cores; arch selectable via A3GO_CH/A3GO_BLK env vars. Classical = eye-avoiding random-rollout UCT, 48 playouts, rollout cap 64.
- Same engine (cross-validated 60/60), $0/local throughout.

Artifacts: experiments_distillbig_confirm.json (N=160 decisive), experiments_distillbig_vs_classical.json (N=64), the distill-ladder JSONs.