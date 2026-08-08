---
node_id: 62ab093f-98b2-5083-aadd-ed764fa9b28c
slug: shiny-term-3012
title: '[control] flywheel-auto — 3D Go campaign (local, $0) [PASS 20-r2 — BREADTH: 7 probes resolved (REP-3 my/opp split directional+ 0.558; SYMM-1 arm-A NULL; +PROBE-1/2, 3DSCI-2, SEARCHX-1) + 22 new STAGED dirs (3 batches); index f9f2bf74 rev22, 40 dirs]'
created_at: '2026-06-07T11:32:09.869722+00:00'
parents:
- purple-fog-6345
summary: 'flywheel-auto control — PASS 20 round-2: REP-3 my/opp liberty split directionally + (0.558 [.46,.66], 2/3 seeds beat plain libs, under-powered → confirm at higher n); SYMM-1 arm-A retest NULL (k=48 0.531 → pivot arm-B). Batch-3 geometry axis seeded (GEO-1 dim-ladder, ALGO-S1/2, ROBUST-1). PASS-20 total: 22 new STAGED dirs + 7 probes resolved. npm 48/48, crossval 60/60. Next: REP-3 higher-power confirm, GEO-1, ALGO-S1. stop=objective_met.'
origin:
  backend: flywheel
  node_id: 62ab093f-98b2-5083-aadd-ed764fa9b28c
  slug: shiny-term-3012
  revision: 40
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 832b9659-cf8b-53a5-a41e-1a19d3bff1d1
  slug: calm-glade-3133
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: 21c2dd03bdb856cecda72c7253197cd82b0aae70e419206efccb8e6c0558983c
---
# Autonomous run controller (flywheel-auto) — multi-pass, LIVING

Read this first on any replan; continue from this contract + the agenda node `snowy-term-0287`.

## Campaign state after PASS 6-8 — CENTRAL OBJECTIVE MET; bigger-board frontier gated on C++ build
- **Headline:** the neural agent BEATS classical MCTS on 4^3 (0.612 [0.533,0.686] equal budget) [b71da32b] — success bar fully met (beats random + beats classical + rising self-play strength). Recipe: distill the classical teacher -> stronger/more teacher data (parity) -> bigger 64x6 net (crosses the line).
- **PASS 7:** scaling re-characterized — the calibrated 64x6 net DOES scale with sims (0.65->0.78 vs fixed classical@48), inverse of the weak net; but classical@128>>@48 bounds the win to matched/low budgets on tiny 4^3 [28f66847].
- **PASS 8:** 5^3 distillation pilot — under-resourced net loses 0.045; strong-teacher 5^3 data-gen is too slow on the Python engine -> **bigger-board recipe is GATED on the C++ engine** [c4091781]. Q8: champion net has NO opening positional preference on 4^3 (~uniform corner/edge/face/interior), unlike 2D Go [853d7c2c].

## Run contract (current frontier)
- **Objective:** extend the proven distillation recipe beyond 4^3 (5^3/7^3) where neural value should beat rollouts more decisively.
- **Decision criterion:** distilled net beats classical on the bigger board at matched budget (CI lower > 0.5).
- **Start nodes:** beats-classical `b71da32b`, scaling `28f66847`, 5^3 pilot `c4091781`, autogo `b4fd8252`, agenda `snowy-term-0287`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local.
- **Lookahead n=2; frontier width k=2.**
- **Terminal condition:** stop when no non-redundant frontier branch justifies the budget; the remaining HIGH-value branch (5^3+ recipe) requires the C++ engine build (large, discrete effort) -> surfaced for a human go/continue, not an autonomous cheap probe.
- **Stop reason: `no_viable_branch`** (for the cheap-probe budget). Per-candidate rejection: (a) 5^3/7^3 recipe — blocked on slow Python classical data-gen, needs C++ engine first; (b) Q7 snapback / seki-frequency / sharper-Q8 — viable but LOW marginal value; (c) managed compute — out of budget ($0/local). Next real leap = build the C++ engine + leaf-parallelism (autogo [b4fd8252]); recommended as a human go/continue.

## Prior passes (kept) — see agenda for node ids
P1 success-bar-leg1/ladders/L&D/komi/geometry; P2 toolchain/engine-60-60/AZ/gating/M4-plateau; P3 M5-22x/rising-strength/komi/seki; P4 net-loses-to-classical/5^3-volume-gated; P5 distillation-lever/self-play-drift/autogo; P6 BEAT-CLASSICAL.

## Design gate — PASSED.

