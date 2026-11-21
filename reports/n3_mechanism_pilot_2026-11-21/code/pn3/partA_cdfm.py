"""P-N3 Part A (rules v1 §1): CDFM RFF threshold selector, 2^3 factorial over the score-matrix blocks. No model run.

Blocks of the D x D probability matrix fed to cdfm.utils.suggest_threshold: T (target), P (padding), X (both cross blocks).
Each taken from the plain output at e = 0 or at e = e_T of the same EXP2 system. Gate A0 reproduces the saved thresholds.
usage: partA_cdfm.py  ->  pn3_out/partA.json
"""
import os, sys, json, itertools
from pathlib import Path
PN3 = Path(__file__).resolve().parent
sys.path.insert(0, str(PN3)); sys.path.insert(0, str(PN3.parents[1] / 'n2_runs' / 'pn2'))
os.environ.setdefault('HF_HUB_OFFLINE', '1')
import numpy as np
from scipy import stats
from common2 import *
OUT3 = PN3.parent / 'pn3_out'; OUT3.mkdir(parents=True, exist_ok=True)
from cdfm import CDFM
_m = CDFM.from_pretrained(str(ART / 'n1_models_cpu' / 'checkpoints/cdfm'), device='cpu', threshold=None)
W = np.asarray(_m.calibration_coefficients_, float); FEAT = list(_m.calibration_feature_names_)
BOOT_SEED = 20261121


def features(P):
    """Exactly the feature map of cdfm.utils.suggest_threshold (probabilities input)."""
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


def logit_thr(P):
    return float(W[0] + W[1:] @ features(P))


def count_target(probs_T, thr):
    a = (probs_T > thr).astype(np.int8); np.fill_diagonal(a, 0)
    s = (a + a.T) > 0
    return int(s[np.triu_indices(s.shape[0], 1)].sum())


def hybrid(P0, P1, dT, aT, aP, aX):
    H = P0.copy()
    if aT: H[:dT, :dT] = P1[:dT, :dT]
    if aP: H[dT:, dT:] = P1[dT:, dT:]
    if aX: H[:dT, dT:] = P1[:dT, dT:]; H[dT:, :dT] = P1[dT:, :dT]
    return H


def shapley(v):
    """3-player Shapley values; v maps frozenset of players {'T','P','X'} to value, v(empty) = 0."""
    N = ('T', 'P', 'X'); w = {0: 1 / 3, 1: 1 / 6, 2: 1 / 3}
    out = {}
    for i in N:
        others = [j for j in N if j != i]; tot = 0.0
        for r in range(3):
            for S in itertools.combinations(others, r):
                S = frozenset(S); tot += w[len(S)] * (v[S | {i}] - v[S])
        out[i] = tot
    return out


def strat(values, cells):
    by = {}
    for x, c in zip(values, cells):
        by.setdefault(c, []).append(float(x))
    keys = sorted(by); w = 1.0 / len(keys)
    means = [np.mean(by[c]) for c in keys]; ac = [w ** 2 * np.var(by[c], ddof=1) / len(by[c]) for c in keys]
    th = w * sum(means); se2 = sum(ac); se = float(np.sqrt(se2))
    if se2 > 0:
        df = se2 ** 2 / sum(a ** 2 / (len(by[c]) - 1) for a, c in zip(ac, keys)); q = stats.t.ppf(0.975, df)
        return dict(theta=float(th), ci95=[float(th - q * se), float(th + q * se)], df=float(df))
    return dict(theta=float(th), ci95=[float(th), float(th)], df=None)


