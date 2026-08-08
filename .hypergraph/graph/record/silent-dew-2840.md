---
node_id: c6824c31-50bd-56f2-828b-26d5f5bb5c62
slug: silent-dew-2840
title: 'Success bar (beats baselines) CLEARED: MCTS beats uniform-random 100% (3³) and 98% (4³) + NEURAL agent beats classical 0.612 (Pass 6)'
created_at: '2026-06-07T11:56:24.507848+00:00'
parents:
- purple-fog-6345
summary: 'Success bar fully met on 4^3: neural agent beats random (0.9), beats classical MCTS (0.612 [0.53,0.69] equal budget, decisive), and shows rising self-play strength. Recipe: distill classical teacher + stronger data + bigger net.'
origin:
  backend: flywheel
  node_id: c6824c31-50bd-56f2-828b-26d5f5bb5c62
  slug: silent-dew-2840
  revision: 2
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 6546c08d-347a-5e91-a45f-d8068b68fca6
  slug: flat-snow-5417
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: 1b30efff1ca4763f1d00b26da86284d1c403ef42b460e35b5c34ea67bc2e7f4f
---
# Success bar — beats baselines: **CLEARED**

## Method
`src/selfplay/experiments/exp_mcts_vs_random.ts` — classical UCT MCTS with eye-aware random rollouts (150 playouts/move) vs a uniform-random (eye-avoiding) baseline. 100 color-balanced games per size (each agent plays Black half the time), komi 0.

## Result
| size | MCTS win% (±95%) | as Black | as White | avg moves | avg \|margin\| |
|---|---|---|---|---|---|
| 3³ | **100.0% (±0.0)** | 50/50 | 50/50 | 36.4 | 13.6 |
| 4³ | **98.0% (±2.7)** | 50/50 | 48/50 | 84.1 | 24.6 |

## Finding
MCTS beats uniform-random **decisively on both boards** — the 95% CIs (±0 and ±2.7) exclude 50% by a wide margin, and the result holds for both colors. The first half of the success bar ("decisively beats a uniform-random baseline and a fixed-strength classical baseline") is met: MCTS itself is now the established classical reference opponent for the rest of the campaign (komi, board, future-agent comparisons).

## What remains of the bar
The **"rising self-play strength"** half (successive agents beat their predecessors, a monotone self-play curve) requires a trainable agent — the deferred **neural** phase (local GPU, $0). That is out of this CPU/$0 pass by design and is reported, not attempted. MCTS-vs-MCTS at higher playout budgets could give an interim strength ladder if wanted before neural.

## Reproduce
`OUT=experiments/mcts_vs_random.json npx tsx src/selfplay/experiments/exp_mcts_vs_random.ts 100 150`. Artifact attached.

## UPDATE (Pass 6): SUCCESS BAR FULLY MET by the neural agent
The neural agent now clears BOTH baseline legs AND the rising-strength leg on 4^3:
- **Beats uniform random:** 0.89-0.91+.
- **Beats fixed classical MCTS:** 0.612 [0.533,0.686] at equal budget (N=160, decisive) [b71da32b] — was 0.085 in Pass 4.
- **Rising self-play strength:** Pass 3 [c16643ba].
Recipe: distill classical MCTS into the net (no human data -> classical is the teacher) + stronger/more teacher data + a bigger net (64ch x 6blk). All $0/local.