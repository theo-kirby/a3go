---
node_id: f6343208-8fd7-5f07-b265-e88f7f653c1b
slug: broken-tree-4527
title: 'INFRA-1 — GPU-batched MCTS server [RESOLVED: premise falsified — GPU was never the wall; M5 server already exists]'
created_at: '2026-06-08T06:51:09.894956+00:00'
parents:
- delicate-breeze-7763
- blue-boat-2948
- mute-cloud-4824
summary: RESOLVED. Profiling shows the batched GPU forward is only 3-11% of MCTS move time; BatchedMCTS (M5) already IS the game-parallel GPU inference server. PASS-11's 7^3 slowness was the CPU eval harness, not a missing server. Real keystone = the engine -> INFRA-2 (resolved 3.5x). No new build needed; C++/TensorRT routes deferred. $0/local.
origin:
  backend: flywheel
  node_id: f6343208-8fd7-5f07-b265-e88f7f653c1b
  slug: broken-tree-4527
  revision: 2
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 6eb32064-8565-548b-adde-b5e7459f9ff7
  slug: red-recipe-9108
  revision: 0
  pushed_at: '2026-08-08T10:03:07+00:00'
  content_sha256: 6288a4f70a0b2763d4e233271d26c965352a3a9dee99773340a840fbfb18757a
---
# INFRA-1 — GPU-batched MCTS inference server [RESOLVED — premise falsified]

## Result: the GPU was never the wall; the M5 batched server already exists.
Profiled `BatchedMCTS.run_policies` (M5) on GPU across board sizes (`bench_infra1.py`).
The batched GPU forward is only **3-11%** of move time; the remaining ~90% is
per-node **Python engine** cost (legal-move generation + clone). PASS-11's "7^3
sim-bound" was an artifact of the EVAL HARNESS running the net on CPU
(`net_vs_classical_mp.py`), not a missing GPU server — `BatchedMCTS` already IS
the game-parallel GPU inference server this node proposed to build.

So INFRA-1 resolves WITHOUT a new build: the keystone bottleneck is the engine,
handed off to **INFRA-2 [14377685->resolved 3.5x]**. The original routes (C++
MCTS+libtorch, TensorRT) are deferred — only worth it if the Python engine,
after INFRA-2, becomes the wall again at much larger boards/sims.

## Evidence (artifacts attached)
- `bench_infra1.json` — sims/s vs board size vs batch, GPU-forward fraction.
- `infra2_speedup.md` — full bottleneck analysis + before/after.

GPU-forward fraction (pre-INFRA-2): 4^3 ~4-11%, 5^3 ~3-8%, 7^3 ~4-10%. The GPU
(RTX 5090) idle-waits on Python. Decision criterion (">=1000 neural sims/move on
7^3 at <2s/move") was ALREADY met by BatchedMCTS on GPU (7^3@512 = 187ms/move/game
amortized even before INFRA-2; 53ms after). $0/local.

## Stop reason: objective_met (re-scoped) — server already existed; real wall = engine -> INFRA-2.