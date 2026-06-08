# PROOF-1 — anchored Elo ladder, 4³ (first instance of Success-bar-v2 S2)

Harness: `neural/ladder.py` (Bradley-Terry MLE, regularized; bootstrap 95% CIs;
random pinned to Elo 0). Per-game CPU sharding across 14 cores, 1 thread each.
G=30 games/pair, 21 pairs, 7 agents. Raw: `ladder_4cubed.json`. Net = the 64×6
distilled champion `best_distill_big_4cubed.pt`.

## Ratings (anchor random = 0)
| rank | agent   | Elo | 95% CI |
|---|---------|----:|--------|
| 1 | cls@128 | 849 | [789, 920] |
| 2 | net@256 | 784 | [736, 848] |
| 3 | net@128 | 656 | [611, 716] |
| 4 | cls@48  | 638 | [592, 689] |
| 5 | net@48  | 611 | [569, 659] |
| 6 | cls@16  | 396 | [365, 430] |
| 7 | random  |   0 | — |

## What it shows
- **Both agents scale monotonically with search** (anchored): classical
  396→638→849 for 16→48→128 sims; net 611→656→784 for 48→128→256.
- **The net wins at low budget, classical wins at high budget (the S1 gap, on
  one scale).** Matched-budget head-to-heads from the win matrix: net@48 beat
  cls@48 17/27 (≈0.63 — consistent with the PASS-6 0.612 headline), but cls@128
  beat net@128 **27/30** (≈0.90). Classical's sim-scaling slope is steeper on 4³
  (+211 Elo over 16→128) than the net's (+45 over 48→128), so more search favors
  classical here — random rollouts to terminal give cheap, well-calibrated value
  on a tiny board, which the net's value head doesn't match as search deepens.
- **cls@128 is the strongest agent in the cast (849)**, ~65 Elo above net@256
  (CIs overlap slightly) — the bar PROOF-2 must clear to claim budget dominance.

## Methodology lessons (the first run was broken — recorded so we don't repeat)
1. **Pure-argmax play makes a rating ladder degenerate.** With temperature→0,
   net-vs-net games are deterministic per color, producing 40/40 or 0/40 results
   and an intransitive cycle (net@48 "beat" net@128 100% while losing to net@256
   100%). Fix: sample the opening plies (temp=1 + Dirichlet root noise for the
   first 6 moves), argmax after — variety without sacrificing endgame strength.
2. **Bradley-Terry diverges under perfect separation.** Random won 0/180 games,
   pinning the unregularized fit at the ±4800 log-clamp for everyone. Fix: a weak
   symmetric prior (reg virtual wins each direction per pair) → finite, ordered
   ratings. Verified the fit recovers a sane ordering at reg∈{0.5,1,2}.
3. **Process-pool eval must pin threads.** 14 worker processes × PyTorch's default
   intra-op threads oversubscribed the 32-thread CPU and stalled everything;
   `torch.set_num_threads(1)` + `OMP_NUM_THREADS=1` per worker fixed it. Also: a
   parent that has initialized CUDA cannot `fork()` workers (deadlock) — use spawn.

## Next
- Add cls@256/512 and net@512 to map the full S1 crossover curve (PROOF-2).
- Run the ladder on 5³/7³ (now cheap after INFRA-2) for cross-board S2.
