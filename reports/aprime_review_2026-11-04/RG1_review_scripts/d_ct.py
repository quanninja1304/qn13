import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
from scipy import optimize
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'b_helpers.py')).read())
rng=np.random.default_rng(99)
qs=queries(3,1);K=6 # (0,1,()),(0,1,(2,)),(0,2,()),(0,2,(1,)),(1,2,()),(1,2,(0,))
Ds=dags(3);pats=[tuple(int(dsep(A,x,y,S)) for x,y,S in qs) for A in Ds]
up=sorted(set(pats));pid={p:i for i,p in enumerate(up)};print('n dags',len(Ds),'patterns',len(up))
def anc(A):
    M=A.copy()
    for _ in range(3): M=((M+M@A)>0).astype(int)
    return M
ancs=[anc(A) for A in Ds]
feats=[]
for x,y in itertools.permutations(range(3),2):
    feats.append((f'{x}inAn{y}',[a[x,y]==1 for a in ancs]));feats.append((f'{x}notAn{y}',[a[x,y]==0 for a in ancs]))
fp=[]
for nm,tv in feats:
    fp.append((nm,tv,sorted({pid[pats[i]] for i,t in enumerate(tv) if not t})))
def dist2(z,pat,delta,W):
    D=[k for k in range(len(z)) if pat[k]==0]
    base=W@z;
    if not D: return base@base
    best=np.inf;cols=W[:,D];d=delta[D]
    for s in itertools.product((1.,-1.),repeat=len(D)):
        s=np.array(s);A=cols*s;_,r=optimize.nnls(A,base-A@d,maxiter=300)
        best=min(best,r*r)
    return best
def run(Bm,mstar_adj,eta,n,B,tab):
    Inv=np.linalg.inv(np.eye(3)-np.array(Bm,float));C=Inv@Inv.T;d=np.sqrt(np.diag(C));R=C/np.outer(d,d)
    ms=[i for i,A in enumerate(Ds) if np.array_equal(A,mstar_adj)][0];pst=pats[ms]
    nk=np.array([n-len(q[2])-3 for q in qs],float);delta=np.sqrt(nk)*eta
    rho=zsig(R[None],qs,sig=False)[2][0];theta=np.arctanh(rho);beta=min(abs(theta[k]) for k in range(6) if pst[k]==0)
    Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,qs,n);lam=n**(-1/3)
    tK=stats.norm.isf(.05/12)
    r={'R1':0,'R1raw':0,'CT':0,'BL1':0,'empty':0,'wrongCT':0,'emptyBL':0};tp={'R1':0,'CT':0,'BL1':0};den=0
    for b in range(B):
        w,V=np.linalg.eigh(Sh[b]);w=np.clip(w,0,None);W=(V/np.sqrt(w+lam))@V.T;wt=w/(w+lam)
        c=np.quantile(tab@wt,.95)
        d2=np.array([dist2(Z[b],p,delta,W) for p in up]);ne=d2.min()<=c
        sup=np.array([max(max([abs(Z[b][k]) for k in range(6) if p[k]==1],default=0),max([delta[k]-abs(Z[b][k]) for k in range(6) if p[k]==0],default=0)) for p in up])
        neB=sup.min()<=tK
        ph=tuple(int(abs(Z[b,k])<delta[k]/2) for k in range(6));inM=ph in pid
        r['empty']+=not ne;r['emptyBL']+=not neB;r['wrongCT']+=(inM and ph!=pst)
        af={'R1':False,'R1raw':False,'CT':False,'BL1':False}
        for nm,tv,nf in fp:
            if not nf: continue
            T=min(d2[j] for j in nf)>c;TB=min(sup[j] for j in nf)>tK
            ct=inM and pid[ph] not in nf
            if tv[ms]:
                if pid[pst] not in nf:
                    den+=1;tp['R1']+=T and ne;tp['CT']+=ct;tp['BL1']+=TB and neB
            else:
                af['R1raw']|=T;af['R1']|=(T and ne);af['CT']|=ct;af['BL1']|=(TB and neB)
        for k in af:r[k]+=af[k]
    out={k:v/B for k,v in r.items()};out.update({'tp_'+k:(v/den if den else None) for k,v in tp.items()});out['beta']=beta
    return out
tab=rng.standard_normal((40000,6))**2
print('=== D1 misspecified eta>2beta: X->Z strong, Y->Z weak. truth collider; eta=0.2 fixed (outside P_n); FWER counts false ancestral features')
A=np.zeros((3,3),int);A[0,2]=1;A[1,2]=1
Bm=[[0,0,0],[0,0,0],[.5,.05,0]]
for n in (200,500,1000,2000,5000,10000,20000,50000,200000):
    o=run(Bm,A,.2,n,600,tab);print(n,'beta=%.3f sqrt(n)beta=%.1f sqrt(n)eta=%.1f'%(o['beta'],n**.5*o['beta'],n**.5*.2),{k:round(v,3) for k,v in o.items() if k not in('beta',) and v is not None},flush=True)
print('=== D2 same SCM, eta<=beta control eta=0.04')
for n in (5000,50000,200000):
    o=run(Bm,A,.04,n,400,tab);print(n,{k:round(v,3) for k,v in o.items() if v is not None},flush=True)
print('=== D3 replicate chain local h=2, also collider h=2 from the doc: b tuned so min coordinate=h/sqrt(2000)')
n=2000
for h in (2,3,4):
    def build(b): return [[0,0,0],[0,0,b],[b,0,0]]
    def bet(b):
        Inv=np.linalg.inv(np.eye(3)-np.array(build(b)));C=Inv@Inv.T;d=np.sqrt(np.diag(C));R=C/np.outer(d,d)
        rho=zsig(R[None],qs,sig=False)[2][0];return abs(np.arctanh(rho[0]))
    b=optimize.brentq(lambda b:bet(b)-h/n**.5,1e-3,3)
    Ach=np.zeros((3,3),int);Ach[0,2]=1;Ach[2,1]=1
    o=run(build(b),Ach,h/n**.5,n,1500,tab);print('chain h',h,'b=%.3f'%b,{k:round(v,3) for k,v in o.items() if v is not None},flush=True)
