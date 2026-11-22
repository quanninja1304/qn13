"""P-N6 feasibility gates G1-G9 on DEV6 (rules PN6 v1 §8). No model is run on the real tables.

usage: gates6.py  ->  pn6_out/gates6.json (exit 0 only if every gate passes)
Needs: DEV6 p-values (run6.py pvals DEV6), alpha6.json (alpha6.py), DEV6 outputs of plain, RL, RH, fullRL, fullRH,
oracle and rep for both models.
"""
import os, sys, json, subprocess, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
from scipy import stats
from common6 import (OUT6, INPUTS5, CELLS, MODELS, R_ARMS, ALPHA_L_GRID, P_TOL, BUDGET_S, items6, syn_items, real_items,
                     base_key, key6, k0_of, assemble6, load_pvals, reject, label, sha, SCR)
from run6 import ORACLE_KEYS, REP_KEYS
import stats6 as S6
import selector4 as SEL

G = {}
dev = syn_items('DEV6')
byk = {base_key(it): it for it in dev}


def gate(name, ok, **kw):
    G[name] = dict(ok=bool(ok), **kw)
    print(name, 'PASS' if ok else 'FAIL', {k: v for k, v in kw.items() if not isinstance(v, (list, dict)) or len(str(v)) < 300}, flush=True)


# G1: inputs regenerate bitwise; target block of padded inputs equals k0; real inputs match the P-N5 hashes
bad = []
for it in dev:
    X1, dT, _ = assemble6(it)
    X2, _, _ = assemble6(it)
    if X1.tobytes() != X2.tobytes():
        bad.append(f'{base_key(it)} not reproducible')
    if it['cond'] != 'k0':
        X0 = assemble6(k0_of(it))[0]
        if np.ascontiguousarray(X1[:, :dT]).tobytes() != X0.tobytes():
            bad.append(f'{base_key(it)} target block differs from k0')
ref5 = json.loads(INPUTS5.read_text())
real_bad = [base_key(it) for it in real_items() if ref5.get(base_key(it)) != sha(assemble6(it)[0])]
gate('G1', not bad and not real_bad, n_dev_inputs=len(dev), problems=bad[:10], n_real_inputs=len(real_items()), real_mismatch=real_bad[:10])

# G2: target-pair p-values within 1e-12 of k0; R-L decisions identical at every grid level; p_hsic reproducible
maxd, ndiff, nel, dec_bad = 0.0, 0, 0, []
for it in dev:
    if it['cond'] == 'k0':
        continue
    p, _ = load_pvals(it); p0, _ = load_pvals(k0_of(it))
    dT = p0.shape[0]
    off = ~np.eye(dT, dtype=bool)
    d = np.abs(p[:dT, :dT] - p0)[off]
    maxd, ndiff, nel = max(maxd, float(d.max())), ndiff + int((d > 0).sum()), nel + int(off.sum())
    for al in ALPHA_L_GRID:
        if not np.array_equal(reject(p, 'RL', al)[:dT, :dT], reject(p0, 'RL', al)):
            dec_bad.append(f'{base_key(it)} alpha {al:g}')
it0 = dev[1]
X, _, _ = assemble6(it0)
repro = bool(np.array_equal(SCR.p_hsic(X), load_pvals(it0)[0]))
gate('G2', maxd <= P_TOL and not dec_bad and repro, max_abs_dp=maxd, elements_differing=ndiff, elements=nel,
     decision_mismatch=dec_bad[:10], p_hsic_reproducible=repro)

# G3: alpha choice recorded (alpha6.py, no model output)
A = json.loads((OUT6 / 'alpha6.json').read_text()) if (OUT6 / 'alpha6.json').exists() else {}
gate('G3', 'alpha_L' in A and 'alpha_H' in A, alpha_L=A.get('alpha_L'), alpha_H=A.get('alpha_H'), table=A.get('table'))


def npz(m, k):
    z = np.load(OUT6 / m / f'{k}.npz', allow_pickle=False)
    return {n: z[n] for n in z.files}


def same_arrays(o1, o2):
    ks = [k for k in o1 if k != 'meta']
    return set(ks) == {k for k in o2 if k != 'meta'} and all(np.array_equal(o1[k], o2[k]) for k in ks)


