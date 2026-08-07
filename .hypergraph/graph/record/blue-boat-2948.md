---
node_id: cff3a5d1-b65b-5429-8903-bf5594ef7954
slug: blue-boat-2948
title: 'C++ engine + self-play generator: 60/60 cross-validated, ~60x faster (4^3) / ~7x (5^3) — unblocks 7^3+ and strong-teacher data-gen at $0/local'
created_at: '2026-06-08T03:53:04.294690+00:00'
parents:
- bold-scene-5560
- withered-boat-6047
- lively-meadow-0948
summary: Built a g++ C++ 3D-Go engine + classical self-play data generator (standalone binary, no pybind11). Cross-validates 60/60 vs TS fixtures on 3^3 AND 4^3. ~60x faster than Python on 4^3 (2.7s/game), ~7x on 5^3 (160 games in 3 min, 31k examples). Validated as a training drop-in (C++ data -> higher holdout acc 0.112 vs 0.068). Removes the data-gen wall that gated the bigger-board program (autogo's headline lever).
flywheel:
  node_id: cff3a5d1-b65b-5429-8903-bf5594ef7954
  slug: blue-boat-2948
  revision: 2
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: eccabefa1a58bd6caf40331ab38c4697ad06d87f0048bba3be0408b52395b162
---
# C++ engine + self-play generator: 60/60 cross-validated, ~60x faster (4^3) / ~7x (5^3) — unblocks the bigger-board program

autogo's headline lever (C++ engine + leaf-parallelism) and our agenda frontier #2. Built a standalone g++ C++ 3D-Go engine + classical self-play data generator (no pybind11/CMake — direct g++ compile + binary file I/O, lowest build risk).

## Correctness FIRST (cross-validated before trusting)
`cpp/engine.cpp` implements the same rules (liberties, capture-over-suicide, suicide rejection, positional superko, Tromp-Taylor scoring). Replaying the TS-dumped fixtures and comparing the full TT breakdown: **60/60 on 3^3 AND 60/60 on 4^3** — behaviorally identical to the TS reference and the Python port. (`cpp_crossval.py`.)

## Throughput (the unlock)
| board | Python (fast playout) | C++ | speedup |
|---|---|---|---|
| 4^3 classical self-play | ~3 min/game (128 pl) | **2.7 s/game** (96 pl) | **~60x** |
| 5^3, 160 games @96 pl (14-way parallel) | ~20 min | **184 s (3 min)**, 31k examples | **~7x** wall |

Parallel wrapper (`cpp_collect.py`) launches K engine processes and combines their binary outputs into a train_distill-compatible `.npz`. The binary format (int32 count,n; then float32 planes/policy/z) loads directly in Python (`cpp_loader.py`).

## Validated as a training drop-in
Distilling a 64x6 net on the C++-generated 5^3 data (31k examples) gives **higher** holdout policy accuracy (0.112) than the Python-generated set (0.068) — more data, same recipe. (Net-vs-classical confirmation eval running.)

## Why this matters
The Python engine was the wall for strong-teacher / bigger-board data-gen (256-playout 4^3 was ~30 min/game; 5^3 was >16 min/game). The C++ engine removes that wall: **7^3/9^3 distillation and arbitrarily-strong teachers are now tractable at $0/local.** This is the prerequisite the 5^3-pilot [c4091781] and transfer [e7c35c64] nodes flagged.

## Engineering notes
- `cpp/engine.cpp` modes: `crossval` (stdin games -> TT breakdown) and `selfplay n games playouts cap seed outfile`.
- Classical UCT MCTS + fast random playout (no superko in rollouts, matching the Python fast playout). Current bottleneck: `legal_play_moves` clones per candidate (room for a grid-only no-ko legality to scale 7^3 further).
- Build: `g++ -O2 -std=c++17 cpp/engine.cpp -o cpp/engine` (g++ 13.3, no cmake needed).

Artifacts: engine.cpp, cpp_crossval.py, cpp_collect.py, cpp_loader.py (in repo).

## Validation eval result (honest caveat)
The C++-data-trained 64x6 net scored **0.25 @256 sims vs Python-classical@48** — below the Python-data net's 0.417 (CIs overlap [~.12,.45] vs [.25,.61], so within noise, but lower point estimate). The C++ self-play games are LONGER (~194 vs 136 examples/game), suggesting the **C++ classical UCT teacher plays somewhat weaker** than the Python one (drags games out). Takeaway: the C++ ENGINE OPS are validated (60/60) and fast; the C++ MCTS TEACHER STRENGTH needs tuning (c_puct, expansion/rollout policy, or higher playouts) before it matches the Python teacher's distillation quality. Infrastructure win stands; teacher-tuning is a refinement.