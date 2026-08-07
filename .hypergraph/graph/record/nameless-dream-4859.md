---
node_id: adb11193-0501-5e63-98a6-101ea8bc591e
slug: nameless-dream-4859
title: 'SCALE-3 — Curriculum / transfer: small->big board pretraining [MED]'
created_at: '2026-06-08T06:51:16.519532+00:00'
parents:
- mute-cloud-4824
summary: Test whether pretraining on small boards (cheap, fast) then fine-tuning on big boards accelerates reaching strength on 7^3/9^3 vs training big from scratch — a sample-efficiency lever for the expensive big-board regime. Cleanest on top of SCALE-2's size-agnostic net. Could substantially cut the cost of the genuinely-3D strength push.
flywheel:
  node_id: adb11193-0501-5e63-98a6-101ea8bc591e
  slug: nameless-dream-4859
  revision: 0
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 439b58cdc414f3e36df558ecda8f89910ae126bc8dddbcb051ef95b0813f6755
---
# SCALE-3 — Curriculum / transfer (small -> big) [MED]

## Why
Big-board data and search are the expensive part of Phase 3. If skill transfers across scale (SCALE-2), then **pretrain cheaply on 4^3/5^3, fine-tune on 7^3/9^3** should reach big-board strength with far less big-board data/search than training from scratch — a direct sample-efficiency win on exactly the costly regime, and a finding about whether 3D-Go has scale-invariant structure.

## Approach
- Use the size-agnostic net (SCALE-2) so weights port directly; otherwise transfer the conv tower and re-init heads.
- Compare three regimes to 7^3/9^3 target strength: (a) from-scratch big, (b) small-pretrain -> big-finetune, (c) joint mixed training.
- Measure big-board examples / GPU-hours to reach a fixed strength (vs classical) for each.

## Decision criterion
Curriculum (b) reaches a fixed 7^3 strength with measurably less big-board compute/data than from-scratch (a) — quantify the speedup. A null result (no transfer) is itself a statement that 3D-Go strength is scale-specific.

## Preconditions / risks
Cleanest **after SCALE-2** (size-agnostic weights). Depends on INFRA-1 for the big-board eval. Risk = negative transfer or small-board pathologies (3^3~2D, 4^3 blowouts [dcd0a5db]) poisoning the prior — start the curriculum at 5^3, not 3^3. $0/local.