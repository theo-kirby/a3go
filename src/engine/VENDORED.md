# Vendored engine slice — provenance

The 3D Go engine in this directory is **vendored** from the `goban` project. It
was copied in, not added as a dependency, because optimizing the engine (its
throughput hot path in particular) is an explicit research target — a3go owns
this code and may rewrite it.

## Source

- **Repo:** `/home/theo/goban` (local working copy)
  - remote: `git@github.com:theo-kirby/goban.git` (a fork of
    `https://github.com/online-go/goban`)
- **Commit at copy time:** `c7b826604642ccdf9b9a535a4c43357992d4b971`
- **License:** Apache-2.0 (headers preserved verbatim in each file below)

## Files (the verified self-contained 5-file closure)

Copied from `goban/src/engine/` with no other dependencies (no `util/`,
`third_party`, `StoneString`, `MoveTree`, or 2D engine code):

| file                  | imports                                  |
| --------------------- | ---------------------------------------- |
| `Topology.ts`         | (none)                                   |
| `GobanError.ts`       | (none)                                   |
| `formats/JGOF.ts`     | `../GobanError`                          |
| `BoardState3D.ts`     | `./formats/JGOF`, `./Topology`           |
| `Scorer3D.ts`         | `./BoardState3D`, `./formats/JGOF`       |

`index.ts` here is **a3go-owned** (not vendored): the public engine API barrel.

The self-play stack under `../selfplay/` (`agents.ts`, `playGame.ts`,
`match.ts`, `mcts.ts`) and the test harness `test/engine3d.test.ts` were also
authored upstream in goban; they import only from this engine slice.

## Re-sync (one-liner)

To re-pull the upstream engine files verbatim (overwrites local edits — see the
divergence rule below before doing this):

```bash
G=/home/theo/goban/src/engine; D=/home/theo/a3go/src/engine; \
cp "$G/Topology.ts" "$G/BoardState3D.ts" "$G/Scorer3D.ts" "$G/GobanError.ts" "$D/" && \
cp "$G/formats/JGOF.ts" "$D/formats/JGOF.ts"
```

## Divergence rule

a3go is the owner of this code. **Do not blind-re-pull** from upstream once you
have started modifying the engine. When you diverge from the upstream commit
above (e.g. to optimize the hot path, change data structures, or fix a bug),
record the change here — what you changed, why, and whether it should be sent
back upstream — so this file stays an accurate map of how a3go's engine differs
from goban's.

### Divergence log

- _(none yet — engine is at the upstream commit above)_
