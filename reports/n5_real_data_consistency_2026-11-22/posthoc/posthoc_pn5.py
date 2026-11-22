"""Post-hoc checks for P-N5 (outside the locked rules; not a basis for any CONFIRMED label).
(1) exact one-sided sign test (zeros dropped) on the per-draw values of the eight hypotheses, with Holm;
(2) AVICI target-skeleton size: per-draw m(structured) - m(Gaussian) at k = 20 and 40, and the number of draws with m = 0;
(3) CDFM NATIVE target-skeleton size per condition.
usage: python -I posthoc_pn5.py <pn5_out dir>
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats

OUT = Path(sys.argv[1])
DT, R = 11, 20
IU = np.triu_indices(DT, 1)
rd = json.loads((OUT / 'pn5_reading.json').read_text())

print('(1) exact sign test, one-sided, zeros dropped')
pv = {}
for h, x in rd['hypotheses'].items():
    v = np.asarray(x['values'], float)
    pos, neg = int((v > 0).sum()), int((v < 0).sum())
    p = stats.binomtest(pos, pos + neg, 0.5, alternative='greater').pvalue if pos + neg else 1.0
    pv[h] = float(p)
    print(f'  {h}: +{pos} -{neg} 0:{R - pos - neg} p = {p:.3g}')
alive = True
for i, h in enumerate(sorted(pv, key=pv.get)):
    thr = 0.05 / (len(pv) - i)
    rej = alive and pv[h] <= thr
    alive = rej
    print(f'  Holm #{i + 1} {h} p {pv[h]:.3g} thr {thr:.5f} {"reject" if rej else "keep"} (locked t-test label: {rd["hypotheses"][h]["label"]})')


def skel(alg, key):
    z = np.load(OUT / alg / f'{key}.npz', allow_pickle=False)
    if alg == 'avici':
        p = z['probs'][:DT, :DT]
        s = np.maximum(p, p.T) > 0.5
    else:
        a = z['adj_native'][:DT, :DT] != 0
        s = a | a.T
    return s[IU]


for alg in ('avici', 'cdfm'):
    print(f'({2 if alg == "avici" else 3}) {alg} NATIVE target-skeleton size m')
    for t in ('sachs', 'wine'):
        m0 = int(skel(alg, f'{t}__k0').sum())
        M = {c: np.array([skel(alg, f'{t}__{c}__r{r:02d}').sum() for r in range(R)], float)
             for c in ('k20_e0', 'k20_e2', 'k40_e0', 'k40_e2')}
        line = ', '.join(f'{c} mean {M[c].mean():.2f} [min {M[c].min():.0f}, max {M[c].max():.0f}] m=0 in {int((M[c] == 0).sum())}'
                         for c in M)
        print(f'  {t}: m0 {m0}; {line}')
        for k in (20, 40):
            d = M[f'k{k}_e2'] - M[f'k{k}_e0']
            se = d.std(ddof=1) / np.sqrt(R)
            q = stats.t.ppf(0.975, R - 1)
            print(f'    m(structured) - m(Gaussian), k = {k}: mean {d.mean():+.2f} CI95_t [{d.mean() - q * se:+.2f}, {d.mean() + q * se:+.2f}] '
                  f'+/0/- {int((d > 0).sum())}/{int((d == 0).sum())}/{int((d < 0).sum())}')
