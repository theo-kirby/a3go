---
node_id: 853d7c2c-10cb-5c76-88c6-a448e8773d25
slug: long-king-8643
title: 'Q8: strong net has NO opening positional preference on 4^3 (corner=edge=face=interior, ~uniform) — unlike 2D Go''s corner-first opening'
created_at: '2026-06-08T02:24:38.423401+00:00'
parents:
- floral-river-3044
- frosty-bread-3825
summary: 'Champion 64x6 net''s policy prior on the empty 4^3 board is near-uniform across position classes (mean/point ~0.0154 for corner/edge/face/interior alike = 1/65). Unlike 2D Go''s strong corner-first opening, 3D 4^3 has flat opening positional structure. Caveat: distilled policy is diffuse; MCTS-visit / value-of-stone is a sharper follow-up.'
flywheel:
  node_id: 853d7c2c-10cb-5c76-88c6-a448e8773d25
  slug: long-king-8643
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 20b6ba31386ccbf433550f5ef0714b27988e0aade77106b00785a0514c9628a2
---
# Q8/Q5 — the strong net has NO opening positional preference on 4^3 (unlike 2D Go's corner-first)

Probed the champion 64x6 net (which beats classical [b71da32b]) by reading its policy prior on the EMPTY 4^3 board — where does a strong 3D-Go agent want to open? Points classified by 3D degree: corner(deg3, x8), edge(deg4, x24), face(deg5, x24), interior(deg6, x8).

## Result: essentially uniform
| class | count | mean policy / point |
|---|---|---|
| corner | 8 | 0.01540 |
| edge | 24 | 0.01531 |
| face | 24 | 0.01544 |
| interior | 8 | 0.01545 |

All ~0.0154 = 1/65 (uniform). Total mass tracks count, not position type. The net opens **without positional preference** — corner, edge, face, and interior are valued near-equally.

## Finding (contrast with 2D Go)
In 2D Go the opening strongly prefers corners > edges > center (corners need fewer stones to make territory). **In 3D 4^3 Go that structure is absent** — the strong agent's opening prior is flat across the corner/edge/face/interior hierarchy. This fits the earlier geometry result (3^3 ~ 2D but 4^3's degree-6 interior dominates as N grows) and the small-board, blowout-dominated character of 4^3: early positional value is roughly uniform.

## Caveat
The distilled policy is diffuse in general (holdout argmax-acc ~0.12), so 'no preference' partly reflects a high-entropy policy. A sharper test (MCTS visit-count distribution on the opening, or value-of-single-stone-by-position) is a cheap follow-up. But the per-point means being indistinguishable across classes is a genuine signal of weak opening positional structure on 4^3.

Artifact: experiments_q8_positional.json.