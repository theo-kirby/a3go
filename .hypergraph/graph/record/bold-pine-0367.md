---
node_id: dcd0a5db-a4a6-5bdb-8e13-d82591ed4b31
slug: bold-pine-0367
title: Methodology lessons — what worked / what didn't (LIVING)
created_at: '2026-06-07T12:52:28.718977+00:00'
parents:
- purple-fog-6345
summary: 'LIVING methodology log. Latest (PASS-15): under-powered n<=32 win-rate evals (+-0.16 CI) overstate magnitude — a 5^3 self-play ''lift'' to 0.406/0.594 vanished at n=128 (==seed, ~0.40); even seed ''parity@512=0.50'' is 0.414 at n=128. Gate/claim on n>=128. Prior lesson: net-vs-net gates mislead on direction. Real claim needs OOD opponent AND n>=128.'
origin:
  backend: flywheel
  node_id: dcd0a5db-a4a6-5bdb-8e13-d82591ed4b31
  slug: bold-pine-0367
  revision: 10
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: befc2f75-d3f8-5e9f-aa83-bdd35de17b36
  slug: little-hall-9089
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: b300578a7d86f96db08e9b8615e978288ecfa7be45331bdbbf10d79737154df5
---
# Methodology lessons — what worked / what didn't (LIVING)

