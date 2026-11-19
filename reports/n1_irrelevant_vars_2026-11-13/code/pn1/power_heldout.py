# v2.2 §1 power reasoning (written 19/11/2026 after E2, before any held-out data). usage: power_heldout.py 3 6 10
"""Replication probability of each locked held-out criterion IF the true effect equals the E2 estimate
(stratified resampling of E2 systems, per_cell per cell; percentile bootstrap CI as the real analysis). Optimistic (winner's curse)."""
import json, os, numpy as np, sys
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pn1_out'); S=1000; B=1000; rng=np.random.default_rng(1)
R={m: json.load(open(f'{OUT}/e2_{m}.json'))['rows'] for m in ('avici','cdfm','foundcause')}
def arr(m,c,k): return np.array([r[c][k] for r in R[m]])
cells=np.array([str(r['cell']) for r in R['avici']]); lin=np.array([r['lin'] for r in R['avici']])
uc=sorted(set(cells))
def ci(v):  # v: (S, n) -> lo, hi of mean
    n=v.shape[1]; idx=rng.integers(0,n,(B,n)); bs=v[:,idx].mean(2); return np.percentile(bs,2.5,1), np.percentile(bs,97.5,1)
def draw(pc):
    return np.stack([np.concatenate([rng.choice(np.where(cells==c)[0],pc) for c in uc]) for _ in range(S)])


def run(pc):
    I=draw(pc); res={}
    def mean_rule(v, rule):
        x=v[I]; lo,hi=ci(x); e=x.mean(1); return float(np.mean(rule(e,lo,hi)))
    harm=lambda e,lo,hi:(e>=0.05)&(lo>0)
    for m,est in (('avici','H_native'),('cdfm','H_native'),('cdfm','H_fixed'),('foundcause','H_native')):
        res[f'{m} HARM {est}']=mean_rule(arr(m,'A20',est),harm)
    res['avici M1 (hi<-0.03)']=mean_rule(arr('avici','A20','H_native')-arr('avici','B20','H_native'),lambda e,lo,hi:hi<-0.03)
    for lab,lo_thr in (('FC branch A-B lo>0.03',0.03),('FC branch A-B lo>0',0.0)):
        res[lab]=mean_rule(arr('foundcause','A20','H_native')-arr('foundcause','B20','H_native'),lambda e,lo,hi,t=lo_thr:lo>t)
    # CDFM M2 fixed: three equivalence CIs inside +-0.03 (dp part checked separately)
    ok=np.ones(S,bool)
    for a,b in (('A20','B20'),('A20','C20'),('B20','C20')):
        x=(arr('cdfm',a,'H_fixed')-arr('cdfm',b,'H_fixed'))[I]; lo,hi=ci(x); ok&=(lo>=-0.03)&(hi<=0.03)
    res['cdfm M2_FIXED H-part']=float(ok.mean())
    # beyond classical, linear systems only, max of baselines recomputed per bootstrap
    Il=np.stack([i[lin[i]] for i in I]); n=Il.shape[1]
    for m,est in (('avici','H_native'),('cdfm','H_fixed'),('cdfm','H_native'),('foundcause','H_native')):
        Hm,Hp,Hg=arr(m,'A20',est)[Il],arr(m,'A20','H_pc')[Il],arr(m,'A20','H_ges')[Il]
        e=Hm.mean(1)-np.maximum(Hp.mean(1),Hg.mean(1)); idx=rng.integers(0,n,(B,n))
        bs=Hm[:,idx].mean(2)-np.maximum(Hp[:,idx].mean(2),Hg[:,idx].mean(2)); lo=np.percentile(bs,2.5,1)
        res[f'{m} BEYOND_CLASSICAL {est} ({n} lin)']=float(np.mean((e>=0.05)&(lo>0)))
    return res
for pc in map(int, sys.argv[1:]):
    print(f'--- {pc} per cell = {8*pc} systems'); [print(f'  {k:40s} {v:.2f}') for k,v in run(pc).items()]
