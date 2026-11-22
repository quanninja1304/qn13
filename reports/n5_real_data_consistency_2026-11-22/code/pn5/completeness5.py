"""P-N5 completeness check, required before reading (rules PN5 v1 §7).

Checks:
 - every job of the locked list (616 for PN5) has exactly one terminal record (ok, timeout or error) in its log, and the
   logs hold no record of a job outside the list;
 - no error record and no budget_stop record;
 - timeouts only on descriptive inputs of PC and GES (never k0, its rerun or k20_e0); their number is recorded;
 - every ok job has its output file, and the input SHA in its meta matches the regenerated input; regeneration asserts
   that the real block is bitwise X_R and the padding block is bitwise the generator output;
 - X_R of each table equals the saved copy and the gate-G1 record (PN5) or the prep record (DEV5);
 - the two data files match the manifest SHA-256 (PN5);
 - the freeze gate wrote ok = true at the first pn5_start and the last pn5_end, with the same freeze commit,
   SHA256SUMS hash and dependency hash;
 - for every algorithm and table, the two k0 runs are bitwise identical (all saved arrays).
usage: completeness5.py [--set PN5|DEV5]  ->  pn5_out/pn5_completeness.json (exit 1 if anything fails)
  DEV5 only tests this script before the freeze (output dev5_completeness_test.json; its freeze-gate items fail by design).
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common5 import (OUT5, SETS5, TABLES, ALGS, CLASSICAL, MAIN, jobs5, key5, assemble5, real_block, xr_file, sha,
                     file_sha, manifest)

ap = argparse.ArgumentParser(); ap.add_argument('--set', default='PN5', choices=['PN5', 'DEV5']); a = ap.parse_args()
SET = a.set
S = SETS5[SET]
bad, rep = [], dict(set=SET)
input_sha_cache = {}


def input_sha(table, cond, r):
    q = (table, cond, r)
    if q not in input_sha_cache:
        X, _, _ = assemble5(SET, table, cond, r)
        input_sha_cache[q] = sha(X)
    return input_sha_cache[q]


def arrays(alg, key):
    z = np.load(OUT5 / alg / f'{key}.npz', allow_pickle=False)
    return {q: z[q] for q in z.files if q != 'meta'}, json.loads(str(z['meta']))


n_jobs, per_alg = 0, {}
for alg in ALGS:
    jl = jobs5(SET, alg, extra_rep=(SET == 'DEV5'))
    keys = {key5(*j): j for j in jl}
    n_jobs += len(keys)
    lp = OUT5 / alg / f'log_{SET}.jsonl'
    recs = [json.loads(l) for l in lp.read_text(encoding='utf-8').splitlines() if l.strip()] if lp.exists() else []
    if not lp.exists():
        bad.append(f'missing {alg}/log_{SET}.jsonl')
    by = {}
    for r_ in recs:
        by.setdefault(r_['key'], []).append(r_)
    c = dict(jobs=len(keys), ok=0, timeout=0, error=0, budget_stop=0, timeouts=[])
    for r_ in recs:
        s_ = r_['status']
        if s_ == 'budget_stop':
            c['budget_stop'] += 1
        elif s_.startswith('error'):
            c['error'] += 1
    for key in set(by) - set(keys):
        bad.append(f'{alg}: log record for a job outside the locked list: {key}')
    for key, (t, cond, r, rp) in keys.items():
        term = [x for x in by.get(key, []) if x['status'] in ('ok', 'timeout') or x['status'].startswith('error')]
        if len(term) != 1:
            bad.append(f'{alg} {key}: {len(term)} terminal records (exactly 1 required)')
            continue
        s_ = term[0]['status']
        if s_ == 'timeout':
            c['timeout'] += 1; c['timeouts'].append(key)
            if alg not in CLASSICAL or cond in MAIN:
                bad.append(f'{alg} {key}: timeout on an input where it is not allowed')
        elif s_ == 'ok':
            c['ok'] += 1
            f = OUT5 / alg / f'{key}.npz'
            if not f.exists():
                bad.append(f'{alg} {key}: ok record but no output file')
                continue
            _, meta = arrays(alg, key)
            if meta['input_sha'] != input_sha(t, cond, r):
                bad.append(f'{alg} {key}: input SHA mismatch')
            if meta['xr_sha'] != real_block(t)['XR_sha']:
                bad.append(f'{alg} {key}: X_R SHA in meta differs')
    if c['error']:
        bad.append(f"{alg}: {c['error']} error records")
    if c['budget_stop']:
        bad.append(f"{alg}: budget_stop record present")
    for t in S['tables']:
        reps = [(key5(t, 'k0'), key5(t, 'k0', rep=True))]
        if SET == 'DEV5' and t == S['tables'][0]:
            reps.append((key5(t, 'k40_e0', 0), key5(t, 'k40_e0', 0, True)))
        for k1, k2 in reps:
            if (OUT5 / alg / f'{k1}.npz').exists() and (OUT5 / alg / f'{k2}.npz').exists():
                A1, A2 = arrays(alg, k1)[0], arrays(alg, k2)[0]
                same = set(A1) == set(A2) and all(A1[q].tobytes() == A2[q].tobytes() and A1[q].dtype == A2[q].dtype for q in A1)
                c.setdefault('reruns_bitwise_identical', {})[f'{k1} vs rerun'] = bool(same)
                if not same:
                    bad.append(f'{alg} {k1}: rerun not bitwise identical')
            else:
                bad.append(f'{alg} {k1}: k0 run or rerun missing')
    per_alg[alg] = c
rep['n_jobs'] = n_jobs
if SET == 'PN5' and n_jobs != 616:
    bad.append(f'{n_jobs} jobs in the list, expected 616')
rep['per_algorithm'] = per_alg

# X_R and data files
ref = {}
if SET == 'PN5':
    gp = OUT5 / 'gates5.json'
    ref = {t: v['XR_sha'] for t, v in json.loads(gp.read_text())['G1']['tables'].items()} if gp.exists() else {}
else:
    pp = OUT5 / 'inputs' / 'prep_DEV5.json'
    ref = {t: v['XR_sha'] for t, v in json.loads(pp.read_text()).items()} if pp.exists() else {}
xr = {}
for t in S['tables']:
    rb = real_block(t)
    saved = sha(np.load(xr_file(t))) if xr_file(t).exists() else None
    xr[t] = dict(recomputed=rb['XR_sha'], saved=saved, gate_record=ref.get(t))
    if not (rb['XR_sha'] == saved == ref.get(t)):
        bad.append(f'{t}: X_R differs between recomputation, saved copy and gate record')
rep['XR'] = xr
if SET == 'PN5':
    man = manifest()
    rep['data_files'] = {t: file_sha(T['path']) == man[T['mkey']]['member_used']['sha256'] for t, T in TABLES.items()}
    if not all(rep['data_files'].values()):
        bad.append('a data file differs from the manifest')

# freeze gate headers
hp = OUT5 / 'pn5_run_header.json'
hdr = json.loads(hp.read_text()) if hp.exists() else []
starts = [h for h in hdr if h['label'] == 'pn5_start']
ends = [h for h in hdr if h['label'] == 'pn5_end']
first, last = (starts[0] if starts else None), (ends[-1] if ends else None)
for lab, h in (('pn5_start', first), ('pn5_end', last)):
    if h is None or not h['ok'] or not h.get('data_ok'):
        bad.append(f'freeze gate {lab} missing or not ok')
if first and last and any(first[q] != last[q] for q in ('freeze_commit', 'sha256sums_sha', 'deps_sha')):
    bad.append('freeze commit, SHA256SUMS hash or dependency hash differs between start and end')
rep['freeze_gate'] = {lab: (None if h is None else dict(ok=h['ok'], freeze_commit=h['freeze_commit'], time_local=h['time_local']))
                      for lab, h in (('pn5_start', first), ('pn5_end', last))}
rep['ok'] = not bad
rep['problems'] = bad
(OUT5 / ('pn5_completeness.json' if SET == 'PN5' else 'dev5_completeness_test.json')).write_text(json.dumps(rep, indent=1))
print(json.dumps({k: v for k, v in rep.items() if k != 'per_algorithm'}, indent=1))
print({alg: {q: v[q] for q in ('jobs', 'ok', 'timeout', 'error', 'budget_stop')} for alg, v in per_alg.items()})
sys.exit(1 if bad else 0)
