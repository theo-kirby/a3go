---
node_id: 9a106027-6d5a-551f-a928-c7c63ff68e58
slug: shrill-union-9485
title: 'Q9 RESOLVED: fair komi on 4^3 ~= 0.5 area pts (SE 0.39, criterion met) via trained net; margin- and win-rate-fair agree near 0-0.5'
created_at: '2026-06-07T17:05:14.814770+00:00'
parents:
- silent-fire-7633
- crimson-voice-3644
summary: '640 net self-play games (4^3, komi=0): mean signed area margin (B-W) = 0.53, SE 0.386 <= 0.5 -> fair komi pinned. Win-rate-fair komi ~0 (black 0.478 at komi 0) agrees with margin-fair ~0.5. Precision limit is the heavy-tailed blowout distribution (std ~9.8), which M5 throughput makes affordable to average out.'
flywheel:
  node_id: 9a106027-6d5a-551f-a928-c7c63ff68e58
  slug: shrill-union-9485
  revision: 1
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: 3020b70d3c75050d016f5d4463a51d8f58e4c557567f52d49102aac6a2158314
---
# Q9 — pin fair komi on 4^3 with the trained net

**Method (the estimator pass-1 recommended):** win-rate vs komi is degenerate on small blowout-dominated boards, so we use the **mean signed area margin**. Play many net self-play games at komi=0 (sims=48, low-temp sampling for variety), record each game's pre-komi area diff (black_area - white_area); fair_komi = mean(diff), SE = std/sqrt(N). Decision criterion (control): **SE <= 0.5 on 4^3**.

## Result (N=640)
| quantity | value |
|---|---|
| mean area diff (B-W) | **0.53** |
| std | 9.77 |
| **SE of mean** | **0.386 <= 0.5 ✓** |
| fair komi estimate | **~0.5 area points** |

Win-rate cross-check (komi added to White): at komi 0, Black wins 0.478 of *decided* games (161/640 are draws — integer scoring + komi 0); at komi -0.47, Black 0.609; at komi +1, Black 0.301. So the **win-rate-fair komi is ~0 (slightly negative)** and the **margin-fair komi is ~0.5** — they **agree** that fair komi on 4^3 is small (~0 to 0.5).

## What limits precision (answers Q1's sub-question)
The margin distribution is **heavy-tailed / blowout-dominated** (std ~9.8, tails out to +/-36 on a 64-point board), so the fair-komi estimate is variance-limited, not bias-limited. An N=256 pilot gave 1.91 +/- 0.65; the apparent divergence from win-rate-fair was small-sample noise that vanished at N=640. Pinning to SE <= 0.5 needs N >~ 450 games — trivial now (640 games in ~11 min) precisely because of M5's 22x self-play throughput. The estimator is sound; **variance, not sampling cost, is the residual limit**, and even that is now cheap.

## Caveat
The net was trained at komi=0, so the margin reflects komi-0 play; and the heavy tail means the CLT SE is approximate. Treat fair komi as ~0.5 +/- 0.4 area points on 4^3.

Artifacts: experiments_komi_neural.json (N=640), experiments_komi_neural_n256.json (N=256 pilot), komi_neural.py.