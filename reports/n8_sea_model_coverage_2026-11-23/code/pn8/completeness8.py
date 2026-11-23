"""P-N8 / Study 7 completeness check (rules PN8 v1 §7). Must pass before analyze8.py reads anything.

Checks, for the runs A1–A4 and B (and IL if it was triggered by G3):
 - every planned job has exactly one terminal record in the logs, with status ok (no error, no budget_stop);
 - each job ran exactly one input, with the planned seed;
 - input hashes match the regenerated inputs; the target block is bit-identical across the inputs of a system; real
   inputs match Study 4's inputs5.json;
 - adapter: layout of `true` correct for every output, AUROC equal where defined;
 - reruns bit-identical to the original outputs;
 - freeze headers: a successful start and end header for each run, all with the same freeze commit;
 - classical controls present for every linear system at k0 and A20, with matching input hashes.
Writes pn8_out/pn8_completeness.json. usage (Study 1 model environment): python -I completeness8.py
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common8 import *

bad, info = [], {}
gates = json.loads((OUT8 / 'gates8.json').read_text()) if (OUT8 / 'gates8.json').exists() else {}
if not gates.get('ok_to_freeze'):
    bad.append('gates8.json missing or not ok')
runs = ['A1', 'A2', 'A3', 'A4', 'B'] + (['IL'] if gates.get('G3', {}).get('label') == 'POSITION_SENSITIVE' else [])
inputs5 = json.loads(INPUTS5.read_text())
hdrs = json.loads((OUT8 / 'pn8_run_header.json').read_text()) if (OUT8 / 'pn8_run_header.json').exists() else []
freezes = set()
for run in runs:
    st = [h for h in hdrs if h['label'] == f'pn8_start_{run}']
    en = [h for h in hdrs if h['label'] == f'pn8_end_{run}']
    if not st or not st[-1]['ok'] or not en or not en[-1]['ok']:
        bad.append(f'{run}: missing or failed start/end freeze header')
    else:
        freezes |= {st[-1]['freeze_commit'], en[-1]['freeze_commit']}
    recs = {}
    lf = OUT8 / f'log_{run}.jsonl'
    for line in (lf.read_text(encoding='utf-8').splitlines() if lf.exists() else []):
        r = json.loads(line)
        recs.setdefault(r['key'], []).append(r)
    jobs = run_jobs(run)
    n_ok = 0
    for j in jobs:
        rs = recs.get(j['key'], [])
        if len(rs) != 1 or rs[0]['status'] != 'ok':
            bad.append(f"{run}: {j['key']} has {len(rs)} terminal records {[x['status'] for x in rs]}")
            continue
        m = load_out(j['key'])['meta']
        if m['seed'] != j['seed'] or m.get('n_inputs') != 1:
            bad.append(f"{run}: {j['key']} seed or input count differs from the plan")
        if not m['layout_ok'] or m['auc_ok'] is False:
            bad.append(f"{run}: {j['key']} adapter check failed")
        X, G, xsha, dT, perm = build(j)
        if m['input_sha'] != xsha:
            bad.append(f"{run}: {j['key']} input hash differs from the regenerated input")
        if j['kind'] == 'real':
            ik = f"{j['table']}__k0" if j['cond'] == 'k0' else f"{j['table']}__k20_e0__r{j['r']:02d}"
            if inputs5.get(ik) != xsha:
                bad.append(f'{run}: {ik} differs from inputs5.json')
        if j['role'] == 'rerun':
            if not np.array_equal(load_out(j['key'])['prob'], load_out(j['of'])['prob']):
                bad.append(f"{run}: rerun {j['key']} not bit-identical")
        n_ok += 1
    info[run] = dict(planned=len(jobs), ok=n_ok)
    if run in RUN_CELLS:                     # target block bit-identical across k0, A20, S20 (and refs share k0)
        for sysid, ci, sseed, i in systems8('PN8'):
            if ci in RUN_CELLS[run]:
                xs = [syn_input(sysid, ci, sseed, c)[0] for c in CONDS_A]
                dT = CELLS[ci][0]
                if not all(np.array_equal(xs[0][:, :dT], x[:, :dT]) for x in xs[1:]):
                    bad.append(f'{sysid}: target block not bit-identical across inputs')
if len(freezes) > 1:
    bad.append(f'runs used different freeze commits: {sorted(freezes)}')
for alg in ('pc', 'ges'):
    for sysid, ci, sseed, i in systems8('PN8'):
        if ci not in LINEAR:
            continue
        for cond in ('k0', 'A20'):
            f = OUT8 / 'classical' / alg / f'{sysid}__{cond}.npz'
            if not f.exists():
                bad.append(f'missing {alg} {sysid} {cond}'); continue
            m = json.loads(str(np.load(f, allow_pickle=False)['meta']))
            if m['status'] != 'ok' or m['input_sha'] != sha(syn_input(sysid, ci, sseed, cond)[0]):
                bad.append(f'{alg} {sysid} {cond}: status or input hash')
out = dict(ok=not bad, runs=info, freeze_commits=sorted(freezes), problems=bad[:200], n_problems=len(bad))
(OUT8 / 'pn8_completeness.json').write_text(json.dumps(out, indent=1))
print(json.dumps(dict(ok=out['ok'], runs=info, freeze_commits=out['freeze_commits'], n_problems=len(bad),
                      first_problems=bad[:10]), indent=1))
sys.exit(0 if not bad else 1)
