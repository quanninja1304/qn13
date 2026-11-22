"""P-N5 feasibility gates G1-G7 (rules PN5 v1 §8), before the code freeze. No model is run on the real tables.

G1 data load and X_R; G2 padding generator on the 40 P-N5 seeds; G3 all 81 inputs per table (inputs only, no model);
G4 reading code on DEV5 (structure only, analyze5.py --smoke) and the completeness script on DEV5;
G5 test code against independent computations and locked cases; G6 determinism of the four algorithms on DEV5 (k0 and
one D = 51 input, rerun); G7 time and memory estimate for the 616 P-N5 jobs.
DEV5 (synthetic stand-in, base 470000, 2 draws) outputs are used only here.
Needs: prep5.py PN5 and DEV5, then run5.py <alg> DEV5 for the four algorithms.
usage: gates5.py  ->  pn5_out/gates5.json and pn5_out/inputs5.json (input SHA-256 of the 162 P-N5 inputs); exit 1 if a gate fails
"""
import os, sys, json, subprocess
T_ = '2'
for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[v] = T_
os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import psutil
from scipy import stats
from common5 import *
from common2 import omega, N_RFF                                     # frozen P-N2
from stats5 import paired_t, holm, describe, p51_contrast

G, bad = {}, []
PY = sys.executable


def gate(name, ok, **info):
    G[name] = dict(pass_=bool(ok), **info)
    if not ok:
        bad.append(name)


# ---------------- G1: data load, selection, X_R ----------------
g1, man = {}, manifest()
for t, T in TABLES.items():
    m = man[T['mkey']]['member_used']
    raw, names = load_raw(t)
    i1, i2 = select_idx(raw.shape[0], T['j']), select_idx(raw.shape[0], T['j'])
    rb = real_block(t)
    X64 = rb['XR'].astype(np.float64)
    saved = sha(np.load(xr_file(t))) if xr_file(t).exists() else None
    g1[t] = dict(sha_ok=file_sha(T['path']) == m['sha256'],
                 shape_ok=raw.shape == (m['n_rows'], m['n_cols_used']) and names == m['variables_used'],
                 idx_ok=bool(np.array_equal(i1, i2) and sha(i1)[:16] == T['idx_sha16'] and len(np.unique(i1)) == N_ROWS
                             and np.array_equal(i1, rb['idx'])),
                 idx_sha=rb['idx_sha'], XR_sha=rb['XR_sha'], XR_dtype=str(rb['XR'].dtype), XR_shape=list(rb['XR'].shape),
                 stats_ok=bool(np.isfinite(X64).all() and np.abs(X64.mean(0)).max() < 1e-6 and np.abs(X64.std(0) - 1).max() < 1e-5),
                 col_mean_abs_max=float(np.abs(X64.mean(0)).max()), col_std_dev_max=float(np.abs(X64.std(0) - 1).max()),
                 n_excess_duplicates=rb['n_excess_duplicates'], n_distinct_rows=N_ROWS - rb['n_excess_duplicates'],
                 dup_ok=rb['n_excess_duplicates'] == T['excess_dup'], saved_copy_ok=saved == rb['XR_sha'])
gate('G1', all(all(v[q] for q in ('sha_ok', 'shape_ok', 'idx_ok', 'stats_ok', 'dup_ok', 'saved_copy_ok')) for v in g1.values())
     and all(v['XR_dtype'] == 'float32' and v['XR_shape'] == [N_ROWS, 11] for v in g1.values()), tables=g1)

# ---------------- G2: padding generator on the 40 P-N5 seeds ----------------
from avici.synthetic.rff import RFFAdditive
c2 = dict(k20_equals_padding2=[], e0_graph_empty=[], k40_params_same=[], k40_graph_U_lt_p=[], k40_x64_consistent=[],
          k40_fidelity_maxrel=[])
