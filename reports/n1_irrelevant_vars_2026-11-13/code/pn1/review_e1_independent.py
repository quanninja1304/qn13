"""Independent re-check of the E1 reading (review, 16/11). Does NOT import metrics.py or analyze_e1.py.
Reads raw .npz directly, regenerates ground truth with common.target, recomputes key numbers, and adds
post hoc robustness descriptives (labelled POST HOC; not part of the locked rules)."""
import json, sys, collections
import numpy as np
from common import systems, target, CELLS, OUT
B, SEED = 2000, 20261114
def raw(m, s, typ, k, var='main'):
    z = np.load(OUT / m / f"{s}__{'-' if k == 0 else typ}__k{k}__{var}.npz", allow_pickle=False)
    return {a: z[a] for a in z.files}
def und(p, thr=0.5): return np.maximum(p, p.T) > thr
def F1(sk, gt):
    iu = np.triu_indices(gt.shape[0], 1); t = gt[iu]; s = sk[iu]
    tp = (t & s).sum(); return 0.0 if tp == 0 else 2 * tp / (2 * tp + (~t & s).sum() + (t & ~s).sum())
def auprc(score, gt):
    iu = np.triu_indices(gt.shape[0], 1); y = gt[iu].astype(int); sc = score[iu]
    o = np.argsort(-sc, kind='stable'); y = y[o]; tp = np.cumsum(y); prec = tp / np.arange(1, len(y) + 1)
    return float((prec * y).sum() / max(y.sum(), 1))
