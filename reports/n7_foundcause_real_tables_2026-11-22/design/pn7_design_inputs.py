"""P-N7 design inputs (rules draft v0): power proxy and budget estimate. Runs no model.

Reads only frozen outputs that were already seen:
  - P-N5 reading (pn5_reading.json): the 20 per-draw P5-1 contrasts of AVICI and CDFM, used as proxies for FoundCause,
    whose effect on the real tables is unknown;
  - P-N1 FoundCause logs (log_HELD.jsonl, log_E2.jsonl): wall time per call by table width D (4 threads, same machine).

Power: for R draws, resample R per-draw contrasts with replacement (B = 4000), apply the one-sided paired t-test of
P-N5 (p = P(T_{R-1} >= t); SE = 0 -> p = 1), and count rejections at 0.025 (the first Holm threshold for two
hypotheses) and at 0.05. Scenarios: observed contrasts; contrasts shifted so their mean is halved.

Budget: each table adds 5 FoundCause calls at k0 for the schedule-noise reference (P-N1 adapter at base 42 as a check,
then bases 1042, 2042, 3042, 4042), as in P-N1's tau_sched.

usage: python -I pn7_design_inputs.py <artifacts dir> <output json>
"""
import json, sys
import statistics as st
from pathlib import Path
import numpy as np
from scipy import stats

ART = Path(sys.argv[1]).resolve()
r5 = json.loads((ART / 'n5_runs' / 'pn5_out' / 'pn5_reading.json').read_text())['hypotheses']
PROXIES = {k: np.asarray(r5[k]['values'], float) for k in ('P5-1S-A', 'P5-1S-C', 'P5-1W-A', 'P5-1W-C')}
R_GRID = (10, 12, 16, 20)
B = 4000
rng = np.random.default_rng(20261122)


def p_one_sided(x):
    se = x.std(ddof=1) / np.sqrt(len(x))
    if se == 0:
        return 1.0                                   # rules: SE = 0 -> DEGENERATE, p = 1
    return float(stats.t.sf(x.mean() / se, len(x) - 1))


power = {}
for name, v in PROXIES.items():
    for scen, vals in (('observed', v), ('half_mean', v - v.mean() / 2)):
        for R in R_GRID:
            ps = np.array([p_one_sided(rng.choice(vals, size=R, replace=True)) for _ in range(B)])
            power[f'{name}|{scen}|R{R}'] = dict(mean=float(vals.mean()), sd=float(vals.std(ddof=1)),
                                                 power_0025=float((ps < 0.025).mean()),
                                                 power_005=float((ps < 0.05).mean()))

# budget from P-N1 FoundCause logs (median wall time per call by D)
times = {}
for f in ('log_HELD.jsonl', 'log_E2.jsonl'):
    for line in (ART / 'n1_runs' / 'pn1_out' / 'foundcause' / f).read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get('status', 'ok') == 'ok' and r.get('runtime_s') is not None:
                times.setdefault(int(r['d']), []).append(float(r['runtime_s']))
med = {d: st.median(v) for d, v in sorted(times.items())}
ds = np.array(sorted(med)); ms = np.array([med[d] for d in ds])
slope, intercept = np.polyfit(ds, ms, 1)          # linear fit of the medians, used only to read off D = 11 and 31
t11, t31 = float(intercept + slope * 11), float(intercept + slope * 31)


N_SCHED = 5   # per table at k0: the P-N1 adapter at base 42 (check against the API) and bases 1042, 2042, 3042, 4042


def est(calls_k0, calls_k20, reruns, sched):
    raw = calls_k0 * t11 + calls_k20 * t31 + reruns * t11 + sched * t11
    return dict(raw_s=round(raw), estimate_s=round(raw * 1.10 + 300), estimate_h=round((raw * 1.10 + 300) / 3600, 2))


budget = {f'one_run_both_tables_R{R}': est(2, 2 * R, 2, 2 * N_SCHED) for R in R_GRID}
budget['two_runs_one_table_each_R20 (per run)'] = est(1, 20, 1, N_SCHED)
budget['one_table_R20'] = est(1, 20, 1, N_SCHED)
out = dict(note='design inputs only; no model run; proxies are AVICI and CDFM contrasts from P-N5, not FoundCause',
           power=power, foundcause_median_s_by_D={str(d): round(v, 1) for d, v in med.items()},
           n_calls_by_D={str(d): len(v) for d, v in sorted(times.items())},
           linear_fit=dict(slope_s_per_column=round(float(slope), 2), intercept_s=round(float(intercept), 1),
                           t_D11_s=round(t11, 1), t_D31_s=round(t31, 1)),
           budget=budget, estimator='(sum of per-call times) * 1.10 + 300 s, as G9 of P-N6')
Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
for k, v in power.items():
    print(k, v)
print(json.dumps({k: out[k] for k in ('foundcause_median_s_by_D', 'n_calls_by_D', 'linear_fit', 'budget')}, indent=1))
