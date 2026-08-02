"""ARCH-3 finalize: pool the per-seed net-vs-classical JSONs into a single A/B
summary (mirrors arch2_ab_summary.json), comparing each input config against the
3-plane `base` baseline. Also gathers holdout policy/value metrics from the
*_train.json files. Idempotent / re-runnable; consumes whatever configs+seeds are
present so it works for the headline (base, all) and after the ablation evals.

    uv run python arch3_finalize.py [out.json] [seed0 seed1 ...]
"""
from __future__ import annotations
import glob, json, math, os, sys


def wilson(wins, total, z=1.96):
    if total == 0:
        return (0.0, 0.0, 0.0)
    p = wins / total
    d = 1 + z * z / total
    c = (p + z * z / (2 * total)) / d
    h = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d
    return (round(p, 4), round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


def pool_cfg(cfg, seeds):
    wins = decided = 0
    per_seed = []
    for s in seeds:
        path = f"experiments_arch3_{cfg}_s{s}.json"
        if not os.path.exists(path):
            continue
        d = json.load(open(path))
        w, dec = d["net_wins"], d["decided"]
        wins += w; decided += dec
        per_seed.append({"seed": s, "wr": d["net_winrate"], "ci": d["winrate_ci95"],
                         "wins": w, "decided": dec, "eval_secs": d.get("eval_secs"),
                         "games_per_sec": d.get("games_per_sec")})
    if not per_seed:
        return None
    p, lo, hi = wilson(wins, decided)
    gps = [x["games_per_sec"] for x in per_seed if x.get("games_per_sec")]
    return {"cfg": cfg, "wins": wins, "decided": decided, "winrate": p, "ci95": [lo, hi],
            "beats_classical": lo > 0.5, "per_seed": per_seed,
            "mean_games_per_sec": round(sum(gps) / len(gps), 4) if gps else None}


def holdout_cfg(cfg, seeds):
    rows = []
    for s in seeds:
        path = f"best_arch3_{cfg}_s{s}_train.json"
        if not os.path.exists(path):
            continue
        d = json.load(open(path))
        rows.append({"seed": s, "best_holdout_top1": d.get("best_holdout_top1"),
                     "final_value_mse": d.get("final", {}).get("holdout_value_mse"),
                     "best_top3": d.get("best_epoch_stats", {}).get("holdout_top3"),
                     "in_planes": d.get("in_planes"), "params": d.get("params")})
    if not rows:
        return None
    def mean(k):
        vs = [r[k] for r in rows if r.get(k) is not None]
        return round(sum(vs) / len(vs), 4) if vs else None
    return {"per_seed": rows, "mean_best_top1": mean("best_holdout_top1"),
            "mean_final_value_mse": mean("final_value_mse"),
            "in_planes": rows[0].get("in_planes"), "params": rows[0].get("params")}


def ci_overlap(a, b):
    """True iff intervals [a0,a1] and [b0,b1] overlap."""
    return a[0] <= b[1] and b[0] <= a[1]


def main() -> int:
    out = sys.argv[1] if len(sys.argv) > 1 else "arch3_ab_summary.json"
    seeds = [int(x) for x in sys.argv[2:]] or [0, 1, 2]
    # discover which configs have any eval present
    cfgs = []
    for path in sorted(glob.glob("experiments_arch3_*_s*.json")):
        base = os.path.basename(path)[len("experiments_arch3_"):]
        cfg = base.rsplit("_s", 1)[0]
        if cfg not in cfgs:
            cfgs.append(cfg)
    # ensure base/all ordering first
    order = [c for c in ["base", "all", "koban", "libs", "capture", "history"] if c in cfgs]
    order += [c for c in cfgs if c not in order]

    strength = {c: pool_cfg(c, seeds) for c in order}
    strength = {c: v for c, v in strength.items() if v}
    holdout = {c: holdout_cfg(c, seeds) for c in order}
    holdout = {c: v for c, v in holdout.items() if v}

    summary = {
        "experiment": "ARCH-3 richer input planes vs 3-plane baseline "
                      "(5^3, net@512 vs cls@48, n=128/seed x3 pooled, identical data+soft-target+trunk)",
        "protocol": {"board": 5, "net_sims": 512, "cls_playouts": 48, "cls_cap": 50,
                     "games_per_seed": 128, "seeds": seeds,
                     "channel_layout": "0=B,1=W,2=stm,3=koban,4=lib1,5=lib2,6=lib3+,7=capture,8=last,9=2ndlast"},
        "strength": strength,
        "holdout": holdout,
    }

    base = strength.get("base")
    if base:
        comps = {}
        for c, v in strength.items():
            if c == "base":
                continue
            delta = round(v["winrate"] - base["winrate"], 4)
            overlap = ci_overlap(v["ci95"], base["ci95"])
            comps[c] = {"delta_vs_base": delta, "ci_overlap_with_base": overlap,
                        "decisive_vs_base": (not overlap) and delta > 0,
                        "beats_classical": v["beats_classical"]}
        summary["vs_base"] = comps
        summary["any_decisive_vs_base"] = any(x["decisive_vs_base"] for x in comps.values())
        summary["any_beats_classical"] = any(v["beats_classical"] for v in strength.values())

    json.dump(summary, open(out, "w"), indent=2)
    print(json.dumps(summary, indent=2))
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
