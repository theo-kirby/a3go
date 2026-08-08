---
node_id: 742a0aab-7d63-5bfe-a0f3-3d2e29dc66c7
slug: frosty-bar-2241
title: 'TOOL-2 — Human-playable UX [DELIVERED: play.py CLI vs net/classical/random; --auto showcase captured]'
created_at: '2026-06-08T12:16:22.835247+00:00'
parents:
- mute-cloud-4824
summary: 'DELIVERED. play.py: terminal 3D Go vs net@sims/classical/random, z-slice board, coord input, live net policy+value readout, --render PNG-per-move, --auto agent-vs-agent showcase. Verified via an auto 4^3 net@128 game (Black +3, 67 plies) captured with renders + JSON move-log. $0/local.'
origin:
  backend: flywheel
  node_id: 742a0aab-7d63-5bfe-a0f3-3d2e29dc66c7
  slug: frosty-bar-2241
  revision: 2
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 359ee78a-b100-5818-87f5-ca306f19dc85
  slug: morning-union-7149
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: 8caf9d6ebc5f839b75873990b7e4ee31a4268f7b6c130a84cdeb6242fc282282
---
# TOOL-2 — Human-playable UX [DELIVERED]

Built `play.py`: terminal 3D Go vs any agent (`net@sims` GPU / `classical@p` / random). Board prints as z-slice layers with coords; human enters `x y z`/`pass`; engine validates. Vs a net, each turn shows the net's top-5 policy moves + value estimate (the agent's 'thinking'). `--render` saves a PNG per move (via TOOL-1); `--auto N` runs agent-vs-agent showcase games and writes a JSON move-log.

## Verified
Captured an `--auto` showcase: a full 4^3 net@128 self-play game, **Black +3 (31 vs 29 stones), 67 plies**, with a per-move PNG sequence + final board + JSON move-log (attached). Interactive human path is built (input loop with legal-move validation + policy/value readout).

$0/local.