"""P-N4 power (rules PN4 §6): noncentral-t approximation from HELD2 cell means and SDs.

Method, per component of a hypothesis:
- SE = sqrt(sum_c w^2 (f_sd * s_c)^2 / n_c), w = 1/4, s_c = HELD2 SD in cell c, f_sd = SD inflation of the scenario;
- df = Welch-Satterthwaite with the same a_c;
- delta = direction * (f_eff * theta_HELD2 - bound) / SE, f_eff = effect shrinkage of the scenario;
- power = P(T'(df, delta) > t_{1 - alpha}(df)), alpha = 0.05 / 8 (the strictest Holm level).
Composite hypotheses: lower bound 1 - sum_i (1 - power_i) over components.
This is an approximation from HELD2 means and variances under the stated shrinkage and inflation assumptions,
not power computed from the full empirical distribution, and not a guarantee of power at k = 40.
usage: <venv python> -I pn4_power.py  ->  pn4_power.json next to this file
"""
import json
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / 'pn4_design_inputs.json').read_text())['HELD2']['contrasts']
ALPHA = 0.05 / 8
COMP = {'D1': (-1, 0.0), 'D2': (+1, 0.0), 'D3a': (+1, 0.0), 'D3b': (-1, 0.0), 'T': (-1, -1.5), 'TpS': (-1, 0.0), 'TmS': (-1, 0.0)}
HYP = {'N4-a': ['D1'], 'N4-b': ['D2'], 'N4-x': ['D3a', 'D3b'], 'N4-c': ['T', 'TpS', 'TmS']}
SCEN = [('as HELD2', 1.0, 1.0), ('effects x0.5, SD x1', 0.5, 1.0), ('effects x0.5, SD x1.5', 0.5, 1.5)]


def se_df(sds, nc):
    a = [(0.25 ** 2) * s * s / nc for s in sds]
    return float(np.sqrt(sum(a))), float(sum(a) ** 2 / sum(x * x / (nc - 1) for x in a))


res = dict(method=__doc__.split('\n\n')[0], alpha_one_sided=ALPHA, scenarios={})
for nc in (15, 20):
    for name, f_eff, f_sd in SCEN:
        comp = {}
        for q, (direction, bound) in COMP.items():
            se, df = se_df([f_sd * s for s in D[q]['cell_sd'].values()], nc)
            delta = direction * (f_eff * D[q]['theta'] - bound) / se
            pw = float(stats.nct.sf(stats.t.ppf(1 - ALPHA, df), df, delta)) if delta > 0 else 0.0
            mde = float((stats.t.ppf(1 - ALPHA, df) + stats.t.ppf(0.8, df)) * se)
            comp[q] = dict(theta_used=f_eff * D[q]['theta'], bound=bound, se=se, df=df, power=pw, mde_beyond_bound_at_power_0_8=mde)
        hyp = {h: max(0.0, 1 - sum(1 - comp[q]['power'] for q in qs)) for h, qs in HYP.items()}
        res['scenarios'][f'n_c={nc} | {name}'] = dict(components=comp, hypothesis_power_lower_bound=hyp)
(HERE / 'pn4_power.json').write_text(json.dumps(res, indent=1))
for k, v in res['scenarios'].items():
    print(k, {q: round(c['power'], 3) for q, c in v['components'].items()}, {h: round(p, 3) for h, p in v['hypothesis_power_lower_bound'].items()})
