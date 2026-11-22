"""Independent re-computation of the eight P-N5 hypotheses from raw outputs (does not import the frozen P-N5 code).
Definitions follow PN5 rules v1 §4-§5. Compares with pn5_reading.json. Prints numbers only; writes nothing.
usage: python -I recheck_pn5.py <pn5_out dir>
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats

OUT = Path(sys.argv[1])
DT, R = 11, 20
IU = np.triu_indices(DT, 1)


def load(alg, key):
    z = np.load(OUT / alg / f'{key}.npz', allow_pickle=False)
    return {n: z[n] for n in z.files}


def skel(alg, o):
    if alg == 'avici':
        p = o['probs'][:DT, :DT]
        s = np.maximum(p, p.T) > 0.5
    elif alg == 'cdfm':
        a = o['adj_native'][:DT, :DT] != 0
        s = a | a.T
    else:
        g = o['skel'][:DT, :DT] != 0
        s = g | g.T
    return s[IU]


def key(t, c, r=None):
    return f'{t}__{c}' if r is None else f'{t}__{c}__r{r:02d}'


def flips(alg, t, c, r):
    return int((skel(alg, load(alg, key(t, c, r))) != skel(alg, load(alg, key(t, 'k0')))).sum())


rd = json.loads((OUT / 'pn5_reading.json').read_text())
H = {}
for t, L in (('sachs', 'S'), ('wine', 'W')):
    for alg, A in (('avici', 'A'), ('cdfm', 'C')):
        v = [flips(alg, t, 'k20_e0', r) - max(flips('pc', t, 'k20_e0', r), flips('ges', t, 'k20_e0', r)) for r in range(R)]
        H[f'P5-1{L}-{A}'] = np.array(v, float)
    for k in (20, 40):
        v = [float(load('cdfm', key(t, f'k{k}_e2', r))['threshold']) - float(load('cdfm', key(t, f'k{k}_e0', r))['threshold'])
             for r in range(R)]
        H[f'P5-2{L}-{k}'] = np.array(v, float)

pv = {}
for h, v in H.items():
    res = stats.ttest_1samp(v, 0.0, alternative='greater')
    pv[h] = float(res.pvalue)
    ref = rd['hypotheses'][h]
    print(f'{h}: mean {v.mean():+.6f} (reading {ref["mean"]:+.6f}) t {res.statistic:.6f} (reading {ref["t"]:.6f}) '
          f'p {res.pvalue:.4g} (reading {ref["p_one_sided"]:.4g}) values_equal {np.allclose(v, ref["values"], rtol=0, atol=1e-12)} '
          f'+/0/- {int((v > 0).sum())}/{int((v == 0).sum())}/{int((v < 0).sum())}')

order = sorted(pv, key=pv.get)
alive = True
for i, h in enumerate(order):
    thr = 0.05 / (len(order) - i)
    rej = alive and pv[h] <= thr
    alive = rej
    print(f'Holm #{i + 1} {h} p {pv[h]:.3g} thr {thr:.5f} -> {"CONFIRMED" if rej else "NOT_CONFIRMED"} (reading {rd["hypotheses"][h]["label"]})')

for t in ('sachs', 'wine'):
    m0 = {a: int(skel(a, load(a, key(t, 'k0'))).sum()) for a in ('avici', 'cdfm', 'pc', 'ges')}
    same = {a: all(np.array_equal(load(a, key(t, 'k0'))[n], load(a, key(t, 'k0') + '__rep')[n])
                   for n in load(a, key(t, 'k0')) if n != 'meta') for a in ('avici', 'cdfm', 'pc', 'ges')}
    thr0 = float(load('cdfm', key(t, 'k0'))['threshold'])
    print(t, 'm0', m0, 'reading', {a: rd['context'][t][a]['m0'] for a in m0}, 'thr0', round(thr0, 6), 'k0 rerun identical', same)
