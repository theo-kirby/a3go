---
node_id: a0e8a3f6-8dce-5d26-9d10-e34901d4a7e1
slug: frosty-grass-9317
title: 'Q10 caveat: trained 4^3 net does NOT beat classical MCTS — loses ~92% at equal budget; rising self-play strength is RELATIVE not absolute'
created_at: '2026-06-07T17:51:55.743729+00:00'
parents:
- still-dream-7550
- silent-dew-2840
summary: 'Parallel net-vs-classical (net on CPU x14 cores). Equal budget 48v48: net wins only 0.085 [0.034,0.199] vs classical random-rollout MCTS; vs 128-playout classical, 0.042 [0.012,0.14]. Despite beating random 0.89 and gen-0 0.65, the net is far below classical strength on 4^3. Lesson: self-play win-rate != absolute strength; anchor to a non-self baseline.'
flywheel:
  node_id: a0e8a3f6-8dce-5d26-9d10-e34901d4a7e1
  slug: frosty-grass-9317
  revision: 2
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 96c4c86277e1cc506adb20dae787e7d4e51b72a81a25daa0873c97cf47c7213c
---
# Q10 reality-check: neural net vs classical MCTS (the success bar's 2nd baseline leg)

PASS 3 showed **rising self-play strength** (net beats random 0.89, beats its own untrained gen-0 0.65 at equal MCTS budget). That establishes *relative* improvement. This node tests **absolute** strength against the success bar's fixed classical baseline: a non-neural UCT MCTS with eye-avoiding random rollouts (classical_mcts.py).

## Method
Color-balanced games, net plays argmax (temp~0) via MCTS, classical via a playout budget. Parallelized across 14 CPU cores (net on CPU — tiny net; also frees the GPU for the concurrent 5^3 branch). PASS 3's sequential GPU attempt was ~3 min/game (2-game inconclusive pilot); this resolves it with N=48.

## Result
| classical budget | net win-rate | 95% CI | verdict |
|---|---|---|---|
| **48 playouts (EQUAL to net's 48 sims)** | **0.085** (4/47) | [0.034, 0.199] | **net loses decisively** |
| 128 playouts (stronger baseline) | 0.042 (2/48) | [0.012, 0.14] | net loses decisively |

## Interpretation (honest, blank-slate)
The trained net is **far weaker than classical random-rollout MCTS**, even at equal search budget. Why: on a tiny 64-point board the games are short and random rollouts run to terminal, so classical MCTS gets an **accurate value signal essentially for free**; the net's learned value/policy after ~960 self-play games is much noisier. So 'beats random 0.89' mostly reflects 'MCTS+anything >> uniform random', and 'beats gen-0 0.65' reflects a modest learned edge — neither implies classical-level absolute strength.

**This qualifies the PASS 3 'plateau broken' claim:** the plateau broke in the *relative* sense (successive nets beat predecessors), but the agent has NOT cleared the success bar's classical-baseline leg. The bar's 'beats baselines' = random AND classical; **random: cleared; classical: NOT cleared** by the neural agent at this training level.

## Methodology lesson
**Self-play win-rate (cand_vs_best, vs_gen0) measures relative, not absolute, strength** — a self-referential ladder can rise while the whole ladder sits below a fixed external baseline. Always anchor to a non-self baseline (here classical MCTS). This is the strength-analogue of the earlier 'loss != strength' lesson.

## Path to super-classical (open frontier)
To beat classical the net needs a much stronger value head: far more self-play volume/generations, higher self-play sims (stronger targets), a larger net, and/or more MCTS sims at play time. Measured starting point: 0.085 at equal budget -> must climb past 0.5.

Artifacts: experiments_net_vs_classical_eq.json (48/48), experiments_net_vs_classical_p128.json (128), net_vs_classical_mp.py, classical_mcts.py.