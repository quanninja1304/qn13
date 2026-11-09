import sys,os,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
rng=np.random.default_rng(31337)
se=lambda B:math.sqrt(.05*.95/B)
print('=== C2: realistic full-order Q on p=5,6,8; R=I and sparse DAG')
def dagR(p,seed):
    r=np.random.default_rng(seed);B=np.zeros((p,p))
    for i in range(p):
        for j in range(i):
            if r.random()<.3:B[i,j]=r.uniform(.3,.7)*r.choice([-1,1])
    Inv=np.linalg.inv(np.eye(p)-B);C=Inv@Inv.T;d=np.sqrt(np.diag(C));return C/np.outer(d,d)
for p,c,B,ns in ((5,2,3000,(200,500,1000,5000)),(6,2,1500,(200,500,1000,5000)),(8,2,120,(200,1000))):
    qs=queries(p,c);K=len(qs)
    for rname,R in (('I',np.eye(p)),('sparse',dagR(p,p))):
        zeta=zsig(R[None],qs,1000,sig=False)[2][0]
        for n in ns:
            lam=n**(-1/3);nk=np.array([n-len(q[2])-3 for q in qs])
            zt=np.sqrt(nk)*np.arctanh(zeta)
            Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,qs,n)
            sz,_,_=ridge_size(Z,zt,Sh,lam,rng,table=8000)
            tr,rh=trunc_size(Z,zt,Sh,n**(-1/4))
            print(f'p={p} c={c} K={K} R={rname} n={n}: ridge={sz:.3f} trunc={tr:.3f} (rhat {rh:.1f}, d={p*(p-1)//2}) SE={se(B):.3f}',flush=True)
