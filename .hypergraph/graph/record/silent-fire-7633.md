---
node_id: 719843c6-be43-513e-b212-80425af3d7ae
slug: silent-fire-7633
title: Q9 — Can a neural agent pin fair komi to ±0.5?
created_at: '2026-06-07T12:52:32.242661+00:00'
parents:
- crimson-frog-9812
- crimson-voice-3644
summary: 'Extends Q1 with Phase 2: the classical phase showed komi is variance-limited, not sample-limited. Can a lower-variance neural value head identify fair komi on 4³ to ±0.5?'
origin:
  backend: flywheel
  node_id: 719843c6-be43-513e-b212-80425af3d7ae
  slug: silent-fire-7633
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 01ab88f1-f78e-5398-894e-4e9b10051dc7
  slug: purple-snow-9217
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: bd4e30615571d61dd298628e23419b88916a62ec99ecacd82773da921cb30b04
---
# Q9 — Neural komi precision (← Q1, ← Phase 2)

The Q1 result (komi unidentifiable by win-rate on 3³; noisy mean-margin estimates on boards) concluded precision is **variance-limited**. This question tests the fix.

## What to answer
- Does the neural value head (lower variance than rollout outcomes) yield a fair-komi estimate with SE ≤ 0.5 on 4³ (and 3³/5³)?
- Do win-rate-fair and value-fair komi agree once the agent is strong?

## Method
Use the trained value net to estimate the komi at which expected score is zero, and run high-volume net-vs-net win-rate sweeps around it. Decision: SE ≤ 0.5.

Status: BLOCKED on Phase 2 (#1–#3).