---
node_id: 0baf0eb3-0365-5424-8406-91fd087a410f
slug: lively-orchard-3365
title: Adopted Hypergraph
created_at: '2026-08-07T20:29:15+00:00'
parents:
- crimson-rice-4497
summary: 'Adoption epoch marker: 108-node legacy Flywheel graph (purple-fog-6345 + proud-king-2753 union) imported verbatim as the record graph; archive frozen (artifacts stay there); state graph seeded by this pass; strictly-older nodes I2-exempt.'
---
## What

Adopted the Hypergraph protocol for a3go (mode A of the hypergraph-adopt skill). The complete legacy Flywheel campaign graph — the union of the campaign root `purple-fog-6345` (73d510e5-875e-59b2-ad07-f4711ee0b748) and the EXPANSION index anchor `proud-king-2753` (f9f2bf74-2ce6-5488-b471-dc0b6c422b99), 108 nodes — was exported and imported verbatim into `.hypergraph/graph/record/` (node_ids and slugs preserved). This node is the adoption epoch marker: record nodes created strictly before it are legacy history, exempt from I2/template compliance, and remain fully citable evidence.

## Why

The campaign's memory lived in Flywheel under a Flywheel-native contract ("commit findings as Flywheel nodes"); the graph is public but not writable by this account, and docs/DIRECTIONS.md's own framing had drifted from the executed truth (six directions run since its "none executed" seeding pass). Adoption brings the record into the repo (git-native local backend), distills an honest state graph, and reroutes the agent contract through hypergraph — with the legacy graph frozen as the archive.

## Method

Union export via one `flywheel_export_subgraph` call over both anchors (closure verified: 0 missing parents; 108 ≥ the 67 nodes cited for the root alone, the index subtree accounting for the rest). `hypergraph import --record` wrote 108 node files; each carries its archive Flywheel identity in frontmatter. Distillation mined four sources in parallel: the repo docs (README/THESIS/DIRECTIONS/six result summaries + executed-but-unsummarized result JSONs) and three graph branches (science questions, neural + phase-3, EXPANSION subtree) read by fanned-out subagent readers. Node-id prefixes cited in docs (b3ea0b95, 31dae43b, 0bc38c41, …) were resolved to slugs via the export before being written into provenance. Per the M1 parentage rule this full-import marker is parented on the newest legacy node (crimson-rice-4497, the ROBUST-1 staged direction).

## Result

Adoption boundary drawn; the state graph is seeded by this pass (see State Impact). What stays on the archive: node artifacts (plots, JSONs, game records attached to legacy nodes) — the local backend has no artifact op, so the `archive:` block in `.hypergraph/config.yml` (both anchors) is the only pointer to them; the archive is read-only from here on. The legacy EXPANSION-index workflow (live status table in a Flywheel node) is superseded by the frontier in STATE.md. Distillation-time contradictions are recorded honestly in the state nodes rather than silently resolved — chiefly: the "~98% of single captures trigger a superko ban" claim (31dae43b) measured at 18–32% by the motif census (spring-sea-3008); and the "5³ parity@512" headline that collapsed to 0.414 [0.332,0.501] under the n=128 re-power (rough-paper-7328). The adopt step "interview the user for invisible dead ends" was skipped — this adoption ran autonomously; the Operator should append any unrecorded dead ends as record nodes.

## Repo

- repo: https://github.com/theo-kirby/a3go.git
- branch: main
- commit: 22316111f24fe4f353cbbaaaa43503fc8815730a

## State Impact

- target: NEW engine-classical — seeded working: three validated engines (TS reference 48/48, Python vectorized+Zobrist, C++ generator) + classical self-play/experiment stack
- target: NEW neural-stack — seeded working: distillation recipe, input-plane results (liberties decisive), capacity findings, trained champions
- target: NEW search — seeded working: classical UCT + batched AZ MCTS, Gumbel negative, search-carries-strength decomposition
- target: NEW evaluation-statistics — seeded working: anchored Elo ladder, SPRT gate, GPU net-vs-net screen, n>=128 discipline born from the n=32 scar
- target: NEW science-questions — seeded working: Q1–Q10 characterization with explicit open tails
- target: NEW strength-program — seeded open: success-bar v1 cleared on 4^3; v2 S1/S4/S5 unmet, 5^3 ceiling just below parity, 7^3 decisive test never run
- target: NEW staged-frontier — seeded open: 29 staged EXPANSION directions with priority ordering and dependency structure
- target: NEW methodology-tooling — seeded working: $0/local, breadth-over-depth, design gate, viz/play tooling; known doc-drift list
