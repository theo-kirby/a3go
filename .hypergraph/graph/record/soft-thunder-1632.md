---
node_id: ebff5f9f-80c2-5716-a09a-c08141d933d7
slug: soft-thunder-1632
title: EVAL-2 — Superko-aware exact solver (history-threaded TT) — push S3 past 2×2×2 [MED, no GPU]
created_at: '2026-06-09T07:00:15.426327+00:00'
parents:
- shrill-moon-6110
- proud-king-2753
summary: Extend the exact solver beyond the current 2×2×2 frontier by threading game history through a transposition table so memoization stays sound under superko (PROOF-3 proved position-only memo is unsound in 3D). The only path to a meaningful S3 oracle on bigger boards. Self-contained, theoretically clean, CPU-only. Extends PROOF-3 22d59c45.
origin:
  backend: flywheel
  node_id: ebff5f9f-80c2-5716-a09a-c08141d933d7
  slug: soft-thunder-1632
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 159b640b-75a8-5a45-a3e1-1ab722422d0b
  slug: round-violet-7813
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: b18aa4c7252213056695c89583782f467299db70c2ed4a5b3bd4ecd6acf99939
---
# EVAL-2 — Superko-aware exact solver (history-threaded TT) — push S3 past 2×2×2 [MED, no GPU]

## Objective
Build a **superko-aware exact solver**: a history-threaded minimax with a transposition table keyed on (position, **relevant history / superko-set**) rather than position alone, so memoization is **sound** under superko. Push the exact-solve frontier past the current 2×2×2 ceiling.

## Why it matters (which finding it extends)
PROOF-3 `22d59c45` delivered exact values for ≤4-cell boards and **proved position-only memoization unsound** (memo gave +2/+4 vs exact 0/+1 because superko makes value history-dependent) — so today an S3 oracle exists only for ≤4-cell boards, with 2×2×2 as the frontier *set by ko*, not cell count. The fix KataGo-adjacent engines use is to make the cache key superko-correct (thread the position-history / ko-state). This is the **only** path to a meaningful S3 (near-optimal check against ground truth) on boards big enough to matter.

## Implementation route
Augment the PROOF-3 solver: incremental Zobrist hash over the *history set* (reuse INFRA-2's Zobrist superko machinery); TT key = (board-zobrist, superko-ban-set signature); prove the key is sound (same key ⇒ same game-theoretic value). Solve upward (2×2×2, then 3×2×2, …) until compute-bound; record the new frontier.

## Decision criterion (CI-based, n≥128)
Deliverable is exact values on ≥1 board strictly larger than 2×2×2 with a **soundness argument/validation** (cross-check against brute-force history-threaded minimax on the largest tractable case — the gold standard, not win-rate). Criterion: new exact-solved frontier established + memo proven sound on it.

## Preconditions / risks
CPU-only, no GPU, self-contained; reuses INFRA-2 Zobrist (`14377685`). Risk: history-threaded state explodes the TT (the whole difficulty — bound it; report where it becomes intractable). Independent of all neural work.

## Cost · value
MED build, $0/local, no GPU. Value: the only route to a *meaningful* S3 oracle; theoretically clean; a strong correctness anchor for the whole campaign.

## Expected artifacts
Superko-aware solver, exact-value table for the new frontier, a soundness note + brute-force cross-validation, intractability boundary.

## Inspiration source
Extends PROOF-3 `22d59c45` (its unsoundness finding + frontier); engine-gating/solver lineage.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
