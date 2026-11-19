"""E1 reading (rules v2 RN1/RN2 + v2.1 A1-A4, A6): primary contrast A, k = 20 vs k = 0 on 80 EXP systems.

usage: analyze_e1.py <model>   -> pn1_out/e1_<model>.json
Bootstrap over systems, 2000 resamples, percentile 95%, seed 20261114 (v2 §5).
"""
import sys, json
import numpy as np
from common import systems, target, CELLS, OUT
from metrics import *

model = sys.argv[1]
rn0 = json.loads((OUT / f'rn0_{model}.json').read_text())
tau_p = rn0['RN0.3_determinism']['tau_rep']
tau_fn = rn0['RN0.3_determinism']['tau_flips_native_rep']; tau_ff = rn0['RN0.3_determinism']['tau_flips_fixed_rep']
if model == 'foundcause':
    ts = rn0['A5_tau_sched']
    tau_p = max(tau_p, ts['tau_sched']); tau_fn = max(tau_fn, ts['tau_flips_native_sched']); tau_ff = max(tau_ff, ts['tau_flips_fixed_sched'])
B, SEED = 2000, 20261114


def label(est, lo, hi, tau, m):
    if lo > max(tau, m): return 'MEANINGFUL'
    if lo > tau: return 'DETECTABLE'
    if hi <= max(tau, m): return 'BELOW_MARGIN'
    return 'INCONCLUSIVE'


def ci_mean(v):
    return boot_ci(v, np.mean, B, SEED)


