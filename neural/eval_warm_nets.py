import torch, json
from net import A3GoNet
from batched_az import BatchedMCTS, match_vs_random_batched, match_net_vs_net_batched
dev="cuda"; n=4
def load(p):
    m=A3GoNet(n).to(dev); m.load_state_dict(torch.load(p,map_location=dev)); m.eval(); return m
warm=load("best_warm_4cubed.pt"); distill=load("best_distill_4cubed.pt"); sp=load("best_selfplay_4cubed.pt")
mw=BatchedMCTS(warm,dev,sims=48,seed=0); mdi=BatchedMCTS(distill,dev,sims=48,seed=0); ms=BatchedMCTS(sp,dev,sims=48,seed=0)
out={"warm_vs_random":round(match_vs_random_batched(mw,n,200,seed=4242),3),
     "warm_vs_distilled":round(match_net_vs_net_batched(mw,mdi,n,200,temp=0.3,seed=77),3),
     "warm_vs_selfplay":round(match_net_vs_net_batched(mw,ms,n,200,temp=0.3,seed=88),3)}
print(json.dumps(out)); json.dump(out,open("experiments_warm_vs_nets.json","w"))
