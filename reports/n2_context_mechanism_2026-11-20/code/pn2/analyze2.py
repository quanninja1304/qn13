"""P-N2 exploratory reading (rules v1 §5-§7, §10). Written before any EXP2 output exists.

usage: analyze2.py <avici|cdfm|classical> [--set EXP2|DEV2]
  DEV2 is allowed only to validate the code (rules v1 §9); its numbers are never used to change locked rules.
Output: pn2_out/<set>_<model>.json
"""
import sys, json, argparse
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score
from common2 import *

ap = argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--set', default='EXP2'); a = ap.parse_args()
B, SEED = 2000, 20261120
M = dict(count=1.5, rate=0.03, thr=0.03)
SYS = systems2(a.set)
E_ORDER = ['e0', 'e0.5', 'e1', 'e2', 'e3']
E_VAL = [0.0, 0.5, 1.0, 2.0, 3.0]


def npz(model, key):
    f = OUT2 / model / f'{key}.npz'
    if not f.exists():
        sys.exit(f'MISSING {model} {key}: reading refused')
    z = np.load(f, allow_pickle=False)
    d = {q: z[q] for q in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


def check_input(o, sid, ci, seed, cond):
    X, t, _ = assemble2(sid, ci, seed, cond)
    if o['meta']['input_sha'] != sha(X):
        sys.exit(f'INPUT SHA MISMATCH {sid} {cond}: reading refused')
    return t


def sym(m):
    return ((m + m.T) > 0).astype(np.int8)


def metrics(sk, s, g, m0):
    dT = g.shape[0]; iu = np.triu_indices(dT, 1)
    t = ((g + g.T) > 0)[iu]; pr = sk[iu] > 0; sv = s[iu]
    tp, fp, fn = int((t & pr).sum()), int((~t & pr).sum()), int((t & ~pr).sum())
    f1 = 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)
    out = dict(m=int(pr.sum()), tp=tp, fp=fp, f1=f1)
    out['auroc'] = float(roc_auc_score(t, sv)); out['ap'] = float(average_precision_score(t, sv))
    if m0 > 0:
        top = np.zeros_like(pr); top[np.argsort(-sv, kind='stable')[:m0]] = True
        tp0 = int((t & top).sum()); out['f1_m0'] = 0.0 if tp0 == 0 else 2 * tp0 / (2 * tp0 + (m0 - tp0) + int(t.sum()) - tp0)
    else:
        out['f1_m0'] = np.nan
    pc = np.clip(sv, 1e-6, 1 - 1e-6); lg = np.log(pc / (1 - pc))
    out['logit_true'] = float(lg[t].mean()); out['logit_false'] = float(lg[~t].mean())
    return out, pr


def readings(model, o, dT, thr0, R=False):
    """skeletons per reading and the score matrix on the target block."""
    if R:
        p = o['probs_T']
        nat = (np.maximum(p, p.T) > 0.5).astype(np.int8) if model == 'avici' else sym(o['adj_native_T'])
    else:
        p = o['probs'][:dT, :dT]
        nat = (np.maximum(p, p.T) > 0.5).astype(np.int8) if model == 'avici' else sym(o['adj_native'][:dT, :dT])
    s = np.maximum(p, p.T)
    rd = dict(native=nat)
    if model == 'cdfm':
        a_ = (p > thr0).astype(np.int8); np.fill_diagonal(a_, 0); rd['frozen'] = sym(a_)
        rd['fixed'] = (s > 0.5).astype(np.int8)
    return rd, s


rows = []
if a.model in ('avici', 'cdfm'):
    for sid, ci, seed in SYS:
        dT, eT, mech = CELLS[ci]
        r = dict(sys=sid, ci=ci, fam=mech, dT=dT, eT=eT)
        o0 = npz(a.model, key2(sid, 'k0', 'plain')); t = check_input(o0, sid, ci, seed, 'k0'); g = t['g']
        thr0 = float(o0['threshold']) if a.model == 'cdfm' else None
        rd0, s0 = readings(a.model, o0, dT, thr0)
        m0 = int(rd0['native'][np.triu_indices(dT, 1)].sum())
        r['m0'] = m0
        base = {}
        for arm in ('plain', 'R'):
            for cond in CONDS:
                o = npz(a.model, key2(sid, cond, arm)); check_input(o, sid, ci, seed, cond)
                rd, s = readings(a.model, o, dT, thr0, R=(arm == 'R'))
                c = {}
                for rname, sk in rd.items():
                    mt, pr = metrics(sk, s, g, m0)
                    for q, v in mt.items():
                        if rname == 'native' or q in ('m', 'tp', 'fp', 'f1'):
                            c[f'{q}_{rname}'] = v
                    if rname == 'native':
                        c['pred_native'] = pr
                if a.model == 'cdfm' and arm == 'plain':
                    c['thr'] = float(o['threshold'])
                if arm == 'R':
                    c.update({q: o['meta'][q] for q in ('merged', 'split', 'false_cross', 'n_target_components', 'n_true_edges')}
                             if cond != 'k0' or 'merged' in o['meta'] else {})
                    c['runtime_s'] = o['meta']['runtime_s']
                if cond != 'k0':
                    c['pad_edges'], c['pad_isolated'] = o['meta']['pad_edges'], o['meta']['pad_isolated']
                base[(arm, cond)] = c
        for arm in ('plain', 'R'):
            k0p = base[('plain', 'k0')]
            for cond in CONDS:
                c = base[(arm, cond)]
                for rn in ('native', 'frozen', 'fixed'):
                    if f'm_{rn}' in c:
                        c[f'dm_{rn}'] = c[f'm_{rn}'] - k0p[f'm_{rn}']
                c['absdm_native'] = abs(c['dm_native']); c['dm_over_dT'] = c['dm_native'] / dT
                c['flips_native'] = int((c['pred_native'] != k0p['pred_native']).sum())
        for k_ in base:
            base[k_].pop('pred_native', None)
        r['v'] = {f'{arm}|{cond}': base[(arm, cond)] for arm, cond in base}
        rows.append(r)


