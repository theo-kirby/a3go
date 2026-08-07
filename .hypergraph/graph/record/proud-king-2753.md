---
node_id: f9f2bf74-2ce6-5488-b471-dc0b6c422b99
slug: proud-king-2753
title: Phase 3 — frontier EXPANSION (KataGo/autogo/online-go-inspired branches), LIVING
created_at: '2026-06-09T07:01:11.286674+00:00'
parents:
- mute-cloud-4824
summary: 'Phase-3 EXPANSION menu (LIVING). PASS-20: 22 new STAGED directions across 3 batches (interp/symmetry/reps, tactical-knowledge LD/STRAT/DATA, geometry GEO/ALGO-S/ROBUST) = 40 total. 7 cheap probes RESOLVED: 3DSCI-2, PROBE-1 (≥3-lib group-health carries the win), PROBE-2, SEARCHX-1 (search carries 5³ strength), SYMM-1 (arm-A null), REP-3 my/opp split (directionally + 0.558, under-powered). Next: REP-3 higher-power confirm, GEO-1, ALGO-S1.'
flywheel:
  node_id: f9f2bf74-2ce6-5488-b471-dc0b6c422b99
  slug: proud-king-2753
  revision: 22
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 4c75fe7ec1cd6dffd68d7d2f5ffa1108a210065b03dc5d788f4d6771b96c451e
---
# Phase 3 — frontier EXPANSION (KataGo/autogo/online-go-inspired branches), LIVING

**This node widens the Phase-3 frontier.** Phase 3's existence thesis is answered
(a strong 3D-Go agent *can* be trained — distill the classical teacher, scale
capacity, scale cheap search with board size) and 15 passes are recorded; the live
frontier (control `62ab093f`, hub `e917c9e4`) had narrowed to two open branches —
ALGO-2 capacity `792c4ec2` and an n≥128 re-power audit — after PASS-15 `b3ea0b95`
showed self-play does **not** lift absolute strength on 5³.

This pass mines three external repos for transferable methods and seeds the graph
with **17 new STAGED direction nodes** so the autonomous picker has a rich menu on
future runs. **No experiments were run; no `neural/` code changed.** Every node
below is a STAGED plan (same convention as the existing 14 Phase-3 direction
nodes) — Objective · Why · Route · Decision criterion (CI-based, n≥128) ·
Preconditions · Cost·value · Expected artifacts · Inspiration source.

**Source material (reference nodes):**
- **KataGo methods** `365b153f-75e1-54ee-9344-4794604da3a4` — the richest seam: aux targets
  (ownership/score/short-term/soft-policy), search Elo levers (optimistic policy,
  value-bias correction, variance-cPUCT), architecture (global-pooling size-
  agnostic heads, nested-bottleneck blocks, richer input planes), SPRT gating.
- **online-go.com** `ba69d0a3-f344-5413-8b0f-e4d65aa947bc` — 3D game-review/analysis UI
  inspiration (ownership/score overlays, win-rate graph, opening explorer, SGF record).
- **autogo** `b4fd8252` (pre-existing) — train×test scaling-law thesis (→ EVAL-3).

## Status index — PICK A START POINT (P17–P18 resolutions marked ✅)

**PASS-18 headline:** ARCH-3 (richer input planes) is the **FIRST EXPANSION branch to beat its 3-plane baseline DECISIVELY** (liberties-alone 0.449 [0.400,0.499] = +0.144 CI-separated; full-stack +0.106). **Per-group LIBERTY planes carry the gain** (strongest arm, even > the 10-plane stack); **ko-ban does NOT help on 5³** (KataGo prime-suspect prior falsified — ko too sparse at this size). This REVISES the P17 'cheap cluster exhausted → needs scale/C++' conclusion: the 5³ ceiling is **not robust to INPUT representation**. Still short of beating classical absolutely (0.449 < 0.5 parity) — closest 5³ net yet. See ARCH-3 `bcf93cd3` + control `62ab093f` P18.

**PASS-19 headline:** SCALE-libs `faddae67` RESOLVED **NULL — capacity is not the 5³ lever.** A GPU net-vs-net Elo screen (the methodology pivot below) shows libs@64×6 (Elo 70.9) ≈ libs96×8 (78.6) **tied at top**, while libs128×10 **over-scales to Elo −11, below the 3-plane base** — more channels/blocks on the liberty input buy zero strength and overshooting regresses. Extends the 5³ ceiling (PASS-15) to the liberty input: liberties reach the doorstep of parity, capacity on top is exhausted. **METHODOLOGY PIVOT (unblocks the frontier):** net-vs-classical strength eval was the wall (~3 h/seed CPU at net@512); replaced by **GPU net-vs-net Elo screen** `screen_nvn.py` (~38 min, relative ordering) + **SPRT-bounded classical anchor** `sprt.py` (EVAL-1, early-stop, for confirmed winners only) + **lazy `config_planes`** (byte-identical, 4.5×/119× faster). Next (rolling, fast-first): liberty-input *refinements*, then 7³ — NOT more 5³ capacity. See control `62ab093f` P19.

