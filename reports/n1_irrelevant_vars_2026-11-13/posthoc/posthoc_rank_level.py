"""Post-hoc DESCRIPTIVE analysis of P-N1 held-out outputs (not a registered test).

Question (from the 20/11 review): when padding changes the target-block output, is it mainly a
change in the number of predicted edges (level / calibration / threshold) or a change in the
ranking of true vs false pairs (discrimination)?

Exact decomposition per system, skeleton, target block only:
  H_native(c) = F1_nat(k0) - F1_nat(c)
             = [F1_nat(k0) - F1_m0(k0)]          (decoder gap at k0; 0 for AVICI/CDFM up to ties)
             + [F1_m0(k0) - F1_m0(c)]            RANK part: top-m0 pairs by score, m0 = native edge count at k0
             + [F1_m0(c) - F1_nat(c)]            LEVEL part: effect of predicting a different number of edges
Reads frozen modules and saved outputs read-only. Usage: python posthoc_rank_level.py <out.json>
"""
import sys, json
from pathlib import Path
import numpy as np
# frozen P-N1 modules (git-ignored run tree); this file lives in reports/n1_irrelevant_vars_2026-11-13/posthoc/
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'artifacts' / 'n1_runs' / 'pn1'))
from common import target, CELLS
from metrics import load, f1, skel_native, skel_fixed, skel_frozen_cdfm, boot_ci
from jobs import held_systems, HELD_PER_CELL
from sklearn.metrics import roc_auc_score, average_precision_score

B, SEED = 2000, 20261114
CONDS = {'avici': ['A20', 'B20'], 'cdfm': ['A20', 'B20', 'C20'], 'foundcause': ['A20', 'B20']}


def topm_skel(s_vec, m, dT):
    iu = np.triu_indices(dT, 1)
    sk = np.zeros((dT, dT), np.int8)
    if m > 0:
        idx = np.argsort(-s_vec, kind='stable')[:m]
        sk[iu[0][idx], iu[1][idx]] = 1
    return sk


def per_cond(model, out, g, dT, m0, thr0=None):
    iu = np.triu_indices(dT, 1)
    p = out['probs'][:dT, :dT]
    s = np.maximum(p, p.T)[iu]
    t = ((g + g.T) > 0)[iu]
    sn = skel_native(model, out, dT)
    r = dict(f1_nat=f1(sn, g), n_nat=int(sn[iu].sum()), f1_m0=f1(topm_skel(s, m0, dT), g),
             auroc=float(roc_auc_score(t, s)), ap=float(average_precision_score(t, s)),
             n_true=int(t.sum()))
    pc = np.clip(s, 1e-6, 1 - 1e-6); lg = np.log(pc / (1 - pc))
    r['logit_true'] = float(lg[t].mean()); r['logit_false'] = float(lg[~t].mean())
    r['s_vec'] = s
    if model == 'cdfm':
        r['f1_frozen'] = f1(skel_frozen_cdfm(out, dT, thr0), g)
        r['thr'] = float(out['threshold'])
    return r


def run(model):
    SYS = held_systems(HELD_PER_CELL[model])
    rows = []
    for sid, ci, seed in SYS:
        t = target(sid, ci, seed); g = t['g']; dT = g.shape[0]
        o0 = load(model, sid, '-', 0)
        sn0 = skel_native(model, o0, dT); m0 = int(sn0[np.triu_indices(dT, 1)].sum())
        thr0 = float(o0['threshold']) if model == 'cdfm' else None
        r0 = per_cond(model, o0, g, dT, m0, thr0)
        row = dict(sys=sid, lin=CELLS[ci][2] == 'lin', dT=dT, k0=r0)
        for c in CONDS[model]:
            o = load(model, sid, c[0], int(c[1:]))
            rc = per_cond(model, o, g, dT, m0, thr0)
            rc['spearman_vs_k0'] = float(np.corrcoef(np.argsort(np.argsort(rc['s_vec'])),
                                                     np.argsort(np.argsort(r0['s_vec'])))[0, 1])
            row[c] = rc
        rows.append(row)
    return rows


def mci(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]
    e, lo, hi = boot_ci(v, np.mean, B, SEED)
    return [round(e, 4), round(lo, 4), round(hi, 4)]


def summarize(model, rows, sub=lambda x: True):
    R = [x for x in rows if sub(x)]
    S = dict(n=len(R))
    gap0 = [x['k0']['f1_nat'] - x['k0']['f1_m0'] for x in R]
    S['decoder_gap_k0'] = mci(gap0)
    S['k0'] = dict(auroc=mci([x['k0']['auroc'] for x in R]), n_nat=mci([x['k0']['n_nat'] for x in R]),
                   n_true=mci([x['k0']['n_true'] for x in R]), f1_nat=mci([x['k0']['f1_nat'] for x in R]))
    for c in CONDS[model]:
        H = [x['k0']['f1_nat'] - x[c]['f1_nat'] for x in R]
        rank = [x['k0']['f1_m0'] - x[c]['f1_m0'] for x in R]
        level = [x[c]['f1_m0'] - x[c]['f1_nat'] for x in R]
        d = dict(H_native=mci(H), H_rank=mci(rank), H_level=mci(level),
                 d_auroc=mci([x[c]['auroc'] - x['k0']['auroc'] for x in R]),
                 d_ap=mci([x[c]['ap'] - x['k0']['ap'] for x in R]),
                 d_n_nat=mci([x[c]['n_nat'] - x['k0']['n_nat'] for x in R]),
                 d_logit_true=mci([x[c]['logit_true'] - x['k0']['logit_true'] for x in R]),
                 d_logit_false=mci([x[c]['logit_false'] - x['k0']['logit_false'] for x in R]),
                 spearman_vs_k0=mci([x[c]['spearman_vs_k0'] for x in R]))
        if model == 'cdfm':
            d['H_frozen'] = mci([x['k0']['f1_nat'] - x[c]['f1_frozen'] for x in R])
            d['H_native_minus_frozen'] = mci([x[c]['f1_frozen'] - x[c]['f1_nat'] for x in R])
            d['d_thr'] = mci([x[c]['thr'] - x['k0']['thr'] for x in R])
        S[c] = d
    # B - A contrasts
    S['B_minus_A'] = dict(
        d_n_nat=mci([x['B20']['n_nat'] - x['A20']['n_nat'] for x in R]),
        d_f1_nat=mci([x['B20']['f1_nat'] - x['A20']['f1_nat'] for x in R]),
        d_f1_m0=mci([x['B20']['f1_m0'] - x['A20']['f1_m0'] for x in R]),
        d_auroc=mci([x['B20']['auroc'] - x['A20']['auroc'] for x in R]),
        d_logit_true=mci([x['B20']['logit_true'] - x['A20']['logit_true'] for x in R]),
        d_logit_false=mci([x['B20']['logit_false'] - x['A20']['logit_false'] for x in R]))
    return S


if __name__ == '__main__':
    out = {}
    for model in ('avici', 'cdfm', 'foundcause'):
        rows = run(model)
        out[model] = dict(all=summarize(model, rows),
                          lin=summarize(model, rows, lambda x: x['lin']),
                          rff=summarize(model, rows, lambda x: not x['lin']))
    path = sys.argv[1]
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print('written', path)
