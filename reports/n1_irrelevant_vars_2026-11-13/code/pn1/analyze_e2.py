"""E2 reading (rules v2 RN3/RN4 + v2.1 A4, A8, A12; operational reading logged 19/11/2026 before viewing E2 metrics).

usage: analyze_e2.py <model>   -> pn1_out/e2_<model>.json
Signatures at k = 20 on 80 EXP systems, computed separately for H_NATIVE and H_FIXED. No lead is selected here.
Bootstrap over systems, 2000 resamples, percentile 95%, seed 20261114.
"""
import sys, json
import numpy as np
from common import systems, target, CELLS, OUT
from metrics import load, dp, flips, f1, skel_fixed, skel_native, skel_frozen_cdfm, cross_edges, boot_ci

model = sys.argv[1]
B, SEED = 2000, 20261114
if model == 'foundcause':
    GRID = [('A', 5), ('A', 10), ('A', 20), ('A', 30), ('B', 20), ('C', 20), ('D', 20)]
else:
    GRID = [(t, k) for t in 'ABCD' for k in (5, 10, 20, 30)]


def ap(score, label):
    """Average precision (area under the precision-recall step curve); ties broken by stable sort."""
    o = np.argsort(-score, kind='stable'); y = label[o].astype(bool)
    if y.sum() == 0:
        return np.nan
    tp = np.cumsum(y); prec = tp / np.arange(1, len(y) + 1)
    return float(prec[y].sum() / y.sum())


def auprc(probs, g):
    dT = g.shape[0]; p = probs[:dT, :dT]; off = ~np.eye(dT, dtype=bool)
    iu = np.triu_indices(dT, 1); s = np.maximum(p, p.T)[iu]; sk = ((g + g.T) > 0)[iu]
    return ap(p[off], g[off]), ap(s, sk)


def mean_ci(v):
    return boot_ci(v, np.mean, B, SEED)


