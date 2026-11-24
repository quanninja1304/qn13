"""P-N9 design inputs: how many sample sizes n, which ones, and how many systems (read-only; no model is run).

Sources, all saved before this script was written:
  - Study 1 held-out rows (P-N1): artifacts/n1_runs/pn1_out/held_{avici,cdfm,foundcause}.json, n = 500;
  - Study 7 rows (P-N8): reports/n8_sea_model_coverage_2026-11-23/checks/pn8_reading.json, n = 500;
  - console logs with per-call run times: artifacts/n1_runs/pn1_out/held_console.log, artifacts/n8_runs/pn8_out/pn8_console.log.
Prints:
  1. per-system means and SDs (pooled within the 8 design cells) of the quantities the figure would plot;
  2. proxies for the correlation of per-system effects across conditions (the correlation across n is unknown);
  3. CI half-widths of a cell-balanced mean by number of systems;
  4. for candidate n grids: SE of the mean per-system slope over log2(n) (compound symmetry with correlation rho),
     power of the labels SHRINKS and STABLE, and the minimal detectable slope;
  5. power of the AVICI contrast H(500) - H(200) and of the persistence rule at one n;
  6. per-call run times at n = 500 and machine-time estimates for the proposed grid (scaling in n is an assumption).
Planning alpha: one-sided 0.05/8 (Holm, worst case over a family of 8).
usage: python -I -X utf8 pn9_n_grid_design.py <repo root>
"""
import json
import math
import re
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

root = Path(sys.argv[1])
held = {m: json.loads((root / 'artifacts' / 'n1_runs' / 'pn1_out' / f'held_{m}.json').read_text())
        for m in ('avici', 'cdfm', 'foundcause')}
pn8 = json.loads((root / 'reports' / 'n8_sea_model_coverage_2026-11-23' / 'checks' / 'pn8_reading.json').read_text())
ALPHA = 0.05 / 8
Z1 = stats.norm.ppf(1 - ALPHA)          # one-sided
Z2 = stats.norm.ppf(1 - ALPHA / 2)      # two-sided
Z80 = stats.norm.ppf(0.8)


def pooled_within(values, cells):
    values, cells = np.asarray(values, float), np.array([str(c) for c in cells])
    ss = df = 0
    for c in np.unique(cells):
        v = values[cells == c]
        if len(v) > 1:
            ss += ((v - v.mean()) ** 2).sum()
            df += len(v) - 1
    return math.sqrt(ss / df)


def describe(label, values, cells):
    v = np.asarray(values, float)
    sw = pooled_within(v, cells)
    print(f'  {label:<44} n={len(v):>3}  mean={v.mean():+.4f}  sd={v.std(ddof=1):.4f}  sd_within_cell={sw:.4f}')
    return float(v.mean()), sw


print('== 1. Per-system quantities at n = 500 (Gaussian padding, k = 20, NATIVE decoder)')
P = {}
for m, d in held.items():
    rows = d['rows']
    cells = [r['cell'] for r in rows]
    lin = [r for r in rows if r['lin']]
    print(f'-- {m} (Study 1 held-out)')
    P[m] = {'H': describe('H = F1(k0) - F1(k20)', [r['A20']['H_native'] for r in rows], cells),
            'flips': describe('flips (target pairs changed)', [r['A20']['flips_native'] for r in rows], cells),
            'beyond': describe('H - max(H_PC, H_GES), linear systems',
                               [r['A20']['H_native'] - max(r['A20']['H_pc'], r['A20']['H_ges']) for r in lin],
                               [r['cell'] for r in lin])}
    if m == 'avici':
        print('-- PC and GES, linear systems of the same held-out set')
        for alg in ('pc', 'ges'):
            describe(f'{alg.upper()} H', [r['A20'][f'H_{alg}'] for r in lin], [r['cell'] for r in lin])
            describe(f'{alg.upper()} flips', [r['A20'][f'flips_{alg}'] for r in lin], [r['cell'] for r in lin])
ra = pn8['rows_A']
c7 = [r['ci'] for r in ra]
print('-- sea (Study 7)')
P['sea'] = {'delta': describe('Delta, Gaussian padding (pairs)', [r['delta_A20_nat'] for r in ra], c7),
            'H': describe('H = F1(k0) - F1(k20), Gaussian padding', [r['H_nat'] for r in ra], c7)}

