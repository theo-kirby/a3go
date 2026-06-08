"""Policy/value network for 3D Go — a small 3D-conv residual tower.

Input: 3 planes over the N^3 lattice (black stones, white stones, side-to-move).
Outputs: policy logits over N^3 + 1 actions (every point + pass) and a scalar
value in [-1, 1] (expected result for the side to move).
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from a3go_engine import Board, BLACK, WHITE


def encode(board: Board) -> np.ndarray:
    """(3, N, N, N) float32 planes for the side to move."""
    n = board.w
    planes = np.zeros((3, n, n, n), dtype=np.float32)
    planes[0] = board.grid == BLACK
    planes[1] = board.grid == WHITE
    planes[2] = 1.0 if board.player == BLACK else 0.0
    return planes


class ResBlock(nn.Module):
    def __init__(self, c: int):
        super().__init__()
        self.c1 = nn.Conv3d(c, c, 3, padding=1, bias=False)
        self.b1 = nn.BatchNorm3d(c)
        self.c2 = nn.Conv3d(c, c, 3, padding=1, bias=False)
        self.b2 = nn.BatchNorm3d(c)

    def forward(self, x):
        y = F.relu(self.b1(self.c1(x)))
        y = self.b2(self.c2(y))
        return F.relu(x + y)


class A3GoNet(nn.Module):
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