## What worked
- **Parallel self-play via process sharding** (`parallel.ts`): ~28x, near-linear, no shared-state hazards.
- **Batched game-parallel MCTS self-play** (Pass 3, `batched_az.py`): run many independent game-trees in lockstep, one **single batched GPU forward per simulation round** across all trees. **22x** on 4^3 (0.05->1.1 games/s). Trees are independent so each contributes one leaf/round -> NO virtual loss needed. This is THE lever that turned the neural flywheel.
- **VOLUME breaks the plateau (Pass 3 confirms M4's diagnosis):** at 5x M4's self-play volume (80 games/gen x 12), strength ROSE — 5 promotions, vs_random 0.61->0.94, final net beats random **0.89 [0.84,0.93]** and beats its own untrained gen-0 **0.65 [0.58,0.71]** (CI excludes 50%). M4 plateaued at 24 games/gen for lack of volume, not a bug; M5 made volume cheap and the plateau lifted.
- **Deterministic bounded-minimax solvers** (ladders, life&death, **seki** in Pass 3): cheap, exact, validate against 2D theory — highest signal/sec. Seki confirmed to exist in 3D and to survive 6-connectivity.
- **Cross-validating the Python engine port vs TS** (replay seeded games, compare Tromp-Taylor): 60/60 — re-run after ANY engine edit (did so after the legal_moves fast-path; stayed 60/60).
- **Best-net gating + replay buffer** in AZ: eliminated catastrophic regression; still essential in Pass 3.
- **Mean-signed-margin for komi** beats win-rate on blowout boards (Pass 3: pinned 4^3 fair komi ~0.5, SE 0.39).

## What didn't / pitfalls
- **Win-rate vs komi is degenerate on small boards** (blowout-dominated); variance-limited. Komi precision is limited by the HEAVY-TAILED margin distribution (std ~9.8 on 4^3, tails +/-36), not by sampling cost — and M5 makes N>450 games trivial, so even that limit is now cheap.
- **3^3 ~= 2D** (mean degree 4.0) and draw-prone — use >=4^3.
- **Naive AZ collapses/regresses** without Dirichlet noise AND replay buffer + gating. Both required.
- **Loss != strength** — always measure gated head-to-head playing strength.
- **Per-gen N=32 eval is NOISY** (SE ~0.09): vs_gen0 looked flat/noisy mid-run; only the high-N (N=200) final eval cleanly showed the rise. Use big-N eval for the headline claim.
- **Un-batched MCTS WAS the neural throughput wall** — fixed in Pass 3 by batching. After batching, pure-Python `legal_moves` (floodfill) became the residual wall; a superko-hash fast-path added ~13% more.
- **Test the engine before trusting an optimization (Pass 3 scar):** my first legal_moves fast-path cached `self.grid` in a local, but `_is_legal` REBINDS `self.grid` to a fresh snapshot — the cached ref went stale/dirty and corrupted later iterations. A 460-position brute-force equivalence test caught 5 mismatches before I believed it. Also: a non-capturing move CAN still trigger superko (intervening captures), so the cheap fast-path still needs a hash check.
- **Don't fight for the GPU you don't own:** an external vLLM process held 28/32 GB VRAM. Single-process batched self-play (tiny net, ~0.7 GB) was safe; GPU-multiprocessing across CPU cores risked OOM-ing it and was NOT pursued.
- **Classical MCTS in TS doesn't scale to 7^3/9^3** (0.01 games/s/core at 5^3).

## Reusable assets
TS: `parallel.ts`+`worker_selfplay.ts`, `exp_{komi,boards}_parallel.ts`, `exp_{ladders,lifedeath,geometry,ko}.ts`, `dump_games.ts`.
Python (`neural/`, uv+torch cu128): `a3go_engine.py` (validated, now with non-cube shape support + fast legal_moves), `crossval.py`, `test_engine_fast.py`, `net.py`, `az.py`, **`batched_az.py` (M5 batched self-play+eval)**, `train_gated.py`, **`train_batched.py` (volume trainer)**, `seki3d.py` (minimax seki solver), `classical_mcts.py`, `komi_neural.py`, `final_strength.py`, `bench_{hotpath,batched}.py`.

## Pass 4 additions
- **SELF-PLAY WIN-RATE != ABSOLUTE STRENGTH (the headline Pass-4 lesson).** The Pass-3 4^3 net beats random 0.89 and beats its own untrained gen-0 0.65 — yet it **loses ~92% to classical random-rollout MCTS at EQUAL budget** (0.085 [0.034,0.199] at 48 vs 48). A self-referential ladder (cand_vs_best, vs_gen0) can rise while the whole ladder sits far below a fixed external baseline. **Always anchor strength to a non-self baseline.** On tiny boards classical MCTS is strong because random rollouts run to terminal = near-free accurate value; the under-trained net's value head can't match it. This is the strength-analogue of 'loss != strength'.
- **5^3 is tractable for neural self-play via M5** (0.122 games/s, ~12x pass-1 classical 0.01 g/s/core) and is **all-decisive (0 draws)** — less degenerate than 3^3/4^3. But strength is **volume-gated**: a 224-game run (8x28) got 0 promotions, below 4^3's first-promotion threshold (~320 buffered games at gen-4). Igniting the flywheel needs 4^3-level volume, which is ~9x more wall-clock on 5^3 — wall-clock is the binding constraint, not per-game feasibility.
- **Ignition volume is a real quantity:** 4^3 needed ~320 buffered self-play games before the first candidate beat the gen-0 best. Below that, candidates train strictly worse (cold start). Size neural runs to clear ignition before reading 'no rising strength' as a negative.
- **Parallelize CPU-bound eval across cores with the net on CPU** (net_vs_classical_mp.py): the tiny net runs fine on CPU, one game/worker across ~14 cores turns a ~3-min/game sequential GPU job into a batch that finishes ~14x faster AND leaves the GPU free for a concurrent training branch.

## Pass 5 additions (autogo transfers + the strongest form of the strength lesson)
- **DISTILLATION FROM A STRONGER TEACHER beats cold-start self-play, cheaply.** We have no human 3D-Go games, but classical MCTS beats our net — so distill IT: collect classical self-play (state, visit-policy, outcome), supervised-train the net. 192 classical games + supervised >> 960 self-play games: the distilled net beats the from-scratch self-play net 0.72 head-to-head and lifts vs-classical from 0.085 to 0.333. When you lack expert data, your strongest available search agent IS your teacher.
- **SELF-PLAY IMPROVEMENT CAN ACTIVELY MISLEAD, not just be noisy.** Warm-starting self-play from the distilled net improved EVERY self-referential metric (beats distilled init 0.75, random 0.91, old self-play net 0.64) yet DROPPED absolute strength vs classical 0.333 -> 0.222. With net-vs-net gating, self-play optimized a within-population objective and drifted off the classical-quality target. Pass 4 said 'self-play WR != absolute strength'; Pass 5 shows it can move OPPOSITE to truth.
- **Fix: anchor the gate to an EXTERNAL baseline.** Promote only if a candidate beats classical MCTS at least as often as the current best does — don't let unanchored net-vs-net set the target. Or keep distilling from an ever-stronger classical teacher (raise playouts) instead of self-play.
- **Holdout policy-argmax accuracy is a weak metric for diffuse MCTS targets** (got 0.13 even as value MSE -> 0.048 and play strength jumped 4x). Use it as a sanity signal, not a strength proxy; play-strength vs a fixed baseline is the truth.
- **autogo (ericjang/autogo) [b4fd8252]** validated our M5 (their 19.4x C++ ~ our 22x Python) and supplied these transfers. Incorporated: distillation, Dirichlet annealing (0.25->0.05, in train_batched), variety>depth sizing, holdout metric. Skipped: multi-node/managed infra. Still on frontier: C++ engine + leaf-parallelism (their next ceiling).

## Pass 6 additions (the recipe that BEAT classical, + a non-result)
- **To beat a strong search baseline with no expert data: distill the baseline, then scale teacher + capacity.** Journey vs classical (equal budget): 0.085 (self-play) -> 0.333 (distill 32x3 from 128-playout classical) -> ~0.48 (stronger 192-playout teacher + 29.6k examples, parity) -> **0.612 (same data, 64ch x 6block net)**. THREE levers, in order: (1) distillation gives the foundation, (2) stronger+more teacher data reaches parity (diminishing returns), (3) NET CAPACITY crosses the line.
- **Capacity fixed the value head.** The scaling node showed deeper PUCT amplified the 32x3 net's value errors; a 64x6 net (same data) jumped 0.484->0.612. When more search HURTS, suspect value-head capacity/calibration, not the search.
- **Test-time sims scaling is NOT a free lunch [9605fb9a]** — it needs a well-calibrated net first; on the weak 32x3 net more sims were flat-to-harmful. autogo's scaling law presumes a good net.
- **Right-size expensive data collection.** 256-playout classical self-play was ~30 min/GAME (killed a 5-hr run); 192-playout was the sweet spot for a stronger-but-affordable teacher.
- **Arch is selectable via A3GO_CH/A3GO_BLK env vars** in train_distill.py + net_vs_classical_mp.py (clean A/B on capacity).

## Phase 3 / Pass 13 additions (infra + measurement)
- **Profile before you build.** INFRA-1 set out to build a GPU-batched MCTS server; profiling showed the batched GPU forward was already only 3-11% of move time (M5 BatchedMCTS already batches across games) and the real wall was the per-node Python engine (`legal_moves` ~90%). The "build a server" premise was falsified by one benchmark — saved a large wasted build.
- **The engine, not the GPU, was the throughput keystone.** INFRA-2: vectorize legal-move generation (numpy boundary-safe shifts; native `legal_move_mask()` consumed directly by the MCTS instead of rebuilding it from a tuple list) + Zobrist incremental superko (`zob ^ Z[cell,color]` + np.isin, no per-candidate tobytes) => **3.5x on 7^3** (11.85s->3.14s profiled), scaling with board size. Re-validated 460/460 brute + 60/60 crossval + npm 48/48 after every edit (the Pass-3 'test before trusting' rule held).
- **A rating ladder needs play variety + a regularized fit.** PROOF-1's first run was degenerate: pure-argmax made net-vs-net games deterministic per color (40/40 cycles), and Bradley-Terry diverged because random won 0 games (all Elo at the clamp). Fixes: opening-temperature sampling (temp=1 + Dirichlet first 6 plies) for variety; weak symmetric prior in the BT fit for finite ratings. Also: pin worker threads (set_num_threads(1)+OMP=1) under a process pool, and use spawn (a CUDA-initialized parent can't fork).
- **Anchored Elo cleanly exposes the S1 gap.** On 4^3 the net beats classical at 48 sims but cls@128 (849 Elo) beats net@128 (656) 27/30; classical's sim-scaling is steeper on tiny boards (Monte-Carlo value ~ free & calibrated). Win-rate-at-one-budget hid this; the ladder makes it a number.
- **Local GPU hygiene scar:** running batched GPU MCTS in the ~3.7GB headroom left by an external vLLM server coincided with that server being OOM-killed (GPU freed entirely). Lesson: when a foreign process owns most of VRAM, cap/measure our allocation explicitly (or run net eval on CPU for small boards) rather than trusting headroom.

