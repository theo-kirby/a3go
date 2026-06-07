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
4. **[docs/FLYWHEEL.md](./docs/FLYWHEEL.md)** — how to record findings as a
   durable research graph.

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
- **Record findings in Flywheel.** Results are durable graph nodes with attached
  artifacts — not just console output (see FLYWHEEL.md).

## Finish checklist (before committing)

- [ ] `npm test` → **48/48 checks pass**
- [ ] `npm run checks` → eslint + prettier clean
- [ ] Any engine divergence logged in `src/engine/VENDORED.md`
- [ ] New findings committed as Flywheel nodes with artifacts
