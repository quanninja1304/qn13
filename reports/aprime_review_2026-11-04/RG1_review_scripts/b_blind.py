import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
from scipy import optimize
rng=np.random.default_rng(4242)
def dags(p):
    pairs=list(itertools.combinations(range(p),2));res=[]
    for perm in itertools.product((0,1,2),repeat=len(pairs)):
        A=np.zeros((p,p),int)
        for (i,j),c in zip(pairs,perm):
            if c==1:A[i,j]=1
            if c==2:A[j,i]=1
        # acyclic test via trace of powers
        M=np.eye(p,dtype=int);ok=True
        for _ in range(p):
            M=M@A
            if np.trace(M)>0: ok=False
        if ok: res.append(A)
    return res
def dsep(A,x,y,S):
    # Bayes-ball style: enumerate trails by (node,direction) reachability (differs from moral-graph route used by the author)
    p=len(A);S=set(S)
    anS=set(S);st=list(S)
    while st:
        v=st.pop()
        for u in range(p):
            if A[u,v] and u not in anS: anS.add(u);st.append(u)
    vis=set();st=[(x,'up')]
    while st:
        v,d=st.pop()
        if (v,d) in vis: continue
        vis.add((v,d))
        if v==y and v not in S: return False
        if d=='up' and v not in S:
            for u in range(p):
                if A[u,v]: st.append((u,'up'))
                if A[v,u]: st.append((u,'down'))
        if d=='down':
            if v not in S:
                for u in range(p):
                    if A[v,u]: st.append((u,'down'))
            if v in anS:
                for u in range(p):
                    if A[u,v]: st.append((u,'up'))
    return True
def rk(M,tol=1e-9): return np.linalg.matrix_rank(M,tol=tol) if M.size else 0
def blind(U,pat):
    K=U.shape[0];E=np.eye(K);I=[k for k in range(K) if pat[k]];D=[k for k in range(K) if not pat[k]]
    B=np.hstack([U,E[:,I]]);r=rk(B)
    b1=r==U.shape[1]+len(I)
    b2=all(rk(np.hstack([B,E[:,[k]]]))==r+1 for k in D)
    return b1 and b2
def explicit(z,pat,U,delta):
    """construct n in null(U^T) so that u=z-n in R^eta(m), exactly as the proof. Return u,residual seminorm"""
    K=len(z);Ns=np.linalg.svd(U.T)[2][U.shape[1]:].T  # basis of N
    I=[k for k in range(K) if pat[k]];D=[k for k in range(K) if not pat[k]]
    c0,*_=np.linalg.lstsq(Ns[I],z[I],rcond=None) if I else (np.zeros(Ns.shape[1]),)
    n0=Ns@c0
    # N0 basis
    if I:
        nn=np.linalg.svd(Ns[I])[2][np.linalg.matrix_rank(Ns[I]):].T
    else: nn=np.eye(Ns.shape[1])
    n1=Ns@nn@rng.normal(size=nn.shape[1])
    t=1+max((delta+abs(z[k]-n0[k]))/abs(n1[k]) for k in D)
    n=n0+t*n1;u=z-n
    return u,n
# p=3, K=6 from a REAL sample covariance; V0 metric Sigma_hat^+
R=np.array([[1,.2,.6],[.2,1,-.3],[.6,-.3,1.]])
qs=queries(3,1)
n=500;Ch=rawcov(R,n,1,rng)
Z,Sh,_=zsig(Ch,qs,n);z=Z[0];Sh=Sh[0]
w,V=np.linalg.eigh(Sh);print('eig Sigma_hat',np.round(w,4))
U=V[:,w>1e-8];Om=(U/w[w>1e-8])@U.T
print('z',np.round(z,2))
# patterns: complete; one independence each; and test pure-chain X-Y|Z 'blatant'
z2=z.copy();z2[1]=40.
for pat in [(0,0,0,0,0,0),(0,1,0,0,0,0),(1,0,0,0,0,0),(0,0,0,1,0,0),(1,1,0,0,0,0),(1,1,1,1,0,0)]:
    bl=blind(U,pat)
    if bl:
        u,nn=explicit(z2,pat,U,delta=5.0)
        I=[k for k in range(6) if pat[k]];D=[k for k in range(6) if not pat[k]]
        print(pat,'blind=True  d2 at constructed u =',float((z2-u)@Om@(z2-u)),'|u_I|max',np.abs(u[I]).max() if I else 0,'min|u_D|',np.abs(u[D]).min())
    else: print(pat,'blind=False')
# dimension rule on p=4, K=18,24, sample-based & population generic
Rr=np.array([[1,.35,.25,.3],[.35,1,.2,.4],[.25,.2,1,.45],[.3,.4,.45,1.]])
Ds=dags(4);print('n dags',len(Ds))
for c in (1,2):
    qq=queries(4,c);K=len(qq)
    _,Sp,_=zsig(Rr[None],qq);Sp=Sp[0]
    Chh=rawcov(Rr,400,1,rng);_,Ss,_=zsig(Chh,qq);Ss=Ss[0]
    for name,SS in (('pop',Sp),('sample-Cov',Ss)):
        w,V=np.linalg.eigh(SS);Ur=V[:,w>1e-8];r=Ur.shape[1]
        pats={}
        for A in Ds: pats.setdefault(tuple(int(dsep(A,x,y,S)) for x,y,S in qq),[]).append(A)
        fl={pt:blind(Ur,pt) for pt in pats}
        rule={pt:(sum(pt)<K-r) for pt in pats}
        mism=sum(fl[p]!=rule[p] for p in pats)
        print(f'p=4 K={K} {name}: rank={r} patterns={len(pats)} blind={sum(fl.values())} rule |D|>r gives={sum(rule.values())} mismatches={mism}')
        for emax in (1,2,3):
            sub=[A for A in Ds if A.sum()<=emax]
            pt_sub={tuple(int(dsep(A,x,y,S)) for x,y,S in qq) for A in sub}
            print(f'   e<={emax}: blind {sum(fl[p] for p in pt_sub)}/{len(pt_sub)}')
# model-specific (block) seminorm on the same 'blind' patterns at K=6: Omega_m = Sigma_II^+ on I only
print('block seminorm on chain pattern with z_XY|Z=40:',end=' ')
I=[1];print(z2[I]@np.linalg.pinv(Sh[np.ix_(I,I)])@z2[I])
# Sigma rank within I at S3 pattern
Rs=np.eye(3);Rs[0,2]=Rs[2,0]=.447
_,S3,_=zsig(Rs[None],qs);S3=S3[0];I=[k for k,q in enumerate(qs) if q[:2] in ((0,1),(1,2))]
print('S3 I-block rank',rk(S3[np.ix_(I,I)]),'P(chi2_rank>chi2_3,.95)=',stats.chi2.sf(stats.chi2.ppf(.95,3),rk(S3[np.ix_(I,I)])))
