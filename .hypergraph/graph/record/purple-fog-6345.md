---
node_id: 73d510e5-875e-59b2-ad07-f4711ee0b748
slug: purple-fog-6345
title: 'a3go: autonomous three dimensional baud research campaign'
created_at: '2026-06-07T11:30:28.244143+00:00'
parents: []
summary: 'Campaign root for autonomous 3D-Go (N^3, 6-connectivity) research: train a strong agent and characterize how the game differs from 2D, derived empirically from the vendored engine + self-play stack.'
flywheel:
  node_id: 73d510e5-875e-59b2-ad07-f4711ee0b748
  slug: purple-fog-6345
  revision: 3
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: ff5b4bfe4e87744bda6e62270bfce43b719cee710555276891b642bb938347c6
---
# a3go — autonomous 3D-Go research campaign

**Can we train an AI to effectively play a three dimensional version of the classic board game go?**

3D Go plays the **identical** Go rules (liberties, capture, suicide, superko, area scoring) on an **N×N×N cubic lattice**, where an interior point has up to **6 neighbors** (±x,±y,±z) instead of 4. This graph is the durable system of record for an autonomous campaign on that game.

## Central claim
> We can train a strong agent to play 3D Go on an N³ 6-liberty board, and in doing so characterize how the game differs from 2D.

There is **no human 3D-Go expert pool**, so "strong" is defined operationally (success bar below).

## Success bar
- **Beats baselines** — decisively beats uniform-random and a fixed-strength classical baseline (MCTS at a set playout budget), over color-balanced matches with CIs.
- **Rising self-play strength** — successive agents beat their predecessors (monotone within noise).
- A result "counts" only when reproducible from a seed and backed by a committed Flywheel node with its data artifact attached.

## Open questions (posed without answers — derive each by running code)
- **Q1 — Fair komi.** What komi balances the game per board size? Does win-rate-fair agree with margin-fair? How precisely can it be pinned, and what limits precision?
- **Q2 — Board sizes.** Of 3³/4³/5³/7³/9³, which are trivial, which decisive vs draw-prone, how does length scale, and which are computationally tractable for self-play here?
- **Q3 — Tactics under 6-connectivity.** Do classic 2D tactics (the ladder canonically) survive? Which carry over, which break, and why?
- **Q4 — Life & death.** What is the analogue of two-eye life on a 6-neighbor lattice? Minimum eye space for life? Does seki occur, and how often? Harder or easier to read than 2D?
- **Q5 — Mechanical oddities.** A catalog of ways 3D Go behaves unlike 2D: termination behavior, ko/superko frequency, value of corner/edge/face/interior, capturing races, naive-policy behavior.

## Budget posture (held for the whole campaign)
**$0 / local-only.** No managed/cloud compute, grants, or leases. The local box (RTX 5090, 16c/32t Ryzen 9950X, ~60 GB RAM) is free and is to be exploited (parallelize self-play across cores; GPU reserved for a deferred neural phase). If a question genuinely *needs* managed compute, that is a finding to report — not a reason to spend.

## Provenance
Engine + self-play vendored from `goban` (3D-Go fork), now owned by a3go. Engine validated at campaign start: **48/48 checks pass**; `npm run checks` clean.