## PASS 9 (continuation): fast playout -> properly-resourced 5^3 test
- **Objective:** unblock the 5^3 recipe WITHOUT a full C++ build, by speeding up the Python classical playout (the data-gen bottleneck), then run a strong-teacher 5^3 distillation to test the bigger-board hypothesis (5^3 value head fit BETTER than 4^3's [c4091781]; only the teacher was too weak).
- **Decision criterion:** strong-teacher 5^3 distilled net beats classical on 5^3 at matched budget (CI lower > 0.5), OR a properly-resourced negative.
- **Approach:** additive engine `play_fast` (capture+suicide, NO superko — rollouts don't need it; does NOT touch the 60/60-crossval play() path) + a random-empty fast rollout (no full legal_moves enumeration per step). Verify classical-fast strength ~ classical-orig before trusting.
- **Stop reason:** (pending).

## PASS 9 RESULT (recipe transfers to 5^3)
- Added 9x-faster fast playout (additive `play_fast`, crossval 60/60) -> strong 5^3 teacher (21.8k examples) tractable.
- **5^3 distilled 64x6 net (value MSE 0.019) reaches PARITY with classical, scaling 0.19->0.50 as sims 48->512** [e7c35c64]. The recipe transfers across board sizes; the MCTS budget scales with the action space (4^3/65-act wins @48 sims; 5^3/126-act needs ~512). Neural sims are cheap, so this is affordable.
- **Stop reason: `objective_met`** for PASS 9 (recipe-transfer demonstrated). Next leaps: push 5^3 to a decisive win (net@1024, cheap-ish); 7^3/9^3 + much faster everything -> the **C++ engine + leaf-parallelism** is now the clear gating prerequisite (a large build = human go/continue).

## PASS 10 (continuation): build a C++ engine core for throughput (unlock 7^3+ and faster everything)
- **Objective:** build a g++-compiled C++ 3D-Go engine (board+play+legal+capture+suicide+superko+Tromp-Taylor) + fast classical self-play data generator, to make bigger-board (7^3) and strong-teacher data-gen tractable (Python is the wall). Standalone binary + file I/O (no pybind11 build-system risk).
- **Decision criterion:** C++ engine cross-validates against the TS fixtures (60/60 TT breakdowns match, like the Python port) BEFORE building self-play on it; then measure data-gen speedup vs Python.
- **Approach:** incremental — Phase A engine+crossval (prove correctness), Phase B classical MCTS self-play + binary output. Fallback to cheap probes (5^3-decisive/Q7/seki-freq) if the build proves intractable.
- **g++ 13.3.0 present; no cmake (use g++ directly).** Stop reason: (pending).

## PASS 10 RESULT (C++ engine built — bigger-board program unblocked)
- **C++ engine + self-play generator [cff3a5d1]: 60/60 cross-validated vs TS fixtures; ~60x faster (4^3) / ~7x (5^3) than Python; parallel wrapper -> train_distill npz.** Removes the data-gen wall that gated 7^3+/strong-teacher work.
- Caveat: C++ classical MCTS teacher is currently a bit WEAKER than Python's (C++-data net 0.25@256 vs Python-data 0.42@256, within noise; longer games). Engine ops validated; teacher-tuning (c_puct/rollout/playouts) is a refinement.
- **Stop reason: `objective_met`** for PASS 10 (engine built+validated). Next: tune the C++ teacher + run the 7^3 program (collect strong 7^3 data, distill, eval at board-scaled sims) — a large multi-hour endeavor now TRACTABLE at $0/local; natural next-session/human-decision boundary. Cheaper: net@1024 to make 5^3 decisive; Q7/seki-freq.

## PASS 11 (continuation): the 7^3 program (now tractable via the C++ engine)
- **Objective:** with the C++ engine, run the recipe on 7^3 (the most-genuinely-3D board): collect classical 7^3 teacher data, distill, eval at board-scaled sims. Tests whether the recipe + budget-scales-with-board law extend to 7^3.
- **First:** feasibility-time C++ 7^3 self-play; optimize legal_play_moves (grid-only no-ko legality, avoid history-copy/candidate) if needed for 7^3 tractability.
- **Decision criterion:** 7^3 distilled net beats/ties classical at board-scaled sims, OR a properly-resourced characterization. Budget $0/local. Stop reason: (pending).

## PASS 11 RESULT + CAMPAIGN SYNTHESIS
- **7^3 characterization [0bc38c41]:** C++ engine made 7^3 tractable; distilled net reveals a clean **cross-board SCALING LAW**: value MSE falls (0.044->0.019->0.006 for 4^3/5^3/7^3 — bigger boards all-decisive -> cleaner targets), policy acc falls (0.12->0.07->0.05 — bigger action space), required MCTS sims grow (48->512->>>512). 7^3 strength is sim-bound on CPU eval.
- **Campaign state:** Thesis answered. A strong agent CAN be trained for 3D Go; the winning method (no human data) is DISTILL-the-classical-teacher + scale capacity + scale (cheap) search with board size. 4^3 beats classical (0.61); 5^3 parity@512; 7^3 value near-perfect, strength sim-bound.
- **Next frontier = GPU-batched MCTS inference server** (autogo-style): the bottleneck for big-board HIGH-SIM play/eval has shifted from data-gen (solved by the C++ engine) to running 1000s of cheap neural sims/move on big boards. Another large build (human go/continue). Cheap probes remaining (Q7 snapback, seki-freq) are minor.
- **Stop reason: `objective_met`** (thesis answered + scaling law characterized). 11-pass session; comprehensive graph record.

## PASS 12 — Phase 3 frontier SCAFFOLDED (human-directed continuation)
- **Trigger:** human review ("only scratched the surface — scaffold new directions toward a *provably strong* agent; make all nodes public; report back for a start-point decision").
- **Done this pass (no experiments run):** (a) flipped all 11 remaining private nodes -> **public** (graph is now 100% public, 47+ nodes); (b) opened **Phase 3 hub `e917c9e4-fe12-5f0a-8e0d-1965c906f5a6`** — a new chapter that raises the bar from *existence* (answered) to *provably strong*; (c) staged **14 direction nodes** + a **Success-bar-v2 GATE `fdb07ec9-ee87-55bf-997c-b30c1c5998ca`** under the hub, across five themes: Infra (GPU-batched MCTS server `f6343208-8fd7-5f07-b265-e88f7f653c1b`, incremental engine `14377685-99ff-581d-8208-e4d8519b2b28`, full AZ self-play `8a724b1c-c666-5571-87fc-e078c55a0223`), Proof (Elo ladder `3ac354fd-ff3a-5e3a-be95-876b6c503d40`, beat-classical-at-all-budgets `75615ad2-12eb-5d2d-9a05-890c011c7f86`, exact-solve `22d59c45-09a2-5524-9943-b2687e52cb94`), Scale (9^3/non-cube `884663c8-410f-55d3-9122-1f493ac9b419`, size-agnostic net `1e58a424-54f6-5dfa-bf50-75d842f7dcda`, curriculum `adb11193-0501-5e63-98a6-101ea8bc591e`), Science (opening theory `5e34766d-c790-54a6-a98c-29b2fdbf7bbb`, life&death-at-scale `777d5c9e-70ce-588f-98e2-4f2a80dfebb6`), Algorithms (Gumbel AZ `4cf07501-9a4f-5aad-adf7-21c04d6d3709`, arch/value-target `792c4ec2-6cc6-51eb-a115-f44fe5dc0ff9`).
- **Keystone enabler:** INFRA-1 GPU-batched MCTS server unblocks S4 (7^3 decisive), PROOF-2 (high-sim sweeps), INFRA-3 (AZ self-play). Cheap-now wins needing no new infra: PROOF-1 (Elo ladder), PROOF-3 (solver), ALGO-1 (Gumbel), INFRA-2 (engine).
- **Run contract (Phase 3, pending human start-point):** Objective = a 3D-Go agent meeting Success-bar-v2 (S1-S5). Decision criteria = per Success-bar-v2 GATE. Budget = **$0/local** (unchanged). Lookahead n=2, frontier width k=2. Terminal condition = Success-bar-v2 met, or budget/again-no-viable-branch.
- **Stop reason: `awaiting_user` (scaffolding pass) — NOT executed.** All 14 nodes are STAGED; the human will pick the start point. Next replan: read hub `e917c9e4-fe12-5f0a-8e0d-1965c906f5a6` -> its status index -> chosen branch.


## PASS 13 — PHASE 3 EXECUTION STARTED (human-directed ignition order)
- **Trigger:** human go-ahead: "ignition order: INFRA-1, PROOF-1, ALGO-1, PROOF-3, INFRA-3, etc."
- **This is now an EXECUTING frontier (not scaffolding).** Hub `e917c9e4`; Success-bar-v2 GATE `fdb07ec9` defines acceptance (S1-S5).

## Run contract (Phase 3 — EXECUTING)
- **Objective:** a 3D-Go agent meeting Success-bar-v2 (S1 budget-dominance, S2 anchored Elo, S3 near-optimal vs exact-solve, S4 decisive 7^3, S5 beat-the-teacher).
- **Decision criterion:** per Success-bar-v2 `fdb07ec9` (each sub-node names its own CI-based criterion).
- **Start nodes (ordered):** INFRA-1 `f6343208` -> PROOF-1 `3ac354fd` -> ALGO-1 `4cf07501` -> PROOF-3 `22d59c45` -> INFRA-3 `8a724b1c` -> (then SCALE/SCIENCE/ALGO-2 as unblocked).
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t, all free; external vLLM holds ~28GB VRAM — coexist, do not OOM it).
- **Lookahead n=2; frontier width k=2** (execute up to 2 distinct branches per pass; the cheap-now wins PROOF-1/ALGO-1/PROOF-3/INFRA-2 need no new infra and can interleave with the INFRA-1 keystone build).
- **Terminal condition:** Success-bar-v2 met, OR no non-redundant branch justifies remaining budget, OR runtime/again-no-viable-branch.
- **Stop reason:** (pending — execution in progress).

### INFRA-1 reframing (from reading the code, before building)
`batched_az.BatchedMCTS.run_policies` ALREADY batches leaf evals across concurrent games on GPU (the M5 lever). PASS-11's 7^3 slowness was the EVAL HARNESS running the net on CPU (`net_vs_classical_mp.py`) + per-node Python engine cost (clone+legal_moves floodfill), NOT a missing GPU batch. So INFRA-1 = (a) benchmark BatchedMCTS sims/s on GPU vs board size/batch to locate the true wall; (b) build a proper GPU-batched net-vs-classical eval harness; (c) if the wall is per-node engine ops, that hands off to INFRA-2. Grounding this empirically first.


## PASS 13 RESULT (INFRA-1 + INFRA-2 resolved; engine was the real keystone)
- **INFRA-1 [f6343208] RESOLVED — premise falsified.** Benchmark+profile: the batched GPU forward is only 3-11%% of MCTS move time; `BatchedMCTS` (M5) already IS the game-parallel GPU inference server this node proposed to build. PASS-11's "7^3 sim-bound" was the CPU eval harness (`net_vs_classical_mp.py`), not a missing server. No new build; C++/TensorRT routes deferred. Artifacts: bench_infra1.json, infra2_speedup.md.
- **INFRA-2 [14377685] RESOLVED — 3.5x on 7^3.** Vectorized legal-move mask (numpy shifts + native `legal_move_mask`, flattened in `az.legal_action_mask`) + Zobrist incremental superko (np.isin, no per-candidate tobytes). Throughput: 4^3 1.33x / 5^3 1.92x / 7^3 **3.53x**; profiled 11.85s->3.14s (3.8x); GPU util 7^3 4%%->15%%. Validated: 460/460 brute, 485/485 vec+Zobrist invariants, 60/60 crossval (3^3,4^3), npm 48/48. All in the a3go-authored Python port (VENDORED.md unaffected). Union-find liberties deferred (flat profile, diminishing returns).
- **Replan:** the engine, not the GPU, was the keystone — reprioritization recorded. 7^3@512 now ~53ms/move/game amortized (was ~12 min/game on CPU), unblocking S4 / PROOF-2 / PROOF-1 / INFRA-3 at 2-3.5x lower cost.
- **Next (continuing ignition order):** PROOF-1 — anchored Elo/Glicko ladder [3ac354fd], now cheap given the faster eval.
- **Stop reason (this sub-step): `objective_met`** for INFRA-1/2; frontier continues to PROOF-1.

## PASS 13 cont — PROOF-1 delivered + an incident to flag
- **PROOF-1 [3ac354fd] DELIVERED.** Regularized Bradley-Terry Elo ladder on 4^3 (7 agents, bootstrap CIs, random=0): cls@128 **849** > net@256 784 > net@128 656 > cls@48 638 > net@48 611 > cls@16 396 > random 0. The net beats classical at 48 sims but cls@128 beats net@128 27/30 -> **the net's win is budget-bounded (S1 gap quantified on one scale)**; classical's sim-scaling is steeper on 4^3. Artifacts: ladder_4cubed.json, ladder_4cubed_summary.md. Fixed two methodology bugs first (argmax degeneracy, BT divergence) — see methodology node.
- **INCIDENT (flag to human): the external vLLM server (was ~28GB VRAM) is no longer running; GPU is fully free.** Not killed directly (pkill matched only the neural venv path; vLLM ran as /usr/bin/python3). Most likely GPU-OOM-killed during PASS-13 7^3 batched-MCTS benchmarks that allocated into vLLM's ~3.7GB headroom. Cannot restart (no launch config). Recorded as methodology scar; GPU now free helps Phase 3 but this is the human's process to restore.
- **Progress vs Success-bar-v2:** S2 has a first instance (4^3 Elo ladder). S1 is quantified-but-open (net loses at high budget). Engine throughput unblocked S4/PROOF-2/INFRA-3.
- **Next ignition items (all $0/local, CPU — no GPU needed):** ALGO-1 Gumbel [4cf07501], PROOF-3 solver [22d59c45], PROOF-2 full crossover [75615ad2].
- **Stop reason this pass: `objective_met`** for INFRA-1/INFRA-2/PROOF-1 (3 frontier nodes resolved/delivered). Pausing for human visibility on the vLLM incident before further GPU-adjacent work; loop can continue to ALGO-1/PROOF-3 (CPU-only) on next invocation.

## PASS 13 cont — PROOF-2 + PROOF-3 delivered (user freed the GPU)
- **User killed vLLM intentionally to free the GPU for this work** (resolves the earlier incident — not my doing to worry about; GPU now fully available).
- **PROOF-2 [75615ad2] DELIVERED.** Test-time search scaling of the distilled nets, GPU net-vs-net, parallel. Curves (winrate vs fixed baseline): 4^3 768:0.90, 5^3 768:0.98, 7^3 512:**1.00**. **Search scaling AMPLIFIES with board size** (4^3 needs ~16x sims to dominate; 7^3 only ~8x) — matches the cross-board value-calibration law [0bc38c41]; deeper PUCT amplifies a calibrated value head. Implication: the genuinely-3D 7^3 is where the net most likely beats classical at ALL budgets (vs 4^3 where PROOF-1 showed the win is budget-bounded).
- **PROOF-3 [22d59c45] DELIVERED.** Sound history-threaded minimax: exact 1x1x1=0, 2x1x1=0, 2x2x1=+1. Position-memoization PROVEN unsound (memo +2/+4 vs exact 0/+1 — superko makes value history-dependent); 2x2x2 is the exact-solving frontier (set by ko). S3 oracle exists only for <=4-cell boards today.
- **Session tally (PASS 13): 5 frontier nodes delivered** — INFRA-1, INFRA-2, PROOF-1, PROOF-2, PROOF-3 — all committed with artifacts, $0/local, npm 48/48, engine 460/460+60/60.
- **Next high-value (ignition continues):** (a) net-vs-classical on 7^3 at high sims = the S4 headline measurement (PROOF-2 strongly implies a decisive win; classical is CPU-expensive on 7^3 so needs a GPU-net+CPU-classical hybrid harness); (b) INFRA-3 AZ self-play to beat the teacher (S5); (c) ALGO-1 Gumbel. Stop reason this sub-step: objective_met.

## PASS 13 — SESSION TALLY (6 frontier nodes delivered, ignition list complete)
- **ALGO-1 [4cf07501]:** Gumbel AlphaZero implemented + A/B'd vs PUCT on 4^3. Honest NEGATIVE — no clear strength-per-sim win (behind at sims 8/16, ~even at 32/64; gumbel@16~puct@32 within noise). Reason: Gumbel targets large action spaces / weak policies; 4^3 (65 actions, strong distilled net) is the wrong regime. Fair test = 7^3 (344 actions); recorded to avoid re-trying on small boards.
- **7^3-classical finding:** classical MCTS is impractical on 7^3 (each rollout ~ board fill; a single net@256-vs-cls@64 game >250s). Classical is not a viable big-board baseline -> S4 redirects to net self-improvement, not beating an unrunnable classical.
- **Delivered this pass (all committed w/ artifacts, $0/local, npm 48/48, engine 460/460+60/60):** INFRA-1 (GPU never the wall), INFRA-2 (3.5x engine via vectorized mask + Zobrist), PROOF-1 (4^3 Elo ladder; net win budget-bounded), PROOF-2 (search scaling amplifies w/ board size; 7^3 saturates@512), PROOF-3 (exact small-board ground truth + memo-unsound), ALGO-1 (Gumbel, negative-on-4^3). The user's full ignition order (INFRA-1->PROOF-1->ALGO-1->PROOF-3) is complete, plus INFRA-2 + PROOF-2.
- **Progress vs Success-bar-v2:** S2 first instance (4^3 ladder); S1 quantified (4^3 budget-bounded) + test-time-scaling half done (7^3 saturates); S3 oracle for <=4-cell boards + unsoundness finding; S4 redirected (classical unrunnable on 7^3); S5 not yet attempted.
- **Next marquee = INFRA-3 [8a724b1c] AZ self-play to beat the teacher (S5)** — the path to a genuinely STRONGER agent, now feasible (free GPU + 3.5x engine + M5 batching). Big multi-hour build; best as a fresh focused effort. Also: ALGO-2 (arch/value-target), SCALE-1/2/3, SCIENCE-1/2, and a superko-aware exact solver for a meaningful S3.
- **Stop reason: `objective_met`** for the ignition list. Clean state; loop can resume at INFRA-3.

## PASS 13 FINAL — INFRA-3 + tooling (session: 9 Phase-3 nodes delivered)
- **INFRA-3 [8a724b1c] RUN 1 (4^3):** AZ self-play, externally-anchored gate. 0.652 -> 0.667 vs classical@48 (within N=24 noise) -> S5 not cleanly met on 4^3. BUT the anchored gate is VALIDATED LIVE: it3/it4 candidates beat best net-vs-net (0.71/0.73) yet regressed vs classical (0.57/0.58) and were correctly NOT promoted (the Pass-5 drift trap, blocked). 4^3 is the wrong board (classical strongest, champion near ceiling); S5 opportunity = 5^3/7^3. Loop+gate built & correct (best_az_4cubed.pt). ~2.3h.
- **TOOL-1 [1f59266a] + TOOL-2 [742a0aab] DELIVERED:** viz.py (z-slice + voxel 3D board render, policy/last-move overlays), figures.py (JSON->PNG pipeline), play.py (human CLI vs net/classical/random, live policy+value readout, --auto showcase). Benchmark figures attached as image artifacts to PROOF-1/2, INFRA-2, ALGO-1; sample board + showcase game (4^3 net@128, Black +3, 67 plies) attached to the tool nodes. matplotlib via uv.
- **SESSION TALLY (PASS 13): 9 Phase-3 frontier nodes delivered** — INFRA-1, INFRA-2, PROOF-1, PROOF-2, PROOF-3, ALGO-1, INFRA-3, TOOL-1, TOOL-2 — all committed with artifacts, $0/local, engine 460/460+60/60, npm 48/48. (User intentionally freed the GPU mid-session.)
- **Open frontier:** INFRA-3 on 5^3 (the real S5 attempt, cheap anchor); ALGO-2 (arch/value-target — the lever for S1 budget-dominance); SCALE-1/2/3 (9^3/non-cube, size-agnostic, curriculum); SCIENCE-1/2 (opening theory, life&death at scale); superko-aware exact solver (meaningful S3).
- **Stop reason: `objective_met`** for this pass's scope. Clean state; loop resumes graph-locally at the open frontier above.

## PASS 14 — INFRA-3 run 2: AZ self-play on 5^3 (S5 retry, frozen-net anchor)
- **Graph-local continuation** (re-invoked /flywheel-auto, no args) -> top open-frontier pick = INFRA-3 @5^3.
- **Design fix:** per-iter classical anchor is too slow on 5^3 (~15-25 min/eval). New variant `az_selfplay_frozen.py` anchors the gate to the FROZEN distilled champion (net-vs-net, GPU-cheap, drift-free since the reference never moves — the Pass-5 drift came from anchoring to the MOVING best). Question: does self-play beat the distilled 5^3 net it started from (which is at parity with classical [e7c35c64])? Classical translation = separate parallel eval on the final best.
- **Gate:** promote iff cand beats current best head-to-head >=0.55 AND cand_vs_frozen-ref >= best_vs_ref (no regression vs the frozen reference).
- **Run:** 5^3, 16 iters, 80 games/iter, 48->64 sims, seed=best_distill5strong_5cubed.pt. Budget $0/local.
- **Decision criterion:** final best beats the frozen distilled champion with CI-lower>0.5 (self-improvement beyond distillation) -> then translate to classical. Stop reason: (pending).

## PASS 14 RESULT — INFRA-3 on 5³ resolved (relative S5 met; does NOT translate to beating classical)
- **Graph-coherence note:** PASS 14 was *executed* in a prior session but never written back; this pass recorded it (INFRA-3 `8a724b1c` rev3 + 3 artifacts) and ran the deferred classical translation.
- **Relative S5 — MET.** Frozen-distilled-champion-anchored AZ self-play on 5³ (seed `best_distill5strong`, 48 sims, 80 games/iter): 2 promotions (it1 0.700, it2 0.735) then plateau; stopped at it4/8. Final champion `best_az_frozen_5cubed.pt` beats its own distilled seed **0.735** net-vs-net over 80 games (CI-lower ≈ 0.64 > 0.5). First clean self-improvement-beyond-distillation signal — absent on 4³.
- **Absolute S5 (classical translation) — NOT MET; the gain did not translate.** Champion vs classical at the seed's matched points (32 games each): net@48 **0.219** [0.11,0.388] (seed 0.194) and net@512 **0.50** [0.332,0.668] (seed 0.50). Statistically identical to the seed — still parity@512, still losing@48.
- **Methodology finding (recorded to `bold-pine-0367`):** a frozen, drift-proof anchor prevents the gate being fooled by a *moving* reference, but net-vs-net improvement is opponent-specific and overstates strength vs an OOD baseline (classical). Beating the in-family frozen net 0.735 moved the absolute needle vs classical by ~0. **Absolute strength must be measured against the OOD opponent, not inferred from the in-family gate.**
- **Stop reason: `objective_met`** for the PASS-14 probe (question answered: relative yes, absolute no).

## Run contract (refreshed — Phase 3, EXECUTING)
- **Objective:** unchanged — a 3D-Go agent meeting Success-bar-v2 (S1–S5); current open gaps = S1 (budget-dominance) and S5-absolute (beat the teacher in absolute terms).
- **Decision criterion:** per Success-bar-v2 `fdb07ec9`.
- **Start nodes (refreshed):** INFRA-3 `8a724b1c` (5³ result), PROOF-2 `75615ad2` (search scaling amplifies w/ board size), agenda `snowy-term-0287`, hub `e917c9e4`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free).
- **Lookahead n=2; frontier width k=2.**
- **Terminal condition:** Success-bar-v2 met, OR no non-redundant branch justifies remaining budget.

