---
node_id: f69c2fa1-cbbb-5a25-be52-d02d04c6f686
slug: restless-meadow-9547
title: Python 3D-Go engine port cross-validated 60/60 vs the TS reference (3³ and 4³)
created_at: '2026-06-07T12:59:20.815513+00:00'
parents:
- crimson-frog-9812
summary: 'Milestone 2/4. A NumPy 3D-Go engine (a3go_engine.py) reproduces the TS reference engine exactly: replaying TS-dumped seeded random games, the Python Tromp-Taylor breakdown matches field-by-field on 60/60 games at both 3³ and 4³. Fast self-play substrate for neural training is ready and trustworthy.'
origin:
  backend: flywheel
  node_id: f69c2fa1-cbbb-5a25-be52-d02d04c6f686
  slug: restless-meadow-9547
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: b3f9de46-d081-576e-99b1-dde5ee0c060c
  slug: royal-glitter-5684
  revision: 0
  pushed_at: '2026-08-08T10:01:49+00:00'
  content_sha256: ea7ac37a16aedfdb429bdf273ee63aca111a8553fe5a28806012e15352d10147
---
# Phase 2 milestone 2 — Python engine port + cross-validation

## What was done
- Ported a minimal 3D-Go engine to NumPy (`neural/a3go_engine.py`): 6-neighbor topology, liberties/capture via flood fill, capture-takes-priority over suicide, suicide rejection, **positional superko** (PSK, side-to-move excluded), and Tromp-Taylor area scoring with komi to White.
- Cross-validation harness: `dump_games.ts` plays seeded uniform-random games in the **TS** engine and records the exact move list + Tromp-Taylor breakdown; `crossval.py` replays those moves in the **Python** engine and compares every score field.

## Result
| board | games | matched | seed |
|---|---|---|---|
| 3³ | 60 | **60** | 777 |
| 4³ | 60 | **60** | 12345 |

Every recorded move is legal in the port and the final {blackStones, whiteStones, blackTerritory, whiteTerritory, neutral, diff, winner} matches the TS engine exactly. The port is behaviorally equivalent to the 48/48-tested reference, so neural self-play data generated with it is trustworthy.

## Why this design
Self-play needs the engine in the training language (Python) for speed/batching; calling TS per move would be far too slow. Cross-validation against the proven TS engine guards against silent rule bugs that would corrupt training.

## Reproduce
`npx tsx src/selfplay/experiments/dump_games.ts 4 60 12345 > neural/fixture_4.json` then `uv run --directory neural python crossval.py fixture_4.json`. Artifact attached.