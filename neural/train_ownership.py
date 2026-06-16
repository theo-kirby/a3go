"""AUX-1: train A3GoNetOwn on distilled data WITH the ownership aux target.

loss = policy-CE + value-MSE + lambda * ownership-MSE.  lambda=0 reproduces the
bare policy+value baseline on the identical architecture/seed (clean A/B). Tracks
holdout policy acc, value MSE, and end-game ownership sign-accuracy (on non-neutral
cells). Model selection = best holdout policy acc (same rule for baseline and
treatment, so ownership never biases selection).

    A3GO_OWN_LAMBDA=1.0 A3GO_CH=64 A3GO_BLK=6 uv run python train_ownership.py \
        distill_own_4cubed.npz 40 best_own4_l1.pt 256 1e-3
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np
import torch
import torch.nn.functional as F
from net_ownership import A3GoNetOwn


def main() -> int:
    npz = sys.argv[1] if len(sys.argv) > 1 else "distill_own_4cubed.npz"
    epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    out = sys.argv[3] if len(sys.argv) > 3 else "best_own_4cubed.pt"
    batch = int(sys.argv[4]) if len(sys.argv) > 4 else 256
    lr = float(sys.argv[5]) if len(sys.argv) > 5 else 1e-3
    lam = float(os.environ.get("A3GO_OWN_LAMBDA", "1.0"))
    ch = int(os.environ.get("A3GO_CH", "32")); blk = int(os.environ.get("A3GO_BLK", "3"))

    seed = int(os.environ.get("A3GO_SEED", "0"))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = np.load(npz)
    X, P, Z, O = d["X"], d["P"], d["Z"], d["O"].astype(np.float32)
    n = X.shape[2]
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(X))
    X, P, Z, O = X[perm], P[perm], Z[perm], O[perm]
    nh = max(1, int(0.1 * len(X)))
    Xh, Ph, Zh, Oh = X[:nh], P[:nh], Z[:nh], O[:nh]
    Xt, Pt, Zt, Ot = X[nh:], P[nh:], Z[nh:], O[nh:]
    print(f"# train_own {npz}: train {len(Xt)}, holdout {len(Xh)}, n={n}, ch={ch}x{blk}, "
          f"lambda={lam}, {device}", flush=True)

    net = A3GoNetOwn(n, channels=ch, blocks=blk).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=1e-4)
    t = lambda a: torch.from_numpy(a).to(device)
    Xt_t, Pt_t, Zt_t, Ot_t = t(Xt), t(Pt), t(Zt), t(Ot)
    Xh_t, Ph_t, Zh_t, Oh_t = t(Xh), t(Ph), t(Zh), t(Oh)
    ph_target = Ph_t.argmax(1)

    def holdout():
        net.eval()
        with torch.no_grad():
            logits, v, o = net.forward_own(Xh_t)
            acc = (logits.argmax(1) == ph_target).float().mean().item()
            vmse = F.mse_loss(v, Zh_t).item()
            omse = F.mse_loss(o, Oh_t).item()
            # ownership sign-accuracy on non-neutral (|target|==1) cells
            nz = Oh_t.abs() > 0.5
            oacc = ((o.sign() == Oh_t.sign()) & nz).float().sum().item() / max(1.0, nz.float().sum().item())
        net.train()
        return acc, vmse, omse, oacc

    m = Xt_t.shape[0]
    history = []
    best_acc = -1.0
    best_stats = None
    t0 = time.time()
    for ep in range(1, epochs + 1):
        net.train()
        pm = torch.randperm(m, device=device)
        last = 0.0
        for i in range(0, m, batch):
            idx = pm[i:i+batch]
            logits, v, o = net.forward_own(Xt_t[idx])
            pol = -(Pt_t[idx] * F.log_softmax(logits, 1)).sum(1).mean()
            val = F.mse_loss(v, Zt_t[idx])
            own = F.mse_loss(o, Ot_t[idx])
            loss = pol + val + lam * own
            opt.zero_grad(); loss.backward(); opt.step()
            last = float(loss.item())
        acc, vmse, omse, oacc = holdout()
        history.append({"epoch": ep, "train_loss": round(last, 4), "holdout_policy_acc": round(acc, 4),
                        "holdout_value_mse": round(vmse, 4), "holdout_own_mse": round(omse, 4),
                        "holdout_own_acc": round(oacc, 4)})
        if acc > best_acc:
            best_acc = acc
            best_stats = history[-1]
            torch.save(net.state_dict(), out)
        if ep % 5 == 0 or ep == 1:
            print(f"  ep{ep}: loss={last:.3f} pacc={acc:.4f} vmse={vmse:.4f} omse={omse:.4f} oacc={oacc:.4f}", flush=True)

    result = {"npz": npz, "n": int(n), "epochs": epochs, "batch": batch, "lr": lr,
              "lambda": lam, "channels": ch, "blocks": blk,
              "train_examples": int(len(Xt)), "holdout_examples": int(len(Xh)),
              "best_holdout_policy_acc": round(best_acc, 4), "best_epoch_stats": best_stats,
              "final": history[-1], "secs": round(time.time() - t0, 1), "history": history}
    res_out = out.replace(".pt", "") + "_train.json"
    with open(res_out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"best holdout policy acc = {best_acc:.4f} -> {out}  ({res_out})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