pad_stats = []
for t in ('sachs', 'wine'):
    for r in range(SETS5['PN5']['draws']):
        seed = draw_seed('PN5', t, r)
        for e in ES:
            pg, p2 = pad_block(seed, 20, e), padding2(1, seed, f'e{e}')     # P-N1 cell 1 is (10, 1, 'rff')
            c2['k20_equals_padding2'].append(bool(pg['P'].tobytes() == p2['P'].tobytes() and np.array_equal(pg['g'], p2['g'])
                                                  and pg['x64'].tobytes() == p2['x64'].tobytes()))
            if e == 0:
                c2['e0_graph_empty'].append(pg['n_edges'] == 0)
            pad_stats.append(dict(table=t, r=r, k=20, e=e, n_edges=pg['n_edges'], n_isolated=pg['n_isolated']))
        P, P2 = pad_params(seed, 'rff', k=40), pad_params(seed, 'rff', k=40)
        c2['k40_params_same'].append(all(np.array_equal(P[q], P2[q]) for q in P))
        for e in ES:
            pad = pad_block(seed, 40, e)
            p = min(2 * e / 39, 0.99)
            gref = np.zeros((40, 40), np.int8)
            for aa in range(40):
                for bb in range(aa + 1, 40):
                    if P['U'][aa, bb] < p:
                        gref[P['pi'][aa], P['pi'][bb]] = 1
            c2['k40_graph_U_lt_p'].append(bool(np.array_equal(gref, pad['g'])))
            if e == 0:
                c2['e0_graph_empty'].append(pad['n_edges'] == 0)
            x = pad_data(P, pad['g'], 'rff', 1.0)
            c2['k40_x64_consistent'].append(x.tobytes() == pad['x64'].tobytes())
            worst = 0.0
            for j in range(40):
                isp = pad['g'][:, j].astype(bool); pa = np.where(isp)[0]; zj = P['noise_scale'][j] * P['Z'][:, j]
                ref = RFFAdditive._rff_mechanism(x=x, z=zj, is_parent=isp, bias=np.array([P['bias'][j]]), omega=omega(P, j, pa),
                                                 b=P['b'][j], w=P['w'][j], c=P['c'][j], n_rff=N_RFF)
                worst = max(worst, float(np.abs(x[:, j] - ref).max() / max(1.0, np.abs(ref).max())))
            c2['k40_fidelity_maxrel'].append(worst)
            pad_stats.append(dict(table=t, r=r, k=40, e=e, n_edges=pad['n_edges'], n_isolated=pad['n_isolated']))
summ2 = {q: (max(v) if q == 'k40_fidelity_maxrel' else bool(all(v))) for q, v in c2.items()}
summ2.update({f'n_{q}': len(v) for q, v in c2.items()})
e2 = [s_['n_edges'] for s_ in pad_stats if s_['e'] == 2]
gate('G2', all(v for q, v in summ2.items() if isinstance(v, bool)) and summ2['k40_fidelity_maxrel'] <= 1e-9,
     **summ2, structured_edges_k20=[min(x['n_edges'] for x in pad_stats if x['e'] == 2 and x['k'] == 20),
                                    max(x['n_edges'] for x in pad_stats if x['e'] == 2 and x['k'] == 20)],
     structured_edges_k40=[min(x['n_edges'] for x in pad_stats if x['e'] == 2 and x['k'] == 40),
                           max(x['n_edges'] for x in pad_stats if x['e'] == 2 and x['k'] == 40)])

# ---------------- G3: all 81 inputs per table (inputs only) ----------------
inputs, g3 = {}, dict(n_inputs=0, n_ok=0, failed=[])
for t in ('sachs', 'wine'):
    XR = real_block(t)['XR']
    for cond in CONDS:
        for r in ([None] if cond == 'k0' else range(SETS5['PN5']['draws'])):
            X, rb, pad = assemble5('PN5', t, cond, r)                 # asserts both blocks bitwise identical
            k = 0 if cond == 'k0' else parse(cond)[0]
            ok = bool(X.dtype == np.float32 and X.flags['C_CONTIGUOUS'] and np.isfinite(X).all() and X.shape == (N_ROWS, 11 + k)
                      and np.ascontiguousarray(X[:, :11]).tobytes() == XR.tobytes()
                      and (pad is None or np.ascontiguousarray(X[:, 11:]).tobytes() == pad['P'].tobytes()))
            inputs[key5(t, cond, r)] = sha(X)
            g3['n_inputs'] += 1; g3['n_ok'] += int(ok)
            if not ok:
                g3['failed'].append(key5(t, cond, r))
