"""RN0 on DEV (rules v2 §6 RN0 + v2.1 A5, A10). Writes pn1_out/rn0_<model>.json.

Operational reading fixed before any DEV model output is inspected (logged in v2.1 §4):
- tau_rep, tau_sched, tau_flips = 95th percentile over the 16 DEV systems of the per-system statistic.
- Equivariance (AVICI, CDFM): max over 10 systems of max|diff| <= 1e-4.
  FoundCause: 95th percentile over the 10 systems of Delta-p(perm vs main) <= tau_sched (same statistic, same quantile).
- Adapter parity: max|diff| <= 1e-6 on probabilities and agreement, identical native adjacency, on every DEV system.
- Competence (A10): mean F1 (FIXED, k = 0) over the 8 linear DEV systems > mean F1 of the full graph.
"""
import sys, json
import numpy as np
from common import systems, target, CELLS, OUT
from metrics import *

model = sys.argv[1]
S = systems('DEV')
rep_var = 'sched42' if model == 'foundcause' else 'rep'
res = dict(model=model, per_system=[])
dps_rep, fl_rep_f, fl_rep_n, dps_sched, fl_sched_f, fl_sched_n, eq = [], [], [], [], [], [], []
parity_ok, det_max = True, 0.0
f1m, f1full, f1pc, f1ges = [], [], [], []
for s, ci, seed in S:
    t = target(s, ci, seed); g = t['g']; dT = g.shape[0]
    m0, mr = load(model, s, '-', 0), load(model, s, '-', 0, rep_var)
    row = dict(sys=s, cell=CELLS[ci])
    d_rep, mx = dp(mr['probs'], m0['probs'], dT)
    det_max = max(det_max, float(np.abs(mr['probs'] - m0['probs']).max()))
    dps_rep.append(d_rep)
    fl_rep_f.append(flips(skel_fixed(mr['probs'], dT), skel_fixed(m0['probs'], dT)))
    fl_rep_n.append(flips(skel_native(model, mr, dT), skel_native(model, m0, dT)))
    if model == 'foundcause':
        ok = (np.abs(mr['probs'] - m0['probs']).max() <= 1e-6 and np.abs(mr['agreement'] - m0['agreement']).max() <= 1e-6
              and (mr['adj_native'] == m0['adj_native']).all())
        parity_ok &= bool(ok); row['parity'] = bool(ok)
        ms = load(model, s, '-', 0, 'sched1042')
        dps_sched.append(dp(ms['probs'], m0['probs'], dT)[0])
        fl_sched_f.append(flips(skel_fixed(ms['probs'], dT), skel_fixed(m0['probs'], dT)))
        fl_sched_n.append(flips(skel_native(model, ms, dT), skel_native(model, m0, dT)))
    mp = load(model, s, '-', 0, 'perm')
    if mp is not None:
        eq.append(dict(sys=s, maxdiff=float(np.abs(mp['probs'] - m0['probs']).max()), dp=dp(mp['probs'], m0['probs'], dT)[0],
                       flips_fixed=flips(skel_fixed(mp['probs'], dT), skel_fixed(m0['probs'], dT))))
    row['f1_fixed'] = f1(skel_fixed(m0['probs'], dT), g); row['f1_native'] = f1(skel_native(model, m0, dT), g)
    row['f1_full'] = f1_full_graph(g); row['edges_true'] = int(((g + g.T) > 0).sum() // 2)
    row['edges_pred_fixed'] = int(skel_fixed(m0['probs'], dT).sum() // 2)
    for alg, lst in (('pc', f1pc), ('ges', f1ges)):
        z = load(alg, s, '-', 0)
        row[f'f1_{alg}'] = f1(z['skel'][:dT, :dT], g)
    if CELLS[ci][2] == 'lin':
        f1m.append(row['f1_fixed']); f1full.append(row['f1_full']); f1pc.append(row['f1_pc']); f1ges.append(row['f1_ges'])
    res['per_system'].append(row)

p95 = lambda v: float(np.percentile(v, 95))
res['RN0.3_determinism'] = dict(max_abs_diff_repeat=det_max, PASS=det_max <= 1e-6, tau_rep=p95(dps_rep),
                                tau_flips_fixed_rep=p95(fl_rep_f), tau_flips_native_rep=p95(fl_rep_n))
if model == 'foundcause':
    res['A5_adapter_parity'] = dict(PASS=parity_ok)
    res['A5_tau_sched'] = dict(tau_sched=p95(dps_sched), tau_flips_fixed_sched=p95(fl_sched_f),
                               tau_flips_native_sched=p95(fl_sched_n), per_system_dp=dps_sched)
    tau_eq = res['A5_tau_sched']['tau_sched'] if parity_ok else None
    stat = p95([e['dp'] for e in eq])
    res['RN0.1_equivariance'] = dict(stat_p95_dp=stat, bound=tau_eq, PASS=(tau_eq is not None and stat <= tau_eq), systems=eq)
else:
    stat = max(e['maxdiff'] for e in eq)
    res['RN0.1_equivariance'] = dict(max_abs_diff=stat, bound=1e-4, PASS=stat <= 1e-4, systems=eq)
res['A10_competence'] = dict(mean_f1_fixed_linear=float(np.mean(f1m)), mean_f1_full_graph=float(np.mean(f1full)),
                            PASS=float(np.mean(f1m)) > float(np.mean(f1full)),
                            context_mean_f1_pc=float(np.mean(f1pc)), context_mean_f1_ges=float(np.mean(f1ges)))
(OUT / f'rn0_{model}.json').write_text(json.dumps(res, indent=1, default=str))
print(json.dumps({k: v for k, v in res.items() if k != 'per_system'}, indent=1, default=str))
