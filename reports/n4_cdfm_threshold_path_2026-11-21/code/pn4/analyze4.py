"""P-N4 reading (rules PN4 v1 §3-§5, §9). Written before any P-N4 output exists.

usage: analyze4.py [--set PN4|DEV4] [--smoke]
  PN4  : the locked reading; refuses unless pn4_out/pn4_completeness.json reports ok (rules §7).
  DEV4 : only with --smoke, to exercise the code path; prints structure, never contrast values (rules §8).
Output: pn4_out/<set>_pn4_reading.json
"""
import sys, json, argparse
import numpy as np
from common4 import *
from stats4 import strat4, composite, holm, size_label
from measures4 import locked_contrasts, descriptive, block_means, f1_skeleton, count_upper, sym
from selector4 import thr as thr_copy

ap = argparse.ArgumentParser(); ap.add_argument('--set', default='PN4', choices=['PN4', 'DEV4'])
ap.add_argument('--smoke', action='store_true'); a = ap.parse_args()
if a.set == 'DEV4' and not a.smoke:
    sys.exit('DEV4 is read only with --smoke (rules PN4 §8)')
if a.set == 'PN4':
    cp = OUT4 / 'pn4_completeness.json'
    if not cp.exists() or not json.loads(cp.read_text()).get('ok'):
        sys.exit('completeness check missing or failed: reading refused (rules PN4 §7)')

LOCKED = ('D1', 'D2', 'D3a', 'D3b', 'S', 'T', 'TpS', 'TmS')
HYP = {'a': [('D1', -1, 0.0)], 'b': [('D2', +1, 0.0)], 'x': [('D3a', +1, 0.0), ('D3b', -1, 0.0)],
       'c': [('T', -1, -1.5), ('TpS', -1, 0.0), ('TmS', -1, 0.0)]}        # rules §3
MARGIN = dict(D1=0.03, D2=0.03, D3a=0.03, D3b=1.5, S=1.5, T=1.5, TpS=1.5, TmS=1.5)   # rules §5


