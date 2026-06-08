"""Concatenate distillation datasets into one (combine teachers / add variety)."""
import sys, numpy as np
outs = sys.argv[1]; ins = sys.argv[2:]
X=[];P=[];Z=[]
for f in ins:
    d=np.load(f); X.append(d["X"]);P.append(d["P"]);Z.append(d["Z"])
    print(f"{f}: {d['X'].shape[0]} examples")
X=np.concatenate(X);P=np.concatenate(P);Z=np.concatenate(Z)
np.savez_compressed(outs, X=X,P=P,Z=Z)
print(f"saved {outs}: {X.shape[0]} total examples")
