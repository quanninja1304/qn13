"""P-N4 feasibility gates G1-G8 (rules PN4 v1 §8), on DEV4 outputs and on old outputs, before the code freeze.

DEV4 outputs are used only for these gates; no contrast is computed on DEV4.
usage: gates4.py  ->  pn4_out/gates4.json (exit 1 if a gate fails)
"""
import os, sys, json, time
T_ = '2'
for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[v] = T_
os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import psutil
from scipy import stats
from common4 import *
from common2 import omega, N_RFF, assemble2                     # frozen P-N2
from selector4 import thr as thr_copy
from measures4 import locked_contrasts, descriptive, count_upper, sym
from selector4 import count_target
from stats4 import strat4, composite, holm

G, bad = {}, []
OUT2 = ART / 'n2_runs' / 'pn2_out'
DESIGN = REPO / 'reports' / 'n4_cdfm_threshold_path_2026-11-21' / 'design' / 'pn4_design_inputs.json'
near = lambda x, ref, tol=1e-10: abs(float(x) - float(ref)) <= tol * max(1.0, abs(float(ref)))
relp = lambda x, ref, tol=1e-9: abs(float(x) - float(ref)) <= tol * abs(float(ref))


def gate(name, ok, **info):
    G[name] = dict(pass_=bool(ok), **info)
    if not ok:
        bad.append(name)


# ---------------- G1: k = 20 generic path == padding2 / assemble2, bitwise (DEV4) ----------------
g1 = []
for sid, ci, seed in systems4('DEV4'):
    for e in (0, eT_of(ci)):
        p2, pg = padding2(ci, seed, f'e{e}'), padding_generic(ci, seed, 20, e)
        same = p2['P'].tobytes() == pg['P'].tobytes() and np.array_equal(p2['g'], pg['g']) and p2['x64'].tobytes() == pg['x64'].tobytes()
        X2, _, _ = assemble2(sid, ci, seed, f'e{e}'); X4, _, _ = assemble4(sid, ci, seed, f'k20_e{e}')
        g1.append(bool(same and X2.tobytes() == X4.tobytes()))
gate('G1', all(g1), n=len(g1))

# ---------------- G2: k = 40 generator checks (DEV4) ----------------
from avici.synthetic.rff import RFFAdditive
c2 = dict(alone_vs_table=[], params_same=[], graph_U_lt_p=[], target_bitwise=[], fidelity_maxrel=[])
pad_stats = []
for sid, ci, seed in systems4('DEV4'):
    dT, eT, mech = CELLS[ci]
    t = target(sid, ci, seed); x0 = zscore(t['x'])
    P, P2 = pad_params(seed, mech, k=40), pad_params(seed, mech, k=40)
    c2['params_same'].append(all(np.array_equal(P[q], P2[q]) for q in P))
    for e in (0, eT):
        X, _, pad = assemble4(sid, ci, seed, f'k40_e{e}')
        c2['target_bitwise'].append(np.ascontiguousarray(X[:, :dT]).tobytes() == x0.tobytes())
        alone = padding_generic(ci, seed, 40, e)['P']
        c2['alone_vs_table'].append(np.ascontiguousarray(zscore(alone)).tobytes() == np.ascontiguousarray(X[:, dT:]).tobytes())
        p = min(2 * e / 39, 0.99); gref = np.zeros((40, 40), np.int8)
        for aa in range(40):
            for bb in range(aa + 1, 40):
                if P['U'][aa, bb] < p:
                    gref[P['pi'][aa], P['pi'][bb]] = 1
        c2['graph_U_lt_p'].append(bool(np.array_equal(gref, pad['g'])))
        x = pad_data(P, pad['g'], mech, 1.0); worst = 0.0
        for j in range(40):
            isp = pad['g'][:, j].astype(bool); pa = np.where(isp)[0]; zj = P['noise_scale'][j] * P['Z'][:, j]
            if mech == 'rff':
                ref = RFFAdditive._rff_mechanism(x=x, z=zj, is_parent=isp, bias=np.array([P['bias'][j]]),
                                                 omega=omega(P, j, pa), b=P['b'][j], w=P['w'][j], c=P['c'][j], n_rff=N_RFF)
            else:
                ref = (x @ (P['W'][:, j] * isp)) + np.array([P['bias'][j]]) + zj
            worst = max(worst, float(np.abs(x[:, j] - ref).max() / max(1.0, np.abs(ref).max())))
        c2['fidelity_maxrel'].append(worst)
        pad_stats.append(dict(sys=sid, e=e, n_edges=pad['n_edges'], n_isolated=pad['n_isolated']))
