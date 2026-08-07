---
node_id: fb45781d-b620-522c-b575-768d31104001
slug: grand-spire-4624
title: Campaign methodology & tooling
created_at: '2026-08-07T20:34:44+00:00'
parents:
- royal-comet-4977
summary: $0/local, breadth-over-depth directive, 10-field design gate, measurement ladder distilled; viz/play tooling delivered; known doc-drift list recorded.
---
Status: working

## Current

- Campaign posture: $0/local-only on an RTX 5090 + 16c/32t box; the $10 managed-compute credit is untouched through 20 passes; the standing Operator directive (2026-06-18) is breadth-over-depth — cheap probes that resolve nodes and open branches, long trains staged as hypotheses with crisp criteria [rec: shiny-term-3012].
- Design gate: every direction gets a 10-field brief (objective, why, route, CI-based decision criterion at n≥128, preconditions, cost·value, expected artifacts, inspiration source) before execution [rec: proud-king-2753].
- The escalating strength-measurement ladder is the campaign's hardest-won methodology: self-play win-rate ≠ absolute strength; self-play improvement can move opposite to truth; an externally-anchored gate stops drift (validated live); net-vs-net overstates strength vs an OOD baseline even with a frozen anchor; n≈24–32 evals carry ±0.16 CIs — gate on n≥128 [rec: bold-pine-0367] [rec: noisy-bonus-3509] [rec: billowing-dew-3640] [rec: rough-paper-7328].
- Legibility tooling delivered: z-slice + voxel renderer with policy/territory overlays and a JSON→PNG figure pipeline [rec: tiny-term-8854]; terminal human-vs-agent play with the net's top-5 policy + value shown per move [rec: frosty-bar-2241].
- Known doc drift, inherited and recorded rather than silently fixed: DIRECTIONS.md's "none executed" framing predates six executed directions; AGENTS.md's "blank slate" rule is false now that results ship in-repo; CODEBASE.md still calls self-play single-threaded; neural/README still calls the neural phase a deferred stub; success-bar-v2 S1–S5 is defined only in the graph (jolly-breeze-8643), not in the repo docs [rec: lively-orchard-3365] [rec: jolly-breeze-8643].

## Negative knowledge

- [scope: sharing a GPU with external processes | confidence: medium | evidence: bold-pine-0367] Do not fight for a GPU you do not own — an external vLLM held 28/32 GB and the run placed in its headroom was OOM-killed.
- [scope: committing graph nodes without checking for an in-flight duplicate | confidence: high | evidence: wild-poetry-7539, dark-poetry-2083] A double-commit left two byte-identical M5 nodes in the graph; downstream references settled on dark-poetry-2083 — check before re-committing a payload after an ambiguous failure.

## Provenance

- lively-orchard-3365 — adoption distillation; doc-drift inventory
- shiny-term-3012 — control node: budget posture, 20 passes, breadth directive
- proud-king-2753 — design-gate convention
- bold-pine-0367 — methodology lessons ledger
- tiny-term-8854 — TOOL-1 viz + figures
- frosty-bar-2241 — TOOL-2 human-playable UX
- jolly-breeze-8643 — S1–S5 defined only in the graph
