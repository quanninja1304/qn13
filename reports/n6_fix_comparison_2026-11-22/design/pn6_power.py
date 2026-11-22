"""P-N6 power record (design input; read-only on frozen HELD2 outputs; no model is run).

Proxy: the old R arm (R-B) of HELD2, 120 systems (15 per cell). R-L may behave differently, so this is a planning
proxy, not a guarantee. Per system (frozen P-N1 metrics: skel_native, skel_frozen_cdfm, f1):
  Q0 = F1(R, k0) - F1(plain, k0)
  QA = F1(R, e0) - F1(plain, k0)              e0 = 20 independent Gaussian columns (A20)
  D2 = phi_FROZEN(e_T) - phi_R(e_T)           CDFM only; fidelity flips against the plain k0 skeleton
Tests as in the P-N6 rules: stratified t within a family (w_c = 1/4, SE^2 = sum w^2 s^2 / n, Welch-Satterthwaite df);
  P6-1 non-inferiority composite: p = max(p(Q0 > -0.03), p(QA > -0.03)); P6-2: one-sided D2 > 0.
Power: within-cell bootstrap (15 systems per cell with replacement, B = 4000) at the strictest Holm level (0.05/6)
and at 0.05, as observed and with every system's value shifted 0.01 toward the margin (P6-1) or scaled by 0.5 (P6-2).
usage: python -I pn6_power.py <artifacts dir> <output json>
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats

ART, DEST = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(ART / 'n1_runs' / 'pn1'))
from common import CELLS, target          # frozen P-N1
from metrics import skel_native, skel_frozen_cdfm, skel_fixed, f1, triu

OUT = ART / 'n2_runs' / 'pn2_out'
M, B, SEED = 0.03, 4000, 20261123


def load(model, sid, cond, arm):
    return dict(np.load(OUT / model / f'{sid}__{cond}__{arm}.npz', allow_pickle=False))


def skel_R(model, o, dT):
    if model == 'avici':
        return skel_fixed(o['probs_T'], dT)
    a = o['adj_native_T'][:dT, :dT]
    return ((a + a.T) > 0).astype(np.int8)


def flips(s1, s0):
    iu = triu(s0.shape[0])
    return int((s1[iu] != s0[iu]).sum())


rows = []
for ci, (dT, eT, fam) in enumerate(CELLS):
    for r in range(15):
        sid, seed = f'HELD2-c{ci}-r{r}', 430000 + 1000 * ci + r
        g = target(sid, ci, seed)['g']
        for model in ('avici', 'cdfm'):
            pk0, pe0 = load(model, sid, 'k0', 'plain'), load(model, sid, 'e0', 'plain')
            rk0, re0 = load(model, sid, 'k0', 'R'), load(model, sid, 'e0', 'R')
            s0 = skel_native(model, pk0, dT)
            f_p0 = f1(s0, g)
            row = dict(sys=sid, ci=ci, fam=fam, model=model, dT=dT,
                       Q0=f1(skel_R(model, rk0, dT), g) - f_p0, QA=f1(skel_R(model, re0, dT), g) - f_p0,
                       H_plain=f_p0 - f1(skel_native(model, pe0, dT), g))
            if model == 'cdfm':
                pT, rT = load(model, sid, f'e{eT}', 'plain'), load(model, sid, f'e{eT}', 'R')
                row['phi_frozen'] = flips(skel_frozen_cdfm(pT, dT, float(pk0['threshold'])), s0)
                row['phi_R'] = flips(skel_R(model, rT, dT), s0)
                row['D2'] = row['phi_frozen'] - row['phi_R']
            rows.append(row)


def strat(vals_by_cell, bound=0.0):
    """One-sided stratified t for mean > bound; returns estimate, se, df, t, p."""
    w = 1 / len(vals_by_cell)
    est = sum(w * np.mean(v) for v in vals_by_cell)
    a = [w ** 2 * np.var(v, ddof=1) / len(v) for v in vals_by_cell]
    se = float(np.sqrt(sum(a)))
    if se == 0:
        return est, 0.0, None, None, 1.0
    df = sum(a) ** 2 / sum(x ** 2 / (len(v) - 1) for x, v in zip(a, vals_by_cell))
    t = (est - bound) / se
    return est, se, df, t, float(stats.t.sf(t, df))


def cells_of(model, fam, key, shift=0.0, scale=1.0):
    return [np.array([(x[key] - shift) * scale for x in rows if x['model'] == model and x['ci'] == ci])
            for ci in range(8) if CELLS[ci][2] == fam]


rng = np.random.default_rng(SEED)
res = dict(proxy='HELD2 R-B (old R arm), 120 systems', margin=M, B=B, observed={}, power={})
H = []
for model in ('avici', 'cdfm'):
    for fam in ('lin', 'rff'):
        H.append((f'P6-1{"A" if model == "avici" else "C"}-{fam}', 'ni', model, fam))
for fam in ('lin', 'rff'):
    H.append((f'P6-2C-{fam}', 'sup', 'cdfm', fam))


def pvalue(kind, model, fam, cells_Q0=None, cells_QA=None, cells_D2=None):
    if kind == 'ni':
        return max(strat(cells_Q0, -M)[4], strat(cells_QA, -M)[4])
    return strat(cells_D2, 0.0)[4]


for hid, kind, model, fam in H:
    if kind == 'ni':
        cq0, cqa = cells_of(model, fam, 'Q0'), cells_of(model, fam, 'QA')
        e0, eA = strat(cq0, -M), strat(cqa, -M)
        res['observed'][hid] = dict(Q0=dict(mean=e0[0], se=e0[1], p=e0[4]), QA=dict(mean=eA[0], se=eA[1], p=eA[4]),
                                    H_plain=float(np.mean([x['H_plain'] for x in rows if x['model'] == model and x['fam'] == fam])))
        variants = dict(observed=(0.0, 1.0), shifted_toward_margin=(0.01, 1.0))
    else:
        cd = cells_of(model, fam, 'D2')
        e = strat(cd, 0.0)
        res['observed'][hid] = dict(D2=dict(mean=e[0], se=e[1], p=e[4]),
                                    phi_frozen=float(np.mean([x['phi_frozen'] for x in rows if x['model'] == 'cdfm' and x['fam'] == fam])),
                                    phi_R=float(np.mean([x['phi_R'] for x in rows if x['model'] == 'cdfm' and x['fam'] == fam])))
        variants = dict(observed=(0.0, 1.0), halved=(0.0, 0.5))
    res['power'][hid] = {}
    for vname, (shift, scale) in variants.items():
        hits = dict(strict=0, nominal=0)
        for _ in range(B):
            idx = [rng.integers(0, 15, 15) for _ in range(4)]
            if kind == 'ni':
                c0 = [c[i] for c, i in zip(cells_of(model, fam, 'Q0', shift), idx)]
                cA = [c[i] for c, i in zip(cells_of(model, fam, 'QA', shift), idx)]
                p = pvalue(kind, model, fam, c0, cA)
            else:
                c2 = [c[i] for c, i in zip(cells_of(model, fam, 'D2', 0.0, scale), idx)]
                p = pvalue(kind, model, fam, cells_D2=c2)
            hits['strict'] += p <= 0.05 / 6
            hits['nominal'] += p <= 0.05
        res['power'][hid][vname] = {k: v / B for k, v in hits.items()}

res['rows'] = rows
DEST.write_text(json.dumps(res, indent=1, default=float))
for hid, o in res['observed'].items():
    print(hid, json.dumps({k: (round(v, 4) if isinstance(v, float) else {q: round(w, 4) for q, w in v.items()}) for k, v in o.items()}),
          '| power', res['power'][hid])
