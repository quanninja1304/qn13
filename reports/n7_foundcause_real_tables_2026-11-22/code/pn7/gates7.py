"""P-N7 gates G1-G8 on DEV7 (rules PN7 v1 §7). Writes pn7_out/gates7.json; exits 1 if any gate fails.

G2 compares a P-N1 DEV output saved on 2026-11-13 with a new call: if they differ, the gate fails and reports the
largest deviation; no tolerance is chosen here (rules §7).
usage: gates7.py
"""
import os, sys, json, subprocess, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
from scipy import stats as sps
from common7 import (OUT7, OUT5, OUT1, INPUTS5, TABLES, R_DRAWS, BASES_REF, ADAPTER_TOL, COMPARE, BUDGET_S, DT, P1_DEV,
                     jobs7, key7, input_key, assemble7, load_out, schedule_source_check, row_indices, max_abs_diff,
                     bitwise_equal, sha)
from metrics import skel_native                      # frozen P-N1
from stats7 import t_one_sided, holm

G = {}
PY = sys.executable
dev = {key7(j): j for j in jobs7('DEV7')}

# G1: inputs
dev5 = {}
for line in (OUT5 / 'avici' / 'log_DEV5.jsonl').read_text(encoding='utf-8').splitlines():
    if line.strip():
        r = json.loads(line)
        dev5[r['key']] = r['input_sha']
mism = []
for j in dev.values():
    if j['table'] == 'standin':
        if dev5.get(input_key(j)) != sha(assemble7(j)[0]):
            mism.append(input_key(j))
inputs5 = json.loads(INPUTS5.read_text())
real_mism, n_real = [], 0
for t in TABLES:
    for j in jobs7('PN7', t):
        if j['variant'] == 'api':
            n_real += 1
            if inputs5.get(input_key(j)) != sha(assemble7(j)[0]):
                real_mism.append(input_key(j))
G['G1'] = dict(ok=not mism and not real_mism and n_real == 2 * (1 + R_DRAWS), dev_mismatch=mism, n_real_inputs=n_real,
               real_mismatch=real_mism)

# G2: FoundCause configuration as P-N1 (bitwise against the saved P-N1 DEV output)
j2 = [j for j in dev.values() if j['table'] == 'p1dev'][0]
new = load_out(j2)
z = np.load(OUT1 / 'foundcause' / f"{P1_DEV['key']}.npz", allow_pickle=False)
old = {n: z[n] for n in z.files}
p1_log = [json.loads(l) for l in (OUT1 / 'foundcause' / 'log_dev.jsonl').read_text().splitlines() if l.strip()]
p1_sha = [r['input_sha'] for r in p1_log if r['key'] == P1_DEV['key']]
dev_g2 = {k: max_abs_diff(new[k], old[k]) for k in COMPARE}
G['G2'] = dict(ok=bool(p1_sha and new['meta']['input_sha'] == p1_sha[0] and bitwise_equal(new, old)),
               input_matches_p1_log=bool(p1_sha and new['meta']['input_sha'] == p1_sha[0]), max_abs_diff=dev_g2)

# G3, G3b: rerun and adapter at k0 of DEV7
g = {j['variant']: load_out(j) for j in dev.values() if j['table'] == 'standin' and j['cond'] == 'k0'}
G['G3'] = dict(ok=bool(bitwise_equal(g['api'], g['rep'])))
d42 = {k: max_abs_diff(g['sched42'][k], g['api'][k]) for k in ('probs', 'agreement', 'adj_native')}
G['G3b'] = dict(ok=max(d42.values()) <= ADAPTER_TOL, max_abs_diff=d42, tolerance=ADAPTER_TOL)

# G3c: row indices (source check, recomputation; no model call)
src = schedule_source_check()
rows_ok, n_checked = True, 0
for js in [list(dev.values())] + [jobs7('PN7', t) for t in TABLES]:
    base_j = [j for j in js if j['cond'] == 'k0' and j['table'] != 'p1dev'][0]
    n0 = assemble7(base_j)[0].shape[0]
    r0 = row_indices(n0)
    for j in js:
        if j['cond'] != 'k0' and j['table'] != 'p1dev':
            n = assemble7(j)[0].shape[0]
            n_checked += 1
            rows_ok &= (n == n0) and all(np.array_equal(x, y) for x, y in zip(r0, row_indices(n)))
G['G3c'] = dict(ok=bool(src['ok'] and rows_ok and n_checked == 2 + 2 * R_DRAWS), source=src, n_padded_inputs=n_checked,
                n_take=int(len(row_indices(500)[0])))

