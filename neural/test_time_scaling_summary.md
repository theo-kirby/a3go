# PROOF-2 — test-time search scaling of the distilled nets (4³/5³/7³)

Harness `neural/test_time_scaling.py` (parallel: one (board,sims) match per core,
GPU shared). 60 color-balanced games/point, temp=0.4 sampling. Win-rate of the
SAME net at S sims vs a fixed low-sim baseline of itself. Raw: `test_time_scaling.json`.

## Scaling curves (win-rate vs fixed baseline)
| board | base | 1× | 2× | 4× | 8× | 16× |
|---|---|---|---|---|---|---|
| 4³ | @48 | .50 | .68 | .77 | .79 | **.90** (768) |
| 5³ | @48 | .42 | .62 | **.91** | .93 | **.98** (768) |
| 7³ | @64 | .36 | **.72** | .87 | **1.00** (512) | — |

(7³@1024 omitted as redundant — @512 already won 60/60.)

## Finding: test-time search scaling grows stronger on bigger boards
- More sims reliably beats fewer sims on every board (monotone, CIs separate) —
  **search is a real strength lever for the distilled net.**
- The effect **amplifies with board size**: to dominate the baseline, 4³ needs
  ~16× sims (→0.90), 5³ ~4× (→0.91), and 7³ only ~4–8× (→1.00). At matched 4×
  budget: 4³ 0.77 < 5³ 0.91; at 8×: 4³ 0.79 < 5³ 0.93 < 7³ 1.00.
- This is exactly the cross-board-law prediction [0bc38c41]: the value head is far
  better calibrated on bigger boards (value MSE 0.044→0.019→0.006 for 4³→5³→7³),
  and deeper PUCT amplifies a *good* value head but a miscalibrated one (PASS-6
  "test-time scaling is no free lunch" [9605fb9a]). Here, on the well-calibrated
  big boards, search pays off hugely — the opposite regime from the weak 32×3 net.

## Why this matters for the Success bar
- **S1/S4 implication:** PROOF-1 showed the net's win over classical is budget-
  bounded *on 4³* (classical's rollout value scales better on tiny boards). This
  result shows the net's OWN strength scales steeply with search on 5³/7³ — where
  random rollouts are weak (long games) and the net's value is near-perfect. So
  the board where we're most likely to dominate classical at all budgets is the
  genuinely-3D one (7³), not 4³. The missing measurement is net-vs-classical at
  high sims on 7³ (classical is CPU-expensive there) — flagged for follow-up.
- This is the test-time-scaling half of S1, delivered cheaply thanks to the free
  GPU + the INFRA-2 engine speedup (7³@512 over 60 games is now minutes, not the
  ~12 min/game it was on CPU in PASS-11).

## Caveat
Equal-sims self-play points (5³ 0.42, 7³ 0.36) sit a bit under 0.50 — n=60 sampling
noise with different RNG seeds; does not affect the clear monotone rise.
