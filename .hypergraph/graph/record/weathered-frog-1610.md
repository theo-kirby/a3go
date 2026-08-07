---
node_id: 31dae43b-f212-51b4-a9d9-2f08d6e6fa70
slug: weathered-frog-1610
title: 'Ko is ubiquitous in 3D: ~98% of single-stone captures trigger a superko ban; ko frequency rises with board size'
created_at: '2026-06-07T13:31:23.042813+00:00'
parents:
- tiny-night-5466
summary: Instrumented random self-play (200 games/size). Captures/game 6.3→10.8→13.8 (3³→4³→5³); single-stone captures 3.3→6.3→8.9/game; and ~98% of single-stone captures are immediately superko-illegal to recapture (652/665, 1235/1254, 1766/1782) — i.e. nearly every single-stone capture is a real ko. Ko fights scale up with the board.
flywheel:
  node_id: 31dae43b-f212-51b4-a9d9-2f08d6e6fa70
  slug: weathered-frog-1610
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 77a762934e2f02b3c93849f50fa571d0a9ace26390bab1307b7368f2e8e3a8ae
---
# Q7 — Ko / superko frequency & dynamics in 3D

## Method
`src/selfplay/experiments/exp_ko.ts` — seeded uniform-random self-play (200 games/size), instrumenting every move (public API only): capture-size via opponent stone-set diff, and **ko bans** = after a single-stone capture, is the opponent's immediate recapture at the vacated point positional-superko-illegal?

## Result
| size | captures/game | single-cap/game | koBans/game | single | multi | koBans |
|---|---|---|---|---|---|---|
| 3³ | 6.30 | 3.33 | 3.26 | 665 | 596 | 652 |
| 4³ | 10.84 | 6.27 | 6.18 | 1254 | 914 | 1235 |
| 5³ | 13.78 | 8.91 | 8.83 | 1782 | 973 | 1766 |

## Findings
1. **Ko is everywhere.** ~**98%** of single-stone captures (652/665, 1235/1254, 1766/1782) are immediately followed by a positional-superko ban on the recapture — exactly the basic ko: recapturing would recreate the prior position, so it is forbidden. The single-stone ko mechanic carries into 3D unchanged and is extremely common.
2. **Ko scales with the board.** Captures/game and ko bans/game both grow steadily with N (3.3→6.3→8.9 single-captures/game for 3³→4³→5³) — more contact, more single-stone captures, more kos.
3. **The ~2% non-bans** are the interesting tail (665−652=13 on 3³): single-stone captures whose 'recapture' is actually legal — snapback-like shapes where retaking captures more than one stone or yields a new position. A natural sub-probe for 3D snapback.

## Connects to
Confirms a Q5 catalog entry (ko/superko behavior) empirically and complements the engine's positional-superko (PSK) implementation. Multi-stone captures (596/914/973) are common too — capturing races are frequent in 3D, a thread for Q8/Q6.

## Reproduce
`OUT=experiments/ko.json npx tsx src/selfplay/experiments/exp_ko.ts 200 "3,4,5"` (deterministic). Artifact attached.