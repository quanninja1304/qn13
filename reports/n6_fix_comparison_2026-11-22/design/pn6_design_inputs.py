"""P-N6 design inputs (descriptive; read-only on frozen P-N2 outputs; no model is run).

(1) EXP2 screening variants (pn2_out/exp2_screen_variants.json, frozen P-N2 code): per family and variant, the share of
    true target edges cut (split) and of padding columns merged into a target component, over all EXP2 inputs;
(2) EXP2, Bonferroni variants: target splits with 20 Gaussian columns (e0) minus splits at k0, per system. Under a
    whole-table Bonferroni correction the per-pair level is alpha / (D(D-1)/2), so target-target decisions can depend on D;
(3) HELD2 runtimes (pn2_out/<model>/log_HELD2_<arm>.jsonl): medians by arm, input and d_T, and totals.
usage: python -I pn6_design_inputs.py <artifacts/n2_runs/pn2_out> <output json>
"""
import collections, json, statistics, sys
from pathlib import Path

SRC, DEST = Path(sys.argv[1]), Path(sys.argv[2])
V = json.loads((SRC / 'exp2_screen_variants.json').read_text())
out = dict(alpha=V['alpha'], screening={}, bonferroni_k0_vs_e0={}, held2_runtime={})

acc = collections.defaultdict(lambda: dict(split=0, true_edges=0, merged=0, padding_cols=0, inputs=0, inputs_with_split=0))
for r in V['rows']:
    a = acc[f"{r['fam']}|{r['variant']}|{r['method']}"]
    a['split'] += r['split']; a['true_edges'] += r['n_true_edges']; a['merged'] += r['merged']; a['padding_cols'] += r['k']
    a['inputs'] += 1; a['inputs_with_split'] += int(r['split'] > 0)
for key, a in sorted(acc.items()):
    out['screening'][key] = dict(a, split_share=a['split'] / max(a['true_edges'], 1), merged_share=a['merged'] / max(a['padding_cols'], 1))

by = collections.defaultdict(dict)
for r in V['rows']:
    if r['method'] == 'bonferroni':
        by[(r['sys'], r['variant'])][r['cond']] = r
for var in ('primary', 'hsic_agnostic'):
    for fam in ('lin', 'rff'):
        d = [c['e0']['split'] - c['k0']['split'] for (s, v), c in by.items()
             if v == var and 'k0' in c and 'e0' in c and c['k0']['fam'] == fam]
        out['bonferroni_k0_vs_e0'][f'{fam}|{var}'] = dict(systems=len(d), mean_extra_splits=sum(d) / len(d),
                                                          more=sum(x > 0 for x in d), same=sum(x == 0 for x in d), fewer=sum(x < 0 for x in d))

for model in ('avici', 'cdfm'):
    for arm in ('plain', 'R'):
        L = [json.loads(l) for l in (SRC / model / f'log_HELD2_{arm}.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
        g = collections.defaultdict(list)
        for x in L:
            g[f"{x['cond']}|dT{x['dT']}"].append(x['runtime_s'])
        out['held2_runtime'][f'{model}|{arm}'] = dict(n=len(L), total_min=sum(x['runtime_s'] for x in L) / 60,
                                                     median_s={k: statistics.median(v) for k, v in sorted(g.items())})

DEST.write_text(json.dumps(out, indent=1))
for sec in ('screening', 'bonferroni_k0_vs_e0'):
    for k, v in out[sec].items():
        print(sec, k, {q: (round(x, 4) if isinstance(x, float) else x) for q, x in v.items()})
for k, v in out['held2_runtime'].items():
    print('runtime', k, 'n', v['n'], 'total %.1f min' % v['total_min'])
