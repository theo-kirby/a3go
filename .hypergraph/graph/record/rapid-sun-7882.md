---
node_id: 6551d432-c11e-52bf-9a6b-caf49ab6fe0c
slug: rapid-sun-7882
title: 'SEARCHX-1 — Net-vs-search decomposition [RESOLVED: raw net WEAK (policy-only ~0.6 vs random); SEARCH carries 5³ strength, policy is the headroom]'
created_at: '2026-06-18T11:52:29.845009+00:00'
parents:
- proud-king-2753
summary: RESOLVED. On 5³ the raw net is weak — policy-only ~0.61 and value-only-1ply ~0.54 vs random; win-rate climbs sharply with MCTS sims. Search, not the prior, carries strength; with the value head well-calibrated (PROBE-2) this is genuine look-ahead. The policy (not value) is the lever with most headroom. Multi-board sweep needs cheap 4³/7³ libs nets.
origin:
  backend: flywheel
  node_id: 6551d432-c11e-52bf-9a6b-caf49ab6fe0c
  slug: rapid-sun-7882
  revision: 2
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: c47f6634-0edf-51da-ba2f-e3e6933c4e30
  slug: floral-truth-1986
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: 614c4f9712e4c79c77e0549222515200c96e614587d7a02cb9266dbb632e4507
---
# SEARCHX-1 — net-vs-search decomposition (libs 5³) [RESOLVED]

How much of agent strength is the NET vs the SEARCH? Degenerate regimes anchored by win-rate vs uniform-random; policy-only also head-to-head vs full(sims=64).

## Result (win-rate vs random, 3 seeds, 24 games/seed)
- policy-only (raw net, no tree):   0.6135 [0.501, 0.726]
- value-only 1-ply (greedy):        0.5417 [0.4266, 0.6568]
- MCTS sims sweep: sims1=0.6135; sims4=0.8424; sims16=0.9438; sims64=0.9583
- policy-only vs full(sims64) [A=policy]: 0.1463 [0.0647, 0.2279]

## Findings
1. **The raw net is WEAK on 5³** — policy-only beats random only ~0.61, value-only-1ply only ~0.54. The network's standalone play is barely above random (consistent with the policy-weak-on-big-boards scar `0bc38c41`).
2. **Search carries the strength:** win-rate vs random climbs sharply with sims (sims1=0.6135; sims4=0.8424; sims16=0.9438; sims64=0.9583); the agent's competence is dominated by MCTS, not the prior. policy-only loses badly to full-search (policy-wr 0.1463).
3. Because the value head is well-calibrated (PROBE-2), this search dependence is genuine look-ahead, not value denoising.

## Implication
On 5³ the lever with most headroom is the POLICY (a stronger raw policy would cut the sims needed) and search efficiency — not the value head. Pairs with SYMM-1 (does TTA substitute for sims?) and the soft-policy / hard-mining (DATA-1) directions. The per-board-size sweep needs cheap 4³/7³ libs nets (stage).

## Artifact
`searchx1_decomp.json`. Code: `searchx_decomp.py` (policy-only + value-only-1ply agents over the BatchedMCTS/config_planes harness).

*Resolved PASS-20 (breadth pass, cheap-first). Budget $0/local. Engine/tests untouched (additive probe scripts only).*