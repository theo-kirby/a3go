# PROOF-3 — exact solving of the smallest 3D-Go boards (ground truth)

Solver `neural/solve_small.py`. Sound method: alpha-beta minimax with the full
superko history threaded through clones (NO position memoization — see below).
Value = optimal Black_area − White_area at komi 0 (Tromp-Taylor); fair komi = that
value. Raw: `solve_small.json`.

## Exact, sound results
| board | cells | value (komi 0) | fair komi | winner | exact nodes |
|---|---|---|---|---|---|
| 1×1×1 | 1 | 0 | 0 | draw | 3 |
| 2×1×1 | 2 | 0 | 0 | draw | 27 |
| 2×2×1 (2D) | 4 | **+1** | **+1** | Black | 2,385 |

These are exhaustively solved. The smallest genuine 2D board (2×2×1) is a Black
win by 1 point; fair komi = 1.

## Two findings
1. **Position-memoization is UNSOUND for 3D Go — demonstrated, not just argued.**
   A solver that memoizes by (Zobrist position, player, passes) — ignoring superko
   history — returns fair_komi **+2** on 2×1×1 and **+4** on 2×2×1, versus the true
   **0** and **+1**. It over-credits the side to move because it permits ko
   recaptures that positional superko actually forbids. Concrete evidence that the
   game value is genuinely history-dependent (consistent with "ko is ubiquitous in
   3D" [31dae43b]) — you cannot collapse positions reached via different histories.
2. **The smallest genuine 3D board (2×2×2, 8 cells) is already beyond naive exact
   solving.** Sound (history-threaded, no-memo) search exceeds an 8M-node budget
   without closing 2×2×2; without a sound superko-aware transposition scheme (or
   symmetry/retrograde machinery), exact 3D solving stops at ~4 cells. This is the
   tractability frontier, and it is set by ko, not by raw cell count.

## Relation to the Success bar
S3 (near-optimal vs exact solve) has a ground-truth oracle only for ≤4-cell boards
today; benchmarking the trained agent against optimal play there is trivial but
low-information (these boards are degenerate/2D). A meaningful S3 needs a
superko-aware exact solver (sound transposition keyed on history-equivalence, or
retrograde analysis) — a real but separable build. Recorded as the honest frontier.