gate('G2', all(c2['alone_vs_table']) and all(c2['params_same']) and all(c2['graph_U_lt_p']) and all(c2['target_bitwise'])
     and max(c2['fidelity_maxrel']) <= 1e-9,
     **{q: (all(v) if q != 'fidelity_maxrel' else max(v)) for q, v in c2.items()}, n_inputs=len(c2['target_bitwise']),
     padding_stats=pad_stats)


# ---------------- G3: selector copy reproduces stored thresholds ----------------
def old(sid, cond):
    return np.load(OUT2 / 'cdfm' / f'{sid}__{cond}__plain.npz')


worst, n3 = 0.0, 0
for setname, reps in (('EXP2', 5), ('HELD2', 15)):
    for ci in RFF_CELLS:
        for r in range(reps):
            for cond in ('e0', f'e{eT_of(ci)}'):
                o = old(f'{setname}-c{ci}-r{r}', cond)
                worst = max(worst, abs(thr_copy(np.asarray(o['probs'], float)) - float(o['threshold']))); n3 += 1
for f in sorted((OUT4 / 'cdfm').glob('DEV4-*.npz')):
    o = np.load(f)
    worst = max(worst, abs(thr_copy(np.asarray(o['probs'], float)) - float(o['threshold']))); n3 += 1
gate('G3', worst <= 1e-12, max_abs=worst, n_outputs=n3)


# ---------------- G4: reading code reproduces old numbers ----------------
def old_rows(setname, reps, with_desc=False):
    rows, cells, consistent = [], [], True
    for ci in RFF_CELLS:
        dT, eT = CELLS[ci][0], eT_of(ci)
        for r in range(reps):
            sid = f'{setname}-c{ci}-r{r}'
            o0, o1 = old(sid, 'e0'), old(sid, f'e{eT}')
            P0, P1 = np.asarray(o0['probs'], float), np.asarray(o1['probs'], float)
            t0, t1 = float(o0['threshold']), float(o1['threshold'])
            m = locked_contrasts(P0, P1, t0, t1, dT)
            if with_desc:
                m['desc'] = descriptive(P0, P1, t0, t1, dT)
            consistent &= (count_upper(sym(o0['adj_native'][:dT, :dT])) == m['m_e0'] and
                           count_upper(sym(o1['adj_native'][:dT, :dT])) == m['m_eT'])
            rows.append(m); cells.append(ci)
    return rows, cells, bool(consistent)


design = json.loads(DESIGN.read_text())['HELD2']['contrasts']
hr, hc, cons_h = old_rows('HELD2', 15)
g4 = {}
for q in ('D1', 'D2', 'D3a', 'D3b', 'S', 'T', 'TpS', 'TmS'):
    st = strat4([x[q] for x in hr], hc, 1, 0.0)
    g4[f'HELD2_{q}_vs_design'] = near(st['theta'], design[q]['theta']) and near(st['ci95'][0], design[q]['ci95'][0]) \
        and near(st['ci95'][1], design[q]['ci95'][1])
rd = json.loads((OUT2 / 'held2_held2_reading.json').read_text(encoding='utf-8'))
for q, part in (('S', 'score_part'), ('T', 'threshold_part')):
    ref = rd['cdfm_threshold_split']['rff'][part]; st = strat4([x[q] for x in hr], hc, 1, 0.0)
    g4[f'HELD2_{q}_vs_held2_reading'] = all(near(st[f], ref[f]) for f in ('theta', 'se', 'df')) and \
        all(near(a_, b_) for a_, b_ in zip(st['ci95'], ref['ci95']))
