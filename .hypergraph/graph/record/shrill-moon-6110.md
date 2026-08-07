---
node_id: 22d59c45-09a2-5524-9943-b2687e52cb94
slug: shrill-moon-6110
title: 'PROOF-3 — exact solve of smallest 3D boards [DELIVERED: 2x2x1 fair komi +1; memoization proven UNSOUND; 2x2x2 = exact frontier]'
created_at: '2026-06-08T06:51:14.317791+00:00'
parents:
- mute-cloud-4824
summary: 'DELIVERED. Sound history-threaded minimax: exact values 1x1x1=0, 2x1x1=0, 2x2x1=+1 (Black). Two findings: (1) position-memoization is UNSOUND for 3D Go — gives +2/+4 vs exact 0/+1 because it permits superko-forbidden ko recaptures (value is history-dependent); (2) the smallest genuine 3D board 2x2x2 already exceeds naive exact solving (>8M nodes) — the frontier is set by ko, not cell count. S3 oracle exists only for <=4-cell boards today. $0/local.'
flywheel:
  node_id: 22d59c45-09a2-5524-9943-b2687e52cb94
  slug: shrill-moon-6110
  revision: 2
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 68feecee8c1cca29cbbe1fc6c5c6440eaade6bbae8e27f0d27d37adcf44670b5
---
# PROOF-3 — exact solving of the smallest 3D boards [DELIVERED + frontier]

Sound alpha-beta minimax with full superko history threaded through clones (no
position memo). Value = optimal Black_area-White_area at komi 0; fair komi = value.

## Exact, sound ground truth
| board | cells | fair komi | winner | nodes |
|---|---|---|---|---|
| 1x1x1 | 1 | 0 | draw | 3 |
| 2x1x1 | 2 | 0 | draw | 27 |
| 2x2x1 (2D) | 4 | **+1** | Black | 2,385 |

## Two findings
1. **Position-memoization is UNSOUND for 3D Go — demonstrated.** A solver memoizing
   by (Zobrist, player, passes) returns fair_komi +2 (2x1x1) and +4 (2x2x1) vs the
   true 0 and +1 — it permits ko recaptures positional superko forbids. The game
   value is genuinely history-dependent (consistent with ko-ubiquity [31dae43b]).
2. **The smallest genuine 3D board (2x2x2, 8 cells) is already beyond naive exact
   solving:** sound no-memo search exceeds 8M nodes without closing it. The exact-
   solving frontier is set by KO, not cell count, and sits at ~4 cells without a
   superko-aware transposition / retrograde scheme.

## S3 status
A ground-truth oracle exists only for <=4-cell boards (degenerate/2D), so S3
(near-optimal vs exact) is trivially checkable but low-information today. A
meaningful S3 needs a superko-aware exact solver (history-equivalence transposition
or retrograde analysis) — a real, separable build. Recorded as the honest frontier.
Artifacts: solve_small.json, solve_small_summary.md. $0/local. Stop reason: objective_met (exact ground truth for smallest boards + unsoundness/frontier findings).