## Next frontier (refreshed lookahead, n=2/k=2)
PASS-14's negative says plain self-play against a frozen *net* anchor does not lift absolute strength on 5³. Two non-redundant continuation branches:
- **[PRIMARY] Hybrid classical-anchored self-play on 5³** — gate promotion on `cand_vs_classical@48` (the OOD objective the absolute metric actually measures), not `cand_vs_frozen-net`. Directly tests the PASS-14 hypothesis: does optimizing the right proxy lift absolute strength? Cost: per-iter classical eval ~4 min (we just measured it) + ~10–15 min self-play/iter → ~1.5–2h for 8 iters, $0/local. Staged as the graph-local continuation point.
- **[SECONDARY] ALGO-2 (arch / value-target scaling)** — raise the absolute ceiling via capacity rather than search, the lever for S1 budget-dominance; orthogonal to the self-play objective question. `gentle-glitter-1363`.
- **Rejected this hop:** another plain-frozen-net self-play run (PASS-14 shows the proxy is the problem, not the iteration count → redundant); 7³ net-vs-classical (classical unrunnable on 7³, established PASS-13 → no absolute anchor exists there).

**Stop reason (this pass): `objective_met`** for PASS-14; frontier refreshed, primary continuation staged. Loop resumes graph-locally at the hybrid-anchor 5³ branch.


## PASS 15 RESULT — classical-anchored self-play on 5³ (INFRA-3 RUN 3) → apparent lift was NOISE; S5-absolute NOT met [node `b3ea0b95`]
- **Executed the refreshed PRIMARY branch.** New variant `az_selfplay_clsmp.py` anchors the promotion gate on **cand-vs-CLASSICAL** (the OOD objective PASS-14 identified as missing), made tractable on 5³ by routing the classical eval through the parallel `net_vs_classical_mp` harness (~4 min/eval; the sequential in-loop path stalled >40 min/eval — confirmed and worked around). Same seed/board/sims/iters as PASS-14.
- **In-loop (n=32) reported a win:** it1 promoted on cand-vs-cls@48 0.194→0.406; a first n=32 @512 translation read 0.594 [0.423,0.745]. **Both were small-sample.**
- **Well-powered n=128 A/B OVERTURNS it:**

  | vs classical (n=128) | @48 | @512 |
  |---|---|---|
  | seed | 0.234 [0.168,0.316] | 0.414 [0.332,0.501] |
  | cls-anchored champion | 0.262 [0.193,0.345] | 0.402 [0.32,0.489] |

  Champion ≈ seed at both sim levels (CIs fully overlap). The 0.406/0.594 were noise; the gate **promoted on a 32-game fluctuation**. **S5-absolute NOT met on 5³** — neither the frozen-net gate (PASS-14) nor the classical gate (PASS-15) beats classical better than plain distillation. The distilled net ≈ champion ≈ ~0.40–0.41 vs classical@512 (just below parity).
