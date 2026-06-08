"""Q8/Q5 — positional value via the CHAMPION 4^3 net's opening policy. On an empty
4^3 board, the net's policy prior over the 64 points reveals where a strong agent
wants to play. Classify points by degree (3D connectivity): corner(deg3),
edge(deg4), face(deg5), interior(deg6)."""
import json, numpy as np, torch
from a3go_engine import Board, BLACK, WHITE
from net import A3GoNet
import torch.nn.functional as F

n=4
dev="cuda"
net=A3GoNet(n,channels=64,blocks=6).to(dev)
net.load_state_dict(torch.load("best_distill_big_4cubed.pt",map_location=dev)); net.eval()

def degree(x,y,z):
    d=0
    for dx,dy,dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
        if 0<=x+dx<n and 0<=y+dy<n and 0<=z+dz<n: d+=1
    return d

b=Board(n)
planes=np.zeros((3,n,n,n),dtype=np.float32); planes[2]=1.0  # empty, black to move
x=torch.from_numpy(planes).unsqueeze(0).to(dev)
with torch.no_grad():
    logits,v=net(x)
pi=F.softmax(logits[0],0).cpu().numpy()  # 65 actions

cls={3:"corner",4:"edge",5:"face",6:"interior"}
agg={c:[] for c in cls.values()}
for xx in range(n):
    for yy in range(n):
        for zz in range(n):
            a=xx*n*n+yy*n+zz
            agg[cls[degree(xx,yy,zz)]].append(pi[a])
out={"board":"4^3 empty, champion 64x6 net opening policy","value_empty":round(float(v.item()),4),"pass_prob":round(float(pi[n*n*n]),5),"classes":{}}
for c,vals in agg.items():
    vals=np.array(vals)
    out["classes"][c]={"count":len(vals),"total_policy_mass":round(float(vals.sum()),4),"mean_per_point":round(float(vals.mean()),5),"per_point_x_count":round(float(vals.mean()*len(vals)),4)}
# rank
order=sorted(out["classes"].items(), key=lambda kv: -kv[1]["mean_per_point"])
out["preference_by_mean_per_point"]=[c for c,_ in order]
print(json.dumps(out,indent=2))
json.dump(out,open("experiments_q8_positional.json","w"),indent=2)
