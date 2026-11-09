import sys,os,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
rng=np.random.default_rng(31337)
se=lambda B:math.sqrt(.05*.95/B)
print('=== C1: K=2^m conditioning subsets of m independent Z, R=I (Sigma=11^T rank 1) ; predicted null term K m/(4 n lam)')
for m,B in ((3,4000),(5,4000),(6,3000),(8,1500)):
    qs=[(0,1,S) for s in range(m+1) for S in itertools.combinations(range(2,2+m),s)]
    K=len(qs);p=2+m;R=np.eye(p)
    for n in (100,200,500,1000,5000,20000):
        if n<=p+m+3: continue
        lam=n**(-1/3)
        Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,qs,n)
        zeta=np.zeros(K)
        sz,stat,wts=ridge_size(Z,zeta,Sh,lam,rng)
        tr,rh=trunc_size(Z,zeta,Sh,n**(-1/4))
        print(f'm={m} K={K} n={n}: lam={lam:.3f} nlam={n*lam:.0f} pred null={K*m/(4*n*lam):.2f} | ridge size={sz:.3f} trunc={tr:.3f} (rhat {rh:.1f}) SE={se(B):.3f}',flush=True)
print('=== C2: realistic full-order Q on p=5,6,8; R=I and sparse DAG')
def dagR(p,seed):
    r=np.random.default_rng(seed);B=np.zeros((p,p))
    for i in range(p):
        for j in range(i):
            if r.random()<.3:B[i,j]=r.uniform(.3,.7)*r.choice([-1,1])
    Inv=np.linalg.inv(np.eye(p)-B);C=Inv@Inv.T;d=np.sqrt(np.diag(C));return C/np.outer(d,d)
for p,c,B,ns in ((5,2,3000,(200,500,1000,5000)),(6,2,1500,(200,500,1000,5000)),(8,2,300,(200,500,1000,5000))):
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
print('=== C3: lambda below sqrt(n) rule: lam=n^-3/4 (sqrt(n)lam->0, n lam->inf), and lam=n^-1/2 boundary, Q2 and K=6')
Q2=[(0,1,()),(0,1,(2,))];Q6=queries(3,1)
for ex,name in ((.75,'n^-3/4'),(.5,'n^-1/2'),(.9,'n^-0.9')):
    for n in (1000,5000,20000,100000):
        lam=n**(-ex);row=[]
        for an,a in (('0',0.),('1/sqrt n',n**-.5),('sqrt(2lam)',math.sqrt(2*lam)),('n^-1/4',n**-.25)):
            R=np.array([[1,0,a],[0,1,0],[a,0,1.]]);B=6000
            Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,Q2,n);zeta=np.zeros(2)
            sz,_,_=ridge_size(Z,zeta,Sh,lam,rng,table=20000);row.append(f'{an}:{sz:.3f}')
        print(f'lam={name} n={n} nlam={n*lam:.1f} sqrtnlam={n**.5*lam:.2f} Q2 size',' '.join(row),flush=True)
print('=== C4: oracle Sigma^-1 sup along a=c/sqrt n, b=0; and ridge on the same path, n=5000')
n=5000
for c_ in (.05,.1,.25,.5,1,2,4):
    a=c_/math.sqrt(n);R=np.array([[1,0,a],[0,1,0],[a,0,1.]]);B=20000
    Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,Q2,n);zeta=np.zeros(2)
    _,S,_=zsig(R[None],Q2);O,rk=oracle_stat(Z,zeta,S[0])
    g=rng.standard_normal((400000,3));w_=g[:,0]+c_;v_=g[:,1];lim=np.mean(g[:,2]**2+(w_*v_/c_)**2>5.991)
    w,V=np.linalg.eigh(Sh);P=np.einsum('bji,bj->bi',V,Z)**2;v0=(P/np.clip(w,1e-12,None)).sum(1)
    lim0=np.mean(g[:,2]**2+(w_*v_)**2/(w_*w_+v_*v_)>5.991)
    print(f'c={c_}: oracle rate={np.mean(O>stats.chi2.ppf(.95,rk)):.3f} (limit U^2+(wv/c)^2 tail {lim:.3f}) | V0 rate={np.mean(v0>5.991):.4f} (limit {lim0:.4f})',flush=True)
print('=== C5: limits V0 two weak links sup over (c1,c2) with rho_XY=c1c2/n')
g=rng.standard_normal((2000000,3));best=[]
for c1 in (0,.5,1,1.5,2,2.5,3,4,6):
    for c2 in (.5,1,1.5,2,2.5,3,4,6):
        w_=g[:,0]+c1;v_=g[:,1]+c2;t=np.mean(g[:,2]**2+(w_*v_-c1*c2)**2/(w_**2+v_**2)>5.991);best.append((t,c1,c2))
print('top',sorted(best)[-4:])
print('=== limit checks: tail U^2+U2^2/4', np.mean(g[:,0]**2+g[:,1]**2/4>5.991))
w_=g[:,0]+1;v_=g[:,1]
print('paper .1247:',np.mean(g[:,2]**2+(w_*v_)**2>5.991),' .0186:',np.mean(g[:,2]**2+(w_*v_)**2/(w_**2+v_**2)>5.991))
w_=g[:,0]+1;v_=g[:,1]+1
print('paper .0905:',np.mean(g[:,2]**2+(w_*v_-1)**2/2>5.991),' .0609:',np.mean(g[:,2]**2+(w_*v_-1)**2/(w_**2+v_**2)>5.991))
print('Var(wv-1)',np.var(w_*v_-1))
