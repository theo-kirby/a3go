import numpy as np, sys
def load_cpp_bin(path):
    with open(path,"rb") as f:
        count,n=np.fromfile(f,dtype=np.int32,count=2)
        X=np.fromfile(f,dtype=np.float32,count=count*3*n*n*n).reshape(count,3,n,n,n)
        P=np.fromfile(f,dtype=np.float32,count=count*(n*n*n+1)).reshape(count,n*n*n+1)
        Z=np.fromfile(f,dtype=np.float32,count=count)
    return X,P,Z
if __name__=="__main__":
    X,P,Z=load_cpp_bin(sys.argv[1])
    print("X",X.shape,"P",P.shape,"Z",Z.shape)
    print("planes: black/white/stm sums ex0:",X[0,0].sum(),X[0,1].sum(),X[0,2].sum())
    print("policy sums ~1:",np.allclose(P.sum(1),1.0,atol=1e-3),"min/max",P.min(),P.max())
    print("Z values:",np.unique(Z))
