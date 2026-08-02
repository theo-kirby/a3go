"""AUX-3: train plain A3GoNet from raw-visit distill data, building the policy
target either HARD (one-hot argmax visits, weight 1x) or SOFT (KataGo-style:
prune low-visit actions, p ∝ visits^(1/T), policy loss up-weighted Wx).

Clean A/B: identical X/Z/architecture/init seed; only the policy target + weight
differ. Eval the resulting checkpoints with net_vs_classical_mp.py.

env:
  A3GO_SP_MODE  = hard | soft        (default soft)
  A3GO_SP_T     = softmax temperature for visits^(1/T)   (default 4.0)
  A3GO_SP_W     = policy-loss weight                      (default 8.0 soft / 1.0 hard)
  A3GO_SP_PRUNE = visit floor as fraction of max visits   (default 0.02)
  A3GO_CH, A3GO_BLK, A3GO_SEED

    A3GO_SP_MODE=soft A3GO_CH=64 A3GO_BLK=6 uv run python train_softpolicy.py \
        distill_softpol_5cubed.npz 40 best_sp5_soft.pt 256 1e-3
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np
import torch
import torch.nn.functional as F
from net import A3GoNet


def build_targets(V, mode, T, prune_frac):
    """V: (N, A) raw visit counts -> target distribution (N, A)."""
    V = V.astype(np.float64)
    if mode == "hard":
        tgt = np.zeros_like(V)
        tgt[np.arange(len(V)), V.argmax(1)] = 1.0
        return tgt.astype(np.float32)
    # soft: prune below frac*max per row, then visits^(1/T), renorm
    mx = V.max(1, keepdims=True)
    floor = prune_frac * mx
    Vp = np.where(V >= np.maximum(floor, 1.0), V, 0.0)
    # guard rows that got fully zeroed (e.g. single-visit pass) -> fall back to V
    empty = Vp.sum(1) == 0
    Vp[empty] = V[empty]
    P = Vp ** (1.0 / T)
    P /= P.sum(1, keepdims=True)
    return P.astype(np.float32)


def main() -> int:
    npz = sys.argv[1] if len(sys.argv) > 1 else "distill_softpol_5cubed.npz"
    epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    out = sys.argv[3] if len(sys.argv) > 3 else "best_sp5.pt"
    batch = int(sys.argv[4]) if len(sys.argv) > 4 else 256
    lr = float(sys.argv[5]) if len(sys.argv) > 5 else 1e-3

    mode = os.environ.get("A3GO_SP_MODE", "soft")
    T = float(os.environ.get("A3GO_SP_T", "4.0"))
    W = float(os.environ.get("A3GO_SP_W", "8.0" if mode == "soft" else "1.0"))
    prune = float(os.environ.get("A3GO_SP_PRUNE", "0.02"))
    ch = int(os.environ.get("A3GO_CH", "64")); blk = int(os.environ.get("A3GO_BLK", "6"))
    seed = int(os.environ.get("A3GO_SEED", "0"))
    device = "cuda" if torch.cuda.is_available() else "cpu"

    d = np.load(npz)
    X, V, Z = d["X"], d["V"], d["Z"]
    n = X.shape[2]
    P = build_targets(V, mode, T, prune)
    best_action = V.argmax(1)  # "true best move" = max visits, for holdout acc

    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(X))
    X, P, Z, best_action = X[perm], P[perm], Z[perm], best_action[perm]
    nh = max(1, int(0.1 * len(X)))
    Xh, Ph, Zh, bah = X[:nh], P[:nh], Z[:nh], best_action[:nh]
    Xt, Pt, Zt = X[nh:], P[nh:], Z[nh:]
    print(f"# train_sp {npz}: mode={mode} T={T} W={W} prune={prune} train {len(Xt)} "
          f"holdout {len(Xh)} n={n} ch={ch}x{blk} seed={seed} {device}", flush=True)

    net = A3GoNet(n, channels=ch, blocks=blk).to(device)
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
            val = F.mse_loss(v, Zt_t[idx])
            loss = W * pol + val
            opt.zero_grad(); loss.backward(); opt.step()
            last = float(loss.item())
        top1, top3, vmse = holdout()
        history.append({"epoch": ep, "train_loss": round(last, 4), "holdout_top1": round(top1, 4),
                        "holdout_top3": round(top3, 4), "holdout_value_mse": round(vmse, 4)})
        if top1 > best:
            best = top1; best_stats = history[-1]; torch.save(net.state_dict(), out)
        if ep % 5 == 0 or ep == 1:
            print(f"  ep{ep}: loss={last:.3f} top1={top1:.4f} top3={top3:.4f} vmse={vmse:.4f}", flush=True)

    result = {"npz": npz, "n": int(n), "mode": mode, "T": T, "W": W, "prune": prune,
              "epochs": epochs, "batch": batch, "lr": lr, "channels": ch, "blocks": blk, "seed": seed,
              "train_examples": int(len(Xt)), "holdout_examples": int(len(Xh)),
              "best_holdout_top1": round(best, 4), "best_epoch_stats": best_stats,
              "final": history[-1], "secs": round(time.time() - t0, 1), "history": history}
    res_out = out.replace(".pt", "") + "_train.json"
    json.dump(result, open(res_out, "w"), indent=2)
    print(f"best holdout top1 = {best:.4f} -> {out}  ({res_out})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
