---
node_id: 5f10c19e-3e85-52f8-b0dd-ac675108a364
slug: shrill-morning-5745
title: 'Q6 RESOLVED: SEKI exists in 3D — minimal eyeless 2-dame seki survives 6-connectivity'
created_at: '2026-06-07T15:56:57.856132+00:00'
parents:
- icy-rain-9864
- green-queen-4645
summary: 'Exact bounded-minimax capture solver + eye detector confirm seki (mutual life, no two eyes) on a 4x3x1 2D slice, and that the SAME standoff stays seki when opened into 3D (dame box gains z-liberties): the extra liberties don''t rescue the filling player. Controls pass (capturable group detected; two-eye group detected).'
origin:
  backend: flywheel
  node_id: 5f10c19e-3e85-52f8-b0dd-ac675108a364
  slug: shrill-morning-5745
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 5751f5e0-661f-5b62-9047-81833313c575
  slug: falling-meadow-2470
  revision: 0
  pushed_at: '2026-08-08T10:01:49+00:00'
  content_sha256: a70ca976f5b45fd70513b0de650c1901c3dd29932ce65b185367ecc35f28ffe4
---
# Q6 — Does seki occur in 3D, and does 6-connectivity change it?

**Method (deterministic, exact):** a bounded-minimax capture solver over the real engine rules (attacker moves first, defender plays optimally, memoized by position hash) plus a simple-eye detector. A group is *alive* if the attacker cannot force its capture; **seki = both groups alive AND neither alive by its own two eyes** (life is mutual/shared-liberty, not independent). No self-play, no net. Added optional non-cube `shape=(w,h,d)` to the Python engine so a thin `(w,h,1)` slice is genuine 2D 4-connectivity (cube crossval still 60/60 — additive, safe).

## Cases
| case | shape | empties | verdict |
|---|---|---|---|
| A — eyeless walls share exactly 2 dame | 4x3x1 (2D) | 2 | **SEKI** (both uncapturable, 0 eyes) |
| B — same standoff opened into 3D; dame box gains z-liberties | 4x3x2 | 4 | **SEKI** (still both uncapturable, 0 eyes) |
| C control — lone stone vs enemy | 3x3x1 | 7 | not-seki, **capturable detected** ✓ |
| D control — group enclosing two simple eyes | 4x4x1 | — | **two-eye life detected** (eyes=2) ✓ |

## Finding
**Seki is real in 3D Go.** The canonical 2D minimal seki — two eyeless groups sharing exactly two dame, where filling a dame self-ataris (mutual zugzwang) — carries over. Crucially, when the contested region is opened into the third dimension (case B: a 2x1x2 dame box, so a stone played in the dame gains an extra z-neighbour liberty), the seki **survives**: the extra liberty does not let the filling side escape the capture race. So 6-connectivity does not trivially dissolve seki by handing out rescue liberties.

## Caveat
The eye test counts *simple* eyes; it would under-count large/compound eye spaces, so 'seki' here means 'mutual life with no simple two-eye life' for these confined constructed test tubes — which is exactly the regime of interest. Establishing the *minimal* 3D seki volume and seki frequency in real games is the natural follow-up.

Artifact: experiments_seki.json (full solver output), seki3d.py (harness).