- **Campaign-wide correction (→ methodology `dcd0a5db`):** n≈24–32 win-rate evals have ±0.16 CIs — too wide for the distinctions drawn from them. Even the seed's headline "5³ parity@512 = 0.50" [e7c35c64, n=32] is **0.414 [0.332,0.501] at n=128** (just below parity). Prior n≤32 win-rates should be read as point estimates with ±0.16 error bars; gate/claim on n≥128.
- **Stop reason: `objective_met`** for PASS-15 (question decisively answered — negative).

## Run contract (refreshed) + next frontier (n=2/k=2)
- **Objective unchanged** (Success-bar-v2 S1–S5). New evidence: self-play does NOT lift absolute strength on 5³ → the lever for S1/S5 is **capacity, not more self-play**.
- **Budget:** 0 USD / $0-local (RTX 5090 + 16c/32t free). **Lookahead n=2; frontier width k=2.**
- **Next branches:**
  - **[PRIMARY] ALGO-2 — architecture / value-target scaling `gentle-glitter-1363`.** Raise the absolute ceiling via capacity (bigger/better net), the lever PROOF-1/PASS-15 point to for S1 budget-dominance, since search and self-play are exhausted on 5³.
  - **[SECONDARY] Re-power the campaign's key win-rate claims at n≥128** — cheap, high-integrity audit: re-measure the 4³ beat-classical headline [b71da32b, 0.612] and the 5³ "parity@512" at n=128 to confirm which survive. Directly motivated by PASS-15's small-sample finding.
  - **Rejected this hop:** further 5³ self-play (both gates exhausted — PASS-14/15); 7³ classical baseline (unrunnable, PASS-13); managed compute ($0/local).
- **Stop reason (this pass): `objective_met`** for PASS-15; frontier refreshed. Loop resumes graph-locally at ALGO-2 (primary) / n≥128 re-power audit (secondary).


## PASS 16 — frontier EXPANSION (seeding pass, NOT executed)
- **User-directed graph/docs seeding pass** to *widen the frontier before the next execution pass*: mine 3 external repos for transferable methods/benchmarks and seed the graph with many pickable STAGED branches. **No experiments run; no `neural/` or engine code changed** (npm 48/48 + engine cross-vals unaffected by construction).
- **Delivered:** 2 external-reference nodes (KataGo methods `365b153f-75e1-54ee-9344-4794604da3a4`, online-go review-UI `ba69d0a3-f344-5413-8b0f-e4d65aa947bc`); a LIVING **EXPANSION index** `f9f2bf74-2ce6-5488-b471-dc0b6c422b99` (status table + recommended what-may-work ordering); **17 STAGED direction nodes** (AUX-1..4 aux heads, SEARCH-1..5, ARCH-1..3, EVAL-1..3, SCI-1, TOOL-3) as a proper multi-parent DAG (each = its result-node(s) + the index); `docs/DIRECTIONS.md` companion + `AGENTS.md` pointer; light edits to hub `e917c9e4` / agenda `6148c5c0` / autogo `b4fd8252`.
- **Guidance (what may work):** the campaign's own evidence (PASS-15 `b3ea0b95`) says S1/S5 = **signal richness + capacity, not more search/self-play**. Recommended order: **(1) aux targets first** — AUX-1 ownership / AUX-2 score / AUX-3 soft-policy (hit the komi-flat `2a2ca6b9` + policy-weak `0bc38c41` scars; cheapest high-upside, pure training change); **(2)** richer input planes ARCH-3 + capacity ARCH-2; **(3) EVAL-1 SPRT + n≥128 re-power audit — alongside everything**; then SEARCH-1 score-aware play, the SEARCH-2/3/4 Elo levers, ARCH-1 size-agnostic keystone, EVAL-2 solver, EVAL-3 scaling-law.
- **Next branches (refreshed):** the two prior open branches (ALGO-2 capacity `792c4ec2`, n≥128 re-power audit) are now subsumed/sharpened by **AUX-1/2/3 + ARCH-2/3 (capacity & signal)** and **EVAL-1 (SPRT + re-power audit)** respectively. High-value core to pick first: **AUX-1, AUX-2, AUX-3, ARCH-3, EVAL-1**; ARCH-1 + EVAL-2 as the keystone/solver builds.
- **Stop reason: `seeding_complete`** — frontier widened, menu staged; loop resumes by *executing* a picked branch (default first pick: AUX-1 or AUX-2).

## PASS 17 — EXECUTION of the EXPANSION menu begins (rolling campaign) [LIVING]
- **Trigger:** human re-invoked `/flywheel-auto` and chose **"Rolling campaign"** scope — keep picking & executing the highest value/cost EXPANSION branch, replanning after each, $0/local-only, until no non-redundant branch justifies remaining local effort.
- **Graph-coherence check:** the working tree's uncommitted `az_cls5`/`seed5` `*_n128.json` are the **PASS-15** artifacts (cls-anchored champion `best_az_cls5_5cubed.pt` + seed), already recorded in node `b3ea0b95` (the n=128 table above). NOT a new pass — they are git-uncommitted prior artifacts (housekeeping for the human; commits remain the user's call). No PASS-15 re-record needed.

## Run contract (refreshed — PASS 17, EXECUTING, rolling campaign)
- **Objective:** advance the Phase-3 frontier toward a *provably stronger* net (Success-bar-v2 S1/S5) by executing the highest value/cost EXPANSION-menu branch, beginning with the aux-target cluster the campaign's evidence prioritizes (signal richness + capacity, NOT more search/self-play — PASS-15 `b3ea0b95`).
- **Decision criterion:** each picked branch resolves at its own node's CI-based n≥128 criterion (e.g. AUX-1: ownership-augmented net beats the bare policy+value baseline vs classical at n≥128 with non-overlapping Wilson CIs, OR — if strength flat — value-MSE drops with CI separation AND end-game ownership acc > 0.8).
- **Start nodes:** EXPANSION index `f9f2bf74` (slug `proud-king-2753`); first pick **AUX-1 ownership head `665706e4-f3f0-5331-8031-f9b98412b79a`** (`proud-star-4959`); hub `e917c9e4`; agenda `6148c5c0`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free; $10 credit balance deliberately UNTOUCHED per CLAUDE.md).
- **Lookahead n=1; frontier width k=1** (rolling: one branch to resolution, then replan to the next-highest value/cost branch; menu order AUX-1 → AUX-2 → AUX-3 → ARCH-3/2 → EVAL-1 alongside).
- **Terminal condition:** no non-redundant EXPANSION branch justifies the remaining local effort (or Success-bar-v2 met). Per-branch stop_reason recorded as each resolves.
- **Stop reason:** (pending — execution in progress).

### AUX-1 (in progress) — per-voxel ownership head
- **Build:** added `Board.ownership_map()` (additive engine method; per-voxel Tromp-Taylor owner, reuses the score flood-fill; logged in VENDORED.md) + `collect_ownership.py` (distill data WITH ownership labels signed to side-to-move, matching Z). Ownership labels validated exact vs `score_tromp_taylor` (black/white area == ±1 cell counts).
- **A/B plan (4³ first):** regenerate 4³ distill data with ownership (384 games, classical teacher @128 playouts) → train baseline (policy+value) AND ownership-augmented (policy CE + value MSE + λ·ownership-MSE, λ swept) on the *same* data/seed → A/B both vs classical at n≥128; compare value-MSE + end-game ownership accuracy. Then 5³ if 4³ promising.


## PASS 17 — AUX-1 RESOLVED + replan to AUX-3 (rolling campaign)
- **AUX-1 (ownership head) RESOLVED** [node `665706e4` / `proud-star-4959`, rev 4, artifacts attached].
  - **Built (additive):** `Board.ownership_map()` (logged in VENDORED.md), `collect_ownership.py`, `net_ownership.py` (`A3GoNetOwn` = A3GoNet byte-for-byte + ownership head; lambda=0 baseline == plain net, same init), `train_ownership.py`.
  - **Result:** ownership head **learns the territory map** (holdout own_acc **0.983–0.986** vs ~0.50 random; fresh played-game sign-agreement **0.927** >> 0.8 bar — see heatmap artifact). But it does **NOT decisively lift 5³ strength**: pooled 3-seed s512 baseline **0.328** [0.282,0.377] vs ownership **0.393** [0.346,0.443] — **+6.5pp, Wilson CIs OVERLAP**, and 1/3 seeds reverses; 4³ flat; neither beats classical. Value-MSE only mixed/weakly favorable (s1 0.0248→0.0177, s2 0.0252→0.0228, but seed0 0.0144→0.0173, no CI).
  - **Verdict:** decision criterion **NOT met** → **NEGATIVE for the strength/calibration hypothesis on 5³, POSITIVE deliverable** (a working ownership predictor → unblocks TOOL-3 heatmap + SCIENCE-2 life&death). **branch stop_reason = `objective_met`** (clean answer; hypothesis negative-with-deliverable).
  - **Sharpened scar:** the 5³ ceiling is set by the **starved POLICY head** (holdout policy_acc ~**0.06**, the only metric trending the WRONG way as boards grow — scaling-law `0bc38c41`) + absolute capacity, NOT by lack of a dense aux target. An aux head alone can't move absolute strength when policy supervision is the binding constraint.
- **REPLAN (evidence-driven re-prioritization):** AUX-1 says attack the **policy head directly**, so promote **AUX-3 (soft policy target T≈4, ×8 weight, prune)** to PRIMARY ahead of AUX-2 (score head — would likely repeat AUX-1's 'learns-fine/strength-flat' unless paired with a policy fix). Data supports it: distill collector already exposes raw MCTS visit counts (P = visits^(1/temp)/sum).

## Run contract (refreshed — PASS 17, EXECUTING, rolling campaign)
- **Objective:** advance toward a provably stronger net by executing the highest value/cost EXPANSION branch; after AUX-1, target the binding constraint (policy head) per the campaign's own evidence.
- **Decision criterion:** each branch resolves at its node's CI-based n≥128 criterion. AUX-3: soft-target net beats hard-target baseline vs classical with CI separation on ≥1 board size, OR holdout policy accuracy improves with CI separation on 5³ with no strength regression.
- **Start nodes:** EXPANSION index `f9f2bf74` (`proud-king-2753`); current pick **AUX-3 soft policy `c017760b-671f-54f1-951d-50887754dad7`** (`snowy-brook-3358`); hub `e917c9e4`; agenda `6148c5c0`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free; $10 credit balance UNTOUCHED per CLAUDE.md).
- **Lookahead n=1; frontier width k=1** (rolling: one branch to resolution, then replan). Menu after AUX-3: AUX-2 → ARCH-3/2 (capacity/planes) → EVAL-1 (SPRT) alongside.
- **Terminal condition:** no non-redundant EXPANSION branch justifies remaining local effort (or Success-bar-v2 met). Per-branch stop_reason recorded as each resolves.
- **Stop reason:** AUX-1 branch = `objective_met`; campaign continues — executing AUX-3.

