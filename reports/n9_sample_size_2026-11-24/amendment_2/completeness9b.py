"""P-N9 amendment 2, item 4 (PN9_amendment2_vi.md): completeness check that accepts only the listed non-ok records. It
replaces amendment_1/completeness9a.py (never run on real outputs), with the same steps and two changes: the accepted list
holds the GES budget stops of amendment 1 and the SEA R3 timeout of amendment 2, and a listed SEA job must also pass the
SEA checks (seed as planned, layout_ok true, auc_ok not false). No metric is computed.

Steps:
 1. the frozen completeness9.py runs unchanged, in this process (runpy, so it uses the same common9 module); its output
    checks/pn9_completeness.json is kept byte for byte as checks/pn9_completeness_frozen.json;
 2. conditions:
    a. every non-ok record in the main-run logs of every model is in the accepted list (model, run, key, status, and its
       time: elapsed_s of a budget stop, wall_total_s of an error), and every listed record is in the logs; budget stops
       only for GES R1 and R3, errors only 'error: exit timeout' of SEA R3;
    b. the job of each listed record has exactly one 'ok' record, with an output, and passes the rules §7 checks of every
       other job: level n as planned, input hash equal to the rebuilt input (and to the output's metadata), for a rerun
       an output identical to the original, and for SEA the seed as planned and the adapter checks;
    c. for each run with listed records: successful start headers = 1 + its listed records; the last start and end headers
       are successful and the end header is the later one;
    d. the problems reported by the frozen check are exactly those the listed records cause: per run with listed records,
       one 'non-ok records' line with its non-ok keys in log order; per listed job, one 'has N records or no output' line,
       N = 1 + its listed records; and, as a count, every planned job is verified by the frozen check or by b;
 3. writes checks/pn9_completeness.json, the file analyze9.py reads.
usage (Study 1 model environment): python -I completeness9b.py [allowed_stops.json allowed_errors.json]
"""
import json
import runpy
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PN9 = HERE.parents[2] / 'artifacts' / 'n9_runs' / 'pn9'
sys.path.insert(0, str(PN9))
import common9 as C

STOPS = Path(sys.argv[1]) if len(sys.argv) > 2 else HERE.parent / 'amendment_1' / 'allowed_stops9.json'
ERRORS = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'allowed_errors9.json'
CHECKS = C.REPORT / 'checks'
OUTF, FROZENF = CHECKS / 'pn9_completeness.json', CHECKS / 'pn9_completeness_frozen.json'
RUNS = {m: (('R1', 'R3') if m in C.CLASSICAL else tuple(C.RUN_CELLS)) for m in C.ALL}
SCOPE = {'budget_stop': lambda m, run: m == 'ges' and run in ('R1', 'R3'),
         'error: exit timeout': lambda m, run: m == 'sea' and run == 'R3'}


def logs(model, run):
    f = C.OUT9 / f'log_{model}_{run}.jsonl'
    return [json.loads(l) for l in f.read_text(encoding='utf-8').splitlines() if l.strip()] if f.exists() else []


def arrays_equal(z1, z2, skip=('meta', 'perm')):                # as in completeness9.py
    k1, k2 = set(z1.files) - set(skip), set(z2.files) - set(skip)
    return k1 == k2 and all(np.array_equal(z1[k], z2[k]) for k in k1)


def tval(r):
    v = r.get('elapsed_s') if r.get('status') == 'budget_stop' else r.get('wall_total_s')
    return float('nan') if v is None else float(v)


# ---------------------------------------------------------------- 1. frozen check, unchanged
for f in (OUTF, FROZENF):
    if f.exists():
        f.unlink()
code = 0
try:
    runpy.run_path(str(PN9 / 'completeness9.py'), run_name='__main__')
except SystemExit as e:
    code = e.code
if not OUTF.exists():
    sys.exit('the frozen completeness9.py wrote no output: stop')
shutil.copyfile(OUTF, FROZENF)
frozen = json.loads(FROZENF.read_text())
fp = list(frozen.get('problems', []))

problems = []
A = [(s['model'], s['run'], s['key'], 'budget_stop', float(s['elapsed_s']))
     for s in json.loads(STOPS.read_text(encoding='utf-8'))['stops']]
A += [(s['model'], s['run'], s['key'], s['status'], float(s['wall_total_s']))
      for s in json.loads(ERRORS.read_text(encoding='utf-8'))['records']]
for s in A:
    if s[3] not in SCOPE or not SCOPE[s[3]](s[0], s[1]):
        problems.append(f'listed record outside the scope of amendments 1 and 2: {s}')
L = {(m, run): logs(m, run) for m in C.ALL for run in RUNS[m]}

# ---------------------------------------------------------------- a. non-ok records in the logs = listed records
F = [(m, run, r['key'], r.get('status'), tval(r)) for (m, run), recs in L.items() for r in recs if r.get('status') != 'ok']
if Counter(F) != Counter(A):
    problems.append(f'non-ok records in the logs {sorted(F, key=str)} differ from the listed records {sorted(A, key=str)}')

