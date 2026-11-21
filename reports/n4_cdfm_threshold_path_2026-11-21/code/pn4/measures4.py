"""P-N4 per-system measures (rules PN4 v1 §2 locked contrasts, §5 descriptive). Pure functions of CDFM outputs.

P0, P1: D x D probability matrices at e = 0 and e = e_T; t0, t1: the NATIVE thresholds stored by CDFM for those outputs
(tau^0, tau^1 of rules §2; gate G3 checks that the copied selector reproduces them). Hybrid thresholds come from the copy.
"""
import itertools
import numpy as np
from selector4 import features, logit_thr, count_target, hybrid, shapley, load_selector

KEYS = list(itertools.product((0, 1), repeat=3))       # (target, padding, cross) taken from e = 0 (0) or e = e_T (1)


def sym(m):
    return ((m + m.T) > 0).astype(np.int8)


def count_upper(sk):
    return int(sk[np.triu_indices(sk.shape[0], 1)].sum())


def f1_skeleton(adj_T, g):
    """F1 of a target-block skeleton against the true skeleton (same definition as HELD2)."""
    dT = g.shape[0]; iu = np.triu_indices(dT, 1)
    t = ((g + g.T) > 0)[iu]; pr = sym(adj_T)[iu] > 0
    tp, fp, fn = int((t & pr).sum()), int((~t & pr).sum()), int((t & ~pr).sum())
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


def cross_mean(P, dT):
    return float(np.concatenate([P[:dT, dT:].ravel(), P[dT:, :dT].ravel()]).mean())


def block_means(P, dT, gP):
    """Mean probability by block; the padding block is split by the skeleton of the padding graph at e = e_T (rules §5)."""
    D = P.shape[0]; k = D - dT
    offT, offP = ~np.eye(dT, dtype=bool), ~np.eye(k, dtype=bool)
    Pb = P[dT:, dT:]
    adj = ((gP + gP.T) > 0) & offP
    non = ~((gP + gP.T) > 0) & offP
    return dict(target=float(P[:dT, :dT][offT].mean()), cross=cross_mean(P, dT), padding=float(Pb[offP].mean()),
                padding_edge_pairs=float(Pb[adj].mean()) if adj.any() else None,
                padding_nonedge_pairs=float(Pb[non].mean()), whole=float(P[~np.eye(D, dtype=bool)].mean()),
                n_padding_edge_pairs=int(adj.sum()), n_padding_nonedge_pairs=int(non.sum()))


def locked_contrasts(P0, P1, t0, t1, dT):
    """D1, D2, D3a, D3b, S, T, T+S, T-S of rules §2 (decomposition anchored at the e = 0 threshold)."""
    T0, T1 = P0[:dT, :dT], P1[:dT, :dT]
    m00, m10, m11 = count_target(T0, t0), count_target(T1, t0), count_target(T1, t1)
    tx = 1 / (1 + np.exp(-logit_thr(hybrid(P0, P1, dT, 0, 0, 1))))
    S, T = m10 - m00, m11 - m10
    return dict(D1=cross_mean(P1, dT) - cross_mean(P0, dT), D2=t1 - t0, D3a=float(tx) - t0,
                D3b=count_target(T0, float(tx)) - m00, S=S, T=T, TpS=T + S, TmS=T - S,
                m_e0=m00, m_eT=m11, thr_X_only=float(tx))


def descriptive(P0, P1, t0, t1, dT):
    """Full 2^3 design (as P-N3 part A), padding-only swap, alternative anchor (rules §5)."""
    W, FEAT = load_selector()
    T0, T1 = P0[:dT, :dT], P1[:dT, :dT]
    L, F, th = {}, {}, {}
    for key in KEYS:
        H = hybrid(P0, P1, dT, *key)
        L[key] = logit_thr(H); F[key] = features(H); th[key] = float(1 / (1 + np.exp(-L[key])))
    base = L[(0, 0, 0)]
    s2k = lambda S: (int('T' in S), int('P' in S), int('X' in S))
    allS = [frozenset(S) for r in range(4) for S in itertools.combinations(('T', 'P', 'X'), r)]
    phi = shapley({S: L[s2k(S)] - base for S in allS})
    phi_feat = {i: {} for i in ('T', 'P', 'X')}
    for j, f in enumerate(FEAT):
        pf = shapley({S: W[1 + j] * (F[s2k(S)][j] - F[(0, 0, 0)][j]) for S in allS})
        for i in pf:
            phi_feat[i][f] = pf[i]

    def eff(idx):
        return float(np.mean([L[k] * np.prod([1 if k[j] else -1 for j in idx]) for k in L]) * 2)
    effects = dict(T=eff([0]), P=eff([1]), X=eff([2]), TP=eff([0, 1]), TX=eff([0, 2]), PX=eff([1, 2]), TPX=eff([0, 1, 2]))
    counts = {f'{a}{b}{c}': dict(on_e0_scores=count_target(T0, th[(a, b, c)]), on_eT_scores=count_target(T1, th[(a, b, c)]))
              for (a, b, c) in KEYS}
    m00, m01 = count_target(T0, t0), count_target(T0, t1)
    m11 = count_target(T1, t1)
    return dict(d_logit=L[(1, 1, 1)] - base, phi=phi, phi_feat=phi_feat, effects=effects, counts=counts,
                P_only_dthr=th[(0, 1, 0)] - t0, P_only_dm_e0_scores=count_target(T0, th[(0, 1, 0)]) - m00,
                alt_S=m11 - m01, alt_T=m01 - m00)
