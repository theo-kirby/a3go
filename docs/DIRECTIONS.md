# a3go research directions — frontier EXPANSION catalog

Human-readable companion to the LIVING **EXPANSION index** flywheel node
(`f9f2bf74-2ce6-5488-b471-dc0b6c422b99`, slug `proud-king-2753`). That node is the system of record; this file is the
legible map. **This was a graph/docs *seeding* pass — every direction below is a
STAGED plan, none executed, and no `neural/` or engine code was changed.**

Phase 3's existence thesis is answered (a strong 3D-Go agent *can* be trained:
distill the classical teacher → scale capacity → scale cheap search with board
size). 15 passes are recorded; PASS-15 (`b3ea0b95`) showed self-play does **not**
lift absolute strength on 5³, so the remaining levers for *provably strong*
(Success-bar-v2 S1–S5) are **signal richness and capacity, not more search or
self-play**. This pass mines three external repos to widen the menu before the
next execution pass.

## Inspiration sources
- **lightvector/KataGo** — the richest seam: auxiliary ownership/score/short-term/
  soft-policy targets, search Elo levers (optimistic policy +40–90, subtree
  value-bias +30–60, variance-cPUCT + uncertainty ~75), playout-cap randomization,
  global-pooling size-agnostic heads, nested-bottleneck blocks, richer input
  planes, SPRT gating. (reference node — see the index.)
- **ericjang/autogo** — autonomous-research framing; the **train-time + test-time
  scaling-law** study as the central thesis (→ EVAL-3); anneal-don't-fix noise
  (→ SEARCH-5). (node `b4fd8252`.)
- **online-go/online-go.com** — frontend over the same vendored goban board; value
  is the **game-review/analysis UI** vocabulary: ownership/territory overlay,
  score-estimate bar, win-rate graph, move-by-move review, opening explorer,
  SGF-equivalent record (→ TOOL-3, SCI-1). (reference node — see the index.)

## Inspiration → direction map

| # | theme | direction | extends | source | flywheel slug |
|---|---|---|---|---|---|
| AUX-1 | Aux targets | Per-voxel ownership / territory head | ALGO-2 `792c4ec2`, scaling-law `0bc38c41` | KataGo | `proud-star-4959` |
| AUX-2 | Aux targets | Score-margin + score-distribution head | Q9 komi `9a106027`, komi-flat `2a2ca6b9`, ALGO-2 `792c4ec2` | KataGo | `throbbing-unit-0557` |
| AUX-3 | Aux targets | Soft policy target (T≈4, ~8×) + policy-target pruning | scaling-law `0bc38c41`, ALGO-2 `792c4ec2` | KataGo | `snowy-brook-3358` |
| AUX-4 | Aux targets | Short-term value / score targets (bias-variance) | ALGO-2 `792c4ec2`, INFRA-3 `8a724b1c` | KataGo | `broad-hall-8962` |
| SEARCH-1 | Search | Score-aware utility + dynamic komi at play time | AUX-2, Q9 komi `9a106027` | KataGo | `spring-brook-4774` |
| SEARCH-2 | Search | Subtree value-bias correction (3×3×3 local-pattern buckets) | PROOF-1 `3ac354fd`, ALGO-1 `4cf07501` | KataGo (30–60 Elo) | `noisy-dust-7661` |
| SEARCH-3 | Search | Variance-scaled cPUCT + uncertainty-weighted playouts | ALGO-1 `4cf07501`, PROOF-1 `3ac354fd`, AUX-4 | KataGo (~75 Elo) | `cold-sun-4675` |
| SEARCH-4 | Search | Optimistic policy head | AUX-3, ALGO-2 `792c4ec2` | KataGo (40–90 Elo) | `cold-butterfly-1441` |
| SEARCH-5 | Search | Self-play exploration/efficiency: playout-cap randomization + shaped Dirichlet + root softmax temp | INFRA-3 `8a724b1c`, autogo `b4fd8252` | KataGo + autogo | `icy-pine-8163` |
| ARCH-1 | Architecture | Global-pooling size-agnostic heads + masked multi-board-size training | SCALE-2 `1e58a424`, SCALE-3 `adb11193`, scaling-law `0bc38c41` | KataGo | `tight-dust-1276` |
| ARCH-2 | Architecture | Nested-bottleneck blocks + fixed-variance init (capacity-per-flop; drop BatchNorm) | ALGO-2 `792c4ec2`, seki `5f10c19e` | KataGo | `purple-field-4026` |
| ARCH-3 | Architecture | Richer input planes (history, liberties, ko-ban, capture-parity) | ALGO-2 `792c4ec2`, ko-ubiquitous `31dae43b` | KataGo | `polished-field-7944` |
| EVAL-1 | Proof | SPRT / sequential-testing gate + n≥128 re-power audit of headline claims | methodology `dcd0a5db`, PROOF-1 `3ac354fd`, PASS-15 `b3ea0b95` | engine-gating + our n≥128 scar | `dawn-pond-0204` |
| EVAL-2 | Proof | Superko-aware exact solver (history-threaded TT) — push S3 past 2×2×2 | PROOF-3 `22d59c45` | extends PROOF-3 | `soft-thunder-1632` |
| EVAL-3 | Proof | Train-time × test-time scaling-law characterization (strength surface) | scaling-law `0bc38c41`, PROOF-2 `75615ad2` | autogo | `cold-poetry-1723` |
| SCI-1 | Science | Center/positional value + 3D opening explorer (joseki book) | SCIENCE-1 `5e34766d`, Q8 `853d7c2c` | online-go + KataGo | `muddy-art-1226` |
| TOOL-3 | Tooling | 3D game-review UI: ownership heatmap + score-estimate bar + win-rate graph + SGF-equiv record | TOOL-1 `1f59266a`, TOOL-2 `742a0aab`, AUX-1, AUX-2 | online-go | `twilight-hill-9139` |