(OUT5 / 'inputs5.json').write_text(json.dumps(inputs, indent=1))
gate('G3', g3['n_inputs'] == 162 and g3['n_ok'] == 162, **g3, n_distinct_input_sha=len(set(inputs.values())))

# ---------------- G4: reading code and completeness script on DEV5 (structure only) ----------------
pr = subprocess.run([PY, '-I', '-W', 'ignore', os.path.join(HERE, 'analyze5.py'), '--set', 'DEV5', '--smoke'],
                    capture_output=True, text=True)
st = json.loads((OUT5 / 'dev5_reading_structure.json').read_text()) if pr.returncode == 0 else {}
pc_ = subprocess.run([PY, '-I', '-W', 'ignore', os.path.join(HERE, 'completeness5.py'), '--set', 'DEV5'], capture_output=True, text=True)
ct = json.loads((OUT5 / 'dev5_completeness_test.json').read_text())
only_freeze = all(p.startswith('freeze gate') for p in ct['problems'])
gate('G4', pr.returncode == 0 and 'SMOKE OK' in pr.stdout and st.get('n_hypotheses') == 4 and only_freeze
     and ct['n_jobs'] == sum(len(jobs5('DEV5', alg, True)) for alg in ALGS),
     analyze_smoke_returncode=pr.returncode, smoke_stdout=pr.stdout.strip()[-300:], hypothesis_ids=st.get('hypothesis_ids'),
     completeness_dev5_problems=ct['problems'], completeness_dev5_only_freeze_items_fail=only_freeze,
     completeness_dev5_counts={alg: {q: v[q] for q in ('jobs', 'ok', 'timeout', 'error', 'budget_stop')}
                               for alg, v in ct['per_algorithm'].items()})

# ---------------- G5: test code ----------------
rng = np.random.default_rng(20261122)
near = lambda x, ref, tol=1e-12: abs(float(x) - float(ref)) <= tol * max(1.0, abs(float(ref)))
relp = lambda x, ref, tol=1e-9: abs(float(x) - float(ref)) <= tol * abs(float(ref))
g5, det = {}, []
ok_i = True
for vals in [rng.normal(0.3, 1.0, 20) for _ in range(4)] + [rng.integers(-2, 5, 20).astype(float), rng.normal(-0.5, 1.0, 20)]:
    ours, ref = paired_t(vals, +1, 0.0), stats.ttest_1samp(vals, 0.0, alternative='greater')
    ok_i &= near(ours['t'], ref.statistic) and relp(ours['p_one_sided'], ref.pvalue) and ours['df'] == 19
    det.append(dict(t=ours['t'], t_ref=float(ref.statistic), p=ours['p_one_sided'], p_ref=float(ref.pvalue)))
g5['case_i_paired_t_vs_scipy'] = bool(ok_i and paired_t(vals, +1, 0.0)['estimate_opposite_side'])
dg = paired_t([3.0] * 20, +1, 0.0)
dz = paired_t([0.0] * 20, +1, 0.0)
hh = holm({'deg': dg['p_one_sided'], 'other': 1e-12})
g5['case_ii_degenerate'] = bool(dg['degenerate'] and dg['status'] == 'DEGENERATE' and dg['p_one_sided'] == 1.0 and dz['degenerate']
                                and dz['p_one_sided'] == 1.0 and hh['deg']['label'] == 'NOT_CONFIRMED' and hh['other']['label'] == 'CONFIRMED')
hA = holm({'h1': 0.0001, 'h2': 0.02, 'h3': 0.03, 'h4': 0.04, 'h5': 0.045, 'h6': 0.049, 'h7': 0.0499, 'h8': 0.05})
hB = holm({f'h{i + 1}': p for i, p in enumerate([0.001, 0.004, 0.006, 0.009, 0.012, 0.02, 0.03, 0.5])})
g5['case_iii_holm_stop'] = bool([hA[f'h{i}']['label'] for i in range(1, 9)] == ['CONFIRMED'] + ['NOT_CONFIRMED'] * 7 and
                                [hB[f'h{i}']['label'] for i in range(1, 9)] == ['CONFIRMED'] * 5 + ['NOT_CONFIRMED'] * 3 and
                                hA['h8']['holm_threshold'] == 0.05)
