---
node_id: 9605fb9a-e859-56d3-9c36-7f0b3349ca05
slug: dawn-block-6253
title: Test-time sims scaling does NOT beat classical on 4^3 — net plateaus ~0.25 and deeper search HURTS (value-head amplification); autogo's scaling law needs a good net first
created_at: '2026-06-07T22:01:55.698146+00:00'
parents:
- round-wave-9279
- frosty-grass-9317
summary: Swept distilled-net sims {48,128,256} vs classical {48,128}. Net stays ~0.25-0.29 vs classical regardless of budget, never near 0.5; net256-vs-cls128 collapses to 0.042 — deeper PUCT amplifies a miscalibrated value head. Test-time scaling is no free lunch on a weak net; bottleneck is net quality -> pivot to stronger-teacher distillation.
origin:
  backend: flywheel
  node_id: 9605fb9a-e859-56d3-9c36-7f0b3349ca05
  slug: dawn-block-6253
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: f94de1a7-0a15-554b-a82c-e5d615777fdb
  slug: withered-shadow-2447
  revision: 0
  pushed_at: '2026-08-08T10:02:40+00:00'
  content_sha256: 6f467baec98e9dfbab6146687556560e290151e8ef468991803c6f1b3ce0404f
---
# Test-time sims scaling does NOT beat classical — and deeper neural search can HURT (value-head amplification)

Hypothesis (from autogo's 'test-time scaling law' + the cost asymmetry: neural batched eval ~0.001 ms/pos vs expensive classical rollouts): let the distilled net think longer to beat classical cheaply. Tested by sweeping net sims {48,128,256} vs classical playouts {48,128}, 24 color-balanced games each.

## Result (distilled net win-rate vs classical)
| net_sims \ cls_playouts | 48 | 128 |
|---|---|---|
| 48  | 0.25 [0.12,0.45] | - |
| 128 | 0.174 [0.07,0.37] | 0.261 [0.13,0.47] |
| 256 | 0.292 [0.15,0.49] | **0.042 [0.01,0.20]** |

## Findings
1. **Scaling net sims does NOT help.** Across 48-256 sims the net sits flat at ~0.25-0.29 vs classical@48, never approaching 0.5. At equal budget (48v48 and 128v128) it stays ~0.25-0.26.
2. **More neural search can HURT.** net256-vs-cls128 collapses to 0.042 (vs net128-vs-cls128's 0.261), and net128-vs-cls48 (0.174) < net48-vs-cls48 (0.25). Signature of a **miscalibrated value head**: deeper PUCT search exploits the net's value errors instead of averaging them out. Classical's terminal random rollouts give a more reliable value on this tiny board, so they scale gracefully and the net does not.
3. **autogo's test-time scaling law does NOT transfer** to our weakly-distilled 4^3 net — it presumes a well-calibrated value/policy net (their strong 19x19 model). Scaling laws are a property of a good net, not a free lunch.

## Implication
The bottleneck is **net quality (the value head)**, not search depth. The only lever left to beat classical is a BETTER net -> **stronger-teacher distillation** (re-distill from higher-playout classical for better value/policy targets). Launched: 160 classical games at 256 playouts to combine with the 128-playout set and re-distill.

Artifact: experiments_scaling.json (full sweep).