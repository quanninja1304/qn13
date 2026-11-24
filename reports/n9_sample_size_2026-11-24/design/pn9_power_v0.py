"""P-N9 rules v0, section 5: power of the 11 Holm components at N = 120 (planning only; no model run).
Worst-case Holm threshold alpha = 0.05/11 for every component. SDs pooled within cells at n = 500 (Study 1 held-out;
Study 7 for SEA). Compound symmetry with correlation rho across n levels; Monte Carlo for the level-wise STABLE label.
usage: python -I -X utf8 pn9_power_v0.py
"""
import math

import numpy as np
from scipy import stats

rng = np.random.default_rng(20261125)
K = 11
A = 0.05 / K
Z1 = stats.norm.ppf(1 - A)          # one-sided component
Z2 = stats.norm.ppf(1 - A / 2)      # two-sided component (A2-diff)
N = 120
SD = {'avici': 0.0896, 'cdfm': 0.0774, 'foundcause': 0.0941, 'sea': 4.2279}
EFF = {'avici': 0.0681, 'cdfm': 0.0847, 'foundcause': 0.0929, 'sea': 5.8375}
GRID = {'cdfm': (100, 200, 500, 1000, 2000, 4000), 'foundcause': (125, 200, 500), 'sea': (500, 1000, 2000, 5000, 20000)}
MARGIN = {'cdfm': 0.05, 'foundcause': 0.05, 'sea': 1.0}
print(f'alpha per component = 0.05/{K} = {A:.5f}; one-sided z = {Z1:.3f}; two-sided z = {Z2:.3f}; N = {N}')

print('== persistence (A1 at n = 200, C1 at n = 4000, S1 at n = 20000): test > 0 and estimate >= margin,')
print('   if the effect equals its n = 500 value')
for m, key, marg in (('A1', 'avici', 0.05), ('C1', 'cdfm', 0.05), ('S1', 'sea', 1.0)):
    se = SD[key] / math.sqrt(N)
    print(f'  {m}: {stats.norm.cdf((EFF[key] - marg) / se) * stats.norm.cdf(EFF[key] / se - Z1):.2f}')

print('== A2-diff (two-sided, H(500) - H(200) = 0) and A2-sim (TOST inside +-0.05, true difference 0)')
for rho in (0.0, 0.5, 0.8):
    se = SD['avici'] * math.sqrt(2 * (1 - rho) / N)
    diff = '  '.join(f'|d|={d}: {stats.norm.cdf(d / se - Z2):.2f}' for d in (0.03, 0.05))
    sim = max(0.0, 2 * stats.norm.cdf(0.05 / se - Z1) - 1)
    print(f'  rho={rho}: A2-diff {diff} | A2-sim {sim:.2f}')


def trend(model, rho, shape, reps=20000):
    g = GRID[model]
    s, m = SD[model], MARGIN[model]
    x = np.log2(np.array(g, float))
    xc = x - x.mean()
    sxx = (xc ** 2).sum()
    span = x.max() - x.min()
    c = m / span
    a = g.index(500)
    L = len(g)
    if shape == 'flat':
        mu = np.zeros(L)
    else:  # 'decline': the n = 500 effect falls linearly in log2(n) to zero over the span
        mu = -EFF[model] * (x - x.min()) / span
    u = rng.normal(0, s * math.sqrt(rho), size=(reps, N, 1))
    e = rng.normal(0, s * math.sqrt(1 - rho), size=(reps, N, L))
    y = mu + u + e
    sl = (y * xc).sum(axis=2) / sxx
    b, sb = sl.mean(axis=1), sl.std(axis=1, ddof=1) / math.sqrt(N)
    shrinks = (b + Z1 * sb) < -c
    stable = np.ones(reps, bool)
    for l in range(L):
        if l == a:
            continue
        d = y[:, :, l] - y[:, :, a]
        dm, ds = d.mean(axis=1), d.std(axis=1, ddof=1) / math.sqrt(N)
        stable &= (dm + Z1 * ds < m) & (dm - Z1 * ds > -m)
    return shrinks.mean(), stable.mean(), c


print('== trend components: P(SHRINKS rejected), P(STABLE rejected)')
for model in ('cdfm', 'foundcause', 'sea'):
    for shape in ('flat', 'decline'):
        parts = []
        for rho in (0.0, 0.5, 0.8):
            p_sh, p_st, c = trend(model, rho, shape)
            parts.append(f'rho={rho}: SHRINKS {p_sh:.2f}, STABLE {p_st:.2f}')
        print(f'  {model:<10} true={shape:<7} c={c:.4f}/doubling: ' + ' | '.join(parts))
