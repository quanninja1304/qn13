import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
rng=np.random.default_rng(2025)
Q=[(0,1,()),(0,1,(2,)),(0,2,())];I=[0,1];k=2
def stats_(z,Sh,lam,delta):
    """z: (N,3) (or single)  d2_eta with |D|=1, closed form; T0^sign(z) when delta=None handled separately"""
    A=Sh+lam*np.eye(3);Ai=np.linalg.inv(A)
    AII=A[np.ix_(I,I)];b=np.linalg.solve(AII,A[I,k]);cv=A[k,k]-A[k,I]@b
    S=np.einsum('...i,ij,...j',z[...,I],np.linalg.inv(AII),z[...,I])
    res=z[...,k]-z[...,I]@b   # free minimiser v_k^o = b'z_I, u_k^o = z_k - b'z_I = res
    return S,res,cv
for n,hs in ((1000,(0,1,2,3,5,8,14)),(5000,(1,3,5,8,14))):
  for h in hs:
    B=2500;lam=n**(-1/3)
    a=max(h,1e-9)/math.sqrt(n-3)
    a=math.tanh(h/math.sqrt(n-3))
    R=np.array([[1,0,a],[0,1,0],[a,0,1.]])
    Ch=wish(R,n,B,rng);Z,Sh,_=zsig(Ch,Q,n)
    delta=math.sqrt(n-3)*math.atanh(a)  # eta=beta, zeta at active boundary
    G0=rng.standard_normal((6000,3))
    rc=np.zeros(4);cbar=[];cI=[];cn=[]
    for b in range(B):
        Sb=Sh[b];z=Z[b]
        S,res,cv=stats_(z,Sb,lam,delta)
        d2=S+(max(delta-abs(res),0))**2/cv
        # thresholds
        w=np.clip(np.linalg.eigvalsh(Sb),0,None);wf=w/(w+lam);wI=np.clip(np.linalg.eigvalsh(Sb[np.ix_(I,I)]),0,None);wIf=wI/(wI+lam)
        c_n=np.quantile((G0**2)@wf,.95);c_I=np.quantile((G0[:,:2]**2)@wIf,.95)
        L=np.linalg.cholesky(Sb+1e-10*np.eye(3));G=G0@L.T
        Sg,rg,cvg=stats_(G,Sb,lam,0.0)
        qs_=[np.quantile(Sg+(np.minimum(sg*rg,0))**2/cvg,.95) for sg in (1,-1)]
        c_bar=max(qs_)
        rc+=np.array([d2>c_I,d2>c_bar,d2>c_n,c_bar>c_n+1e-9])
        cbar.append(c_bar);cI.append(c_I);cn.append(c_n)
    print(f'n={n} h={h} a={a:.4f}: P(d2>c_I)={rc[0]/B:.3f} P(d2>c_bar)={rc[1]/B:.3f} P(d2>c_n)={rc[2]/B:.3f} | mean c_I={np.mean(cI):.2f} c_bar={np.mean(cbar):.2f} c_n={np.mean(cn):.2f} frac c_bar>c_n={rc[3]/B:.3f} SE={math.sqrt(.05*.95/B):.4f}',flush=True)