def boot(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]
    if len(v) == 0:
        return dict(est=None, ci=None, n=0)
    rng = np.random.default_rng(SEED); idx = rng.integers(0, len(v), (B, len(v)))
    bs = v[idx].mean(1)
    return dict(est=float(v.mean()), ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], n=int(len(v)))


def label(b, margin):
    if b['est'] is None:
        return dict(sign='NA', size='NA')
    lo, hi = b['ci']
    sign = 'POS' if lo > 0 else ('NEG' if hi < 0 else 'NONE')
    size = 'SMALL' if (lo >= -margin and hi <= margin) else ('LARGE' if (lo > margin or hi < -margin) else 'UNCLEAR')
    return dict(sign=sign, size=size)


def margin_of(y):
    return M['count'] if y.startswith(('m_', 'dm_', 'absdm', 'flips', 'tp_', 'fp_')) else (M['thr'] if y == 'thr' else M['rate'])


Y_PRIMARY = ['m_native', 'auroc_native', 'f1_m0_native'] + (['m_frozen', 'm_fixed', 'thr'] if a.model == 'cdfm' else [])
Y_SECOND = ['f1_native', 'tp_native', 'fp_native', 'absdm_native', 'flips_native', 'ap_native', 'dm_over_dT',
            'logit_true_native', 'logit_false_native'] + (['f1_frozen', 'f1_fixed'] if a.model == 'cdfm' else [])
Y_R = ['m_native', 'auroc_native', 'f1_m0_native', 'f1_native', 'ap_native'] + (['m_frozen', 'm_fixed', 'f1_frozen', 'f1_fixed'] if a.model == 'cdfm' else [])


def contrast_values(r, arm, y, kind):
    v = r['v']
    get = lambda c: v[f'{arm}|{c}'].get(y, np.nan)
    if kind == 'REP':
        return get(rep_cond(r['ci'])) - get('e0')
    if kind == 'L1-END':
        return get('e3') - get('e0')
    if kind.startswith('PROF_'):
        return get(kind[5:]) - get('e0')
    if kind == 'SLOPE':
        ys = np.array([get(c) for c in E_ORDER], float)
        return float(np.polyfit(E_VAL, ys, 1)[0]) if not np.isnan(ys).any() else np.nan
    if kind.startswith('L2_'):
        return get(kind[3:]) - get('e0')
    raise ValueError(kind)


KINDS = ['REP', 'L1-END', 'PROF_e0.5', 'PROF_e1', 'PROF_e2', 'SLOPE', 'L2_s0.25', 'L2_s0.5', 'L2_e2']


def summarize(sel, arm, ys):
    out = {}
    for y in ys:
        out[y] = {}
        for kind in KINDS:
            vals = [contrast_values(r, arm, y, kind) for r in rows if sel(r)]
            b = boot(vals); b.update(label(b, margin_of(y))); out[y][kind] = b
    return out


HYP = [('HA1', 'avici', 'lin', 'm_native', 'NEG'), ('HA2', 'avici', 'rff', 'm_native', 'NEG'),
       ('HA3', 'avici', 'lin', 'f1_m0_native', 'POS'), ('HA4', 'avici', 'lin', 'auroc_native', 'POS'),
       ('HA5', 'avici', 'rff', 'f1_m0_native', 'NEG'), ('HA6', 'avici', 'rff', 'auroc_native', 'NEG'),
       ('HC1', 'cdfm', 'rff', 'thr', 'POS'), ('HC2', 'cdfm', 'rff', 'm_native', 'NEG'),
       ('HC3', 'cdfm', 'rff', 'f1_m0_native', 'NEG'), ('HC4', 'cdfm', 'rff', 'auroc_native', 'NEG'),
       ('HC5', 'cdfm', 'lin', 'thr', 'POS')]

