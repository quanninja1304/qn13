import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
from scipy import optimize
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'b_helpers.py')).read())
rng=np.random.default_rng(1234)
qs=queries(3,1);Ds=dags(3);pats=[tuple(int(dsep(A,x,y,S)) for x,y,S in qs) for A in Ds]
def anc(A):
    M=A.copy()
    for _ in range(3): M=((M+M@A)>0).astype(int)
    return M
ancs=[anc(A) for A in Ds]
Ach=np.zeros((3,3),int);Ach[0,2]=1;Ach[2,1]=1
ms=[i for i,A in enumerate(Ds) if np.array_equal(A,Ach)][0]
# feature list false at truth
F=[]
for x,y in itertools.permutations(range(3),2):
    for neg in (0,1):
        tv=[(a[x,y]==0) if neg else (a[x,y]==1) for a in ancs];F.append(tv)
fls=[tv for tv in F if not tv[ms]]
upat=sorted(set(pats))
bad={}
for p in upat:
    idx=[i for i,q in enumerate(pats) if q==p]
    bad[p]=any(all(tv[i] for i in idx) for tv in fls)
n=2000
for h in (.5,1,1.5,2,2.5,3,3.5,4,5,5.28):
    def R_(b):
        Inv=np.linalg.inv(np.eye(3)-np.array([[0,0,0],[0,0,b],[b,0,0.]]));C=Inv@Inv.T;d=np.sqrt(np.diag(C));return C/np.outer(d,d)
    b=optimize.brentq(lambda b:abs(np.arctanh(zsig(R_(b)[None],qs,sig=False)[2][0][0]))-h/n**.5,1e-3,3)
    R=R_(b);B=100000
    Ch=wish(R,n,B,rng);Z,_,_=zsig(Ch,qs,n,sig=False)
    nk=np.array([n-len(q[2])-3 for q in qs],float);d=np.sqrt(nk)*h/n**.5
    ph=(np.abs(Z)<d/2).astype(int)
    cnt=sum(bad.get(tuple(r),False) for r in ph)
    print(f'h={h} b={b:.3f} CT FWER={cnt/B:.4f} (SE {(cnt/B*(1-cnt/B)/B)**.5:.4f})',flush=True)
