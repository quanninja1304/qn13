"""P-N4 (rules PN4 v1, locked 2026-11-21 at commit 05b6945): systems, inputs, padding at k = 20 and k = 40.

Imports the frozen P-N2 module common2.py (fddfadd) and, through it, the frozen P-N1 module common.py, unchanged.
Deterministic given the seeds. No metric is computed here.
"""
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RUNS4 = HERE.parent                                   # artifacts/n4_runs
ART = RUNS4.parent                                    # artifacts
REPO = ART.parent                                     # safety_prior
OUT4 = RUNS4 / 'pn4_out'
sys.path.insert(0, str(ART / 'n2_runs' / 'pn2'))
from common2 import CELLS, N, target, zscore, sha, pad_params, pad_graph, pad_data, padding2   # frozen P-N2 and P-N1

RFF_CELLS = (1, 3, 5, 7)                              # P-N1 cell order: (10,1,rff), (10,2,rff), (20,1,rff), (20,2,rff)
SETS4 = {'PN4': (440000, 20), 'DEV4': (450000, 2)}    # rules PN4 §1
KS = (20, 40)


def systems4(set_name):
    base, reps = SETS4[set_name]
    return [(f'{set_name}-c{ci}-r{r}', ci, base + 1000 * ci + r) for ci in RFF_CELLS for r in range(reps)]


def eT_of(ci):
    return int(CELLS[ci][1])


def conds4(ci):
    """The five inputs of a system (rules PN4 §1): k0, then (k, e) for k in (20, 40) and e in (0, e_T)."""
    return ['k0'] + [f'k{k}_e{e}' for k in KS for e in (0, eT_of(ci))]


def parse(cond):
    k, e = cond.split('_')
    return int(k[1:]), int(e[1:])


def padding_generic(ci, seed, k, e):
    """The three frozen P-N2 functions with k as a parameter (rules PN4 §1). Used at k = 40; gate G1 checks k = 20."""
    mech = CELLS[ci][2]
    P = pad_params(seed, mech, k=k)
    g = pad_graph(P, float(e), k=k)
    x64 = pad_data(P, g, mech, 1.0)
    deg = g.sum(0) + g.sum(1)
    return dict(P=zscore(x64), g=g, e=float(e), s=1.0, n_edges=int(g.sum()), n_isolated=int((deg == 0).sum()), x64=x64)


def padding4(ci, seed, k, e):
    if k == 20:
        return padding2(ci, seed, f'e{e}')                # exactly the P-N2 call (rules PN4 §1)
    return padding_generic(ci, seed, k, e)


def assemble4(sid, ci, seed, cond):
    """Input table of (system, condition); k0 is the target block alone, as in P-N1 and P-N2."""
    t = target(sid, ci, seed)
    if 'x0' not in t:
        t['x0'] = zscore(t['x'])
    if cond == 'k0':
        return t['x0'], t, None
    k, e = parse(cond)
    pad = padding4(ci, seed, k, e)
    x = zscore(np.concatenate([t['x'], pad['P']], 1))
    dT = t['x'].shape[1]
    assert np.ascontiguousarray(x[:, :dT]).tobytes() == t['x0'].tobytes(), 'target block not bitwise identical'
    return x, t, pad


def key4(sid, cond):
    return f'{sid}__{cond}'
