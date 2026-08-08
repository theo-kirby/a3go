---
node_id: 73adb0d5-d1bc-58b2-a7ee-833ec3cce15b
slug: steep-sun-9979
title: 3DSCI-3 — Do 3D cyclic-ko pathologies exist? (double-ko, sending-two-returning-one, triple-ko) [edge hypothesis, engine-only]
created_at: '2026-06-18T11:52:28.415934+00:00'
parents:
- proud-king-2753
summary: 'Edge rules question: 2D Go has notorious cyclic positions (double-ko, sending-two-returning-one, triple-ko) that positional superko handles but situational superko doesn''t. Do 3D analogues exist, how common are they, and does the campaign''s superko implementation resolve them correctly? Engine-only construction + search; stresses the rules core and EVAL-2''s solver.'
origin:
  backend: flywheel
  node_id: 73adb0d5-d1bc-58b2-a7ee-833ec3cce15b
  slug: steep-sun-9979
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: ba4432ca-eba6-53e4-8f61-4d1676ea9414
  slug: spring-hat-5761
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: ecf95ac74922d867d06ed056847147fcf2995c2bb8772291439368a114e28f5b
---
# 3DSCI-3 — Do 3D cyclic-ko pathologies exist?

## Objective
Investigate whether 3D Go admits the cyclic-repetition pathologies that make 2D rules subtle: double-ko, sending-two-returning-one, triple-ko, and longer cycles. Construct candidate positions (by hand and by searching self-play games for near-repetitions), and verify the engine's positional-superko handling terminates and scores them correctly.

## Why it matters (which finding it extends)
The campaign leans heavily on superko (PROOF-3 `22d59c45`: value is history-dependent; ko is everywhere). If 3D admits cycles that the current superko check mis-handles, it threatens BOTH engine correctness and the ko-ban feature semantics. Conversely, proving 3D's extra connectivity makes such cycles rarer/impossible is a genuine rules-science result. Directly de-risks EVAL-2 `ebff5f9f` (the superko-aware solver) and the ko-ban plane.

## Implementation route
Two prongs: (a) constructive — attempt to build minimal double-ko / sending-two shapes in 3³/4³ and check engine behavior (legal-move set, hash-history termination, TT score); (b) empirical — scan self-play game records for positions whose zobrist recurs within N plies, classify the cycle type. Engine-only; reuse the existing zobrist history.

## Decision criterion (CI-based, n≥128)
Existence is binary, not CI-based: deliver either a concrete 3D cyclic-ko position (with engine trace) OR evidence (over n≥128 games + constructive attempts) that the common 2D cycles don't realize in 3D. Plus a correctness verdict on the engine's handling.

## Preconditions / risks
Engine validated; positional superko present. Risk: constructing these by hand in 3D is fiddly — lean on the empirical recurrence scan first. Pure analysis, no training.

## Cost · value
CHEAP (engine-only). Value: a rules-science result + correctness assurance under the campaign's most-relied-on mechanic; feeds EVAL-2 and the ko-ban feature.

## Expected artifacts
`cyclic_ko_probe.py`, any discovered cyclic positions (engine traces), a recurrence-scan JSON, an engine-correctness verdict note.

## Inspiration source
2D superko rules theory (double-ko/sending-two/triple-ko). Extends PROOF-3 `22d59c45`, EVAL-2 `ebff5f9f`.

*STAGED — not executed. Budget $0/local. Breadth-expansion PASS-20. Pick against the EXPANSION index `f9f2bf74` + hub `e917c9e4`.*