"""P-N2 HELD2 reading (rules PN2_rules_held2 v1 §2-§5, §8). Written before any HELD2 output exists.

usage: analyze_held2.py [--set HELD2|EXP2]
  EXP2 = validation mode only (rules held2 §7): the five point estimates must equal the EXP2 REP estimates;
         p-values and Holm on EXP2 are code checks, not results.
Output: pn2_out/<set>_held2_reading.json
Metric definitions are those of rules v1 §5 (same logic as the frozen analyze2.py).
"""
import sys, json, argparse
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score, average_precision_score
from held2 import *

ap = argparse.ArgumentParser(); ap.add_argument('--set', default='HELD2'); a = ap.parse_args()
SYS = systems_by_set(a.set)
FWER, BOOT, BSEED = 0.05, 2000, 20261121
HYP = [('HA1', 'avici', 'lin', 'm_native', 'NEG'), ('HA2', 'avici', 'rff', 'm_native', 'NEG'),
       ('HC1', 'cdfm', 'rff', 'thr', 'POS'), ('HA5', 'avici', 'rff', 'f1_m0_native', 'NEG'),
       ('HC4', 'cdfm', 'rff', 'auroc_native', 'NEG')]


def npz(model, key):
    f = OUT2 / model / f'{key}.npz'
    if not f.exists():
        sys.exit(f'MISSING {model} {key}: reading refused')
    z = np.load(f, allow_pickle=False)
    d = {q: z[q] for q in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


_sha = {}
def check(o, sid, ci, seed, cond):
    if (sid, cond) not in _sha:
        X, _, _ = assemble2(sid, ci, seed, cond)
        _sha[(sid, cond)] = sha(X)
    if o['meta']['input_sha'] != _sha[(sid, cond)]:
        sys.exit(f'INPUT SHA MISMATCH {sid} {cond}: reading refused')


def sym(m):
    return ((m + m.T) > 0).astype(np.int8)


def count_upper(sk):
    return int(sk[np.triu_indices(sk.shape[0], 1)].sum())


def metrics(sk, s, g, m0):
    dT = g.shape[0]; iu = np.triu_indices(dT, 1)
    t = ((g + g.T) > 0)[iu]; pr = sk[iu] > 0; sv = s[iu]
    tp, fp, fn = int((t & pr).sum()), int((~t & pr).sum()), int((t & ~pr).sum())
    out = dict(m=int(pr.sum()), tp=tp, fp=fp, f1=0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    out['auroc'] = float(roc_auc_score(t, sv)); out['ap'] = float(average_precision_score(t, sv))
    if m0 > 0:
        top = np.zeros_like(pr); top[np.argsort(-sv, kind='stable')[:m0]] = True
        tp0 = int((t & top).sum())
        out['f1_m0'] = 0.0 if tp0 == 0 else 2 * tp0 / (2 * tp0 + (m0 - tp0) + int(t.sum()) - tp0)
    else:
        out['f1_m0'] = np.nan
    return out


def readings(model, o, dT, thr0, R=False):
    p = o['probs_T'] if R else o['probs'][:dT, :dT]
    if model == 'avici':
        nat = (np.maximum(p, p.T) > 0.5).astype(np.int8)
    else:
        nat = sym(o['adj_native_T'] if R else o['adj_native'][:dT, :dT])
    s = np.maximum(p, p.T)
    rd = dict(native=nat)
    if model == 'cdfm':
        a_ = (p > thr0).astype(np.int8); np.fill_diagonal(a_, 0); rd['frozen'] = sym(a_)
        rd['fixed'] = (s > 0.5).astype(np.int8)
    return rd, s


rows = {}
for model in ('avici', 'cdfm'):
    R_ = []
    for sid, ci, seed in SYS:
        dT, eT, mech = CELLS[ci]
        g = target(sid, ci, seed)['g']
        o0 = npz(model, key2(sid, 'k0', 'plain')); check(o0, sid, ci, seed, 'k0')
        thr0 = float(o0['threshold']) if model == 'cdfm' else None
        rd0, _ = readings(model, o0, dT, thr0)
        m0 = count_upper(rd0['native'])
        v = {}
        for arm in ('plain', 'R'):
            for cond in conds_held2(ci):
                o = npz(model, key2(sid, cond, arm)); check(o, sid, ci, seed, cond)
                rd, s = readings(model, o, dT, thr0, R=(arm == 'R'))
                c = {}
                for rn, sk in rd.items():
                    for q, val in metrics(sk, s, g, m0).items():
                        if rn == 'native' or q in ('m', 'tp', 'fp', 'f1'):
                            c[f'{q}_{rn}'] = val
                if model == 'cdfm' and arm == 'plain':
                    c['thr'] = float(o['threshold'])
                if arm == 'R':
                    c.update({q: o['meta'][q] for q in ('merged', 'split', 'false_cross', 'n_true_edges', 'k')})
                    if model == 'cdfm':
                        c['thr_components'] = [float(x) for x in o['thr_components']]
                v[f"{arm}|{'eT' if cond not in ('k0', 'e0') else cond}"] = c
        for arm in ('plain', 'R'):
            for cnd in ('e0', 'eT'):
                v[f'{arm}|{cnd}']['absdm_native'] = abs(v[f'{arm}|{cnd}']['m_native'] - v['plain|k0']['m_native'])
        if model == 'cdfm':   # rules held2 §4: post-hoc split anchored at the e = 0 threshold (descriptive)
            oe0 = npz(model, key2(sid, 'e0', 'plain')); oeT = npz(model, key2(sid, rep_cond(ci), 'plain'))
            a_ = (oeT['probs'][:dT, :dT] > float(oe0['threshold'])).astype(np.int8); np.fill_diagonal(a_, 0)
            mid = count_upper(sym(a_))
            v['decomp'] = dict(score_part=mid - v['plain|e0']['m_native'], threshold_part=v['plain|eT']['m_native'] - mid)
        R_.append(dict(sys=sid, ci=ci, fam=mech, dT=dT, m0=m0, v=v))
    rows[model] = R_


def strat(values, cells, sigma=1):
    """Cell-balanced mean, cell-stratified SE, Welch-Satterthwaite df, one-sided p in the direction sigma (rules held2 §3)."""
    by = {}
    for x, c in zip(values, cells):
        if not np.isnan(x):
            by.setdefault(c, []).append(float(x))
    keys = sorted(by); w = 1.0 / len(keys)
    means, ac, nc = [], [], []
    for c in keys:
        v = np.asarray(by[c]); n = len(v)
        means.append(float(v.mean())); nc.append(n)
        ac.append(w ** 2 * (v.var(ddof=1) if n > 1 else 0.0) / n)
    theta = w * sum(means); se2 = sum(ac); se = float(np.sqrt(se2))
    out = dict(theta=float(theta), se=se, n_by_cell=nc, cell_means=means, degenerate=False)
    if se2 > 0:
        den = sum(x ** 2 / (n - 1) for x, n in zip(ac, nc) if n > 1)
        df = float(se2 ** 2 / den) if den > 0 else float('inf')
        tstat = sigma * theta / se
        q = stats.t.ppf(0.975, df)
        out.update(df=df, t=float(tstat), p_one_sided=float(stats.t.sf(tstat, df)), ci95=[float(theta - q * se), float(theta + q * se)])
    else:
        out.update(df=None, t=None, p_one_sided=0.0 if sigma * theta > 0 else 1.0, ci95=[float(theta), float(theta)], degenerate=True)
    rng = np.random.default_rng(BSEED)
    arrs = [np.asarray(by[c]) for c in keys]
    bs = np.array([w * sum(x[rng.integers(0, len(x), len(x))].mean() for x in arrs) for _ in range(BOOT)])
    out['boot_ci95_stratified'] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    return out


def size_label(ci, margin):
    lo, hi = ci
    sign = 'POS' if lo > 0 else ('NEG' if hi < 0 else 'NONE')
    size = 'SMALL' if (lo >= -margin and hi <= margin) else ('LARGE' if (lo > margin or hi < -margin) else 'UNCLEAR')
    return sign, size


def margin_of(y):
    return 1.5 if y.startswith(('m_', 'absdm', 'tp_', 'fp_')) or y.endswith('_part') else (0.03 if y != 'thr' else 0.03)


def rep_vals(model, fam, y, arm='plain'):
    sel = [r for r in rows[model] if r['fam'] == fam]
    vals = [r['v'][f'{arm}|eT'].get(y, np.nan) - r['v'][f'{arm}|e0'].get(y, np.nan) for r in sel]
    return vals, [r['ci'] for r in sel], sel


def describe(vals, cells, y, sigma=1):
    st = strat(vals, cells, sigma)
    st['sign'], st['size'] = size_label(st['ci95'], margin_of(y))
    return st


res = dict(set=a.set, rules='P-N2 HELD2 v1 (commit 7bc8ba0)', n_systems=len(SYS), hypotheses={})
# ---- confirmatory: five hypotheses, Holm (rules held2 §2-§3) ----
for hid, model, fam, y, sgn in HYP:
    sigma = 1 if sgn == 'POS' else -1
    vals, cells, sel = rep_vals(model, fam, y)
    st = describe(vals, cells, y, sigma)
    st.update(model=model, family=fam, Y=y, predicted=sgn,
              excluded_m0_zero=[r['sys'] for r in sel if r['m0'] == 0] if y == 'f1_m0_native' else [],
              by_dT={str(d): float(np.mean([m for m, c in zip(st['cell_means'], sorted(set(cells))) if CELLS[c][0] == d]))
                     for d in (10, 20)})
    st['estimate_opposite_sign'] = bool(sigma * st['theta'] < 0)
    res['hypotheses'][hid] = st
order = sorted(res['hypotheses'], key=lambda h: res['hypotheses'][h]['p_one_sided'])
going = True
for j, hid in enumerate(order):
    thr = FWER / (len(order) - j)
    h = res['hypotheses'][hid]
    h['holm_rank'], h['holm_threshold'] = j + 1, thr
    if going and h['p_one_sided'] <= thr:
        h['label'] = 'CONFIRMED'
    else:
        going = False
        h['label'] = 'NOT_CONFIRMED'
# ---- descriptive (rules held2 §4) ----
Y_ALL = {'avici': ['m_native', 'f1_native', 'tp_native', 'fp_native', 'absdm_native', 'ap_native', 'auroc_native', 'f1_m0_native'],
         'cdfm': ['m_native', 'f1_native', 'tp_native', 'fp_native', 'absdm_native', 'ap_native', 'auroc_native', 'f1_m0_native',
                  'thr', 'm_frozen', 'm_fixed', 'f1_frozen', 'f1_fixed']}
res['descriptive_REP'] = {m: {fam: {y: describe(*rep_vals(m, fam, y)[:2], y) for y in Y_ALL[m]} for fam in ('lin', 'rff')} for m in Y_ALL}
res['cdfm_threshold_split'] = {fam: {part: describe([r['v']['decomp'][part] for r in rows['cdfm'] if r['fam'] == fam],
                                                    [r['ci'] for r in rows['cdfm'] if r['fam'] == fam], part)
                                     for part in ('score_part', 'threshold_part')} for fam in ('lin', 'rff')}
# ---- R arm, secondary (rules held2 §5) ----
Y_R = {'avici': ['m_native', 'f1_m0_native', 'auroc_native', 'f1_native'],
       'cdfm': ['m_native', 'f1_m0_native', 'auroc_native', 'f1_native', 'm_frozen', 'm_fixed']}
rr = {}
for m in ('avici', 'cdfm'):
    rr[m] = {}
    for fam in ('lin', 'rff'):
        sel = [r for r in rows[m] if r['fam'] == fam]; cells = [r['ci'] for r in sel]
        d = dict(REP_after_R={y: describe(*rep_vals(m, fam, y, 'R')[:2], y) for y in Y_R[m]})
        d['cost_at_k0'] = describe([r['v']['R|k0']['f1_native'] - r['v']['plain|k0']['f1_native'] for r in sel], cells, 'f1')
        for cnd in ('e0', 'eT'):
            d[f'F1_after_R_{cnd}_vs_original_k0'] = describe([r['v'][f'R|{cnd}']['f1_native'] - r['v']['plain|k0']['f1_native'] for r in sel], cells, 'f1')
            d[f'screen_{cnd}'] = dict(mean_merged_frac=float(np.mean([r['v'][f'R|{cnd}']['merged'] / r['v'][f'R|{cnd}']['k'] for r in sel])),
                                      mean_split_frac=float(np.mean([r['v'][f'R|{cnd}']['split'] / r['v'][f'R|{cnd}']['n_true_edges'] for r in sel])),
                                      mean_false_cross=float(np.mean([r['v'][f'R|{cnd}']['false_cross'] for r in sel])))
        d['screen_k0_split_frac'] = float(np.mean([r['v']['R|k0']['split'] / r['v']['R|k0']['n_true_edges'] for r in sel]))
        dm = np.array([abs(r['v']['R|eT']['m_native'] - r['v']['R|e0']['m_native']) for r in sel])
        d['per_system_abs_dm_REP_after_R'] = dict(max=int(dm.max()), frac_ge_2=float((dm >= 2).mean()),
                                                  systems_ge_2=[r['sys'] for r, x in zip(sel, dm) if x >= 2])
        if m == 'cdfm':
            d['component_thresholds_descriptive'] = {cnd: float(np.mean([np.mean(r['v'][f'R|{cnd}']['thr_components'])
                                                                         for r in sel if r['v'][f'R|{cnd}']['thr_components']]))
                                                     for cnd in ('k0', 'e0', 'eT')}
        rr[m][fam] = d
res['R_secondary'] = rr
if a.set == 'EXP2':   # validation (rules held2 §7)
    ref = {}
    for m in ('avici', 'cdfm'):
        ref.update({h: v['REP']['est'] for h, v in json.loads((OUT2 / f'exp2_{m}.json').read_text())['hypotheses'].items()})
    res['validation'] = {hid: dict(theta=res['hypotheses'][hid]['theta'], exp2_REP=ref[hid],
                                   match=abs(res['hypotheses'][hid]['theta'] - ref[hid]) < 1e-9) for hid, *_ in HYP}
res['rows'] = {m: [{k: (v if k != 'v' else {q: {kk: vv for kk, vv in x.items() if kk != 'thr_components'} if isinstance(x, dict) else x
                                            for q, x in v.items()}) for k, v in r.items()} for r in rows[m]] for m in rows}
(OUT2 / f'{a.set.lower()}_held2_reading.json').write_text(json.dumps(res, indent=1, default=float))
for hid in [h for h, *_ in HYP]:
    h = res['hypotheses'][hid]
    print(f"{hid}: theta {h['theta']:+.4f} CI [{h['ci95'][0]:+.4f}, {h['ci95'][1]:+.4f}] t {h['t']} df {h['df']} p {h['p_one_sided']:.3g} "
          f"holm {h['holm_threshold']:.4f} -> {h['label']} ({h['sign']}/{h['size']})")
if a.set == 'EXP2':
    print('validation:', json.dumps(res['validation']))
