"""TOOL-1 (board viz) — render an N^3 3D-Go position to PNG.

Two views: (1) a row of 2D z-slice layers (the practical way to read a 3D board —
each layer is a w×h plane), and (2) a 3D voxel scatter. Optional overlays: last
move, a policy heatmap (per-cell probabilities), and Tromp-Taylor territory tint.

Decoupled from the engine — takes a grid array — so it works for any position.

    from viz import render_slices
    render_slices(board.grid, "pos.png", player=board.player, last_move=(x,y,z))
"""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EMPTY, BLACK, WHITE = 0, 1, 2


def render_slices(grid, path, player=None, last_move=None, policy=None, title=None):
    """grid: (w,h,d) int array. policy: optional (w,h,d) float (e.g. net policy over
    plays, pass excluded). Renders d z-layers side by side."""
    grid = np.asarray(grid)
    w, h, d = grid.shape
    fig, axes = plt.subplots(1, d, figsize=(2.4 * d + 0.5, 2.7), squeeze=False)
    axes = axes[0]
    pmax = float(policy.max()) if policy is not None and policy.max() > 0 else 1.0
    for z in range(d):
        ax = axes[z]
        ax.set_xlim(-0.5, w - 0.5); ax.set_ylim(-0.5, h - 0.5)
        ax.set_xticks(range(w)); ax.set_yticks(range(h))
        ax.set_aspect("equal"); ax.grid(True, color="#bbada0", lw=0.8)
        ax.set_facecolor("#e8d9b5")
        ax.set_title(f"z={z}", fontsize=9)
        if policy is not None:
            ax.imshow(policy[:, :, z].T, origin="lower", extent=(-0.5, w - 0.5, -0.5, h - 0.5),
                      cmap="Reds", alpha=0.55, vmin=0, vmax=pmax, zorder=0)
        for x in range(w):
            for y in range(h):
                v = grid[x, y, z]
                if v == EMPTY:
                    continue
                col = "black" if v == BLACK else "white"
                ax.scatter([x], [y], s=320, c=col, edgecolors="black", zorder=3)
        if last_move is not None and last_move != "pass" and last_move[2] == z:
            lx, ly, _ = last_move
            ax.scatter([lx], [ly], s=70, marker="x", c="#d62728", zorder=4, linewidths=2.5)
        ax.tick_params(labelsize=7)
    bs = int((grid == BLACK).sum()); ws = int((grid == WHITE).sum())
    tt = title or "3D-Go position"
    pl = {BLACK: "Black", WHITE: "White"}.get(player, "")
    fig.suptitle(f"{tt}  —  {w}×{h}×{d}   ●{bs}  ○{ws}" + (f"   ({pl} to move)" if pl else ""),
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


def render_voxels(grid, path, title=None):
    grid = np.asarray(grid)
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection="3d")
    filled = grid != EMPTY
    colors = np.empty(grid.shape + (4,), dtype=float)
    colors[grid == BLACK] = (0.1, 0.1, 0.1, 0.95)
    colors[grid == WHITE] = (0.95, 0.95, 0.95, 0.95)
    ax.voxels(filled, facecolors=colors, edgecolor="#555", linewidth=0.3)
    ax.set_title(title or "3D-Go position (voxels)")
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


if __name__ == "__main__":
    # demo: a small sample position
    import sys
    sys.path.insert(0, ".")
    from a3go_engine import Board
    import random
    b = Board(4)
    rng = random.Random(7)
    for _ in range(18):
        mv = b.legal_moves()
        if not mv:
            break
        b.play(*rng.choice(mv))
    render_slices(b.grid, "figures/sample_board_slices.png", player=b.player,
                  title="Sample 4³ position (18 random plies)")
    render_voxels(b.grid, "figures/sample_board_voxels.png",
                  title="Sample 4³ position (voxels)")
    print("wrote figures/sample_board_slices.png, figures/sample_board_voxels.png")