g4['HELD2_native_count_consistent'] = cons_h
er, ec, cons_e = old_rows('EXP2', 5, with_desc=True)
pa = json.loads((ART / 'n3_runs' / 'pn3_out' / 'partA.json').read_text())['summary']
st = strat4([x['desc']['d_logit'] for x in er], ec, 1, 0.0)
g4['EXP2_d_logit_vs_partA'] = near(st['theta'], pa['d_logit']['theta']) and all(near(a_, b_) for a_, b_ in zip(st['ci95'], pa['d_logit']['ci95']))
for gp in ('T', 'P', 'X'):
    st = strat4([x['desc']['phi'][gp] for x in er], ec, 1, 0.0)
    g4[f'EXP2_phi_{gp}_vs_partA'] = near(st['theta'], pa['phi'][gp]['theta'])
for key in ('000', '001', '010', '011', '111'):
    g4[f'EXP2_count_{key}_eT_vs_partA'] = near(np.mean([x['desc']['counts'][key]['on_eT_scores'] for x in er]),
                                               pa['counts_on_eT_scores'][key])
for q, part in (('S', 'score_part_e0anchor'), ('T', 'threshold_part_e0anchor')):
    g4[f'EXP2_{q}_vs_partA'] = near(strat4([x[q] for x in er], ec, 1, 0.0)['theta'], pa[part]['theta'])
g4['EXP2_native_count_consistent'] = cons_e
gate('G4', all(g4.values()), checks=g4)

# ---------------- G5: test code vs full-precision HC1, plus locked unit cases ----------------
hc1 = rd['hypotheses']['HC1']
st = strat4([x['D2'] for x in hr], hc, +1, 0.0)
g5 = dict(HC1_theta=near(st['theta'], hc1['theta']), HC1_se=near(st['se'], hc1['se']), HC1_df=near(st['df'], hc1['df']),
          HC1_t=near(st['t'], hc1['t']), HC1_ci=all(near(a_, b_) for a_, b_ in zip(st['ci95'], hc1['ci95'])),
          HC1_p_relative=relp(st['p_one_sided'], hc1['p_one_sided']))
g5_detail = dict(HC1_recomputed={k_: st[k_] for k_ in ('theta', 'se', 'df', 't', 'p_one_sided', 'ci95')},
                 HC1_reference={k_: hc1[k_] for k_ in ('theta', 'se', 'df', 't', 'p_one_sided', 'ci95')})
# (i) composite p = max of components; a DEGENERATE component forces p = 1
g5['case_i_composite_max'] = composite([dict(p_one_sided=0.001), dict(p_one_sided=0.2), dict(p_one_sided=0.03)]) == 0.2
# (ii) Holm stops at the first non-rejection, even if a later p is below its own threshold
hA = holm({'h1': 0.0001, 'h2': 0.02, 'h3': 0.03, 'h4': 0.04, 'h5': 0.045, 'h6': 0.049, 'h7': 0.0499, 'h8': 0.05})
hB = holm({f'h{i + 1}': p for i, p in enumerate([0.001, 0.004, 0.006, 0.009, 0.012, 0.02, 0.03, 0.5])})
g5['case_ii_holm_stop'] = ([hA[f'h{i}']['label'] for i in range(1, 9)] == ['CONFIRMED'] + ['NOT_CONFIRMED'] * 7 and
                           [hB[f'h{i}']['label'] for i in range(1, 9)] == ['CONFIRMED'] * 5 + ['NOT_CONFIRMED'] * 3 and
                           hA['h8']['holm_threshold'] == 0.05)
# (iii) SE = 0 -> DEGENERATE, p = 1, not confirmed; the composite containing it is not confirmed either
cells20 = [1] * 5 + [3] * 5 + [5] * 5 + [7] * 5
dg = strat4([-3.0] * 20, cells20, -1, 0.0)
good = strat4(list(-3.0 + 0.01 * np.arange(20)), cells20, -1, 0.0)
cp = composite([good, dg])
hh = holm({'deg': cp, 'other': 1e-12})
g5['case_iii_degenerate'] = (dg['degenerate'] and dg['status'] == 'DEGENERATE' and dg['p_one_sided'] == 1.0 and cp == 1.0
                             and hh['deg']['label'] == 'NOT_CONFIRMED' and hh['other']['label'] == 'CONFIRMED')
