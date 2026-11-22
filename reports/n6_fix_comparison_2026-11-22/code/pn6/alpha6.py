"""P-N6 choice of alpha_L and alpha_H on DEV6 (rules PN6 v1 §3, gate G3). No model output is used.

For every DEV6 padded input (A20 and S20 of all 16 systems, both families) and every grid level: decisions from the
cached p-values, connected components, frozen P-N2 screen_metrics against the true target graph, and
J = merged / k + split / |E_T| (as P-N2). The level with the smallest mean J wins; ties go to the smaller level.
Splits at k0 are reported per level.
usage: alpha6.py  ->  pn6_out/alpha6.json
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
from common6 import OUT6, ALPHA_L_GRID, ALPHA_H_GRID, syn_items, assemble6, load_pvals, reject, SCR, sha

rows = []
for it in syn_items('DEV6'):
    X, dT, info = assemble6(it)
    p, pm = load_pvals(it)
    assert pm['input_sha'] == sha(X), f"cached p-values do not match {it['sid']} {it['cond']}"
    for arm, grid in (('RL', ALPHA_L_GRID), ('RH', ALPHA_H_GRID)):
        for al in grid:
            R = reject(p, arm, al)
            lab = SCR.components(R)
            s = SCR.screen_metrics(lab, R, dT, info['g'])
            J = None if it['cond'] == 'k0' else s['merged'] / s['k'] + s['split'] / s['n_true_edges']
            rows.append(dict(sys=it['sid'], ci=it['ci'], cond=it['cond'], arm=arm, alpha=al, J=J, **s))

out = dict(rule='J = merged/k + split/|E_T| on A20 and S20, mean over both families; ties to the smaller level', table={})
for arm, grid in (('RL', ALPHA_L_GRID), ('RH', ALPHA_H_GRID)):
    best = None
    for al in grid:
        pad = [r for r in rows if r['arm'] == arm and r['alpha'] == al and r['cond'] != 'k0']
        k0 = [r for r in rows if r['arm'] == arm and r['alpha'] == al and r['cond'] == 'k0']
        mJ = float(np.mean([r['J'] for r in pad]))
        out['table'][f'{arm}|{al:g}'] = dict(mean_J=mJ, n_inputs=len(pad), merged_mean=float(np.mean([r['merged'] for r in pad])),
                                            split_mean=float(np.mean([r['split'] for r in pad])),
                                            k0_split_mean=float(np.mean([r['split'] for r in k0])),
                                            inputs_with_merge=int(sum(r['merged'] > 0 for r in pad)))
        if best is None or mJ < best[0] - 1e-15:
            best = (mJ, al)
    out['alpha_L' if arm == 'RL' else 'alpha_H'] = best[1]
(OUT6 / 'alpha6.json').write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
