"""P-N2 screening-only variants (rules v1 §8.2-§8.3): no model is rerun.

For every system and input of a set, at the locked alpha (pn2_out/alpha.json):
  primary test of the family (Fisher-z linear, HSIC RFF), HSIC on both families (family-agnostic variant, alpha_HSIC),
  Spearman on RFF (alpha_HSIC), and BH at q = alpha of the corresponding test.
usage: screen_variants.py <DEV2|EXP2>  ->  pn2_out/<set>_screen_variants.json
"""
import os, sys, json, time
if os.name == 'nt':   # keep the system awake while this process runs (DEV2: one job slept 7.15 h); no effect on results
    import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
import numpy as np
from common2 import *
from screen import *

SET = sys.argv[1]
alpha = json.loads((OUT2 / 'alpha.json').read_text())
rows = []
t0 = time.time()
for sid, ci, seed in systems2(SET):
    dT, eT, mech = CELLS[ci]
    for cond in CONDS:
        X, t, _ = assemble2(sid, ci, seed, cond)
        p = {'hsic': pvalues(X, 'hsic')}
        if mech == 'lin':
            p['fisherz'] = pvalues(X, 'fisherz')
            variants = [('primary', 'fisherz', alpha['fisherz'], 'bonferroni'), ('hsic_agnostic', 'hsic', alpha['hsic'], 'bonferroni'),
                        ('bh_primary', 'fisherz', alpha['fisherz'], 'bh')]
        else:
            p['spearman'] = pvalues(X, 'spearman')
            variants = [('primary', 'hsic', alpha['hsic'], 'bonferroni'), ('hsic_agnostic', 'hsic', alpha['hsic'], 'bonferroni'),
                        ('spearman', 'spearman', alpha['hsic'], 'bonferroni'), ('bh_primary', 'hsic', alpha['hsic'], 'bh')]
        for name, test, al, meth in variants:
            R = reject_bonferroni(p[test], al) if meth == 'bonferroni' else reject_bh(p[test], al)
            sm = screen_metrics(components(R), R, dT, t['g'])
            rows.append(dict(sys=sid, fam=mech, dT=dT, cond=cond, variant=name, test=test, alpha=al, method=meth, **sm))
summary = {}
for fam in ('lin', 'rff'):
    for name in sorted({r['variant'] for r in rows if r['fam'] == fam}):
        for cond in CONDS:
            R_ = [r for r in rows if r['fam'] == fam and r['variant'] == name and r['cond'] == cond]
            summary[f'{fam}|{name}|{cond}'] = dict(
                n=len(R_), mean_merged_frac=float(np.mean([r['merged'] / r['k'] if r['k'] else 0.0 for r in R_])),
                mean_split_frac=float(np.mean([r['split'] / r['n_true_edges'] for r in R_])),
                mean_false_cross=float(np.mean([r['false_cross'] for r in R_])),
                frac_inputs_any_false_cross=float(np.mean([r['false_cross'] > 0 for r in R_])),
                mean_target_components=float(np.mean([r['n_target_components'] for r in R_])))
(OUT2 / f'{SET.lower()}_screen_variants.json').write_text(json.dumps(dict(set=SET, alpha=alpha, summary=summary, rows=rows,
                                                                         wall_seconds=round(time.time() - t0, 1)), indent=1))
print('done', SET, len(rows), 'rows', round(time.time() - t0, 1), 's')
