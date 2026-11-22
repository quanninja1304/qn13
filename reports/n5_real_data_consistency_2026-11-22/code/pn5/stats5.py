"""P-N5 statistics (rules PN5 v1 §5, §6). Pure functions, no data access.

paired_t: one-sided paired t over draws (df = n - 1) toward the predicted side of a bound. All values equal (SE = 0) is
          DEGENERATE: p = 1, never confirmed (rules §5, as P-N4). Also counts draws above, at and below the bound and the
          number of distinct values, to show how discrete the contrast is (rules §5, §6).
holm: Holm at familywise level 0.05, stopping at the first non-rejection (same rule as stats4.py of P-N4).
describe: summary over completed draws; None marks a timeout, is excluded and counted, never imputed (rules §3, §6).
p51_contrast: draw-wise flips_M - max(flips_PC, flips_GES) (rules §5); a draw with a missing control is None.
"""
import numpy as np
from scipy import stats

FWER = 0.05


def paired_t(values, direction=+1, bound=0.0):
    v = np.asarray(values, float)
    if v.ndim != 1 or len(v) < 2 or np.isnan(v).any():
        raise ValueError('paired_t needs at least two finite values')
    n = len(v)
    mean, sd = float(v.mean()), float(v.std(ddof=1))
    d = direction * (v - bound)
    out = dict(n=n, mean=mean, sd=sd, direction=int(direction), bound=float(bound), n_above=int((d > 0).sum()),
               n_at=int((d == 0).sum()), n_below=int((d < 0).sum()), n_distinct=int(len(np.unique(v))))
    if np.all(v == v[0]):
        out.update(se=0.0, degenerate=True, status='DEGENERATE', df=None, t=None, p_one_sided=1.0, ci95=[mean, mean])
    else:
        se = sd / np.sqrt(n)
        df = n - 1
        t = direction * (mean - bound) / se
        q = stats.t.ppf(0.975, df)
        out.update(se=float(se), degenerate=False, df=df, t=float(t), p_one_sided=float(stats.t.sf(t, df)),
                   ci95=[float(mean - q * se), float(mean + q * se)])
    out['estimate_opposite_side'] = bool(direction * (mean - bound) < 0)
    return out


def holm(pvals, fwer=FWER):
    """pvals: dict id -> p. Returns dict id -> dict(holm_rank, holm_threshold, label)."""
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


def describe(values):
    """values: list over draws, None = timeout. Statistics use completed draws only."""
    done = np.asarray([float(x) for x in values if x is not None], float)
    out = dict(n_completed=int(len(done)), n_timeout=int(sum(1 for x in values if x is None)))
    if len(done) == 0:
        return out
    out.update(mean=float(done.mean()), median=float(np.median(done)), q1=float(np.percentile(done, 25)),
               q3=float(np.percentile(done, 75)), min=float(done.min()), max=float(done.max()))
    if len(done) > 1:
        se = float(done.std(ddof=1) / np.sqrt(len(done)))
        q = stats.t.ppf(0.975, len(done) - 1)
        out['ci95_t'] = [out['mean'] - q * se, out['mean'] + q * se]
    return out


def p51_contrast(f_model, f_controls):
    """Draw-wise f_model - max over the available controls; None if any control or the model is missing (timeout)."""
    out = []
    for i, fm in enumerate(f_model):
        cs = [fc[i] for fc in f_controls]
        out.append(None if fm is None or any(c is None for c in cs) else float(fm - max(cs)))
    return out
