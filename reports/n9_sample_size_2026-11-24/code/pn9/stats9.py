"""P-N9 / Study 8 statistics (rules PN9 v1 §4). Pure functions.

- strat: the stratified t of Study 2 (8 cells, equal weights, SE^2 = sum w^2 s_c^2 / n_c, Welch-Satterthwaite df), imported
  unchanged from the frozen P-N8 stats8.strat8 (SE = 0 -> DEGENERATE). holm and size_label: frozen P-N7, via stats8.
- p-values for the null hypotheses of §4.2, all from the same (theta, se, df) of strat:
    p_greater(r, c): H0 theta <= c (one-sided, upper)       p_less(r, c): H0 theta >= c (one-sided, lower)
    p_two_sided(r): H0 theta = 0                             p_tost(r, m): H0 |theta| >= m (larger of two one-sided p)
    p_iut(rs, m): H0 'some |theta_l| >= m' (largest TOST p over the levels; intersection-union)
  A degenerate result (SE = 0) gives p = 1 for every null (rules §4.2).
"""
import sys
from pathlib import Path
import numpy as np
from scipy import stats

_ART = Path(__file__).resolve().parents[2]
if str(_ART / 'n8_runs' / 'pn8') not in sys.path:
    sys.path.insert(1, str(_ART / 'n8_runs' / 'pn8'))
import stats8 as S8                                   # frozen P-N8 (and frozen P-N7 stats7 through it)

strat = S8.strat8
holm = S8.holm
size_label = S8.size_label


def _ok(r):
    return not r.get('degenerate') and r.get('se', 0) > 0 and r.get('df') is not None


def p_greater(r, c=0.0):
    return float(stats.t.sf((r['theta'] - c) / r['se'], r['df'])) if _ok(r) else 1.0


def p_less(r, c=0.0):
    return float(stats.t.cdf((r['theta'] - c) / r['se'], r['df'])) if _ok(r) else 1.0


def p_two_sided(r):
    return float(min(1.0, 2 * min(p_greater(r), p_less(r)))) if _ok(r) else 1.0


def p_tost(r, m):
    return max(p_greater(r, -m), p_less(r, m)) if _ok(r) else 1.0


def p_iut(results, m):
    return max(p_tost(r, m) for r in results) if results else 1.0


def slope_per_system(values_by_level, levels):
    """OLS slope of one system's values on log2(n) over the given levels (rules §3)."""
    x = np.log2(np.asarray(levels, float))
    y = np.asarray(values_by_level, float)
    xc = x - x.mean()
    return float((xc * (y - y.mean())).sum() / (xc ** 2).sum())


def ci95(r):
    return r['ci95']


def check_pvalues(seed=9, cases=200):
    """Internal consistency of the p-value helpers against direct formulas on random strat results (used by gates9)."""
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(cases):
        cells = np.repeat(np.arange(8), int(rng.integers(3, 16)))
        r = strat(rng.normal(rng.normal(0, 0.05), 0.08, len(cells)), cells)
        if not _ok(r):
            continue
        tt = r['theta'] / r['se']
        worst = max(worst, abs(p_greater(r) - r['p']))                       # same as strat8's one-sided p
        worst = max(worst, abs(p_two_sided(r) - 2 * stats.t.sf(abs(tt), r['df'])))
        m = 0.05
        direct = max(stats.t.sf((r['theta'] + m) / r['se'], r['df']), stats.t.cdf((r['theta'] - m) / r['se'], r['df']))
        worst = max(worst, abs(p_tost(r, m) - direct))
    return worst