## One paragraph per direction

### AUX-1 — Per-voxel ownership / territory head
*Theme: Aux targets · extends ALGO-2 `792c4ec2`, scaling-law `0bc38c41` · source: KataGo · node `proud-star-4959`*

Add a per-voxel ownership head (predict every cell's final owner) as a dense spatial auxiliary target. KataGo calls ownership its single biggest early-training accelerator. Our net is supervised by one scalar outcome; the scaling law `0bc38c41` shows policy gets *harder* as boards grow, i.e. the trunk is starved of dense signal. The head also *is* the ownership heatmap TOOL-3 needs. Pure training change on existing data; the cheapest high-upside aux head.

### AUX-2 — Score-margin + score-distribution head
*Theme: Aux targets · extends Q9 komi `9a106027`, komi-flat `2a2ca6b9`, ALGO-2 `792c4ec2` · source: KataGo · node `throbbing-unit-0557`*

Predict the final area margin (and a small distribution over it). This is the fix for our sharpest komi scar — on 3³ win-rate is **flat** across komi −1.5…+7.5 (`2a2ca6b9`) because games blow out and the binary outcome carries no komi information. A signed margin target is dense and monotone in komi, so it can pin fair komi natively (Q9 `9a106027` needed a bespoke estimator), and it is the prerequisite for score-aware play (SEARCH-1) and honest handicap evaluation.

### AUX-3 — Soft policy target (T≈4, ~8×) + policy-target pruning
*Theme: Aux targets · extends scaling-law `0bc38c41`, ALGO-2 `792c4ec2` · source: KataGo · node `snowy-brook-3358`*

Train the policy head against the *softened full MCTS visit distribution* (T≈4), up-weighted ~8×, pruning near-zero-visit junk. Policy is the campaign's weakest head — accuracy 0.12→0.07→0.05 as the board grows (`0bc38c41`), the only curve trending the wrong way. A soft, richer target transfers search's full preference ordering and damps label noise where the action space is largest. Cheap, training-only, and the precondition for the optimistic-policy head (SEARCH-4).

### AUX-4 — Short-term value / score targets (bias-variance)
*Theme: Aux targets · extends ALGO-2 `792c4ec2`, INFRA-3 `8a724b1c` · source: KataGo · node `broad-hall-8962`*

Predict value/score a few plies ahead (TD/n-step bootstrap), not only the final outcome — KataGo's bias-variance lever for value calibration. Deeper PUCT *amplifies* a miscalibrated value head (we saw it: search hurt the weak net `9605fb9a`, capacity fixed it `b71da32b`). Short-term targets are lower-variance and train faster, and they yield the per-node value-variance estimate that uncertainty-weighted search (SEARCH-3) needs.

### SEARCH-1 — Score-aware utility + dynamic komi at play time
*Theme: Search · extends AUX-2, Q9 komi `9a106027` · source: KataGo · node `spring-brook-4774`*

Once AUX-2 lands, make MCTS optimize a blend of win-prob and expected score, and adjust komi during self-play so games stay competitive instead of blowouts. Blowout-domination is *why* win-rate can't see komi (`2a2ca6b9`) and why a pure-win-prob agent plays slack when ahead. Score-aware play sharpens moves and densifies the training signal; dynamic komi keeps self-play near 50%. Together they unlock honest komi/handicap evaluation. **Depends on AUX-2.**

### SEARCH-2 — Subtree value-bias correction (3×3×3 local-pattern buckets)
*Theme: Search · extends PROOF-1 `3ac354fd`, ALGO-1 `4cf07501` · source: KataGo (30–60 Elo) · node `noisy-dust-7661`*

Bucket tree nodes by their local 3×3×3 pattern, learn each bucket's systematic value bias online, and subtract it during search — a pure search-time, no-retrain Elo gain (KataGo: +30–60). We have an anchored Elo ladder (PROOF-1 `3ac354fd`) to measure the delta cleanly and a working MCTS (ALGO-1 `4cf07501`) to host it. The 3D pattern key is the degree-6 neighborhood (our geometry findings `c85ce2bf` make it well-defined).

### SEARCH-3 — Variance-scaled cPUCT + uncertainty-weighted playouts
*Theme: Search · extends ALGO-1 `4cf07501`, PROOF-1 `3ac354fd`, AUX-4 · source: KataGo (~75 Elo) · node `cold-sun-4675`*

Scale the exploration constant by observed value variance and weight playouts by uncertainty — KataGo's largest single search-time item (~+75 Elo). It improves efficiency at *low* sims, the regime where our net's win is currently bounded (PROOF-1: net wins at matched/low budget, loses at high). A better low-sim search is the cheapest path toward S1 budget-dominance that doesn't need a bigger net. **Needs AUX-4's variance estimate.**

### SEARCH-4 — Optimistic policy head
*Theme: Search · extends AUX-3, ALGO-2 `792c4ec2` · source: KataGo (40–90 Elo) · node `cold-butterfly-1441`*

Add a second policy head biased toward moves whose search value *exceeded* their prior (the under-rated over-performers), blended into selection — KataGo: +40–90 Elo. Our weak policy *narrows* search prematurely on big boards (`0bc38c41`); an optimistic head explicitly counteracts that, and compounds with AUX-3's softer target. **Depends on AUX-3.**

### SEARCH-5 — Self-play exploration/efficiency: playout-cap randomization + shaped Dirichlet + root softmax temp
*Theme: Search · extends INFRA-3 `8a724b1c`, autogo `b4fd8252` · source: KataGo + autogo · node `icy-pine-8163`*

Upgrade self-play with playout-cap randomization (cheap moves + a fraction expensive), legal-move-scaled Dirichlet, and a root softmax temperature — replacing `az.py`'s flat Dirichlet(0.5). PASS-15 `b3ea0b95` showed self-play does **not** lift absolute 5³ strength, so the value here is **data quality** for the aux-head retrains, not more self-improvement. autogo independently warns fixed noise compounds badly — anneal it. Gated on downstream net quality, not self-play win-rate.

### ARCH-1 — Global-pooling size-agnostic heads + masked multi-board-size training
*Theme: Architecture · extends SCALE-2 `1e58a424`, SCALE-3 `adb11193`, scaling-law `0bc38c41` · source: KataGo · node `tight-dust-1276`*

Make the net fully-convolutional with global-average-pooling value/score heads and train it on mixed board sizes (zero-pad + mask), so **one net plays 3³→9³**. Today each size needs its own fixed-FC net — the bottleneck for the whole SCALE theme (SCALE-2 `1e58a424`, SCALE-3 `adb11193`). The keystone build: it unlocks curriculum transfer and a unified fit of the cross-board law `0bc38c41`. Medium cost, highest leverage / reusability.

### ARCH-2 — Nested-bottleneck blocks + fixed-variance init (capacity-per-flop; drop BatchNorm)
*Theme: Architecture · extends ALGO-2 `792c4ec2`, seki `5f10c19e` · source: KataGo · node `purple-field-4026`*

Swap the plain BatchNorm resnet for KataGo's nested-bottleneck blocks with fixed-variance (BN-free) init — more capacity per FLOP and more stable training. This is the literal **scale-capacity** lever the campaign's evidence prioritizes for S1 (the move that first beat classical was 32×3→64×6, `b71da32b`; PASS-15 says capacity, not search). FLOP-efficiency matters because bigger nets slow per-sim eval — measure strength *per wall-clock*.

### ARCH-3 — Richer input planes (history, liberties, ko-ban, capture-parity)
*Theme: Architecture · extends ALGO-2 `792c4ec2`, ko-ubiquitous `31dae43b` · source: KataGo · node `polished-field-7944`*

Feed the net move-history, per-group liberty counts, a ko-ban/superko-forbidden plane, and capture-parity — beyond the bare B/W/stm it sees now. Ko is **ubiquitous** in 3D (~98% of single-captures trigger a superko ban, `31dae43b`) yet the net is blind to it: a cheap, plausibly large omission. The cheapest high-upside win in the expansion; ablate plane groups to attribute the gain (ko-ban + liberties are the prime suspects).

### EVAL-1 — SPRT / sequential-testing gate + n≥128 re-power audit of headline claims
*Theme: Proof · extends methodology `dcd0a5db`, PROOF-1 `3ac354fd`, PASS-15 `b3ea0b95` · source: engine-gating + our n≥128 scar · node `dawn-pond-0204`*

Build a Leela/Stockfish-style SPRT gate so every A/B is well-powered at fixed error rates with the minimum games, and re-audit the headline win-rate claims (4³ beats-classical `b71da32b` 0.612; 5³ parity@512) at n≥128. PASS-15 `b3ea0b95` is the scar — an n=32 eval promoted a net on a fluctuation that vanished at n=128. SPRT makes every downstream AUX/ARCH/SEARCH A/B both trustworthy and cheap. **Do early, alongside everything.**

### EVAL-2 — Superko-aware exact solver (history-threaded TT) — push S3 past 2×2×2
*Theme: Proof · extends PROOF-3 `22d59c45` · source: extends PROOF-3 · node `soft-thunder-1632`*

Extend the exact solver beyond the 2×2×2 frontier by keying the transposition table on (position, superko-history) so memoization stays **sound** under superko — PROOF-3 `22d59c45` proved position-only memo is unsound in 3D (value is history-dependent). The only path to a meaningful S3 oracle (near-optimal check vs ground truth) on bigger boards. Self-contained, theoretically clean, CPU-only, reuses INFRA-2's Zobrist.

### EVAL-3 — Train-time × test-time scaling-law characterization (strength surface)
*Theme: Proof · extends scaling-law `0bc38c41`, PROOF-2 `75615ad2` · source: autogo · node `cold-poetry-1723`*

Map a3go strength as a *joint* surface over training compute (net size × data) × test-time search × board size — autogo's central scaling-law thesis, instantiated for 3D Go. We have the two marginals (cross-board law `0bc38c41`; search-scaling amplifies with size `75615ad2`); the joint surface tells us where compute is best spent per board. A strong, legible science headline, best run after the aux/capacity nets exist so the train-time axis is meaningful.

### SCI-1 — Center/positional value + 3D opening explorer (joseki book)
*Theme: Science · extends SCIENCE-1 `5e34766d`, Q8 `853d7c2c` · source: online-go + KataGo · node `muddy-art-1226`*

Mine a strong net's self-play for 3D opening theory: does the third dimension give the center/interior systematic value? 2D Go opens in corners; our 4³ champion showed **no** positional preference (`853d7c2c`) — a genuine 3D oddity worth nailing down on bigger boards where the degree-6 interior dominates. Package it as a browsable 3D opening explorer (online-go-style). Best after a stronger net exists.

### TOOL-3 — 3D game-review UI: ownership heatmap + score-estimate bar + win-rate graph + SGF-equiv record
*Theme: Tooling · extends TOOL-1 `1f59266a`, TOOL-2 `742a0aab`, AUX-1, AUX-2 · source: online-go · node `twilight-hill-9139`*

Build an online-go-style 3D review UI: per-voxel ownership heatmap (AUX-1), live score-estimate bar (AUX-2), per-move win-rate graph, move-by-move review with variations, over an SGF-equivalent 3D record. TOOL-1/2 already render boards and read out the net; the missing layer is *analysis*. The overlays are free once AUX-1/AUX-2 exist (their head outputs *are* the overlays). **Depends on AUX-1 + AUX-2.**

## Guidance — what may work / where to go

The campaign's own evidence says the remaining levers for S1/S5 are **signal
richness and capacity, not more search or self-play** (PASS-15). KataGo's track
record sharpens this into a recommended order:

1. **Auxiliary targets first (AUX-1 ownership, AUX-2 score, AUX-3 soft-policy).** KataGo's single biggest early-training accelerator, and they hit our two named weak spots: the policy head degrades on big boards (`0bc38c41`) → soft-policy; win-rate can't identify komi because games are blowout-dominated (`2a2ca6b9`) → a score-margin head gives a dense, komi-sensitive signal. Cheapest high-upside branch; pure training change on the existing nets. **Likely to work.**
2. **Richer input planes (ARCH-3) + capacity (ARCH-2).** Ko is ubiquitous in 3D (`31dae43b`) yet the net never sees a ko-ban/history plane — a cheap, plausibly large fix. Nested-bottleneck capacity is the literal "scale capacity" lever PASS-15/PROOF-1 point to for S1.
3. **EVAL-1 SPRT + re-power audit — do this alongside everything.** PASS-15 proved n≤32 evals are too noisy to gate on; SPRT makes every future A/B both well-powered and cheap. High integrity value, low cost. **Do early.**
4. **Score-aware play (SEARCH-1) + dynamic komi** once AUX-2 lands — unlocks honest komi/handicap evaluation and could finally make S4-style big-board comparisons meaningful.
5. **Search Elo levers (SEARCH-2/3/4)** are real (KataGo banks 30–90 Elo each) but depend on the aux heads (uncertainty/optimistic need short-term/soft targets) — sequence them after AUX.
6. **ARCH-1 size-agnostic net** is the keystone for the whole SCALE theme (one net 3³→9³, curriculum transfer) and the most reusable single build; medium cost, high leverage.
7. **EVAL-2 superko-aware solver** is the only path to a *meaningful S3* (PROOF-3 left 2×2×2 as the frontier); self-contained, theoretically clean, no GPU.
8. **EVAL-3 scaling-law study** reframes our cross-board law as autogo's central scaling thesis — a strong "science" headline once the aux/capacity nets exist.
9. **Lower priority / dependent:** SEARCH-5 self-play tweaks (self-play already shown not to lift absolute strength on 5³ — value is in *data quality* for the aux-head retrain), SCI-1 opening explorer & TOOL-3 review UI (legibility/science payoff, best after a stronger net exists).

**Rejected as before:** 7³ net-vs-classical (classical unrunnable, PASS-13);
managed compute ($0/local); more plain frozen-net self-play (both gates exhausted,
PASS-14/15).

---

High-value core if the breadth is trimmed: **AUX-1/2/3, ARCH-1/3, EVAL-1/2.**
Pick against the [EXPANSION index node](https://flywheel.paradigma.inc) (`proud-king-2753`)
and the Phase-3 hub `e917c9e4`; the index carries the live status table.
