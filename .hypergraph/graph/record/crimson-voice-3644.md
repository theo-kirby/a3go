---
node_id: 279b3238-a1de-50ad-9239-770ebf2070a5
slug: crimson-voice-3644
title: Q1 — Fair komi in 3D Go
created_at: '2026-06-07T11:32:46.073104+00:00'
parents:
- purple-fog-6345
summary: 'Open question: what komi balances N³ Go?'
origin:
  backend: flywheel
  node_id: 279b3238-a1de-50ad-9239-770ebf2070a5
  slug: crimson-voice-3644
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 6efbfef2-714a-5639-8eee-f0182ad7a0f6
  slug: lively-disk-6022
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: d719bc855e5d3a7b0f96f4fafcc1110f30f35c701d6fcd5c3132275d801de2ed
---
# Q1 — Fair komi

Komi compensates White for Black's first move. Known for 2D 19×19 (~6.5–7.5); **unknown for N³**.

## What to answer
- Fair komi per board size (3³, 4³, …): the komi where Black's win-rate crosses 50%.
- Does **win-rate-fair** agree with **mean-score-margin-fair**, or do they diverge (a sign of coarse/blowout-prone scoring)?
- How precisely can it be pinned (±0.5?), and what limits the precision?

## Method
Equal-strength MCTS vs MCTS under a swept komi grid; Black win-rate(komi) + 50%-crossing with CI. Mean signed (blackArea−whiteArea) at komi 0 is a point estimate of fair komi.

## Testable seed (may be wrong)
First-move advantage exists and fair komi **grows with N**. Falsified if komi is flat or negative across sizes.

Status: open.