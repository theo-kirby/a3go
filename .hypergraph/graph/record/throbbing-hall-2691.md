---
node_id: 5e34766d-c790-54a6-a98c-29b2fdbf7bbb
slug: throbbing-hall-2691
title: SCIENCE-1 — 3D opening theory & the value of the center / third dimension [MED]
created_at: '2026-06-08T06:51:17.098590+00:00'
parents:
- long-king-8643
- mute-cloud-4824
summary: On 4^3 the champion net has NO opening positional preference (corner=edge=face=interior), unlike 2D Go. Test whether that holds on 5^3/7^3/9^3, extract the strong net's actual opening moves, and quantify whether the high-liberty 3D center is genuinely more valuable. A core 'how is 3D Go different from 2D' result the thesis explicitly asks for.
origin:
  backend: flywheel
  node_id: 5e34766d-c790-54a6-a98c-29b2fdbf7bbb
  slug: throbbing-hall-2691
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: b2ca7249-d21f-547e-b6a7-06ecdc890d86
  slug: bitter-firefly-6962
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: 0b83eb16561d7ec9f9c05ccd2549e7a8cd62a8cdbc8841eef7f08efd7d986af3
---
# SCIENCE-1 — 3D opening theory & value of the center [MED]

## Why
A central thesis question is *how 3D Go differs from 2D*. One sharp Phase-2 finding: the champion net shows **no opening positional preference on 4^3** — corner, edge, face, interior all ~uniform [853d7c2c] — unlike 2D Go's strong corner-first theory. Is that a 4^3 small-board artifact or a genuine 3D phenomenon? In 3D the interior has degree 6 vs a 2D plane's degree 4, and corners are rarer by volume [c85ce2bf] — so the *opposite* of 2D (center-favoring) is plausible on bigger boards.

## Approach
- Re-run the positional-value probe (Q8 method [853d7c2c]) on 5^3, 7^3, 9^3 with the strongest available net + search.
- Extract the net's **actual opening move distribution** (policy heatmaps over the lattice) and self-play opening trees — is there an emergent 3D "joseki" / preferred first region?
- Tie to geometry: correlate move value with degree / distance-from-center / face-vs-interior, controlling for board size.

## Decision criterion
A characterized opening-preference-vs-board-size curve (does center-favoring emerge as N grows?) with the net's opening heatmaps as artifacts — a concrete "3D opening theory differs from 2D as follows" statement.

## Preconditions / risks
Needs a *strong* net per size (so depends on the strength track) and INFRA-1 for big-board search. Risk = weak nets give uninformative uniform heatmaps (the Pass-2 holdout-accuracy lesson [dcd0a5db]) — only read this off a net that clears the strength bar. $0/local. Continues [853d7c2c, c85ce2bf].