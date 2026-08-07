---
node_id: 0bbe92d5-3b7f-552d-866a-ea63dec0c815
slug: withered-hall-6943
title: 'TRANSFER-1 — Zero-shot cross-board transfer: does a 4³-trained net know anything about 5³? [edge hypothesis, cheap eval]'
created_at: '2026-06-18T11:52:29.201341+00:00'
parents:
- proud-king-2753
summary: 'Edge hypothesis: with a size-agnostic global-pooling head (ARCH-1), evaluate a net trained ONLY on 4³ directly on 5³ (and 5³→7³) with no fine-tuning. If transfer is non-trivial, 3D Go tactics are board-size-portable and a curriculum (small→big) could bootstrap the expensive big boards cheaply. Mostly eval; cheap.'
flywheel:
  node_id: 0bbe92d5-3b7f-552d-866a-ea63dec0c815
  slug: withered-hall-6943
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 9ec75faab36453b7b98b569efd0bc499c1bfe950cc48114219e5cfb5639cba8c
---
# TRANSFER-1 — Zero-shot cross-board transfer (4³ → 5³ → 7³)

## Objective
Test whether 3D-Go knowledge is board-size-portable: train a size-agnostic net (global-pooling head, ARCH-1) on one board size and evaluate it ZERO-SHOT on a larger size, with no fine-tuning. Quantify the strength retained (net-vs-net vs the native-size net and vs classical) as a function of the size gap.

## Why it matters (which finding it extends)
The campaign treats each board size as a fresh, expensive data-collection problem (7³ is the wall). If tactics transfer — liberties, captures, atari are locally identical regardless of board size — then a SMALL-board net is a free warm-start for big boards, turning the 7³ program from "collect from scratch" into "transfer + light fine-tune". The scaling-law node (`0bc38c41`) characterized per-size training but never tested cross-size generalization — a genuine gap.

## Implementation route
Requires a size-agnostic head (depends on ARCH-1 `5f4399f0`; global-avg-pool the trunk so the value/policy heads are board-size-independent). Train on 4³ rich-plane data, evaluate on 5³ via `screen_nvn` (net-vs-net vs native 5³ net + SPRT-anchor vs classical only if it transfers well). Then 5³→7³.

## Decision criterion (CI-based, n≥128)
n≥128: zero-shot transferred net beats RANDOM on the larger board with CI-lower>0.5 (any transfer at all), and report its net-vs-net Elo gap to the native net. Strong result = within ~1σ of native; even weak-but-positive transfer justifies a curriculum.

## Preconditions / risks
Blocked on ARCH-1 size-agnostic head (`5f4399f0`) — stage that first or build the pooling head here. Risk: policy head action-space differs by size (n³+1) — global-pool the spatial policy or use a fully-convolutional policy. Eval-heavy but cheap once the head exists.

## Cost · value
CHEAP-MED (mostly eval). High value: if positive, it is the lever that makes the 7³+ program affordable at $0/local — a structural unblock, not a marginal gain.

## Expected artifacts
Size-agnostic checkpoint, cross-board net-vs-net transfer JSON (4³→5³, 5³→7³), a transfer-vs-size-gap curve.

## Inspiration source
KataGo trains one net across 9–19 board sizes; curriculum learning. Depends on ARCH-1 `5f4399f0`; extends scaling-law `0bc38c41`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20. Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*