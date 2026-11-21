"""P-N4 statistics (rules PN4 v1 §4). Pure functions, no data access.

strat4: cell-balanced mean, cell-stratified SE, Welch-Satterthwaite df, one-sided p toward the predicted side of a bound.
        SE = 0 is DEGENERATE: p = 1 and never confirmed (rules PN4 v1 §4; old phases keep their own rule).
composite: p of an intersection-union hypothesis = max of the component p-values.
holm: Holm at familywise level 0.05 over the given p-values, stopping at the first non-rejection.
"""
import numpy as np
from scipy import stats

FWER = 0.05
BOOT, BOOT_SEED = 2000, 20261122


def strat4(values, cells, direction=1, bound=0.0, boot=False):
    """direction +1: predicted mu > bound; -1: predicted mu < bound. Returns estimate, SE, df, t, p, 95% CI."""
    vals = np.asarray(values, float)
    if np.isnan(vals).any():
        raise ValueError('NaN in per-system contrast')
    by = {}
    for x, c in zip(vals, cells):
        by.setdefault(c, []).append(float(x))
    keys = sorted(by); w = 1.0 / len(keys)
    means, ac, nc = [], [], []
    for c in keys:
        v = np.asarray(by[c]); n = len(v)
        means.append(float(v.mean())); nc.append(n)
        ac.append(w ** 2 * (v.var(ddof=1) if n > 1 else 0.0) / n)
    theta = w * sum(means); se2 = sum(ac); se = float(np.sqrt(se2))
    out = dict(theta=float(theta), se=se, n_by_cell=nc, cells=[int(c) for c in keys], cell_means=means,
               direction=int(direction), bound=float(bound))
    if se2 > 0:
        den = sum(x ** 2 / (n - 1) for x, n in zip(ac, nc) if n > 1)
        df = float(se2 ** 2 / den) if den > 0 else float('inf')
        t = direction * (theta - bound) / se
        q = stats.t.ppf(0.975, df)
        out.update(degenerate=False, df=df, t=float(t), p_one_sided=float(stats.t.sf(t, df)),
                   ci95=[float(theta - q * se), float(theta + q * se)])
    else:
        out.update(degenerate=True, status='DEGENERATE', df=None, t=None, p_one_sided=1.0, ci95=[float(theta), float(theta)])
    out['estimate_opposite_side'] = bool(direction * (theta - bound) < 0)
    if boot:
        rng = np.random.default_rng(BOOT_SEED)
        arrs = [np.asarray(by[c]) for c in keys]
        bs = np.array([w * sum(x[rng.integers(0, len(x), len(x))].mean() for x in arrs) for _ in range(BOOT)])
        out['boot_ci95_stratified'] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    return out


def composite(components):
    """components: list of strat4 outputs. Intersection-union p = max of component p (a DEGENERATE component gives 1)."""
    return float(max(c['p_one_sided'] for c in components))


def holm(pvals, fwer=FWER):
    """pvals: dict id -> p. Returns dict id -> (rank, threshold, label)."""
    order = sorted(pvals, key=lambda h: pvals[h])
    out, going, m = {}, True, len(order)
    for j, h in enumerate(order):
        thr_ = fwer / (m - j)
        if going and pvals[h] <= thr_:
            lab = 'CONFIRMED'
        else:
            going = False
            lab = 'NOT_CONFIRMED'
        out[h] = dict(holm_rank=j + 1, holm_threshold=thr_, label=lab)
    return out


def size_label(ci, margin):
    lo, hi = ci
    sign = 'POS' if lo > 0 else ('NEG' if hi < 0 else 'NONE')
    size = 'SMALL' if (lo >= -margin and hi <= margin) else ('LARGE' if (lo > margin or hi < -margin) else 'UNCLEAR')
    return sign, size
