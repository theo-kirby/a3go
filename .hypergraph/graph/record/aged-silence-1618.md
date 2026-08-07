---
node_id: 01d82e67-c9ad-59a5-8ccc-95e9a7d6adf7
slug: aged-silence-1618
title: Ladders break in 3D — work only where topology is genuinely 2D
created_at: '2026-06-07T11:42:43.519227+00:00'
parents:
- solitary-bush-1534
summary: 'Exact minimax ladder solver: the ladder captures in a depth=1 plane but FAILS on a 3D surface and in the open 3D interior. The extra connectivity lets the victim gain liberties past the escape cap.'
flywheel:
  node_id: 01d82e67-c9ad-59a5-8ccc-95e9a7d6adf7
  slug: aged-silence-1618
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 16fd87aee7e422ffddb05c2480b26f96ba0e99a2e1029221158fee3b378e3e9b
---
# Q3 — Do ladders work in 3D Go? **No (except in genuinely-2D topology).**

## Method
Exact bounded minimax ladder solver (`src/selfplay/experiments/exp_ladders.ts`): attacker ataris the victim to 1 liberty, defender must extend; the solver searches both sides to depth 24 with the standard "victim reaches >=3 liberties => escaped" prune (LIBCAP=3). Deterministic — no seeds, fully reproducible. Identical victim-at-2-liberties setups are run across three topologies.

## Result
| scenario | initLibs | libsAfter1stExtend | ladder works? |
|---|---|---|---|
| A. 2D plane 5×5×1, chased into corner | 2 | **2** | **YES (capture)** |
| B. 3D surface 5×5×2 (same attack, +z leak) | 3 | n/a | **NO (escapes)** |
| C. 3D open interior 5×5×5 | 2 | **5** | **NO (escapes)** |

## Mechanism
A ladder needs the victim pinned at exactly 2 liberties so each atari→extend cycle is repeatable. The crux is how many liberties a *forced extension* yields:
- **2D plane (A):** the forced extension leaves the victim at **2** liberties → re-atariable → the ladder runs to the edge and captures.
- **3D interior (C):** the same forced extension leaves the victim at **5** liberties (the 6-neighbor point exposes new liberties in the orthogonal dimensions) → far past the escape cap → atari cannot be maintained → **escapes**.
- **3D surface (B):** even a single extra z-layer already gives the victim a 3rd initial liberty; the pin never forms.

## Conclusion
The ladder — the canonical shape-dependent 2D tactic — **does not function under 6-connectivity**. One extra dimension of liberty is enough to break the 2-liberty pin it depends on. This is a strong-form confirmation that connectivity-dependent tactics do not automatically carry over to 3D.

## Reproduce
`OUT=experiments/ladders.json npx tsx src/selfplay/experiments/exp_ladders.ts` (deterministic). Artifact attached: per-scenario verdicts.