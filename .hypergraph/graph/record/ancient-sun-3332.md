---
node_id: 365b153f-75e1-54ee-9344-4794604da3a4
slug: ancient-sun-3332
title: 'Reference: lightvector/KataGo — transferable methods for 3D Go (aux targets, search, architecture)'
created_at: '2026-06-09T06:55:00.378083+00:00'
parents:
- mute-cloud-4824
summary: 'Catalog of KataGo''s methods we lack, each with mechanism + claimed Elo + how it maps to a3go gaps: ownership/score/short-term/soft-policy aux heads (KataGo''s biggest accelerator; hit our komi-flat 2a2ca6b9 and policy-weak 0bc38c41 spots), optimistic policy (+40-90), subtree value-bias (+30-60), variance-cPUCT+uncertainty (~+75), playout-cap randomization, global-pooling size-agnostic heads, nested-bottleneck blocks, richer input planes (ko-ban for ubiquitous-3D-ko 31dae43b), SPRT gating. Source material for the EXPANSION direction nodes.'
origin:
  backend: flywheel
  node_id: 365b153f-75e1-54ee-9344-4794604da3a4
  slug: ancient-sun-3332
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 9bf431c9-dc5f-58d7-a8d6-62108086a51a
  slug: rapid-forest-6634
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: df19e388ee495114e645d74cfb924e759bd54c6fad699d52a8739f7f8754039d
---
# Reference: lightvector/KataGo — transferable methods for 3D Go

[github.com/lightvector/KataGo](https://github.com/lightvector/KataGo) — the
strongest open AlphaZero-lineage Go engine, and the richest external seam for
this campaign. KataGo's own papers/release-notes attach **claimed Elo** to most
of its tricks, and several map 1:1 onto a3go's confirmed weak spots. This node
catalogs the transferable methods (mechanism · claimed benefit · how it maps to
our gaps/findings). It is source material for the EXPANSION direction nodes, not
an experiment. Sister reference: autogo `b4fd8252` (research-loop framing).

Our net today (`neural/net.py:A3GoNet`) is a bare **policy+value** resnet (3
input planes B/W/stm, fixed-size FC heads, BatchNorm, no global pooling, komi not
an input). Every method below is something we *lack*.

## Auxiliary training targets (KataGo's biggest early-training accelerator)
- **Per-voxel ownership head** (predict who owns each point at game end). KataGo:
  *"immensely faster"* early learning; dense spatial signal regularizes value.
  → maps to our **policy-acc-falls-with-board-size law** `0bc38c41` (the net needs
  denser supervision than one scalar outcome) and ALGO-2 capacity `792c4ec2`.
- **Final-score + score-distribution head** (margin, not just win/loss). Gives a
  komi-sensitive, dense target. → directly answers **komi-is-unidentifiable-by-
  win-rate on 3³** `2a2ca6b9` (games are blowout-dominated so win% is flat across
  komi) and Q9 fair-komi `9a106027`.
- **Short-term value/score targets** (predict value/score a few plies ahead, not
  only the final outcome) — a bias-variance lever for value calibration; feeds
  uncertainty-aware search.
- **Soft policy target** (train policy toward the full MCTS visit distribution at
  temperature T≈4, up-weighted ~8×) **+ policy-target pruning** (drop low-visit
  junk). → our **policy is the weak head** (`0bc38c41`: acc 0.12→0.07→0.05 as the
  board grows); a softer, richer target is the obvious fix.

## Search-time methods (each banks claimed Elo)
- **Optimistic policy head** (a second policy biased toward moves that *over*-
  performed) — **+40–90 Elo**.
- **Subtree value-bias correction** (bucket positions by local 3×3 pattern, learn
  & subtract the systematic value bias of each bucket) — **+30–60 Elo**.
- **Dynamic variance-scaled cPUCT + uncertainty-weighted playouts** (exploration
  constant scales with observed value variance; playouts weighted by uncertainty)
  — **~+75 Elo**. Needs the short-term/variance targets above.
- **Playout-cap randomization** (most self-play moves cheap, a fraction expensive
  with full noise) — more/cheaper training data without hurting target quality.
- **Score-aware utility + dynamic komi at play time** (optimize a blend of
  win-prob and expected score; adjust komi so games aren't blowouts) — needed for
  honest komi/handicap evaluation; pairs with the score head.

## Self-play / exploration shaping
- **Shaped Dirichlet root noise** (concentration scaled to legal-move count) **+
  root softmax temperature** — better root exploration than our flat Dirichlet(0.5)
  in `az.py`. Compatible with autogo's *anneal-don't-fix* lesson `b4fd8252`.

## Architecture
- **Global-pooling, size-agnostic heads** (global-average-pool channels into the
  value/score heads; fully-convolutional trunk) → **one net trains/plays on many
  board sizes**. The keystone for our SCALE theme (SCALE-2 `1e58a424`, SCALE-3
  `adb11193`) and the cross-board law `0bc38c41`.
- **Masked multi-board-size training** (zero-pad to max size + legality mask, mix
  sizes in a batch).
- **Nested-bottleneck residual blocks + fixed-variance init**, and **dropping
  BatchNorm** — more capacity-per-flop and more stable training; the literal
  "scale capacity" lever PROOF-1 `3ac354fd` / PASS-15 `b3ea0b95` point to for S1.
- **Richer input planes** (move history, liberty counts, ko-ban, ladder status).
  → ko is *ubiquitous* in 3D (`31dae43b`, ~98% of single-captures trigger a
  superko ban) yet our net never sees a ko-ban or history plane.

## Methodology we can borrow
- **SPRT / sequential testing** to gate every net change cheaply and at fixed
  error rates (Leela/Stockfish-style) — directly addresses our PASS-15 scar that
  n≤32 win-rate evals (±0.16 CIs) are too noisy to gate on (`dcd0a5db`, `b3ea0b95`).

## What does NOT transfer
KataGo's human-SGF bootstrap (we have none — classical MCTS is our teacher,
`b4fd8252`), its multi-GPU cluster scale ($0/local posture), and 2D-specific
features (real ladders break in 3D, `01d82e67`).

Related: [[methodology]], hub `e917c9e4`, scaling-law `0bc38c41`, autogo `b4fd8252`.
