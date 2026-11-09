import numpy as np, itertools, math
from scipy import stats
def queries(p,c,pairs=None):
    out=[]
    for i,j in (pairs or itertools.combinations(range(p),2)):
        rest=[v for v in range(p) if v not in (i,j)]
        for s in range(c+1):
            for S in itertools.combinations(rest,s): out.append((i,j,S))
    return out
def coefs(C,qs):
    """C: (B,p,p). returns Ax,Ay (B,K,p): unit-variance residual coefficient vectors"""
    B,p=C.shape[0],C.shape[1];K=len(qs)
    Ax=np.zeros((B,K,p));Ay=np.zeros((B,K,p))
    bys={}
    for k,(x,y,S) in enumerate(qs): bys.setdefault(tuple(S),[]).append(k)
    for S,ks in bys.items():
        S_=list(S)
        for k in ks:
            x,y,_=qs[k]
            Ax[:,k,x]=1;Ay[:,k,y]=1
        if S_:
            inv=np.linalg.inv(C[:,S_][:,:,S_])
            for k in ks:
                x,y,_=qs[k]
                Ax[:,k,S_]=-(inv@C[:,S_,x][...,None])[...,0]
                Ay[:,k,S_]=-(inv@C[:,S_,y][...,None])[...,0]
    vx=np.einsum('bki,bij,bkj->bk',Ax,C,Ax);vy=np.einsum('bki,bij,bkj->bk',Ay,C,Ay)
    return Ax/np.sqrt(vx)[...,None],Ay/np.sqrt(vy)[...,None]
def zsig(C,qs,n=None,sig=True):
    Ax,Ay=coefs(C,qs)
    CAx=Ax@C;CAy=Ay@C
    rho=np.einsum('bki,bki->bk',CAx,Ay)
    z=None
    if n is not None:
        nk=np.array([n-len(q[2])-3 for q in qs],float)
        z=np.sqrt(nk)*np.arctanh(rho)
    if not sig: return z,None,rho
    a=CAx@np.swapaxes(Ax,1,2); b=CAx@np.swapaxes(Ay,1,2); c=CAy@np.swapaxes(Ax,1,2); d=CAy@np.swapaxes(Ay,1,2)
    rk=rho[:,:,None];rl=rho[:,None,:]
    num=(a*d+b*c)-rl*(a*c+b*d)-rk*(a*b+c*d)+.5*rk*rl*(a*a+b*b+c*c+d*d)
    S=num/((1-rk*rk)*(1-rl*rl))
    return z,.5*(S+np.swapaxes(S,1,2)),rho
def rawcov(R,n,B,rng):
    """sample covariance from raw Gaussian rows (no Bartlett)"""
    L=np.linalg.cholesky(R);p=R.shape[0];out=np.zeros((B,p,p))
    for s in range(0,B,200):
        e=min(B,s+200)
        X=rng.standard_normal((e-s,n,p))@L.T
        X-=X.mean(1,keepdims=True)
        out[s:e]=np.swapaxes(X,1,2)@X/(n-1)
    return out
def wish(R,n,B,rng):
    """Wishart by chi2 via Gaussian Bartlett - own implementation; for large n"""
    p=R.shape[0];L=np.linalg.cholesky(R);nu=n-1
    A=np.zeros((B,p,p))
    for i in range(p):
        A[:,i,i]=np.sqrt(rng.chisquare(nu-i,size=B))
        A[:,i,:i]=rng.standard_normal((B,i))
    M=L@A
    return M@np.swapaxes(M,1,2)/nu
def ridge_size(Z,zeta,Sh,lam,rng,table=20000):
    """returns P(W>c_hat) with weighted chi2 from fresh table per call"""
    E=Z-zeta
    w,V=np.linalg.eigh(Sh);w=np.clip(w,0,None)
    P=np.einsum('bji,bj->bi',V,E)**2
    stat=(P/(w+lam)).sum(1);wts=w/(w+lam)
    G=rng.standard_normal((table,w.shape[1]))**2
    rej=np.empty(len(stat))
    for b in range(len(stat)):
        rej[b]=np.mean(G@wts[b]>stat[b])<.05
    return rej.mean(),stat,wts
def trunc_size(Z,zeta,Sh,tau):
    E=Z-zeta;w,V=np.linalg.eigh(Sh);P=np.einsum('bji,bj->bi',V,E)**2
    keep=w>tau;st=(P*keep/np.where(keep,w,1)).sum(1);r=keep.sum(1)
    return np.mean(st>stats.chi2.ppf(.95,np.maximum(r,1))),r.mean()
def oracle_stat(Z,zeta,S):
    w,V=np.linalg.eigh(S);k=w>1e-10
    Pinv=(V[:,k]/w[k])@V[:,k].T;E=Z-zeta
    return np.einsum('bi,ij,bj->b',E,Pinv,E),int(k.sum())
