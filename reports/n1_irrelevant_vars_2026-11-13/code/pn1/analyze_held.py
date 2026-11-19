"""RN5 held-out reading (rules v2 RN5 + v2.1 A1-A3, A8, A9 + v2.2 §3). Frozen before any held-out model output exists.

usage: analyze_held.py <avici|cdfm|foundcause|decide> [--set HELD|EXP]
  HELD (default): read set = 80 systems (AVICI, CDFM) or the nested 24 (FoundCause, r in {0,1,2}); PC/GES on the same systems.
  EXP: validation mode only. Runs the same code on the 80 exploratory systems (all models) so it can be checked against E1/E2.
  decide: combines held_<model>.json into the project decision (v2.1 A9).
Bootstrap over systems, 2000 resamples, percentile 95%, seed 20261114 (unchanged from v2 §5).
"""
import sys, json, argparse
import numpy as np
from common import systems, target, CELLS, OUT
from metrics import load, dp, flips, f1, skel_fixed, skel_native, skel_frozen_cdfm, boot_ci
from jobs import held_systems, HELD_PER_CELL, HELD_CONDS

ap = argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--set', default='HELD'); a = ap.parse_args()
B, SEED = 2000, 20261114
M1_MARGIN, M2_MARGIN, HARM_MIN, BC_MIN = 0.03, 0.03, 0.05, 0.05


def decide():
    r = {m: json.loads((OUT / f'held_{m}.json').read_text())['summary'] for m in ('avici', 'cdfm', 'foundcause')}
    leads = {'avici': r['avici']['RN5_lead']['label'], 'cdfm': r['cdfm']['RN5_lead']['label']}
    go = any(v == 'REPLICATED' for v in leads.values())
    out = dict(RN5_leads=leads, foundcause=dict(no_lead='UNEXPLAINED in E2', A20=r['foundcause']['RN5_harm_bc'],
                                               B20_branch=r['foundcause']['B20_branch']['label']),
               decision='GO mechanism validation' if go else 'NO GO on held-out (see per-model labels)',
               note='Per-model labels; not a familywise-controlled claim (v2.1 A9).')
    (OUT / 'held_decision.json').write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1)); sys.exit(0)


if a.model == 'decide':
    decide()
model = a.model
if a.set == 'HELD':
    SYS = held_systems(HELD_PER_CELL[model]); CONDS = HELD_CONDS[model]
    man = json.loads((OUT / 'held_manifest.json').read_text())
else:
    SYS = systems('EXP'); man = None
    CONDS = {'avici': [('A', 20), ('B', 20)], 'foundcause': [('A', 20), ('B', 20)],
             'cdfm': [('A', 5), ('A', 10), ('A', 20), ('A', 30), ('B', 20), ('C', 20)]}[model]
rn0 = json.loads((OUT / f'rn0_{model}.json').read_text())
tau_p = rn0['RN0.3_determinism']['tau_rep']
tau_fn = rn0['RN0.3_determinism']['tau_flips_native_rep']; tau_ff = rn0['RN0.3_determinism']['tau_flips_fixed_rep']
if model == 'foundcause':
    ts = rn0['A5_tau_sched']
    tau_p = max(tau_p, ts['tau_sched']); tau_fn = max(tau_fn, ts['tau_flips_native_sched']); tau_ff = max(tau_ff, ts['tau_flips_fixed_sched'])


def need(alg, s, typ, k):
    o = load(alg, s, typ, k)
    if o is None:
        sys.exit(f'MISSING output {alg} {s} {typ} {k}: reading refused')
    if man is not None:
        key = f"{s}__{'-' if k == 0 else typ}__k{k}__main"
        if o['meta']['input_sha'] != man['jobs'][key]['input_sha']:
            sys.exit(f'INPUT SHA MISMATCH {alg} {key}: reading refused')
    return o


def counts(sk, g):
    iu = np.triu_indices(g.shape[0], 1); t = ((g + g.T) > 0)[iu]; s = sk[iu] > 0
    tp, fp, fn = int((t & s).sum()), int((~t & s).sum()), int((t & ~s).sum())
    return dict(tp=tp, fp=fp, fn=fn, precision=(tp / (tp + fp) if tp + fp else np.nan), recall=tp / (tp + fn))


