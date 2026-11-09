import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
rng=np.random.default_rng(808)
Q2=[(0,1,()),(0,1,(2,))]
print('=== V0 on a=b=c/sqrt n, rho_XY=c^2/n, real data')
for n in (1000,5000):
  for c in (1,1.5,2):
    a=c/n**.5;R=np.array([[1,c*c/n,a],[c*c/n,1,a],[a,a,1.]]);B=30000
    Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,Q2,n);rho=zsig(R[None],Q2,sig=False)[2][0]
    nk=np.array([n-3,n-4.]);zt=np.sqrt(nk)*np.arctanh(rho);E=Z-zt
    w,V=np.linalg.eigh(Sh);P=np.einsum('bji,bj->bi',V,E)**2
    v0=(P/np.clip(w,1e-14,None)).sum(1)
    tr,_=trunc_size(Z,zt,Sh,n**-.25)
    print(f'n={n} c={c}: V0 rate={np.mean(v0>5.991):.4f} V1={tr:.4f} SE={(0.05*.95/B)**.5:.4f}',flush=True)
print('=== lam choices K=70,165')
for p,c,B,ns in ((5,2,3000,(200,500,1000)),(6,2,1500,(200,500,1000))):
    qs=queries(p,c);R=np.eye(p);K=len(qs)
    for n in ns:
        Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,qs,n);zt=np.zeros(K)
        row=[]
        for nm,l in (('n^-1/3',n**(-1/3)),('n^-1/4',n**(-1/4)),('0.5',.5),('2',2.),('10',10.)):
            sz,_,_=ridge_size(Z,zt,Sh,l,rng,table=8000);row.append(f'{nm}:{sz:.3f}')
        print(f'p={p} K={K} n={n}',' '.join(row),flush=True)
print('=== lam=n^-3/4 K=6, K=24 generic')
Rg3=np.array([[1,.3,.5],[.3,1,.4],[.5,.4,1.]]);Rg4=np.array([[1,.35,.25,.3],[.35,1,.2,.4],[.25,.2,1,.45],[.3,.4,.45,1.]])
for qs,R,B in ((queries(3,1),Rg3,4000),(queries(4,2),Rg4,2000)):
    nkf=lambda n:np.array([n-len(q[2])-3 for q in qs],float)
    th=np.arctanh(zsig(R[None],qs,sig=False)[2][0])
    for n in (1000,5000,20000,100000):
        Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,qs,n);zt=np.sqrt(nkf(n))*th
        a,_,_=ridge_size(Z,zt,Sh,n**-.75,rng,table=8000);b,_,_=ridge_size(Z,zt,Sh,n**(-1/3),rng,table=8000)
        print(f'K={len(qs)} n={n}: lam=n^-3/4 (nlam={n**.25:.1f}) size={a:.3f}; lam=n^-1/3 size={b:.3f} SE={(0.0475/B)**.5:.3f}',flush=True)
