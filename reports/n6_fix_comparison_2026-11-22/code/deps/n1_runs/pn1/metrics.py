"""P-N1 metrics on the target block (rules v2 §5 + v2.1). Pure functions over saved outputs."""
import json
import numpy as np
from common import OUT, job_key


def load(model, sysid, typ, k, variant='main'):
    f = OUT / model / f'{job_key(sysid, typ, k, variant)}.npz'
    if not f.exists():
        return None
    z = np.load(f, allow_pickle=False)
    d = {kk: z[kk] for kk in z.files}
    d['meta'] = json.loads(str(d['meta']))
    if 'perm' in d and d['perm'].size:   # undo column permutation: out_perm[i,j] refers to original (perm[i], perm[j])
        p = d['perm']
        for kk in ('probs', 'logits', 'adj_native', 'agreement', 'C', 'skel'):
            if kk in d and d[kk].ndim == 2:
                u = np.zeros_like(d[kk]); u[np.ix_(p, p)] = d[kk]; d[kk] = u
    return d


def triu(dT):
    return np.triu_indices(dT, 1)


def skel_fixed(probs, dT, thr=0.5):
    p = probs[:dT, :dT]
    return (np.maximum(p, p.T) > thr).astype(np.int8)


def skel_native(model, out, dT):
    if model == 'avici':
        return skel_fixed(out['probs'], dT)                       # package has no decoder; README: p > 0.5
    a = out['adj_native'][:dT, :dT]
    return ((a + a.T) > 0).astype(np.int8)


def skel_frozen_cdfm(out, dT, thr0):
    p = out['probs'][:dT, :dT]
    a = (p > thr0).astype(np.int8); np.fill_diagonal(a, 0)
    return ((a + a.T) > 0).astype(np.int8)


def f1(sk, g):
    dT = g.shape[0]; iu = triu(dT)
    t = ((g + g.T) > 0)[iu]; s = sk[iu] > 0
    tp = (t & s).sum(); fp = (~t & s).sum(); fn = (t & ~s).sum()
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


def f1_full_graph(g):
    dT = g.shape[0]; npairs = dT * (dT - 1) // 2; ne = ((g + g.T) > 0)[triu(dT)].sum()
    prec = ne / npairs
    return 2 * prec / (prec + 1)


def dp(p1, p0, dT):
    a, b = p1[:dT, :dT], p0[:dT, :dT]
    off = ~np.eye(dT, dtype=bool)
    return float(np.abs(a - b)[off].mean()), float(np.abs(a - b)[off].max())


def flips(s1, s0):
    dT = s0.shape[0]; iu = triu(dT)
    return int((s1[iu] != s0[iu]).sum())


def cross_edges(probs, dT, thr=0.5):
    p = probs; m = np.maximum(p, p.T) > thr
    return int(m[:dT, dT:].sum())


def boot_ci(vals, stat=np.median, B=2000, seed=20261114):
    vals = np.asarray(vals, float); rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(vals), (B, len(vals)))
    bs = np.array([stat(vals[i]) for i in idx])
    return float(stat(vals)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
