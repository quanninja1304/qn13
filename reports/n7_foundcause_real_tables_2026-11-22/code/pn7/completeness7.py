"""P-N7 completeness check before reading (rules PN7 v1 §6). Exits 1 on any problem; writes <set>_completeness.json.

Checks: every job has exactly one 'ok' record and an output, and no other record (no error, no budget_stop); input
hashes match the regenerated inputs (real inputs also match P-N5 inputs5.json; DEV7 inputs match the DEV5 log of P-N5);
the k0 rerun is bitwise identical; the adapter at base 42 matches the API within 1e-6 at k0; the row indices of the
schedule are identical between k0 and every padded input (package source check plus recomputation, no model call);
P-N5 classical outputs exist and belong to the same inputs; freeze-gate headers ok at the start and end of each run.
usage: completeness7.py --set PN7|DEV7
"""
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
from common7 import (OUT7, OUT5, INPUTS5, TABLES, ADAPTER_TOL, COMPARE, jobs7, key7, input_key, assemble7, out_file,
                     load_out, schedule_source_check, row_indices, max_abs_diff, bitwise_equal, sha)

ap = argparse.ArgumentParser()
ap.add_argument('--set', choices=['PN7', 'DEV7'], required=True)
a = ap.parse_args()
bad = []
runs = [('pn7_' + t, jobs7('PN7', t)) for t in TABLES] if a.set == 'PN7' else [('dev7', jobs7('DEV7'))]
inputs5 = json.loads(INPUTS5.read_text())
dev5 = {}
for line in (OUT5 / 'avici' / 'log_DEV5.jsonl').read_text(encoding='utf-8').splitlines():
    if line.strip():
        r = json.loads(line)
        dev5[r['key']] = r['input_sha']
src = schedule_source_check()
if not src['ok']:
    bad.append(f'schedule source lines not as described: {src}')
stats = dict(n_jobs=0, inputs_checked=0, row_index_inputs=0)
for label, jobs in runs:
    logp = OUT7 / 'foundcause' / f'log_{label}.jsonl'
    recs = [json.loads(l) for l in logp.read_text(encoding='utf-8').splitlines() if l.strip()] if logp.exists() else []
    expected = {key7(j) for j in jobs}
    for r in recs:
        if r.get('status') != 'ok':
            bad.append(f"{label}: record {r.get('key')} has status {r.get('status')}")
        if r.get('key') not in expected:
            bad.append(f"{label}: unexpected record {r.get('key')}")
    oks = {}
    for r in recs:
        if r.get('status') == 'ok':
            oks.setdefault(r['key'], []).append(r)
    for j in jobs:
        k = key7(j)
        stats['n_jobs'] += 1
        if len(oks.get(k, [])) != 1:
            bad.append(f'{label}: {k} has {len(oks.get(k, []))} ok records')
            continue
        if not out_file(j).exists():
            bad.append(f'{label}: output missing for {k}')
            continue
        X, dT = assemble7(j)
        s = sha(X)
        stats['inputs_checked'] += 1
        if oks[k][0]['input_sha'] != s or load_out(j)['meta']['input_sha'] != s:
            bad.append(f'{label}: input hash differs for {k}')
        ik = input_key(j)
        if a.set == 'PN7' and inputs5.get(ik) != s:
            bad.append(f'{label}: {ik} differs from inputs5.json')
        if a.set == 'DEV7' and j['table'] == 'standin' and dev5.get(ik) != s:
            bad.append(f'{label}: {ik} differs from the DEV5 log of P-N5')
    # k0 rerun, adapter at base 42, row indices
    t = jobs[0]['table']
    k0 = [j for j in jobs if j['table'] == t and j['cond'] == 'k0']
    get = {j['variant']: j for j in k0}
    try:
        o_api, o_rep, o_42 = (load_out(get[v]) for v in ('api', 'rep', 'sched42'))
        if not bitwise_equal(o_api, o_rep):
            bad.append(f'{label}: k0 rerun not bitwise identical')
        dev = max(max_abs_diff(o_42[c], o_api[c]) for c in ('probs', 'agreement', 'adj_native'))
        if dev > ADAPTER_TOL:
            bad.append(f'{label}: adapter at base 42 differs from the API by {dev:.3g}')
        stats[f'{label}_adapter42_max_abs_diff'] = dev
    except FileNotFoundError as e:
        bad.append(f'{label}: k0 outputs missing ({e})')
    n0 = assemble7(get['api'])[0].shape[0]
    rows0 = row_indices(n0)
    for j in jobs:
        if j['table'] == t and j['cond'] != 'k0':
            n = assemble7(j)[0].shape[0]
            stats['row_index_inputs'] += 1
            if n != n0 or not all(np.array_equal(x, y) for x, y in zip(rows0, row_indices(n))):
                bad.append(f'{label}: row indices differ between k0 and {key7(j)}')
    # P-N5 classical outputs on the same inputs
    for j in jobs:
        if j['table'] in TABLES or j['table'] == 'standin':
            if j['variant'] != 'api':
                continue
            for alg in ('pc', 'ges', 'avici', 'cdfm'):
                p = OUT5 / alg / f'{input_key(j)}.npz'
                if not p.exists():
                    bad.append(f'P-N5 output missing: {alg} {input_key(j)}')
                    continue
                m = json.loads(str(np.load(p, allow_pickle=False)['meta']))
                if m.get('input_sha') != sha(assemble7(j)[0]):
                    bad.append(f'P-N5 output {alg} {input_key(j)} belongs to another input')
hdr_info = None
if a.set == 'PN7':
    hp = OUT7 / 'pn7_run_header.json'
    H = json.loads(hp.read_text()) if hp.exists() else []
    hdr_info = {}
    commits = set()
    for t in TABLES:
        st = [h for h in H if h['label'] == f'pn7_start_{t}']
        en = [h for h in H if h['label'] == f'pn7_end_{t}']
        if not st or not en:
            bad.append(f'freeze-gate header missing for {t}')
            continue
        s0, e0 = st[-1], en[-1]
        for hh in (s0, e0):
            if not hh['ok']:
                bad.append(f"freeze gate not ok: {hh['label']}")
            commits.add((hh['freeze_commit'], hh['sha256sums_sha'], hh['deps_sha']))
        hdr_info[t] = dict(start=dict(ok=s0['ok'], time_local=s0['time_local']), end=dict(ok=e0['ok'], time_local=e0['time_local']))
    if len(commits) > 1:
        bad.append('freeze headers differ between or within the runs')
out = dict(set=a.set, schedule_source=src, **stats, freeze_gate=hdr_info, ok=not bad, problems=bad, n_problems=len(bad))
(OUT7 / f'{a.set.lower()}_completeness.json').write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != 'problems'}, indent=1))
for b in bad[:30]:
    print('PROBLEM:', b)
sys.exit(1 if bad else 0)