## PASS 17 — AUX-3 RESOLVED + meta-finding + replan to ARCH-2 (capacity)
- **AUX-3 (soft policy target) RESOLVED** [node `c017760b` / `snowy-brook-3358`, rev 3, artifacts attached].
  - **Built (train-only):** `collect_softpolicy.py` (stores RAW MCTS visit counts; regenerated 5³ data = **52,901 ex**, classical@128), `train_softpolicy.py` (clean A/B: HARD argmax-1x vs SOFT prune+visits^(1/4)+8x weight, same data/seed, plain A3GoNet 64×6).
  - **Result (5³, net@512 vs cls@48, n=128, 3 seeds, pooled):** HARD 0.269 [0.227,0.316] vs SOFT **0.298** [0.254,0.345]. Soft beats hard on **all 3 seeds** (+4.7/+2.3/+1.5pp) and has **lower value-MSE on all 3 seeds**, but **Wilson CIs OVERLAP** → consistent-but-NOT-decisive. **Neither beats classical at 5³.** (top1/top3-vs-argmax favors hard by construction — not a fair metric.)
  - **Verdict:** decision criterion **NOT decisively met** → consistent-but-marginal POSITIVE. **branch stop_reason = `objective_met`**.
- **META-FINDING (AUX-1 ⊕ AUX-3):** two independent **target/auxiliary-representation** changes — dense ownership (AUX-1) and softened+weighted policy (AUX-3) — each give **small, consistent, non-decisive** gains, and **neither makes the 64×6 net beat classical at 5³.** ⇒ The 5³ absolute-strength ceiling is **NOT set by how the net is supervised** (target representation). Remaining untried levers: **input representation** (ARCH-3 richer planes — what the net SEES) and **raw capacity / capacity-per-flop** (ARCH-2 nested-bottleneck, ALGO-2). **PIVOT from target-tweaks to architecture/capacity.**
- **REPLAN:** promote **ARCH-2 (nested-bottleneck blocks + fixed-variance/fixup init, drop BN) `8cecf366-472e-5450-89c6-b149b3ed36f3`** to PRIMARY — train-only, no engine risk, directly tests the leading 'capacity is the lever' hypothesis (the move that first beat classical was 32×3→64×6, `b71da32b`). ARCH-3 (richer input planes) SECONDARY. AUX-2 (score head) deprioritized — would likely repeat the aux-cluster's marginal pattern.

## Run contract (refreshed — PASS 17, EXECUTING, rolling campaign)
- **Objective:** advance toward a provably stronger net; having exhausted target/supervision representation (AUX-1, AUX-3), attack capacity/architecture.
- **Decision criterion:** ARCH-2 — at matched **wall-clock** budget the nested-bottleneck/fixup net beats the BN 64×6 baseline vs classical with CI separation on ≥1 board size (or matches strength at lower FLOPs). Hold the TARGET fixed (reuse AUX-3 soft target + the 52,901-ex data) so only architecture varies.
- **Start nodes:** EXPANSION index `f9f2bf74` (`proud-king-2753`); current pick **ARCH-2 `8cecf366`**; hub `e917c9e4`; agenda `6148c5c0`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free; $10 credit UNTOUCHED).
- **Lookahead n=1; frontier width k=1** (rolling). Menu after ARCH-2: ARCH-3 (input planes) → EVAL-1 (SPRT) alongside → AUX-2.
- **Terminal condition:** no non-redundant EXPANSION branch justifies remaining local effort (or Success-bar-v2 met). Per-branch stop_reason recorded as each resolves.
- **Stop reason:** AUX-1 = `objective_met`; AUX-3 = `objective_met`; campaign continues — executing ARCH-2.

## PASS 17 — ARCH-2 RESOLVED + THREE-BRANCH META-CONCLUSION (cheap-tweak cluster exhausted)
- **ARCH-2 (BN-free nested-bottleneck + fixed-variance init) RESOLVED** [node `8cecf366`, rev 3, artifacts attached].
  - **Built (train-only; net.py UNCHANGED → 48/48 + cross-vals safe):** `net_arch2.py` `A3GoNetBR` (nested-bottleneck blocks, NO BatchNorm anywhere; c=64/cb=48/8blk = **1.13M params vs BN-64×6 1.41M**), trained on the SAME AUX-3 data + soft target so only architecture varies.
  - **Result (5³, net@512 vs cls@48, n=128, 3 seeds, pooled):** ARCH-2 **0.303** [0.259,0.351] vs BN-64×6 **0.298** [0.254,0.345] → **STRENGTH PARITY** (CIs overlap; neither beats classical). Value-MSE matches; policy-top1 LAGS (value head carries parity). **Clean speed: 0.87× — ARCH-2 13% SLOWER per CPU eval game** (more sequential conv layers) despite ~20% fewer params → no per-wallclock win. ReZero gamma=0 init too slow; **gamma0=0.3 needed** (node-flagged init risk confirmed).
  - **Verdict:** criterion NOT met → parity, no advantage. **branch stop_reason = `objective_met`**.
- **META-CONCLUSION (AUX-1 ⊕ AUX-3 ⊕ ARCH-2) — 3/3 non-decisive:** three independent cheap levers — dense ownership target (AUX-1), softened+weighted policy target (AUX-3), BN-free capacity-per-FLOP architecture (ARCH-2) — **all fail to push the 5³ net past classical**, each parity-to-marginal. The 5³ absolute-strength ceiling is **ROBUST to target-representation AND to capacity-reshaping at fixed scale.** The cheap-representational-tweak cluster is **EXHAUSTED.**
- **Genuinely-different remaining levers (none yet tried):** **(1) ARCH-3 richer INPUT planes** (history/liberties/ko-ban/capture-parity — change what the net SEES; train-side + light feature extraction); **(2) raw SCALE-UP** (96×8/128×10 + more teacher data — the literal 32×3→64×6 move that worked, `b71da32b`; gated on slow Python data-gen ~50min/dataset); **(3) stronger teacher/search** (data ceiling); **(4) the C++ engine** for 7³+ scale (large discrete effort, prior passes already flagged for human go/continue).
- **REPLAN / FRONTIER (1 hop ahead, staged & resumable):** next pick = **ARCH-3 richer input planes `bcf93cd3-8d8b-5924-a570-3232f7f1d065`** (most-distinct untried lever, attacks input not supervision). SECONDARY = capacity SCALE-UP (bigger net + more data). **SURFACED FOR HUMAN:** the cheap-tweak cluster is exhausted (3/3); the next real strength leap likely needs **scale (net+data)** or the **C++ engine** — a larger discrete effort worth a human go/continue, consistent with the PASS-8 C++-gating precedent.

## Run contract (refreshed — PASS 17 pass-boundary; campaign CONTINUES, resumable at ARCH-3)
- **Objective:** advance toward a provably stronger 5³ net (Success-bar-v2 S1/S5). Cheap target/arch tweaks exhausted (AUX-1/AUX-3/ARCH-2); next = input representation (ARCH-3) then scale.
- **Decision criterion:** ARCH-3 — at n≥128 the richer-input net beats the 3-plane baseline vs classical with CI separation on ≥1 board size, OR holdout policy/value improves with CI separation + no strength regression.
- **Start nodes:** EXPANSION index `f9f2bf74`; next pick **ARCH-3 `bcf93cd3`**; hub `e917c9e4`; agenda `6148c5c0`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free; $10 credit UNTOUCHED).
- **Lookahead n=1; frontier width k=1** (rolling). Menu after ARCH-3: capacity SCALE-UP / EVAL-1 SPRT / AUX-2 / (C++ engine = human-gated).
- **Terminal condition:** no non-redundant branch justifies remaining local effort (or Success-bar-v2 met). NOT reached — ARCH-3 is viable & non-redundant.
- **Stop reason (PASS 17 branches):** AUX-1 = `objective_met`; AUX-3 = `objective_met`; ARCH-2 = `objective_met`. **Campaign NOT terminated** — pass boundary; next pass resumes graph-locally at ARCH-3. (Human checkpoint surfaced: scale-up vs C++ engine for the next real leap.)

## PASS 18 — ARCH-3 EXECUTION (richer input planes) [EXECUTING, rolling campaign]
- **Graph-local continuation** (re-invoked /flywheel-auto): top staged frontier pick = **ARCH-3 `bcf93cd3`** (richer input planes) — the most-distinct untried lever (attacks INPUT representation, not target/capacity) after the cheap-tweak cluster (AUX-1/AUX-3/ARCH-2) was exhausted 3/3 in PASS-17. Terminal condition NOT reached (ARCH-3 viable & non-redundant).
- **Hypothesis:** the 5³ ceiling is partly a representational gap — the net is blind to ko (ubiquitous in 3D, `31dae43b`), per-group liberties, and move history. Hand it KataGo-style planes and absolute strength vs classical should rise.
- **Built (all additive; npm 48/48, crossval 60/60 3³+4³, base planes == net.encode byte-for-byte):**
  - `a3go_engine.py`: additive `last_move`/`last_move2` tracking (init/play/play_fast/pass/clone) — rules-neutral; a3go-authored Python port (VENDORED.md tracks the TS engine only, unaffected).
  - `input_planes.py`: canonical 10-plane stack [0=B,1=W,2=stm,3=koban,4=lib1,5=lib2,6=lib3+,7=capture,8=last,9=2ndlast] + per-config channel slices. **ko-ban is CAPTURE-AWARE** (validated over 12k positions: koban ⊆ engine-illegal, and every ko ban on 4³ is a recapture-capture — a naive `zobrist^Z[cell]` test would have MISSED exactly the prime suspect).
  - `net_arch3.py` `A3GoNetIn` (configurable in_planes; in_planes=3 == A3GoNet byte-for-byte → clean control); `collect_arch3.py` (re-runs the SAME deterministic AUX-3 soft-policy games, storing the full stack), `train_arch3.py`, `eval_arch3.py` (BatchedMCTS subclass swaps only the encoder), `arch3_pipeline.sh`, `arch3_finalize.py`.