# G4: skeleton reading = adjacency OR its transpose (frozen skel_native)
ok4 = True
for o in g.values():
    a = np.asarray(o['adj_native'])[:DT, :DT] != 0
    ok4 &= np.array_equal(skel_native('foundcause', o, DT) != 0, a | a.T)
G['G4'] = dict(ok=bool(ok4))

# G5: comparator reproduces the 20 reported P5-1 values (both tables, both models)
r5 = json.loads((OUT5 / 'pn5_reading.json').read_text())['hypotheses']
import analyze7 as A
ok5, detail5 = True, {}
for t, L in (('sachs', 'S'), ('wine', 'W')):
    pc0, ges0 = A.p5_skel('pc', f'{t}__k0'), A.p5_skel('ges', f'{t}__k0')
    for alg, M in (('avici', 'A'), ('cdfm', 'C')):
        m0 = A.p5_skel(alg, f'{t}__k0')
        vals = []
        for r in range(R_DRAWS):
            k = f'{t}__k20_e0__r{r:02d}'
            mx = max(A.flips(A.p5_skel('pc', k), pc0), A.flips(A.p5_skel('ges', k), ges0))
            vals.append(A.flips(A.p5_skel(alg, k), m0) - mx)
        same = [float(v) for v in vals] == [float(v) for v in r5[f'P5-1{L}-{M}']['values']]
        detail5[f'P5-1{L}-{M}'] = same
        ok5 &= same
G['G5'] = dict(ok=bool(ok5), detail=detail5)

# G6: statistics code against references
x = np.array([1.0, 2.0, 0.0, 3.0, 1.0, 2.0])
ref = sps.ttest_1samp(x, 0.0, alternative='greater')
t6 = t_one_sided(x)
deg = t_one_sided(np.ones(5))
hh = holm({'a': 0.01, 'b': 0.04})
hh2 = holm({'a': 0.03, 'b': 0.04})
G['G6'] = dict(ok=bool(abs(t6['p'] - ref.pvalue) < 1e-12 and deg['degenerate'] and deg['p'] == 1.0
                       and hh['a'][2] and hh['b'][2] and not hh2['a'][2] and not hh2['b'][2]),
               cases=dict(t_vs_scipy=abs(t6['p'] - ref.pvalue), degenerate=deg['degenerate'], holm=[hh, hh2]))

# G7: reading code (structure only) and the DEV7 completeness check
rs = subprocess.run([PY, '-I', '-W', 'ignore', os.path.join(HERE, 'analyze7.py'), '--set', 'DEV7', '--smoke'],
                    capture_output=True, text=True)
rc = subprocess.run([PY, '-I', '-W', 'ignore', os.path.join(HERE, 'completeness7.py'), '--set', 'DEV7'],
                    capture_output=True, text=True)
G['G7'] = dict(ok=rs.returncode == 0 and 'SMOKE OK' in rs.stdout and rc.returncode == 0,
               analyze_smoke=rs.stdout.strip()[-200:], analyze_err=rs.stderr.strip()[-400:],
               completeness_rc=rc.returncode, completeness_tail=rc.stdout.strip()[-600:])

# G8: time and memory; estimate per main run (one table)
log = [json.loads(l) for l in (OUT7 / 'foundcause' / 'log_dev7.jsonl').read_text().splitlines() if l.strip()]
ok_rec = [r for r in log if r.get('status') == 'ok']
t11 = st.median([r['runtime_s'] for r in ok_rec if r['table'] == 'standin' and r['cond'] == 'k0'])
t31 = st.median([r['runtime_s'] for r in ok_rec if r['table'] == 'standin' and r['cond'] == 'k20_e0'])
per_run = [j for j in jobs7('PN7', 'sachs')]
n11 = sum(1 for j in per_run if j['cond'] == 'k0')
n31 = sum(1 for j in per_run if j['cond'] == 'k20_e0')
raw = n11 * t11 + n31 * t31
est = raw * 1.10 + 300
G['G8'] = dict(ok=est <= BUDGET_S, median_s_D11=t11, median_s_D31=t31, calls_D11=n11, calls_D31=n31,
               estimate_s_per_run=round(est, 1), estimate_h_per_run=round(est / 3600, 2),
               estimate_h_two_runs=round(2 * est / 3600, 2), peak_wset_mb=max(r['peak_wset_mb'] for r in ok_rec),
               g2_runtime_s=[r['runtime_s'] for r in ok_rec if r['table'] == 'p1dev'])
out = dict(gates=G, ok=all(v['ok'] for v in G.values()))
(OUT7 / 'gates7.json').write_text(json.dumps(out, indent=1, default=str))
print(json.dumps({k: v['ok'] for k, v in G.items()}, indent=1), '\nALL OK' if out['ok'] else '\nGATE FAILURE')
sys.exit(0 if out['ok'] else 1)
