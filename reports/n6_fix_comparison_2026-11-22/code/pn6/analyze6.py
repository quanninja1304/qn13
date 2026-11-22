"""P-N6 reading (rules PN6 v1 §5-§6, §9).

usage: analyze6.py [--set PN6|DEV6] [--smoke]
PN6: refuses unless pn6_out/pn6_completeness.json has ok = true. DEV6: --smoke only (gate G7): runs the whole reading
path and writes the structure of the result (keys only); no value is printed or written.
"""
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
from common6 import (OUT6, OUT5, CELLS, MODELS, R_ARMS, REAL_TABLES, REAL_PADDED, REAL_DRAWS, MARGIN_F1, MARGIN_PAIRS,
                     MARGIN_EDGES, systems6, conds6, label, assemble6, key6)
from measures6 import load, system_measures, skel_R, flips
from metrics import skel_native
from stats6 import strat_t, ni_composite, holm, size_label, clopper_pearson, describe

ap = argparse.ArgumentParser()
ap.add_argument('--set', default='PN6', choices=['PN6', 'DEV6'])
ap.add_argument('--smoke', action='store_true')
a = ap.parse_args()
if a.set == 'PN6':
    c = OUT6 / 'pn6_completeness.json'
    if not (c.exists() and json.loads(c.read_text()).get('ok')):
        sys.exit('REFUSED: pn6_completeness.json missing or not ok (rules §7)')
elif not a.smoke:
    sys.exit('DEV6 is read with --smoke only (gate G7)')

FAMS = ('lin', 'rff')
rows = []                                     # one row per (system, model)
for sid, ci, seed in systems6(a.set):
    dT, eT, fam = CELLS[ci]
    for model in MODELS:
        outs, meta = {}, {}
        for cond in conds6(ci):
            it = dict(kind='syn', set=a.set, sid=sid, ci=ci, seed=seed, cond=cond)
            for arm in ('plain',) + R_ARMS:
                o = load(OUT6 / model / f'{key6(it, arm)}.npz')
                outs[(arm, label(cond))] = o
                if arm != 'plain':
                    meta[(arm, label(cond))] = o['meta']
        g = assemble6(dict(kind='syn', set=a.set, sid=sid, ci=ci, seed=seed, cond='k0'))[2]['g']
        ms = system_measures(model, outs, dT, g)
        scr = {f'{arm}|{c}': {q: meta[(arm, c)][q] for q in ('merged', 'split', 'false_cross', 'n_target_components', 'mixed')}
               for arm in R_ARMS for c in ('k0', 'A20', 'S20')}
        rows.append(dict(sys=sid, ci=ci, fam=fam, dT=dT, model=model, m=ms, screen=scr))


def cells(model, fam, f):
    return [np.array([f(r) for r in rows if r['model'] == model and r['ci'] == ci], float)
            for ci in range(8) if CELLS[ci][2] == fam]


# ---- hypotheses (rules §5)
H = {}
for model, L in (('avici', 'A'), ('cdfm', 'C')):
    for fam in FAMS:
        h = ni_composite(cells(model, fam, lambda r: r['m']['RL']['Q0']), cells(model, fam, lambda r: r['m']['RL']['Q_A20']), MARGIN_F1)
        for comp in ('Q0', 'QA20'):
            h[comp]['sign'], h[comp]['size'] = size_label(h[comp]['ci95'], MARGIN_F1)
        H[f'P6-1{L}-{fam}'] = dict(kind='non-inferiority', model=model, fam=fam, margin=MARGIN_F1, **h)
for fam in FAMS:
    s = strat_t(cells('cdfm', fam, lambda r: r['m']['FROZEN']['phi_S20'] - r['m']['RL']['phi_S20']), 0.0)
    s['sign'], s['size'] = size_label(s['ci95'], MARGIN_PAIRS)
    s['phi_frozen'] = strat_t(cells('cdfm', fam, lambda r: r['m']['FROZEN']['phi_S20']), 0.0)['estimate']
    s['phi_RL'] = strat_t(cells('cdfm', fam, lambda r: r['m']['RL']['phi_S20']), 0.0)['estimate']
    H[f'P6-2C-{fam}'] = dict(kind='one-sided', model='cdfm', fam=fam, **s)
hl = holm({h: v['p'] for h, v in H.items()})
for h, v in H.items():
    v['holm_rank'], v['holm_threshold'], rej = hl[h]
    v['label'] = 'CONFIRMED' if (rej and not v.get('degenerate')) else 'NOT_CONFIRMED'

