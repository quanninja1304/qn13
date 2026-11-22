"""Independent re-computation of the two P-N7 hypotheses from raw outputs.

Written on 23 Nov 2026, before any P-N7 main-run output was read. It does not import the frozen P-N7, P-N5 or P-N1
code (analyze7, stats7, common7, common5, metrics). Definitions follow PN7 rules v1 §2-§5:
- NATIVE skeleton of FoundCause: `adj_native` OR its transpose, on the 55 pairs of the 11 real variables;
- PC/GES skeleton: the saved `skel` matrix OR its transpose (P-N5 outputs);
- flips: pairs whose skeleton state differs from k0; D_r = flips_FC,r - max(flips_PC,r, flips_GES,r) at k20_e0;
- test: one-sided one-sample t over the 20 draws (df 19), SE = 0 -> DEGENERATE with p = 1; Holm 0.05 over the two.
Also checks: output count, input hashes against Study 4's input hashes, k0 rerun bitwise, adapter at base 42 within
1e-6, and the descriptive quantities (m0, dm, dp, schedule reference). Prints numbers and match flags; writes nothing.

usage: python -I recheck_pn7.py <pn7_out dir> <pn5_out dir> <inputs5.json> [--dev]
--dev: smoke test of the code paths on the development outputs (stand-in table, 2 draws, base 1042; no reading file).
       Prints check flags only; values are suppressed, as in gate G7 of the rules.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

OUT7, OUT5, INPUTS5 = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
DEV = '--dev' in sys.argv[4:]
DT, TOL = 11, 1e-6
R, BASES = (2, (1042,)) if DEV else (20, (1042, 2042, 3042, 4042))
TABLES = (('standin', 'P7-1X'),) if DEV else (('sachs', 'P7-1S'), ('wine', 'P7-1W'))
UPPER = np.triu_indices(DT, 1)
inputs5 = json.loads(INPUTS5.read_text(encoding='utf-8'))


def npz(path):
    with np.load(path, allow_pickle=False) as z:
        return {n: z[n] for n in z.files}


def fc(table, cond, variant, r=None):
    base = f'{table}__{cond}' if r is None else f'{table}__{cond}__r{r:02d}'
    return npz(OUT7 / 'foundcause' / f'{base}__{variant}.npz'), base


def p5(alg, table, cond, r=None):
    base = f'{table}__{cond}' if r is None else f'{table}__{cond}__r{r:02d}'
    return npz(OUT5 / alg / f'{base}.npz')


def sk_fc(o):
    a = np.asarray(o['adj_native'])[:DT, :DT] != 0
    return (a | a.T)[UPPER]


def sk_classical(o):
    g = np.asarray(o['skel'])[:DT, :DT] != 0
    return (g | g.T)[UPPER]


def n_diff(a, b):
    return int(np.count_nonzero(a != b))


def mean_abs_offdiag(p1, p0):
    a, b = np.asarray(p1, float)[:DT, :DT], np.asarray(p0, float)[:DT, :DT]
    mask = ~np.eye(DT, dtype=bool)
    return float(np.mean(np.abs(a - b)[mask]))


def meta(o):
    return json.loads(str(o['meta']))


reading_path = OUT7 / 'pn7_reading.json'
reading = json.loads(reading_path.read_text(encoding='utf-8')) if (reading_path.exists() and not DEV) else None
n_files = sum(len(list((OUT7 / 'foundcause').glob(f'{t}__*.npz'))) for t, _ in TABLES)
print(f'FoundCause output files on the tables read: {n_files} (expected {len(TABLES) * (3 + R + len(BASES))})')

pvals, summary = {}, {}
for table, hname in TABLES:
    k0, k0key = fc(table, 'k0', 'api')
    rep, _ = fc(table, 'k0', 'rep')
    s42, _ = fc(table, 'k0', 'sched42')
    arrays = [n for n in k0 if n != 'meta']
    rerun_ok = all(np.array_equal(k0[n], rep[n]) for n in arrays)
    adapter_dev = max(float(np.max(np.abs(np.asarray(k0[n], float) - np.asarray(s42[n], float))))
                      for n in ('probs', 'agreement', 'adj_native'))
    hash_ok = [meta(k0)['input_sha'] == inputs5.get(k0key)]
    s0 = sk_fc(k0)
    pc0, ges0 = sk_classical(p5('pc', table, 'k0')), sk_classical(p5('ges', table, 'k0'))
    flips_fc, flips_max, contrast, dm, dp = [], [], [], [], []
    for r in range(R):
        o, key = fc(table, 'k20_e0', 'api', r)
        hash_ok.append(meta(o)['input_sha'] == inputs5.get(key))
        f_fc = n_diff(sk_fc(o), s0)
        f_pc = n_diff(sk_classical(p5('pc', table, 'k20_e0', r)), pc0)
        f_ges = n_diff(sk_classical(p5('ges', table, 'k20_e0', r)), ges0)
        flips_fc.append(f_fc)
        flips_max.append(max(f_pc, f_ges))
        contrast.append(f_fc - max(f_pc, f_ges))
        dm.append(int(sk_fc(o).sum()) - int(s0.sum()))
        dp.append(mean_abs_offdiag(o['probs'], k0['probs']))
    sched = {b: n_diff(sk_fc(fc(table, 'k0', f'sched{b}')[0]), s0) for b in BASES}
    x = np.asarray(contrast, float)
    sd = float(np.std(x, ddof=1))
    if sd == 0.0:
        p, tstat, degenerate = 1.0, None, True
    else:
        res = stats.ttest_1samp(x, 0.0, alternative='greater')
        p, tstat, degenerate = float(res.pvalue), float(res.statistic), False
    half = float(stats.t.ppf(0.975, R - 1) * sd / np.sqrt(R))
    pvals[hname] = p
    summary[hname] = dict(table=table, mean=float(x.mean()), ci=(float(x.mean()) - half, float(x.mean()) + half), t=tstat,
                          p=p, degenerate=degenerate, values=contrast)
    print(f'\n[{table}] input hashes match Study 4: {all(hash_ok)} ({sum(hash_ok)}/{len(hash_ok)}); '
          f'k0 rerun bitwise: {rerun_ok}; adapter at base 42 max deviation {adapter_dev:.3g} (<= {TOL}: {adapter_dev <= TOL})')
    if DEV:
        print(f'  [dev] computed: {len(flips_fc)} draws, contrast, t test, schedule reference ({len(sched)} base); values suppressed')
        continue
    print(f'  m0 {int(s0.sum())}; flips FC mean {np.mean(flips_fc):.2f} [min {min(flips_fc)}, max {max(flips_fc)}]; '
          f'max(PC, GES) mean {np.mean(flips_max):.2f}; dm mean {np.mean(dm):+.2f}; dp mean {np.mean(dp):.4f}')
    print(f'  contrast D_r: mean {x.mean():+.4f} CI95 [{x.mean() - half:+.4f}, {x.mean() + half:+.4f}] '
          f"t {tstat if tstat is None else round(tstat, 4)} p {p:.4g} degenerate {degenerate}; +/0/- "
          f'{int((x > 0).sum())}/{int((x == 0).sum())}/{int((x < 0).sum())}')
    sv = list(sched.values())
    print(f'  schedule reference at k0 (flips vs base 42): {sched}; mean {np.mean(sv):.2f}; max {max(sv)}')
    if reading is not None:
        ref = reading['hypotheses'][hname]
        tr = reading['tables'][table]
        print(f'  vs reading: values equal {list(map(int, contrast)) == list(map(int, tr["contrast_values"]))}; '
              f'mean {abs(ref["mean"] - x.mean()) <= 1e-12}; p {abs(ref["p"] - p) <= 1e-12 * max(1.0, p)}; '
              f'schedule {all(int(tr["schedule_reference"]["values"][str(b)]) == sched[b] for b in BASES)}; '
              f'm0 {tr["m0_fc"] == int(s0.sum())}')

print('\nHolm 0.05 over the two hypotheses (step-down):')
remaining = sorted(pvals.items(), key=lambda kv: kv[1])
still = True
for i, (h, p) in enumerate(remaining):
    level = 0.05 / (len(remaining) - i)
    ok = still and p <= level and not summary[h]['degenerate']
    if not ok:
        still = False
    label = 'CONFIRMED' if ok else 'NOT_CONFIRMED'
    extra = f" (reading: {reading['hypotheses'][h]['label']})" if reading is not None else ''
    print(f'  {h}: Holm step computed; values suppressed' if DEV else f'  {h}: p {p:.4g} vs {level:.4f} -> {label}{extra}')
