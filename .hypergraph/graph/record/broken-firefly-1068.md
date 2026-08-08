---
node_id: e5b977dc-fac7-5f66-bb41-06ffc4817b1f
slug: broken-firefly-1068
title: Q10 — Rising self-play strength curve (2nd half of the success bar)
created_at: '2026-06-07T12:52:33.019103+00:00'
parents:
- crimson-frog-9812
- silent-dew-2840
summary: 'Extends the success bar with Phase 2: successive neural generations should beat their predecessors (monotone within noise). The classical phase cleared ''beats baselines''; this clears ''rising strength''.'
origin:
  backend: flywheel
  node_id: e5b977dc-fac7-5f66-bb41-06ffc4817b1f
  slug: broken-firefly-1068
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 0c80ac4f-8c52-57ac-9789-b355ec10544a
  slug: tight-wind-7318
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: 6d5e5a9ceaa0029de428857c1c434fbcb3f64f7a84a32a3cad3a9271da6f4ca3
---
# Q10 — Rising self-play strength curve (← success bar, ← Phase 2)

The success bar has two halves; pass 1 cleared **beats baselines** (MCTS 100%/98% vs random). This is the **rising self-play strength** half.

## What to answer
- Do successive trained generations beat their predecessors with win-rate CI excluding 50% (a monotone-within-noise strength curve)?
- Does the neural agent beat classical MCTS at equal playout budget?

## Method
Generation-over-generation round-robin (color-balanced, CIs); plot Elo/win-rate vs generation. Decision: monotone increase within noise + beats classical MCTS.

Status: BLOCKED on Phase 2 (#3–#4).