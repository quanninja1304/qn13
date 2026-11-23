"""P-N8 / Study 7 development gate (rules PN8 v1 §6), on DEV8 (base 510000) and the DEV5 stand-in only.

G1 adapter, rerun bit-identity, output independent of the graph file; G2 inputs and target block; G3 column-permutation
diagnostic (95th percentile of target-block mean |dp| permuted vs seed change); G4 k0 quality on the 8 linear DEV
systems (mean SEA F1 > complete-graph F1); G5 runtime estimate of the main runs vs rules §8. Code checks: stats8.strat8
against the frozen P-N2 strat; analyze8.py --dev structure run (prints no values).
Writes pn8_out/gates8.json. usage (Study 1 model environment): python -I gates8.py [--g4-config-checked]
"""
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common8 import *
from stats8 import check_against_frozen

CONFIG_CHECKED = '--g4-config-checked' in sys.argv
EST_H = {'A1': 1.4, 'A2': 1.4, 'A3': 2.0, 'A4': 2.0, 'B': 1.7}     # rules §8
jobs = run_jobs('DEV')
by = {j['key']: j for j in jobs}
out = {}
missing = [k for k in by if not out_path(k).exists()]
O = {k: load_out(k) for k in by if k not in missing}

# G1
g1 = dict(missing=missing, adapter_fail=[k for k, o in O.items() if not o['meta']['layout_ok'] or o['meta']['auc_ok'] is False])
rr = next(j for j in jobs if j['role'] == 'rerun')
zd = next(j for j in jobs if j['role'] == 'zerodag')
g1['rerun_bitwise'] = bool(np.array_equal(O[rr['key']]['prob'], O[rr['of']]['prob'])) if rr['key'] in O else False
g1['graph_file_independent'] = bool(np.array_equal(O[zd['key']]['prob'], O[zd['of']]['prob'])) if zd['key'] in O else False
g1['ok'] = not missing and not g1['adapter_fail'] and g1['rerun_bitwise'] and g1['graph_file_independent']
out['G1'] = g1

# G2: regenerated inputs match, target block bit-identical across the inputs of each DEV system
g2bad = []
for k, j in by.items():
    if k in O and O[k]['meta']['input_sha'] != build(j)[2]:
        g2bad.append(k)
for sysid, ci, sseed, i in systems8('DEV8'):
    xs = [syn_input(sysid, ci, sseed, c)[0] for c in CONDS_A]
    if not all(np.array_equal(xs[0][:, :CELLS[ci][0]], x[:, :CELLS[ci][0]]) for x in xs[1:]):
        g2bad.append(f'{sysid}: target block')
out['G2'] = dict(ok=not g2bad, problems=g2bad)

# G3: permutation diagnostic (8 systems, r = 0, A20)
rows = []
for j in jobs:
    if j['role'] != 'perm':
        continue
    base = O[j['of']]; perm = O[j['key']]
    alt = O[next(x['key'] for x in jobs if x['role'] == 'seedalt' and x['of'] == j['of'])]
    dT = base['meta']['dT']
    rows.append(dict(sysid=j['sysid'], dp_perm=M1.dp(perm['prob'], base['prob'], dT)[0],
                     dp_seed=M1.dp(alt['prob'], base['prob'], dT)[0],
                     flips_perm=flips(skel(perm['prob'], dT), skel(base['prob'], dT)),
                     flips_seed=flips(skel(alt['prob'], dT), skel(base['prob'], dT))))
q_perm = float(np.percentile([r['dp_perm'] for r in rows], 95))
q_seed = float(np.percentile([r['dp_seed'] for r in rows], 95))
g3_pass = q_perm <= q_seed
out['G3'] = dict(pass_=g3_pass, label='PASS' if g3_pass else 'POSITION_SENSITIVE', q95_dp_perm=q_perm, q95_dp_seed=q_seed,
                 rows=rows, note='diagnostic only; does not establish or refute permutation equivariance (rules §6)')

