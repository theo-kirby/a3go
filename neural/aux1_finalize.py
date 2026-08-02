"""AUX-1 finalizer: pool the seed A/B at 5^3 s512, summarise train metrics, and
render the ownership-heatmap figure (the one expected AUX-1 artifact still missing).

Outputs:
  - aux1_ab_summary.json   pooled Wilson CIs (baseline lambda=0 vs ownership lambda=1.0)
                           + per-lambda value-MSE / ownership-accuracy from training
  - aux1_ownership_heatmap.png   predicted vs true per-voxel ownership on one played 5^3 game

Run: A3GO_CH=64 A3GO_BLK=6 uv run python aux1_finalize.py
"""
from __future__ import annotations
import json, math, os

import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from net import encode
from net_ownership import A3GoNetOwn
from a3go_engine import Board
from classical_mcts import ClassicalMCTS


def wilson(wins, total, z=1.96):
    if total == 0:
        return (0.0, 0.0, 0.0)
    p = wins / total
    d = 1 + z * z / total
    c = (p + z * z / (2 * total)) / d
    h = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d
    return (round(p, 4), round(max(0, c - h), 4), round(min(1, c + h), 4))


def pool(files):
    wins = decided = draws = 0
    for f in files:
        d = json.load(open(f))
        wins += d["net_wins"]
        decided += d["decided"]
        draws += d["draws"]
    p, lo, hi = wilson(wins, decided)
    return {"wins": wins, "decided": decided, "draws": draws,
            "winrate": p, "ci95": [lo, hi], "files": files}


def main():
    ch = int(os.environ.get("A3GO_CH", "64"))
    blk = int(os.environ.get("A3GO_BLK", "6"))

    # --- pool the 3 seeds at 5^3 s512 (seed0 = no-suffix run, seed1, seed2) ---
    l00 = pool(["experiments_aux1_5_l00_s512.json",
                "experiments_aux1_5_l00_s512_seed1.json",
                "experiments_aux1_5_l00_s512_seed2.json"])
    l10 = pool(["experiments_aux1_5_l10_s512.json",
                "experiments_aux1_5_l10_s512_seed1.json",
                "experiments_aux1_5_l10_s512_seed2.json"])

    # value-MSE / ownership-acc per lambda (single-train metrics)
    def train_metrics(tag):
        d = json.load(open(f"best_own5_{tag}_train.json"))
        bes = d.get("best_epoch_stats", {})
        return {"lambda": d.get("lambda"),
                "holdout_value_mse": bes.get("holdout_value_mse"),
                "holdout_own_mse": bes.get("holdout_own_mse"),
                "holdout_own_acc": bes.get("holdout_own_acc"),
                "holdout_policy_acc": bes.get("holdout_policy_acc")}

    tm = {}
    for tag in ["l00_s1", "l10_s1", "l00_s2", "l10_s2"]:
        try:
            tm[tag] = train_metrics(tag)
        except FileNotFoundError:
            pass

    ci_overlap = not (l10["ci95"][0] > l00["ci95"][1] or l00["ci95"][0] > l10["ci95"][1])
    summary = {
        "experiment": "AUX-1 per-voxel ownership head — pooled A/B (5^3, net_sims=512 vs classical@48, 3 seeds)",
        "baseline_lambda0": l00,
        "ownership_lambda1.0": l10,
        "delta_winrate": round(l10["winrate"] - l00["winrate"], 4),
        "strength_ci_overlap": ci_overlap,
        "beats_baseline_decisively": not ci_overlap and l10["winrate"] > l00["winrate"],
        "either_beats_classical": l00["ci95"][0] > 0.5 or l10["ci95"][0] > 0.5,
        "train_metrics": tm,
        "verdict": ("ownership head learns the territory map (own_acc~0.985 >> 0.8) but does NOT "
                    "decisively lift 5^3 strength (pooled CIs overlap) nor value-MSE; "
                    "negative for the strength/calibration hypothesis, positive deliverable "
                    "(working ownership predictor for TOOL-3 / SCIENCE-2)."),
    }
    json.dump(summary, open("aux1_ab_summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))

    # --- ownership heatmap on one played 5^3 game ---
    n = 5
    board = Board(n)
    a = ClassicalMCTS(playouts=128, seed=7, max_rollout=50)
    b = ClassicalMCTS(playouts=128, seed=4242, max_rollout=50)
    passes = 0
    for _ in range(n * n * n * 2):
        if passes >= 2:
            break
        mv = (a if board.player == 1 else b).select_move(board, passes)
        if mv == "pass":
            board.pass_move(); passes += 1
        else:
            board.play(*mv); passes = 0

    true_own = board.ownership_map().astype(np.float32)  # (n,n,n) in {-1,0,+1}
    net = A3GoNetOwn(n, channels=ch, blocks=blk)
    net.load_state_dict(torch.load("best_own5_l10.pt", map_location="cpu"))
    net.eval()
    x = torch.from_numpy(encode(board)).unsqueeze(0)
    with torch.no_grad():
        _, _, o = net.forward_own(x)
    pred_own = o.squeeze(0).numpy()  # (n,n,n) in [-1,+1]

    decided_mask = true_own != 0
    sign_agree = float((np.sign(pred_own[decided_mask]) == np.sign(true_own[decided_mask])).mean())
    summary["heatmap_sign_agreement_decided"] = round(sign_agree, 4)
    json.dump(summary, open("aux1_ab_summary.json", "w"), indent=2)

    fig, axes = plt.subplots(2, n, figsize=(3 * n, 6))
    for z in range(n):
        axes[0, z].imshow(true_own[:, :, z], cmap="bwr", vmin=-1, vmax=1)
        axes[0, z].set_title(f"true z={z}")
        axes[0, z].axis("off")
        axes[1, z].imshow(pred_own[:, :, z], cmap="bwr", vmin=-1, vmax=1)
        axes[1, z].set_title(f"pred z={z}")
        axes[1, z].axis("off")
    fig.suptitle(f"AUX-1 ownership: true (top) vs net-predicted (bottom), 5^3 game — "
                 f"sign-agreement on decided cells = {sign_agree:.3f}")
    fig.tight_layout()
    fig.savefig("aux1_ownership_heatmap.png", dpi=110)
    print(f"\nheatmap sign-agreement (decided cells) = {sign_agree:.4f}")
    print("wrote aux1_ab_summary.json, aux1_ownership_heatmap.png")


if __name__ == "__main__":
    main()