# ---- descriptive (rules §6)
MEAS = ('Q0', 'Q_A20', 'Q_S20', 'G_A20', 'G_S20', 'phi_k0', 'phi_A20', 'phi_S20', 'sigma_A20', 'sigma_S20', 'dm_A20', 'dm_S20')
MARG = lambda q: MARGIN_F1 if q[0] in 'QG' else (MARGIN_EDGES if q.startswith('dm') else MARGIN_PAIRS)
desc = {}
for model in MODELS:
    fixes = ('plain', 'RL', 'RH') + (('FIXED', 'FROZEN', 'LOCAL') if model == 'cdfm' else ())
    for fam in FAMS:
        for fx in fixes:
            d = {}
            for q in MEAS:
                s = strat_t(cells(model, fam, lambda r, fx=fx, q=q: r['m'][fx][q]), 0.0)
                d[q] = dict(estimate=s['estimate'], ci95=s['ci95'], label=size_label(s['ci95'], MARG(q)))
            sel = [r for r in rows if r['model'] == model and r['fam'] == fam]
            for c in ('A20', 'S20'):
                k = sum(r['m'][fx][f'sigma_{c}'] > 0 for r in sel)
                d[f'share_sigma_pos_{c}'] = dict(k=int(k), n=len(sel), ci95=clopper_pearson(int(k), len(sel)))
            d['worst_abs_dm'] = int(max(max(abs(r['m'][fx]['dm_A20']), abs(r['m'][fx]['dm_S20'])) for r in sel))
            desc[f'{model}|{fam}|{fx}'] = d
screen = {}
for model in MODELS:
    for fam in FAMS:
        sel = [r for r in rows if r['model'] == model and r['fam'] == fam]
        for arm in R_ARMS:
            for c in ('k0', 'A20', 'S20'):
                v = [r['screen'][f'{arm}|{c}'] for r in sel]
                screen[f'{model}|{fam}|{arm}|{c}'] = dict(
                    merged_mean=float(np.mean([x['merged'] for x in v])), split_mean=float(np.mean([x['split'] for x in v])),
                    false_cross_mean=float(np.mean([x['false_cross'] for x in v])), n_mixed=int(sum(x['mixed'] for x in v)))
        for c in ('A20', 'S20'):   # R-L: sigma split by whether a target component contains padding
            mixed = [r for r in sel if r['screen'][f'RL|{c}']['mixed']]
            clean = [r for r in sel if not r['screen'][f'RL|{c}']['mixed']]
            screen[f'{model}|{fam}|RL|{c}|sigma_by_mixing'] = dict(
                mixed=dict(n=len(mixed), sigma_pos=int(sum(r['m']['RL'][f'sigma_{c}'] > 0 for r in mixed))),
                not_mixed=dict(n=len(clean), sigma_pos=int(sum(r['m']['RL'][f'sigma_{c}'] > 0 for r in clean))))

# ---- real tables (rules §6; descriptive): PN6 only
real = {}
if a.set == 'PN6':
    for model in MODELS:
        for t in REAL_TABLES:
            p0 = load(OUT5 / model / f'{t}__k0.npz')               # P-N5 plain k0 (already seen in P-N5)
            dT = 11
            s0 = skel_native(model, p0, dT)
            for arm in R_ARMS:
                rk0 = load(OUT6 / model / f'{t}__k0__{arm}.npz')
                sk0 = skel_R(model, rk0, dT)
                d = dict(phi_k0=flips(sk0, s0), k0_target_components=rk0['meta']['n_target_components'])
                for c in REAL_PADDED:
                    sig, phi, mer = [], [], []
                    for r in range(REAL_DRAWS):
                        o = load(OUT6 / model / f'{t}__{c}__r{r:02d}__{arm}.npz')
                        sk = skel_R(model, o, dT)
                        sig.append(flips(sk, sk0)); phi.append(flips(sk, s0)); mer.append(o['meta']['merged'])
                    kpos = int(sum(x > 0 for x in sig))
                    d[c] = dict(sigma=describe(sig), phi=describe(phi), merged=describe(mer),
                                share_sigma_pos=dict(k=kpos, n=REAL_DRAWS, ci95=clopper_pearson(kpos, REAL_DRAWS)))
                real[f'{model}|{t}|{arm}'] = d

res = dict(set=a.set, rules='PN6 v1 (678f55f)', hypotheses=H, descriptive=desc, screening=screen, real_tables=real,
           n_systems=len(rows) // len(MODELS))
if a.smoke:
    def struct(o):
        if isinstance(o, dict):
            return {k: struct(v) for k, v in o.items()}
        return type(o).__name__
    (OUT6 / f'{a.set.lower()}_reading_structure.json').write_text(json.dumps(struct(res), indent=1))
    print('SMOKE OK', len(H), 'hypotheses;', len(desc), 'descriptive groups;', len(real), 'real-table groups')
else:
    (OUT6 / 'pn6_reading.json').write_text(json.dumps(res, indent=1, default=float))
    for h, v in H.items():
        if v['kind'] == 'non-inferiority':
            print(f"{h}: Q0 {v['Q0']['estimate']:+.4f} CI {v['Q0']['ci95'][0]:+.4f},{v['Q0']['ci95'][1]:+.4f} p {v['Q0']['p']:.3g} | "
                  f"QA20 {v['QA20']['estimate']:+.4f} CI {v['QA20']['ci95'][0]:+.4f},{v['QA20']['ci95'][1]:+.4f} p {v['QA20']['p']:.3g} | "
                  f"p {v['p']:.3g} Holm#{v['holm_rank']} -> {v['label']}")
        else:
            print(f"{h}: diff {v['estimate']:+.3f} CI {v['ci95'][0]:+.3f},{v['ci95'][1]:+.3f} (FROZEN {v['phi_frozen']:.2f}, RL {v['phi_RL']:.2f}) "
                  f"p {v['p']:.3g} Holm#{v['holm_rank']} -> {v['label']}")
