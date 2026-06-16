"""AUX-1: A3GoNet + a per-voxel ownership head (KataGo's ownership aux target).

A3GoNetOwn replicates A3GoNet's stem/tower/policy/value submodules *exactly*
(same module names, same capacity on the policy+value path) and adds an
ownership head off the same trunk that predicts each cell's final owner in
[-1, +1] (tanh). forward(x) returns (policy_logits, value) — identical signature
to A3GoNet, so BatchedMCTS / the eval harness use it unchanged. forward_own(x)
additionally returns the (B, N, N, N) ownership map for training.

A/B design: the baseline is *this same class* trained with ownership weight
lambda=0 (the ownership head then gets no gradient and the trunk is identical to
a plain A3GoNet); the treatment is lambda>0. Same architecture, same init seed —
the only difference is whether the dense ownership signal flows into the trunk.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from net import ResBlock, encode  # noqa: F401  (encode re-exported for callers)


class A3GoNetOwn(nn.Module):
    def __init__(self, n: int, channels: int = 32, blocks: int = 3):
        super().__init__()
        self.n = n
        self.num_actions = n * n * n + 1
        self.stem = nn.Sequential(
            nn.Conv3d(3, channels, 3, padding=1, bias=False),
            nn.BatchNorm3d(channels),
            nn.ReLU(),
        )
        self.tower = nn.Sequential(*[ResBlock(channels) for _ in range(blocks)])
        # Policy head (identical to A3GoNet)
        self.p_conv = nn.Conv3d(channels, 4, 1, bias=False)
        self.p_bn = nn.BatchNorm3d(4)
        self.p_fc = nn.Linear(4 * n * n * n, self.num_actions)
        # Value head (identical to A3GoNet)
        self.v_conv = nn.Conv3d(channels, 2, 1, bias=False)
        self.v_bn = nn.BatchNorm3d(2)
        self.v_fc1 = nn.Linear(2 * n * n * n, 64)
        self.v_fc2 = nn.Linear(64, 1)
        # Ownership head (AUX-1): trunk -> conv -> per-voxel tanh
        self.o_conv = nn.Conv3d(channels, channels, 3, padding=1, bias=False)
        self.o_bn = nn.BatchNorm3d(channels)
        self.o_out = nn.Conv3d(channels, 1, 1)

    def _trunk(self, x):
        return self.tower(self.stem(x))

    def _pv(self, t):
        p = F.relu(self.p_bn(self.p_conv(t)))
        p = self.p_fc(p.flatten(1))
        v = F.relu(self.v_bn(self.v_conv(t)))
        v = F.relu(self.v_fc1(v.flatten(1)))
        v = torch.tanh(self.v_fc2(v))
        return p, v.squeeze(-1)

    def forward(self, x):
        return self._pv(self._trunk(x))

    def forward_own(self, x):
        t = self._trunk(x)
        p, v = self._pv(t)
        o = torch.tanh(self.o_out(F.relu(self.o_bn(self.o_conv(t)))))
        return p, v, o.squeeze(1)
