"""P-N6 post-hoc descriptive extras (POST-HOC; not in the locked rules; no test; does not change any locked label).

Reads the saved outputs only; runs no model. Uses the skeleton rules of PN6 v1 §3 (same as recheck_pn6.py), the frozen
P-N1 generator only for the true target graphs, and the cached HSIC p-values for the screening partitions.

  1. R-L cost at k0, split by pair type: pairs that the k0 partition puts in different components (forced non-edges)
     versus pairs inside one component (the model runs on the component).
  2. Merge sizes by cell (R-L and R-H; A20 and S20).
  3. Falsely rejected cross pairs: observed total versus the nominal expectation if the p-values were valid
     (R-L: alpha_L * d_T * k per system; R-H: alpha_H / (D(D - 1)/2) * d_T * k).
  4. Worst |dm| per R arm: where it comes from (k0 part versus the padded input; mixing).
  5. Real tables: the R-L and R-H partition at k0, and the parts of phi(k0); sigma > 0 draws versus mixing.
  6. CDFM, R-L at k0, pairs inside a component: anchor-dependent accounting with the plain k0 threshold tau0 as the
     anchor. "score part" = the R-L component probabilities read at tau0, against plain k0; "threshold part" = the
     R-L per-component NATIVE reading against that tau0 reading. An accounting split, not two separate causes.

usage: python -I posthoc_pn6.py <artifacts dir> <output json>
"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.sparse.csgraph import connected_components

ART = Path(sys.argv[1]).resolve()
OUT6, OUT5 = ART / 'n6_runs' / 'pn6_out', ART / 'n5_runs' / 'pn5_out'
sys.path.insert(0, str(ART / 'n1_runs' / 'pn1'))
from common import CELLS, target          # frozen P-N1: true target graphs only

BASE, REPS, K = 480000, 15, 20
AL = json.loads((OUT6 / 'alpha6.json').read_text())
ALPHA = dict(RL=float(AL['alpha_L']), RH=float(AL['alpha_H']))


def thr_or(P, tau):
    A = np.asarray(P, float) > tau
    np.fill_diagonal(A, False)
    return A | A.T


def adj_or(A):
    A = np.array(A) != 0
    np.fill_diagonal(A, False)
    return A | A.T


def iu(d):
    return np.triu_indices(d, 1)


def load(model, key):
    z = np.load(OUT6 / model / f'{key}.npz', allow_pickle=False)
    d = {n: z[n] for n in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


def r_skel(model, o):
    return thr_or(o['probs_T'], 0.5) if model == 'avici' else adj_or(o['adj_T'])


def plain_skel(model, o, dT):
    return thr_or(o['probs'][:dT, :dT], 0.5) if model == 'avici' else adj_or(o['adj_native'][:dT, :dT])


def partition(key, arm):
    p = np.load(OUT6 / 'pvals' / f'{key}.npz', allow_pickle=False)['p']
    D = p.shape[0]
    a = ALPHA[arm] if arm == 'RL' else ALPHA[arm] / (D * (D - 1) / 2)
    R = np.asarray(p, float) < a
    np.fill_diagonal(R, False)
    R = R | R.T
    return R, connected_components(R.astype(np.int8), directed=False)[1]


def mean(x):
    return float(np.mean(x)) if len(x) else None


res = dict(note='POST-HOC descriptive; not in the locked rules; no test', alpha=ALPHA)

# ---------------------------------------------------------------- 1, 2, 3, 4 on the synthetic systems
parts = defaultdict(lambda: defaultdict(list))
thr_split = defaultdict(list)
merges = defaultdict(list)
cross = defaultdict(lambda: dict(observed=0, nominal=0.0, systems=0, systems_with_any=0))
worst = {}
for ci in range(8):
    dT, eT, fam = CELLS[ci]
    conds = {'k0': 'k0', 'A20': 'e0', 'S20': f'e{eT}'}
    for r in range(REPS):
        sid = f'PN6-c{ci}-r{r}'
        g = target(sid, ci, BASE + 1000 * ci + r)['g']
        true = ((g + g.T) > 0)[iu(dT)]
        scr = {}
        for arm in ('RL', 'RH'):
            for c, n in conds.items():
                R, lab = partition(f'{sid}__{n}', arm)
                D = len(lab)
                tl = set(lab[:dT].tolist())
                merged = sum(1 for v in range(dT, D) if lab[v] in tl)
                scr[(arm, c)] = dict(lab=lab, merged=merged)
                if c != 'k0':
                    merges[(arm, c, f'c{ci} (d_T={dT}, e_T={eT}, {fam})')].append(merged)
                    fc = int(R[:dT, dT:].sum())
                    per_pair = ALPHA['RL'] if arm == 'RL' else ALPHA['RH'] / (D * (D - 1) / 2)
                    x = cross[(arm, fam, c)]
                    x['observed'] += fc
                    x['nominal'] += per_pair * dT * (D - dT)
                    x['systems'] += 1
                    x['systems_with_any'] += int(fc > 0)
        lab0 = scr[('RL', 'k0')]['lab']
        i, j = iu(dT)
        is_cross = lab0[i] != lab0[j]
        for model in ('avici', 'cdfm'):
            p0 = plain_skel(model, load(model, f'{sid}__k0__plain'), dT)[iu(dT)]
            for arm in ('RL', 'RH'):
                S = {c: r_skel(model, load(model, f'{sid}__{n}__{arm}')) for c, n in conds.items()}
                dm0 = int(S['k0'][iu(dT)].sum()) - int(p0.sum())
                for c in ('A20', 'S20'):
                    dm = int(S[c][iu(dT)].sum()) - int(p0.sum())
                    key = (model, fam, arm)
                    if key not in worst or abs(dm) > abs(worst[key]['dm']):
                        worst[key] = dict(system=sid, cell=list(CELLS[ci]), input=c, dm=dm, dm_k0_part=dm0,
                                          sigma=int((S[c][iu(dT)] != S['k0'][iu(dT)]).sum()),
                                          merged=scr[(arm, c)]['merged'])
            s0 = r_skel(model, load(model, f'{sid}__k0__RL'))[iu(dT)]
            pp = parts[(model, fam)]
            pp['phi_k0'].append(int((s0 != p0).sum()))
            pp['phi_k0_cross'].append(int((s0 != p0)[is_cross].sum()))
            pp['phi_k0_within'].append(int((s0 != p0)[~is_cross].sum()))
            pp['split_true_edges'].append(int((true & is_cross).sum()))
            pp['dTP_cross'].append(-int((p0 & true)[is_cross].sum()))
            pp['dFP_cross'].append(-int((p0 & ~true)[is_cross].sum()))
            pp['dTP_within'].append(int((s0 & true)[~is_cross].sum()) - int((p0 & true)[~is_cross].sum()))
            pp['dFP_within'].append(int((s0 & ~true)[~is_cross].sum()) - int((p0 & ~true)[~is_cross].sum()))
            pp['n_target_components_k0'].append(len(set(lab0[:dT].tolist())))
            if model == 'cdfm':
                o0 = load(model, f'{sid}__k0__RL')
                tau0 = float(load(model, f'{sid}__k0__plain')['threshold'])
                sc_ = thr_or(o0['probs_T'], tau0)[iu(dT)]
                w = ~is_cross
                pp['within_edges_plain'].append(int(p0[w].sum()))
                pp['within_edges_RL_native'].append(int(s0[w].sum()))
                pp['within_edges_RL_at_tau0'].append(int(sc_[w].sum()))
                pp['within_flips_score_part'].append(int((sc_ != p0)[w].sum()))
                pp['within_flips_threshold_part'].append(int((s0 != sc_)[w].sum()))
                pp['within_dFP_score_part'].append(int((sc_ & ~true)[w].sum()) - int((p0 & ~true)[w].sum()))
                pp['within_dFP_threshold_part'].append(int((s0 & ~true)[w].sum()) - int((sc_ & ~true)[w].sum()))
                thr = [float(x) for x in o0['thr_components']]
                pp['mean_component_threshold_minus_tau0'].append(float(np.mean(thr)) - tau0 if thr else 0.0)
                pp['systems_with_split_target'].append(int(len(set(lab0[:dT].tolist())) > 1))
                if len(set(lab0[:dT].tolist())) > 1 and thr:
                    thr_split[(model, fam)].append(float(np.mean(thr)) - tau0)

res['1_RL_k0_parts'] = {f'{m}|{f}': {k: mean(v) for k, v in d.items()} for (m, f), d in sorted(parts.items())}
res['6_cdfm_split_systems_threshold'] = {
    f'{m}|{f}': dict(n_split_systems_with_a_model_call=len(v), mean_component_threshold_minus_tau0=mean(v),
                     share_below_tau0=float(np.mean([x < 0 for x in v])) if v else None,
                     min=float(min(v)) if v else None, max=float(max(v)) if v else None)
    for (m, f), v in sorted(thr_split.items())}
res['2_merge_sizes'] = {f'{a}|{c}|{cell}': dict(n=len(v), with_merge=sum(1 for x in v if x > 0),
                                                 sizes=sorted(x for x in v if x > 0))
                        for (a, c, cell), v in sorted(merges.items())}
res['3_false_cross'] = {f'{a}|{f}|{c}': dict(observed_total=x['observed'], nominal_expected_total=round(x['nominal'], 3),
                                              ratio=round(x['observed'] / x['nominal'], 2), systems=x['systems'],
                                              systems_with_any=x['systems_with_any'])
                        for (a, f, c), x in sorted(cross.items())}
res['4_worst_abs_dm'] = {f'{m}|{f}|{a}': w for (m, f, a), w in sorted(worst.items())}

# ---------------------------------------------------------------- 5 real tables
real = {}
for t in ('sachs', 'wine'):
    for arm in ('RL', 'RH'):
        _, lab0 = partition(f'{t}__k0', arm)
        comps = [sorted(np.where(lab0 == L)[0].tolist()) for L in sorted(set(lab0.tolist()))]
        i, j = iu(11)
        is_cross = lab0[i] != lab0[j]
        for model in ('avici', 'cdfm'):
            z = np.load(OUT5 / model / f'{t}__k0.npz', allow_pickle=False)
            p0 = plain_skel(model, {n: z[n] for n in z.files}, 11)[iu(11)]
            s0 = r_skel(model, load(model, f'{t}__k0__{arm}'))[iu(11)]
            d = dict(components_k0=comps, m_plain_k0=int(p0.sum()), m_fix_k0=int(s0.sum()),
                     phi_k0=int((s0 != p0).sum()), plain_edges_on_cross_pairs=int(p0[is_cross].sum()),
                     phi_k0_within=int((s0 != p0)[~is_cross].sum()))
            for c in ('k20_e0', 'k40_e0'):
                rows = []
                for r in range(20):
                    _, lab = partition(f'{t}__{c}__r{r:02d}', arm)
                    tl = set(lab[:11].tolist())
                    merged = sum(1 for v in range(11, len(lab)) if lab[v] in tl)
                    s = r_skel(model, load(model, f'{t}__{c}__r{r:02d}__{arm}'))[iu(11)]
                    rows.append((int((s != s0).sum()), merged))
                d[c] = dict(sigma_pos_draws=sum(1 for s, _ in rows if s > 0),
                            sigma_pos_and_mixed=sum(1 for s, m in rows if s > 0 and m > 0),
                            mixed_draws=sum(1 for _, m in rows if m > 0),
                            sigma_values=sorted(s for s, _ in rows if s > 0))
            real[f'{model}|{t}|{arm}'] = d
res['5_real_tables'] = real

Path(sys.argv[2]).write_text(json.dumps(res, indent=1))
for k, v in res.items():
    print('==', k)
    if isinstance(v, dict):
        for kk, vv in v.items():
            print('  ', kk, json.dumps(vv))
    else:
        print('  ', v)
