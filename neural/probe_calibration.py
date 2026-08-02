"""PROBE-2 — value-head calibration vs the true Tromp-Taylor outcome.

The distill npz stores, per position, the rich input stack X and the realized
game outcome Z in {-1,0,+1} (side-to-move perspective). We forward the trained
value head on a held-out split and ask: when the net predicts value v, does the
game actually end at mean outcome ~v? Build a reliability diagram, expected
calibration error (ECE), and fit a single temperature T (v' = tanh(atanh(v)/T))
that minimizes calibration error — a free, no-retrain inference fix if it helps.

Runs per config (base 3-plane vs libs) so we can see whether the richer input
changes calibration, not just accuracy. Forward-pass only, seconds.

    uv run python probe_calibration.py [npz] [out.json]
"""
from __future__ import annotations
import os, sys, json, time
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
import torch
torch.set_num_threads(1)

from net_arch3 import A3GoNetIn
from input_planes import n_planes, slice_stack

CFGS = ["base", "libs"]
SEEDS = [0, 1, 2]
NBINS = 10


def ece_and_diagram(v, z, nbins=NBINS):
    """v in [-1,1] predicted, z in {-1,0,1} realized. Map to [0,1] win-prob space
    (p=(v+1)/2, y=(z+1)/2 with draws=0.5) and bin. Returns (ece, bins)."""
    p = (v + 1) / 2
    y = (z + 1) / 2
    edges = np.linspace(0, 1, nbins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, nbins - 1)
    bins = []
    ece = 0.0
    N = len(p)
    for b in range(nbins):
        m = idx == b
        cnt = int(m.sum())
        if cnt == 0:
            bins.append({"bin": b, "count": 0, "mean_pred": None, "mean_real": None})
            continue
        mp = float(p[m].mean()); mr = float(y[m].mean())
        bins.append({"bin": b, "count": cnt, "mean_pred": round(mp, 4), "mean_real": round(mr, 4)})
        ece += cnt / N * abs(mp - mr)
    return ece, bins


def fit_temperature(v, z):
    """Find scalar T>0 minimizing MSE between tanh(atanh(v)/T) and z. Grid+refine."""
    v = np.clip(v, -0.999, 0.999)
    a = np.arctanh(v)
    best_T, best_mse = 1.0, 1e9
    for T in np.concatenate([np.linspace(0.3, 3.0, 28), np.linspace(0.5, 1.5, 41)]):
        vp = np.tanh(a / T)
        mse = float(np.mean((vp - z) ** 2))
        if mse < best_mse:
            best_mse, best_T = mse, float(T)
    return best_T, best_mse


def main():
    npz = sys.argv[1] if len(sys.argv) > 1 else "distill_arch3_5cubed.npz"
    out = sys.argv[2] if len(sys.argv) > 2 else "probe2_calibration.json"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    t0 = time.time()
    d = np.load(npz)
    Xf, Z = d["X"], d["Z"].astype(np.float32)
    n = Xf.shape[2]
    rng = np.random.default_rng(0)
    perm = rng.permutation(len(Xf))
    hold = perm[: max(1, int(0.2 * len(Xf)))]   # held-out split
    Zh = Z[hold]
    print(f"# PROBE-2 calibration npz={npz} n={n}^3 holdout={len(hold)} device={device}", flush=True)

    report = {"experiment": "PROBE-2 value-head calibration vs TT outcome (5^3)",
              "npz": npz, "n": int(n), "holdout": int(len(hold)), "nbins": NBINS, "by_cfg": {}}
    for cfg in CFGS:
        Xc = torch.from_numpy(np.ascontiguousarray(slice_stack(Xf, cfg)[hold])).to(device)
        vs = []
        for seed in SEEDS:
            net = A3GoNetIn(n, in_planes=n_planes(cfg), channels=64, blocks=6)
            net.load_state_dict(torch.load(f"best_arch3_{cfg}_s{seed}.pt", map_location=device))
            net.to(device).eval()
            with torch.no_grad():
                v = net(Xc)[1].float().cpu().numpy()
            vs.append(v)
        v = np.mean(vs, axis=0)  # ensemble-mean value (per-seed avg)
        mse = float(np.mean((v - Zh) ** 2))
        ece, bins = ece_and_diagram(v, Zh)
        T, mse_T = fit_temperature(v, Zh)
        vT = np.tanh(np.arctanh(np.clip(v, -0.999, 0.999)) / T)
        eceT, _ = ece_and_diagram(vT, Zh)
        report["by_cfg"][cfg] = {
            "value_mse": round(mse, 4), "ece": round(ece, 4),
            "best_temperature": round(T, 3), "value_mse_after_temp": round(mse_T, 4),
            "ece_after_temp": round(eceT, 4),
            "mean_abs_pred": round(float(np.mean(np.abs(v))), 4),
            "reliability_bins": bins,
        }
        print(f"  cfg={cfg:5s}: MSE={mse:.4f} ECE={ece:.4f} -> T*={T:.3f} ECE_T={eceT:.4f} "
              f"(over/under-conf: {'over' if T>1 else 'under'})", flush=True)

    report["secs"] = round(time.time() - t0, 1)
    json.dump(report, open(out, "w"), indent=2)
    print(f"wrote {out} ({report['secs']}s)", flush=True)


if __name__ == "__main__":
    main()
