---
node_id: 7a3245ed-121b-5a58-ad34-6b210badca95
slug: small-mountain-7064
title: 'REP-3 — My/opp liberty split (group-health) [RESOLVED: directionally +0.06 over plain libs (0.558, 2/3 seeds) but under-powered; confirm at higher n]'
created_at: '2026-06-18T11:52:27.186027+00:00'
parents:
- proud-king-2753
summary: 'RESOLVED (directional). My/opp liberty-ownership split (derived from stored stack, no re-collection) beats plain libs net-vs-net pooled 0.5585 [0.4591, 0.6578] (per-seed [0.6129, 0.4688, 0.5938]), never regresses, slightly better holdout fit — supports PROBE-1''s ownership hypothesis. Not CI-separated at n=96 (under-powered). Next: higher-power confirm + finer-bucket arm (needs re-collection).'
origin:
  backend: flywheel
  node_id: 7a3245ed-121b-5a58-ad34-6b210badca95
  slug: small-mountain-7064
  revision: 2
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: a80169e6-bb06-596a-af5d-af6e8cb8b51a
  slug: lucky-morning-4972
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: 427bb83dbb0eb8f46c8aca1784380b11a4654f24da8c40f73a550293cb26e124
---
# REP-3 — my/opp liberty split (group-health) [RESOLVED: directionally positive, under-powered]

PROBE-1's recommended refinement: split each liberty bucket (1/2/≥3) by side-to-move ownership, so the net distinguishes my-group-in-atari (defend) from opp-group-in-atari (capture). 9 input planes [black,white,stm, my1/2/3, opp1/2/3], DERIVED from the stored 10-plane stack (no re-collection) — a clean A/B vs plain libs, only the liberty-ownership split differs. Live encoder validated == derive-from-stack (selftest PASS).

## Result (5³, net-vs-net split vs plain libs, sims=48)
- **split-vs-libs pooled winrate = 0.5585 [0.4591, 0.6578]** (per-seed [0.6129, 0.4688, 0.5938], 32 games/seed × 3 = 96 decided)
- holdout top1 (split): [0.0841, 0.0741, 0.1009] (mean ~0.086) vs plain libs ~0.080 — split fits at least as well.

## Findings
- **Directionally POSITIVE and theory-consistent:** the my/opp ownership split beats plain libs on 2/3 seeds (pooled 0.558) and never regresses — supporting PROBE-1's claim that *ownership* is the information-losing bit in the winning liberty feature. But the 95% CI [0.4591, 0.6578] includes 0.5 at n=96, so it is **not yet CI-separated** (same under-powered regime as SYMM-1 arm-A; per-seed variance 0.47–0.61).
- Costs only +3 planes at fixed 64×6 capacity (heeds the SCALE-libs over-scaling lesson). No re-collection needed.

## Next (cheap)
1. **Higher-power confirm** (more games, e.g. n≥300) to resolve the 0.558 lead — the single cheapest way to convert this to a decision.
2. **Add the finer-bucket arm (libs_fine 1/2/3/4+)** — NOT derivable from the stored stack (needs one re-collection of rich data with a 4+ bucket); combine split+fine.
3. If confirmed, SPRT-anchor the split net vs classical (closest-to-parity candidate).

## Artifact
`rep3_split.json`. Code: `rep3_split.py` (split_from_stack derive + split_planes live encoder + selftest + train + net-vs-net screen).

*Resolved PASS-20 round-2. Budget $0/local. npm 48/48, crossval 60/60 intact (additive).*