print('== 2. Proxies for the correlation of per-system effects across conditions (all at n = 500)')
cd = held['cdfm']['rows']
for a, b in (('A10', 'A20'), ('A20', 'A30'), ('A20', 'B20')):
    print(f'  CDFM       corr(H at {a}, H at {b}) = '
          f'{np.corrcoef([r[a]["H_native"] for r in cd], [r[b]["H_native"] for r in cd])[0, 1]:+.3f}')
for m in ('avici', 'foundcause'):
    rows = held[m]['rows']
    print(f'  {m:<10} corr(H at A20, H at B20) = '
          f'{np.corrcoef([r["A20"]["H_native"] for r in rows], [r["B20"]["H_native"] for r in rows])[0, 1]:+.3f}')
print(f'  SEA        corr(Delta at A20, Delta at S20) = '
      f'{np.corrcoef([r["delta_A20_nat"] for r in ra], [r["delta_S20_nat"] for r in ra])[0, 1]:+.3f}')

print('== 3. CI half-width, 1.96 * sd_within / sqrt(N), of a cell-balanced mean')
NS = (24, 40, 80, 120)
print('  ' + f'{"quantity":<24}' + ''.join(f'N={N:<8}' for N in NS))
for m, q in (('avici', 'H'), ('cdfm', 'H'), ('foundcause', 'H'), ('sea', 'H'), ('sea', 'delta'),
             ('avici', 'beyond'), ('cdfm', 'beyond'), ('foundcause', 'beyond')):
    s = P[m][q][1]
    frac = 0.5 if q == 'beyond' else 1.0   # linear half of the systems
    print('  ' + f'{m + " " + q:<24}' + ''.join(f'{1.96 * s / math.sqrt(N * frac):<10.4f}' for N in NS))

print('== 4. Trend over log2(n): mean per-system OLS slope, SE = s * sqrt((1 - rho) / (Sxx * N))')
print('   SHRINKS: upper bound < -m, power when the n = 500 effect falls to zero over the span;')
print('   STABLE: two-sided interval inside (-m, +m), power when the true slope is 0; m = margin / span.')
GRIDS = {'avici': [(100, 200, 500, 1000)],
         'cdfm': [(500, 4000), (500, 1000, 2000, 4000), (100, 200, 500, 1000, 2000, 4000)],
         'foundcause': [(125, 500), (125, 200, 500)],
         'sea': [(500, 20000), (500, 2000, 20000), (500, 1000, 2000, 5000, 20000)]}
for m, grids in GRIDS.items():
    q = 'delta' if m == 'sea' else 'H'
    eff, s = P[m][q]
    margin = 1.0 if m == 'sea' else 0.05          # practical margins of the earlier studies
    for g in grids:
        x = np.log2(np.array(g, float))
        sxx, span = float(((x - x.mean()) ** 2).sum()), float(x.max() - x.min())
        mpd, decline = margin / span, -eff / span
        print(f'  {m:<10} grid={str(g):<36} L={len(g)}  Sxx={sxx:5.2f}  span={span:.2f} doublings  '
              f'm={mpd:.4f}/doubling  full decline={decline:+.4f}/doubling')
        for N in (40, 80, 120):
            cells = []
            for rho in (0.0, 0.5, 0.8):
                se = s * math.sqrt((1 - rho) / (sxx * N))
                p_sh = stats.norm.cdf((-decline - mpd) / se - Z1) if -decline > mpd else 0.0
                p_st = max(0.0, 2 * stats.norm.cdf(mpd / se - Z1) - 1)
                cells.append(f'rho={rho}: SE={se:.4f} P(SHRINKS)={p_sh:.2f} P(STABLE)={p_st:.2f} MDS={(Z1 + Z80) * se:.4f}')
            print(f'      N={N:<4}' + ' | '.join(cells))

print('== 5a. AVICI contrast H(500) - H(200), two-sided, SE = s * sqrt(2 (1 - rho) / N)')
s = P['avici']['H'][1]
for N in (40, 80, 120):
    print(f'  N={N:<4}' + ' | '.join(
        f'rho={rho}: ' + ' '.join(f'P(|d|={d})={stats.norm.cdf(d / (s * math.sqrt(2 * (1 - rho) / N)) - Z2):.2f}'
                                  for d in (0.03, 0.05)) for rho in (0.0, 0.5, 0.8)))
