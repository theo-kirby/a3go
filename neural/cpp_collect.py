"""Parallel C++ classical self-play data-gen: launch K engine processes, combine
their .bin outputs into an .npz compatible with train_distill.py."""
import sys, os, subprocess, time, numpy as np
from cpp_loader import load_cpp_bin

def main():
    n=int(sys.argv[1]); games=int(sys.argv[2]); playouts=int(sys.argv[3])
    cap=int(sys.argv[4]); out=sys.argv[5]
    workers=min(14, os.cpu_count() or 8)
    per=[games//workers]*workers
    for i in range(games-sum(per)): per[i]+=1
    t0=time.time(); procs=[]; bins=[]
    for w in range(workers):
        if per[w]==0: continue
        bf=f"/tmp/cppsp_{n}_{w}.bin"; bins.append(bf)
        procs.append(subprocess.Popen(["./cpp/engine","selfplay",str(n),str(per[w]),str(playouts),str(cap),str(1000+w),bf],
                                      stderr=subprocess.DEVNULL))
    for p in procs: p.wait()
    Xs=[];Ps=[];Zs=[]
    for bf in bins:
        if os.path.exists(bf):
            X,P,Z=load_cpp_bin(bf); Xs.append(X);Ps.append(P);Zs.append(Z); os.remove(bf)
    X=np.concatenate(Xs);P=np.concatenate(Ps);Z=np.concatenate(Zs)
    np.savez_compressed(out,X=X,P=P,Z=Z)
    dt=time.time()-t0
    print(f"C++ collect n={n} games={games} playouts={playouts}: {X.shape[0]} examples in {dt:.1f}s ({dt/games:.2f}s/game wall, {workers} workers) -> {out}")

if __name__=="__main__": main()
