---
node_id: bea50f57-5bd9-5c87-a78e-11279248a88a
slug: cool-leaf-5231
title: ALGO-S2 — Graph MCTS + superko-aware transposition table [search-structure, efficiency+strength, cheap]
created_at: '2026-06-18T13:58:08.267882+00:00'
parents:
- proud-king-2753
summary: 3D Go has many transpositions (move orders reaching the same position). The engine already maintains a zobrist hash; reuse it to merge tree nodes that share a position (graph MCTS / TT), so visit counts and values pool across paths. Cheaper effective search + stronger play, especially as boards grow. The superko history makes correctness subtle — a genuine 3D twist.
flywheel:
  node_id: bea50f57-5bd9-5c87-a78e-11279248a88a
  slug: cool-leaf-5231
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 80d046c72294a01d58ab410e9678789fb51efa883c9d7593b865f87f0056eb11
---
# ALGO-S2 — Graph MCTS with a superko-aware transposition table

## Objective
Replace the MCTS tree with a DAG: positions reached by different move orders share one node, keyed by the engine's zobrist hash, so visits/values pool across transpositions (graph history interaction handled by the superko history). Effectively multiplies search efficiency.

## Why it matters (which finding it extends)
SEARCHX-1 (`6551d432`) showed strength is search-bound (5³ needs ~512 sims; 7³ more). Transpositions are abundant in Go and likely MORE so in 3D's 6-connected lattice; merging them is a direct efficiency win that turns the same sim budget into deeper effective search — attacking the sim-bound ceiling without a faster net. The superko twist (the same grid with different histories is legally different) makes the correct keying a real 3D research question.

## Implementation route
Search only. The engine exposes `board.zobrist`; key tree nodes by (zobrist) or (zobrist, history-signature) and share statistics, with care for superko-divergent histories (the dominant correctness risk — validate against plain MCTS on positions with/without ko). Net-vs-net graph-MCTS vs tree-MCTS at matched sims and matched wall-clock.

## Decision criterion (CI-based, n≥128)
net-vs-net: graph-MCTS CI-separated above tree-MCTS at matched sims (more efficient search), AND no strength regression at matched wall-clock; plus a transposition-rate measurement by board size. Correctness gate: identical results to tree-MCTS on ko-free positions.

## Preconditions / risks
Self-contained. Risk: superko/graph-history-interaction correctness — a node's value can depend on path via ko; key conservatively (include a ko-relevant history signature) and validate. This risk is itself a finding.

## Cost · value
CHEAP (search change, no training). High value: a sim-efficiency multiplier that directly eases the sim-bound ceiling, with a novel 3D-superko correctness angle.

## Expected artifacts
Graph-MCTS variant, transposition-rate-by-size JSON, net-vs-net efficiency comparison, a superko-keying correctness note.

## Inspiration source
Transposition tables / graph MCTS (GHI problem). Extends SEARCHX-1 `6551d432`, PROOF-3 superko `22d59c45`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-3 (geometry / dimensionality-ladder / search-structure axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*