- **Design (clean A/B):** SAME data-gen seeds + soft target (T=4,W=8,prune=0.02) + trunk (A3GoNet 64×6) + protocol (5³, net@512 vs cls@48 cap50, n=128, seeds 0/1/2 pooled) as AUX-3/ARCH-2 — ONLY the input representation varies. Configs: base(3) / all(10) headline + per-group ablations koban/libs/capture/history for attribution if a gain appears. Augmented adds only ~12k params (a genuine INPUT change, not capacity).
- **Decision criterion (`bcf93cd3`):** at n≥128 the richer-input net beats the 3-plane baseline vs classical with CI separation on ≥1 board size, ablation isolating which planes carry it; OR holdout improves with CI separation + no strength regression.
- **Status: EXECUTING** ($0/local, RTX 5090 + 32t free): pipeline = collect 5³(384g@128) → train 6cfg×3seed → eval base+all×3seed. Per-seed JSONs + idempotent `arch3_pipeline.sh` make it resumable. **Stop reason: (pending — execution in progress).**

## Run contract (refreshed — PASS 18, EXECUTING, rolling campaign)
- **Objective:** advance toward a provably stronger 5³ net (Success-bar-v2 S1/S5) by attacking the INPUT representation (ARCH-3), the most-distinct untried lever after target/capacity tweaks were exhausted 3/3 (P17).
- **Decision criterion:** per ARCH-3 `bcf93cd3` (n≥128, CI separation vs baseline + ablation attribution).
- **Start nodes:** EXPANSION index `f9f2bf74` (`proud-king-2753`); current pick **ARCH-3 `bcf93cd3`**; hub `e917c9e4`; agenda `6148c5c0`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free; $10 credit UNTOUCHED per CLAUDE.md).
- **Lookahead n=1; frontier width k=1** (rolling). Menu after ARCH-3: capacity SCALE-UP / EVAL-1 SPRT / AUX-2 / (C++ engine = human-gated).
- **Terminal condition:** no non-redundant branch justifies remaining local effort (or Success-bar-v2 met). Per-branch stop_reason recorded as each resolves.
- **Stop reason:** AUX-1/AUX-3/ARCH-2 = `objective_met` (P17); ARCH-3 = (pending — EXECUTING).

## PASS 18 — ARCH-3 RESOLVED · FIRST DECISIVE POSITIVE · liberties carry it · prior conclusion REVISED
- **ARCH-3 (richer input planes) RESOLVED** [node `bcf93cd3` rev3, artifacts: arch3_ab_summary.json + arch3_attribution.png]. **Decision criterion MET** — the FIRST EXPANSION branch to beat its 3-plane baseline decisively.
- **Result (5³, net@512 vs cls@48, n=128×3 seeds pooled ≈384; SAME data/soft-target/trunk as AUX-3/ARCH-2, only INPUT varies; base reproduces AUX-3 baseline 0.305≈0.298 → control validated):**

  | input cfg | winrate vs classical | Δ vs base | CI-sep |
  |---|---|---|---|
  | base (3: B/W/stm) | 0.305 [0.261,0.353] | — | — |
  | +ko-ban (4) | 0.278 [0.235,0.324] | −0.027 | no |
  | +capture (4) | 0.333 [0.287,0.381] | +0.028 | no |
  | +history (5) | 0.356 [0.310,0.406] | +0.051 | no |
  | all (10) | 0.411 [0.363,0.461] | +0.106 | **YES** |
  | **+liberties (6)** | **0.449 [0.400,0.499]** | **+0.144** | **YES** |

- **Attribution (ablation):** **per-group LIBERTY planes carry the ENTIRE gain (+0.144) — the strongest single arm, even beating the full 10-plane stack (0.449 > 0.411).** Handing the net the atari/safety signal directly is the lever (3D 6-connectivity makes liberties hard to infer from raw stones). **ko-ban does NOT help on 5³** (−0.027, only negative arm) — the KataGo "ko-ban prime suspect" prior is **FALSIFIED at this board size** (ko too sparse; validated capture-aware koban ⊆ engine-illegal but rare). capture/history give mild non-decisive lifts; the kitchen-sink `all` is DILUTED vs liberties-alone → **focused high-signal features beat a feature dump.**
- **No cost:** augmented net +12k params (0.85%) and SAME wall-clock (0.045 g/s) → a genuine INPUT-representation effect, not capacity/speed. All 3 seeds improve (libs 0.383/0.422/0.543, every seed > baseline best 0.320) → not a lucky-init artifact. **branch stop_reason = `objective_met` (decisive POSITIVE).**
- **CAMPAIGN CORRECTION (overturns the PASS-17 surfaced conclusion):** the cheap-tweak cluster was **NOT exhausted**. The 5³ ceiling is robust to target-representation (AUX-1/AUX-3) and to capacity-reshaping at fixed scale (ARCH-2), but **NOT to INPUT representation** — liberty planes lift it +0.144, to the doorstep of parity (0.449, upper CI 0.499). The "next leap needs scale/C++" call was premature: a cheap, train-side input change moved absolute strength for the first time. Still short of beating classical absolutely (libs lo 0.400 < 0.5).
- **Built (all additive; npm 48/48, crossval 60/60 3³+4³, base planes == net.encode byte-for-byte):** `input_planes.py` (10-plane stack + per-config slices, capture-aware ko-ban), `net_arch3.py` `A3GoNetIn` (in_planes=3 == A3GoNet byte-for-byte), `collect_arch3.py`/`train_arch3.py`/`eval_arch3.py`, `arch3_pipeline.sh`/`arch3_ablation.sh`/`arch3_finalize.py`; engine `last_move`/`last_move2` (rules-neutral; Python port, VENDORED.md unaffected). ~17h compute, $0/local.

## Run contract (refreshed — PASS 18 boundary; campaign CONTINUES, resumable at the liberty-scale-up branch)
- **Objective:** push the now-working liberty-input net from 0.449 to **beat classical absolutely on 5³** (S1/S5: CI-lower > 0.5), then generalize. Lever found: INPUT (liberties); combine with the capacity/sims/board-size axes.
- **Decision criterion:** liberty-input net beats classical with CI-lower > 0.5 at n≥128 on ≥1 board size (absolute S1/S5), OR a properly-powered characterization of how far each axis closes the remaining 0.05 gap.
- **Start nodes:** EXPANSION index `f9f2bf74` (`proud-king-2753`, P18-annotated); resolved ARCH-3 `bcf93cd3`; hub `e917c9e4`; agenda `6148c5c0`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free; $10 credit UNTOUCHED per CLAUDE.md).
- **Lookahead n=1; frontier width k=1** (rolling).
- **Terminal condition:** Success-bar-v2 met, OR no non-redundant branch justifies remaining local effort. NOT reached — a hot, cheap lead (liberty input near parity) is open.

## Next frontier (refreshed lookahead, n=1/k=1) — staged & resumable
- **[PRIMARY] Liberty-input + CAPACITY scale-up** — the literal "scale capacity" lever (PROOF-1/PASS-15) now has a *working feature substrate*. Train a bigger net (96×8 / 128×10) on the liberty input (cfg=`libs`), eval vs classical@48 n≥128. Cheapest path to actually cross parity on 5³. (Reuse `net_arch3.A3GoNetIn` with larger ch/blk; data already collected.) Also try libs at net@1024 (cheap, sims-only). Extends ALGO-2 `792c4ec2`.
- **[SECONDARY] Liberty-input on 7³** — where cross-board value calibration is cleanest (value-MSE smallest, `0bc38c41`) and search scaling amplifies with board size (PROOF-2 `75615ad2`); liberties may cross parity more easily on the genuinely-3D board. Needs 7³ rich-plane collect (C++ engine data-gen available).
- **[CHEAP] Liberty-encoding refinement** — split my-vs-opp liberty planes / finer buckets; ko-ban revisit on 7³ (where ko frequency rises, `31dae43b`).
- **Rejected this hop:** ko-ban-focused work on 5³ (falsified); kitchen-sink all-planes (diluted vs libs); more target-rep/self-play (exhausted P14/15/17); managed compute ($0/local).
- **Stop reason (PASS 18): `objective_met`** for ARCH-3 (decisive positive). **Campaign NOT terminated** — pass boundary; next pass resumes graph-locally at the liberty-scale-up branch. **HUMAN CHECKPOINT surfaced:** ARCH-3 overturns the P17 'needs scale/C++' call — a cheap input change works; recommend continuing the liberty-scale-up push at $0/local before any managed-compute consideration.