g5['case_iv_max_contrast'] = bool(p51_contrast([5, 3, 4, 7], [[2, 4, 1, 7], [3, 1, 4, 8]]) == [2.0, -1.0, 0.0, -1.0]
                                  and p51_contrast([5, 3], [[2, None], [3, 1]]) == [2.0, None]
                                  and p51_contrast([5, 2], [[1, 1]]) == [4.0, 1.0])
d1, d2 = describe([1, None, 3]), describe([None, None])
g5['case_v_timeout_excluded'] = bool(d1['n_completed'] == 2 and d1['n_timeout'] == 1 and d1['mean'] == 2.0 and d1['min'] == 1.0
                                     and d2['n_completed'] == 0 and d2['n_timeout'] == 2 and 'mean' not in d2)
cnt = paired_t([1, 0, 0, 2, -1, 3, 0, 1], +1, 0.0)
g5['case_vi_sign_counts'] = bool(cnt['n_above'] == 4 and cnt['n_at'] == 3 and cnt['n_below'] == 1 and cnt['n_distinct'] == 5)
gate('G5', all(g5.values()), checks=g5, paired_t_vs_scipy=det)

# ---------------- G6: determinism on DEV5 ----------------
g6 = {}
for alg in ALGS:
    for k1 in (key5('standin', 'k0'), key5('standin', 'k40_e0', 0)):
        f1, f2 = OUT5 / alg / f'{k1}.npz', OUT5 / alg / f'{k1}__rep.npz'
        if not (f1.exists() and f2.exists()):
            g6[f'{alg}:{k1}'] = False
            continue
        z1, z2 = np.load(f1), np.load(f2)
        q1 = [q for q in z1.files if q != 'meta']
        g6[f'{alg}:{k1}'] = bool(set(q1) == {q for q in z2.files if q != 'meta'} and all(z1[q].tobytes() == z2[q].tobytes() for q in q1))
gate('G6', len(g6) == 8 and all(g6.values()), checks=g6)

# ---------------- G7: time and memory ----------------
def etype(cond):
    return 'k0' if cond == 'k0' else f"e{parse(cond)[1]}"


rt, mem = {}, {}
for alg in ALGS:
    for l in (OUT5 / alg / 'log_DEV5.jsonl').read_text(encoding='utf-8').splitlines():
        x = json.loads(l)
        if x.get('status') == 'ok':
            rt.setdefault((alg, x['d'], etype(x['cond'])), []).append(x['runtime_s'])
            mem[alg] = max(mem.get(alg, 0.0), x['peak_wset_mb'] if alg in MODELS else (x.get('worker_peak_wset_mb') or 0.0))
med = {k: float(np.median(v)) for k, v in rt.items()}
need = {}
for alg in ALGS:
    for t, cond, r, rp in jobs5('PN5', alg):
        q = (alg, 11 + (0 if cond == 'k0' else parse(cond)[0]), etype(cond))
        need[q] = need.get(q, 0) + 1
missing = [q for q in need if q not in med]
est_jobs = sum(med[q] * n for q, n in need.items() if q in med)
est = est_jobs * 1.10 + 300
gate('G7', not missing and est <= BUDGET_S, estimate_s=est, estimate_h=est / 3600, n_jobs=sum(need.values()),
     median_runtime_s={f'{a_}|D{d}|{e}': v for (a_, d, e), v in sorted(med.items())},
     n_jobs_by_cell={f'{a_}|D{d}|{e}': v for (a_, d, e), v in sorted(need.items())}, missing_cells=[str(q) for q in missing],
     peak_wset_mb=mem, available_ram_mb=round(psutil.virtual_memory().available / 2 ** 20, 1),
     note='DEV5 medians include AVICI compile time on the first input of each width (conservative)')

G['all_pass'] = not bad
G['failed'] = bad
(OUT5 / 'gates5.json').write_text(json.dumps(G, indent=1, default=float))
print(json.dumps({k: (v['pass_'] if isinstance(v, dict) and 'pass_' in v else v) for k, v in G.items()}, indent=1))
print('G7 estimate (h):', round(G['G7']['estimate_h'], 2), '| peak MB:', G['G7']['peak_wset_mb'])
sys.exit(1 if bad else 0)
