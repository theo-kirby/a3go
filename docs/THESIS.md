# Research thesis — Autonomous 3D-Go research

## The thesis

Go (Baduk) is normally played on a 2D grid: each intersection has up to 4
orthogonal neighbors, and the rules of liberties, capture, and territory follow
from that 4-connectivity. **3D Go** plays the identical rules on an N×N×N cubic
lattice instead: an interior intersection has up to **6 neighbors** (±x, ±y, ±z).
Nothing else changes — liberties, capture, suicide, superko, and area scoring
are exactly the standard rules, evaluated over the 6-neighbor topology.

The central claim to test:

> **We can train a strong agent to play 3D Go on an N³ 6-liberty board, and in
> doing so characterize how the game differs from 2D.**

"Strong" must be defined operationally (see [Success bar](#success-bar) below):
there is no human 3D-Go expert pool to measure against, so strength is defined
relative to baselines and to the agent's own self-play history.

The program has two intertwined goals:

1. **Build strength** — produce an agent that decisively beats simple baselines
   and improves against itself.
2. **Map the game** — answer concrete questions about how 6-connectivity changes
   Go: balance, board size, tactics, and life & death.

This repo ships a validated engine and a self-play stack (see
[CODEBASE.md](./CODEBASE.md)) so these questions can be answered **empirically,
by running code** — not by argument. The questions below are deliberately posed
*without* answers; the research is to derive them.

## The exploratory surface (open questions)

These are open. Treat each as a hypothesis to test with experiments, not a
settled fact. Record what you find as Flywheel nodes with attached artifacts.

### Q1 — What is fair komi?

Black moves first and gains an advantage; **komi** is the compensation given to
White to make the game fair. The fair komi for 2D 19×19 is well known
(~6.5–7.5). For an N³ board it is unknown. What komi makes the game balanced,
for each board size? Does "fair" by win-rate agree with "fair" by mean score
margin, or do they diverge? How precisely can it be pinned down, and what
limits that precision?

### Q2 — Which board sizes are interesting and tractable?

Candidate sizes are 3³, 4³, 5³, 7³, 9³. Which are trivial (effectively solved or
near-solved)? Which are decisive vs. draw-prone? How does game length scale? And
crucially — which are **computationally tractable** for self-play on the
available hardware? Characterize the trade-off and pick the size(s) the rest of
the campaign should focus on.

### Q3 — Do classic 2D tactics survive 6-connectivity?

The **ladder** is the canonical example: a forced capture that works by keeping
the victim pinned at exactly 2 liberties while chasing it to the edge. Whether
this — and other shape-dependent tactics — still function in 3D is open, because
the number of liberties a stone gains by extending depends on local
connectivity, which differs from 2D. Which 2D tactics carry over, which break,
and why?

### Q4 — How do life & death work in 3D?

In 2D, a group is unconditionally alive with two eyes. What is the analogous
condition on a 6-neighbor lattice? What is the minimum eye space for life? Does
seki (mutual life) occur, and how often? Is life & death harder or easier to
read than in 2D?

### Q5 — What else is mechanically different from 2D?

A catalog of "oddities": ways 3D Go behaves unlike 2D Go. Candidates to probe
include how games terminate, ko/superko frequency, the value of corners vs.
edges vs. faces vs. the interior, capturing-race behavior, and whether naive
self-play policies behave the same way they do in 2D. Build the catalog
empirically; confirm or refute each candidate by running code.

## Success bar

There is **no human 3D-Go expert pool**, so "strong" cannot mean "beats human
experts." Define it operationally instead:

- **Beats baselines.** The agent decisively beats a uniform-random baseline and
  a fixed-strength classical baseline (e.g. MCTS at a set playout budget),
  measured over color-balanced matches with confidence intervals.
- **Rising self-play strength.** Successive agents beat their predecessors —
  a monotone (within noise) self-play strength curve.

A result "counts" when it is reproducible from a seed and backed by a committed
Flywheel node with its data artifact attached.

## How this connects to the rest of the repo

- [CODEBASE.md](./CODEBASE.md) — the engine + self-play API you use to run the
  experiments above (factual; no conclusions).
- [FLYWHEEL.md](./FLYWHEEL.md) — how to record findings as a durable research
  graph.
- [BOOTSTRAP.md](./BOOTSTRAP.md) — the startup sequence that turns this thesis
  into a running autonomous campaign.
- `neural/README.md` — the deferred neural phase and the gate that opens it.