rows = []
for s, ci, seed in SYS:
    t = target(s, ci, seed); g = t['g']; dT = g.shape[0]
    if man is not None and t['seed_used'] != man['systems'][s]['seed_used']:
        sys.exit(f'TARGET SEED MISMATCH {s}')
    o0 = need(model, s, '-', 0)
    sn0, sf0 = skel_native(model, o0, dT), skel_fixed(o0['probs'], dT)
    r = dict(sys=s, cell=CELLS[ci], lin=CELLS[ci][2] == 'lin', r=int(s.split('-r')[1]),
             f1_native_0=f1(sn0, g), f1_fixed_0=f1(sf0, g), cnt_0=counts(sn0, g))
    cl0 = {alg: need(alg, s, '-', 0)['skel'][:dT, :dT] for alg in ('pc', 'ges')}
    for typ, k in CONDS:
        o = need(model, s, typ, k); c = f'{typ}{k}'
        sn, sf = skel_native(model, o, dT), skel_fixed(o['probs'], dT)
        r[c] = dict(dp=dp(o['probs'], o0['probs'], dT)[0], flips_native=flips(sn, sn0), flips_fixed=flips(sf, sf0),
                    H_native=r['f1_native_0'] - f1(sn, g), H_fixed=r['f1_fixed_0'] - f1(sf, g), cnt=counts(sn, g))
        if model == 'cdfm':
            r[c]['H_frozen'] = r['f1_native_0'] - f1(skel_frozen_cdfm(o, dT, float(o0['threshold'])), g)
        for alg in ('pc', 'ges'):
            z = need(alg, s, typ, k)['skel'][:dT, :dT]
            r[c][f'H_{alg}'] = f1(cl0[alg], g) - f1(z, g); r[c][f'flips_{alg}'] = flips(z, cl0[alg])
    rows.append(r)

V = lambda c, key, sub=None: np.array([x[c][key] for x in rows if sub is None or sub(x)], float)
lin = lambda x: x['lin']
mci = lambda v: boot_ci(v, np.mean, B, SEED)


def change_label(est, lo, hi, tau, m):
    if lo > max(tau, m): return 'MEANINGFUL'
    if lo > tau: return 'DETECTABLE'
    if hi <= max(tau, m): return 'BELOW_MARGIN'
    return 'INCONCLUSIVE'


def summarize(sub=None):
    S = dict(n_systems=sum(1 for x in rows if sub is None or sub(x)))
    # A1 change labels at A20
    e, lo, hi = boot_ci(V('A20', 'dp', sub), np.median, B, SEED)
    S['SCORE_CHANGE'] = dict(median_dp=e, ci=[lo, hi], label=change_label(e, lo, hi, tau_p, 0.01))
    for nm, key, tau in (('GRAPH_CHANGE_NATIVE', 'flips_native', tau_fn), ('GRAPH_CHANGE_FIXED', 'flips_fixed', tau_ff)):
        e, lo, hi = mci(V('A20', key, sub)); S[nm] = dict(mean_flips=e, ci=[lo, hi], label=change_label(e, lo, hi, tau, 1.0))
    # A2 harm at A20
    for est in ('H_native', 'H_fixed'):
        e, lo, hi = mci(V('A20', est, sub)); S[f'HARM_{est}'] = dict(mean=e, ci=[lo, hi], HARM=bool(e >= HARM_MIN and lo > 0))
    # A3 beyond classical on linear systems; max over baselines recomputed inside each resample
    sl = (lambda x: lin(x) and (sub is None or sub(x)))
    Hpc, Hges = V('A20', 'H_pc', sl), V('A20', 'H_ges', sl)
    rng = np.random.default_rng(SEED); idx = rng.integers(0, len(Hpc), (B, len(Hpc)))
    for est in ('H_native', 'H_fixed'):
        Hm = V('A20', est, sl); e = Hm.mean() - max(Hpc.mean(), Hges.mean())
        bs = np.array([Hm[i].mean() - max(Hpc[i].mean(), Hges[i].mean()) for i in idx]); lo, hi = np.percentile(bs, [2.5, 97.5])
        lab = 'PASS' if (e >= BC_MIN and lo > 0) else ('CONTRARY' if hi < BC_MIN else 'INCONCLUSIVE')
        S[f'BEYOND_CLASSICAL_{est}'] = dict(est=float(e), ci=[float(lo), float(hi)], label=lab, n_linear=len(Hm))
    # descriptive per condition
    S['descriptive'] = {}
    for typ, k in CONDS:
        c = f'{typ}{k}'; d = dict(median_dp=boot_ci(V(c, 'dp', sub), np.median, B, SEED))
        for key in ('H_native', 'H_fixed', 'flips_native', 'flips_fixed', 'H_pc', 'H_ges', 'flips_pc', 'flips_ges') + (('H_frozen',) if model == 'cdfm' else ()):
            d[key] = mci(V(c, key, sub))
        for q in ('tp', 'fp', 'fn', 'precision', 'recall'):
            v = np.array([x[c]['cnt'][q] - x['cnt_0'][q] for x in rows if sub is None or sub(x)], float)
            d[f'delta_{q}_native'] = mci(v[~np.isnan(v)])
        S['descriptive'][c] = d
    return S


