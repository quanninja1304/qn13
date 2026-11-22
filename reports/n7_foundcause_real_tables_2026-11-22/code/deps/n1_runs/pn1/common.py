"""P-N1 (rules v2 + v2.1, locked 2026-11-14): shared data generation, job keys, hashing.

Everything here is deterministic given the seeds below. No metric is computed here.
"""
import hashlib, os
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]            # .../artifacts
ENV = ROOT / 'n1_models_cpu'
RUNS = ROOT / 'n1_runs'
CFG = RUNS / 'config'
OUT = RUNS / 'pn1_out'
N = 500

# 8 cells: (d_T, edges_per_var, mechanism)
CELLS = [(dT, e, m) for dT in (10, 20) for e in (1, 2) for m in ('lin', 'rff')]
SETS = {'DEV': (100000, 2), 'EXP': (200000, 10), 'HELD': (300000, 3), 'ORACLE': (150000, 3)}
TYPES = ['A', 'B', 'C', 'D']
KS = [0, 5, 10, 20, 30]


def cfg_path(e, m):
    return CFG / f'er{e}-{m}-gauss.yaml'


def systems(set_name):
    """List of (system_id, cell_index, base_seed). ORACLE uses 20 systems (cells cycled)."""
    base, reps = SETS[set_name]
    out = []
    if set_name == 'ORACLE':
        for r in range(20):
            ci = r % 8
            out.append((f'ORACLE-c{ci}-r{r}', ci, base + ci * 1000 + r))
        return out
    for ci in range(8):
        for r in range(reps):
            out.append((f'{set_name}-c{ci}-r{r}', ci, base + ci * 1000 + r))
    return out


def zscore(x):
    """Column-wise z-score in float64, returned as float32. Column-wise => target block is unaffected by padding."""
    x = np.asarray(x, dtype=np.float64)
    return ((x - x.mean(0)) / x.std(0)).astype(np.float32)


_target_cache = {}


def target(sysid, ci, seed):
    """Target system. Registered rejection rule: a target with 0 edges is replaced by the next seed (logged)."""
    if sysid in _target_cache:
        return _target_cache[sysid]
    from avici import simulate_data
    dT, e, m = CELLS[ci]
    s, rejected = seed, []
    while True:
        g, x, _ = simulate_data(d=dT, n=N, seed=s, path=str(cfg_path(e, m)))
        if g.sum() > 0:
            break
        rejected.append(s); s += 500
    res = dict(g=g.astype(np.int8), x=zscore(x), seed_used=s, rejected=rejected, cell=CELLS[ci])
    _target_cache[sysid] = res
    return res


def pad_seed(seed, typ, k):
    ss = np.random.SeedSequence([seed, TYPES.index(typ), k, 20261114])
    return int(ss.generate_state(1)[0])


def padding(sysid, ci, seed, typ, k):
    """Returns (P [n,k] float32 z-scored, G_P [k,k] or None, note). Independent of X_T except type C (row-permuted copies)."""
    if k == 0:
        return np.zeros((N, 0), np.float32), np.zeros((0, 0), np.int8), ''
    ps = pad_seed(seed, typ, k)
    rng = np.random.default_rng(ps)
    dT, e, m = CELLS[ci]
    gp, note = np.zeros((k, k), np.int8), ''
    if typ == 'A':
        p = rng.standard_normal((N, k))
    elif typ == 'B':
        from avici import simulate_data
        g, p, _ = simulate_data(d=k, n=N, seed=ps, path=str(cfg_path(e, m)))
        gp = g.astype(np.int8)
        if min(2 * e / (k - 1), 0.99) == 0.99:
            note = 'B_CLIPPED'
    elif typ == 'C':
        xt = target(sysid, ci, seed)['x']
        p = np.stack([xt[rng.permutation(N), j % dT] for j in range(k)], 1)
    elif typ == 'D':
        p = rng.standard_t(3, size=(N, k))
    else:
        raise ValueError(typ)
    return zscore(p), gp, note


def assemble(sysid, ci, seed, typ, k, perm=None):
    """X_k = zscore([X_T | P_k]); padding appended AFTER the target block. Optional column permutation (equivariance check)."""
    t = target(sysid, ci, seed)
    p, gp, note = padding(sysid, ci, seed, typ, k)
    x = zscore(np.concatenate([t['x'], p], 1))
    dT = t['x'].shape[1]
    if 'x0' not in t:
        t['x0'] = zscore(t['x'])          # the k = 0 input block
    assert np.ascontiguousarray(x[:, :dT]).tobytes() == t['x0'].tobytes(), 'target block not bitwise identical (RN0.4)'
    if perm is not None:
        x = np.ascontiguousarray(x[:, perm])
    return x, t, gp, note


def sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def job_key(sysid, typ, k, variant='main'):
    typ = '-' if k == 0 else typ
    return f'{sysid}__{typ}__k{k}__{variant}'


def perm_for(sysid, d):
    rng = np.random.default_rng(np.random.SeedSequence([int(hashlib.md5(sysid.encode()).hexdigest()[:8], 16), d, 7]))
    return rng.permutation(d)
