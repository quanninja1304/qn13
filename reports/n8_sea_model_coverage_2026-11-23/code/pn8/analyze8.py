"""P-N8 / Study 7 reading (rules PN8 v1 §3–§5): six hypotheses with Holm 0.05, Label and Size; descriptive measures;
sensitivity readout 1 - P(no edge) > 0.5. Refuses to read unless completeness8.py has written an ok record for PN8.

usage (Study 1 model environment):
  python -I analyze8.py            main reading (PN8 synthetic + Study 4 real tables)
  python -I analyze8.py --dev      structure check on DEV8 / DEV5 outputs: runs the whole pipeline, prints no values
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common8 import *
from stats8 import strat8, t_one_sided, holm, size_label

DEV = '--dev' in sys.argv


def sk_classical_syn(alg, sysid, cond, dT):
    z = np.load(OUT8 / 'classical' / alg / f'{sysid}__{cond}.npz', allow_pickle=False)
    g = z['skel'][:dT, :dT] != 0
    return (g | g.T)[np.triu_indices(dT, 1)]


def sk_classical_real(alg, key, dT):
    z = np.load(OUT5 / alg / f'{key}.npz', allow_pickle=False)
    g = z['skel'][:dT, :dT] != 0
    return (g | g.T)[np.triu_indices(dT, 1)]


def tpfp(s, g):
    t = ((g + g.T) > 0)[np.triu_indices(g.shape[0], 1)]
    return int((t & s).sum()), int((~t & s).sum())


def part_a(set_name, only_r0=False):
    off = SETS8[set_name]['off']
    rows = []
    for sysid, ci, sseed, i in systems8(set_name):
        r = int(sysid.rsplit('-r', 1)[1])
        if only_r0 and r != 0:
            continue
        X0, _, dT, g = syn_input(sysid, ci, sseed, 'k0')
        a = seed_a(i, off)
        o = {c: load_out(f'{sysid}__{c}__s{a}') for c in CONDS_A}
        refs = [load_out(f'{sysid}__k0__s{seed_b(i, m, off)}') for m in range(1, M_REF + 1)]
        assert o['k0']['meta']['input_sha'] == sha(X0)
        row = dict(sysid=sysid, ci=ci, lin=ci in LINEAR, dT=dT)
        for alt in (False, True):
            tag = 'alt' if alt else 'nat'
            sK, sA, sS = (skel(o[c]['prob'], dT, alt) for c in CONDS_A)
            sR = [skel(x['prob'], dT, alt) for x in refs]
            row[f'delta_A20_{tag}'] = float(np.mean([flips(s, sA) - flips(s, sK) for s in sR]))
            row[f'delta_S20_{tag}'] = float(np.mean([flips(s, sS) - flips(s, sK) for s in sR]))
            fK, fA, fS = f1(sK, g), f1(sA, g), f1(sS, g)
            row[f'H_{tag}'] = fK - fA
            row[f'H_S20_{tag}'] = fK - fS
            row[f'f1_k0_{tag}'] = fK
            row[f'flips_same_A20_{tag}'] = flips(sK, sA)
            row[f'flips_same_S20_{tag}'] = flips(sK, sS)
            row[f'flips_seed_{tag}'] = float(np.mean([flips(s, sK) for s in sR]))
            row[f'edges_k0_{tag}'], row[f'edges_A20_{tag}'], row[f'edges_S20_{tag}'] = int(sK.sum()), int(sA.sum()), int(sS.sum())
            (tpK, fpK), (tpA, fpA) = tpfp(sK, g), tpfp(sA, g)
            row[f'dTP_A20_{tag}'], row[f'dFP_A20_{tag}'] = tpA - tpK, fpA - fpK
            if ci in LINEAR:
                hc, fc = {}, {}
                for alg in ('pc', 'ges'):
                    c0, c1 = sk_classical_syn(alg, sysid, 'k0', dT), sk_classical_syn(alg, sysid, 'A20', dT)
                    hc[alg] = f1(c0, g) - f1(c1, g)
                    fc[alg] = flips(c0, c1)
                row[f'H_pc'], row[f'H_ges'] = hc['pc'], hc['ges']
                row[f'beyond_{tag}'] = row[f'H_{tag}'] - max(hc['pc'], hc['ges'])
                row['flips_pc'], row['flips_ges'] = fc['pc'], fc['ges']
                row[f'c11_A20_{tag}'] = row[f'flips_same_A20_{tag}'] - max(fc['pc'], fc['ges'])
        row['dp_A20'] = M1.dp(o['A20']['prob'], o['k0']['prob'], dT)[0]
        row['dp_S20'] = M1.dp(o['S20']['prob'], o['k0']['prob'], dT)[0]
        row['dp_seed'] = float(np.mean([M1.dp(x['prob'], o['k0']['prob'], dT)[0] for x in refs]))
        rows.append(row)
    return rows


def part_b(set5, tables, draws):
    off = 0 if set5 == 'PN5' else SETS8['DEV8']['off']
    out = {}
    for table in tables:
        j = C5.TABLES[table]['j'] if table in C5.TABLES else 0
        rows = []
        for r in range(draws):
            a = seed_ar(j, r, off)
            K = load_out(f'{set5}-{table}__k0__r{r:02d}__s{a}')
            X = load_out(f'{set5}-{table}__k20_e0__r{r:02d}__s{a}')
            R = [load_out(f'{set5}-{table}__k0__r{r:02d}__s{seed_br(j, r, m, off)}') for m in range(1, M_REF + 1)]
            dT = K['meta']['dT']
            row = dict(table=table, r=r, dT=dT)
            for alt in (False, True):
                tag = 'alt' if alt else 'nat'
                sK, sX = skel(K['prob'], dT, alt), skel(X['prob'], dT, alt)
                sR = [skel(x['prob'], dT, alt) for x in R]
                row[f'delta_{tag}'] = float(np.mean([flips(s, sX) - flips(s, sK) for s in sR]))
                row[f'flips_same_{tag}'] = flips(sK, sX)
                row[f'flips_seed_{tag}'] = float(np.mean([flips(s, sK) for s in sR]))
                row[f'edges_k0_{tag}'], row[f'edges_pad_{tag}'] = int(sK.sum()), int(sX.sum())
                if set5 == 'PN5':
                    fc = {alg: flips(sk_classical_real(alg, f'{table}__k0', dT),
                                     sk_classical_real(alg, f'{table}__k20_e0__r{r:02d}', dT)) for alg in ('pc', 'ges')}
                    row['flips_pc'], row['flips_ges'] = fc['pc'], fc['ges']
                    row[f'c11_{tag}'] = row[f'flips_same_{tag}'] - max(fc['pc'], fc['ges'])
            row['dp'] = M1.dp(X['prob'], K['prob'], dT)[0]
            row['dp_seed'] = float(np.mean([M1.dp(x['prob'], K['prob'], dT)[0] for x in R]))
            rows.append(row)
        out[table] = rows
    return out


def tests(A, B, tag):
    cells = [x['ci'] for x in A]
    lin = [x for x in A if x['lin']]
    res = {'P8-1': strat8([x[f'delta_A20_{tag}'] for x in A], cells),
           'P8-1S': strat8([x[f'delta_S20_{tag}'] for x in A], cells),
           'P8-2': strat8([x[f'H_{tag}'] for x in A], cells),
           'P8-3': strat8([x[f'beyond_{tag}'] for x in lin], [x['ci'] for x in lin])}
    for h, table in (('P8-4S', 'sachs'), ('P8-4W', 'wine')):
        if table in B:
            v = [x[f'delta_{tag}'] for x in B[table]]
            t = t_one_sided(v)
            res[h] = dict(theta=t['mean'], se=t['se'], df=t['df'], t=t['t'], p=t['p'], ci95=t['ci95'],
                          degenerate=t['degenerate'], draws_pos_zero_neg=[int(np.sum(np.array(v) > 0)),
                                                                          int(np.sum(np.array(v) == 0)),
                                                                          int(np.sum(np.array(v) < 0))])
    for h, d in res.items():
        d['size'] = size_label(d['ci95'], MARGIN[h])[1]
    return res


def mean_of(rows, k):
    v = [x[k] for x in rows if k in x]
    return float(np.mean(v)) if v else None


if DEV:
    A = part_a('DEV8', only_r0=True)
    B = part_b('DEV5', ('standin',), DEV5_DRAWS)
    B = {'sachs': B['standin']}                     # structure only: the stand-in plays the role of one table
    for tag in ('nat', 'alt'):
        T = tests(A, B, tag)
        hl = holm({h: T[h]['p'] for h in T})
        assert set(hl) == set(T)
    print(json.dumps(dict(dev_structure_ok=True, n_rows_A=len(A), keys_A=sorted(A[0]), n_rows_B=len(B['sachs']),
                          keys_B=sorted(B['sachs'][0]), hypotheses=sorted(T)), indent=1))
    sys.exit(0)

comp = OUT8 / 'pn8_completeness.json'
if not comp.exists() or not json.loads(comp.read_text())['ok']:
    sys.exit('completeness8.py has not passed: refusing to read (rules §7)')
gates = json.loads((OUT8 / 'gates8.json').read_text())
A = part_a('PN8')
B = part_b('PN5', TABLES, R_DRAWS)
T = tests(A, B, 'nat')
hl = holm({h: T[h]['p'] for h in HYPS})
for h in HYPS:
    rank, thr, rej = hl[h]
    T[h].update(holm_rank=rank, holm_threshold=thr, label='CONFIRMED' if rej else 'NOT_CONFIRMED', margin=MARGIN[h])
S = tests(A, B, 'alt')                                # sensitivity readout, no Holm (rules §1)
desc = dict(
    A={c: {k: mean_of([x for x in A if x['ci'] == c], k) for k in A[0] if k not in ('sysid', 'ci', 'lin', 'dT')}
       for c in range(8)},
    A_all={k: mean_of(A, k) for k in A[0] if k not in ('sysid', 'ci', 'lin', 'dT')},
    B={t: {k: mean_of(B[t], k) for k in B[t][0] if k not in ('table', 'r', 'dT')} for t in B})
reading = dict(rules='PN8 v1 (locked 49558ae)', flags=dict(G3=gates.get('G3', {}).get('label'),
                                                           G4=gates.get('G4', {}).get('flag')),
               hypotheses=T, sensitivity_alt_readout=S, descriptive=desc, rows_A=A, rows_B=B)
(OUT8 / 'pn8_reading.json').write_text(json.dumps(reading, indent=1))
print(f"flags: G3 {reading['flags']['G3']}, G4 {reading['flags']['G4']}")
print(f"{'ID':<6} {'estimate':>9} {'95% CI':>22} {'t':>7} {'df':>6} {'p':>10} {'Holm':>12} {'label':<14} size")
for h in HYPS:
    d = T[h]
    ci = f"[{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]"
    t_ = 'NA' if d['t'] is None else f"{d['t']:.2f}"
    df_ = 'NA' if d['df'] is None else f"{d['df']:.1f}"
    print(f"{h:<6} {d['theta']:+9.3f} {ci:>22} {t_:>7} {df_:>6} {d['p']:10.2e} {d['holm_rank']}, {d['holm_threshold']:.4f}"
          f" {d['label']:<14} {d['size']}")
print('sensitivity (1 - P(no edge) > 0.5), no Holm:')
for h in HYPS:
    d = S[h]
    print(f"  {h:<6} {d['theta']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] p {d['p']:.2e} {d['size']}")