# G4: conditional R-L statement on DEV6; R-oracle equals plain k0 bit for bit
cond_n = {m: 0 for m in MODELS}; cond_bad = []
for it in dev:
    if it['cond'] == 'k0':
        continue
    p, _ = load_pvals(it); p0, _ = load_pvals(k0_of(it))
    dT = p0.shape[0]
    same = np.array_equal(reject(p, 'RL', A['alpha_L'])[:dT, :dT], reject(p0, 'RL', A['alpha_L']))
    for m in MODELS:
        o, o0 = npz(m, key6(it, 'RL')), npz(m, key6(k0_of(it), 'RL'))
        if same and not json.loads(str(o['meta']))['mixed']:
            cond_n[m] += 1
            ok = sorted(o['comp_sha'].tolist()) == sorted(o0['comp_sha'].tolist()) and np.array_equal(o['probs_T'], o0['probs_T'])
            if m == 'cdfm':
                ok = ok and np.array_equal(o['adj_T'], o0['adj_T']) and \
                    dict(zip(o['comp_sha'].tolist(), o['thr_components'].tolist())) == dict(zip(o0['comp_sha'].tolist(), o0['thr_components'].tolist()))
            if not ok:
                cond_bad.append(f'{m} {base_key(it)}')
orc_bad = []
for m in MODELS:
    for sid, cond in ORACLE_KEYS:
        it = byk[f'{sid}__{cond}']
        if not same_arrays(npz(m, key6(it, 'oracle')), npz(m, key6(k0_of(it), 'plain'))):
            orc_bad.append(f'{m} {sid} {cond}')
gate('G4', not cond_bad and all(v >= 1 for v in cond_n.values()) and not orc_bad, conditional_inputs=cond_n,
     conditional_failures=cond_bad[:10], oracle_failures=orc_bad)

# G5: the frozen selector reproduces CDFM's NATIVE thresholds; the local threshold at k0 equals NATIVE
dmax, loc_bad = 0.0, []
for it in dev:
    o = npz('cdfm', key6(it, 'plain'))
    dmax = max(dmax, abs(SEL.thr(np.asarray(o['probs'], float)) - float(o['threshold'])))
    if it['cond'] == 'k0':
        dT = o['probs'].shape[0]
        if abs(SEL.thr(np.asarray(o['probs'][:dT, :dT], float)) - float(o['threshold'])) > 1e-12:
            loc_bad.append(base_key(it))
gate('G5', dmax <= 1e-12 and not loc_bad, max_abs_threshold_diff=dmax, local_k0_mismatch=loc_bad)

# G6: statistics code against reference computations and predefined cases
rng = np.random.default_rng(6)
cases = {}
x = rng.normal(0.01, 0.05, 15)
s1 = S6.strat_t([x], -0.03)
ref = stats.ttest_1samp(x + 0.03, 0.0, alternative='greater')
cases['single_cell_vs_ttest'] = abs(s1['t'] - ref.statistic) < 1e-12 and abs(s1['p'] - ref.pvalue) <= 1e-9 * max(ref.pvalue, 1e-300)
cl = [rng.normal(0, s, 15) for s in (0.02, 0.04, 0.06, 0.08)]
w = 0.25; est = sum(w * c.mean() for c in cl); av = [w * w * c.var(ddof=1) / 15 for c in cl]
se = np.sqrt(sum(av)); df = sum(av) ** 2 / sum(v * v / 14 for v in av)
s4 = S6.strat_t(cl, -0.03)
cases['stratified_vs_formula'] = abs(s4['estimate'] - est) < 1e-15 and abs(s4['p'] - stats.t.sf((est + 0.03) / se, df)) < 1e-15
ni = S6.ni_composite(cl, [c - 0.01 for c in cl], 0.03)
cases['ni_p_is_max'] = ni['p'] == max(ni['Q0']['p'], ni['QA20']['p'])
cases['degenerate'] = S6.strat_t([np.zeros(15)] * 4, 0.0)['p'] == 1.0 and S6.strat_t([np.zeros(15)] * 4, 0.0)['degenerate']
hl = S6.holm({'a': 0.001, 'b': 0.04, 'c': 0.03, 'd': 0.5})
cases['holm_stop'] = hl['a'][2] and not hl['c'][2] and not hl['b'][2] and not hl['d'][2]
cp_ok = True
for k, n in ((0, 20), (3, 20), (20, 20), (7, 120)):
    lo, hi = S6.clopper_pearson(k, n)
    r = stats.binomtest(k, n).proportion_ci(confidence_level=0.95, method='exact')
    cp_ok &= abs(lo - r.low) < 1e-10 and abs(hi - r.high) < 1e-10
