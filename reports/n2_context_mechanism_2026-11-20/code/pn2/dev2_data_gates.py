"""P-N2 DEV2 data-only gates G1-G9 (rules v1 §9) and alpha selection (§8.4). No model is run here.

usage: dev2_data_gates.py   ->  pn2_out/dev2_data_gates.json, pn2_out/alpha.json
"""
import sys, json, time
import numpy as np
from scipy import stats
from common2 import *
from screen import *

SYS = systems2('DEV2')
GRID = (0.01, 0.05, 0.10)
BOOT, BSEED = 2000, 20261120
OUT2.mkdir(parents=True, exist_ok=True)
t_start = time.time()


def z64(x):
    x = np.asarray(x, np.float64)
    return (x - x.mean(0)) / x.std(0)


def clopper_pearson(x, n, a=0.05):
    lo = 0.0 if x == 0 else stats.beta.ppf(a / 2, x, n - x + 1)
    hi = 1.0 if x == n else stats.beta.ppf(1 - a / 2, x + 1, n - x)
    up1 = 1.0 if x == n else stats.beta.ppf(1 - a, x + 1, n - x)
    return [float(lo), float(hi)], float(up1)


def cluster_boot(per_sys, B=BOOT, seed=BSEED):
    """per_sys: list of arrays (one per system) of 0/1 indicators; mean over all inputs, resampling systems."""
    rng = np.random.default_rng(seed)
    S = len(per_sys)
    est = float(np.mean(np.concatenate(per_sys)))
    bs = []
    for _ in range(B):
        idx = rng.integers(0, S, S)
        bs.append(np.mean(np.concatenate([per_sys[i] for i in idx])))
    return est, [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


# ---------------- G1-G7: generator gates ----------------
from avici.synthetic.rff import RFFAdditive
g = {k: [] for k in ('G1', 'G2', 'G3', 'G4_s1_bitwise', 'G4_s0_maxabs', 'G6_maxrel', 'G7')}
pad_stats, g5 = [], []
tables = {}                                           # (sid, cond) -> (X, dT, gT, mech, ci)
for sid, ci, seed in SYS:
    dT, eT, mech = CELLS[ci]
    t = target(sid, ci, seed)
    x0 = zscore(t['x'])
    tables[(sid, 'k0')] = (x0, dT, t['g'], mech, ci)
    P, P2 = pad_params(seed, mech), pad_params(seed, mech)
    same = all(np.array_equal(P[q], P2[q]) for q in P)
    gs = {e: pad_graph(P, e) for e in (0, 0.5, 1, 2, 3)}
    nested = all(np.all(gs[a] <= gs[b]) for a, b in ((0, 0.5), (0.5, 1), (1, 2), (2, 3)))
    g['G3'].append(bool(same and nested))
    # G4
    s1 = padding2(ci, seed, 's1')['P']
    e2 = padding2(ci, seed, 'e2')['P']
    g['G4_s1_bitwise'].append(s1.tobytes() == e2.tobytes())
    d0 = np.abs(z64(pad_data(P, gs[2], mech, s=0.0)) - z64(pad_data(P, gs[0], mech, s=1.0))).max()
    g['G4_s0_maxabs'].append(float(d0))
    # G6: fidelity to AVICI mechanism code, every level, every node with the same graph and parameters
    worst = 0.0
    for e in (0, 0.5, 1, 2, 3):
        x = pad_data(P, gs[e], mech, 1.0)
        for j in range(K):
            isp = gs[e][:, j].astype(bool)
            pa = np.where(isp)[0]
            zj = P['noise_scale'][j] * P['Z'][:, j]
            if mech == 'rff':
                ref = RFFAdditive._rff_mechanism(x=x, z=zj, is_parent=isp, bias=np.array([P['bias'][j]]),
                                                 omega=omega(P, j, pa), b=P['b'][j], w=P['w'][j], c=P['c'][j], n_rff=N_RFF)
            else:
                ref = (x @ (P['W'][:, j] * isp)) + np.array([P['bias'][j]]) + zj
            worst = max(worst, float(np.abs(x[:, j] - ref).max() / max(1.0, np.abs(ref).max())))
    g['G6_maxrel'].append(worst)
    for cond in PADDED:
        X, tt, pad = assemble2(sid, ci, seed, cond)
        tables[(sid, cond)] = (X, dT, t['g'], mech, ci)
        g['G1'].append(np.ascontiguousarray(X[:, :dT]).tobytes() == x0.tobytes())
        alone = padding2(ci, seed, cond)['P']
        g['G2'].append(np.ascontiguousarray(zscore(alone)).tobytes() == np.ascontiguousarray(X[:, dT:]).tobytes())
        e, s = cond_es(cond)
        g['G7'].append(bool(np.array_equal(pad['g'], gs[e])))
        rho = stats.spearmanr(pad['P'])[0]
        iu = np.triu_indices(K, 1)
        pad_stats.append(dict(sys=sid, cell=ci, mech=mech, cond=cond, n_edges=pad['n_edges'], n_isolated=pad['n_isolated'],
                              mean_abs_spearman=float(np.abs(rho[iu]).mean())))
        if cond == 'e0':
            g5.append(dict(sys=sid, mean_abs_spearman=float(np.abs(rho[iu]).mean()),
                           mean_abs_skew=float(np.abs(stats.skew(pad['P'], axis=0)).mean()),
                           mean_excess_kurt=float(stats.kurtosis(pad['P'], axis=0).mean())))
ref_rng = np.random.default_rng(BSEED)
A_ref = [float(np.abs(stats.spearmanr(zscore(ref_rng.standard_normal((N, K))))[0][np.triu_indices(K, 1)]).mean()) for _ in range(16)]
gates = dict(
    G1=dict(n=len(g['G1']), pass_=all(g['G1'])),
    G2=dict(n=len(g['G2']), pass_=all(g['G2'])),
    G3=dict(n=len(g['G3']), pass_=all(g['G3'])),
    G4=dict(s1_bitwise_all=all(g['G4_s1_bitwise']), s0_maxabs=max(g['G4_s0_maxabs']),
            pass_=all(g['G4_s1_bitwise']) and max(g['G4_s0_maxabs']) <= 1e-12),
    G5=dict(descriptive=g5, A_reference_mean_abs_spearman=dict(mean=float(np.mean(A_ref)), sd=float(np.std(A_ref)))),
    G6=dict(maxrel=max(g['G6_maxrel']), pass_=max(g['G6_maxrel']) <= 1e-9),
    G7=dict(n=len(g['G7']), pass_=all(g['G7'])))
print('generator gates:', json.dumps({k: v.get('pass_', 'descriptive') for k, v in gates.items()}), flush=True)

# ---------------- screening p-values (primary test per family + variants), timing ----------------
P_ = {}
timing = []
for (sid, cond), (X, dT, gT, mech, ci) in tables.items():
    tests = ['fisherz', 'hsic'] if mech == 'lin' else ['hsic', 'spearman']
    for test in tests:
        t0 = time.perf_counter()
        P_[(sid, cond, test)] = pvalues(X, test)
        timing.append(dict(sys=sid, cond=cond, test=test, D=X.shape[1], seconds=round(time.perf_counter() - t0, 3)))
print('p-values done', round(time.time() - t_start, 1), 's', flush=True)

# ---------------- G8: vectorized HSIC vs causal-learn KCI_UInd ----------------
from causallearn.utils.KCI.KCI import KCI_UInd
kci = KCI_UInd(kernelX='Gaussian', kernelY='Gaussian', approx=True, est_width='median')
maxdp, n_pairs, dis, near = 0.0, 0, 0, []
t0 = time.perf_counter()
for sid, ci, seed in SYS:
    dT, eT, mech = CELLS[ci]
    if mech != 'rff':
        continue
    for cond in ('e0', rep_cond(ci), 'e3'):
        X = np.asarray(tables[(sid, cond)][0], np.float64)
        pv = P_[(sid, cond, 'hsic')]
        D = X.shape[1]
        m = D * (D - 1) // 2
        for a in range(D):
            for b in range(a + 1, D):
                pk, _ = kci.compute_pvalue(X[:, [a]], X[:, [b]])
                n_pairs += 1
                maxdp = max(maxdp, abs(pk - pv[a, b]))
                for al in GRID:
                    thr = al / m
                    if (pk < thr) != (pv[a, b] < thr):
                        if abs(pk - thr) <= 1e-9 * thr and abs(pv[a, b] - thr) <= 1e-9 * thr:
                            near.append(dict(sys=sid, cond=cond, pair=[a, b], alpha=al, p_kci=pk, p_vec=float(pv[a, b])))
                        else:
                            dis += 1
gates['G8'] = dict(n_pairs=n_pairs, max_abs_dp=maxdp, decision_disagreements=dis, near_threshold_cases=near,
                   seconds=round(time.perf_counter() - t0, 1), pass_=bool(maxdp <= 1e-6 and dis == 0))
print('G8:', {k: gates['G8'][k] for k in ('n_pairs', 'max_abs_dp', 'decision_disagreements', 'pass_')}, flush=True)

# ---------------- G9: diagnostic calibration on target x padding pairs ----------------
g9 = {}
for test, fam in (('fisherz', 'lin'), ('hsic', 'rff')):
    S = [(sid, ci) for sid, ci, _ in SYS if CELLS[ci][2] == fam]
    rate = {}
    for kind, conds in (('e0', ['e0']), ('structured', [c for c in PADDED if c != 'e0'])):
        cross = np.concatenate([P_[(sid, c, test)][:CELLS[ci][0], CELLS[ci][0]:].ravel() for sid, ci in S for c in conds])
        rate[kind] = {str(lv): float((cross < lv).mean()) for lv in (0.05, 0.01, 0.001)}
        rate[kind]['n_pairs'] = int(len(cross))
    fw = {}
    for al in GRID:
        ind0, per_sys = [], []
        for sid, ci in S:
            dT = CELLS[ci][0]
            def anyfalse(c):
                p = P_[(sid, c, test)]
                m = p.shape[0] * (p.shape[0] - 1) // 2
                return int((p[:dT, dT:] < al / m).any())
            ind0.append(anyfalse('e0'))
            per_sys.append(np.array([anyfalse(c) for c in PADDED if c != 'e0']))
        ci0, up0 = clopper_pearson(sum(ind0), len(ind0))
        est_s, ci_s = cluster_boot(per_sys)
        fw[str(al)] = dict(e0=dict(systems_with_false_cross=sum(ind0), n_systems=len(ind0), ci95=ci0, upper95_one_sided=up0),
                           structured=dict(rate=est_s, ci95_cluster_boot=ci_s, n_inputs=int(sum(len(v) for v in per_sys))))
    g9[test] = dict(family=fam, pairwise_rejection_rate=rate, any_false_cross_per_input=fw,
                    stop=bool(rate['e0']['0.05'] > 0.10 or rate['structured']['0.05'] > 0.10))
gates['G9'] = dict(note='diagnostic only; nominal alpha; not evidence of FWER control (rules v1 §8.1, §9)', **g9)
print('G9 stop flags:', {t: g9[t]['stop'] for t in g9}, flush=True)

# ---------------- alpha selection by J (rules v1 §8.4) ----------------
def j_of(sid, ci, cond, test, al, method='bonferroni'):
    X, dT, gT, mech, _ = tables[(sid, cond)]
    p = P_[(sid, cond, test)]
    R = reject_bonferroni(p, al) if method == 'bonferroni' else reject_bh(p, al)
    sm = screen_metrics(components(R), R, dT, gT)
    jv = (sm['merged'] / sm['k'] if sm['k'] else 0.0) + sm['split'] / sm['n_true_edges']
    return jv, sm


def J_table(test, fam, method='bonferroni', alphas=GRID):
    out = {}
    cells = sorted({ci for _, ci, _ in SYS if CELLS[ci][2] == fam})
    for al in alphas:
        per = []
        for ci in cells:
            for cond in PADDED:
                per.append(np.mean([j_of(sid, c2, cond, test, al, method)[0] for sid, c2, _ in SYS if c2 == ci]))
        k0 = [j_of(sid, c2, 'k0', test, al, method)[1] for sid, c2, _ in SYS if c2 in cells]
        out[str(al)] = dict(J=float(np.mean(per)), k0_split_rate=float(np.mean([d['split'] / d['n_true_edges'] for d in k0])),
                            k0_mean_target_components=float(np.mean([d['n_target_components'] for d in k0])))
    return out


def choose(table):
    J = {float(a): round(v['J'], 3) for a, v in table.items()}
    best = min(J.values())
    tied = sorted(a for a, v in J.items() if v == best)
    return 0.05 if 0.05 in tied else tied[0], tied


Jfz, Jhs = J_table('fisherz', 'lin'), J_table('hsic', 'rff')
a_fz, tie_fz = choose(Jfz)
a_hs, tie_hs = choose(Jhs)
alpha = dict(fisherz=a_fz, hsic=a_hs, J=dict(fisherz=Jfz, hsic=Jhs), tied=dict(fisherz=tie_fz, hsic=tie_hs),
             rule='min J over grid {0.01, 0.05, 0.10}; ties at 3 decimals -> 0.05 if tied else smallest (rules v1 §8.4)')
info = dict(hsic_on_linear_at_alpha_hsic=J_table('hsic', 'lin', alphas=(a_hs,)),
            spearman_on_rff_at_alpha_hsic=J_table('spearman', 'rff', alphas=(a_hs,)),
            bh_fisherz=J_table('fisherz', 'lin', 'bh', alphas=(a_fz,)), bh_hsic=J_table('hsic', 'rff', 'bh', alphas=(a_hs,)))
res = dict(rules='P-N2 v1 (commit 5c2c76c)', set='DEV2', n_systems=len(SYS), gates=gates, alpha=alpha,
           variants_info_only=info, pad_stats=pad_stats, screening_timing=timing, wall_seconds=round(time.time() - t_start, 1))
(OUT2 / 'dev2_data_gates.json').write_text(json.dumps(res, indent=1, default=float))
(OUT2 / 'alpha.json').write_text(json.dumps(dict(fisherz=a_fz, hsic=a_hs, source='dev2_data_gates.json'), indent=1))
print('alpha:', {'fisherz': a_fz, 'hsic': a_hs}, 'J fisherz', {a: round(v['J'], 4) for a, v in Jfz.items()},
      'J hsic', {a: round(v['J'], 4) for a, v in Jhs.items()}, flush=True)
print('done', round(time.time() - t_start, 1), 's')
