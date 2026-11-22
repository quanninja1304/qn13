"""P-N6 measures (rules PN6 v1 §3-§4). Pure functions over saved outputs.

Skeletons on the target block (frozen P-N1 metrics):
  plain NATIVE: skel_native (AVICI 0.5 on max(p_ij, p_ji); CDFM adjacency OR its transpose)
  R-L / R-H:    AVICI 0.5 on the stitched component probabilities; CDFM the stitched per-component NATIVE adjacency
  CDFM decoder controls on plain outputs: FIXED skel_fixed (0.5); FROZEN skel_frozen_cdfm with the plain k0 threshold;
  LOCAL: the frozen P-N4 selector (selector4.thr) on the target block's probabilities (D = d_T), then p_ij > tau.
F1: frozen metrics.f1 against the true target skeleton.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import json
import numpy as np
import common6                                            # sets sys.path for the frozen modules
from metrics import skel_native, skel_fixed, skel_frozen_cdfm, f1, triu   # frozen P-N1
import selector4 as SEL                                   # frozen P-N4 (uses common4 for the checkpoint path)


def load(path):
    z = np.load(path, allow_pickle=False)
    d = {n: z[n] for n in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


def upper(s):
    return s[triu(s.shape[0])]


def flips(a, b):
    return int((upper(a) != upper(b)).sum())


def m_edges(s):
    return int(upper(s).sum())


def sym(a):
    a = (np.asarray(a) != 0).astype(np.int8)
    np.fill_diagonal(a, 0)
    return ((a + a.T) > 0).astype(np.int8)


def skel_R(model, o, dT):
    if model == 'avici':
        return skel_fixed(o['probs_T'], dT)
    return sym(o['adj_T'][:dT, :dT])


def local_threshold(o, dT):
    return SEL.thr(np.asarray(o['probs'][:dT, :dT], float))


def skel_local(o, dT, tau=None):
    PT = np.asarray(o['probs'][:dT, :dT], float)
    tau = SEL.thr(PT) if tau is None else tau
    return sym(PT > tau), tau


def skeletons(model, outs, dT):
    """outs: {(fix_source, cond): output} with fix_source in plain / RL / RH and cond in k0 / A20 / S20.
    Returns {(fix, cond): skeleton} for plain, RL, RH and, for CDFM, FIXED, FROZEN, LOCAL."""
    S = {}
    for c in ('k0', 'A20', 'S20'):
        S[('plain', c)] = skel_native(model, outs[('plain', c)], dT)
        for arm in ('RL', 'RH'):
            S[(arm, c)] = skel_R(model, outs[(arm, c)], dT)
    if model == 'cdfm':
        thr0 = float(outs[('plain', 'k0')]['threshold'])
        for c in ('k0', 'A20', 'S20'):
            o = outs[('plain', c)]
            S[('FIXED', c)] = skel_fixed(o['probs'], dT)
            S[('FROZEN', c)] = skel_frozen_cdfm(o, dT, thr0)
            S[('LOCAL', c)] = skel_local(o, dT)[0]
    return S


def system_measures(model, outs, dT, g):
    """Per-system measures of rules §4 for every fix and padded input."""
    S = skeletons(model, outs, dT)
    fixes = sorted({f for f, _ in S})
    f1p0 = f1(S[('plain', 'k0')], g)
    res = {}
    for fx in fixes:
        r = dict(F1_k0=f1(S[(fx, 'k0')], g), phi_k0=flips(S[(fx, 'k0')], S[('plain', 'k0')]))
        r['Q0'] = r['F1_k0'] - f1p0
        for c in ('A20', 'S20'):
            fc = f1(S[(fx, c)], g)
            r[f'F1_{c}'] = fc
            r[f'Q_{c}'] = fc - f1p0
            r[f'G_{c}'] = fc - f1(S[('plain', c)], g)
            r[f'phi_{c}'] = flips(S[(fx, c)], S[('plain', 'k0')])
            r[f'sigma_{c}'] = flips(S[(fx, c)], S[(fx, 'k0')])
            r[f'dm_{c}'] = m_edges(S[(fx, c)]) - m_edges(S[('plain', 'k0')])
        res[fx] = r
    res['m0'] = m_edges(S[('plain', 'k0')])
    return res
