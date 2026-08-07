---
node_id: b08727b4-5be8-58d2-a2a6-e747fce437de
slug: noisy-dust-7661
title: SEARCH-2 — Subtree value-bias correction (3×3×3 local-pattern buckets) [MED, ~30–60 Elo]
created_at: '2026-06-09T07:00:08.916608+00:00'
parents:
- divine-thunder-7666
- empty-lab-3357
- proud-king-2753
summary: 'Implement KataGo''s subtree value-bias correction adapted to 3D: bucket tree nodes by their local 3×3×3 pattern, learn each bucket''s systematic value bias online, and subtract it during search. KataGo banks 30–60 Elo. Extends PROOF-1 ladder 3ac354fd and ALGO-1 Gumbel 4cf07501 (both search-side).'
flywheel:
  node_id: b08727b4-5be8-58d2-a2a6-e747fce437de
  slug: noisy-dust-7661
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 1726ca3845116ecd529b4827d8a8f7d59cfc51c043eefe7254cd406cb009e16f
---
# SEARCH-2 — Subtree value-bias correction (3×3×3 local-pattern buckets) [MED, ~30–60 Elo]

## Objective
Port KataGo's **subtree value-bias correction** to 3D: hash each tree node by its **local 3×3×3 neighborhood pattern**, accumulate the running difference between the node's leaf value and its subtree-averaged value per bucket, and subtract that learned bias from leaf evaluations during search. A pure search-time strength add.

## Why it matters (which finding it extends)
It is a **search-only** Elo gain (no retrain): KataGo reports **+30–60 Elo** from correcting the net's systematic, locally-patterned value errors. We have an anchored Elo ladder (PROOF-1 `3ac354fd`) to measure such a delta cleanly, and a working MCTS (ALGO-1 `4cf07501`) to host it. The 3D analogue of KataGo's 2D pattern is the degree-6 local neighborhood; our geometry findings (degree-4-to-6 mix, `c85ce2bf`) make the bucket key non-trivial but well-defined.

## Implementation route
In `az.py`, add a per-bucket running bias table keyed by the local 3×3×3 pattern (with symmetry canonicalization); during backup, update bucket bias; during selection, use bias-corrected leaf value. A/B vs uncorrected MCTS on the PROOF-1 ladder at matched sims.

## Decision criterion (CI-based, n≥128)
At n≥128 on the anchored ladder: bias-corrected search gains ≥ +25 Elo over uncorrected at matched sims with non-overlapping bootstrap CIs (KataGo claims 30–60). SPRT-gate the head-to-head.

## Preconditions / risks
Search-side only; no retrain, no new infra. CPU/GPU as today. Risk: 3×3×3 pattern space is large — may need coarser buckets or hashing; gains can shrink with a strong net (measure on 4³ *and* 5³). Independent of the aux heads.

## Cost · value
MED build. Value: a clean, retrain-free Elo bump measurable on the existing ladder; banks KataGo's 30–60 Elo if it transfers to 3D.

## Expected artifacts
Bias-correction MCTS variant, an Elo-delta JSON on the PROOF-1 ladder (corrected vs uncorrected, n≥128), bucket-occupancy stats.

## Inspiration source
KataGo subtree value-bias correction (30–60 Elo). Extends PROOF-1 `3ac354fd`, ALGO-1 `4cf07501`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
