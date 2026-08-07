---
node_id: 4e63c2d6-ce9f-5b7f-8b28-b5abb1058db9
slug: dry-glade-4547
title: 'DATA-1 — Hard-position mining: reweight distillation toward net↔teacher disagreement [data-quality lever, cheap train]'
created_at: '2026-06-18T12:25:09.676561+00:00'
parents:
- proud-king-2753
summary: 'PASS-15 concluded the 5³ lever is DATA QUALITY, not more self-play. Test it directly: reweight (or oversample) the distill set toward positions where the net most disagrees with the teacher''s policy/value (high-loss / high-KL), retrain, and net-vs-net. A cheap, on-thesis data-quality bet that needs no new self-play. Bridges to the LD-3 tsumego hard-set.'
flywheel:
  node_id: 4e63c2d6-ce9f-5b7f-8b28-b5abb1058db9
  slug: dry-glade-4547
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 47aa746a122b932804560a04119f301589cf9d961a914bcedb4b733a728ece9f
---
# DATA-1 — Hard-position mining for distillation

## Objective
Improve the distilled net by curriculum/reweighting on the EXISTING data rather than collecting more: score each training position by net↔teacher disagreement (policy KL and value error of a baseline net), then retrain with high-disagreement positions upweighted/oversampled. Measure net-vs-net vs the uniform-weighted baseline.

## Why it matters (which finding it extends)
PASS-15 (`b3ea0b95`) found that more frozen-net self-play does NOT lift absolute 5³ strength — the lever is signal richness / DATA QUALITY. Hard-example mining is the most direct, cheapest test of that thesis: same games, same net, just a smarter sampling distribution over the positions we already have. KataGo and modern distillation both rely on it. Complements the input-representation wins (ARCH-3) on the orthogonal data axis.

## Implementation route
Train-side only, reuse train_arch3. Pass 1: forward a baseline libs net over the distill set, record per-position policy-KL(teacher‖net) + value error. Pass 2: retrain with a sampling weight monotone in that score (or a hardness curriculum). Optionally fold in the LD-3 solved tsumego as guaranteed-hard positions. Net-vs-net the result vs the uniform baseline.

## Decision criterion (CI-based, n≥128)
net-vs-net: hard-mined net CI-separated above the uniform-weighted libs net at n≥128/3-seeds. Negative is also decisive (data reweighting is not the 5³ lever — sharpens PASS-15).

## Preconditions / risks
Data + libs checkpoints exist; cheap GPU retrain (~20 min). Risk: upweighting noisy/near-terminal positions can hurt — clip weights, hold the value/policy loss mix fixed; this is a clean A/B since only the sampling weights change.

## Cost · value
CHEAP train. High value: the most direct test of the PASS-15 data-quality thesis, on the existing data, no new self-play.

## Expected artifacts
`data_hardmine.py` (scorer + weighted trainer), hard-mined checkpoints, net-vs-net screen JSON vs uniform baseline, a hardness-distribution plot.

## Inspiration source
Hard-example mining / prioritized replay; KataGo data curricula. Extends PASS-15 `b3ea0b95`, ARCH-3 `bcf93cd3`; can consume LD-3 hard positions.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20 batch-2 (3D tactical/positional knowledge axis). Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*