def ci(v, stat=np.mean):
    v = np.asarray(v, float); rng = np.random.default_rng(SEED); idx = rng.integers(0, len(v), (B, len(v)))
    bs = [stat(v[i]) for i in idx]; return [round(float(stat(v)), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]
S = systems('EXP')
# 1. integrity: same target fed to every model at k0 and k20; shapes
logs = {}
for m in ('avici', 'cdfm', 'foundcause', 'pc', 'ges'):
    for l in open(OUT / m / 'log_E1.jsonl', encoding='utf-8'):
        r = json.loads(l); logs.setdefault(r['key'], {})[m] = r
bad = 0; shapes = collections.Counter()
for key, d in logs.items():
    if len({v.get('input_sha') for v in d.values() if v.get('input_sha')}) != 1 or len(d) != 5: bad += 1
    shapes[(d['avici']['dT'], d['avici']['d'])] += 1
by_sys = collections.defaultdict(set)
for key, d in logs.items(): by_sys[key.split('__')[0]].add(d['avici']['target_sha'])
print('1. integrity: job keys', len(logs), '| keys with sha mismatch across 5 algs:', bad, '| systems whose k0/k20 target sha differ:', sum(len(v) != 1 for v in by_sys.values()), '| (dT,d) counts', dict(shapes))
print('   npz keys:', {m: sorted(raw(m, S[0][0], 'A', 20).keys()) for m in ('avici', 'cdfm', 'foundcause', 'pc')})
old = {m: json.load(open(OUT / f'e1_{m}.json', encoding='utf-8'))['summary'] for m in ('avici', 'cdfm', 'foundcause')}
for m in ('avici', 'cdfm', 'foundcause'):
    R = collections.defaultdict(list)
    for s, cidx, seed in S:
        t = target(s, cidx, seed); g = t['g']; dT = g.shape[0]; gt = (g + g.T) > 0; lin = CELLS[cidx][2] == 'lin'
        o0, o1 = raw(m, s, '-', 0), raw(m, s, 'A', 20)
        assert o0['probs'].shape == (dT, dT) and o1['probs'].shape == (dT + 20, dT + 20)
        p0, p1 = o0['probs'], o1['probs'][:dT, :dT]; off = ~np.eye(dT, dtype=bool)
        R['dp'].append(np.abs(p1 - p0)[off].mean())
        f0, f1 = und(p0), und(p1); iu = np.triu_indices(dT, 1)
        R['flipsF'].append((f0[iu] != f1[iu]).sum()); hF = F1(f0, gt) - F1(f1, gt); R['HF'].append(hF)
        if m == 'avici': n0, n1 = f0, f1
        else:
            a0, a1 = o0['adj_native'], o1['adj_native'][:dT, :dT]; n0, n1 = (a0 + a0.T) > 0, (a1 + a1.T) > 0
        R['flipsN'].append((n0[iu] != n1[iu]).sum()); hN = F1(n0, gt) - F1(n1, gt); R['HN'].append(hN); R['lin'].append(lin)
        an = o1['adj_native'] if m != 'avici' else (o1['probs'] > 0.5)
        R['X_native'].append(int(((an + an.T) > 0)[:dT, dT:].sum())); R['X_fixed'].append(int(und(o1['probs'])[:dT, dT:].sum()))
        R['E_native0'].append(int(n0[iu].sum())); R['E_native20'].append(int(n1[iu].sum())); R['E_true'].append(int(gt[iu].sum()))
        R['dAUPRC'].append(auprc(np.maximum(p0, p0.T), gt) - auprc(np.maximum(p1, p1.T), gt))   # POST HOC, threshold-free
        for alg in ('pc', 'ges'):
            k0, k1 = raw(alg, s, '-', 0)['skel'][:dT, :dT] > 0, raw(alg, s, 'A', 20)['skel'][:dT, :dT] > 0
            R[f'H_{alg}'].append(F1(k0, gt) - F1(k1, gt))
    A = {k: np.array(v, float) for k, v in R.items()}; L = A['lin'] > 0
    o = old[m]
    print(f'== {m}')
    print('  recomputed vs analyze_e1:  median dp', round(float(np.median(A['dp'])), 4), '/', round(o['SCORE_CHANGE']['median_dp'], 4),
          '| flipsF', A['flipsF'].mean(), '/', o['GRAPH_CHANGE_FIXED']['mean_flips'], '| flipsN', A['flipsN'].mean(), '/', o['GRAPH_CHANGE_NATIVE']['mean_flips'],
          '| H_F', round(A['HF'].mean(), 4), '/', round(o['H_fixed']['mean'], 4), '| H_N', round(A['HN'].mean(), 4), '/', round(o['H_native']['mean'], 4))
    bc = A['HN'][L].mean() - max(A['H_pc'][L].mean(), A['H_ges'][L].mean())
    print('  beyond-classical native (linear):', round(bc, 4), '/', round(o['BEYOND_CLASSICAL_H_native']['est'], 4))
    print('  POST HOC  share of systems with H_native > 0 / = 0 / < 0:', round((A['HN'] > 0).mean(), 2), round((A['HN'] == 0).mean(), 2), round((A['HN'] < 0).mean(), 2),
          '| median H_native', round(float(np.median(A['HN'])), 4), '| H_native linear', ci(A['HN'][L]), 'rff', ci(A['HN'][~L]))
    print('  POST HOC  AUPRC(k0) - AUPRC(k20), skeleton, threshold-free:', ci(A['dAUPRC']), '| linear', ci(A['dAUPRC'][L]), 'rff', ci(A['dAUPRC'][~L]))
    print('  POST HOC  cross edges target<->padding per system: native', round(A['X_native'].mean(), 2), 'fixed', round(A['X_fixed'].mean(), 2),
          '| target-block edges native k0 -> k20:', round(A['E_native0'].mean(), 1), '->', round(A['E_native20'].mean(), 1), '(true', round(A['E_true'].mean(), 1), ')')
# FoundCause: is ensemble-schedule noise able to produce a signed F1 shift? DEV, k=0, base 42 vs 1042
d = []
for s, cidx, seed in systems('DEV'):
    t = target(s, cidx, seed); gt = (t['g'] + t['g'].T) > 0
    a, b = raw('foundcause', s, '-', 0, 'sched42')['probs'], raw('foundcause', s, '-', 0, 'sched1042')['probs']
    d.append(F1(und(a), gt) - F1(und(b), gt))
print('== FoundCause POST HOC schedule noise in F1 (DEV, k0, base 42 minus base 1042): mean', round(float(np.mean(d)), 4), 'sd', round(float(np.std(d)), 4), 'range', round(min(d), 3), round(max(d), 3))