rows, a0 = [], 0.0
for sid, ci, seed in systems2('EXP2'):
    dT, eT, mech = CELLS[ci]
    if mech != 'rff':
        continue
    o0 = np.load(OUT2 / 'cdfm' / f'{key2(sid, "e0", "plain")}.npz'); o1 = np.load(OUT2 / 'cdfm' / f'{key2(sid, rep_cond(ci), "plain")}.npz')
    P0, P1 = np.asarray(o0['probs']), np.asarray(o1['probs'])
    for P, o in ((P0, o0), (P1, o1)):
        a0 = max(a0, abs(1 / (1 + np.exp(-logit_thr(P))) - float(o['threshold'])))
    L, F, thr = {}, {}, {}
    for aT, aP, aX in itertools.product((0, 1), repeat=3):
        H = hybrid(P0, P1, dT, aT, aP, aX)
        L[(aT, aP, aX)] = logit_thr(H); F[(aT, aP, aX)] = features(H); thr[(aT, aP, aX)] = 1 / (1 + np.exp(-L[(aT, aP, aX)]))
    base = L[(0, 0, 0)]
    S2key = lambda S: (int('T' in S), int('P' in S), int('X' in S))
    allS = [frozenset(S) for r in range(4) for S in itertools.combinations(('T', 'P', 'X'), r)]
    phi = shapley({S: L[S2key(S)] - base for S in allS})
    phi_feat = {i: {f: 0.0 for f in FEAT} for i in ('T', 'P', 'X')}
    for k, f in enumerate(FEAT):
        pf = shapley({S: W[1 + k] * (F[S2key(S)][k] - F[(0, 0, 0)][k]) for S in allS})
        for i in pf:
            phi_feat[i][f] = pf[i]
    # 2^3 effects (coded -1/+1): main effects and interactions on the logit
    def eff(sign):
        return float(np.mean([L[k] * np.prod([1 if k[j] else -1 for j in sign]) for k in L]) * 2)
    effects = dict(T=eff([0]), P=eff([1]), X=eff([2]), TP=eff([0, 1]), TX=eff([0, 2]), PX=eff([1, 2]), TPX=eff([0, 1, 2]))
    T0, T1 = P0[:dT, :dT], P1[:dT, :dT]
    counts = {f'{k[0]}{k[1]}{k[2]}': dict(on_eT_scores=count_target(T1, thr[k]), on_e0_scores=count_target(T0, thr[k])) for k in thr}
    # local-threshold counterfactual policy (statistics and D of the target block only)
    loc0, loc1 = 1 / (1 + np.exp(-logit_thr(T0))), 1 / (1 + np.exp(-logit_thr(T1)))
    n_e0, n_eT = count_target(T0, float(o0['threshold'])), count_target(T1, float(o1['threshold']))
    rows.append(dict(sys=sid, ci=ci, dT=dT, d_logit=L[(1, 1, 1)] - base, phi=phi, phi_feat=phi_feat, effects=effects, counts=counts,
                     rep_native=n_eT - n_e0, score_part_e0anchor=count_target(T1, float(o0['threshold'])) - n_e0,
                     threshold_part_e0anchor=n_eT - count_target(T1, float(o0['threshold'])),
                     rep_local_policy=count_target(T1, loc1) - count_target(T0, loc0)))
cells = [r['ci'] for r in rows]
summ = dict(gate_A0=dict(max_abs=a0, pass_=bool(a0 <= 1e-12)), n_systems=len(rows),
            d_logit=strat([r['d_logit'] for r in rows], cells),
            phi={i: strat([r['phi'][i] for r in rows], cells) for i in ('T', 'P', 'X')},
            phi_share_of_d_logit={i: float(np.mean([r['phi'][i] for r in rows]) / np.mean([r['d_logit'] for r in rows])) for i in ('T', 'P', 'X')},
            phi_by_feature={i: {f: float(np.mean([r['phi_feat'][i][f] for r in rows])) for f in FEAT} for i in ('T', 'P', 'X')},
            effects={k: strat([r['effects'][k] for r in rows], cells) for k in rows[0]['effects']},
            counts_on_eT_scores={k: float(np.mean([r['counts'][k]['on_eT_scores'] for r in rows])) for k in rows[0]['counts']},
            counts_on_e0_scores={k: float(np.mean([r['counts'][k]['on_e0_scores'] for r in rows])) for k in rows[0]['counts']},
            rep_native=strat([r['rep_native'] for r in rows], cells),
            score_part_e0anchor=strat([r['score_part_e0anchor'] for r in rows], cells),
            threshold_part_e0anchor=strat([r['threshold_part_e0anchor'] for r in rows], cells),
            rep_local_policy=strat([r['rep_local_policy'] for r in rows], cells))
(OUT3 / 'partA.json').write_text(json.dumps(dict(summary=summ, rows=rows), indent=1, default=float))
print(json.dumps({k: summ[k] for k in ('gate_A0', 'd_logit', 'phi', 'phi_share_of_d_logit', 'rep_native', 'score_part_e0anchor',
                                       'threshold_part_e0anchor', 'rep_local_policy')}, indent=1))