rows = []
for s, ci, seed in systems('EXP'):
    t = target(s, ci, seed); g = t['g']; dT = g.shape[0]
    o0 = load(model, s, '-', 0)
    sn0, sf0 = skel_native(model, o0, dT), skel_fixed(o0['probs'], dT)
    r = dict(sys=s, cell=CELLS[ci], lin=CELLS[ci][2] == 'lin')
    a0 = auprc(o0['probs'], g)
    r['k0'] = dict(f1_native=f1(sn0, g), f1_fixed=f1(sf0, g), E_fixed=int(sf0.sum() // 2), auprc_dir=a0[0], auprc_skel=a0[1])
    cl0 = {alg: load(alg, s, '-', 0)['skel'][:dT, :dT] for alg in ('pc', 'ges')}
    for typ, k in GRID:
        o = load(model, s, typ, k)
        sn, sf = skel_native(model, o, dT), skel_fixed(o['probs'], dT)
        a = auprc(o['probs'], g)
        c = dict(dp=dp(o['probs'], o0['probs'], dT)[0], flips_native=flips(sn, sn0), flips_fixed=flips(sf, sf0),
                 H_native=r['k0']['f1_native'] - f1(sn, g), H_fixed=r['k0']['f1_fixed'] - f1(sf, g),
                 E_fixed=int(sf.sum() // 2), X_fixed=cross_edges(o['probs'], dT),
                 dauprc_dir=a0[0] - a[0], dauprc_skel=a0[1] - a[1])
        if model == 'cdfm':
            c['H_frozen'] = r['k0']['f1_native'] - f1(skel_frozen_cdfm(o, dT, float(o0['threshold'])), g)
        if model != 'avici':
            a_ = o['adj_native']; c['X_native'] = int(((a_ + a_.T) > 0)[:dT, dT:].sum())
        for alg in ('pc', 'ges'):
            z = load(alg, s, typ, k)['skel']
            c[f'H_{alg}'] = f1(cl0[alg], g) - f1(z[:dT, :dT], g); c[f'flips_{alg}'] = flips(z[:dT, :dT], cl0[alg])
            c[f'X_{alg}'] = int(z[:dT, dT:].sum())
        r[f'{typ}{k}'] = c
    rows.append(r)

V = lambda cond, key, sub=None: np.array([r[cond][key] for r in rows if sub is None or sub(r)], float)
lin = lambda r: r['lin']
res = dict(model=model, n_systems=len(rows), grid=[f'{t}{k}' for t, k in GRID])

# RN3 signatures at k = 20, per estimand
sig = {}
dpA = {k: V(f'A{k}', 'dp') for k in (5, 10, 20, 30)}
med_dpA = {k: float(np.median(v)) for k, v in dpA.items()}
d30_5 = boot_ci(dpA[30] - dpA[5], np.median, B, SEED)
dp_part = dict(median_dpA_by_k=med_dpA, median_dp30_minus_dp5=d30_5,
               nondecreasing=bool(all(med_dpA[a] <= med_dpA[b] for a, b in ((5, 10), (10, 20), (20, 30)))),
               PASS=bool(d30_5[1] > 0 and all(med_dpA[a] <= med_dpA[b] for a, b in ((5, 10), (10, 20), (20, 30)))))
for est in ('H_native', 'H_fixed'):
    HA, HB, HC, HD = (V(f'{t}20', est) for t in 'ABCD')
    m1 = mean_ci(HA - HB); m3 = mean_ci(HD - HA)
    pairs = {'A-B': mean_ci(HA - HB), 'A-C': mean_ci(HA - HC), 'B-C': mean_ci(HB - HC)}
    m2_h = all(v[1] >= -0.03 and v[2] <= 0.03 for v in pairs.values())
    side = lambda v, m: ('+' if v[1] > m else '-' if v[2] < -m else None)
    e = dict(H_by_type_k20={t: mean_ci(V(f'{t}20', est)) for t in 'ABCD'},
             M1=dict(delta_A_minus_B=m1, PASS=side(m1, 0.03) is not None, sign=side(m1, 0.03),
                     E_fixed_A_minus_B=mean_ci(V('A20', 'E_fixed') - V('B20', 'E_fixed'))),
             M2=dict(pairs=pairs, H_part=bool(m2_h), dp_part=dp_part['PASS'], PASS=bool(m2_h and dp_part['PASS'])),
             M3=dict(delta_D_minus_A=m3, PASS=side(m3, 0.05) is not None, sign=side(m3, 0.05)))
    e['fired'] = [m for m in ('M1', 'M2', 'M3') if e[m]['PASS']]
    sig[est] = e
res['signatures'] = sig
res['dp_curve_A'] = dp_part
e1 = json.loads((OUT / f'e1_{model}.json').read_text())['summary']
res['M4_from_E1'] = e1['M4']

# RN4 descriptive
desc = {}
for typ, k in GRID:
    c = f'{typ}{k}'
    d = dict(median_dp=boot_ci(V(c, 'dp'), np.median, B, SEED))
    for key in ('flips_native', 'flips_fixed', 'H_native', 'H_fixed', 'dauprc_dir', 'dauprc_skel', 'H_pc', 'H_ges', 'flips_pc', 'flips_ges'):
        d[key] = mean_ci(V(c, key))
    for key in ('E_fixed', 'X_fixed', 'X_pc', 'X_ges') + (('X_native',) if model != 'avici' else ()) + (('H_frozen',) if model == 'cdfm' else ()):
        d[key] = float(V(c, key).mean())
    d['H_native_linear'] = mean_ci(V(c, 'H_native', lin)); d['H_fixed_linear'] = mean_ci(V(c, 'H_fixed', lin))
    d['H_native_rff'] = mean_ci(V(c, 'H_native', lambda r: not r['lin'])); d['H_fixed_rff'] = mean_ci(V(c, 'H_fixed', lambda r: not r['lin']))
    if typ == 'B' and k == 5:
        d['note'] = 'B_CLIPPED for e = 2 cells'
    desc[c] = d
res['descriptive'] = desc
res['k0'] = {key: float(np.nanmean([r['k0'][key] for r in rows])) for key in rows[0]['k0']}

# descriptive beyond-classical on linear systems, k = 20, every type (A repeats E1)
rng = np.random.default_rng(SEED)
bc = {}
for typ in 'ABCD':
    c = f'{typ}20'; Hpc, Hges = V(c, 'H_pc', lin), V(c, 'H_ges', lin)
    idx = rng.integers(0, len(Hpc), (B, len(Hpc)))
    for est in ('H_native', 'H_fixed'):
        Hm = V(c, est, lin); e_ = Hm.mean() - max(Hpc.mean(), Hges.mean())
        bs = np.array([Hm[i].mean() - max(Hpc[i].mean(), Hges[i].mean()) for i in idx])
        bc[f'{c}_{est}'] = [float(e_), *map(float, np.percentile(bs, [2.5, 97.5]))]
res['beyond_classical_descriptive_linear'] = bc
(OUT / f'e2_{model}.json').write_text(json.dumps(dict(summary=res, rows=rows), indent=1, default=str))
print(json.dumps(res, indent=1, default=str))
