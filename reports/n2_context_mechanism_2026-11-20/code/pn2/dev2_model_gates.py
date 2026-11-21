"""P-N2 DEV2 model gates G10 (determinism, R-oracle) and G11 (timing, EXP2 estimate). Rules v1 §9.
No contrast or effect estimate is computed here.

usage: dev2_model_gates.py  ->  pn2_out/dev2_model_gates.json
"""
import json
import numpy as np
from common2 import *

N1OUT = ART / 'n1_runs' / 'pn1_out'
res = dict(rules='P-N2 v1 (commit 5c2c76c)', set='DEV2')


def npz(model, key):
    f = OUT2 / model / f'{key}.npz'
    if not f.exists():
        return None
    z = np.load(f, allow_pickle=False)
    d = {q: z[q] for q in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


g10 = {}
for model in ('avici', 'cdfm'):
    tau = json.loads((N1OUT / f'rn0_{model}.json').read_text())['RN0.3_determinism']['tau_rep']
    rep, orc = [], []
    for sid, cond in (('DEV2-c0-r0', 'k0'), ('DEV2-c0-r0', 'e3'), ('DEV2-c5-r0', 'k0'), ('DEV2-c5-r0', 'e3')):
        p, r = npz(model, key2(sid, cond, 'plain')), npz(model, key2(sid, cond, 'rep'))
        rep.append(None if p is None or r is None else float(np.abs(p['probs'] - r['probs']).max()))
    for sid, cond in (('DEV2-c0-r0', 'e0'), ('DEV2-c0-r0', 'e3'), ('DEV2-c5-r0', 'e0'), ('DEV2-c5-r0', 'e3')):
        p0, o = npz(model, key2(sid, 'k0', 'plain')), npz(model, key2(sid, cond, 'oracle'))
        orc.append(None if p0 is None or o is None else float(np.abs(p0['probs'] - o['probs']).max()))
    ok = all(v is not None and v <= tau for v in rep + orc)
    g10[model] = dict(tau_from_PN1=tau, rerun_max_abs_diff=rep, oracle_vs_k0_max_abs_diff=orc, pass_=ok)
res['G10'] = g10

# G11 timing
def logs(model, arm):
    f = OUT2 / model / f'log_DEV2_{arm}.jsonl'
    return [json.loads(l) for l in f.read_text(encoding='utf-8').splitlines()] if f.exists() else []


tim = {}
for model in ('avici', 'cdfm'):
    for arm in ('plain', 'R'):
        L = [r for r in logs(model, arm) if r['status'] == 'ok']
        tim[f'{model}_{arm}'] = dict(n=len(L), total_s=round(sum(r['runtime_s'] for r in L), 1),
                                     mean_s=round(float(np.mean([r['runtime_s'] for r in L])), 2) if L else None,
                                     errors=sum(1 for r in logs(model, arm) if r['status'] != 'ok'))
for alg in ('pc', 'ges'):
    f = OUT2 / alg / 'log_DEV2.jsonl'
    L = [json.loads(l) for l in f.read_text(encoding='utf-8').splitlines()] if f.exists() else []
    L = [r for r in L if r['status'] == 'ok']
    tim[alg] = dict(n=len(L), total_s=round(sum(r['runtime_s'] for r in L), 1),
                    max_s=max((r['runtime_s'] for r in L), default=None))
dg = json.loads((OUT2 / 'dev2_data_gates.json').read_text())
scr = dg['screening_timing']
tim['screening_tables'] = {t: round(sum(r['seconds'] for r in scr if r['test'] == t), 1) for t in ('fisherz', 'hsic', 'spearman')}
scale = 40 / 16
est = sum(v['total_s'] for k, v in tim.items() if k.endswith('_plain') or k.endswith('_R')) * scale
est += (tim['pc']['total_s'] + tim['ges']['total_s']) * scale
est += sum(tim['screening_tables'].values()) * scale
tim['EXP2_estimate_hours'] = round(est / 3600, 2)
tim['EXP2_over_12h'] = bool(est / 3600 > 12)
res['G11'] = tim
(OUT2 / 'dev2_model_gates.json').write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
