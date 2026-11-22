"""P-N7 statistics (rules PN7 v1 §4): one-sided paired t over draws, DEGENERATE, Holm, size labels. Pure functions."""
import numpy as np
from scipy import stats


def t_one_sided(values, bound=0.0):
    """H1: E[D] > bound. SE = 0 -> DEGENERATE with p = 1 (never confirmed)."""
    x = np.asarray(values, float)
    n = len(x)
    mean, sd = float(x.mean()), float(x.std(ddof=1))
    se = sd / np.sqrt(n)
    if se == 0:
        return dict(n=n, mean=mean, sd=sd, se=0.0, df=n - 1, t=None, p=1.0, ci95=[mean, mean], degenerate=True)
    t = (mean - bound) / se
    q = stats.t.ppf(0.975, n - 1)
    return dict(n=n, mean=mean, sd=sd, se=float(se), df=n - 1, t=float(t), p=float(stats.t.sf(t, n - 1)),
                ci95=[mean - q * se, mean + q * se], degenerate=False)


def holm(pvals, level=0.05):
    """{name: (rank, threshold, rejected)} for a dict of p-values; stops at the first non-rejection."""
    order = sorted(pvals, key=lambda k: pvals[k])
    out, stop = {}, False
    for i, k in enumerate(order):
        thr = level / (len(order) - i)
        rej = (not stop) and pvals[k] <= thr
        stop = stop or not rej
        out[k] = (i + 1, thr, rej)
    return out


def size_label(ci, margin):
    lo, hi = ci
    sign = 'POS' if lo > 0 else ('NEG' if hi < 0 else 'NONE')
    size = 'SMALL' if (lo > -margin and hi < margin) else ('LARGE' if (lo > margin or hi < -margin) else 'UNCLEAR')
    return sign, size


def describe(values):
    x = np.asarray(values, float)
    return dict(n=int(len(x)), mean=float(x.mean()), median=float(np.median(x)), min=float(x.min()), max=float(x.max()),
                q1=float(np.percentile(x, 25)), q3=float(np.percentile(x, 75)))