# (iv) shifted bound: t = (-1.5 - theta) / SE, checked against an independent computation
rng = np.random.default_rng(7)
vals = list(-2.0 + 0.4 * rng.standard_normal(20))
by = {c: [v for v, cc in zip(vals, cells20) if cc == c] for c in (1, 3, 5, 7)}
th_ = sum(np.mean(by[c]) for c in by) / 4
a_c = [(1 / 16) * np.var(by[c], ddof=1) / 5 for c in by]
se_ = np.sqrt(sum(a_c)); df_ = sum(a_c) ** 2 / sum(x * x / 4 for x in a_c)
t_ = (-1.5 - th_) / se_
sb = strat4(vals, cells20, -1, -1.5)
g5['case_iv_shifted_bound'] = near(sb['t'], t_) and near(sb['df'], df_) and relp(sb['p_one_sided'], stats.t.sf(t_, df_))
gate('G5', all(g5.values()), checks=g5, **g5_detail)

# ---------------- G6: CDFM determinism at D = 50 and D = 60 (rerun 2 DEV4 inputs) ----------------
import torch; torch.set_num_threads(2)
from cdfm import CDFM
mdl = CDFM.from_pretrained(str(ART / 'n1_models_cpu' / 'checkpoints/cdfm'), device='cpu', threshold=None)
g6 = {}
for sid, ci, seed, cond in (('DEV4-c1-r0', 1, 451000, 'k40_e0'), ('DEV4-c5-r0', 5, 455000, 'k40_e1')):
    X, _, _ = assemble4(sid, ci, seed, cond)
    r = mdl.predict(X, threshold=None, standardize=False)
    o = np.load(OUT4 / 'cdfm' / f'{key4(sid, cond)}.npz')
    g6[f'{sid}__{cond}__D{X.shape[1]}'] = bool(
        np.asarray(r.probabilities, np.float64).tobytes() == o['probs'].tobytes() and
        np.asarray(r.logits, np.float64).tobytes() == o['logits'].tobytes() and
        np.asarray(r.adjacency, np.int8).tobytes() == o['adj_native'].tobytes() and float(r.threshold) == float(o['threshold']))
gate('G6', all(g6.values()), checks=g6)

# ---------------- G7: runtime estimate; G8: memory at D = 60 ----------------
logf = OUT4 / 'cdfm' / 'log_DEV4.jsonl'
recs = [json.loads(l) for l in logf.read_text(encoding='utf-8').splitlines() if l.strip()]
ok_recs = [x for x in recs if x['status'] == 'ok']
by_d = {}
for x in ok_recs:
    by_d.setdefault(x['d'], []).append(x['runtime_s'])
med = {d: float(np.median(v)) for d, v in sorted(by_d.items())}
need = {}
for sid, ci, seed in systems4('PN4'):
    for cond in conds4(ci):
        d = CELLS[ci][0] + (0 if cond == 'k0' else parse(cond)[0])
        need[d] = need.get(d, 0) + 1
est = sum(med[d] * n for d, n in need.items()) * 1.10 + 60
gate('G7', set(need) <= set(med) and est <= 3 * 3600, median_runtime_s_by_D=med, n_inputs_by_D=need, estimate_s=est,
     n_failed_DEV4=len(recs) - len(ok_recs))
d60 = [x for x in ok_recs if x['d'] == 60]
gate('G8', len(d60) > 0 and len(ok_recs) == len(recs), peak_wset_mb_max=max(x['peak_wset_mb'] for x in ok_recs),
     peak_wset_mb_at_D60=max(x['peak_wset_mb'] for x in d60) if d60 else None,
     available_ram_mb=round(psutil.virtual_memory().available / 2 ** 20, 1))

G['all_pass'] = not bad
G['failed'] = bad
(OUT4 / 'gates4.json').write_text(json.dumps(G, indent=1, default=float))
print(json.dumps({k: (v['pass_'] if isinstance(v, dict) and 'pass_' in v else v) for k, v in G.items()}, indent=1))
print('G7 estimate (s):', round(G['G7']['estimate_s']), '| median runtime by D:', G['G7']['median_runtime_s_by_D'])
sys.exit(1 if bad else 0)
