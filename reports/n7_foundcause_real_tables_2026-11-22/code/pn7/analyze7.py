"""P-N7 reading (rules PN7 v1 §3-§5). PN7: refuses unless pn7_completeness.json is ok. DEV7 (--smoke): runs every code
path on the DEV7 outputs and writes only the structure (types), never values (G7).

usage: analyze7.py --set PN7
       analyze7.py --set DEV7 --smoke
"""
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
from common7 import OUT7, OUT5, TABLES, R_DRAWS, DEV_DRAWS, BASES_REF, DEV_BASES_REF, DT, jobs7, load_out
from metrics import skel_native                       # frozen P-N1
from stats7 import t_one_sided, holm, size_label, describe

IU = np.triu_indices(DT, 1)
MARGIN_PAIRS = 1.0


def up(s):
    return (np.asarray(s) != 0)[IU]


def flips(a, b):
    return int((up(a) != up(b)).sum())


def edges(s):
    return int(up(s).sum())


def fc_skel(o):
    return skel_native('foundcause', o, DT)


def p5(alg, key):
    z = np.load(OUT5 / alg / f'{key}.npz', allow_pickle=False)
    return {n: z[n] for n in z.files}


def p5_skel(alg, key):
    o = p5(alg, key)
    if alg in ('pc', 'ges'):
        g = o['skel'][:DT, :DT] != 0
        return (g | g.T).astype(np.int8)
    return skel_native(alg, o, DT)


def dp(p1, p0):
    a, b = np.asarray(p1)[:DT, :DT], np.asarray(p0)[:DT, :DT]
    off = ~np.eye(DT, dtype=bool)
    return float(np.abs(a - b)[off].mean())


def table_reading(set_name, table):
    jobs = {(j['cond'], j['r'], j['variant']): j for j in jobs7(set_name, None if set_name == 'DEV7' else table)
            if j['table'] == table}
    draws = DEV_DRAWS if set_name == 'DEV7' else R_DRAWS
    bases = DEV_BASES_REF if set_name == 'DEV7' else BASES_REF
    k0 = load_out(jobs[('k0', None, 'api')])
    s0 = fc_skel(k0)
    key5 = lambda r: f'{table}__k20_e0__r{r:02d}'
    pc0, ges0 = p5_skel('pc', f'{table}__k0'), p5_skel('ges', f'{table}__k0')
    av0, cd0 = p5_skel('avici', f'{table}__k0'), p5_skel('cdfm', f'{table}__k0')
    rows = []
    for r in range(draws):
        o = load_out(jobs[('k20_e0', r, 'api')])
        s = fc_skel(o)
        f_pc = flips(p5_skel('pc', key5(r)), pc0)
        f_ges = flips(p5_skel('ges', key5(r)), ges0)
        rows.append(dict(r=r, flips_fc=flips(s, s0), flips_pc=f_pc, flips_ges=f_ges, max_pc_ges=max(f_pc, f_ges),
                         dm_fc=edges(s) - edges(s0), dp_fc=dp(o['probs'], k0['probs']),
                         flips_avici=flips(p5_skel('avici', key5(r)), av0), flips_cdfm=flips(p5_skel('cdfm', key5(r)), cd0),
                         dropped=o['dropped'].tolist(), n_duplicates=int(o['n_duplicates'])))
    D = [x['flips_fc'] - x['max_pc_ges'] for x in rows]
    sched = {}
    for b in bases:
        ob = load_out(jobs[('k0', None, f'sched{b}')])
        sched[str(b)] = flips(fc_skel(ob), s0)
    sv = list(sched.values())
    return dict(table=table, n_draws=draws, m0_fc=edges(s0), k0_dropped=k0['dropped'].tolist(),
                k0_n_duplicates=int(k0['n_duplicates']), rows=rows, contrast_values=D, contrast=t_one_sided(D),
                flips_fc=describe([x['flips_fc'] for x in rows]), max_pc_ges=describe([x['max_pc_ges'] for x in rows]),
                dm_fc=describe([x['dm_fc'] for x in rows]), dp_fc=describe([x['dp_fc'] for x in rows]),
                flips_avici_p5=describe([x['flips_avici'] for x in rows]),
                flips_cdfm_p5=describe([x['flips_cdfm'] for x in rows]),
                schedule_reference=dict(values=sched, mean=float(np.mean(sv)), max=int(max(sv)),
                                        note='whole-schedule variability at k0 (rows, column permutation, tie-break); '
                                             'descriptive only: not a threshold, not subtracted from flips'))


def structure(x):
    if isinstance(x, dict):
        return {k: structure(v) for k, v in x.items()}
    if isinstance(x, list):
        return [structure(x[0])] if x else []
    return type(x).__name__


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', choices=['PN7', 'DEV7'], required=True)
    ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args()
    if a.set == 'PN7':
        cp = OUT7 / 'pn7_completeness.json'
        c = json.loads(cp.read_text()) if cp.exists() else {}
        if not c.get('ok'):
            print('REFUSED: pn7_completeness.json missing or not ok', flush=True)
            return 1
        tables = TABLES
    else:
        if not a.smoke:
            print('DEV7 is read only with --smoke (structure only)', flush=True)
            return 1
        tables = ('standin',)
    per = {t: table_reading(a.set, t) for t in tables}
    hyp = {}
    for t in tables:
        name = f"P7-1{'S' if t == 'sachs' else ('W' if t == 'wine' else 'X')}"
        c = per[t]['contrast']
        hyp[name] = dict(table=t, **c, sign_size=list(size_label(c['ci95'], MARGIN_PAIRS)))
    H = holm({k: v['p'] for k, v in hyp.items()})
    for k, v in hyp.items():
        rank, thr, rej = H[k]
        v.update(holm_rank=rank, holm_threshold=thr, label='CONFIRMED' if (rej and not v['degenerate']) else 'NOT_CONFIRMED')
    out = dict(set=a.set, rules='PN7 v1 (7bc40f8)', hypotheses=hyp, tables=per)
    if a.smoke:
        (OUT7 / 'dev7_reading_structure.json').write_text(json.dumps(structure(out), indent=1))
        print(f'SMOKE OK {len(hyp)} hypothesis; tables {list(per)}', flush=True)
        return 0
    (OUT7 / 'pn7_reading.json').write_text(json.dumps(out, indent=1))
    for k, v in hyp.items():
        print(f"{k}: mean {v['mean']:+.3f} CI {v['ci95'][0]:+.3f},{v['ci95'][1]:+.3f} p {v['p']:.3g} "
              f"Holm#{v['holm_rank']} -> {v['label']}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
