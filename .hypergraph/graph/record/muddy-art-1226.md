---
node_id: 5b0393b7-72f1-5dc1-88fe-f7a56c1cccdc
slug: muddy-art-1226
title: SCI-1 — Center/positional value + 3D opening explorer (joseki book) [MED, after strong net]
created_at: '2026-06-09T07:00:16.870666+00:00'
parents:
- throbbing-hall-2691
- long-king-8643
- proud-king-2753
summary: 'Mine a strong net''s self-play for 3D opening theory: does the third dimension create a center/interior preference (2D Go opens in corners; our 4³ net showed NO preference, 853d7c2c)? Build a browsable 3D opening explorer / joseki book. Extends SCIENCE-1 5e34766d and Q8 853d7c2c.'
flywheel:
  node_id: 5b0393b7-72f1-5dc1-88fe-f7a56c1cccdc
  slug: muddy-art-1226
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 70a985636f0bc189de0ba1ee2366946749b85ada33c42b537aedf191e0325477
---
# SCI-1 — Center/positional value + 3D opening explorer (joseki book) [MED, after strong net]

## Objective
Characterize **3D opening theory**: does the extra dimension give the **center/interior** (or any region) systematic value, and what are the recurring early-game shapes? Build a **browsable 3D opening explorer / joseki book** aggregating a strong net's self-play.

## Why it matters (which finding it extends)
2D Go opens in the corners (most territory-efficient); our champion 4³ net showed **no positional opening preference** (corner≈edge≈face≈interior, `853d7c2c`) — a genuine 3D oddity worth nailing down on bigger boards where the degree-6 interior dominates (`c85ce2bf`). SCIENCE-1 `5e34766d` poses the value-of-the-third-dimension question; this node answers it empirically with a *strong* net and packages the result as an explorer (online-go-style opening tree) — a legible science artifact. Best **after** a stronger net exists (AUX/ARCH), so the openings reflect skill not noise.

## Implementation route
Generate many strong-net self-play games per board size; aggregate first-N-move frequencies by region (corner/edge/face/interior, and center-distance); test for a preference vs uniform; build an opening-tree explorer (move → frequency → continuations) over the SGF-equivalent record (TOOL-3 format). Compare 4³ (`853d7c2c`) to 5³/7³.

## Decision criterion (CI-based, n≥128)
At n≥128 games per size: a statistically significant regional opening preference (or its confirmed absence) per board size, with CIs — extending `853d7c2c` from 4³ to bigger boards; plus a working opening explorer. Criterion: preference test resolved with CI, explorer renders real games.

## Preconditions / risks
Needs a **strong net** (gate on AUX/ARCH landing) + TOOL-3's record format for the explorer. GPU for self-play. Risk: 'opening preference' is sensitive to temperature/noise (control the self-play settings); low standalone priority until the net is strong.

## Cost · value
MED build. Value: a flagship 3D-science result (is the center special in 3D Go?) + a reusable opening explorer; legibility payoff.

## Expected artifacts
Opening-frequency-by-region dataset (4³/5³/7³, n≥128), a center-value figure, and an interactive/rendered 3D opening explorer.

## Inspiration source
online-go.com opening/joseki explorer + KataGo opening analysis. Extends SCIENCE-1 `5e34766d`, Q8 `853d7c2c`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
