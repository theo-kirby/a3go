"""Test-time sims scaling: distilled net at varying sims vs classical at varying
playouts. Exploits the cost asymmetry (neural batched eval ~free vs expensive
classical rollouts). Win-rate + Wilson 95% CI per config, parallel over cores."""
import sys, json, math, os, time
import multiprocessing as mp
from net_vs_classical_mp import _play_one, wilson

def main():
    ckpt = sys.argv[1] if len(sys.argv) > 1 else "best_distill_4cubed.pt"
    n = 4
    games = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    cap = 64
    configs = [(48,48),(128,48),(256,48),(128,128),(256,128)]
    workers = min(14, os.cpu_count() or 8)
    results = []
    for net_sims, cls_pl in configs:
        t0 = time.time()
        args = [(g, ckpt, n, net_sims, cls_pl, cap) for g in range(games)]
        with mp.Pool(workers) as pool:
            res = pool.map(_play_one, args)
        w = d = 0
        for nb, winner, diff in res:
            if winner == "draw": continue
            d += 1
            if (winner=="black")==nb: w += 1
        p, lo, hi = wilson(w, d)
        row = {"net_sims":net_sims,"cls_playouts":cls_pl,"net_winrate":p,
               "ci95":[lo,hi],"decided":d,"net_wins":w,"beats":lo>0.5,"secs":round(time.time()-t0,1)}
        results.append(row)
        print(json.dumps(row), flush=True)
        json.dump({"ckpt":ckpt,"games":games,"results":results}, open("experiments_scaling.json","w"), indent=2)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
