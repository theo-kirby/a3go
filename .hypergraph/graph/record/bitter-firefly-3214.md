---
node_id: 61f98193-0575-5820-8cca-61a622af8e72
slug: bitter-firefly-3214
title: 'Life & death in 3D: two-eye life holds; minimal unconditionally-alive eye space is the straight-four, same as 2D (vol ≤4)'
created_at: '2026-06-07T11:42:48.232139+00:00'
parents:
- green-queen-4645
summary: 'A bounded minimax kill-search (attacker moves first) reproduces 2D L&D theory exactly and finds that for eye-space volumes ≤4, 3D verdicts MATCH the 2D analogue: two separated eyes alive, straight-3 dead, straight-4 alive, square-four dead. The 2×2×2 cube (vol 8) is alive.'
flywheel:
  node_id: 61f98193-0575-5820-8cca-61a622af8e72
  slug: bitter-firefly-3214
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 8501693f08cafec798fd565b114a1e450b7b426fb44da569a21e05a60f8ec95d
---
# Q4 — Life & death in 3D Go (first constructive results)

## Method
`src/selfplay/experiments/exp_lifedeath.ts`. Fill an N³ board entirely with the defender (Black) except a carved-out empty **cavity** (the eye space); the board boundary seals the group so its *only* liberties are the cavity points. Then run an exact memoized minimax with the **attacker moving first** (the standard "killer plays first" / unconditional-life test): a shape is **ALIVE** iff the attacker cannot capture with optimal play. Deterministic; node-budgeted (4M) with position-hash memoization. All searches below completed within budget.

## Result
| shape | dims | vol | verdict | nodes |
|---|---|---|---|---|
| 1 point (single eye) | 3D | 1 | DEAD | 1 |
| 2 points adjacent (domino) | 3D | 2 | DEAD | 4 |
| **2 separated eyes** | 3D | 2 | **ALIVE** | 1 |
| straight-3 | 2D | 3 | DEAD | 15 |
| straight-3 | 3D | 3 | DEAD | 15 |
| **straight-4** | 2D | 4 | **ALIVE** | 90 |
| **straight-4** | 3D | 4 | **ALIVE** | 90 |
| 2×2 square (square-four) | 2D | 4 | DEAD | 32 |
| 2×2 square (planar, in 3D bulk) | 3D | 4 | DEAD | 32 |
| bent-3 (planar L) | 3D | 3 | DEAD | 11 |
| bent-3 (non-planar, uses +z) | 3D | 3 | DEAD | 11 |
| 2×2×2 cube | 3D | 8 | ALIVE | 5255 |

## Findings
1. **Validation:** the solver reproduces known 2D life-and-death theory exactly — straight-3 dead, straight-4 alive, square-four dead — which is strong evidence the search is correct.
2. **Two-eye life holds in 3D:** two separated single-point eyes are unconditionally alive (the attacker has no legal move — filling either eye is suicide). The classic sufficient condition carries over.
3. **For eye-space volume ≤ 4, 6-connectivity does NOT change the verdict:** every shape tested has the same life/death status in the genuinely-2D plane and in the 3D bulk. The minimal *unconditionally* alive single eye space is the **straight-four (vol 4)** in both — three-point spaces are all dead (killer takes the vital point), even the non-planar bent-3 that uses the extra z-dimension.
4. **Compact 3D shapes live once large enough:** the 2×2×2 cube (vol 8) is alive (enough room to force two eyes).

## Open (frontier)
- **Seki** (mutual life) — not yet probed; needs shared-liberty constructions.
- Whether any *compact* 3D shape of volume 5–7 is alive where its 2D-projected analogue is dead (does 3D ever make life *easier* at a given volume?).
- Eye spaces touching faces/edges/corners (boundary effects), and multi-group capturing races.

## Reproduce
`OUT=experiments/lifedeath.json npx tsx src/selfplay/experiments/exp_lifedeath.ts` (deterministic). Artifact attached.