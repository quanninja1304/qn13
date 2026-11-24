"""Checks for the user's N = 120 argument (planning only; SDs from the saved Study 1 / Study 7 outputs at n = 500).
1. Persistence under two readings: the Study 1 rule (estimate >= 0.05 and one-sided test > 0) versus
   'whole CI above 0.05' (lower bound > 0.05), at N = 80 and 120, if the true effect equals its n = 500 value.
2. Equivalence labels by Monte Carlo under compound symmetry with correlation rho across n levels:
   (a) slope-based STABLE (interval of the mean per-system slope over log2 n inside +-margin/span);
   (b) level-wise STABLE: every level's contrast with the anchor n = 500 inside +-margin (intersection-union, TOST);
   (c) the same two rules when the true curve is U-shaped with zero mean slope (does STABLE wrongly pass?);
   (d) AVICI SIMILAR: TOST of H(500) - H(200) inside +-0.05.
usage: python -I -X utf8 pn9_n120_check.py
"""
import math

import numpy as np
from scipy import stats

rng = np.random.default_rng(20261125)
ALPHA = 0.05 / 8
Z1 = stats.norm.ppf(1 - ALPHA)
SD = {'avici': 0.0896, 'cdfm': 0.0774, 'foundcause': 0.0941, 'sea_delta': 4.2279}
EFF = {'avici': 0.0681, 'cdfm': 0.0847, 'foundcause': 0.0929, 'sea_delta': 5.8375}

print('== 1. Persistence at one n if the effect equals its n = 500 value')
for m in ('avici', 'cdfm', 'foundcause'):
    for N in (80, 120):
        se = SD[m] / math.sqrt(N)
        rule1 = stats.norm.cdf((EFF[m] - 0.05) / se) * stats.norm.cdf(EFF[m] / se - Z1)
        lb196 = stats.norm.cdf((EFF[m] - 0.05) / se - 1.96)
        lbholm = stats.norm.cdf((EFF[m] - 0.05) / se - Z1)
        print(f'  {m:<10} N={N}: Study 1 rule {rule1:.2f} | lower 95% bound > 0.05: {lb196:.2f} | '
              f'lower bound > 0.05 at the Holm level: {lbholm:.2f}')


def sim(model, grid, anchor, N, rho, margin, shape='flat', reps=20000):
    s = SD[model]
    L = len(grid)
    x = np.log2(np.array(grid, float))
    xc = x - x.mean()
    sxx = (xc ** 2).sum()
    a = grid.index(anchor)
    mu = np.zeros(L)
    if shape == 'U':   # U-shape with zero mean slope over the grid: amplitude = margin at the ends
        q = (x - x.mean()) ** 2
        q = q - q.mean()
        mu = margin * q / np.abs(q).max()
    # per-system values: mu + u_i + e_il
    u = rng.normal(0, s * math.sqrt(rho), size=(reps, N, 1))
    e = rng.normal(0, s * math.sqrt(1 - rho), size=(reps, N, L))
    y = mu + u + e
    slope = (y * xc).sum(axis=2) / sxx                    # per-system OLS slope
    b, sb = slope.mean(axis=1), slope.std(axis=1, ddof=1) / math.sqrt(N)
    m_slope = margin / (x.max() - x.min())
    st_slope = (b + Z1 * sb < m_slope) & (b - Z1 * sb > -m_slope)
    ok = np.ones(reps, bool)
    for l in range(L):
        if l == a:
            continue
        d = y[:, :, l] - y[:, :, a]
        dm, ds = d.mean(axis=1), d.std(axis=1, ddof=1) / math.sqrt(N)
        ok &= (dm + Z1 * ds < margin) & (dm - Z1 * ds > -margin)
    return st_slope.mean(), ok.mean()


print('== 2. STABLE labels by simulation (true curve flat, or U-shaped with zero mean slope)')
cases = [('cdfm', (100, 200, 500, 1000, 2000, 4000), 500, 0.05),
         ('foundcause', (125, 200, 500), 500, 0.05),
         ('sea_delta', (500, 1000, 2000, 5000, 20000), 500, 1.0)]
for model, grid, anchor, margin in cases:
    for shape in ('flat', 'U'):
        for N in (80, 120):
            parts = []
            for rho in (0.0, 0.5, 0.8):
                p_slope, p_level = sim(model, grid, anchor, N, rho, margin, shape)
                parts.append(f'rho={rho}: slope-STABLE {p_slope:.2f}, level-STABLE {p_level:.2f}')
            print(f'  {model:<10} {shape:<4} N={N}: ' + ' | '.join(parts))

print('== 2d. AVICI SIMILAR: TOST of H(500) - H(200) inside +-0.05 (true difference 0)')
for N in (80, 120):
    parts = []
    for rho in (0.0, 0.5, 0.8):
        se = SD['avici'] * math.sqrt(2 * (1 - rho) / N)
        parts.append(f'rho={rho}: {max(0.0, 2 * stats.norm.cdf(0.05 / se - Z1) - 1):.2f}')
    print(f'  N={N}: ' + ' | '.join(parts))

print('== 3. Per-cell CI half-width of H (1.96 * sd_within / sqrt(n per cell))')
for m in ('avici', 'cdfm', 'foundcause'):
    print(f'  {m:<10} 10 per cell: +-{1.96 * SD[m] / math.sqrt(10):.3f} | 15 per cell: +-{1.96 * SD[m] / math.sqrt(15):.3f}')