print('== 5b. Persistence rule at one n (estimate >= 0.05 and one-sided test > 0), if the effect equals its n = 500 value')
for m in ('avici', 'cdfm', 'foundcause'):
    eff, s = P[m]['H']
    print(f'  {m:<10}' + '  '.join(
        f'N={N}: {stats.norm.cdf((eff - 0.05) / (s / math.sqrt(N))) * stats.norm.cdf(eff / (s / math.sqrt(N)) - Z1):.2f}'
        for N in (40, 80, 120)))
eff, s = P['sea']['delta']
print(f'  {"sea Delta":<10}' + '  '.join(
    f'N={N}: {stats.norm.cdf((eff - 1.0) / (s / math.sqrt(N))) * stats.norm.cdf(eff / (s / math.sqrt(N)) - Z1):.2f}'
    for N in (40, 80, 120)))

print('== 6. Per-call run times at n = 500 (console logs) and machine-time estimates')
rx = re.compile(r'^\[(\d+)/(\d+)\]\s+(\S+)\s+d=(\d+)\s+([\d.]+)s ok')
times, sec = defaultdict(list), None
for raw in open(root / 'artifacts' / 'n1_runs' / 'pn1_out' / 'held_console.log', encoding='utf-8-sig', errors='replace'):
    if raw.startswith('=== '):
        sec = raw.split()[1]
        continue
    mt = rx.match(raw.strip())
    if mt and sec:
        times[(sec, 'k0' if '__k0__' in mt.group(3) else 'pad', int(mt.group(4)))].append(float(mt.group(5)))
for key in sorted(times):
    print(f'  {key[0]:<10} {key[1]:<4} d={key[2]:<3} median={st.median(times[key]):7.1f} s  mean={st.mean(times[key]):7.1f} s  calls={len(times[key])}')
sea_t = [float(x) for x in re.findall(r'([\d.]+)s ok', (root / 'artifacts' / 'n8_runs' / 'pn8_out' / 'pn8_console.log')
                                       .read_text(encoding='utf-8-sig', errors='replace'))]
print(f'  SEA        all  median={st.median(sea_t):.1f} s  mean={st.mean(sea_t):.1f} s  calls={len(sea_t)}')


def per_system(model):
    """Mean seconds for one k0 call plus one padded call at n = 500, averaged over d_T = 10 and 20."""
    k0 = st.mean([st.mean(times[(model, 'k0', d)]) for d in (10, 20)])
    pad = st.mean([st.mean(times[(model, 'pad', d)]) for d in (30, 40)])
    return k0 + pad


N = 80
scal = {'avici': lambda n: 0.5 * n / 500 + 0.5 * (n / 500) ** 2,   # assumed: half linear (MLP), half quadratic (row attention)
        'cdfm': lambda n: n / 500,                                 # assumed: induced attention, linear in n
        'foundcause': lambda n: 1.0,                               # assumed upper bound for n <= 500
        'ges': lambda n: n / 500}                                  # assumed linear in n
plan = {'avici': (100, 200, 500, 1000), 'cdfm': (100, 200, 500, 1000, 2000, 4000), 'foundcause': (125, 200, 500),
        'ges': (100, 125, 200, 500, 1000, 2000, 4000)}
names = {'avici': 'AVICI', 'cdfm': 'CDFM', 'foundcause': 'FoundCause', 'ges': 'GES'}
total = 0.0
for m, grid in plan.items():
    sec_sys = per_system(names[m]) * sum(scal[m](n) for n in grid)
    hours = sec_sys * N / 3600
    total += hours
    print(f'  estimate {names[m]:<10} grid={str(grid):<36} {sec_sys / 60:6.1f} min per system  -> {hours:6.1f} h for N={N}')
sea_levels, sea_calls = (500, 1000, 2000, 5000, 20000), 7   # k0 at 5 seeds, Gaussian and structured padding at seed a
h_sea = st.mean(sea_t) * sea_calls * len(sea_levels) * N / 3600
total += h_sea
print(f'  estimate SEA        grid={str(sea_levels):<36} {st.mean(sea_t) * sea_calls * len(sea_levels) / 60:6.1f} min per system  '
      f'-> {h_sea:6.1f} h for N={N} (assumed constant in n: FCI runs on 500-row batches)')
print(f'  estimate total (PC not included; FoundCause upper bound; GES at 5000 and 20000 not included): {total:.1f} h')
