import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
rng=np.random.default_rng(777)
# random R p=5 from random factor; random Q with repeated pairs, non-marginal
A=rng.normal(size=(5,8));C=A@A.T;d=np.sqrt(np.diag(C));R=C/np.outer(d,d)
qs=[(0,1,()),(0,1,(2,)),(0,1,(2,3)),(0,2,(1,)),(1,3,(0,4)),(3,4,()),(2,4,(0,1,3)),(0,4,(3,))]
K=len(qs)
_,S,rho=zsig(R[None],qs);S=S[0];rho=rho[0]
print('min eig R',np.linalg.eigvalsh(R).min(),'rho',np.round(rho,3))
# route 1: influence function direct MC (uses my own regression of population coefs by lstsq on huge sample path independent of Isserlis)
N=4000000
V=rng.standard_normal((N,5))@np.linalg.cholesky(R).T
psi=np.zeros((N,K))
for k,(x,y,Sx) in enumerate(qs):
    Sx=list(Sx)
    def res(t):
        if not Sx: return V[:,t]/np.sqrt(R[t,t])
        b=np.linalg.solve(R[np.ix_(Sx,Sx)],R[Sx,t])
        e=V[:,t]-V[:,Sx]@b
        return e/np.sqrt(R[t,t]-R[t,Sx]@b)
    ex,ey=res(x),res(y)
    psi[:,k]=(ex*ey-rho[k]/2*(ex**2+ey**2))/(1-rho[k]**2)
Cp=np.cov(psi,rowvar=False)
print('psi mean max',np.abs(psi.mean(0)).max(),'  |Cov(psi)-(2.1)| max',np.abs(Cp-S).max(),'expected MC err ~',3/np.sqrt(N))
# route 2: raw data Fisher z MC at n=800
n=800;B=20000
Ch=rawcov(R,n,B,rng)
Z,_,_=zsig(Ch,qs,n,sig=False)
Cz=np.cov(Z,rowvar=False)
nk=np.array([n-len(q[2])-3 for q in qs]);adj=np.sqrt(np.outer(nk,nk))/n
print('|Cov(z)-(2.1)*sqrt(nk nl)/n| max',np.abs(Cz-S*adj).max(),'expected ~',2.5/np.sqrt(B))
print('off-diagonal S rounded\n',np.round(S,3))
# plug in S_hat unit diagonal; rank(S)=K? 
print('eig S',np.round(np.linalg.eigvalsh(S),4))
# Prop2(i) Gram identity: finite-diff gradient
def g(C):return np.arctanh(zsig(C[None],qs,sig=False)[2][0])
H=np.zeros((K,5,5));h=1e-6
for i in range(5):
    for j in range(i,5):
        E=np.zeros((5,5));E[i,j]=E[j,i]=1
        dg=(g(R+h*E)-g(R-h*E))/(2*h)
        for k in range(K):
            H[k,i,j]=H[k,j,i]=dg[k]/(1 if i==j else 2)
G=np.array([[2*np.trace(H[k]@R@H[l]@R) for l in range(K)] for k in range(K)])
print('|2tr(HkRHlR)-(2.1)| max',np.abs(G-S).max())
# E x^4<=15(E x^2)^2 check in direction near 0 eigen; Monte Carlo at drop