## Phase 3 / Pass 13 cont — anchored self-play gate + tooling
- **The externally-anchored gate stops self-play drift — validated LIVE (INFRA-3).** In a running AZ loop on 4^3, iters 3-4 produced candidates that beat the best NET-VS-NET (0.71/0.73) but would have regressed vs classical (0.57/0.58); the gate correctly refused them. Concrete confirmation of the Pass-5 lesson (net-vs-net-only gating drifts off absolute strength) and that anchoring the gate to a fixed external baseline fixes it.
- **Pick the board where there's headroom.** AZ self-play gave no robust gain on 4^3 (0.652->0.667, within noise) because 4^3 is where classical is strongest (PROOF-1) and the champion is near the small-board ceiling. PROOF-2 shows the net scales steeply with search on 5^3/7^3 — that is where self-improvement should be attempted.
- **Profiling beats assuming (INFRA-1/2).** The "build a GPU MCTS server" plan was falsified by one profile (GPU 3-11% of move time); the real wall was the engine (legal_moves), fixed for 3.5x by vectorizing + Zobrist. Always measure the bottleneck before building for it.
- **Tooling built:** z-slice + voxel 3D board renderer (`viz.py`), JSON->PNG figure pipeline (`figures.py`), human-play CLI with net policy/value readout + auto-showcase (`play.py`). Figures attached as artifacts across the result nodes.
- **Net-vs-net self-improvement overstates strength vs an out-of-distribution baseline (PASS-14, INFRA-3 5^3).** A FROZEN-net anchor cures the Pass-5 *drift* trap (a moving reference can be gamed), but it does not make net-vs-net a valid proxy for absolute strength: the 5^3 self-play champion beat its own frozen distilled seed 0.735 head-to-head yet was statistically IDENTICAL to that seed against classical (0.219@48, 0.50@512 — both unchanged). The self-play family shares blind spots the OOD opponent (random-rollout classical, different style) exploits the same before and after. Lesson: gate/measure absolute claims against the OOD opponent, not the in-family reference; an in-family head-to-head gain is necessary, not sufficient. Corollary fix to try: anchor the promotion gate on cand_vs_classical, not cand_vs_frozen-net.
- **Under-powered win-rate evals (n≈24–32) have ±0.16 CIs — too wide for the distinctions drawn from them (PASS-15).** Classical-anchored 5^3 self-play *looked* like it lifted the net 0.194→0.406 vs classical@48 (1 promotion) and 0.594@512; both were n=32. At **n=128 the lift vanished**: champion 0.262@48 / 0.402@512 is statistically identical to the distilled seed 0.234@48 / 0.414@512 (CIs fully overlap). The promotion gate had fired on a 32-game noise fluctuation. Even the campaign's headline **'5^3 reaches parity@512 = 0.50' [e7c35c64] was n=32; at n=128 it is 0.414 [0.332,0.501]** — just *below* parity. **Rule: gate promotions and any beats/ties-classical claim on n≥128; read all prior n≤32 win-rates as point estimates with ±0.16 error bars.** This compounds the prior lesson: net-vs-net gates mislead on *direction* (in-family vs OOD), small-N evals mislead on *magnitude* — a real strength claim needs the OOD opponent AND n≥128.