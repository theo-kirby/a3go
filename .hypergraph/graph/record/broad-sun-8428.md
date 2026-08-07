---
node_id: c85ce2bf-30fb-5784-82d4-a8033dc93bd3
slug: broad-sun-8428
title: 'Board geometry oddity: 3³ averages degree 4 (like a 2D plane); the degree-6 interior dominates only as N grows'
created_at: '2026-06-07T11:44:26.066592+00:00'
parents:
- frosty-bread-3825
summary: 'Degree distribution per N³: corners are degree 3 (vs 2 in 2D), bulk is degree 6 (vs 4). 3³ has a single interior point and mean degree exactly 4.0 — as connected as an infinite 2D board — while 9³ is 47% interior. This substrate explains the ladder/L&D differences.'
flywheel:
  node_id: c85ce2bf-30fb-5784-82d4-a8033dc93bd3
  slug: broad-sun-8428
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 4cf0e870839b4e761ac0d13fcf86b4da9b639f4793219206e9b4205892e1d9f3
---
# Q5 — How 6-connectivity reshapes the board (geometric substrate)

## Method
`src/selfplay/experiments/exp_geometry.ts` — classify every intersection of N³ by neighbor degree using the engine topology (3 = cube corner, 4 = edge, 5 = face, 6 = interior). Deterministic, instant.

## Result
| N | points | corner(3) | edge(4) | face(5) | interior(6) | interior% | mean degree |
|---|---|---|---|---|---|---|---|
| 3³ | 27 | 8 | 12 | 6 | 1 | 3.7% | **4.00** |
| 4³ | 64 | 8 | 24 | 24 | 8 | 12.5% | 4.50 |
| 5³ | 125 | 8 | 36 | 54 | 27 | 21.6% | 4.80 |
| 7³ | 343 | 8 | 60 | 150 | 125 | 36.4% | 5.14 |
| 9³ | 729 | 8 | 84 | 294 | 343 | 47.1% | 5.33 |

## Findings (oddities confirmed)
1. **Corners are degree 3, not 2.** Every cube has exactly 8 corners; in 2D a corner has 2 liberties, in 3D it has 3.
2. **3³ is, on average, a 2D board.** It has a *single* degree-6 interior point and a **mean degree of exactly 4.0** — identical to the interior of an infinite 2D grid. So 3³ behaves much like a small 2D game; the genuinely-3D character (high-degree bulk) is barely present.
3. **The degree-6 interior takes over with size.** Interior fraction climbs 3.7% → 47% from 3³ → 9³ (mean degree → 5.33). 3D-ness is a large-board phenomenon.

## Why it matters (ties the campaign together)
This is the substrate behind the other results: a ladder is a 2-liberty pin, and in the **degree-6 interior** a forced extension gains liberties too fast to maintain it (see ladders node) — but on 3³, which is mostly boundary, 2D-like tactics fare better. Likewise life needs more eye-space room as connectivity rises. It also reframes Q2: 3³ is nearly a 2D game; the interesting 3D regime starts at 4³–5³ and up.

## Reproduce
`OUT=experiments/geometry.json npx tsx src/selfplay/experiments/exp_geometry.ts`. Artifact attached.