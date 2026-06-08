import torch, json
from net import A3GoNet
from batched_az import BatchedMCTS, match_vs_random_batched, match_net_vs_net_batched
dev="cuda"; n=4
distill=A3GoNet(n).to(dev); distill.load_state_dict(torch.load("best_distill_4cubed.pt",map_location=dev)); distill.eval()
sp=A3GoNet(n).to(dev); sp.load_state_dict(torch.load("best_batched_4cubed.pt",map_location=dev)); sp.eval()
md=BatchedMCTS(distill,dev,sims=48,seed=0); ms=BatchedMCTS(sp,dev,sims=48,seed=0)
out={"distilled_vs_random":round(match_vs_random_batched(md,n,200,seed=4242),3),
     "distilled_vs_selfplaynet":round(match_net_vs_net_batched(md,ms,n,200,temp=0.3,seed=77),3)}
print(json.dumps(out)); json.dump(out,open("experiments_distill_vs_nets.json","w"))