# G4: k0 quality on the 8 linear DEV systems (cells 0, 2, 4, 6; r = 0, 1)
g4 = []
off = SETS8['DEV8']['off']
for sysid, ci, sseed, i in systems8('DEV8'):
    if ci not in LINEAR:
        continue
    X0, _, dT, g = syn_input(sysid, ci, sseed, 'k0')
    o = O[f'{sysid}__k0__s{seed_a(i, off)}']
    cl = {}
    for alg in ('pc', 'ges'):
        z = np.load(OUT8 / 'classical' / alg / f'{sysid}__k0.npz', allow_pickle=False)
        s = z['skel'][:dT, :dT] != 0
        cl[alg] = f1((s | s.T)[np.triu_indices(dT, 1)], g)
    g4.append(dict(sysid=sysid, f1_sea=f1(skel(o['prob'], dT), g), f1_pc=cl['pc'], f1_ges=cl['ges'], f1_empty=0.0,
                   f1_complete=float(M1.f1_full_graph(g))))
mean = {k: float(np.mean([r[k] for r in g4])) for k in ('f1_sea', 'f1_pc', 'f1_ges', 'f1_empty', 'f1_complete')}
g4_pass = mean['f1_sea'] > mean['f1_complete']
flag = None if g4_pass else ('BASELINE_TOO_WEAK_FOR_THIS_HARM_TEST' if CONFIG_CHECKED else None)
out['G4'] = dict(pass_=g4_pass, means=mean, rows=g4, flag=flag,
                 needs_config_check=(not g4_pass and not CONFIG_CHECKED),
                 note='limits interpretation only; P8-2 and P8-3 stay in the Holm family of six (rules §6)')

# G5: runtime estimate from DEV timings (wall time per process by D; nearest measured D)
tD = {}
for k, o in O.items():
    tD.setdefault(o['meta']['D'], []).append(o['meta']['wall_total_s'])
tmean = {D: float(np.mean(v)) for D, v in tD.items()}


def est(D):
    near = min(tmean, key=lambda x: abs(x - D))
    return tmean[near] * D / near if near != D else tmean[D]


est_h = {}
for run in EST_H:
    jl = run_jobs(run)
    est_h[run] = sum(est((CELLS[j['ci']][0] + (0 if j['cond'] == 'k0' else 20)) if j['kind'] == 'syn'
                         else (11 if j['cond'] == 'k0' else 31)) for j in jl) / 3600
out['G5'] = dict(per_process_s_by_D=tmean, estimate_h=est_h, rules_estimate_h=EST_H,
                 report_user=any(est_h[r] > 1.5 * EST_H[r] for r in EST_H), total_h=sum(est_h.values()))

# code checks
worst = check_against_frozen()
dev = subprocess.run([sys.executable, '-I', '-X', 'utf8', str(HERE / 'analyze8.py'), '--dev'], capture_output=True, text=True)
out['code'] = dict(strat8_vs_frozen_max_abs=worst, strat8_ok=worst < 1e-12, analyze_dev_exit=dev.returncode,
                   analyze_dev_ok=dev.returncode == 0 and '"dev_structure_ok": true' in dev.stdout)
out['ok_to_freeze'] = bool(g1['ok'] and out['G2']['ok'] and out['code']['strat8_ok'] and out['code']['analyze_dev_ok']
                           and not out['G4']['needs_config_check'])
(OUT8 / 'gates8.json').write_text(json.dumps(out, indent=1))
print(json.dumps(dict(G1=dict((k, v) for k, v in g1.items() if k != 'missing'), n_missing=len(missing),
                      G2_ok=out['G2']['ok'], G3=dict(label=out['G3']['label'], q95_perm=q_perm, q95_seed=q_seed),
                      G4=dict(pass_=g4_pass, means=mean, flag=flag, needs_config_check=out['G4']['needs_config_check']),
                      G5=dict(estimate_h=est_h, total_h=out['G5']['total_h'], report_user=out['G5']['report_user']),
                      code=out['code'], ok_to_freeze=out['ok_to_freeze']), indent=1))
sys.exit(0 if out['ok_to_freeze'] else 1)
