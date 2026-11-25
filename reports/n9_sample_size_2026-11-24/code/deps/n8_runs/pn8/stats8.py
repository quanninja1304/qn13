"""P-N8 / Study 7 statistics (rules PN8 v1 §4). Pure functions.

- t_one_sided, holm, size_label: imported unchanged from the frozen P-N7 stats7.py (paired one-sided t over draws with
  SE = 0 -> DEGENERATE, p = 1; Holm; size labels SMALL inside (-M, M), LARGE entirely outside one side, else UNCLEAR).
- strat8: the stratified one-sided t of Study 2 (cell-balanced mean, SE^2 = sum w^2 s_c^2 / n_c, Welch-Satterthwaite df),
  copied from the frozen P-N2 analyze_held2.strat without the bootstrap, with this study's zero-SE rule
  (SE = 0 -> DEGENERATE, p = 1). gates8.py checks it against the frozen function on test data.
"""
import ast, sys
from pathlib import Path
import numpy as np
from scipy import stats

_ART = Path(__file__).resolve().parents[2]
if str(_ART / 'n7_runs' / 'pn7') not in sys.path:
    sys.path.insert(1, str(_ART / 'n7_runs' / 'pn7'))
import stats7 as S7                                   # frozen P-N7

t_one_sided, holm, size_label = S7.t_one_sided, S7.holm, S7.size_label
HELD2_FILE = _ART / 'n2_runs' / 'pn2' / 'analyze_held2.py'


def strat8(values, cells):
    """H1: cell-balanced mean > 0. Returns theta, se, df, t, one-sided p, 95% CI, degenerate flag."""
    by = {}
    for x, c in zip(values, cells):
        if not np.isnan(x):
            by.setdefault(c, []).append(float(x))
    keys = sorted(by)
    w = 1.0 / len(keys)
    means, ac, nc = [], [], []
    for c in keys:
        v = np.asarray(by[c]); n = len(v)
        means.append(float(v.mean())); nc.append(n)
        ac.append(w ** 2 * (v.var(ddof=1) if n > 1 else 0.0) / n)
    theta = w * sum(means); se2 = sum(ac); se = float(np.sqrt(se2))
    out = dict(theta=float(theta), se=se, n_by_cell=nc, cell_means=means, degenerate=False)
    if se2 > 0:
        den = sum(x ** 2 / (n - 1) for x, n in zip(ac, nc) if n > 1)
        df = float(se2 ** 2 / den) if den > 0 else float('inf')
        tstat = theta / se
        q = stats.t.ppf(0.975, df)
        out.update(df=df, t=float(tstat), p=float(stats.t.sf(tstat, df)), ci95=[float(theta - q * se), float(theta + q * se)])
    else:
        out.update(df=None, t=None, p=1.0, ci95=[float(theta), float(theta)], degenerate=True)
    return out


def frozen_strat():
    """The frozen P-N2 strat() extracted from its source (no module-level code of analyze_held2 is run)."""
    tree = ast.parse(HELD2_FILE.read_text(encoding='utf-8'))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'strat')
    ns = dict(np=np, stats=stats, BSEED=20261121, BOOT=50)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(HELD2_FILE), 'exec'), ns)
    return ns['strat']


def check_against_frozen(n_cases=200, seed=8):
    """Max |difference| of theta, se, df, t, p, CI between strat8 and the frozen strat (sigma = +1) on random data."""
    fs = frozen_strat()
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(n_cases):
        C = int(rng.choice([4, 8])); N = int(rng.integers(3, 16))
        cells = np.repeat(np.arange(C), N)
        vals = rng.normal(rng.normal(0, 1), rng.uniform(0.1, 3), C * N)
        if rng.random() < 0.3:
            vals = np.round(vals)                      # discrete counts, as flips
        a, b = strat8(vals, cells), fs(vals, cells, 1)
        diffs = [a['theta'] - b['theta'], a['se'] - b['se'], a['df'] - b['df'], a['t'] - b['t'], a['p'] - b['p_one_sided'],
                 a['ci95'][0] - b['ci95'][0], a['ci95'][1] - b['ci95'][1]]
        worst = max(worst, max(abs(x) for x in diffs))
    return worst