## PASS 19 — SCALE-libs EXECUTING (capacity scale-up on the winning liberty input)
- **Graph-local continuation** (re-invoked /flywheel-auto): executing the staged PRIMARY branch from the P18 replan = **SCALE-libs `faddae67`** (`bitter-pine-2861`), child of ARCH-3 `bcf93cd3` + ALGO-2 `792c4ec2` + index `f9f2bf74`.
- **Question:** ARCH-3 found liberty input lifts 5³ to 0.449 (doorstep of parity). Does the PROVEN capacity lever (32×3→64×6 first beat classical, `b71da32b`) on `cfg=libs` cross parity (CI-lower > 0.5)?
- **Method (only CAPACITY varies):** train `A3GoNetIn` cfg=libs at **96×8 (4.08M params)** and **128×10** (×3 seeds) on the SAME data + soft target; eval 96×8 ×3 vs classical@48 n=128 net@512 (same protocol as ARCH-3's libs@64×6 0.449 baseline). 128×10 eval deferred (agent-in-loop on the 96×8 signal).
- **Binding constraint surfaced:** big-net CPU eval is the wall (96×8@512 ≈ 2.9h/seed; the net forward dominates once channels grow — INFRA-1's "forward ~10%% of move time" held only for 64×6). → a **GPU-batched net-vs-classical eval harness** (net on GPU batched across games + classical on CPU) is the infra unblock for the whole capacity/sims/7³ liberty program; staged for a future pass.
- **Status: EXECUTING** ($0/local). Idempotent `arch3_scale.sh`, per-seed JSONs resumable. **Stop reason: (pending).**

## Run contract (refreshed — PASS 19, EXECUTING, rolling campaign)
- **Objective:** push the liberty-input net from 0.449 to beat classical absolutely on 5³ (S1/S5, CI-lower>0.5) via capacity, OR characterize how far capacity closes the ~0.05 gap (capacity curve 64×6→96×8→128×10 on fixed liberty input).
- **Decision criterion:** scaled libs net CI-lower>0.5 vs classical@48 n≥128 on 5³, OR powered capacity-curve characterization.
- **Start nodes:** SCALE-libs `faddae67`; ARCH-3 `bcf93cd3`; EXPANSION index `f9f2bf74`; hub `e917c9e4`; agenda `6148c5c0`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free; $10 credit UNTOUCHED).
- **Lookahead n=1; frontier width k=1** (rolling).
- **Terminal condition:** Success-bar-v2 met, OR no non-redundant branch justifies remaining local effort. NOT reached.
- **Stop reason:** ARCH-3 = `objective_met` (P18, decisive +); SCALE-libs = (pending — EXECUTING).

## PASS 19 — SCALE-libs RESOLVED + METHODOLOGY PIVOT (net-vs-classical → GPU net-vs-net + SPRT)

**The wall, named.** PASS-19 began the staged SCALE-libs capacity scale-up but hit the campaign's real bottleneck: net-vs-classical strength eval runs the net on **CPU at net@512 (~3 h/seed)** — the in-flight 96×8 eval would have blocked ~9 h with no interim signal. Code audit: cost is (a) classical's CPU rollouts, (b) Python per-node engine ops in the net's own MCTS tree, (c) the net forward on CPU — a GPU net-vs-classical harness buys only ~2.5×. **Fix is a methodology change, not a faster version of the same thing.**

**The pivot (the unblock, now built & validated):**
- **GPU net-vs-net Elo screen** `screen_nvn.py` — both sides batched on GPU, no classical rollouts; round-robin over the lever family → Bradley-Terry Elo (reuses `ladder.py` fitter, `eval_arch3._RichMCTS` encoder pattern), ×3 seeds pooled. Screens *relative* strength in **~38 min** (vs ~9 h CPU), streaming per-pair.
- **Encoder speedup** `input_planes.config_planes` now lazily computes only a config's channels (skips the per-empty-cell ko/capture loop for base/libs) — **byte-identical** to `rich_planes` (`test_input_planes.py`, 960 cases), 4.5× faster for libs / 119× for base. Also speeds the SPRT anchor.
- **SPRT-bounded classical anchor** `sprt.py` (= EVAL-1 `259c2ebe`): wraps net-vs-classical in a sequential probability ratio test (H0 ≤parity vs H1 >parity) that early-stops; reserved for anchoring a confirmed net-vs-net winner. n≥128 re-power audit baked in.
- Engine untouched / additive Python only → `npm test` 48/48, `crossval.py` 60/60, encoder identity 960/960 all green.

**SCALE-libs result (`faddae67`) — NULL: capacity is not the 5³ lever, and over-scaling hurts.** Net-vs-net Elo (anchor base=0, sims=24, 48 games/pair, 3 seeds; sanity gate PASSED — base-vs-libs 0.333 reproduces the ARCH-3 classical direction libs>base):

| agent | Elo | CI95 |
|---|---|---|
| libs96×8 (4.08M) | 78.6 | [19.4, 143.4] |
| libs@64 (1.42M)  | 70.9 | [17.7, 134.9] |
| all (64×6, 10pl) | 25.2 | [−38.9, 89.9] |
| base (64×6, 3pl) | 0.0  | anchor |
| libs128×10       | −11.0 | [−68.6, 51.3] |

libs@64 ≈ libs96×8 (tied top, CIs coincident; head-to-head 0.521); **libs128×10 over-scales to the bottom, below the 3-plane base** (loses libs96×8 0.717) — under-trained for its capacity on the same ~20-min data budget. Extends the campaign 5³ ceiling (PASS-15) to the liberty input: liberties reach the doorstep of parity, capacity on top of them is exhausted at 5³. **Stop reason: `objective_characterized`** (capacity-curve null + over-scaling regression). libs@64×6 remains the strongest 5³ net.

## Run contract (refreshed — PASS 19 boundary; campaign CONTINUES, rolling, fast-first)
- **Objective:** keep the frontier moving via a rolling portfolio of FAST explorations (minutes–tens-of-minutes each), each resolving a Flywheel node, screened by GPU net-vs-net; spend a classical anchor (SPRT) only on a confirmed winner. No single step locks into hours of idle CPU eval.
- **Resolved this pass:** SCALE-libs `faddae67` (null); methodology infra `screen_nvn.py` + `sprt.py` + lazy `config_planes` delivered (serves EVAL-1 `259c2ebe`).
- **Decision criterion:** net-vs-net Elo CI-separation for relative levers; SPRT CI-lower>0.5 vs classical@48 n≥128 for any absolute "beats classical" claim.
- **1-hop replan (n=1, k=1) — capacity is dead on 5³; pick the highest fast-value branch:**
  1. **Liberty-encoding refinements** (WS2) — my/opp liberty split, finer buckets, liberty-after-move; cheap GPU train + net-vs-net screen. The lever is the *input*, not capacity, so refine the input. *(Recommended next.)*
  2. **Liberties on 7³** — search-scaling amplifies with board size (PROOF-2); capacity may finally have room where it had none on 5³.
  3. **AUX-2 score head `d971bf0e`** on the liberty net — komi-sensitive dense target (addresses komi-flat scar `2a2ca6b9`).
  4. **Fast science (WS3):** EVAL-2 sound superko solver `ebff5f9f` (CPU), ko/seki frequency stats, behavioral "why do liberties help?" (forward-pass only).
- **Budget ceiling:** 0. **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free; $10 credit UNTOUCHED).
- **In flight:** SPRT cross-check of libs@64 vs classical (net@512) — expected `not_a_winner` (sub-parity), cross-checks the 0.449/0.383 fixed-n numbers; resolves EVAL-1 `259c2ebe`.
- **Terminal condition:** Success-bar-v2 met OR no non-redundant branch justifies remaining local effort. NOT reached.
- **Stop reason this pass:** SCALE-libs = `objective_characterized`. Frontier open; next = liberty-input refinement (capacity ruled out).


## PASS 19 — WS1 CLOSED: EVAL-1 SPRT harness resolved
SPRT cross-check finished: `sprt.py` decided **not_a_winner** for libs@64 s0 at decided=98 (llr −3.70 < −2.944), wr 0.337 [0.251, 0.435] — overlaps the s0 fixed-n 0.383 [0.303,0.469] (CI-consistent), confirms libs@64 sub-parity. EVAL-1 `259c2ebe` → rev 2 RESOLVED (artifact sprt_libs64_s0.json); harness validated, reserved for anchoring net-vs-net winners. **Workstream 1 (the methodology unblock) complete:** screen_nvn.py + sprt.py + lazy config_planes built, validated, and both SCALE-libs (null) and EVAL-1 (built) resolved. npm 48/48, crossval 60/60, encoder-identity 960/960 green. **Frontier open; next pick = liberty-input refinements (capacity ruled out on 5³), screened by net-vs-net.**

## PASS-20 (2026-06-18) — STRATEGY PIVOT: BREADTH over depth (user directive); 10 new cheap-first directions seeded
**User redirected the campaign** (recorded as a working rule in AGENTS.md "Breadth over depth — expand the surface, don't grind"): instead of spending long wall-clock grinding one lever (the PASS-19 liberty-refinement + capacity track), **widen the research surface** — seed many new directions, out-of-box solutions, and edge hypotheses as STAGED nodes, biased to minutes-scale forward-pass / engine-only probes that each resolve a node. Stage expensive questions as hypotheses with a crisp decision criterion and move on; spend real compute only where cheap signal already favors a direction.

**Resolved this pass:** widened EXPANSION index `f9f2bf74` (→ rev 20) with **10 NEW STAGED directions** across fresh axes the menu lacked:
- **Interp / no-train:** PROBE-1 `67169cf2` input-plane ablation attribution (which liberty bucket carries the +0.144); PROBE-2 `9867fdd6` value-head calibration (ECE + temp-scaling).
- **Symmetry:** SYMM-1 `3f47168a` order-48 cube group — test-time-augmentation-averaged inference (a free, no-retrain shot at the 0.449→0.5 parity gap that capacity could not close) + 48× data aug.
- **Novel input reps:** REP-1 `42747f38` 3D structural geometry (neighbor-count / dist-to-surface); REP-2 `6ac526b8` move-liberties / self-atari; REP-3 `7a3245ed` my/opp liberty split + finer buckets.
- **Rules science / engine-only:** 3DSCI-2 `a9982d50` tactical-motif census (capture/superko/seki/snapback × board size — quantifies the 98%-ko claim `31dae43b`); 3DSCI-3 `73adb0d5` 3D cyclic-ko pathologies (double-ko / sending-two).
- **Transfer:** TRANSFER-1 `0bbe92d5` zero-shot cross-board 4³→5³→7³ (curriculum unblock for the 7³ wall).
- **Net-vs-search decomposition:** SEARCHX-1 `6551d432` policy-only / value-only / tiny-sim strength curves.

No `neural/` engine code or experiments touched (seeder scripts only: `_seed_nodes.py`, `_update_index.py`); npm 48/48 + crossval 60/60 remain valid.

