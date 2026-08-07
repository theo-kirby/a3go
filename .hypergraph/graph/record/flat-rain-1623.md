---
node_id: ba69d0a3-f344-5413-8b0f-e4d65aa947bc
slug: flat-rain-1623
title: 'Reference: online-go.com — 3D game-review / analysis UI inspiration'
created_at: '2026-06-09T07:00:03.149029+00:00'
parents:
- tiny-term-8854
- frosty-bar-2241
- mute-cloud-4824
summary: 'online-go.com is a web frontend over the same online-go/goban board we vendored. Its transferable value is the game-review/analysis UI: ownership/territory overlay, score-estimate bar, win-rate-over-time graph, move-by-move review with variation branches, and an opening/joseki explorer over an SGF-equivalent game record. Source material for TOOL-3 (3D review UI) and SCI-1 (3D opening explorer); pairs with the ownership/score aux heads (AUX-1/2) that produce the overlays.'
flywheel:
  node_id: ba69d0a3-f344-5413-8b0f-e4d65aa947bc
  slug: flat-rain-1623
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 1343c6fbdedbca1fada5851a05eaa1164021ab39f3b56710c7de78faf2fdc10c
---
# Reference: online-go.com — 3D game-review / analysis UI inspiration

[online-go.com (OGS)](https://online-go.com) is a web frontend built over the
**same `online-go/goban` board library we vendored** (see `src/engine/VENDORED.md`).
We do not want its server/social stack; the transferable value is its **game-
review / analysis UI vocabulary**, which is the natural target for a3go's 3D
tooling once a strong net + aux heads exist.

## Transferable UI concepts
- **Ownership / territory overlay** — shade each point by predicted final owner.
  In 3D this is a per-voxel heatmap; it is exactly what the **AUX-1 ownership
  head** emits, so the head and the overlay ship together.
- **Score-estimate bar** — a live area/score estimate with a fair-komi readout;
  driven by the **AUX-2 score head**. Makes 3D komi legible (our `2a2ca6b9` scar
  was that win-rate alone can't see komi).
- **Win-rate-over-time graph** — per-move win-prob curve flagging the blunders /
  swing points of a game (the net already emits a value per move via `play.py`).
- **Move-by-move review with variation branches** — step through a game, fork
  "what-if" lines, let the net analyze each — the core analysis loop.
- **Opening / joseki explorer** — aggregate many games into a browsable opening
  tree. Feeds **SCI-1** (3D opening book / center-value science).
- **SGF-equivalent game record** — OGS persists games as SGF. 3D needs an
  SGF-analogue (coordinates + captures + komi) so games are replayable/shareable;
  `play.py`'s move log is the seed of this format.

## How it maps to a3go
TOOL-1 `1f59266a` (3D voxel/slice renderer) and TOOL-2 `742a0aab` (`play.py`
human CLI) already render boards and read out policy/value. The missing layer is
**review/analysis**: overlays from the aux heads + a navigable record. That is
**TOOL-3**. The opening-explorer half is **SCI-1**.

## What does NOT transfer
The OGS server, accounts, matchmaking, ranking ladder, and chat — all out of
scope for a $0/local research tool. We borrow the *visual grammar*, not the app.

Related: hub `e917c9e4`, TOOL-1 `1f59266a`, TOOL-2 `742a0aab`, KataGo ref (aux
heads), autogo `b4fd8252`.
