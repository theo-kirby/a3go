---
node_id: 5f4399f0-b761-5fb5-bc8c-d6ffbbf73793
slug: tight-dust-1276
title: ARCH-1 — Global-pooling size-agnostic heads + masked multi-board-size training [MED-HIGH, keystone]
created_at: '2026-06-09T07:00:12.194941+00:00'
parents:
- bitter-unit-9524
- nameless-dream-4859
- delicate-breeze-7763
- proud-king-2753
summary: 'Make the net fully-convolutional with global-pooling value/score heads and train it on mixed board sizes (zero-pad + mask), so ONE net plays 3³→9³. The keystone build for the whole SCALE theme: SCALE-2 size-agnostic net 1e58a424, SCALE-3 curriculum adb11193, and the cross-board scaling law 0bc38c41.'
flywheel:
  node_id: 5f4399f0-b761-5fb5-bc8c-d6ffbbf73793
  slug: tight-dust-1276
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 198238d5abfd6ec987fb32ab2b4bb1c4a51d7694a566bf0cc4f632e4ee9decdf
---
# ARCH-1 — Global-pooling size-agnostic heads + masked multi-board-size training [MED-HIGH, keystone]

## Objective
Re-architect `A3GoNet` to be **fully-convolutional** with **global-average-pooling** feeding the value/score heads (no fixed-size FC), and train it on a **mixture of board sizes** via zero-pad-to-max + legality mask. Result: a single net that trains and plays across 3³→9³.

## Why it matters (which finding it extends)
Today every board size needs its own net with fixed-size FC heads — the bottleneck for the entire SCALE theme (SCALE-2 `1e58a424` size-agnostic net, SCALE-3 `adb11193` curriculum transfer). KataGo's global-pooling heads are the proven mechanism: pool spatial features to a vector before the value/score MLP, so the head is size-independent; mask + pad to mix sizes in a batch. This is the **single most reusable build** in the expansion — it unlocks curriculum transfer (small→big pretraining) and a clean way to *fit* the cross-board law `0bc38c41` with one model instead of three.

## Implementation route
Replace FC heads with global-pool→MLP; keep the trunk convolutional; add a board-mask channel and masked losses; build a multi-size data loader (pad to max, mask illegal/out-of-board cells). Train on 4³+5³(+7³) jointly; evaluate per-size strength vs the per-size dedicated nets.

## Decision criterion (CI-based, n≥128)
At n≥128: the single size-agnostic net reaches ≥ parity (CI-overlapping or better) with the dedicated per-size nets on each of 4³/5³/7³ vs classical — i.e. one net is not worse than three. Then test zero-shot/curriculum transfer to a held-out size (feeds SCALE-3).

## Preconditions / risks
Train-side rearchitecture; GPU free. Risk: global pooling can underperform size-specific FC on a *single* fixed size (the win is generality + transfer — measure both); mixed-size batching needs careful masking (validate logits are masked, not just zeroed). Keystone for SCALE-2/3.

## Cost · value
MED-HIGH build (real net surgery + data pipeline). Value: the keystone enabling one-net-all-boards, curriculum transfer, and a unified scaling-law fit — high leverage, highly reusable.

## Expected artifacts
Size-agnostic `net.py` variant, multi-size data loader, per-size strength table (one net vs three) at n≥128, a transfer-to-held-out-size probe.

## Inspiration source
KataGo global-pooling size-agnostic heads + masked multi-board-size training. Extends SCALE-2 `1e58a424`, SCALE-3 `adb11193`, scaling-law `0bc38c41`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*
