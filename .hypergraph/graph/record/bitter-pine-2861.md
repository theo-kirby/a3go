---
node_id: faddae67-0dc0-566e-9054-9869f0e627f6
slug: bitter-pine-2861
title: 'SCALE-libs — RESOLVED P19: capacity does NOT lift the 5³ liberty net (libs@64≈libs96×8 tied; libs128×10 over-scales below base)'
created_at: '2026-06-18T07:47:01.084932+00:00'
parents:
- polished-field-7944
- gentle-glitter-1363
- proud-king-2753
summary: 'SCALE-libs RESOLVED (P19 replan): GPU net-vs-net Elo screen shows capacity does NOT lift the 5³ liberty net. libs@64 (Elo 70.9) ≈ libs96×8 (78.6) tied at top; libs128×10 over-scales to Elo −11, below the 3-plane base. libs@64×6 stays the strongest 5³ net. Null result for the capacity lever; methodology pivot (net-vs-net + SPRT) unblocks the frontier.'
flywheel:
  node_id: faddae67-0dc0-566e-9054-9869f0e627f6
  slug: bitter-pine-2861
  revision: 2
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 9bd4a1afb57df4ff6f30acbf5471a3d9a6abd505d368ad32035cbc71ee59d514
---
> **STATUS: RESOLVED (PASS-19 replan) — null result; capacity is not the 5³ lever.**
> Resolved by GPU net-vs-net Elo screen (methodology pivot from the ~9h CPU net-vs-classical eval).

# SCALE-libs RESOLVED (PASS-19 replan) — capacity does NOT lift the 5³ liberty net

**Question (SCALE-libs `faddae67`):** ARCH-3 found liberty input planes lift the 5³
net to 0.449 vs classical (+0.144 CI-separated over the 3-plane baseline, doorstep
of parity). Does the *proven* capacity lever (the 32×3→64×6 step that first beat
classical, `b71da32b`) applied to `cfg=libs` cross parity — i.e. does scaling the
liberty net up (64×6 → 96×8 → 128×10) lift its *relative* strength?

**Answer: NO — and over-scaling hurts.** libs@64×6 and libs96×8 are *statistically
tied* at the top of the Elo ladder (no capacity gain), while libs128×10 — the
*largest* net — collapses to the bottom, **below the 3-plane baseline**. So scaling
the liberty net buys zero relative strength on 5³, and pushing capacity to 128×10
on the same data/training budget is actively worse. libs@64×6 remains the strongest
(most capacity-efficient) 5³ net.

## Method — the methodology pivot (why this is fast, not a 9h CPU wait)

The PASS-19 plan tried to resolve this with the ARCH-3 net-vs-classical protocol
(net@512 vs classical@48, n=128/seed). That is the campaign's real bottleneck: the
net runs on CPU and classical's random rollouts dominate, so each scaled-net eval is
~3 h/seed (the in-flight 96×8 eval would have blocked ~9 h). **Code audit:** the cost
is (a) classical's CPU rollouts, (b) Python per-node engine ops in the net's own MCTS
tree, (c) the net forward on CPU — a GPU net-vs-classical harness buys only ~2.5×.

The fix is a methodology change: screen *relative* strength with **GPU net-vs-net**
(`screen_nvn.py`) — both sides batched, no classical rollouts. A round-robin over the
lever family fits a Bradley-Terry / Elo ladder (same fitter as `ladder.py`, anchor =
`base`), ×3 seed checkpoints per config pooled into the win counts (≥128 decided
games/agent pooled — answers the PASS-15 small-sample scar at the rating level).
Encoding sped up first: `input_planes.config_planes` now computes only the channels a
config needs (skips the per-empty-cell ko/capture loop for base/libs), byte-identical
to `rich_planes` (`test_input_planes.py`, 960 cases), 4.5× faster for libs / 119× for
base. Screen: n=5³, sims=24, 48 games/pair, full run ~36 min on GPU vs ~9 h CPU.

**Sanity gate PASSED:** net-vs-net reproduces the known ARCH-3 classical direction —
base-vs-libs = 15/45, i.e. **libs@64 beats base 0.667** head-to-head (classical:
libs 0.449 > base 0.305). The screen tracks real relative strength.

## Result — pairwise (A-winrate; 3 seeds pooled, ~46 decided/pair, sims=24)

| pair | A / decided | A winrate |
|---|---|---|
| base vs libs        | 15/45 | 0.333 (libs +67%) |
| base vs all         | 24/46 | 0.522 |
| base vs libs96x8    | 21/45 | 0.467 (libs96x8 +53%) |
| base vs libs128x10  | 19/44 | 0.432 (libs128x10 +57%) |
| libs vs all         | 26/46 | 0.565 |
| **libs vs libs96x8**   | 25/48 | **0.521 (wash, libs@64 ahead)** |
| **libs vs libs128x10** | 25/47 | **0.532 (wash, libs@64 ahead)** |
| all vs libs96x8     | 18/46 | 0.391 |
| all vs libs128x10   | 30/47 | 0.638 |
| libs96x8 vs libs128x10 | 33/46 | 0.717 (libs96x8 crushes 128x10) |

**Anchored Elo ladder (Bradley-Terry, anchor base=0, bootstrap 95% CI):**

