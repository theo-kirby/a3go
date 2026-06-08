import sys, json, math, os
import multiprocessing as mp
from net_vs_classical_mp import _play_one, wilson
ckpt="best_distill5strong_5cubed.pt"; n=5; games=24; cap=50
configs=[(128,48),(256,48)]
res=[]
for ns,cp in configs:
    args=[(g,ckpt,n,ns,cp,cap) for g in range(games)]
    with mp.Pool(min(14,os.cpu_count())) as pool: r=pool.map(_play_one,args)
    w=d=0
    for nb,winner,diff in r:
        if winner=="draw": continue
        d+=1; w+= (winner=="black")==nb
    p,lo,hi=wilson(w,d)
    row={"net_sims":ns,"cls_playouts":cp,"net_winrate":p,"ci95":[lo,hi],"decided":d,"net_wins":w,"beats":lo>0.5}
    res.append(row); print(json.dumps(row),flush=True)
    json.dump({"results":res},open("experiments_5cube_scaling.json","w"),indent=2)
print("DONE",flush=True)
