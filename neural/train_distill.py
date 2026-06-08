"""Supervised distillation of classical MCTS into the net (autogo bootstrap idea).
Train A3GoNet on (state -> classical-MCTS visit policy, game outcome) targets.
Tracks HOLDOUT POLICY ACCURACY (autogo's non-self metric) as a fixed anchor.
Same 32x3 architecture as the PASS 3/4 self-play net, to isolate the effect of
distillation (not architecture).

    uv run python train_distill.py [npz] [epochs] [out.pt] [batch] [lr]
"""
from __future__ import annotations
import sys, json, time
import numpy as np
import torch
import torch.nn.functional as F
from net import A3GoNet


def main() -> int:
    npz = sys.argv[1] if len(sys.argv) > 1 else "distill_4cubed.npz"
    epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    out = sys.argv[3] if len(sys.argv) > 3 else "best_distill_4cubed.pt"
    batch = int(sys.argv[4]) if len(sys.argv) > 4 else 256
    lr = float(sys.argv[5]) if len(sys.argv) > 5 else 1e-3

    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = np.load(npz)
    X, P, Z = d["X"], d["P"], d["Z"]
    n = X.shape[2]
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    perm = rng.permutation(len(X))
    X, P, Z = X[perm], P[perm], Z[perm]
    nh = max(1, int(0.1 * len(X)))
    Xh, Ph, Zh = X[:nh], P[:nh], Z[:nh]
    Xt, Pt, Zt = X[nh:], P[nh:], Z[nh:]
    print(f"# distill {npz}: train {len(Xt)}, holdout {len(Xh)}, n={n}, {device}", flush=True)

    import os
    _ch=int(os.environ.get('A3GO_CH','32')); _bl=int(os.environ.get('A3GO_BLK','3'))
    net = A3GoNet(n, channels=_ch, blocks=_bl).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=1e-4)
    Xt_t = torch.from_numpy(Xt).to(device); Pt_t = torch.from_numpy(Pt).to(device); Zt_t = torch.from_numpy(Zt).to(device)
    Xh_t = torch.from_numpy(Xh).to(device); Ph_t = torch.from_numpy(Ph).to(device); Zh_t = torch.from_numpy(Zh).to(device)
    ph_target = Ph_t.argmax(1)

    def holdout():
        net.eval()
        with torch.no_grad():
            logits, v = net(Xh_t)
            acc = (logits.argmax(1) == ph_target).float().mean().item()
            vmse = F.mse_loss(v, Zh_t).item()
            ploss = -(Ph_t * F.log_softmax(logits, 1)).sum(1).mean().item()
        net.train()
        return acc, ploss, vmse

    m = Xt_t.shape[0]
    history = []
    best_acc = -1.0
    t0 = time.time()
    for ep in range(1, epochs + 1):
        net.train()
        pm = torch.randperm(m, device=device)
        last = 0.0
        for i in range(0, m, batch):
            idx = pm[i:i+batch]
            logits, v = net(Xt_t[idx])
            loss = -(Pt_t[idx] * F.log_softmax(logits, 1)).sum(1).mean() + F.mse_loss(v, Zt_t[idx])
            opt.zero_grad(); loss.backward(); opt.step()
            last = float(loss.item())
        acc, hploss, hvmse = holdout()
        history.append({"epoch": ep, "train_loss": round(last, 4), "holdout_policy_acc": round(acc, 4),
                        "holdout_policy_loss": round(hploss, 4), "holdout_value_mse": round(hvmse, 4)})
        if acc > best_acc:
            best_acc = acc
            torch.save(net.state_dict(), out)
        if ep % 5 == 0 or ep == 1:
            print(f"  ep{ep}: train_loss={last:.3f} holdout_acc={acc:.4f} hp_loss={hploss:.3f} hv_mse={hvmse:.3f}", flush=True)

    result = {"npz": npz, "n": int(n), "epochs": epochs, "batch": batch, "lr": lr,
              "train_examples": int(len(Xt)), "holdout_examples": int(len(Xh)),
              "best_holdout_policy_acc": round(best_acc, 4),
              "final": history[-1], "secs": round(time.time() - t0, 1), "history": history}
    with open("experiments_distill_4.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"best holdout policy acc = {best_acc:.4f} -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
