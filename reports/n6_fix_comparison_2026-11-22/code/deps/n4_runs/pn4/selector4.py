"""CDFM threshold selector for P-N4 (rules PN4 v1 §0 step 2, §2).

features, logit_thr, count_target, hybrid and shapley are copied from the frozen P-N3 file partA_cdfm.py (7fbd635), which
runs its whole analysis on import. Only the layout changed: the calibration weights are loaded lazily. Gates G3 and G4 check
that the copy reproduces the stored CDFM thresholds and the old P-N3 / HELD2 numbers.
"""
import os, itertools
import numpy as np

_W, _FEAT = None, None


def load_selector():
    """Calibration weights and feature names stored in the CDFM checkpoint (same call as partA_cdfm.py)."""
    global _W, _FEAT
    if _W is None:
        os.environ.setdefault('HF_HUB_OFFLINE', '1')
        from cdfm import CDFM
        from common4 import ART
        m = CDFM.from_pretrained(str(ART / 'n1_models_cpu' / 'checkpoints/cdfm'), device='cpu', threshold=None)
        _W = np.asarray(m.calibration_coefficients_, float)
        _FEAT = list(m.calibration_feature_names_)
    return _W, _FEAT


def features(P):
    """Exactly the feature map of cdfm.utils.suggest_threshold (probabilities input)."""
    _, FEAT = load_selector()
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
    W, _ = load_selector()
    return float(W[0] + W[1:] @ features(P))


def thr(P):
    return float(1 / (1 + np.exp(-logit_thr(P))))


def count_target(probs_T, thr_):
    """m(A, tau) of rules PN4 §2: unordered target pairs with max(A_ij, A_ji) > tau (strict)."""
    a = (probs_T > thr_).astype(np.int8); np.fill_diagonal(a, 0)
    s = (a + a.T) > 0
    return int(s[np.triu_indices(s.shape[0], 1)].sum())


def hybrid(P0, P1, dT, aT, aP, aX):
    """H(aT, aP, aX) of rules PN4 §2: target, padding and cross blocks from P^aT, P^aP, P^aX."""
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