## Run contract (refreshed — PASS-20 boundary; BREADTH pass, rolling)
- **Objective:** widen the frontier — maintain a diverse menu of pickable, well-posed STAGED bets (out-of-box ideas, edge hypotheses) and resolve them with cheap fast probes (minutes), expanding the graph each pass rather than grinding one lever for hours. Spend real compute only where a cheap probe already favors the direction.
- **Decision criterion:** each pass leaves the graph WIDER (≥several new STAGED nodes) and/or resolves a cheap probe node; net-vs-net Elo CI-separation for relative levers; SPRT CI-lower>0.5 vs classical@48 n≥128 for any absolute "beats classical" claim (anchor confirmed winners only).
- **Start nodes:** EXPANSION index `f9f2bf74` (rev 20, 28 directions); new cheap-first set PROBE-1 `67169cf2`, PROBE-2 `9867fdd6`, SYMM-1 `3f47168a`, REP-1/2/3, 3DSCI-2 `a9982d50`, 3DSCI-3, TRANSFER-1, SEARCHX-1 `6551d432`; hub `e917c9e4`; ARCH-3 `bcf93cd3`.
- **Budget ceiling:** 0. **Unit:** USD (managed). **Compute approval cap:** $0/local-only (RTX 5090 + 16c/32t free; $10 credit UNTOUCHED).
- **Lookahead n=1; frontier width k=1** (rolling, fast-first).
- **Terminal condition:** no non-redundant branch justifies remaining local effort (the menu is wide; not reached).
- **Recommended next executable (cheap-first):** 3DSCI-2 motif census (engine-only, informs every feature bet) → PROBE-1 (localizes the liberty win) → SEARCHX-1 + PROBE-2 (no-train) → SYMM-1 arm-A (free TTA strength). Then cheap REP-3/REP-2 trains screened net-vs-net.
- **Stop reason this pass:** `objective_met` (breadth-expansion: 10 new STAGED directions seeded, index + control refreshed; frontier open and wider).

## PASS-20 EXECUTION (2026-06-18) — 5 cheap probes RESOLVED + batch-2 axis seeded
Executed the breadth pass's cheap-first probes (each → a resolved Flywheel node + JSON artifact), then widened a second axis. npm 48/48, crossval 60/60 intact (additive probe scripts only: `motif_census.py`, `probe_ablation.py`, `probe_calibration.py`, `searchx_decomp.py`, `cube_symmetry.py`, `symm_tta.py`).

**Resolved probe nodes (artifacts attached):**
- **3DSCI-2 `a9982d50`** (motif_census.json) — engine-only census 3³/4³/5³/7³. **The "~98% of single-stone captures → superko ban" prior (`31dae43b`) is OVERSTATED: 18–32% in actual play, falling with size.** Ko-ban density <0.1% of empty cells (0.001→0.00004) → **directly explains the PASS-18 ko-ban-plane null** (the plane the net saw was ~all-zeros). Capture/self-atari/atari-giving rates all fall with board size; game length 36→352. 7³ classical self-play ~prohibitive (8 games ≈ 24 min) — re-confirms the data-gen wall.
- **PROBE-1 `67169cf2`** (probe1_ablation.json) — **counter-intuitive: the libs net relies MOST on the ≥3-liberty (group-health) plane, NOT the atari/1-lib plane** (Part A policy-KL 0.155 vs 0.04/0.03; ≥3-lib ablation ≈ all-liberty ablation; 76% top-1 flips). Overturns the KataGo atari-prime-suspect prior. Part B (net-vs-net, low power n≈34): removing ALL liberties costs most (0.618, near-CI); single planes recoverable/not CI-separated → liberties a partially-redundant SET. → **refine via REP-3 finer buckets / my-opp / group-health, not atari.**
- **PROBE-2 `9867fdd6`** (probe2_calibration.json) — value heads **already well-calibrated** (ECE 0.007–0.009), mildly under-confident; free temperature≈0.65 halves ECE. Not a scar → MCTS is doing real look-ahead, not denoising a biased value.
- **SEARCHX-1 `6551d432`** (searchx1_decomp.json) — **raw net is WEAK**: policy-only ~0.61, value-only-1ply ~0.54 vs random; **search carries 5³ strength** (sims 1/4/16/64 vs random = 0.61/0.84/0.94/0.96; policy-only loses 0.15 to full-search). **The POLICY (not value) is the lever with most headroom** — points at soft-policy (AUX-3) / optimistic-policy (SEARCH-4) / hard-mining (DATA-1).
- **SYMM-1 arm-A `3f47168a`** (symm1_tta.json) — order-48 cube-symmetry TTA-averaged inference vs plain net = **0.558 [0.443,0.673]**, all 3 seeds ≥0.5 but **CI includes 0.5 (under-powered at n=72, k=8)**. Directionally positive, not a confirmed free win; `cube_symmetry.py` geometry validated 48/48. → retest at k=48/more games, or pivot to arm-B 48× train augmentation.

**Batch-2 seeded (different axis — 3D tactical/positional KNOWLEDGE, all STAGED):** LD-1 minimal living shape `2341cdd9`, LD-2 nakade taxonomy `1cb25477`, LD-3 generated tsumego+net-reading `7ae71a3a`, STRAT-1 center-vs-surface opening `1b196886`, STRAT-2 3D influence function `48ef927d`, DATA-1 hard-position mining `4e63c2d6`. EXPANSION index `f9f2bf74` → rev 21 (34 directions).

## Run contract (refreshed — PASS-20 execution boundary; BREADTH, rolling)
- **Objective:** keep widening the frontier with cheap fast probes (each resolves a node + artifact) and a diverse menu of STAGED bets; spend real compute only where cheap signal already favors. (User directive: breadth over grind, AGENTS.md.)
- **Decision criterion:** each pass leaves the graph wider and/or resolves cheap probe nodes; net-vs-net CI-separation for relative levers; SPRT CI-lower>0.5 vs classical for absolute "beats classical".
- **Start nodes:** EXPANSION index `f9f2bf74` (rev 21); resolved probes 3DSCI-2/PROBE-1/PROBE-2/SEARCHX-1/SYMM-1; batch-2 LD/STRAT/DATA nodes; hub `e917c9e4`.
- **Budget ceiling:** 0. **Compute approval cap:** $0/local-only ($10 credit UNTOUCHED).
- **Lookahead n=1; frontier width k=1** (rolling, fast-first).
- **Recommended next (cheap-first, evidence-driven):** (1) **REP-3** finer/my-opp/group-health liberty buckets — PROBE-1 says group-health is the carrier; (2) **SYMM-1 higher-power retest** (k=48) — resolve the 0.558 signal; (3) **LD-1 / STRAT-1** engine-science (no GPU); (4) **stronger policy** lever from SEARCHX-1 (AUX-3 soft-policy / SEARCH-4 optimistic / DATA-1 hard-mining).
- **Terminal condition:** no non-redundant branch justifies remaining local effort — NOT reached (menu wide, several cheap probes pending).
- **Stop reason this pass:** `objective_met` (breadth pass: 5 probes resolved with artifacts + 6 new STAGED directions; index+control refreshed; frontier open and wider).

## PASS-20 ROUND-2 (2026-06-18) — evidence-driven next round executed + batch-3 (geometry axis)
Per the user "do both" directive: ran the cheap-first next round (REP-3 + SYMM-1 retest) AND widened a third axis. npm 48/48, crossval 60/60 intact (additive: `rep3_split.py`, `cube_symmetry.py`, `symm_tta.py`).

**Resolved (round-2):**
- **REP-3 my/opp liberty split `7a3245ed`** (rep3_split.json) — PROBE-1's recommended refinement (ownership is the dropped bit in the winning liberty feature). 9 planes derived from the stored 10-plane stack (NO re-collection; live encoder == derive-from-stack, selftest PASS), trained 3 seeds, net-vs-net vs plain libs. **Pooled 0.558 [0.459, 0.658]** (per-seed 0.613/0.469/0.594; beats plain libs on 2/3 seeds, slightly better holdout fit ~0.086 vs ~0.080). **Directionally POSITIVE and theory-consistent, never regresses, but NOT CI-separated at n=96 (under-powered).** The cheapest path to a decision is more games (n≥300); finer-bucket arm (1/2/3/4+) needs one re-collection.
- **SYMM-1 arm-A `3f47168a`** (symm1_tta_k48.json) — higher-power retest with FULL k=48 averaging + more games: **0.531 [0.431, 0.631]** (per-seed 0.406/0.656/0.531). Full averaging did NOT lift the k=8 signal (0.558); both include 0.5 with high per-seed variance. **RESOLVED NULL — cube-symmetry TTA gives no reliable free strength (net already ~symmetry-robust in expectation); arm A closed, pivot to arm-B 48× train-time augmentation** (`cube_symmetry.py` geometry reusable).

**Pattern:** REP-3 (0.558) and SYMM (0.531) both land "directionally-positive-but-not-CI-separated at n~96" with large per-seed variance → at 5³ the cheap unblock is MORE GAMES per A/B, not new levers. (Echoes the PASS-15 small-sample scar.)

**Batch-3 seeded (geometry/dimensionality axis, all STAGED):** GEO-1 2D→3D dimensionality ladder `7390a76f` (engine supports (w,h,d); Go on (n,n,1)=2D … (n,n,n)=cube — a free interpolation), GEO-2 slab/depth-2 tactics `189adb1d`, GEO-3 cross-depth transfer `3f5b8ced`, ALGO-S1 MCTS-Solver `e45385fe`, ALGO-S2 graph-MCTS+superko-TT `bea50f57`, ROBUST-1 non-cube generalization `d1a8d69c`. EXPANSION index `f9f2bf74` → rev 22 (**40 directions**).

## Run contract (refreshed — PASS-20 round-2 boundary; BREADTH, rolling)
- **Objective:** keep widening + resolving cheap probes; spend real compute only where cheap signal favors (AGENTS.md breadth rule).
- **Tally PASS-20:** 22 new STAGED directions (batches 1/2/3) + **7 probes resolved with artifacts** (3DSCI-2, PROBE-1, PROBE-2, SEARCHX-1, SYMM-1[null], REP-3[directional+]).
- **Start nodes:** EXPANSION index `f9f2bf74` (rev 22); REP-3 `7a3245ed`; resolved probes; batch-3 GEO/ALGO-S/ROBUST; hub `e917c9e4`.
- **Budget:** 0 USD managed; $0/local-only ($10 credit UNTOUCHED). **n=1, k=1**, fast-first.
- **Recommended next (cheap-first, evidence-driven):** (1) **REP-3 higher-power confirm** (n≥300) — convert the 0.558 lead to a decision; (2) **GEO-1 dimensionality ladder / STRAT-1 / LD-1** (engine-science, no GPU); (3) **ALGO-S1 MCTS-Solver** (search carries 5³ strength per SEARCHX-1); (4) stronger-policy lever (AUX-3/SEARCH-4/DATA-1). SYMM arm-A closed null.
- **Terminal condition:** no non-redundant branch justifies remaining local effort — NOT reached (menu wide; clear cheap next steps).
- **Stop reason this pass:** `objective_met` (round-2: 2 more probes resolved + 6 new STAGED directions; index+control refreshed; frontier open and wider).