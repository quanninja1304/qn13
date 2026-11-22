"""P-N5 measures on the real block (rules PN5 v1 §4). Pure functions over saved outputs, as in P-N1 (metrics.py) and P-N2.

Skeleton, NATIVE reading:
  AVICI: max(p_ij, p_ji) > 0.5;  CDFM: adjacency OR its transpose;  PC, GES: every edge type of the full-table output graph.
CDFM extra readings (descriptive): FIXED max(p_ij, p_ji) > 0.5; FROZEN p_ij > tau(k0), diagonal removed, symmetrized.
dp: mean |p_ij - p_ij(k0)| over the 110 ordered pairs; flips: changed skeleton states over the 55 unordered pairs.
"""
import numpy as np

DT = 11


def sym(m):
    return ((m + m.T) > 0).astype(np.int8)


def upper(s):
    return s[np.triu_indices(s.shape[0], 1)]


def skel_native(alg, o, dT=DT):
    if alg == 'avici':
        p = o['probs'][:dT, :dT]
        return (np.maximum(p, p.T) > 0.5).astype(np.int8)
    if alg == 'cdfm':
        return sym(o['adj_native'][:dT, :dT].astype(np.int8))
    return sym(o['skel'][:dT, :dT].astype(np.int8))


def skel_fixed(o, dT=DT):
    p = o['probs'][:dT, :dT]
    return (np.maximum(p, p.T) > 0.5).astype(np.int8)


def skel_frozen(o, thr0, dT=DT):
    p = o['probs'][:dT, :dT]
    a = (p > thr0).astype(np.int8)
    np.fill_diagonal(a, 0)
    return sym(a)


def dp(o1, o0, dT=DT):
    a, b = o1['probs'][:dT, :dT], o0['probs'][:dT, :dT]
    off = ~np.eye(dT, dtype=bool)
    return float(np.abs(a - b)[off].mean())


def flips(s1, s0):
    return int((upper(s1) != upper(s0)).sum())


def m_edges(s):
    return int(upper(s).sum())


def measures(alg, o, o0, dT=DT):
    """Measures of one output o against the k0 output o0 of the same algorithm and table."""
    s, s0 = skel_native(alg, o, dT), skel_native(alg, o0, dT)
    m, m0 = m_edges(s), m_edges(s0)
    out = dict(flips=flips(s, s0), m=m, dm=m - m0, absdm=abs(m - m0), changed=(upper(s) != upper(s0)))
    if alg in ('avici', 'cdfm'):
        out['dp'] = dp(o, o0, dT)
    if alg == 'cdfm':
        thr0 = float(o0['threshold'])
        out['thr'] = float(o['threshold'])
        out['dthr'] = out['thr'] - thr0
        sf, sf0 = skel_fixed(o, dT), skel_fixed(o0, dT)
        sz, sz0 = skel_frozen(o, thr0, dT), skel_frozen(o0, thr0, dT)
        out.update(flips_fixed=flips(sf, sf0), flips_frozen=flips(sz, sz0), m_fixed=m_edges(sf), m_frozen=m_edges(sz))
    return out


def pair_names(names, dT=DT):
    iu = np.triu_indices(dT, 1)
    return [f'{names[i]} - {names[j]}' for i, j in zip(*iu)]