**PASS-20 headline (BREADTH pass — user directive 2026-06-18 "expand the surface, don't grind"):** seeded **10 NEW cheap-first STAGED directions** across fresh axes the menu lacked, biased to minutes-scale forward-pass / engine-only probes that each resolve a node (NOT hour-long trains): interpretability no-train probes (PROBE-1 input-ablation attribution = *which* liberty bucket carries the +0.144; PROBE-2 value-head calibration), the order-48 **cube-symmetry** lever (SYMM-1 — free test-time-augmentation strength + 48× data), novel input representations (REP-1 3D structural geometry, REP-2 move-liberties/self-atari, REP-3 my/opp + finer liberty split), 3D-Go rules **science** (3DSCI-2 tactical-motif census, 3DSCI-3 cyclic-ko pathologies), cross-board **transfer** (TRANSFER-1 zero-shot 4³→5³), and a **net-vs-search decomposition** (SEARCHX-1 policy-only/value-only strength curves). New working rule "Breadth over depth" recorded in AGENTS.md. See control `62ab093f` P20.

**PASS-20 EXECUTION (2026-06-18) — 5 cheap probes RESOLVED + 6 new directions (batch-2):** the breadth pass executed its cheap-first probes (each a resolved node + artifact) AND widened a second axis. Headlines:
- **3DSCI-2 census** `a9982d50`: the "~98% of single-stone captures → superko ban" prior is **overstated** — only **18–32%** in actual play, falling with size; ko-ban density **<0.1%** of empty cells → **explains the PASS-18 ko-ban null** (the plane was ~all-zeros). Captures/atari fall with board size.
- **PROBE-1 ablation** `67169cf2`: the net relies **MOST on the ≥3-liberty (group-health) plane, NOT atari** — overturns the KataGo atari-prime-suspect prior; liberties act as a partially-redundant set. → refine via REP-3 finer buckets/group-health, not atari.
- **PROBE-2 calibration** `9867fdd6`: value heads **already well-calibrated** (ECE~0.008), mildly under-confident; free temp≈0.65 halves ECE. Not a scar.
- **SEARCHX-1 decomposition** `6551d432`: raw net is **WEAK** (policy-only ~0.61 vs random); **search carries 5³ strength** (sims 1→64: 0.61→0.96 vs random; policy-only loses 0.15 to full search). The POLICY is the headroom.
- **SYMM-1 arm-A TTA** `3f47168a`: cube-symmetry-averaged inference vs plain = **0.558 [0.443,0.673]** — directionally positive (all seeds ≥0.5) but **under-powered**; retest at k=48/more games or pivot to arm-B 48× augmentation. Geometry (`cube_symmetry.py`) validated 48/48.

npm 48/48, crossval 60/60 intact (additive probe scripts only). See control `62ab093f` P20-exec.

