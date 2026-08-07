---
node_id: a2e7a6f9-25ee-5278-bcfd-9e7aab4326d3
slug: northern-creek-9091
title: Staged frontier (EXPANSION)
created_at: '2026-08-07T20:34:44+00:00'
parents:
- royal-comet-4977
summary: 29 staged directions with design briefs; GEO-1 precondition cleared (d=1 ≡ 2D Go, corner-flip endpoint measured); live priority REP-3 confirm → GEO-1/STRAT-1/LD-1 → ALGO-S1; ARCH-1 is the keystone bottleneck.
flywheel:
  node_id: f2640f0d-ecb6-55d4-9cfe-519938c9d136
  slug: tight-bread-8914
  revision: 1
  pushed_at: '2026-08-07T21:12:41+00:00'
  content_sha256: 84ca12837e7d7e61a61a1ffa74cab1d272d486b4d80890cad91642030ffea042
---
Status: open

## Current

- 29 staged EXPANSION directions await execution, each with a 10-field design brief and CI-based decision criterion (n≥128), catalogued by the index [rec: proud-king-2753]: the original-17 remainder (AUX-2 throbbing-unit-0557, AUX-4 broad-hall-8962, SEARCH-1 spring-brook-4774, SEARCH-2 noisy-dust-7661, SEARCH-3 cold-sun-4675, SEARCH-4 cold-butterfly-1441, SEARCH-5 icy-pine-8163, ARCH-1 tight-dust-1276, EVAL-2 soft-thunder-1632, EVAL-3 cold-poetry-1723, SCI-1 muddy-art-1226, TOOL-3 twilight-hill-9139, SCIENCE-2 proud-tree-3638), batch-1 leftovers (REP-1 rapid-salad-8510, REP-2 raspy-wood-4619, 3DSCI-3 steep-sun-9979, TRANSFER-1 withered-hall-6943), batch-2 knowledge axis (LD-1 patient-paper-9241, LD-2 cold-hill-1866, LD-3 lucky-wave-5153, STRAT-1 red-credit-3434, STRAT-2 wild-glade-7676, DATA-1 dry-glade-4547), batch-3 geometry/search (GEO-1 still-recipe-4954, GEO-2 lively-sun-0512, GEO-3 noisy-dream-0116, ALGO-S1 wispy-glitter-1456, ALGO-S2 cool-leaf-5231, ROBUST-1 crimson-rice-4497).
- The index's live priority (post round-2): REP-3 higher-power confirm (n≥300) → REP-3 finer-bucket arm (needs one re-collection) → GEO-1 / STRAT-1 / LD-1 (no-GPU engine science) → ALGO-S1 [rec: proud-king-2753].
- GEO-1 (still-recipe-4954) precondition cleared and the dimensionality ladder unblocked with a measured d=1 endpoint: on (3,3,1) komi 0, MCTS(512) self-play, n=128/arm, a corner first move flips Black from 100% to 1% win rate (CI-separated) vs center/edge/free — cell-type preference is decisive at d=1 yet absent on 4³ opening-uniformity, so STRAT-1 gains a depth axis: preference must die with depth somewhere on (n,n,d) [rec: icy-fjord-0022].
- Dependency structure: ARCH-1 (tight-dust-1276) is the keystone bottleneck — TRANSFER-1, GEO-3 and ROBUST-1 all hard-require it, and it is the most expensive staged item in an otherwise cheap-first frontier [rec: proud-king-2753]. AUX-2 (throbbing-unit-0557) blocks SEARCH-1, TOOL-3, SCI-1 and the komi/handicap program [rec: throbbing-unit-0557].
- Unbanked cheap wins named but never staged as nodes: the 7³ S4 run itself, SYMM-1 arm B (48× train-time augmentation), the PROBE-2 free temperature ≈0.65 strength A/B, the SCALE-libs higher-sims tie-break, a retrain-without-plane control for PROBE-1, and tuning the C++ teacher [rec: patient-silence-7334] [rec: bitter-hill-4867] [rec: bitter-pine-2861] [rec: square-heart-9657] [rec: blue-boat-2948].
- Graph hygiene inherited from the archive: wild-poetry-7539 and dark-poetry-2083 are byte-identical duplicate M5 nodes (downstream references use dark-poetry-2083); SCIENCE-2 and SCALE-libs never appeared in the index tables [rec: proud-king-2753] [rec: bitter-pine-2861].

## Negative knowledge

- [scope: net-vs-net screening at n≈72–96 decided games, sims 24–48 | confidence: medium | evidence: patient-silence-7334, small-mountain-7064, square-heart-9657] This power regime produced three consecutive non-decisions; SYMM-1 read 0.558 at n≈96 and went null at higher power — REP-3 reads the identical 0.558, so its n≥300 confirm must land before anything builds on it.

## Provenance

- lively-orchard-3365 — adoption distillation
- proud-king-2753 — the EXPANSION index: staged set, priorities, dependencies
- patient-silence-7334 — SYMM-1 null; arm B never staged
- small-mountain-7064 — REP-3 under-powered positive
- square-heart-9657 — PROBE-1 criterion unmet; retrain control never staged
- bitter-pine-2861 — SCALE-libs tie-break named, never staged
- blue-boat-2948 — C++ teacher tuning named, never staged
- icy-fjord-0022 — GEO-1 precondition cleared; d=1 endpoint measured
