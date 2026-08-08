---
node_id: e45385fe-3584-5056-94e2-999cc48b294a
slug: wispy-glitter-1456
title: 'ALGO-S1 — MCTS-Solver: exact win/loss backup for endgame & L&D [search-structure, cheap]'
created_at: '2026-06-18T13:58:07.616242+00:00'
parents:
- proud-king-2753
summary: 'Augment the MCTS with proven-win/loss propagation (MCTS-Solver): when a node is a forced terminal, back up ±∞ instead of a noisy value estimate, so solved subgames are played perfectly. 3D endgames and life-and-death are exactly where the value head is weakest (SEARCHX-1 said search carries strength) — exact backup is a cheap, principled strength lever.'
origin:
  backend: flywheel
  node_id: e45385fe-3584-5056-94e2-999cc48b294a
  slug: wispy-glitter-1456
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 28a082e8-4335-5c1c-9896-95fe834a0e11
  slug: dry-water-2931
  revision: 0
  pushed_at: '2026-08-08T10:02:40+00:00'
  content_sha256: de91e85140d4162821b50073b778267284c204c1444442eeac2d192d5c4b5910
---
# ALGO-S1 — MCTS-Solver (exact terminal backup)

## Objective
Add MCTS-Solver semantics to the batched MCTS: when a child is a proven terminal (or all children are proven losses/there is a proven win), propagate an exact ±∞ value instead of the network estimate, so the search plays solved positions perfectly and prunes proven-lost lines.

## Why it matters (which finding it extends)
SEARCHX-1 (`6551d432`) showed search — not the raw net — carries 5³ strength, and PROBE-2 showed the value head is calibrated but still just an estimate near terminals. MCTS-Solver replaces estimates with proof exactly where it matters most: endgame and life-and-death (LD-1/2/3). It is a well-known 30–80 Elo lever in solver-augmented MCTS, cheap to add, and complements (not competes with) the policy/value levers.

## Implementation route
Engine + search only (no training). The engine already detects terminal/scored positions; mark nodes proven-win/loss when a child is a winning terminal or all children proven, propagate up. Reuse the EVAL-2 superko-aware solver (`ebff5f9f`) for deeper proofs. Net-vs-net solver-MCTS vs plain MCTS at matched sims.

## Decision criterion (CI-based, n≥128)
net-vs-net: solver-MCTS CI-separated above plain MCTS at matched sims, n≥128/3-seeds (5³, and the depth ladder where endgames are short). Also measure endgame error reduction directly.

## Preconditions / risks
Self-contained (engine + search). Best paired with EVAL-2 `ebff5f9f`. Risk: proof depth is limited mid-game — gains concentrate in the endgame; report where it helps.

## Cost · value
CHEAP (no training, pure search change). High value: principled, additive strength, strongest exactly where the value head is weakest.

## Expected artifacts
Solver-augmented `batched_az` variant, net-vs-net JSON vs plain MCTS, endgame-error reduction stats.

## Inspiration source
MCTS-Solver (Winands et al.); solver-augmented AlphaZero. Extends SEARCHX-1 `6551d432`, EVAL-2 `ebff5f9f`, LD nodes.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-3 (geometry / dimensionality-ladder / search-structure axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*