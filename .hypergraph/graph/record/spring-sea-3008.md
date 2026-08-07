---
node_id: a9982d50-b5d5-5639-bdf1-70d0f4de1b45
slug: spring-sea-3008
title: '3DSCI-2 — Tactical-motif census across board sizes [RESOLVED: ''98% ko'' prior overstated (18–32%); ko-ban density <0.1% of empties → explains P18 ko-ban null]'
created_at: '2026-06-18T11:52:27.875751+00:00'
parents:
- proud-king-2753
summary: 'RESOLVED. Engine-only motif census 3³–7³: single-capture→ko-ban rate only 18–32% (not ~98%, falsifies the strong reading of 31dae43b); ko-ban density <0.1% of empty cells and falls with size → explains the PASS-18 ko-ban-plane null. Captures/self-atari fall with board size; liberty/atari motifs common (5–14%/move). 7³ classical self-play ~prohibitive (re-confirms data-gen wall).'
flywheel:
  node_id: a9982d50-b5d5-5639-bdf1-70d0f4de1b45
  slug: spring-sea-3008
  revision: 4
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 042460d7ccb152fbe7363aff3a0d5b868d54936d7debf508fea15746861655b1
---
# 3DSCI-2 — tactical-motif census across board sizes [RESOLVED]

Engine-only classical self-play census (3³/4³/5³/7³). Motif rates are playout-strength-robust; n=7 at fewer games (classical self-play cost ~prohibitive at 7³ — itself a finding).

## Result (per board size 3³ / 4³ / 5³ / 7³)
- mean game length: 36.2 / 82.4 / 130.4 / 352.4
- capture rate / play: 0.1087 / 0.0818 / 0.0481 / 0.0465
- mean capture size: 2.917 / 3.254 / 2.083 / 1.612
- **single-capture → immediate ko-ban rate: 0.3167 / 0.2281 / 0.2366 / 0.1828**
- self-atari rate / play: 0.1056 / 0.0781 / 0.0413 / 0.0267
- atari-giving rate / play: 0.1398 / 0.0922 / 0.0674 / 0.062
- **ko-ban density / empty cell: 0.00105 / 0.00058 / 7e-05 / 4e-05**
- terminal neutral (seki/dame proxy): 2.5 / 2.75 / 5.91 / 5.75

## Findings (decisive)
1. **The "~98% of single-stone captures trigger a superko ban" prior (`31dae43b`) is dramatically OVERSTATED in actual play.** Only **18–32%** of in-game single-stone captures create an immediate ko-ban, and the share FALLS with board size (0.32→0.18 from 3³→7³).
2. **Ko-forbidden recaptures are vanishingly rare per position:** ko-ban density is **<0.1%** of empty cells and collapses with size (0.00105→0.00004). This directly EXPLAINS the PASS-18 ko-ban-plane falsification (`bcf93cd3`): the plane the net saw was almost all-zeros, so it could carry no signal at 5³.
3. **Captures, self-atari and atari-giving all FALL with board size** (capture/play 0.11→0.05) — bigger boards are less tactically dense per move, even as games get much longer (game length 36→352). Liberty/atari motifs (5–14% of moves) are common enough to matter — consistent with liberty planes being the lever, ko-ban not.

## Why it matters
Turns feature selection from anecdote into data: liberty/capture features are well-supported by motif frequency; ko-ban is empirically negligible at the sizes we train. The 7³ classical-self-play cost (8 games ≈ 24 min) re-confirms the data-gen wall that gates the 7³ program.

## Artifact
`motif_census.json` (full per-size counters). Code: `motif_census.py` (capture-aware ko logic shared with input_planes; sub-sampled koban-density scan).

*Resolved PASS-20 (breadth pass, cheap-first). Budget $0/local. Engine/tests untouched (additive probe scripts only).*