res = dict(model=model, set=a.set, rules='v2.2', tau=dict(dp=tau_p, flips_native=tau_fn, flips_fixed=tau_ff), primary=summarize())
P = res['primary']
if model == 'avici':
    # lead M1, sign -, NATIVE = FIXED (one test, not two)
    d = mci(V('A20', 'H_native') - V('B20', 'H_native'))
    lab = 'REPLICATED' if d[2] < -M1_MARGIN else ('NOT_REPLICATED' if d[1] > -M1_MARGIN else 'INCONCLUSIVE')
    res['M1'] = dict(delta_A_minus_B=d, label=lab, registered_sign='-')
    bc = P['BEYOND_CLASSICAL_H_native']['label']; mech = lab
elif model == 'cdfm':
    def m2(est):
        pairs = {p: mci(V(p[0] + '20', est) - V(p[1] + '20', est)) for p in ('AB', 'AC', 'BC')}
        inside = all(v[1] >= -M2_MARGIN and v[2] <= M2_MARGIN for v in pairs.values())
        outside = any(v[1] > M2_MARGIN or v[2] < -M2_MARGIN for v in pairs.values())
        h = 'PASS_H' if inside else ('CONTRARY_H' if outside else 'INCONCLUSIVE_H')
        med = {k: float(np.median(V(f'A{k}', 'dp'))) for k in (5, 10, 20, 30)}
        c = boot_ci(V('A30', 'dp') - V('A5', 'dp'), np.median, B, SEED)
        mono = all(med[x] <= med[y] for x, y in ((5, 10), (10, 20), (20, 30)))
        if h == 'PASS_H' and c[1] > 0 and mono: lab = 'PASS'
        elif h == 'CONTRARY_H' or c[2] < 0: lab = 'CONTRARY'
        else: lab = 'INCONCLUSIVE'
        return dict(pairs=pairs, H_part=h, dp30_minus_dp5=c, dp_contrast_lo_gt_0=bool(c[1] > 0), median_dp_by_k=med,
                    nondecreasing=bool(mono), label=lab)
    res['M2_FIXED'] = m2('H_fixed')                       # lead (v2.2 §3.2)
    res['M2_NATIVE_descriptive'] = m2('H_native')         # reported, never substitutes for the lead
    bc = P['BEYOND_CLASSICAL_H_fixed']['label']; mech = res['M2_FIXED']['label'].replace('PASS', 'REPLICATED').replace('CONTRARY', 'NOT_REPLICATED')
else:
    d = mci(V('A20', 'H_native') - V('B20', 'H_native'))
    lab = 'SIGN_CONFIRMED' if d[1] > 0 else ('CONTRARY' if d[2] < 0 else 'INCONCLUSIVE')
    res['B20_branch'] = dict(delta_A_minus_B_native=d, label=lab, lo_above_0_03=bool(d[1] > 0.03),
                             note='side branch chosen after E2; tests a hypothesis generated by E2; does not relabel E2 UNEXPLAINED')
    res['RN5_harm_bc'] = dict(HARM_native=P['HARM_H_native']['HARM'], HARM_fixed=P['HARM_H_fixed']['HARM'],
                              BC_native=P['BEYOND_CLASSICAL_H_native']['label'], BC_fixed=P['BEYOND_CLASSICAL_H_fixed']['label'])
    bc = mech = None
if model in ('avici', 'cdfm'):
    if bc == 'PASS' and mech == 'REPLICATED': rn5 = 'REPLICATED'
    elif bc == 'CONTRARY' or mech == 'NOT_REPLICATED': rn5 = 'NOT_REPLICATED'
    else: rn5 = 'INCONCLUSIVE'
    res['RN5_lead'] = dict(label=rn5, beyond_classical=bc, mechanism=mech,
                           estimand='H_native (= H_fixed)' if model == 'avici' else 'H_fixed')
    res['subset24_descriptive'] = summarize(lambda x: x['r'] < 3) if a.set == 'HELD' else None
tag = 'held' if a.set == 'HELD' else 'valexp'
(OUT / f'{tag}_{model}.json').write_text(json.dumps(dict(summary=res, rows=rows), indent=1, default=str))
print(json.dumps({k: v for k, v in res.items() if k not in ('primary', 'subset24_descriptive')}, indent=1, default=str))
print('primary:', json.dumps({k: v for k, v in P.items() if k != 'descriptive'}, default=str))