## Status index (all STAGED; pick a start point)
| theme | node | id | cost | depends on | source |
|---|---|---|---|---|---|
| Aux | AUX-1 ownership head — **✅RESOLVED P17: learns territory (own-acc .98) but strength non-decisive on 5³** | `665706e4-f3f0-5331-8031-f9b98412b79a` | med | — | KataGo |
| Aux | AUX-2 score-margin + distribution head | `d971bf0e-673d-5b30-a686-5acca18f2316` | med | — | KataGo |
| Aux | AUX-3 soft policy — **✅RESOLVED P17: soft>hard all seeds but CIs overlap (non-decisive)** | `c017760b-671f-54f1-951d-50887754dad7` | med | — | KataGo |
| Aux | AUX-4 short-term value/score targets | `4842d305-9e69-52f7-bf02-c9926031a385` | med | — | KataGo |
| Search | SEARCH-1 score-aware utility + dynamic komi | `0b9fe131-8eff-543e-a6c7-42c24615c0b1` | med | AUX-2 | KataGo |
| Search | SEARCH-2 subtree value-bias correction | `b08727b4-5be8-58d2-a2a6-e747fce437de` | med | — | KataGo (30–60 Elo) |
| Search | SEARCH-3 variance-cPUCT + uncertainty playouts | `0844658b-97b8-5040-b6ec-4ee3c03a73e3` | med | AUX-4 | KataGo (~75 Elo) |
| Search | SEARCH-4 optimistic policy head | `312d9495-eee2-552f-8fe8-3730840814fb` | med | AUX-3 | KataGo (40–90 Elo) |
| Search | SEARCH-5 playout-cap rand + shaped Dirichlet + root temp | `e3615791-6e33-54cf-989d-445e2c857aad` | med | — | KataGo + autogo |
| Arch | ARCH-1 global-pooling size-agnostic + masked multi-size | `5f4399f0-b761-5fb5-bc8c-d6ffbbf73793` | med-high | — | KataGo |
| Arch | ARCH-2 nested-bottleneck (BN-free) — **✅RESOLVED P17: strength PARITY, no win (non-decisive)** | `8cecf366-472e-5450-89c6-b149b3ed36f3` | med | — | KataGo |
| Arch | ARCH-3 richer input planes — **✅RESOLVED P18: DECISIVE +0.144 — LIBERTIES carry it; ko-ban prior FALSIFIED on 5³** | `bcf93cd3-8d8b-5924-a570-3232f7f1d065` | med | — | KataGo |
| Proof | EVAL-1 SPRT gate + n≥128 re-power audit — **🔧P19: `sprt.py` BUILT (SPRT wrapper around net-vs-classical, early-stop); libs@64 cross-check in flight** | `259c2ebe-e702-5525-a4eb-a7291e5c857a` | med | — | engine-gating + our scar |
| Proof | EVAL-2 superko-aware exact solver | `ebff5f9f-80c2-5716-a09a-c08141d933d7` | med | — | extends PROOF-3 |
| Proof | EVAL-3 train×test scaling-law surface | `8c790338-cbbd-598c-ac01-d8f6d95fc321` | med-high | aux/capacity nets | autogo |
| Science | SCI-1 center value + 3D opening explorer | `5b0393b7-72f1-5dc1-88fe-f7a56c1cccdc` | med | strong net | online-go + KataGo |
| Tooling | TOOL-3 3D game-review UI (ownership/score/winrate) | `f70cb8c1-b1d7-5aa9-b063-b86c3bc90762` | med | AUX-1, AUX-2 | online-go |

*Multi-parent DAG: each direction node's parents = the result node(s) it extends
**plus** this expansion node. "Depends on" lists intra-expansion prerequisites
(e.g. SEARCH-1 needs the AUX-2 score head).*

## PASS-20 new directions (breadth pass, cheap-first) — all STAGED
Fresh axes added 2026-06-18 under the "expand the surface, don't grind" directive. Cost tag **cheap/no-train** = forward-pass or engine-only, minutes, resolvable without a long train.
| theme | node | id | cost | depends on | source |
|---|---|---|---|---|---|
| Interp | PROBE-1 ablation — **✅RESOLVED P20: net relies most on ≥3-LIB group-health plane, NOT atari; liberties a redundant set** | `67169cf2-5124-58f2-b3c3-f43baa726d78` | **cheap/no-train** | libs ckpts | KataGo importance |
| Interp | PROBE-2 calibration — **✅RESOLVED P20: already well-calibrated (ECE~.008), free temp≈.65 halves it; not a scar** | `9867fdd6-8970-5ddb-a1cb-702155d96774` | **cheap/no-train** | ckpts+data | calibration |
| Symmetry | SYMM-1 cube-symmetry — **✅RESOLVED P20-r2 NULL: arm-A TTA k=8 0.558 + k=48 0.531 both incl. 0.5 → no free gain; pivot to arm-B 48× aug** | `3f47168a-3f0c-5e7d-84a0-9a493d423f73` | **cheap infer** / med train | ckpts | AlphaGo/KataGo |
| Rep | REP-1 3D structural-geometry planes (neighbor-count / dist-to-surface / face-type) | `42747f38-817c-542c-9561-5966c8c96cf0` | cheap train | — | KataGo loc feats |
| Rep | REP-2 liberty-after-move (pseudo-liberty / self-atari) planes | `6ac526b8-9f9b-586e-b746-68db41b0390e` | cheap train | — | KataGo |
| Rep | REP-3 my/opp liberty split — **🔧P20-r2: my/opp-split directionally + (0.558 [.46,.66], 2/3 seeds beat plain libs) but under-powered; confirm at higher n; finer-bucket arm needs re-collection** | `7a3245ed-121b-5a58-ad34-6b210badca95` | cheap train | — | KataGo |
| Science | 3DSCI-2 motif census — **✅RESOLVED P20: '98% ko' overstated (18–32%); ko-ban density <0.1% → explains P18 ko null** | `a9982d50-b5d5-5639-bdf1-70d0f4de1b45` | **cheap/engine** | — | quantifies `31dae43b` |
| Science | 3DSCI-3 3D cyclic-ko pathologies (double-ko / sending-two / triple-ko) | `73adb0d5-d1bc-58b2-a7ee-833ec3cce15b` | **cheap/engine** | — | superko theory |
| Transfer | TRANSFER-1 zero-shot cross-board (4³→5³→7³) via global-pool head | `0bbe92d5-3b7f-552d-866a-ea63dec0c815` | cheap-med eval | ARCH-1 | KataGo multi-size |
| Search | SEARCHX-1 decomposition — **✅RESOLVED P20: raw net weak (~0.61 vs random); SEARCH carries 5³ strength; policy=headroom** | `6551d432-c11e-52bf-9a6b-caf49ab6fe0c` | **cheap/no-train** | ckpts | AZ/KataGo raw-net |

