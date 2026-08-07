---
node_id: b4fd8252-d081-5898-9e8a-117bbc918757
slug: lively-meadow-0948
title: 'Reference: ericjang/autogo — transferable findings (Dirichlet-anneal, distill-from-teacher, variety>depth, C++/leaf-parallel ceiling, batched inference server)'
created_at: '2026-06-07T18:53:33.469144+00:00'
parents:
- purple-fog-6345
- bold-pine-0367
summary: 'External sister project (Claude-automated 2D-Go research). Validates our M5 (their 19.4x C++ ~ our 22x Python). Pass 5 incorporates: classical-MCTS distillation warm-start + Dirichlet-noise annealing (targets our ''net loses to classical'' result). Skips multi-node/managed infra. C++ engine + leaf-parallelism left as high-value frontier.'
flywheel:
  node_id: b4fd8252-d081-5898-9e8a-117bbc918757
  slug: lively-meadow-0948
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: cdfd474ba86cf29b5dca31b6cc83405e49f8b9204ced044240db97cb7cbec88b
---
# External source: ericjang/autogo — transferable findings

https://github.com/ericjang/autogo — Eric Jang's project automating the AI-research loop (Claude-driven `autoresearch`/`experiment` skills) on **2D Go (19x19)**. A sister project to this campaign (automating the researcher), with a Python + **C++/pybind11 engine & MCTS**, a **batched inference server**, AlphaZero self-play, on a **multi-node GPU cluster**. Reviewed in Pass 5; this node records what transfers and what we're incorporating.

## Independent validation of our M5
Their throughput experiment: Python MCTS 48 sims/s -> C++ + batched-eval + leaf-parallelism (virtual loss) **933 sims/s (19.4x)** on 19x19. We hit **22x** on 4^3 with *pure-Python* batched eval (M5 [dark-poetry-2083]) — same ballpark; their result shows the next ceiling is C++ + virtual loss.

## Transferable findings (autogo fastlearn + throughput reports)
1. **Fixed Dirichlet root noise compounds badly across iterations** — gave a one-shot boost but caused collapse by iter ~5; noise-free MCTS gave cleaner per-game targets + consistent self-improvement.
2. **Supervised bootstrap from a stronger teacher** works (they pre-train on strong games). We have no human 3D-Go data, but classical MCTS beats our net 92% -> classical MCTS is our teacher.
3. **Variety > per-game strength**: 50 games x 1024 sims beat 25 x 2048 at equal compute. Favor game count over depth.
4. **Holdout policy accuracy** + a **league/Elo** as non-self strength anchors (we independently learned in Pass 4 that self-play win-rate != absolute strength).
5. **Replay buffer = regularization; pruning hurts** (matches our approach). **Loss-masking bug**: train policy on ALL MCTS positions, not just the winner's — we already do this (verified, no bug).
6. **C++ engine + MCTS via pybind11 + leaf-parallelism (virtual loss)** is the lever beyond our Python ceiling -> enables 5^3/7^3 + super-classical volume (our frontier #7). High effort.
7. **Batched inference server** (queue + adaptive ~1-2ms timeout, batch 64, zero-pad-to-max-size + mask for mixed board sizes) — the scalable form of our in-process batching, useful if we go multiprocess/async.

## Being incorporated in Pass 5 (cheap, high value; targets 'net loses to classical' [a0e8a3f6])
- **Classical-MCTS distillation warm-start** (finding 2): collect classical self-play (state, visit-policy, outcome), supervised-train the net, evaluate vs classical. Track holdout policy accuracy (finding 4).
- **Dirichlet noise annealing** across generations 0.25->0.05 (finding 1), + a warm-start-from-checkpoint path so AZ self-play can continue from the distilled net.
- **Variety > depth** (finding 3) as run-sizing guidance.

## Skipped (against our $0/local single-box posture)
Multi-node GPU cluster, SSH/Docker dispatch, GPU leases — managed/multi-box compute. If a question truly needed it we report, not spend. C++ engine port = high-value but high-effort; left on the frontier.

Related: [[methodology]] (self-play WR != absolute strength), Q10 net-vs-classical [a0e8a3f6], M5 [dark-poetry-2083].

**Scaling-law follow-up (PASS-16):** autogo's central **train-time + test-time scaling-law** thesis is now a dedicated STAGED direction — **EVAL-3** `8c790338-cbbd-598c-ac01-d8f6d95fc321` (characterize a3go strength as a joint train×test×board-size surface, unifying the cross-board law `0bc38c41` and PROOF-2 search-scaling `75615ad2`). Also seeded: SEARCH-5 (self-play exploration — anneal-don't-fix, this node's lesson 1). See EXPANSION index `f9f2bf74-2ce6-5488-b471-dc0b6c422b99`.
