"""ARCH-3: train A3GoNetIn on the rich-plane distill data, selecting an input
config's channels (input_planes.CONFIG_CHANNELS). Same soft policy target
(T=4, x8 weight, prune=0.02) and same A3GoNet trunk/heads as AUX-3/ARCH-2, so the
ONLY difference between arms is the input representation. `base` slices the first
3 channels -> reproduces the AUX-3 soft baseline.

env: A3GO_CFG (base|koban|libs|capture|history|all), A3GO_CH (64), A3GO_BLK (6),
     A3GO_SEED, A3GO_SP_T (4), A3GO_SP_W (8), A3GO_SP_PRUNE (0.02)

    A3GO_CFG=all A3GO_SEED=0 uv run python train_arch3.py distill_arch3_5cubed.npz 40 best_arch3_all_s0.pt
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np
import torch
import torch.nn.functional as F
from net_arch3 import A3GoNetIn, param_count
from train_softpolicy import build_targets
from input_planes import slice_stack, CONFIG_CHANNELS


def main() -> int:
    npz = sys.argv[1] if len(sys.argv) > 1 else "distill_arch3_5cubed.npz"
    epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    out = sys.argv[3] if len(sys.argv) > 3 else "best_arch3.pt"
    batch = int(sys.argv[4]) if len(sys.argv) > 4 else 256
    lr = float(sys.argv[5]) if len(sys.argv) > 5 else 1e-3

    cfg = os.environ.get("A3GO_CFG", "all")
    assert cfg in CONFIG_CHANNELS, f"unknown A3GO_CFG={cfg}"
    T = float(os.environ.get("A3GO_SP_T", "4.0"))
    W = float(os.environ.get("A3GO_SP_W", "8.0"))
    prune = float(os.environ.get("A3GO_SP_PRUNE", "0.02"))
    ch = int(os.environ.get("A3GO_CH", "64")); blk = int(os.environ.get("A3GO_BLK", "6"))
    seed = int(os.environ.get("A3GO_SEED", "0"))
    device = "cuda" if torch.cuda.is_available() else "cpu"

    d = np.load(npz)
    X_full, V, Z = d["X"], d["V"], d["Z"]
    X = slice_stack(X_full, cfg)
    in_planes = X.shape[1]
    n = X.shape[2]
    P = build_targets(V, "soft", T, prune)
    best_action = V.argmax(1)

    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(X))
    X, P, Z, best_action = X[perm], P[perm], Z[perm], best_action[perm]
    nh = max(1, int(0.1 * len(X)))
    Xh, Zh, bah = X[:nh], Z[:nh], best_action[:nh]
    Xt, Pt, Zt = X[nh:], P[nh:], Z[nh:]

    net = A3GoNetIn(n, in_planes=in_planes, channels=ch, blocks=blk).to(device)
    pc = param_count(net)
    print(f"# train_arch3 {npz}: cfg={cfg} in_planes={in_planes} ch={ch}x{blk} params={pc} "
          f"T={T} W={W} prune={prune} train {len(Xt)} holdout {len(Xh)} seed={seed} {device}", flush=True)
    opt = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=1e-4)
    t = lambda a: torch.from_numpy(a).to(device)
    Xt_t, Pt_t, Zt_t = t(Xt), t(Pt), t(Zt)
    Xh_t, Zh_t = t(Xh), t(Zh)
    bah_t = torch.from_numpy(bah).to(device)

    def holdout():
        net.eval()
        with torch.no_grad():
            logits, v = net(Xh_t)
            top1 = (logits.argmax(1) == bah_t).float().mean().item()
            top3 = (logits.topk(3, 1).indices == bah_t.unsqueeze(1)).any(1).float().mean().item()
            vmse = F.mse_loss(v, Zh_t).item()
        net.train()
        return top1, top3, vmse

    m = Xt_t.shape[0]
    history = []; best = -1.0; best_stats = None; t0 = time.time()
    for ep in range(1, epochs + 1):
        net.train(); pm = torch.randperm(m, device=device); last = 0.0
        for i in range(0, m, batch):
            idx = pm[i:i+batch]
            logits, v = net(Xt_t[idx])
            pol = -(Pt_t[idx] * F.log_softmax(logits, 1)).sum(1).mean()
            loss = W * pol + F.mse_loss(v, Zt_t[idx])
            opt.zero_grad(); loss.backward(); opt.step()
            last = float(loss.item())
        top1, top3, vmse = holdout()
        history.append({"epoch": ep, "train_loss": round(last, 4), "holdout_top1": round(top1, 4),
                        "holdout_top3": round(top3, 4), "holdout_value_mse": round(vmse, 4)})
        if top1 > best:
            best = top1; best_stats = history[-1]; torch.save(net.state_dict(), out)
        if ep % 5 == 0 or ep == 1:
            print(f"  ep{ep}: loss={last:.3f} top1={top1:.4f} top3={top3:.4f} vmse={vmse:.4f}", flush=True)

    result = {"npz": npz, "n": int(n), "cfg": cfg, "in_planes": int(in_planes),
              "channel_indices": CONFIG_CHANNELS[cfg], "channels": ch, "blocks": blk, "params": pc,
              "T": T, "W": W, "prune": prune, "epochs": epochs, "batch": batch, "lr": lr, "seed": seed,
              "train_examples": int(len(Xt)), "holdout_examples": int(len(Xh)),
              "best_holdout_top1": round(best, 4), "best_epoch_stats": best_stats,
              "final": history[-1], "secs": round(time.time() - t0, 1), "history": history}
    json.dump(result, open(out.replace(".pt", "") + "_train.json", "w"), indent=2)
    print(f"best holdout top1 = {best:.4f} params={pc} cfg={cfg} -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
