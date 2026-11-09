import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
rng=np.random.default_rng(55)
print('=== F1 ridge size near boundary of PD cone: equi rho, K=6 and p=4 K=24; n small')
Q6=queries(3,1);Q24=queries(4,2)
def equi(p,r):return (1-r)*np.eye(p)+r*np.ones((p,p))
for p,qs,B in ((3,Q6,6000),(4,Q24,3000)):
  for r in (.9,.99,.999):
    R=equi(p,r)
    for n in (50,100,200,1000,5000):
      if n<=p+3:continue
      lam=n**(-1/3);nk=np.array([n-len(q[2])-3 for q in qs])
      zt=np.sqrt(nk)*np.arctanh(zsig(R[None],qs,sig=False)[2][0])
      Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,qs,n)
      sz,_,_=ridge_size(Z,zt,Sh,lam,rng,table=12000)
      print(f'p={p} K={len(qs)} equi={r} lmin={1-r:.3f} n={n}: ridge size={sz:.3f} SE={(0.0475/B)**.5:.3f}',flush=True)
print('=== F2 drifting eigen near lam on several blocks: Q= {X_i _|_ Y | , X_i _|_ Y | Z_i}, i=1..q, a=sqrt(2lam) each. K=2q')
for q in (2,4,8):
  # V = (Y, X1..Xq, Z1..Zq); Xi ~ Zi corr a; all else indep
  p=1+2*q
  qs=[]
  for i in range(q):
      qs.append((0,1+i,()));qs.append((0,1+i,(1+q+i,)))
  for n in (100,200,1000,5000):
    if n<=p+4:continue
    lam=n**(-1/3)
    for an,a in (('sqrt(2lam)',min(.95,math.sqrt(2*lam))),('1/sqrt n',n**-.5),('0',0.)):
      R=np.eye(p)
      for i in range(q):R[1+i,1+q+i]=R[1+q+i,1+i]=a
      B=4000
      Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,qs,n)
      sz,_,_=ridge_size(Z,np.zeros(2*q),Sh,lam,rng,table=12000)
      print(f'q={q} K={2*q} n={n} a={an}({a:.3f}): ridge size={sz:.3f} SE={(0.0475/B)**.5:.3f}',flush=True)