cases['clopper_pearson_vs_scipy'] = bool(cp_ok)
gate('G6', all(cases.values()), cases=cases)

# G7: reading code and completeness check run on DEV6 (structure only)
py = sys.executable
r1 = subprocess.run([py, '-I', '-W', 'ignore', os.path.join(HERE, 'analyze6.py'), '--set', 'DEV6', '--smoke'], capture_output=True, text=True)
r2 = subprocess.run([py, '-I', '-W', 'ignore', os.path.join(HERE, 'completeness6.py'), '--set', 'DEV6'], capture_output=True, text=True)
gate('G7', r1.returncode == 0 and 'SMOKE OK' in r1.stdout and r2.returncode == 0,
     analyze_smoke=r1.stdout.strip()[-200:], analyze_err=r1.stderr.strip()[-300:], completeness_rc=r2.returncode,
     completeness_tail=r2.stdout.strip()[-300:])

# G8: determinism (reruns bit for bit)
rep_bad = []
for m in MODELS:
    for arm in ('plain', 'RL', 'RH'):
        for sid, cond in REP_KEYS:
            it = byk[f'{sid}__{cond}']
            if not same_arrays(npz(m, key6(it, f'{arm}__rep')), npz(m, key6(it, arm))):
                rep_bad.append(f'{m} {arm} {sid} {cond}')
gate('G8', not rep_bad, failures=rep_bad)


# G9: runtime and memory; estimate for the PN6 run; full pipeline against target-only cost
def log(task, name):
    p = OUT6 / task / name
    return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()] if p.exists() else []


def med(recs, f):
    v = [r['runtime_s'] for r in recs if f(r)]
    return statistics.median(v) if v else None


pv = log('pvals', 'log_DEV6.jsonl')
parts, peaks = {}, {}
for m in MODELS:
    peaks[m] = max([r.get('peak_wset_mb', 0) for arm in ('plain', 'RL', 'RH') for r in log(m, f'log_DEV6_{arm}.jsonl')] or [0])
for it in items6('PN6'):
    dT = 11 if it['kind'] == 'real' else CELLS[it['ci']][0]
    if it['kind'] == 'syn':
        t = med(pv, lambda r: r['cond'] == it['cond'] and r['dT'] == dT) or 0.0
    else:
        D = 11 if it['cond'] == 'k0' else 11 + int(it['cond'][1:3])
        base = med(pv, lambda r: r['cond'] == 'e0' and r['dT'] == 20) or 0.0   # D = 40
        t = base * (D / 40.0) ** 2
    parts['pvals'] = parts.get('pvals', 0.0) + t
    for m in MODELS:
        for arm in ('plain',) + R_ARMS:
            if arm == 'plain' and it['kind'] == 'real':
                continue
            recs = log(m, f'log_DEV6_{arm}.jsonl')
            if it['kind'] == 'syn':
                t = med(recs, lambda r: r['cond'] == it['cond'] and r['dT'] == dT)
            else:
                t = med(recs, lambda r: r['cond'] == 'k0' and r['dT'] == 10)   # one 11-variable component
            parts[f'{m}|{arm}'] = parts.get(f'{m}|{arm}', 0.0) + (t or 0.0)
total = sum(parts.values())
estimate = total * 1.10 + 300
full = {}
for m in MODELS:
    for arm in ('fullRL', 'fullRH'):
        recs = log(m, f'log_DEV6_{arm}.jsonl')
        full[f'{m}|{arm}'] = dict(target_components_s=round(sum(r.get('model_s', 0) for r in recs), 1),
                                  other_components_s=round(sum(r.get('other_components_s', 0) for r in recs), 1),
                                  n_other_components=int(sum(r.get('n_other_components', 0) for r in recs)), n_jobs=len(recs))
gate('G9', estimate <= BUDGET_S, estimate_s=round(estimate, 1), estimate_h=round(estimate / 3600, 2),
     parts_s={k: round(v, 1) for k, v in parts.items()}, peak_wset_mb=peaks, full_pipeline_dev6=full)

out = dict(gates=G, ok=all(g['ok'] for g in G.values()))
(OUT6 / 'gates6.json').write_text(json.dumps(out, indent=1, default=float))
print('ALL GATES PASS' if out['ok'] else 'SOME GATE FAILED')
sys.exit(0 if out['ok'] else 1)
