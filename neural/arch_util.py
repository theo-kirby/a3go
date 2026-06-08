"""Infer A3GoNet architecture (channels, blocks) from a checkpoint state_dict and
load it. Checkpoints in this repo were trained at either 32x3 or 64x6; rather than
hard-code per-file, read the shapes back off the weights so any checkpoint loads."""
from __future__ import annotations
import torch
from net import A3GoNet


def infer_arch(state: dict) -> tuple[int, int]:
    # channels = out-channels of the stem conv (stem.0.weight: [C,3,3,3,3])
    channels = state["stem.0.weight"].shape[0]
    # blocks = highest tower.<i>. index + 1
    idxs = set()
    for k in state:
        if k.startswith("tower."):
            idxs.add(int(k.split(".")[1]))
    blocks = (max(idxs) + 1) if idxs else 0
    return channels, blocks


def load_net(ckpt: str, n: int, device: str):
    state = torch.load(ckpt, map_location=device)
    ch, bl = infer_arch(state)
    net = A3GoNet(n, channels=ch, blocks=bl).to(device)
    net.load_state_dict(state)
    net.eval()
    return net, ch, bl
