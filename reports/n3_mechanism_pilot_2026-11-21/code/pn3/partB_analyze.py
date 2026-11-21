"""P-N3 Part B reading (rules v1 §2, §4). Exploratory screening; written before any pilot output exists.

usage: partB_analyze.py  ->  pn3_out/partB.json (refuses to read if any output is missing, failed, stale or a PLAIN output
differs from the frozen P-N2 EXP2 output)
"""
import sys, json
from pathlib import Path
PN3 = Path(__file__).resolve().parent
sys.path.insert(0, str(PN3)); sys.path.insert(0, str(PN3.parents[1] / 'n2_runs' / 'pn2'))
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score
from common2 import *
from partB_run_configs import CONFIGS

OUT3 = PN3.parent / 'pn3_out'; OUT_IV = OUT3 / 'avici_iv'
B, SEED, M_Q = 2000, 20261121, 0.03
SYS = [(s, ci, seed) for s, ci, seed in systems2('EXP2') if CELLS[ci][2] == 'lin']


def load(sid, cond, cfg):
    f = OUT_IV / f'{sid}__{cond}__{cfg}.npz'
    if not f.exists():
        sys.exit(f'MISSING {f.name}: reading refused')
    z = np.load(f); meta = json.loads(str(z['meta']))
    if meta['status'] != 'ok':
        sys.exit(f'FAILED {f.name}: reading refused')
    if cfg == 'PLAIN' and not meta.get('bitwise_vs_PN2'):
        sys.exit(f'PLAIN differs from P-N2 output {f.name}: reading refused')
    return np.asarray(z['probs']), meta


def metrics(p, g, m0):
    dT = g.shape[0]; iu = np.triu_indices(dT, 1)
    s = np.maximum(p[:dT, :dT], p[:dT, :dT].T)[iu]; t = ((g + g.T) > 0)[iu]; pr = s > 0.5
    tp, fp, fn = int((t & pr).sum()), int((~t & pr).sum()), int((t & ~pr).sum())
    top = np.zeros_like(pr); top[np.argsort(-s, kind='stable')[:m0]] = True; tp0 = int((t & top).sum())
    f1m0 = (0.0 if tp0 == 0 else 2 * tp0 / (2 * tp0 + (m0 - tp0) + int(t.sum()) - tp0)) if m0 > 0 else np.nan
    return dict(m=int(pr.sum()), f1=0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn), auroc=float(roc_auc_score(t, s)), f1_m0=f1m0)


rows = []
for sid, ci, seed in SYS:
    dT = CELLS[ci][0]; g = target(sid, ci, seed)['g']
    pk0 = np.asarray(np.load(OUT2 / 'avici' / f'{key2(sid, "k0", "plain")}.npz')['probs'])
    sk0 = np.maximum(pk0, pk0.T)[np.triu_indices(dT, 1)]; m0 = int((sk0 > 0.5).sum())
    v = {}
    for name, _, _ in CONFIGS:
        for cond, tag in (('e0', 'e0'), (rep_cond(ci), 'eT')):
            p, meta = load(sid, cond, name)
            X, _, _ = assemble2(sid, ci, seed, cond)
            if meta['input_sha'] != sha(X):
                sys.exit(f'INPUT SHA MISMATCH {sid} {cond} {name}: reading refused')
            v[(name, tag)] = metrics(p, g, m0)
    rows.append(dict(sys=sid, ci=ci, m0=m0, v=v))
cells = np.array([r['ci'] for r in rows]); keys = sorted(set(cells.tolist()))


def cell_mean(x):
    return float(np.mean([np.nanmean(x[cells == c]) for c in keys]))


def strat(x):
    x = np.asarray(x, float); w = 1.0 / len(keys)
    means, ac, nc = [], [], []
    for c in keys:
        xc = x[cells == c]; xc = xc[~np.isnan(xc)]; means.append(xc.mean()); nc.append(len(xc)); ac.append(w ** 2 * xc.var(ddof=1) / len(xc))
    th = w * sum(means); se2 = sum(ac); se = np.sqrt(se2)
    if se2 == 0:
        return dict(theta=float(th), ci95=[float(th), float(th)])
    df = se2 ** 2 / sum(a ** 2 / (n - 1) for a, n in zip(ac, nc)); q = stats.t.ppf(0.975, df)
    return dict(theta=float(th), ci95=[float(th - q * se), float(th + q * se)])


def rep(name, y):
    return np.array([r['v'][(name, 'eT')][y] - r['v'][(name, 'e0')][y] for r in rows], float)


