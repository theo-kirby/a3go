"""ARCH-3: A3GoNet with a configurable number of input planes.

Byte-for-byte identical to net.A3GoNet (same BN residual tower, same policy/value
heads, same init order) EXCEPT the stem's first conv accepts `in_planes` channels
instead of 3. With in_planes=3 the module is the SAME network as A3GoNet (same
param shapes, same seeded init), so the 3-plane `base` config is a clean control
for the richer-input arms — only the input representation varies.

Reuses ResBlock from net.py so the trunk is provably the same block.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from net import ResBlock


class A3GoNetIn(nn.Module):
    def __init__(self, n: int, in_planes: int = 3, channels: int = 32, blocks: int = 3):
        super().__init__()
        self.n = n
        self.in_planes = in_planes
        self.num_actions = n * n * n + 1
        self.stem = nn.Sequential(
            nn.Conv3d(in_planes, channels, 3, padding=1, bias=False),
            nn.BatchNorm3d(channels),
            nn.ReLU(),
        )
        self.tower = nn.Sequential(*[ResBlock(channels) for _ in range(blocks)])
        # Policy head
        self.p_conv = nn.Conv3d(channels, 4, 1, bias=False)
        self.p_bn = nn.BatchNorm3d(4)
        self.p_fc = nn.Linear(4 * n * n * n, self.num_actions)
        # Value head
        self.v_conv = nn.Conv3d(channels, 2, 1, bias=False)
        self.v_bn = nn.BatchNorm3d(2)
        self.v_fc1 = nn.Linear(2 * n * n * n, 64)
        self.v_fc2 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.tower(self.stem(x))
        p = F.relu(self.p_bn(self.p_conv(x)))
        p = self.p_fc(p.flatten(1))
        v = F.relu(self.v_bn(self.v_conv(x)))
        v = F.relu(self.v_fc1(v.flatten(1)))
        v = torch.tanh(self.v_fc2(v))
        return p, v.squeeze(-1)


def param_count(net) -> int:
    return sum(p.numel() for p in net.parameters())