res = dict(model=a.model, set=a.set, rules='P-N2 v1 (commit 5c2c76c)', margins=M, n_systems=len(rows))
if a.model in ('avici', 'cdfm'):
    res['m0_zero_systems'] = [r['sys'] for r in rows if r['m0'] == 0]
    fams = {'lin': lambda r: r['fam'] == 'lin', 'rff': lambda r: r['fam'] == 'rff', 'pooled_reference_only': lambda r: True}
    res['plain'] = {f: summarize(s, 'plain', Y_PRIMARY + Y_SECOND) for f, s in fams.items()}
    res['R'] = {f: summarize(s, 'R', Y_R) for f, s in fams.items()}
    res['by_dT'] = {f'{fam}_dT{d}': summarize(lambda r, fam=fam, d=d: r['fam'] == fam and r['dT'] == d, 'plain', ['m_native', 'f1_m0_native', 'auroc_native'])
                    for fam in ('lin', 'rff') for d in (10, 20)}
    hyp = {}
    for hid, mdl, fam, y, sgn in HYP:
        if mdl != a.model:
            continue
        b = res['plain'][fam][y]['REP']; endb = res['plain'][fam][y]['L1-END']
        lab = 'CONSISTENT' if b['sign'] == sgn else ('INCONCLUSIVE' if b['sign'] == 'NONE' else 'CONTRARY')
        shape = 'shape differs from prediction' if endb['sign'] not in ('NONE', sgn, 'NA') else ''
        hyp[hid] = dict(family=fam, Y=y, predicted=sgn, REP=b, label=lab, size=b['size'], L1_END=endb, shape_flag=shape)
    res['hypotheses'] = hyp
    # rules v1 §10.3: R reduces change vs R is a useful fix
    rr = {}
    for fam in ('lin', 'rff'):
        sel = [r for r in rows if r['fam'] == fam]
        cost_k0 = boot([r['v']['R|k0']['f1_native'] - r['v']['plain|k0']['f1_native'] for r in sel])
        cost_k0.update(label(cost_k0, M['rate']))
        per = {}
        for cond in PADDED:
            after = boot([r['v'][f'R|{cond}']['f1_native'] - r['v']['plain|k0']['f1_native'] for r in sel])
            after.update(label(after, M['rate']))
            useful = 'YES' if (cost_k0['size'] == 'SMALL' and after['size'] == 'SMALL') else \
                     ('NO' if ((cost_k0['size'] == 'LARGE' and cost_k0['sign'] == 'NEG') or (after['size'] == 'LARGE' and after['sign'] == 'NEG')) else 'UNCLEAR')
            scr = {q: float(np.mean([r['v'][f'R|{cond}'][q] / (r['v'][f'R|{cond}']['n_true_edges'] if q == 'split' else (20 if q == 'merged' else 1)) for r in sel]))
                   for q in ('merged', 'split', 'false_cross')}
            per[cond] = dict(f1_after_R_vs_original_k0=after, useful_fix=useful, mean_merged_frac=scr['merged'],
                             mean_split_frac=scr['split'], mean_false_cross=scr['false_cross'],
                             mean_runtime_s=float(np.mean([r['v'][f'R|{cond}']['runtime_s'] for r in sel])))
        reduces = {}
        for y in Y_R:
            for kind in ('REP', 'L1-END'):
                pl, rr_ = res['plain'][fam][y][kind], res['R'][fam][y][kind]
                reduces[f'{y}|{kind}'] = bool(pl['size'] == 'LARGE' and rr_['size'] == 'SMALL')
        rr[fam] = dict(cost_at_k0=cost_k0, per_condition=per, R_reduces_change=reduces)
    res['R_evaluation'] = rr
    res['rows'] = rows
else:   # classical: PC and GES on linear systems, descriptive (rules v1 §4)
    out = {}
    for alg in ('pc', 'ges'):
        vals = {}
        for sid, ci, seed in SYS:
            dT, eT, mech = CELLS[ci]
            if mech != 'lin':
                continue
            g = target(sid, ci, seed)['g']; sk0 = None; v = {}
            for cond in ('k0', 'e0', rep_cond(ci), 'e3'):
                o = npz(alg, key2(sid, cond, 'plain')); check_input(o, sid, ci, seed, cond)
                sk = o['skel'][:dT, :dT]; mt, _ = metrics(sk, sk.astype(float), g, 1)
                v[cond if cond in ('k0', 'e0', 'e3') else 'eT'] = dict(m=mt['m'], f1=mt['f1'])
            vals[sid] = v
        S = list(vals.values())
        out[alg] = {kind: {y: boot([s[c1][y] - s[c0][y] for s in S]) for y in ('m', 'f1')}
                    for kind, (c1, c0) in (('REP', ('eT', 'e0')), ('L1-END', ('e3', 'e0')), ('H_e0', ('e0', 'k0')))}
    res['classical'] = out
(OUT2 / f'{a.set.lower()}_{a.model}.json').write_text(json.dumps(res, indent=1, default=float))
print(json.dumps(res.get('hypotheses', res.get('classical')), indent=1, default=float)[:4000])