# paired bootstrap indices (systems resampled within cells, shared by all configurations)
rng = np.random.default_rng(SEED)
idx_by_cell = {c: np.where(cells == c)[0] for c in keys}
BOOT = [np.concatenate([rng.choice(idx_by_cell[c], len(idx_by_cell[c]), replace=True) for c in keys]) for _ in range(B)]


def boot_cell_mean(x, ix):
    xc, cc = x[ix], cells[ix]
    return float(np.mean([np.nanmean(xc[cc == c]) for c in keys]))


plain = {y: rep('PLAIN', y) for y in ('m', 'auroc', 'f1_m0')}
th_plain = strat(plain['m'])
plain_ci_has_0 = th_plain['ci95'][0] <= 0 <= th_plain['ci95'][1]
res = dict(n_systems=len(rows), plain=dict(REP={y: strat(plain[y]) for y in plain}), configs={})
for name, mode, layers in CONFIGS:
    d = {}
    dm = rep(name, 'm')
    d['REP'] = {y: strat(rep(name, y)) for y in ('m', 'auroc', 'f1_m0')}
    d['paired_minus_PLAIN'] = {y: strat(rep(name, y) - plain[y]) for y in ('m', 'auroc', 'f1_m0')}
    th_i = d['REP']['m']['theta']
    a = 1 - abs(th_i) / abs(th_plain['theta']) if th_plain['theta'] != 0 else np.nan
    a_bs = [1 - abs(boot_cell_mean(dm, ix)) / abs(boot_cell_mean(plain['m'], ix)) if boot_cell_mean(plain['m'], ix) != 0 else np.nan for ix in BOOT]
    d['a'] = dict(est=float(a), ci95=[float(np.nanpercentile(a_bs, 2.5)), float(np.nanpercentile(a_bs, 97.5))])
    d['reversal_point'] = bool(np.sign(th_i) != np.sign(th_plain['theta']) and th_i != 0)
    lo, hi = d['REP']['m']['ci95']
    d['reversal_significant'] = bool((th_plain['theta'] < 0 and lo > 0) or (th_plain['theta'] > 0 and hi < 0))
    dq = {}
    for tag in ('e0', 'eT'):
        for y in ('f1', 'auroc'):
            dq[f'{y}_{tag}'] = strat(np.array([r['v'][(name, tag)][y] - r['v'][('PLAIN', tag)][y] for r in rows]))
    d['quality_vs_PLAIN'] = dq
    d['degradation_flag'] = bool(any(v['theta'] < -M_Q for v in dq.values()))
    res['configs'][name] = d
# classification (rules v1 §2 table); KO-all is a technical check only
lab = {}
usable = lambda n: not res['configs'][n]['degradation_flag'] and not res['configs'][n]['reversal_significant']
if plain_ci_has_0:
    lab['note'] = 'CI of theta_PLAIN contains 0: a_I not used for classification'
else:
    a_ = lambda n: res['configs'][n]['a']['est']
    lab['KO-all'] = f"technical check only (a = {a_('KO-all'):.2f})"
    if usable('V0-all') and a_('V0-all') >= 0.5:
        lab['V0-all'] = 'candidate: sensitive to the value path (all layers)'
    for l in range(1, 9):
        v0, ko = f'V0-{l}', f'KO-{l}'; tags = []
        dko_v0 = strat(rep(ko, 'm') - rep(v0, 'm'))
        if usable(v0) and usable(ko) and a_(v0) <= 0.25 and a_(ko) >= 0.75 and not (dko_v0['ci95'][0] <= 0 <= dko_v0['ci95'][1]):
            tags.append('candidate: normalization-sensitive at this layer')
        if usable(v0) and a_(v0) >= 0.5:
            tags.append('candidate: sensitive to the value path at this layer')
        if (usable(v0) and a_(v0) >= 0.5) or (usable(ko) and a_(ko) >= 0.5):
            tags.append('sensitive to intervention at this layer (not the only locus)')
        lab[f'layer_{l}'] = dict(tags=tags or ['not yet distinguished'], a_V0=a_(v0), a_KO=a_(ko), KO_minus_V0=dko_v0)
res['classification'] = lab
res['plain_ci_contains_0'] = plain_ci_has_0
(OUT3 / 'partB.json').write_text(json.dumps(res, indent=1, default=float))
print('PLAIN REP dm', th_plain)
for name, *_ in CONFIGS:
    c = res['configs'][name]
    print(f"{name:7s} REP dm {c['REP']['m']['theta']:+.2f} a {c['a']['est']:+.2f} [{c['a']['ci95'][0]:+.2f},{c['a']['ci95'][1]:+.2f}] "
          f"rev {c['reversal_point']}/{c['reversal_significant']} degr {c['degradation_flag']}")
print(json.dumps(lab, indent=1, default=float))
