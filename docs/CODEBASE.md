# Codebase guide — engine + self-play API

Factual reference for the code in `src/`. No research conclusions live here —
those belong in the Flywheel graph. For *why* the engine is shaped this way, see
the frozen upstream references in [docs/upstream/](./upstream/).

## Layout

```
src/
  engine/        vendored 3D Go engine (see src/engine/VENDORED.md) + index.ts barrel
    Topology.ts        lattice + neighbor relation
    BoardState3D.ts    board state, moves, capture, superko
    Scorer3D.ts        Tromp-Taylor scoring + influence estimate
    GobanError.ts      error types
    formats/JGOF.ts    JGOFNumericPlayerColor enum (+ unused JSON-Go types)
    index.ts           public engine API (a3go-owned barrel)
  selfplay/      self-play tooling
    agents.ts          Agent interface, RandomAgent, legality/eye helpers, makeRng
    mcts.ts            UCT MCTSAgent
    playGame.ts        single-game runner
    match.ts           color-balanced head-to-head match driver
    index.ts           public self-play API (barrel)
    experiments/       runnable experiment scripts (exp_*.ts)
test/
  engine3d.test.ts     48-check correctness harness
experiments/           OUTPUT dir for run logs / result JSON (gitignored)
```

## Running things (tsx only)

Everything runs through **`tsx`** (TypeScript execute). The engine uses TS enums
and extensionless relative imports that the bare `node` runtime does not handle —
**always use `tsx` or the `npm run` scripts; never `node file.ts`.**

```bash
npm install              # one-time
npm test                # tsx test/engine3d.test.ts — expect 48/48 checks pass
npm run selfplay        # MCTS vs random (alias of exp:mcts-vs-random)

npm run exp:mcts-vs-random  [games] [playouts]
npm run exp:komi            [size] [games] [playouts]
npm run exp:boards          [games] [playouts] [sizesCSV]
npm run exp:ladders

npm run checks          # eslint + prettier:check (run before committing)
```

Each `exp_*.ts` honors an `OUT=<path>` env var to write its results as JSON
(write these under `experiments/`, which is gitignored except for `.gitkeep`).
Direct invocation also works, e.g.
`OUT=experiments/komi3.json npx tsx src/selfplay/experiments/exp_komi_mcts.ts 3 50 128`.

## Engine API

Import from the barrel: `import { ... } from "../engine";` (or `./engine` /
`../../engine` depending on depth).

### `JGOFNumericPlayerColor`

Enum used for board contents: `EMPTY = 0`, `BLACK = 1`, `WHITE = 2`.

### `Topology3D(width, height, depth)`

The lattice and its 6-neighbor relation — the seam where 3D plugs in.

- `numPoints` — total intersections (`width*height*depth`).
- `forEachPoint(cb)` — visit every `(x, y, z)`.
- `forEachNeighbor(x, y, z, cb)` — visit in-bounds orthogonal neighbors (≤6).
- `idx(x, y, z)` — flat integer index for scratch buffers / sets.

`Topology2D(width, height)` (4 neighbors, `depth = 1`) is also exported for
genuinely-2D control experiments.

### `BoardState3D(config)`

`config: { width, height, depth, board?, player? }`. Storage is
`board[z][y][x]` of `JGOFNumericPlayerColor`. Standard Go rules over the 6-neighbor
topology.

- `play(x, y, z): PlaceResult3D` — place the current player's stone. Resolves
  captures (6-neighbor liberty counting), **rejects suicide**, and enforces
  **positional superko** (the resulting whole-board position may not repeat).
  **Throws `Error` on any illegal move** — callers must handle the throw
  (this is how legality is probed; see `isLegalMove`). On success it advances
  `player` and `move_number` and returns `{ color, position, captured }`.
- `pass()` — pass; flips `player`, increments `move_number`.
- `setStone(x, y, z, color)` — place a stone directly, bypassing rules. For
  setting up positions ("sandbox place mode"); does **not** check legality or
  update history.