**Recommended cheap-first execution order (PASS-20):** 3DSCI-2 (engine census, informs every feature bet) · PROBE-1 (localizes the liberty win → tells REP-2/REP-3 what to build) · SEARCHX-1 + PROBE-2 (net-vs-search + calibration, both no-train) · SYMM-1 arm-A (free TTA strength) · then REP-3/REP-2/REP-1 cheap trains screened net-vs-net · TRANSFER-1 after ARCH-1. Anchor only a confirmed net-vs-net winner to classical via SPRT (`259c2ebe`).

## PASS-20 batch-2 — 3D tactical & positional KNOWLEDGE axis (life-and-death / shape / influence) — all STAGED
A different axis from batch-1: what 3D Go *is* tactically. Almost entirely unexplored, mostly cheap engine/solver/forward-pass.
| theme | node | id | cost | depends on | source |
|---|---|---|---|---|---|
| L&D | LD-1 minimal living shape / 3D two-eye condition | `2341cdd9-...` patient-paper-9241 | **cheap/engine** | EVAL-2 | 2D L&D theory |
| L&D | LD-2 3D nakade / dead-shape taxonomy | `1cb25477-...` cold-hill-1866 | **cheap/engine** | LD-1, cube_symmetry | 2D nakade |
| L&D | LD-3 generated 3D tsumego + net L&D reading | `7ae71a3a-...` lucky-wave-5153 | **cheap/no-train** | LD-1/2 | KataGo benchmarks |
| Strategy | STRAT-1 center-vs-surface opening value 5³/7³ (follows `853d7c2c`) | `1b196886-...` red-credit-3434 | **cheap/engine** | — | 2D opening theory |
| Strategy | STRAT-2 3D influence / ownership-correlation function | `48ef927d-...` wild-glade-7676 | **cheap/stats** | AUX-1 | 2D influence |
| Data | DATA-1 hard-position mining for distillation (tests PASS-15 data-quality thesis) | `4e63c2d6-...` dry-glade-4547 | cheap train | — | hard-example mining |

**Next cheap-first picks (post-P20):** REP-3 finer/my-opp liberty buckets (PROBE-1 says group-health is the carrier) → SYMM-1 higher-power retest (k=48) → LD-1/STRAT-1 (engine science, no GPU) → DATA-1 hard-mining. Stronger policy is the SEARCHX-1-identified lever (soft-policy AUX-3 / optimistic SEARCH-4).