| agent | Elo | CI95 |
|---|---|---|
| libs96x8 (96×8, 4.08M) | **78.6** | [19.4, 143.4] |
| libs (64×6, 1.42M)     | **70.9** | [17.7, 134.9] |
| all (64×6, 10-plane)   | 25.2  | [−38.9, 89.9] |
| base (64×6, 3-plane)   | 0.0   | anchor |
| libs128x10 (128×10)    | **−11.0** | [−68.6, 51.3] |

## Reading

- **libs@64 and libs96×8 are statistically tied at the top** (Elo 70.9 vs 78.6,
  CIs almost coincident; head-to-head 0.521 ≈ even). Doubling capacity to 96×8
  (4.08M params) buys **no** relative strength.
- **Over-scaling to 128×10 is actively worse:** the largest net lands at Elo −11,
  *below the 3-plane baseline*, and loses the direct match to libs96×8 0.717. On the
  same data + soft-target budget (all six nets trained in ~20 min total), 128×10 is
  under-trained for its capacity — more channels/blocks made it *worse*, not better.
- **vs the common baseline**, the *smallest* liberty net is the most efficient:
  libs@64 beats base +67% head-to-head, more than any scaled arm.
- This extends the campaign's recurring **5³ strength ceiling** (PASS-15: self-play
  doesn't lift absolute strength; the capacity lever that worked 32×3→64×6 does not
  re-fire here) to the liberty input: liberties move the net to the doorstep of
  parity, but *capacity on top of liberties* is exhausted at 5³ — and overshooting
  it (128×10) regresses below baseline.

## Caveats / scope

- **Search depth:** screened at sims=24 (shallow), not net@512. Bigger nets can need
  more search to express capacity, so this is the *conservative* direction — yet even
  at sims=24 the smaller net is ≥ the larger ones, so capacity is not merely
  under-served, it is *not ahead*. A higher-sims confirm on the one key pair
  (libs@64 vs libs128×10) is the cheap follow-up if a tie-break is wanted.
- **Relative, not absolute:** net-vs-net cannot say "beats classical". The single
  SPRT-bounded classical anchor (EVAL-1 `259c2ebe`, `sprt.py`) cross-checks libs@64
  (sub-parity, "not_a_winner") and would anchor any net-vs-net winner — here there is
  no scaled winner to anchor, so libs@64×6 remains the strongest 5³ net.

**Implication for the frontier:** capacity is not the lever on 5³. The liberty gain
is real but capped here; the productive next moves are (a) liberty-encoding
*refinements* (my/opp split, finer buckets, liberty-after-move) and (b) pushing
liberties to **7³**, where search-scaling amplifies with board size (PROOF-2) and a
capacity gain may finally have room — not more channels on 5³.

Artifact: `screen_nvn_5cubed.json` (full wins/games matrix, Elo, bootstrap CIs).
Resolves SCALE-libs `faddae67`; child of ARCH-3 `bcf93cd3`, control `62ab093f`,
index `f9f2bf74`. Methodology node for EVAL-1 `259c2ebe` (net-vs-net screen +
SPRT anchor). Stop reason: **objective_characterized** (capacity-curve null result).


---

## Original STAGED plan (PASS-18 replan → PASS-19, for provenance)

# SCALE-libs — capacity scale-up on the winning liberty input (5³ → parity?)

## Objective
ARCH-3 (PASS-18) found **liberty input planes** decisively lift 5³ strength (libs 0.449 [0.400,0.499], +0.144 CI-separated vs the 3-plane baseline) — the doorstep of parity but still short of beating classical absolutely (lo 0.400 < 0.5). This branch applies the **proven capacity lever** (the 32×3→64×6 scale-up that first beat classical on 4³, `b71da32b`) to the liberty input: does a bigger net on `cfg=libs` cross parity (CI-lower > 0.5)?

## Decision criterion (CI-based, n≥128)
Scaled liberty-input net beats classical@48 with **CI-lower > 0.5** at n≥128 on 5³ (absolute S1/S5 met) — OR a powered characterization of how far capacity closes the remaining ~0.05 gap (capacity curve 64×6 → 96×8 → 128×10 at fixed input + data + soft-target).

## Method (clean single-variable: only CAPACITY varies)
Reuse `net_arch3.A3GoNetIn` (cfg=libs, 6 planes) + the SAME data `distill_arch3_5cubed.npz` + soft target (T=4/W=8/prune) + protocol (net@512 vs cls@48 cap50, n=128, seeds 0/1/2 pooled) as ARCH-3. Train 96×8 and 128×10 (×3 seeds); eval 96×8 first vs classical, 128×10 deferred (agent-in-loop on the 96×8 signal).

## Cost · binding constraint
Big-net CPU eval is the wall: 96×8@512 ≈ 2.9h/seed, 128×10 ≈ 5h/seed (the net forward dominates once channels grow; INFRA-1's "forward is ~10%% of move time" held only for 64×6). Surfaces the need for a **GPU-batched net-vs-classical eval harness** (net on GPU batched across games, classical on CPU) to make the full capacity/sims/7³ program affordable — staged as the infra unblock.

## Expected artifacts
Capacity-curve A/B JSON (winrate vs classical, n≥128, per capacity), holdout metrics, scaled checkpoints.

*STAGED → EXECUTING PASS 19. Extends ARCH-3 `bcf93cd3` (liberty lever) + ALGO-2 `792c4ec2` (capacity). Budget $0/local.*