# ---------------------------------------------------------------- b. the job of each listed record
verified, extra_ok = [], Counter()
for m, run, key in sorted({s[:3] for s in A}):
    plan = {j['key']: j for j in C.run_jobs(m, run)}
    j = plan.get(key)
    if j is None:
        problems.append(f'{m} {run}: listed record {key} is not a planned job')
        continue
    rs = [r for r in L.get((m, run), []) if r['key'] == key and r.get('status') == 'ok']
    if len(rs) != 1 or not C.out_path(m, key).exists():
        problems.append(f'{m} {run}: {key} has {len(rs)} ok records, not one ok record with an output')
        continue
    r, bad = rs[0], []
    if r['n'] != j['n']:
        bad.append('level differs from the plan')
    d = C.inputs_at(j['sysid'], j['ci'], j['sys_seed'], j['n'])
    if C.sha(d[j['cond']]) != r['input_sha']:
        bad.append('input hash differs')
    meta = C.load(m, key)['meta']
    if meta.get('key') != key or meta.get('input_sha') != r['input_sha']:
        bad.append('output metadata differs from the record')
    if m == 'sea' and (r.get('seed') != j['seed'] or r.get('layout_ok') is not True or r.get('auc_ok') is False):
        bad.append('SEA seed or adapter check')
    if j['role'] == 'rerun' and not arrays_equal(np.load(C.out_path(m, j['of']), allow_pickle=False),
                                                 np.load(C.out_path(m, key), allow_pickle=False)):
        bad.append(f"rerun differs from {j['of']}")
    if bad:
        problems.append(f'{m} {run}: {key}: ' + '; '.join(bad))
        continue
    verified.append(dict(model=m, run=run, key=key, n=j['n'], cond=j['cond'], role=j['role'], input_sha=r['input_sha']))
    extra_ok[f'{m}_{run}'] += 1

# ---------------------------------------------------------------- c. one new session per listed record
hf = C.OUT9 / 'pn9_run_header.json'
hdrs = json.loads(hf.read_text()) if hf.exists() else []
for (m, run), k in sorted(Counter(s[:2] for s in A).items()):
    st = [h for h in hdrs if h['label'] == f'pn9_start_{m}_{run}']
    en = [h for h in hdrs if h['label'] == f'pn9_end_{m}_{run}']
    n_ok = sum(1 for h in st if h['ok'])
    if n_ok != 1 + k:
        problems.append(f'{m} {run}: {n_ok} successful start headers for {k} listed records (expected {1 + k})')
    if not st or not st[-1]['ok'] or not en or not en[-1]['ok'] or en[-1]['time_unix'] <= st[-1]['time_unix']:
        problems.append(f'{m} {run}: last start or end header missing, failed or out of order')

# ---------------------------------------------------------------- d. frozen problems = those the listed records cause
exp = []
for m, run in sorted({s[:2] for s in A}):
    recs = L.get((m, run), [])
    exp.append(f"{m} {run}: non-ok records {[r['key'] for r in recs if r.get('status') != 'ok'][:5]}")
    for key in sorted({s[2] for s in A if s[:2] == (m, run)}):
        exp.append(f"{m} {run}: {key} has {sum(1 for r in recs if r['key'] == key)} records or no output")
if frozen.get('n_problems') != len(fp):
    problems.append('the frozen check truncated its list of problems')
if Counter(fp) != Counter(exp):
    problems.append(f'frozen-check problems not explained by the listed records: {sorted((Counter(fp) - Counter(exp)).elements())[:20]}; '
                    f'expected but absent: {sorted((Counter(exp) - Counter(fp)).elements())[:20]}')
summary = {k: dict(v, ok_with_listed=v['ok'] + extra_ok.get(k, 0)) for k, v in frozen.get('summary', {}).items()}
for k, v in summary.items():
    if v['ok_with_listed'] != v['planned']:
        problems.append(f"{k}: {v['ok_with_listed']} of {v['planned']} planned jobs verified")

# ---------------------------------------------------------------- 3. result
res = dict(ok=not problems, amendment='PN9 amendments 1 and 2 (amendment_2/PN9_amendment2_vi.md)',
           accepted_files=[STOPS.name, ERRORS.name],
           listed_records=[dict(model=a, run=b, key=c, status=s, time_s=t) for a, b, c, s, t in A], verified_jobs=verified,
           frozen=dict(file=FROZENF.name, exit_code=code, ok=frozen.get('ok'), n_problems=frozen.get('n_problems'), problems=fp),
           summary=summary, problems=problems)
OUTF.write_text(json.dumps(res, indent=1))
print(json.dumps(dict(ok=res['ok'], n_problems=len(problems), problems=problems[:10], verified_jobs=len(verified),
                      frozen_ok=frozen.get('ok'), frozen_n_problems=frozen.get('n_problems')), indent=1))
sys.exit(0 if res['ok'] else 1)
