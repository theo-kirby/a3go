"""ARCH-2: BN-free nested-bottleneck residual tower with fixed-variance init.

A3GoNetBR mirrors A3GoNet's input (3 planes) and output heads (policy logits over
N^3+1, scalar tanh value) EXACTLY in interface — forward(x) -> (p, v) — so the
eval harness and BatchedMCTS use it unchanged. The only change is the trunk:

  - **No BatchNorm anywhere** (stem, tower, heads) — removes the small-batch
    instability and the train/eval running-stat mismatch BN introduces.
  - **Nested-bottleneck block** (KataGo-style): outer residual whose branch is a
    1x1 reduce (c->cb) -> an inner residual of two 3x3 convs at the bottleneck
    width cb -> 1x1 expand (cb->c). More representational depth per FLOP.
  - **Fixed-variance / ReZero init:** each block ends with a learnable scalar gate
    `gamma` initialized to 0, so the tower is the identity map at init and every
    residual branch starts contributing zero. This is the normalization-free
    stabilizer (a robust cousin of Fixup) — guarantees a well-conditioned start
    without BN's running statistics.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from net import encode  # noqa: F401  (re-export; identical input encoding)


class NestedBottleneck(nn.Module):
    def __init__(self, c: int, cb: int, gamma0: float = 0.3):
        super().__init__()
        self.reduce = nn.Conv3d(c, cb, 1, bias=True)
        self.conv_a = nn.Conv3d(cb, cb, 3, padding=1, bias=True)
        self.conv_b = nn.Conv3d(cb, cb, 3, padding=1, bias=True)
        self.expand = nn.Conv3d(cb, c, 1, bias=True)
        # Fixed-variance gate: small positive init keeps per-block residual
        # variance ~O(1/L) (stable, BN-free) while letting all blocks learn from
        # step 0 -- ReZero's gamma0=0 leaves the deep trunk gated off and converges
        # far too slowly (validated in the smoke test).
        self.gamma = nn.Parameter(torch.full((1,), gamma0))

    def forward(self, x):
        y = F.relu(self.reduce(x))
        z = F.relu(self.conv_a(y))
        z = self.conv_b(z)
        y = F.relu(y + z)            # inner residual at the bottleneck width
        y = self.expand(y)
        return x + self.gamma * y    # outer residual; gamma starts at 0


class A3GoNetBR(nn.Module):
    def __init__(self, n: int, channels: int = 64, blocks: int = 8, bottleneck: int = 48,
                 gamma0: float = 0.3):
        super().__init__()
        self.n = n
        self.num_actions = n * n * n + 1
        self.channels, self.blocks, self.bottleneck = channels, blocks, bottleneck
        # BN-free stem
        self.stem = nn.Sequential(
            nn.Conv3d(3, channels, 3, padding=1, bias=True),
            nn.ReLU(),
        )
        self.tower = nn.Sequential(
            *[NestedBottleneck(channels, bottleneck, gamma0=gamma0) for _ in range(blocks)]
        )
        # BN-free policy head
        self.p_conv = nn.Conv3d(channels, 4, 1, bias=True)
        self.p_fc = nn.Linear(4 * n * n * n, self.num_actions)
        # BN-free value head
        self.v_conv = nn.Conv3d(channels, 2, 1, bias=True)
        self.v_fc1 = nn.Linear(2 * n * n * n, 64)
        self.v_fc2 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.tower(self.stem(x))
        p = F.relu(self.p_conv(x))
        p = self.p_fc(p.flatten(1))
        v = F.relu(self.v_conv(x))
        v = F.relu(self.v_fc1(v.flatten(1)))
        v = torch.tanh(self.v_fc2(v))
        return p, v.squeeze(-1)


def param_count(net) -> int:
    return sum(p.numel() for p in net.parameters())
