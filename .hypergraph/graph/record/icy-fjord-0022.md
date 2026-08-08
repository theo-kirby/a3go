---
node_id: 11bba26c-bc3f-573c-b82e-5f20699215b7
slug: icy-fjord-0022
title: 'GEO-1 precondition cleared: (n,n,1) is exactly 2D Go; (3,3,1) cell-type anchor measured'
created_at: '2026-08-07T21:05:57+00:00'
parents:
- still-recipe-4954
summary: ''
flywheel:
  node_id: d978be15-f951-5d9f-946d-1bef77ff8c59
  slug: proud-poetry-6487
  revision: 2
  pushed_at: '2026-08-08T10:06:14+00:00'
  content_sha256: c54e9a8efcc020e97747eff6b7698cf576df10c630d3de29ea8411f3e3fac560
---
## What

Executed the GEO-1 precondition probe: verified that the engine on depth-1 boards
(n,n,1) reproduces 2D Go exactly, and took the first d=1 boundary measurement of the
dimensionality ladder on (3,3,1). New experiment script
`src/selfplay/experiments/exp_2d_boundary.ts`; evidence JSON committed at
`experiments/2d_boundary.json`.

## Why

The GEO-1 design brief (parent, still-recipe-4954) requires "verify (n,n,1)
reproduces a 2D engine on a known 2D position first" before any (n,n,d) ladder work,
naming d=1 superko/scoring edge cases as the risk and a "2D-boundary validation
note" as an expected artifact. This clears that precondition at $0/local, CPU-only
(~2.5 min single-threaded on a laptop), and banks the ladder's 2D endpoint — where
Go is solved on 3x3 — as a known-answer calibration anchor.

## Method

`OUT=experiments/2d_boundary.json npx tsx src/selfplay/experiments/exp_2d_boundary.ts 128 512`
(seed 20260807). Three parts:

- A, structural: exhaustive equivalence of `Topology3D(n,n,1)` against the
  independently-written `Topology2D(n,n)` — point iteration order, flat idx mapping,
  and per-point neighbor sets — for n in {1..9, 19} (646 points).
- B, rules: known-answer 2D checks on `BoardState3D(n,n,1)`: liberty counts
  corner/edge/center = 2/3/4; corner capture + prisoner accounting; suicide
  rejection on (1,1,1) and in a 2D corner; the classic 2D ko (immediate recapture
  must throw positional-superko, retake legal after an elsewhere exchange); a
  hand-scored Tromp-Taylor position (B 15 / W 1 / diff +14 / 9 neutral); empty board
  all-neutral draw at komi 0.
- C, measurement: (3,3,1), komi 0, MCTS(512) vs MCTS(512), 128 games/arm, four arms:
  free first move, and Black's first move forced by cell type — center (1,1), edge
  (1,0), corner (0,0). Wilson 95% CIs. Anchor: 2D 3x3 Go is solved (perfect play =
  Black takes all 9, +9, tengen first).

## Result

**16/16 boundary checks pass** (646 topology points identical; every rule check
known-answer correct): depth-1 boards ARE 2D Go in this engine — no d=1
superko/scoring edge case exists. GEO-1's ladder may treat d=1 as a valid 2D
endpoint with no engine work.

Measurement, Black win rate [95% CI], mean diff, +9 whole-board sweeps (of 128):

- free:        128/128 = 100% [97,100], +6.40, 28
- center(1,1): 128/128 = 100% [97,100], +6.91, 39
- edge(1,0):   128/128 = 100% [97,100], +5.51, 44
- corner(0,0):   1/128 =   1% [0,4],    -7.13,  1

Interpretation: at the 2D boundary, first-move cell type is DECISIVE — a corner
opening flips 3x3 from certain Black win to near-certain loss (CI-separated, 100%
vs 1%), consistent with solved 2D theory and in sharp contrast to the 4-cubed
opening-uniformity result (853d7c2c / gentle-glitter-1363 lineage). Cell-type
preference therefore exists at d=1 and is gone by the 4-cubed cube: the GEO-1
ladder has a measured non-trivial endpoint, and STRAT-1's "does preference emerge
with board size" question gains a second axis — preference must also *die with
depth* somewhere on (n,n,d). Caveats: arm C values are MCTS-vs-MCTS behavioral
estimates, not perfect play (free-arm mean diff +6.40 < +9 shows MCTS(512) is not
perfect even on 3x3); the edge arm's 100% win rate does not contradict solved
theory, it reflects equal-strength self-play, not optimal punishment.

Cost: ~135 s single-threaded, CPU-only. `npm test` 48/48; `npm run checks` clean;
no engine changes (VENDORED.md untouched). Evidence: `experiments/2d_boundary.json`
(committed via a .gitignore evidence exception), script committed at
`src/selfplay/experiments/exp_2d_boundary.ts`.

## Repo

- repo: https://github.com/theo-kirby/a3go.git
- branch: main
- commit: 76db28178ace12ae979c4513744eb4b2e2b7849b

## State Impact

- target: silent-dew-3574 — new claim: depth-1 boards are exactly 2D Go — Topology3D(n,n,1) ≡ Topology2D(n,n) exhaustively (n≤19, 646 points) and 16/16 known-answer 2D rule checks (ko/superko, suicide, Tromp-Taylor) pass via exp_2d_boundary.ts; no d=1 edge cases
- target: northern-creek-9091 — GEO-1 (still-recipe-4954) precondition verified, ladder unblocked with a measured d=1 endpoint: on (3,3,1) komi 0, MCTS(512) n=128/arm, corner first move flips Black 100%→1% [CI-separated] vs center/edge/free — cell-type preference is decisive at d=1 yet absent on 4³ (853d7c2c), sharpening STRAT-1
