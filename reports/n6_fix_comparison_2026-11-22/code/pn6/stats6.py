"""P-N6 statistics (rules PN6 v1 §5-§6): stratified one-sided t, non-inferiority composite, Holm, size labels,
Clopper-Pearson intervals, descriptive summaries."""
import numpy as np
from scipy import stats


def strat_t(cells, bound=0.0):
    """One-sided stratified t for mean > bound. cells: list of per-cell arrays; w_c = 1/len(cells);
    SE^2 = sum w^2 s_c^2 / n_c; Welch-Satterthwaite df; p = t.sf. SE = 0 -> DEGENERATE with p = 1 (rules §5)."""
    cells = [np.asarray(c, float) for c in cells]
    w = 1.0 / len(cells)
    est = float(sum(w * c.mean() for c in cells))
    a = [w * w * c.var(ddof=1) / len(c) for c in cells]
    se = float(np.sqrt(sum(a)))
    out = dict(estimate=est, se=se, n_cells=[len(c) for c in cells], bound=bound)
    if se == 0.0:
        out.update(degenerate=True, df=None, t=None, p=1.0, ci95=[est, est])
        return out
    df = float(sum(a) ** 2 / sum(x * x / (len(c) - 1) for x, c in zip(a, cells)))
    t = (est - bound) / se
    q = float(stats.t.ppf(0.975, df))
    out.update(degenerate=False, df=df, t=float(t), p=float(stats.t.sf(t, df)), ci95=[est - q * se, est + q * se])
    return out


def ni_composite(cells_q0, cells_qa, margin):
    """P6-1: both E[Q0] > -margin and E[Q(A20)] > -margin; p = larger one-sided p (intersection-union)."""
    a, b = strat_t(cells_q0, -margin), strat_t(cells_qa, -margin)
    return dict(Q0=a, QA20=b, p=max(a['p'], b['p']), degenerate=bool(a['degenerate'] or b['degenerate']))


def holm(pvals, alpha=0.05):
    """pvals: {id: p}. Holm step-down; stops at the first non-rejection. Returns {id: (rank, threshold, rejected)}."""
    order = sorted(pvals, key=lambda h: (pvals[h], h))
    m, out, alive = len(order), {}, True
    for i, h in enumerate(order):
        thr = alpha / (m - i)
        rej = alive and pvals[h] <= thr
        alive = rej
        out[h] = (i + 1, thr, bool(rej))
    return out


def size_label(ci, margin):
    lo, hi = ci
    sign = 'POS' if lo > 0 else ('NEG' if hi < 0 else 'NONE')
    size = 'SMALL' if (lo >= -margin and hi <= margin) else ('LARGE' if (lo > margin or hi < -margin) else 'UNCLEAR')
    return sign, size


def clopper_pearson(k, n, conf=0.95):
    if n == 0:
        return [None, None]
    lo = 0.0 if k == 0 else float(stats.beta.ppf((1 - conf) / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - (1 - conf) / 2, k + 1, n - k))
    return [lo, hi]


def describe(values):
    v = np.asarray([x for x in values if x is not None], float)
    out = dict(n=int(len(v)))
    if len(v) == 0:
        return out
    out.update(mean=float(v.mean()), median=float(np.median(v)), q1=float(np.percentile(v, 25)),
               q3=float(np.percentile(v, 75)), min=float(v.min()), max=float(v.max()))
    if len(v) > 1:
        se = float(v.std(ddof=1) / np.sqrt(len(v)))
        q = float(stats.t.ppf(0.975, len(v) - 1))
        out['ci95_t'] = [out['mean'] - q * se, out['mean'] + q * se]
    return out
