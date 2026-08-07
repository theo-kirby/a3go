# Hypergraph onboarding — a3go

This project runs under the **Hypergraph protocol**
([spec + tooling](https://github.com/theo-kirby/hypergraph-protocol); PyPI:
`hypergraph-protocol`, CLI `hypergraph`). Two graphs live in this repo as
committed markdown under `.hypergraph/graph/`:

- **Record graph** (root `purple-fog-6345`) — append-only history: every
  experiment, decision, dead end. The 108 pre-adoption nodes were imported
  verbatim from the legacy Flywheel campaign graph.
- **State graph** (root `royal-comet-4977`) — small distilled projection of what
  is true *now*; `STATE.md` is its generated snapshot. The **frontier**
  (open/broken/blocked state nodes) is what a fresh agent reads first.

## The four non-negotiables

1. **Orient on arrival.** Run the `hypergraph-orient` skill (or read `STATE.md`).
   Do not traverse the record graph to find out what's true — that's what the
   state graph is for. Frontier provenance slugs point into the record graph for
   history when you need it.
2. **Record every unit of work** — feature, fix, experiment, negative result,
   decision, staged bet — with the `hypergraph-record` skill: one causally-parented
   record node with a `## State Impact` section (choose the parent by "this work
   followed from that result"). Evidence files are committed to the repo and
   referenced by path. Work that isn't recorded is invisible to the campaign.
3. **Never write state nodes.** Declare impacts; only the `hypergraph-reconcile`
   skill folds them into the state graph. Never hand-edit `STATE.md`.
4. **Verify before finishing:**
   ```bash
   hypergraph export --config .hypergraph/config.yml
   hypergraph check --record .hypergraph/cache/record.json \
       --state .hypergraph/cache/state.json --config .hypergraph/config.yml
   ```
   Exit 0 required. The `hypergraph` CLI must be >=0.0.2 (adoption-epoch support); until 0.0.2 is on PyPI, use the dev checkout: `uv run /Users/theo/hypergraph/tools/hypergraph.py <subcommand> …`.
   Then `git add .hypergraph/graph STATE.md` — an uncommitted node is no node.

## Adoption specifics

- **Epoch**: config `epoch.marker` names the "Adopted Hypergraph" record node.
  Record nodes older than it are legacy history — exempt from template
  compliance, still fully citable as `[rec: <slug>]` evidence.
- **Archive**: the pre-adoption Flywheel graph (roots `purple-fog-6345`,
  `proud-king-2753`) is **frozen and read-only**. Legacy *artifacts* (plots,
  logs, SGFs) were not imported — fetch them from the archive via Flywheel MCP
  (`docs/FLYWHEEL.md`) if needed. Never write to the archive.
- **Mirror**: `mirror: flywheel` — local files are canonical; the reconcile pass
  pushes to NEW mirror roots and runs `push --verify`. Mirror slugs differ from
  local slugs; the mirror's "Hypergraph mirror slug legend" node maps them.
- The legacy "EXPANSION index" workflow (live status table in a Flywheel node)
  is superseded: staged directions are `open` state nodes on the frontier;
  their history lives in the imported record nodes.
