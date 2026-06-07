# a3go

**Autonomous 3-dimensional Go research.** A self-contained repo for an autonomous
[Flywheel](https://docs.flywheel.paradigma.inc) research agent to investigate
**3D Go** — Go (Baduk) played on an N×N×N cubic lattice, where an interior point
has 6 liberties (±x, ±y, ±z) instead of 4. The rules are exactly standard Go;
only the neighbor topology changes.

It bundles a validated 3D-Go engine, a self-play stack (random + MCTS agents,
game/match runners, experiment scripts), and the reference docs an agent needs to
build a research graph and run an autonomous, $0/local-only campaign on the
thesis.

## Quick start

```bash
npm install
npm test            # tsx test/engine3d.test.ts — expect 48/48 checks pass
npm run selfplay    # MCTS vs random self-play summary
```

Everything runs through **`tsx`** — never `node file.ts` (the engine's TS enums +
extensionless imports require it). More commands:

```bash
npm run exp:mcts-vs-random   # MCTS vs uniform-random, by board size
npm run exp:komi             # fair-komi estimate via MCTS self-play
npm run exp:boards           # board-size characterization
npm run exp:ladders          # do 2D ladders survive 6-connectivity?
npm run checks               # eslint + prettier:check
```

## Docs

- **[AGENTS.md](./AGENTS.md)** — the agent contract and read order (`CLAUDE.md`
  is a symlink to it).
- **[docs/BOOTSTRAP.md](./docs/BOOTSTRAP.md)** — first-run startup sequence →
  autonomous campaign.
- **[docs/THESIS.md](./docs/THESIS.md)** — the research thesis and open questions.
- **[docs/CODEBASE.md](./docs/CODEBASE.md)** — engine + self-play API and how to
  run it.
- **[docs/FLYWHEEL.md](./docs/FLYWHEEL.md)** — recording findings as a durable
  research graph.
- **[docs/upstream/](./docs/upstream/)** — frozen engine references (historical).
- **[neural/README.md](./neural/README.md)** — the deferred neural-training phase
  and its start gate.

## Provenance & license

The engine and self-play code under `src/` are **vendored** from the `goban`
project (Apache-2.0) and may be modified here — see
[src/engine/VENDORED.md](./src/engine/VENDORED.md) and [NOTICE](./NOTICE).
a3go-authored code is MIT ([LICENSE](./LICENSE)).
