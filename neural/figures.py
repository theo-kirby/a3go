"""TOOL-1 (figures) — turn the campaign's result JSONs into committed PNG figures.

Each function loads one result artifact and writes a clean plot. Run with no args
to regenerate all figures that have inputs present.

    uv run python figures.py            # all available
    uv run python figures.py ladder     # one
"""
from __future__ import annotations
import sys, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = "figures"
os.makedirs(OUT, exist_ok=True)


def _save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p, flush=True)
    return p


def fig_ladder(path="ladder_4cubed.json"):
    if not os.path.exists(path):
        return
    d = json.load(open(path))
    rk = d["ranking"]
    labels = [r["agent"] for r in rk][::-1]
    elo = [r["elo"] for r in rk][::-1]
    lo = [r["elo"] - r["ci95"][0] for r in rk][::-1]
    hi = [r["ci95"][1] - r["elo"] for r in rk][::-1]
    colors = ["#d62728" if "cls" in l else "#1f77b4" if "net" in l else "#7f7f7f" for l in labels]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(labels, elo, xerr=[lo, hi], color=colors, capsize=4)
    ax.set_xlabel("Elo (anchor: random = 0)")
    ax.set_title(f"PROOF-1 — anchored rating ladder, {d['n']}³ (G={d['games_per_pair']}/pair)")
    ax.grid(axis="x", alpha=0.3)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#d62728", label="classical"),
                       Patch(color="#1f77b4", label="net"),
                       Patch(color="#7f7f7f", label="random")], loc="lower right", fontsize=8)
    return _save(fig, "proof1_elo_ladder_4cubed.png")


def fig_scaling(path="test_time_scaling.json"):
    if not os.path.exists(path):
        return
    d = json.load(open(path))
    fig, ax = plt.subplots(figsize=(7, 4.5))
    marks = {4: "o", 5: "s", 7: "^"}
    for bd in d["boards"]:
        xs = [c["sims"] for c in bd["curve"]]
        ys = [c["winrate"] for c in bd["curve"]]
        lo = [c["winrate"] - c["ci95"][0] for c in bd["curve"]]
        hi = [c["ci95"][1] - c["winrate"] for c in bd["curve"]]
        ax.errorbar(xs, ys, yerr=[lo, hi], marker=marks.get(bd["n"], "o"), capsize=3,
                    label=f"{bd['n']}³ (base@{bd['baseline_sims']})")
    ax.axhline(0.5, color="k", ls="--", alpha=0.5)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("search sims (log)")
    ax.set_ylabel("win-rate vs fixed low-sim baseline")
    ax.set_title("PROOF-2 — test-time search scaling amplifies with board size")
    ax.legend(); ax.grid(alpha=0.3)
    return _save(fig, "proof2_test_time_scaling.png")


def fig_engine():
    # INFRA-2 before/after (from bench_infra1.json final + recorded baseline)
    before = {"4³": 10148, "5³": 6447, "7³": 2747}
    after = {"4³": 13556, "5³": 12398, "7³": 9688}
    boards = list(before.keys())
    x = np.arange(len(boards)); w = 0.38
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.bar(x - w/2, [before[b] for b in boards], w, label="before (pure-Python legal_moves)", color="#9ecae1")
    ax.bar(x + w/2, [after[b] for b in boards], w, label="after (vectorized + Zobrist)", color="#08519c")
    for i, b in enumerate(boards):
        ax.text(i + w/2, after[b] + 150, f"{after[b]/before[b]:.1f}×", ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(boards)
    ax.set_ylabel("MCTS sims / s (GPU-batched)")
    ax.set_title("INFRA-2 — engine speedup (legal_moves vectorize + Zobrist superko)")
    ax.legend(); ax.grid(axis="y", alpha=0.3)
    return _save(fig, "infra2_engine_speedup.png")


def fig_gumbel(path="ab_gumbel_4cubed.json"):
    if not os.path.exists(path):
        return
    d = json.load(open(path))
    labels = [r["matchup"].replace("_vs_", "\nvs ") for r in d["results"]]
    wr = [r["gumbel_winrate"] for r in d["results"]]
    lo = [r["gumbel_winrate"] - r["ci95"][0] for r in d["results"]]
    hi = [r["ci95"][1] - r["gumbel_winrate"] for r in d["results"]]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.bar(range(len(labels)), wr, yerr=[lo, hi], capsize=4,
           color=["#2ca02c" if w >= 0.5 else "#d62728" for w in wr])
    ax.axhline(0.5, color="k", ls="--", alpha=0.6)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Gumbel win-rate"); ax.set_ylim(0, 1)
    ax.set_title(f"ALGO-1 — Gumbel vs PUCT, {d['n']}³ (no clear win on small board)")
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, "algo1_gumbel_ab_4cubed.png")


def fig_az(path="az_selfplay_4cubed.json"):
    if not os.path.exists(path):
        return
    d = json.load(open(path))
    h = [e for e in d["history"] if "cand_wr_vs_classical" in e]
    if not h:
        return
    its = [e["iter"] for e in h]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(its, [e["cand_wr_vs_classical"] for e in h], "o-", label="candidate vs classical")
    ax.plot(its, [e["best_wr_vs_classical"] for e in h], "s--", label="best (anchor) vs classical")
    ax.plot(its, [e["cand_vs_best"] for e in h], "^:", label="cand vs best (net-vs-net)")
    ax.axhline(0.5, color="k", ls="--", alpha=0.4)
    ax.set_xlabel("self-play iteration"); ax.set_ylabel("win-rate")
    ax.set_title(f"INFRA-3 — AZ self-play vs the classical teacher ({d['n']}³)")
    ax.legend(); ax.grid(alpha=0.3)
    return _save(fig, "infra3_az_selfplay_4cubed.png")


ALL = {"ladder": fig_ladder, "scaling": fig_scaling, "engine": fig_engine,
       "gumbel": fig_gumbel, "az": fig_az}

if __name__ == "__main__":
    which = sys.argv[1:] or list(ALL)
    for k in which:
        if k in ALL:
            ALL[k]()