## PASS-20 round-2 (cheap-first execution cont'd) + batch-3 (geometry axis)
**Executed the evidence-driven next round:** REP-3 my/opp split `7a3245ed` (PROBE-1's pick) → **directionally + (0.558, 2/3 seeds beat plain libs, slightly better holdout) but under-powered**; SYMM-1 arm-A retest at full k=48 `3f47168a` → **null (0.531, both k include 0.5) → arm A closed, pivot to arm-B 48× aug**. Both land in the same "directionally-positive-but-not-CI-separated at n~96" regime → the cheap unblock now is more GAMES, not new levers. npm 48/48, crossval 60/60.

## PASS-20 batch-3 — BOARD GEOMETRY & the 2D→3D dimensionality ladder (+ search-structure) — all STAGED
The engine supports non-cube (w,h,d) shapes, so Go on (n,n,1)=2D … (n,n,n)=cube is a free, unexplored interpolation. Mostly cheap engine/small-net/search work.
| theme | node | id | cost | depends on | source |
|---|---|---|---|---|---|
| Geometry | GEO-1 2D→3D dimensionality ladder (komi/opening/strength vs depth) | `7390a76f-...` still-recipe-4954 | **cheap/engine** | — | dim interpolation |
| Geometry | GEO-2 value of the 3rd dim / slab anisotropy / depth-2 tactics | `189adb1d-...` lively-sun-0512 | **cheap/engine** | GEO-1 | layered-board |
| Geometry | GEO-3 cross-depth transfer (does 2D knowledge climb the ladder?) | `3f5b8ced-...` noisy-dream-0116 | cheap-med eval | ARCH-1, GEO-1 | curriculum |
| Search | ALGO-S1 MCTS-Solver (exact W/L terminal backup; endgame/L&D) | `e45385fe-...` wispy-glitter-1456 | **cheap/search** | EVAL-2 | MCTS-Solver |
| Search | ALGO-S2 graph MCTS + superko-aware transposition table | `bea50f57-...` cool-leaf-5231 | **cheap/search** | — | TT / GHI |
| Robust | ROBUST-1 cube-trained net on slabs / odd shapes (generalization) | `d1a8d69c-...` crimson-rice-4497 | **cheap/no-train** | ARCH-1 | dist-shift |

**Next cheap-first (post-round-2):** (1) REP-3 **higher-power confirm** (n≥300) — cheapest path to a decision on the 0.558 lead; (2) REP-3 **+finer-bucket arm** (one re-collection); (3) **GEO-1 dimensionality ladder** / **STRAT-1** / **LD-1** (engine-science, no GPU); (4) **ALGO-S1 MCTS-Solver** (search-side strength, SEARCHX-1 said search carries it). SYMM arm-A closed.

## Recommended what-may-work ordering (rationale)
The campaign's own evidence says the remaining levers for S1/S5 are **signal
richness and capacity, not more search or self-play** (PASS-15 `b3ea0b95`).
KataGo's track record sharpens this into an order:

1. **Auxiliary targets first — AUX-1 (ownership), AUX-2 (score), AUX-3
   (soft-policy).** KataGo's biggest early-training accelerator, and they hit our
   two named weak spots: the **policy head degrades on big boards** (`0bc38c41`) →
   soft-policy; **win-rate can't see komi** because games blow out (`2a2ca6b9`) →
   a score head gives a dense, komi-sensitive signal. Cheapest high-upside branch;
   pure training change on the existing nets. **Likely to work.**
2. **Richer input planes (ARCH-3) + capacity (ARCH-2).** Ko is ubiquitous in 3D
   (`31dae43b`) yet the net never sees a ko-ban/history plane — a cheap, plausibly
   large fix. Nested-bottleneck capacity is the literal "scale capacity" lever
   PASS-15/PROOF-1 point to for S1.
3. **EVAL-1 (SPRT + re-power audit) — alongside everything.** PASS-15 proved n≤32
   evals are too noisy to gate on; SPRT makes every future A/B well-powered and
   cheap. High integrity, low cost. **Do early.**
4. **Score-aware play (SEARCH-1) + dynamic komi** once AUX-2 lands — unlocks honest
   komi/handicap evaluation and could make S4-style big-board comparisons meaningful.
5. **Search Elo levers (SEARCH-2/3/4)** are real (KataGo banks 30–90 Elo each) but
   depend on the aux heads (uncertainty/optimistic need short-term/soft targets) —
   sequence them after AUX.
6. **ARCH-1 size-agnostic net** is the keystone for the whole SCALE theme (one net
   3³→9³, curriculum transfer) and the most reusable single build; medium cost,
   high leverage.
7. **EVAL-2 superko-aware solver** is the only path to a *meaningful S3* (PROOF-3
   left 2×2×2 as the frontier); self-contained, theoretically clean, no GPU.
8. **EVAL-3 scaling-law study** reframes our cross-board law as autogo's central
   scaling thesis — a strong "science" headline once the aux/capacity nets exist.
9. **Lower priority / dependent:** SEARCH-5 self-play tweaks (self-play already
   shown not to lift absolute strength on 5³ — value is *data quality* for the
   aux-head retrain), SCI-1 opening explorer & TOOL-3 review UI (legibility/science
   payoff, best after a stronger net exists).

**Rejected (as before):** 7³ net-vs-classical (classical unrunnable, PASS-13);
managed compute ($0/local); more plain frozen-net self-play (both gates exhausted,
PASS-14/15).

See the human-readable companion **`docs/DIRECTIONS.md`** for the
inspiration→direction table + one paragraph per direction.

Related: hub `e917c9e4`, control `62ab093f`, agenda `6148c5c0`, methodology
`dcd0a5db`, KataGo ref `365b153f-75e1-54ee-9344-4794604da3a4`, online-go ref `ba69d0a3-f344-5413-8b0f-e4d65aa947bc`, autogo `b4fd8252`.