def npz(key):
    f = OUT4 / 'cdfm' / f'{key}.npz'
    if not f.exists():
        sys.exit(f'MISSING {key}: reading refused')
    z = np.load(f, allow_pickle=False)
    d = {q: z[q] for q in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


def checked(sid, ci, seed, cond):
    o = npz(key4(sid, cond))
    X, t, pad = assemble4(sid, ci, seed, cond)
    if o['meta']['input_sha'] != sha(X):
        sys.exit(f'INPUT SHA MISMATCH {sid} {cond}: reading refused')
    return o, t, pad


rows = []
for sid, ci, seed in systems4(a.set):
    dT, eT = CELLS[ci][0], eT_of(ci)
    ok0, t, _ = checked(sid, ci, seed, 'k0')
    g = t['g']
    rec = dict(sys=sid, ci=ci, dT=dT, f1_k0=f1_skeleton(ok0['adj_native'], g))
    for k in KS:
        o0, _, _ = checked(sid, ci, seed, f'k{k}_e0')
        o1, _, pad1 = checked(sid, ci, seed, f'k{k}_e{eT}')
        P0, P1 = np.asarray(o0['probs'], float), np.asarray(o1['probs'], float)
        t0, t1 = float(o0['threshold']), float(o1['threshold'])
        m = locked_contrasts(P0, P1, t0, t1, dT)
        m['desc'] = descriptive(P0, P1, t0, t1, dT)
        m['bm_e0'], m['bm_eT'] = block_means(P0, dT, pad1['g']), block_means(P1, dT, pad1['g'])
        m['f1_e0'] = f1_skeleton(o0['adj_native'][:dT, :dT], g)
        m['f1_eT'] = f1_skeleton(o1['adj_native'][:dT, :dT], g)
        m['H_e0'] = rec['f1_k0'] - m['f1_e0']
        m['native_count_consistent'] = bool(count_upper(sym(o0['adj_native'][:dT, :dT])) == m['m_e0'] and
                                            count_upper(sym(o1['adj_native'][:dT, :dT])) == m['m_eT'])
        m['selector_reproduction_abs'] = float(max(abs(thr_copy(P0) - t0), abs(thr_copy(P1) - t1)))
        m['pad_edges_eT'], m['pad_isolated_eT'] = int(pad1['n_edges']), int(pad1['n_isolated'])
        rec[f'k{k}'] = m
    rows.append(rec)
cells = [r['ci'] for r in rows]


def desc_stat(vals, q=None):
    st = strat4(vals, cells, 1, 0.0, boot=True)
    if q in MARGIN:
        st['sign'], st['size'] = size_label(st['ci95'], MARGIN[q])
    st['by_dT'] = {str(dd): float(np.mean([mu for mu, c in zip(st['cell_means'], st['cells']) if CELLS[c][0] == dd]))
                   for dd in (10, 20)}
    return st


res = dict(set=a.set, rules='P-N4 v1 (commit 05b6945)', n_systems=len(rows), hypotheses={})
# ---- confirmatory: 8 hypotheses, composite p = max of components, Holm 0.05 over all 8 (rules §3-§4) ----
pv = {}
for k in KS:
    for h, comps in HYP.items():
        cs = []
        for q, d, b in comps:
            st = strat4([r[f'k{k}'][q] for r in rows], cells, d, b, boot=True)
            st['quantity'] = q
            st['sign'], st['size'] = size_label(st['ci95'], MARGIN[q])
            cs.append(st)
        hid = f'N4-{h}(k={k})'
        res['hypotheses'][hid] = dict(k=k, components=cs, p=composite(cs), any_degenerate=any(c['degenerate'] for c in cs),
                                      any_estimate_opposite_side=any(c['estimate_opposite_side'] for c in cs))
        pv[hid] = res['hypotheses'][hid]['p']
for hid, v in holm(pv).items():
    res['hypotheses'][hid].update(v)
res['reading'] = {}
for k in KS:
    lab = lambda h: res['hypotheses'][f'N4-{h}(k={k})']['label']
    res['reading'][f'k={k}'] = dict(cross_block_path_confirmed=all(lab(h) == 'CONFIRMED' for h in ('a', 'b', 'x')),
                                    threshold_part_dominates_mean_confirmed=lab('c') == 'CONFIRMED')
# ---- descriptive (rules §5) ----
desc = {}
for k in KS:
    K = f'k{k}'
    d = {q: desc_stat([r[K][q] for r in rows], q) for q in LOCKED}
    d['per_system'] = dict(frac_T_below_minus_abs_S=float(np.mean([r[K]['T'] < -abs(r[K]['S']) for r in rows])),
                           frac_D3b_negative=float(np.mean([r[K]['D3b'] < 0 for r in rows])),
                           frac_D2_positive=float(np.mean([r[K]['D2'] > 0 for r in rows])))
    dl = [r[K]['desc']['d_logit'] for r in rows]
    d['d_logit'] = desc_stat(dl)
    d['shapley'] = {gp: desc_stat([r[K]['desc']['phi'][gp] for r in rows]) for gp in ('T', 'P', 'X')}
    d['shapley_share_of_mean_d_logit'] = {gp: float(np.mean([r[K]['desc']['phi'][gp] for r in rows]) / np.mean(dl))
                                          for gp in ('T', 'P', 'X')}
    feats = list(rows[0][K]['desc']['phi_feat']['T'].keys())
    d['shapley_by_feature_mean'] = {gp: {f: float(np.mean([r[K]['desc']['phi_feat'][gp][f] for r in rows])) for f in feats}
                                    for gp in ('T', 'P', 'X')}
    d['effects'] = {e: desc_stat([r[K]['desc']['effects'][e] for r in rows]) for e in rows[0][K]['desc']['effects']}
    d['counts_mean'] = {key: {an: float(np.mean([r[K]['desc']['counts'][key][an] for r in rows]))
                              for an in ('on_e0_scores', 'on_eT_scores')} for key in rows[0][K]['desc']['counts']}
    d['padding_only_swap'] = dict(dthr=desc_stat([r[K]['desc']['P_only_dthr'] for r in rows]),
                                  dm_e0_scores=desc_stat([r[K]['desc']['P_only_dm_e0_scores'] for r in rows]))
    blocks = ('target', 'cross', 'padding', 'padding_edge_pairs', 'padding_nonedge_pairs', 'whole')
    d['block_means'] = {cnd: {b: float(np.mean([r[K][f'bm_{cnd}'][b] for r in rows if r[K][f'bm_{cnd}'][b] is not None]))
                              for b in blocks} for cnd in ('e0', 'eT')}
    d['block_mean_change'] = {b: desc_stat([r[K]['bm_eT'][b] - r[K]['bm_e0'][b] for r in rows]) for b in blocks
                              if all(r[K]['bm_eT'][b] is not None for r in rows)}
    d['alternative_anchor_eT'] = dict(S=desc_stat([r[K]['desc']['alt_S'] for r in rows]),
                                      T=desc_stat([r[K]['desc']['alt_T'] for r in rows]))
    d['quality'] = dict(f1_k0=float(np.mean([r['f1_k0'] for r in rows])), f1_e0=float(np.mean([r[K]['f1_e0'] for r in rows])),
                        f1_eT=float(np.mean([r[K]['f1_eT'] for r in rows])), H_e0=desc_stat([r[K]['H_e0'] for r in rows]))
    d['padding_graph_eT'] = dict(mean_edges=float(np.mean([r[K]['pad_edges_eT'] for r in rows])),
                                 mean_isolated=float(np.mean([r[K]['pad_isolated_eT'] for r in rows])))
    d['checks'] = dict(native_count_consistent_all=all(r[K]['native_count_consistent'] for r in rows),
                       selector_reproduction_max_abs=float(max(r[K]['selector_reproduction_abs'] for r in rows)))
    desc[K] = d
desc['k40_minus_k20'] = {q: desc_stat([r['k40'][q] - r['k20'][q] for r in rows]) for q in LOCKED}
res['descriptive'] = desc
res['rows'] = rows
blob = json.dumps(res, indent=1, default=float)
if a.smoke:   # code-path check only: nothing is written and no contrast value is printed (rules §8)
    print(json.dumps(dict(set=a.set, n_rows=len(rows), hypotheses=sorted(res['hypotheses']),
                          descriptive_keys=sorted(res['descriptive']['k20']), json_bytes=len(blob)), indent=1))
    sys.exit(0)
(OUT4 / f'{a.set.lower()}_pn4_reading.json').write_text(blob)
for hid, h in res['hypotheses'].items():
    comp = '; '.join(f"{c['quantity']} {c['theta']:+.4f} [{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}] p {c['p_one_sided']:.3g}"
                     + (' DEGENERATE' if c['degenerate'] else '') for c in h['components'])
    print(f"{hid}: p {h['p']:.3g} holm {h['holm_threshold']:.5f} -> {h['label']} | {comp}")
print(json.dumps(res['reading']))
