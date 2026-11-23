"""Feasibility check for SEA (step 2): read SEA's result files, check the adapter, measure repeatability and target-block
change on development inputs. Descriptive only.

SEA returns, per input, pred = [P(i->j) for i<j] + [P(j->i) for i<j] (pairs in row-major upper-triangular order) and
true in the same layout. The adapter check compares `true` with the DAG we wrote, and recomputes SEA's AUROC.
Skeleton (as in SEA's own accuracy metric, threshold 0.5 per direction): edge {i, j} if max(P(i->j), P(j->i)) > 0.5.
usage (Study 1 model environment): python -I read_results.py <work dir>
"""
import json
import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

W = Path(sys.argv[1]).resolve()
inputs = {i['key']: i for i in json.loads((W / 'inputs.json').read_text(encoding='utf-8'))}
runs = {r: pickle.load(open(W / f'run_{r}.pkl', 'rb')) for r in ('A_seed0', 'B_seed0', 'C_seed1')}
meta = {r: json.loads((W / f'run_{r}.json').read_text(encoding='utf-8')) for r in runs}


def unpack(res, key):
    m = res[key]
    p, t = np.asarray(m['pred'][0], float), np.asarray(m['true'][0], float)
    D = inputs[key]['d']
    P = D * (D - 1) // 2
    assert p.shape == (2 * P,) and t.shape == (2 * P,), (key, p.shape, P)
    iu = np.triu_indices(D, 1)
    F, B = np.zeros((D, D)), np.zeros((D, D))
    F[iu], B[iu] = p[:P], p[P:]
    prob = F + B.T                      # prob[i, j] = P(i -> j) for all ordered pairs
    G = np.load(W / 'inputs' / key / 'DAG.npy')
    t_ok = np.array_equal(t, np.concatenate([G[iu], G.T[iu]]).astype(float))
    auc_ok = None
    if 0 < t.sum() < len(t):
        auc_ok = abs(roc_auc_score(t, p) - m['auc'][0]) < 1e-6
    return prob, G, t_ok, auc_ok, float(m['time'][0])


def skel(prob, dT):
    s = np.maximum(prob, prob.T)[:dT, :dT] > 0.5
    return s[np.triu_indices(dT, 1)]


def f1(s, G, dT):
    g = ((G + G.T) > 0)[:dT, :dT][np.triu_indices(dT, 1)]
    tp, fp, fn = int((g & s).sum()), int((~g & s).sum()), int((g & ~s).sum())
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


print('runs:', {r: (round(meta[r]['wall_s'], 1), round(meta[r]['peak_wset_mb'])) for r in runs}, '(wall s, peak MB)')
rows = []
for key in inputs:
    dT = 11 if key.startswith('standin') else (10 if 'c0-' in key else 20)
    A, G, t_ok, auc_ok, tA = unpack(runs['A_seed0'], key)
    B, _, _, _, tB = unpack(runs['B_seed0'], key)
    C, _, _, _, tC = unpack(runs['C_seed1'], key)
    rows.append(dict(key=key, D=inputs[key]['d'], dT=dT, true_layout_ok=t_ok, auroc_matches=auc_ok,
                     rerun_bitwise=bool(np.array_equal(A, B)), seed_max_abs_dp=float(np.abs(A - C).max()),
                     seed_flips=int((skel(A, dT) != skel(C, dT)).sum()), edges=int(skel(A, dT).sum()),
                     f1_target=f1(skel(A, dT), G, dT), time_s=tA))
base = {r['key'].split('__')[0]: r for r in rows if r['key'].endswith('k0')}
for r in rows:
    root = r['key'].split('__')[0]
    if r['key'].endswith('k0'):
        r['flips_vs_k0'] = 0
    else:
        k0prob, _, _, _, _ = unpack(runs['A_seed0'], f'{root}__k0')
        Aprob, _, _, _, _ = unpack(runs['A_seed0'], r['key'])
        r['flips_vs_k0'] = int((skel(Aprob, r['dT']) != skel(k0prob, r['dT'])).sum())
for r in rows:
    print(f"{r['key']:<24} D={r['D']:<3} layout={r['true_layout_ok']} auroc={r['auroc_matches']} rerun_bitwise={r['rerun_bitwise']} "
          f"seed: max|dp|={r['seed_max_abs_dp']:.3f} flips={r['seed_flips']:<2} | edges={r['edges']:<3} F1={r['f1_target']:.3f} "
          f"flips_vs_k0={r['flips_vs_k0']:<3} time={r['time_s']:.1f}s")
(W / 'feasibility_summary.json').write_text(json.dumps(dict(runs=meta, rows=rows), indent=1), encoding='utf-8')
