"""P-N6 common (rules PN6 v1, locked 678f55f): sets, systems, inputs, keys, screening decisions, job lists.

Frozen modules are imported unchanged (rules §11): P-N1 common.py; P-N2 common2.py and screen.py; P-N5 common5.py for
the real-table inputs. measures6.py adds P-N1 metrics.py and P-N4 selector4.py (with common4.py).
"""
import sys, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RUNS6 = HERE.parent                                     # artifacts/n6_runs
ART = RUNS6.parent                                      # artifacts
REPO = ART.parent                                       # safety_prior
OUT6 = RUNS6 / 'pn6_out'
REPORT = REPO / 'reports' / 'n6_fix_comparison_2026-11-22'
INPUTS5 = REPO / 'reports' / 'n5_real_data_consistency_2026-11-22' / 'checks' / 'inputs5.json'
OUT5 = ART / 'n5_runs' / 'pn5_out'
for _sub in ('n5_runs/pn5', 'n4_runs/pn4', 'n2_runs/pn2', 'n1_runs/pn1'):   # frozen modules ahead of site-packages
    if str(ART / _sub) not in sys.path:
        sys.path.insert(1, str(ART / _sub))
from common import CELLS, N, sha                         # frozen P-N1
from common2 import assemble2                            # frozen P-N2: P-N1 target, padding2, bitwise target check
import screen as SCR                                     # frozen P-N2: p_hsic, reject_bonferroni, components, screen_metrics

SETS6 = {'PN6': dict(base=480000, reps=15), 'DEV6': dict(base=490000, reps=2)}
ALPHA_L_GRID = (1e-5, 1e-4, 1e-3)
ALPHA_H_GRID = (0.001, 0.01, 0.05)
MODELS = ('avici', 'cdfm')
R_ARMS = ('RL', 'RH')
REAL_TABLES = ('sachs', 'wine')
REAL_PADDED = ('k20_e0', 'k40_e0')
REAL_DRAWS = 20
BUDGET_S = 3 * 3600
P_TOL = 1e-12
MARGIN_F1, MARGIN_EDGES, MARGIN_PAIRS = 0.03, 1.5, 1.5


def systems6(set_name):
    s = SETS6[set_name]
    return [(f'{set_name}-c{ci}-r{r}', ci, s['base'] + 1000 * ci + r) for ci in range(8) for r in range(s['reps'])]


def conds6(ci):
    """P-N2 condition names of the three inputs of a system: k0, A20 (e = 0) and S20 (e = e_T)."""
    return ('k0', 'e0', f'e{CELLS[ci][1]}')


def label(cond):
    return {'k0': 'k0', 'e0': 'A20'}.get(cond, 'S20')


def syn_items(set_name):
    return [dict(kind='syn', set=set_name, sid=sid, ci=ci, seed=seed, cond=c)
            for sid, ci, seed in systems6(set_name) for c in conds6(ci)]


def real_items():
    out = []
    for t in REAL_TABLES:
        out.append(dict(kind='real', set='PN6', table=t, cond='k0', r=None))
        out += [dict(kind='real', set='PN6', table=t, cond=c, r=r) for c in REAL_PADDED for r in range(REAL_DRAWS)]
    return out


def items6(set_name):
    """Inputs of a set (rules §2): synthetic systems x three inputs; PN6 also has the real-table inputs."""
    return syn_items(set_name) + (real_items() if set_name == 'PN6' else [])


def base_key(it):
    if it['kind'] == 'syn':
        return f"{it['sid']}__{it['cond']}"
    return f"{it['table']}__{it['cond']}" + ('' if it['r'] is None else f"__r{it['r']:02d}")


def key6(it, arm):
    return f'{base_key(it)}__{arm}'


def k0_of(it):
    return dict(it, cond='k0', r=None) if it['kind'] == 'real' else dict(it, cond='k0')


def assemble6(it):
    """(X, d_T, info). Synthetic: frozen assemble2, which asserts the bitwise target block. Real: frozen assemble5 with
    the P-N5 draws, which asserts the bitwise real block; info holds the target graph only for synthetic inputs."""
    if it['kind'] == 'syn':
        X, t, pad = assemble2(it['sid'], it['ci'], it['seed'], it['cond'])
        return np.ascontiguousarray(X), int(t['x'].shape[1]), dict(g=t['g'], pad=pad)
    from common5 import assemble5
    X, rb, pad = assemble5('PN5', it['table'], it['cond'], it['r'])
    return np.ascontiguousarray(X), int(rb['XR'].shape[1]), dict(g=None, pad=pad)


def pval_file(it):
    return OUT6 / 'pvals' / f'{base_key(it)}.npz'


def load_pvals(it):
    z = np.load(pval_file(it), allow_pickle=False)
    return np.asarray(z['p']), json.loads(str(z['meta']))


def reject(p, arm, alpha):
    """Pairwise decisions (rules §3): R-L rejects when p < alpha_L; R-H when p < alpha_H / (D(D - 1)/2), which is the
    frozen P-N2 reject_bonferroni."""
    if arm == 'RH':
        return SCR.reject_bonferroni(p, alpha)
    R = p < alpha
    np.fill_diagonal(R, False)
    return R | R.T


def alphas():
    a = json.loads((OUT6 / 'alpha6.json').read_text())
    return dict(RL=float(a['alpha_L']), RH=float(a['alpha_H']))


def target_components(lab, dT):
    """Components with at least one target variable; columns in increasing table index (rules §3)."""
    return [np.where(lab == L)[0] for L in sorted(set(lab[:dT].tolist()))]


def screen_stats(lab, R, dT, g):
    """Screening metrics. Synthetic: frozen P-N2 screen_metrics (needs the target graph). Real: the parts without it."""
    D = len(lab)
    tl = set(lab[:dT].tolist())
    mixed = any(lab[v] in tl for v in range(dT, D))
    if g is not None:
        s = SCR.screen_metrics(lab, R, dT, g)
    else:
        s = dict(merged=int(sum(1 for v in range(dT, D) if lab[v] in tl)), split=None,
                 false_cross=int(R[:dT, dT:].sum()) if D > dT else 0, n_target_components=len(tl), n_true_edges=None, k=D - dT)
    s['mixed'] = bool(mixed)
    return s
