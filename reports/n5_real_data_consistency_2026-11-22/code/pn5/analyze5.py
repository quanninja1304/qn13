"""P-N5 reading (rules PN5 v1 §5, §6, §9). Refuses to read PN5 unless completeness5.py wrote ok = true.

Locked part (§5): P5-1 (draw-wise flips_M - max(flips_PC, flips_GES) at k20_e0, AVICI and CDFM, per table) and
P5-2 (CDFM tau(structured) - tau(Gaussian) in the same draw, k = 20 and k = 40, per table); one-sided paired t over the
draws; DEGENERATE if all values are equal; Holm 0.05 over the eight p-values. Everything else is descriptive (§6).
Timeouts (PC, GES, descriptive inputs only) are excluded and counted, never imputed.
usage: analyze5.py [--set PN5|DEV5] [--smoke]
  --smoke (gate G4): run the whole reading path, then print and write only the structure (keys and counts), no value.
Output: pn5_out/pn5_reading.json (PN5) or pn5_out/<set>_reading_structure.json (smoke)
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common5 import OUT5, SETS5, KS, ES, ALGS, MODELS, LETTER, alg_conds, key5, real_block
from measures5 import measures, pair_names
from stats5 import paired_t, holm, size_label, describe, p51_contrast

ap = argparse.ArgumentParser()
ap.add_argument('--set', default='PN5', choices=['PN5', 'DEV5']); ap.add_argument('--smoke', action='store_true')
a = ap.parse_args()
SET = a.set
if SET == 'DEV5' and not a.smoke:
    sys.exit('DEV5 is read only in smoke mode (gate G4)')
if SET == 'PN5' and not a.smoke:
    cp = OUT5 / 'pn5_completeness.json'
    if not cp.exists() or not json.loads(cp.read_text())['ok']:
        sys.exit('REFUSED: completeness check missing or not ok (rules PN5 §7)')
S = SETS5[SET]
D = S['draws']
MARGIN = dict(flips=1.0, thr=0.03)


def status_map(alg):
    st = {}
    for l in (OUT5 / alg / f'log_{SET}.jsonl').read_text(encoding='utf-8').splitlines():
        if l.strip():
            r = json.loads(l)
            st[r['key']] = r['status']
    return st


def load(alg, key):
    z = np.load(OUT5 / alg / f'{key}.npz', allow_pickle=False)
    return {q: z[q] for q in z.files if q != 'meta'}


# ---------------- measures per (algorithm, table, condition, draw); None = timeout ----------------
M, CTX = {}, {}
for alg in ALGS:
    st = status_map(alg)
    M[alg] = {}
    for t in S['tables']:
        o0 = load(alg, key5(t, 'k0'))
        base = measures(alg, o0, o0)
        CTX.setdefault(t, {})[alg] = dict(m0=base['m'], **({'thr0': base['thr'], 'm0_fixed': base['m_fixed']} if alg == 'cdfm' else {}))
        M[alg][t] = {}
        for cond in alg_conds(alg):
            if cond == 'k0':
                continue
            vals = []
            for r in range(D):
                k_ = key5(t, cond, r)
                if st.get(k_) == 'timeout':
                    vals.append(None)
                elif st.get(k_) == 'ok':
                    vals.append(measures(alg, load(alg, k_), o0))
                else:
                    sys.exit(f'MISSING {alg} {k_}: reading refused')
            M[alg][t][cond] = vals


def series(alg, t, cond, q):
    if cond not in M[alg][t]:
        return None
    return [None if v is None else v[q] for v in M[alg][t][cond]]


def signs(c):
    done = [x for x in c if x is not None]
    return dict(n_above=sum(1 for x in done if x > 0), n_at=sum(1 for x in done if x == 0),
                n_below=sum(1 for x in done if x < 0), n_distinct=len(set(done)))


# ---------------- locked hypotheses (rules §5) ----------------
H = {}
for t in S['tables']:
    L = LETTER[t]
    fPC, fGES = series('pc', t, 'k20_e0', 'flips'), series('ges', t, 'k20_e0', 'flips')
    for alg, A in (('avici', 'A'), ('cdfm', 'C')):
        fM = series(alg, t, 'k20_e0', 'flips')
        c = p51_contrast(fM, [fPC, fGES])
        if any(x is None for x in c):
            sys.exit(f'a main-input value is missing for P5-1{L}-{A}: reading refused')
        h = paired_t(c, +1, 0.0)
        h.update(estimand='E_r[flips_M,r - max(flips_PC,r, flips_GES,r)] at k20_e0, conditional on the fixed table',
                 table=t, alg=alg, values=c,
                 components=dict(flips_model=describe(fM), flips_pc=describe(fPC), flips_ges=describe(fGES),
                                 max_pc_ges=describe([max(x, y) for x, y in zip(fPC, fGES)])))
        h['sign'], h['size'] = size_label(h['ci95'], MARGIN['flips'])
        H[f'P5-1{L}-{A}'] = h
    for k in KS:
        t2, t0 = series('cdfm', t, f'k{k}_e2', 'thr'), series('cdfm', t, f'k{k}_e0', 'thr')
        c = [x - y for x, y in zip(t2, t0)]
        h = paired_t(c, +1, 0.0)
        h.update(estimand=f'E_r[tau_r(k{k}, structured) - tau_r(k{k}, Gaussian)], CDFM, conditional on the fixed table',
                 table=t, alg='cdfm', k=k, values=c, tau_structured=describe(t2), tau_gaussian=describe(t0))
        h['sign'], h['size'] = size_label(h['ci95'], MARGIN['thr'])
        H[f'P5-2{L}-{k}'] = h
lab = holm({h: v['p_one_sided'] for h, v in H.items()})
for h in H:
    H[h].update(lab[h])

# ---------------- descriptive (rules §6) ----------------
DESC = {}
for alg in ALGS:
    qs = ['flips', 'dm', 'absdm'] + (['dp'] if alg in MODELS else []) + \
         (['thr', 'dthr', 'flips_fixed', 'flips_frozen', 'm_fixed', 'm_frozen'] if alg == 'cdfm' else [])
    for t in S['tables']:
        for cond, vals in M[alg][t].items():
            DESC.setdefault(alg, {}).setdefault(t, {})[cond] = {q: describe(series(alg, t, cond, q)) for q in qs}

P51_OTHER = {}
for t in S['tables']:
    for cond in ('k20_e2', 'k40_e0', 'k40_e2'):
        ctrl = ['pc', 'ges'] if cond in alg_conds('ges') else ['pc']
        for alg in MODELS:
            c = p51_contrast(series(alg, t, cond, 'flips'), [series(q, t, cond, 'flips') for q in ctrl])
            P51_OTHER.setdefault(t, {}).setdefault(cond, {})[alg] = dict(controls=ctrl, contrast=describe(c), **signs(c))

PAIRS = {}
for t in S['tables']:
    pn = pair_names(real_block(t)['names'])
    for alg in ALGS:
        for cond, vals in M[alg][t].items():
            ch = [v['changed'] for v in vals if v is not None]
            fr = np.mean(np.asarray(ch, float), axis=0) if ch else np.zeros(len(pn))
            PAIRS.setdefault(t, {}).setdefault(alg, {})[cond] = dict(
                n_draws=len(ch), n_pairs_ever_changed=int((fr > 0).sum()),
                pairs_freq_ge_0_5=[dict(pair=pn[i], freq=float(fr[i])) for i in np.argsort(-fr, kind='stable') if fr[i] >= 0.5])


def paired_diff(alg, t, c1, c0, q):
    s1, s0 = series(alg, t, c1, q), series(alg, t, c0, q)
    if s1 is None or s0 is None:
        return None                                          # condition not run (GES at k40_e2)
    return describe([None if (x is None or y is None) else x - y for x, y in zip(s1, s0)])


DIFFS = {}
for alg in ALGS:
    qs = ['flips', 'absdm'] + (['dp'] if alg in MODELS else []) + (['thr'] if alg == 'cdfm' else [])
    for t in S['tables']:
        d_ = {}
        for k in KS:
            d_[f'structured_minus_gaussian_k{k}'] = {q: paired_diff(alg, t, f'k{k}_e2', f'k{k}_e0', q) for q in qs}
        for e in ES:
            d_[f'k40_minus_k20_e{e}'] = {q: paired_diff(alg, t, f'k40_e{e}', f'k20_e{e}', q) for q in qs}
        DIFFS.setdefault(alg, {})[t] = d_

TIMEOUTS = {alg: {t: {cond: sum(1 for v in vals if v is None) for cond, vals in M[alg][t].items()} for t in S['tables']}
            for alg in ALGS}
for t in S['tables']:
    rb = real_block(t)
    CTX[t]['table'] = dict(n_total_rows=rb['n_total'], n_selected=int(rb['XR'].shape[0]), idx_sha=rb['idx_sha'],
                           XR_sha=rb['XR_sha'], n_excess_duplicates_in_selection=rb['n_excess_duplicates'],
                           n_distinct_rows_in_selection=int(rb['XR'].shape[0]) - rb['n_excess_duplicates'],
                           variables=rb['names'])

res = dict(set=SET, rules='PN5 v1 (99197d8)', n_draws=D, hypotheses=H, holm_fwer=0.05, descriptive=DESC,
           p51_style_other_conditions=P51_OTHER, pair_change_frequency=PAIRS, paired_differences=DIFFS,
           timeouts=TIMEOUTS, context=CTX)


def structure(x, depth=0):
    """Keys and counts only, no value (smoke mode)."""
    if isinstance(x, dict):
        return {k: structure(v, depth + 1) for k, v in x.items()} if depth < 3 else f'dict[{len(x)}]'
    if isinstance(x, list):
        return f'list[{len(x)}]'
    return type(x).__name__


if a.smoke:
    out = dict(set=SET, smoke=True, hypothesis_ids=sorted(H), n_hypotheses=len(H),
               hypothesis_fields=sorted(next(iter(H.values())).keys()), structure=structure(
                   {k: v for k, v in res.items() if k not in ('hypotheses',)}))
    (OUT5 / f'{SET.lower()}_reading_structure.json').write_text(json.dumps(out, indent=1))
    print('SMOKE OK', SET, 'hypotheses:', len(H), 'sections:', sorted(k for k in res if k not in ('set', 'rules')))
    sys.exit(0)

(OUT5 / 'pn5_reading.json').write_text(json.dumps(res, indent=1, default=float))
for h, v in H.items():
    print(f"{h}: mean {v['mean']:+.4f} CI [{v['ci95'][0]:+.4f}, {v['ci95'][1]:+.4f}] t={v['t']} p={v['p_one_sided']:.3g} "
          f"Holm#{v['holm_rank']} -> {v['label']} | above/at/below {v['n_above']}/{v['n_at']}/{v['n_below']}")
