"""P-N4 design inputs (rules PN4 §6): per-cell means and SDs of the P-N4 contrasts on old CDFM RFF outputs.

Read-only on frozen outputs: P-N2 EXP2 (20 RFF systems) and HELD2 (60 RFF systems), plain runs at e = 0 and e = e_T.
Descriptive design computation only; nothing here is a P-N4 result.
Contrasts (rules PN4 §2): D1 cross-block mean, D2 NATIVE threshold, D3a/D3b X-only swap (counted on e = 0 target
scores), S/T split anchored at the e = 0 threshold, T+S, T-S.
The selector functions are copied from the frozen P-N3 partA_cdfm.py (that file runs its analysis on import).
usage (from anywhere): <venv python> -I pn4_design_inputs.py  ->  pn4_design_inputs.json next to this file
"""
import os, sys, json
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ART = REPO / 'artifacts'
OUT2 = ART / 'n2_runs' / 'pn2_out' / 'cdfm'
os.environ.setdefault('HF_HUB_OFFLINE', '1')
from cdfm import CDFM
_m = CDFM.from_pretrained(str(ART / 'n1_models_cpu' / 'checkpoints/cdfm'), device='cpu', threshold=None)
W = np.asarray(_m.calibration_coefficients_, float); FEAT = list(_m.calibration_feature_names_)
CELLS = [(dT, e, m) for dT in (10, 20) for e in (1, 2) for m in ('lin', 'rff')]   # P-N1 cell order
RFF = (1, 3, 5, 7)


def features(P):
    D = P.shape[0]; mask = ~np.eye(D, dtype=bool); probs = P[mask]
    if probs.min() < 0.0 or probs.max() > 1.0:
        probs = 1.0 / (1.0 + np.exp(-np.clip(probs, -50.0, 50.0)))
    ps = np.sort(probs)[::-1]; n = len(ps)
    fv = dict(mean=float(np.mean(probs)), std=float(np.std(probs)), p25=float(np.percentile(probs, 25)),
              p50=float(np.percentile(probs, 50)), p75=float(np.percentile(probs, 75)), p90=float(np.percentile(probs, 90)),
              logD=np.log(D))
    gaps = ps[:-1] - ps[1:]
    fv['median_gap'] = float(np.median(gaps)) if len(gaps) > 0 else 0.0
    fv['max_gap'] = float(np.max(gaps)) if len(gaps) > 0 else 0.0
    denom = max(ps[0] - ps[-1], 1e-10); y = (ps - ps[-1]) / denom; x = np.arange(n) / max(n - 1, 1); diff = y - x
    mi = max(1, min(int(0.5 * D), n - 1)); ki = mi + np.argmax(diff[mi:])
    fv['knee_T'] = float((ps[ki] + ps[ki + 1]) / 2) if ki < n - 1 else float(ps[ki])
    return np.array([fv[f] for f in FEAT])


def thr(P):
    return float(1 / (1 + np.exp(-(W[0] + W[1:] @ features(P)))))


def count_target(pT, t):
    a = (pT > t).astype(np.int8); np.fill_diagonal(a, 0); s = (a + a.T) > 0
    return int(s[np.triu_indices(s.shape[0], 1)].sum())


def hybrid(P0, P1, dT, aT, aP, aX):
    H = P0.copy()
    if aT: H[:dT, :dT] = P1[:dT, :dT]
    if aP: H[dT:, dT:] = P1[dT:, dT:]
    if aX: H[:dT, dT:] = P1[:dT, dT:]; H[dT:, :dT] = P1[dT:, :dT]
    return H


def per_system(P0, P1, t0, t1, dT):
    cross = lambda P: np.concatenate([P[:dT, dT:].ravel(), P[dT:, :dT].ravel()]).mean()
    tx = thr(hybrid(P0, P1, dT, 0, 0, 1))
    T0, T1 = P0[:dT, :dT], P1[:dT, :dT]
    m00, m10, m11 = count_target(T0, t0), count_target(T1, t0), count_target(T1, t1)
    S, T = m10 - m00, m11 - m10
    return dict(D1=cross(P1) - cross(P0), D2=t1 - t0, D3a=tx - t0, D3b=count_target(T0, tx) - m00,
                S=S, T=T, TpS=T + S, TmS=T - S)


def strat(v, cells):
    by = {}
    for x, c in zip(v, cells):
        by.setdefault(c, []).append(float(x))
    keys = sorted(by); w = 1.0 / len(keys)
    ac = [w ** 2 * np.var(by[c], ddof=1) / len(by[c]) for c in keys]
    th = w * sum(np.mean(by[c]) for c in keys); se = float(np.sqrt(sum(ac)))
    df = sum(ac) ** 2 / sum(a ** 2 / (len(by[c]) - 1) for a, c in zip(ac, keys)) if se > 0 else None
    q = stats.t.ppf(0.975, df) if df else 0.0
    return dict(theta=float(th), se=se, df=df, ci95=[th - q * se, th + q * se],
                cell_mean={str(c): float(np.mean(by[c])) for c in keys},
                cell_sd={str(c): float(np.std(by[c], ddof=1)) for c in keys},
                cell_n={str(c): len(by[c]) for c in keys})


out = dict(note='Descriptive design computation on old outputs (rules PN4 §6); not a P-N4 result.',
           selector_features=FEAT)
for setname, reps in (('EXP2', 5), ('HELD2', 15)):
    recs, cells, gate = [], [], 0.0
    for ci in RFF:
        eT = int(CELLS[ci][1]); dT = CELLS[ci][0]
        for r in range(reps):
            sid = f'{setname}-c{ci}-r{r}'
            o0 = np.load(OUT2 / f'{sid}__e0__plain.npz'); o1 = np.load(OUT2 / f'{sid}__e{eT}__plain.npz')
            P0, P1 = np.asarray(o0['probs'], float), np.asarray(o1['probs'], float)
            t0, t1 = float(o0['threshold']), float(o1['threshold'])
            gate = max(gate, abs(thr(P0) - t0), abs(thr(P1) - t1))
            recs.append(per_system(P0, P1, t0, t1, dT)); cells.append(ci)
    out[setname] = dict(n_systems=len(recs), selector_reproduction_max_abs=gate,
                        contrasts={q: strat([x[q] for x in recs], cells) for q in ('D1', 'D2', 'D3a', 'D3b', 'S', 'T', 'TpS', 'TmS')},
                        frac_T_below_minus_abs_S=float(np.mean([x['T'] < -abs(x['S']) for x in recs])),
                        frac_D3b_negative=float(np.mean([x['D3b'] < 0 for x in recs])))
(HERE / 'pn4_design_inputs.json').write_text(json.dumps(out, indent=1))
for s in ('EXP2', 'HELD2'):
    print(s, {q: round(v['theta'], 4) for q, v in out[s]['contrasts'].items()}, 'gate', out[s]['selector_reproduction_max_abs'])
