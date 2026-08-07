---
node_id: 083fdbd1-800d-5a2a-b33d-84b5d790167c
slug: lone-rain-3739
title: Science questions (Q1–Q10)
created_at: '2026-08-07T20:34:19+00:00'
parents:
- royal-comet-4977
summary: 'Q1–Q10 characterized: komi ~0.5 on 4^3 only; ladders break in 3D; two-eye life + seki hold; ko prior corrected to 18–32%; no 4^3 opening preference; memoization unsound. Open tails: snapback, seki frequency, 9^3.'
---
Status: working

## Current

- Q1/Q9 fair komi: unidentifiable by win-rate on 3³ (Black-win% flat across komi −1.5…+7.5 — blowout regime, |margin| 10–13 pts) [rec: gentle-sun-9997]; pinned on 4³ at ≈0.5 area pts (SE 0.386 ≤ the ±0.5 criterion, n=640 net self-play) [rec: shrill-union-9485]. 3³ and 5³ komi were never pinned; the seed hypothesis "fair komi grows with N" is neither confirmed nor falsified [rec: flat-frog-8683].
- Q2 board sizes: 4³ is the sweet spot; 3³ is near-2D (mean degree exactly 4.00, interior 3.7%) and draw-prone; 5³ is all-decisive and tractable via batching (0.122 games/s, 12× classical); game length scales ~linearly in points (34.9/74.5/138.4 moves) [rec: flat-frog-8683] [rec: broad-sun-8428] [rec: spring-cherry-3158].
- Q3: ladders break in 3D — exact bounded minimax shows the extra liberty dimension destroys the 2-liberty pin (works only where topology is genuinely 2D) [rec: aged-silence-1618].
- Q4/Q6 life & death: two-eye life holds in 3D; minimal unconditionally-alive eye space is the straight-four in both 2D and 3D; seki exists and survives 6-connectivity; every vol≤8 shape verdict equals its 2D verdict (3D does not make life easier per volume) [rec: bitter-firefly-3214] [rec: shrill-morning-5745] [rec: polished-snow-4561].
- Q7 ko: captures are common but the "~98% of single captures trigger a superko ban" prior [rec: weathered-frog-1610] is overstated in play — the motif census measured 18–32%, falling with board size, and ko-ban density <0.1% of cells [rec: spring-sea-3008].
- Q8: the 4³ champion shows no opening positional preference (corner=edge=face=interior ≈ uniform, unlike 2D corner-first theory); caveat — the policy is diffuse, and the sharper MCTS-visit-distribution test was never run [rec: long-king-8643].
- Q10: rising self-play strength resolved on 4³ — self-play volume breaks the gating plateau (5 promotions/12 gens; final beats its own gen-0 0.652 at identical sims) [rec: still-dream-7550].
- Exact ground truth: 2×2×1 fair komi +1; position memoization is UNSOUND (superko makes value history-dependent, demonstrated); exact solving stops at ~4 cells, set by ko, so 2×2×2 is already out of naive reach [rec: shrill-moon-6110].
- Open tails, never probed: 3D snapback (the ~2% non-ko single captures), seki frequency and minimal 3D seki volume in real games, 9³/non-cube boards [rec: weathered-frog-1610] [rec: shrill-morning-5745] [rec: tiny-rain-6373].

## Negative knowledge

- [scope: estimating fair komi by win-rate on small blowout boards | confidence: high | evidence: gentle-sun-9997, flat-frog-8683] Win-rate carries no komi information in blowout regimes (Black-win% flat across komi −1.5…+7.5 on 3³); mean signed margin is the estimator, and the cross-size margin table (−0.03/+2.10/−5.68) is itself untrustworthy at 60 games/size.

## Provenance

- lively-orchard-3365 — adoption distillation
- gentle-sun-9997 — Q1 komi unidentifiable by win-rate on 3³
- shrill-union-9485 — Q9 komi pinned on 4³
- flat-frog-8683 — Q2 board characterization
- broad-sun-8428 — geometry census, 3³ is mean-degree 4
- aged-silence-1618 — Q3 ladders break
- bitter-firefly-3214 — Q4 two-eye life
- shrill-morning-5745 — Q6 seki exists
- polished-snow-4561 — Q6 3D life not easier per volume
- weathered-frog-1610 — Q7 ko census (original prior)
- spring-sea-3008 — motif census correcting the ko prior
- long-king-8643 — Q8 no opening preference on 4³
- still-dream-7550 — Q10 rising strength resolved
- shrill-moon-6110 — PROOF-3 exact solves + memoization unsound
