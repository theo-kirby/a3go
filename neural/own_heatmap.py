"""AUX-1 / TOOL-3: render the ownership head's prediction vs the true terminal
Tromp-Taylor ownership for a sample net self-play game, as per-z-slice heatmaps.

    A3GO_CH=64 A3GO_BLK=6 uv run python own_heatmap.py best_own4_l10.pt 4 own_heatmap_4cubed.png
"""
from __future__ import annotations
import os, sys
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from net_ownership import A3GoNetOwn, encode
from batched_az import BatchedMCTS, action_to_move
from a3go_engine import Board


def main() -> int:
    ckpt = sys.argv[1] if len(sys.argv) > 1 else "best_own4_l10.pt"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    out = sys.argv[3] if len(sys.argv) > 3 else "own_heatmap_4cubed.png"
    ch = int(os.environ.get("A3GO_CH", "64")); blk = int(os.environ.get("A3GO_BLK", "6"))

    net = A3GoNetOwn(n, channels=ch, blocks=blk)
    net.load_state_dict(torch.load(ckpt, map_location="cpu"))
    net.eval()
    mcts = BatchedMCTS(net, "cpu", sims=64, seed=7)

    board = Board(n)
    passes = 0
    pre_terminal = None
    for _ in range(n * n * n * 2):
        if passes >= 2:
            break
        pre_terminal = board.clone()
        pi = mcts.run_policies([board], [passes], [0.3])[0]
        mv = action_to_move(int(pi.argmax()), n)
        if mv == "pass":
            board.pass_move(); passes += 1
        else:
            board.play(*mv); passes = 0

    true_own = board.ownership_map().astype(np.float32)  # absolute B+/W-
    # predicted ownership at the pre-terminal position, signed back to absolute
    bb = pre_terminal
    with torch.no_grad():
        _, _, o = net.forward_own(torch.from_numpy(encode(bb)[None]))
    pred = o[0].numpy()
    if bb.player != 1:  # encode/predict is side-to-move; convert to absolute B+
        pred = -pred

    s = board.score_tromp_taylor()
    fig, axes = plt.subplots(3, n, figsize=(3 * n, 9))
    if n == 1:
        axes = axes.reshape(3, 1)
    for z in range(n):
        # final stones
        ax = axes[0, z]
        grid = board.grid[:, :, z]
        ax.imshow(np.zeros_like(grid), cmap="Greys", vmin=0, vmax=1)
        for x in range(n):
            for y in range(n):
                v = grid[x, y]
                if v != 0:
                    ax.scatter(y, x, s=300, c="black" if v == 1 else "white",
                               edgecolors="black", zorder=3)
        ax.set_title(f"stones z={z}"); ax.set_xticks([]); ax.set_yticks([])
        # true ownership
        axes[1, z].imshow(true_own[:, :, z], cmap="bwr", vmin=-1, vmax=1)
        axes[1, z].set_title(f"true own z={z}"); axes[1, z].set_xticks([]); axes[1, z].set_yticks([])
        # predicted ownership
        axes[2, z].imshow(pred[:, :, z], cmap="bwr", vmin=-1, vmax=1)
        axes[2, z].set_title(f"pred own z={z}"); axes[2, z].set_xticks([]); axes[2, z].set_yticks([])

    # accuracy on non-neutral cells
    nz = np.abs(true_own) > 0.5
    acc = float((np.sign(pred) == np.sign(true_own))[nz].mean()) if nz.any() else float("nan")
    fig.suptitle(f"AUX-1 ownership head — {ckpt} on {n}^3  |  result {s['winner']} diff {s['diff']:.0f}"
                 f"  |  pred sign-acc {acc:.2f} (red=Black, blue=White)")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    print(f"saved {out}  (terminal {s['winner']} {s['diff']:.0f}, pred-vs-true sign-acc {acc:.3f})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