rows = []
for s, ci, seed in systems('EXP'):
    t = target(s, ci, seed); g = t['g']; dT = g.shape[0]
    o0, o1 = load(model, s, '-', 0), load(model, s, 'A', 20)
    r = dict(sys=s, cell=CELLS[ci], lin=CELLS[ci][2] == 'lin')
    r['dp'], r['dp_max'] = dp(o1['probs'], o0['probs'], dT)
    sf0, sf1 = skel_fixed(o0['probs'], dT), skel_fixed(o1['probs'], dT)
    sn0, sn1 = skel_native(model, o0, dT), skel_native(model, o1, dT)
    r['flips_fixed'], r['flips_native'] = flips(sf1, sf0), flips(sn1, sn0)
    r['f1_fixed_0'], r['f1_fixed_20'] = f1(sf0, g), f1(sf1, g)
    r['f1_native_0'], r['f1_native_20'] = f1(sn0, g), f1(sn1, g)
    r['H_fixed'] = r['f1_fixed_0'] - r['f1_fixed_20']; r['H_native'] = r['f1_native_0'] - r['f1_native_20']
    if model == 'cdfm':
        sz1 = skel_frozen_cdfm(o1, dT, float(o0['threshold']))
        r['f1_frozen_20'] = f1(sz1, g); r['H_frozen'] = r['f1_native_0'] - r['f1_frozen_20']
        r['thr_0'], r['thr_20'] = float(o0['threshold']), float(o1['threshold'])
    r['E_fixed_0'], r['E_fixed_20'] = int(sf0.sum() // 2), int(sf1.sum() // 2)
    r['X_fixed_20'] = cross_edges(o1['probs'], dT)
    for alg in ('pc', 'ges'):
        z0, z1 = load(alg, s, '-', 0), load(alg, s, 'A', 20)
        k0, k1 = z0['skel'][:dT, :dT], z1['skel'][:dT, :dT]
        r[f'H_{alg}'] = f1(k0, g) - f1(k1, g); r[f'flips_{alg}'] = flips(k1, k0); r[f'f1_{alg}_0'] = f1(k0, g)
        r[f'X_{alg}_20'] = int(z1['skel'][:dT, dT:].sum())
    rows.append(r)

V = lambda key, sub=None: np.array([r[key] for r in rows if (sub is None or sub(r))], float)
res = dict(model=model, n_systems=len(rows), tau=dict(dp=tau_p, flips_native=tau_fn, flips_fixed=tau_ff))
# A1 change labels
e, lo, hi = boot_ci(V('dp'), np.median, B, SEED)
res['SCORE_CHANGE'] = dict(median_dp=e, ci=[lo, hi], label=label(e, lo, hi, tau_p, 0.01))
for nm, key, tau in (('GRAPH_CHANGE_NATIVE', 'flips_native', tau_fn), ('GRAPH_CHANGE_FIXED', 'flips_fixed', tau_ff)):
    e, lo, hi = ci_mean(V(key)); res[nm] = dict(mean_flips=e, ci=[lo, hi], label=label(e, lo, hi, tau, 1.0))
# A2 harm
for nm in ('H_native', 'H_fixed'):
    e, lo, hi = ci_mean(V(nm)); res[nm] = dict(mean=e, ci=[lo, hi], HARM=bool(e >= 0.05 and lo > 0))
res['F1_k0'] = dict(native=float(V('f1_native_0').mean()), fixed=float(V('f1_fixed_0').mean()))
# A3 beyond classical, linear only; max taken after aggregation, recomputed inside each resample
lin = lambda r: r['lin']
Hpc, Hges = V('H_pc', lin), V('H_ges', lin)
rng = np.random.default_rng(SEED); idx = rng.integers(0, len(Hpc), (B, len(Hpc)))
for nm in ('H_native', 'H_fixed'):
    Hm = V(nm, lin)
    est = Hm.mean() - max(Hpc.mean(), Hges.mean())
    bs = np.array([Hm[i].mean() - max(Hpc[i].mean(), Hges[i].mean()) for i in idx])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    d_pc, d_ges = ci_mean(Hm - Hpc), ci_mean(Hm - Hges)
    res[f'BEYOND_CLASSICAL_{nm}'] = dict(est=float(est), ci=[float(lo), float(hi)], PASS=bool(est >= 0.05 and lo > 0),
                                         minus_pc=d_pc, minus_ges=d_ges, H_model_linear=ci_mean(Hm))
# A4 classical references (linear: claim-bearing; RFF: diagnostic misspecified)
for scope, sub in (('linear', lin), ('rff_diagnostic', lambda r: not r['lin'])):
    for alg in ('pc', 'ges'):
        h = ci_mean(V(f'H_{alg}', sub)); fl = ci_mean(V(f'flips_{alg}', sub))
        res[f'classical_{alg}_{scope}'] = dict(H=h, F1_near_equivalent=bool(h[1] >= -0.02 and h[2] <= 0.02), flips=fl,
                                               output_near_invariant=bool(fl[2] < 1.0), f1_k0=float(V(f'f1_{alg}_0', sub).mean()),
                                               X_mean=float(V(f'X_{alg}_20', sub).mean()))
# M4 (readable from E1)
if model == 'cdfm':
    e, lo, hi = ci_mean(V('H_native') - V('H_frozen'))
    alt = res['SCORE_CHANGE']['label'] == 'BELOW_MARGIN' and res['GRAPH_CHANGE_NATIVE']['label'] in ('DETECTABLE', 'MEANINGFUL')
    res['M4'] = dict(H_native_minus_frozen=[e, lo, hi], PASS=bool((e >= 0.03 and lo > 0) or alt), alt_route=bool(alt),
                     thr_0=float(V('thr_0').mean()), thr_20=float(V('thr_20').mean()))
elif model == 'foundcause':
    e, lo, hi = ci_mean(V('H_native') - V('H_fixed'))
    res['M4'] = dict(H_native_minus_fixed=[e, lo, hi], PASS=bool(e >= 0.03 and lo > 0), reading='agreement pruning, not threshold')
    res['E2_TRIGGER'] = any(res[k]['label'] in ('DETECTABLE', 'MEANINGFUL') for k in ('SCORE_CHANGE', 'GRAPH_CHANGE_NATIVE', 'GRAPH_CHANGE_FIXED'))
else:
    res['M4'] = 'NOT_APPLICABLE (AVICI: FROZEN = NATIVE)'
# descriptive by cell
res['by_cell'] = {}
for c in CELLS:
    sub = lambda r, c=c: tuple(r['cell']) == c
    res['by_cell'][str(c)] = {k: float(V(k, sub).mean()) for k in ('dp', 'flips_fixed', 'flips_native', 'H_fixed', 'H_native', 'H_pc', 'H_ges',
                                                                   'f1_fixed_0', 'E_fixed_0', 'E_fixed_20', 'X_fixed_20')}
res['X_fixed_20_mean'] = float(V('X_fixed_20').mean())
(OUT / f'e1_{model}.json').write_text(json.dumps(dict(summary=res, rows=rows), indent=1, default=str))
print(json.dumps(res, indent=1, default=str))
