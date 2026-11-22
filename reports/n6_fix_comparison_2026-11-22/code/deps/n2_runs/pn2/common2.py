"""P-N2 (rules v1, locked 2026-11-20 at commit 5c2c76c): sets, coupled padding generator, input assembly.

Everything is deterministic given the seeds. No metric is computed here.
Target systems come from the frozen P-N1 module `common.py` (read-only import).
"""
import sys, json, hashlib
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RUNS2 = HERE.parent                                   # artifacts/n2_runs
ART = RUNS2.parent                                    # artifacts
PN1 = ART / 'n1_runs' / 'pn1'
OUT2 = RUNS2 / 'pn2_out'
sys.path.insert(0, str(PN1))
from common import CELLS, N, target, zscore, sha      # frozen P-N1, rules v2/v2.1/v2.2

K = 20
N_RFF = 100
SETS2 = {'DEV2': (410000, 2), 'EXP2': (420000, 5)}   # HELD2 base 430000 reserved (rules v1 §2): never generated here
CONDS = ['k0', 'e0', 'e0.5', 'e1', 'e2', 'e3', 's0.25', 's0.5']   # s=0 is e0 and s=1 is e2 (aliases, §3)
PADDED = CONDS[1:]


def systems2(set_name):
    base, reps = SETS2[set_name]
    return [(f'{set_name}-c{ci}-r{r}', ci, base + ci * 1000 + r) for ci in range(8) for r in range(reps)]


def cond_es(cond):
    """(e, s) of a padded condition."""
    if cond.startswith('e'):
        return float(cond[1:]), 1.0
    if cond.startswith('s'):
        return 2.0, float(cond[1:])
    raise ValueError(cond)


def rep_cond(ci):
    """REP level e = e_T of the cell."""
    return f'e{int(CELLS[ci][1])}'


def pad_params(seed, mech, k=K, n=N):
    """All randomness of the padding block, drawn once in the order fixed by rules v1 §3."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, 20261120, 2]))
    P = dict(pi=rng.permutation(k), U=rng.uniform(size=(k, k)))
    P['noise_scale'] = rng.uniform(0.2, 2.0, size=k)
    P['bias'] = rng.uniform(-3, 3, size=k)
    P['Z'] = rng.normal(size=(n, k))                  # drawn once for the whole block
    if mech == 'lin':
        sgn = rng.choice([-1, 1], size=(k, k))        # AVICI SignedUniform: sign first, then magnitude
        mag = rng.uniform(1, 3, size=(k, k))
        P['W'] = sgn * mag
    elif mech == 'rff':
        P['ls'] = rng.uniform(7, 10, size=k)
        P['c'] = rng.uniform(10, 20, size=k)
        P['G'] = rng.normal(size=(k, k, N_RFF))
        P['b'] = rng.uniform(0, 2 * np.pi, size=(k, N_RFF))
        P['w'] = rng.normal(size=(k, N_RFF))
    else:
        raise ValueError(mech)
    return P


def pad_graph(P, e, k=K):
    """Edge pi[a] -> pi[b] iff a < b and U[a, b] < p_e; nested in e by construction. g[i, j] = 1 means i -> j."""
    p = min(2 * e / (k - 1), 0.99)
    pi, U = P['pi'], P['U']
    g = np.zeros((k, k), np.int8)
    for a in range(k):
        for b in range(a + 1, k):
            if U[a, b] < p:
                g[pi[a], pi[b]] = 1
    return g


def omega(P, j, pa):
    return P['G'][j][pa, :] / P['ls'][j]


def pad_data(P, g, mech, s=1.0):
    """Float64 padding block before z-scoring (rules v1 §3)."""
    k = g.shape[0]
    n = P['Z'].shape[0]
    x = np.zeros((n, k))
    for j in P['pi']:
        pa = np.where(g[:, j])[0]
        z = P['noise_scale'][j] * P['Z'][:, j]
        if mech == 'lin':
            f = x[:, pa] @ P['W'][pa, j] if len(pa) else 0.0
        else:
            phi = np.cos(x[:, pa] @ omega(P, j, pa) + P['b'][j])
            f = np.sqrt(2.0) * P['c'][j] * (phi @ P['w'][j]) / np.sqrt(N_RFF)
        x[:, j] = s * f + P['bias'][j] + z
    return x


def padding2(ci, seed, cond):
    """z-scored float32 padding block for a padded condition, with recorded graph statistics."""
    mech = CELLS[ci][2]
    e, s = cond_es(cond)
    P = pad_params(seed, mech)
    g = pad_graph(P, e)
    x64 = pad_data(P, g, mech, s)
    deg = g.sum(0) + g.sum(1)
    return dict(P=zscore(x64), g=g, e=e, s=s, n_edges=int(g.sum()), n_isolated=int((deg == 0).sum()), x64=x64)


def assemble2(sysid, ci, seed, cond):
    """Input table for (system, condition). k0 is the target block alone (identical to P-N1's k = 0 input)."""
    t = target(sysid, ci, seed)
    if 'x0' not in t:
        t['x0'] = zscore(t['x'])
    if cond == 'k0':
        return t['x0'], t, None
    pad = padding2(ci, seed, cond)
    x = zscore(np.concatenate([t['x'], pad['P']], 1))
    dT = t['x'].shape[1]
    assert np.ascontiguousarray(x[:, :dT]).tobytes() == t['x0'].tobytes(), 'target block not bitwise identical (G1)'
    return x, t, pad


def key2(sysid, cond, variant):
    return f'{sysid}__{cond}__{variant}'