- `getStone(x, y, z)` — read a point.
- `getRawStoneString(x, y, z)` — flood-fill the connected same-color group.
- `countLiberties(group)` / `getLiberties(group)` — liberty count / positions.
- `getColorLiberties(color)` — every empty point adjacent to a stone of `color`.
- `clone()` — **deep copy including superko history**, move number, and prisoner
  counts. Required for any rollout / legality probe: a clone must reject the same
  superko-illegal moves the original would.
- `hashPosition()` — string hash of the board (excludes side-to-move; positional,
  not situational, superko).
- Fields: `width`, `height`, `depth`, `topology`, `player`, `move_number`,
  `black_prisoners`, `white_prisoners`.

### `Scorer3D`

- `scoreTrompTaylor(state, { komi?, dead? }): ScoreResult` — **final**
  Tromp-Taylor area scoring. All stones count as alive (minus any flat indices
  in the optional `dead` set); each maximal empty region goes to a color iff it
  borders exactly one color; komi is added to White; `diff = black.area −
  white.area` (positive ⇒ Black ahead).
- `estimateScoreInfluence(state, { komi? }): ScoreResult` — **live mid-game**
  estimate via multi-source BFS influence. Returns the same shape; crude around
  life & death.
- `ScoreResult`: `{ black, white: { stones, territory, area }, komi, diff,
  winner: "black"|"white"|"draw", margin, blackTerritory, whiteTerritory,
  neutral }`.

## Self-play API

Import from `../selfplay` (or the relevant depth).

### `Agent` interface

```ts
interface Agent { readonly name: string; selectMove(state: BoardState3D): Move; }
type Move = Intersection3D | "pass";
```

`selectMove` **must treat `state` as read-only** (clone before mutating).

- `RandomAgent(seed, name?, { fillEyes? })` — uniform-random over legal moves,
  skipping its own simple eyes by default. `fillEyes: true` recovers the naive
  everything-legal behavior for comparison.
- `MCTSAgent({ playouts, seed, komi?, c?, name? })` — classical UCT with
  eye-aware random rollouts.
- Helpers: `makeRng(seed)` (deterministic mulberry32 PRNG — use for
  reproducibility), `isLegalMove`, `isSimpleEye`, `emptyPoints`.

### Runners

- `playGame(initial, black, white, { komi?, maxMoves?, recordMoves? }):
  GameRecord` — play one game to completion (two consecutive passes), then score
  it. `black` moves first. `GameRecord` carries winner, `diff`, `margin`,
  `moveCount`, prisoner counts, `terminatedByPasses`, `hitMoveCap`, and optional
  `moves`.
- `playMatch(makeA, makeB, { n, games, komi?, seedBase? }): MatchResult` —
  color-balanced head-to-head (swaps who plays Black each game). Returns win
  counts, A's win-rate with a 95% CI, the per-color split, averages, and
  wall-clock seconds.

## Performance note (code fact)

Self-play is **CPU-bound** and, **as written, single-threaded**. The per-move
hot path is the clone-and-try legality check: `isLegalMove` (and MCTS
expansion/rollout) `clone()`s the board and calls `play()` inside a try/catch,
and `clone()` deep-copies the board and the superko history set. Throughput
therefore falls off quickly as the board grows.

This is a property of the **current code, not the hardware**. The machine has
many CPU cores and a capable GPU (see [BOOTSTRAP.md](./BOOTSTRAP.md) → "You have
strong local compute"), all of which are free to use at $0. Two independent
levers exist and both are fair game: **parallelism** (fan games across cores via
`worker_threads` or multiple processes — embarrassingly parallel, since games are
independent) and **a faster per-move path** (e.g. incremental legality + Zobrist
hashing instead of clone-and-try). Measuring the throughput and deciding
whether/how to attack it is itself part of the work (see
[THESIS.md](./THESIS.md) Q2 and `neural/README.md`).
