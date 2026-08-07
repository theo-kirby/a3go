# a3go — agent contract

`a3go` ("autonomous 3-dimensional Go research") is a self-contained repo for an
**autonomous research agent** to investigate 3D Go. It bundles a validated 3D-Go
engine, a self-play stack, and the reference docs you need; you build the
research graph and run the campaign yourself.

If you are starting this repo for the first time, your runbook is
**[docs/BOOTSTRAP.md](./docs/BOOTSTRAP.md)** — go there after reading this page.

## Relation to `goban`

The engine and self-play code are **vendored** from the `goban` project (a 3D-Go
fork of online-go/goban). They were copied in, not depended on, because
optimizing the engine is itself a research target — a3go owns this code and may
rewrite it. Provenance, the exact source commit, and the re-sync/divergence rules
are in **[src/engine/VENDORED.md](./src/engine/VENDORED.md)**. Vendored files keep
their Apache-2.0 headers; new a3go code is MIT (see `LICENSE` and `NOTICE`).

## Read order

1. **[docs/BOOTSTRAP.md](./docs/BOOTSTRAP.md)** — the first-run startup sequence
   (validate → auth/budget → build graph → autonomous run).
2. **[docs/THESIS.md](./docs/THESIS.md)** — the research thesis and the open
   questions (posed *without* answers).
3. **[docs/CODEBASE.md](./docs/CODEBASE.md)** — engine + self-play API and how to
   run it.
4. **[.hypergraph/AGENTS.md](./.hypergraph/AGENTS.md)** — how to record findings
   as a durable research graph (the Hypergraph protocol; supersedes the
   Flywheel-native flow — [docs/FLYWHEEL.md](./docs/FLYWHEEL.md) is retained for
   reading the frozen pre-adoption archive graph).
5. **[docs/DIRECTIONS.md](./docs/DIRECTIONS.md)** — Phase-3 frontier-EXPANSION
   catalog: the menu of STAGED research directions (KataGo/autogo/online-go-
   inspired) with a what-may-work priority guide. Read before picking the next
   execution pass; the live status now lives in **[STATE.md](./STATE.md)** (the
   generated frontier), not the legacy EXPANSION index node.

Frozen upstream engine references live in
[docs/upstream/](./docs/upstream/) (historical; for the *why* of the engine).

## Essential commands

```bash
npm install              # one-time
npm test                 # tsx test/engine3d.test.ts — expect 48/48 checks
npm run selfplay         # MCTS vs random self-play
npm run exp:komi | exp:boards | exp:ladders | exp:mcts-vs-random
npm run checks           # eslint + prettier:check
```

## Toolchains: `tsx` for TS, `uv` for GPU/Python

- **TypeScript (engine + self-play, CPU-only): always run through `tsx`** or the
  `npm run` scripts. **Never `node file.ts`** — the engine uses TS enums and
  extensionless relative imports the bare `node` runtime does not resolve;
  `npm test`/`npm run *` already use `tsx`. This stack does not touch the GPU.
- **Anything that needs the GPU is Python, managed with
  [`uv`](https://docs.astral.sh/uv/)** (`uv init`/`uv add`/`uv run`, not raw
  `pip`/`venv`/`conda`). That's the deferred neural phase; keep it in its own
  Python project under `neural/` (see [neural/README.md](./neural/README.md)).

## Working rules

- **Blank slate.** This repo intentionally ships no prior findings. Derive every
  conclusion by running code; do not assume outcomes from the question framing.
- **Budget.** The first autonomous run is **$0 / local-only** — no *managed/cloud*
  compute, grants, or leases (see BOOTSTRAP.md). This is **not** a reason to
  ration the local box: it's a strong machine (RTX 5090 + a 16-core/32-thread
  CPU, all free) — parallelize self-play across cores and use the GPU for the
  neural phase. Report, don't spend, only if a question genuinely needs
  *managed* compute.
- **You own `src/engine`.** Modify it freely (the throughput hot path is a prime
  target), but **log every divergence from upstream in
  [src/engine/VENDORED.md](./src/engine/VENDORED.md)**.
- **Record findings in the Hypergraph record graph.** Results are durable,
  causally-parented record nodes with a `## State Impact` declaration — not just
  console output (run the `hypergraph-record` skill; see
  [.hypergraph/AGENTS.md](./.hypergraph/AGENTS.md)). Evidence files are committed
  to the repo and referenced by path. The pre-adoption Flywheel graph is a frozen
  archive: read it via FLYWHEEL.md if you need legacy artifacts, never write to it.
- **Breadth over depth — expand the surface, don't grind.** The priority is
  *widening the research frontier*: seed many new directions, out-of-the-box
  approaches, and edge hypotheses as STAGED graph nodes — not committing hours of
  wall-clock to long training runs on big models. Prefer cheap, fast probes
  (minutes, not hours) that each resolve a node and open new branches. When a
  question would need a long/expensive train to settle, **stage it as a hypothesis
  with a crisp decision criterion and move on** rather than blocking on it; only
  spend real compute on a direction the cheap signal already favors. A diverse
  graph of pickable, well-posed bets is worth more than one deeply-ground result.
  (Staged bets are decision record nodes whose `## State Impact` opens `open`
  state nodes on the frontier — see `.hypergraph/AGENTS.md`.)

## Finish checklist (before committing)

- [ ] `npm test` → **48/48 checks pass**
- [ ] `npm run checks` → eslint + prettier clean
- [ ] Any engine divergence logged in `src/engine/VENDORED.md`
- [ ] New findings recorded as hypergraph record nodes (with evidence committed);
      `hypergraph export` + `check` exit 0

<!-- hypergraph:begin -->
## Hypergraph protocol

This repo's memory lives in two graphs under `.hypergraph/` (see `.hypergraph/AGENTS.md`):

1. **Orient on arrival**: run the `hypergraph-orient` skill or read `STATE.md` —
   the frontier (open/broken/blocked) is what matters now.
2. **Record every unit of work** (features, fixes, experiments, dead ends,
   decisions): the `hypergraph-record` skill — one causally-parented record node
   with a `## State Impact` section. Unrecorded work is invisible to the project.
3. **Never write state nodes**; declare impacts and let the
   `hypergraph-reconcile` skill fold them. `STATE.md` is generated — never
   hand-edit it.
4. **Verify before finishing**: `hypergraph export` + `hypergraph check` must
   exit 0.
<!-- hypergraph:end -->
