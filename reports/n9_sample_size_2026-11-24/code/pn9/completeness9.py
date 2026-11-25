"""P-N9 / Study 8 completeness check before reading (rules PN9 v1 §7). No metric is computed.

Checks, for every model and main run:
  - every planned job has an output and exactly one terminal record, 'ok'; no 'error' or 'budget_stop' record;
  - the level n and, for SEA, the seed in each record match the plan;
  - input hashes: every input is rebuilt here and its SHA-256 must equal the runner's record;
  - reruns at the end of each run: output identical to the original, array by array;
  - SEA: layout_ok on every output and auc_ok never false;
  - freeze headers: a successful start and end header for each run (verify_freeze9.py).
Writes reports/n9_sample_size_2026-11-24/checks/pn9_completeness.json; exit 0 only if everything passes.
usage (Study 1 model environment): python -I completeness9.py
"""
import sys
import json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common9 import *

CHECKS = REPORT / 'checks'
RUNS = {m: (('R1', 'R3') if m in CLASSICAL else tuple(RUN_CELLS)) for m in ALL}
problems = []
summary = {}


def logs(model, run):
    f = OUT9 / f'log_{model}_{run}.jsonl'
    return [json.loads(l) for l in f.read_text(encoding='utf-8').splitlines() if l.strip()] if f.exists() else []


def arrays_equal(z1, z2, skip=('meta', 'perm')):
    k1, k2 = set(z1.files) - set(skip), set(z2.files) - set(skip)
    return k1 == k2 and all(np.array_equal(z1[k], z2[k]) for k in k1)


hdr_file = OUT9 / 'pn9_run_header.json'
hdrs = json.loads(hdr_file.read_text()) if hdr_file.exists() else []
built = {}
for m in ALL:
    for run in RUNS[m]:
        planned = run_jobs(m, run)
        recs = logs(m, run)
        by_key = {}
        for r in recs:
            by_key.setdefault(r['key'], []).append(r)
        bad_status = [r['key'] for r in recs if r.get('status') != 'ok']
        if bad_status:
            problems.append(f'{m} {run}: non-ok records {bad_status[:5]}')
        n_ok = 0
        for j in planned:
            rs = by_key.get(j['key'], [])
            if len(rs) != 1 or rs[0].get('status') != 'ok' or not out_path(m, j['key']).exists():
                problems.append(f"{m} {run}: {j['key']} has {len(rs)} records or no output")
                continue
            r = rs[0]
            if r['n'] != j['n'] or (m == 'sea' and r['seed'] != j['seed']):
                problems.append(f"{m} {run}: {j['key']} level or seed differs from the plan")
            k = (j['sysid'], j['n'], j['cond'])
            if k not in built:
                d = inputs_at(j['sysid'], j['ci'], j['sys_seed'], j['n'])
                built[(j['sysid'], j['n'], 'k0')], built[(j['sysid'], j['n'], 'A20')] = sha(d['k0']), sha(d['A20'])
            if built[k] != r['input_sha']:
                problems.append(f"{m} {run}: {j['key']} input hash differs")
            if m == 'sea' and (r.get('layout_ok') is not True or r.get('auc_ok') is False):
                problems.append(f"sea {run}: {j['key']} adapter check")
            if j['role'] == 'rerun':
                z1, z2 = np.load(out_path(m, j['of']), allow_pickle=False), np.load(out_path(m, j['key']), allow_pickle=False)
                if not arrays_equal(z1, z2):
                    problems.append(f"{m} {run}: rerun {j['key']} differs from {j['of']}")
            n_ok += 1
        extra = set(by_key) - {j['key'] for j in planned}
        if extra:
            problems.append(f'{m} {run}: records of unplanned jobs {sorted(extra)[:5]}')
        start = [h for h in hdrs if h['label'] == f'pn9_start_{m}_{run}']
        end = [h for h in hdrs if h['label'] == f'pn9_end_{m}_{run}']
        if not start or not start[-1]['ok'] or not end or not end[-1]['ok']:
            problems.append(f'{m} {run}: missing or failed start/end freeze header')
        summary[f'{m}_{run}'] = dict(planned=len(planned), ok=n_ok)
res = dict(ok=not problems, summary=summary, problems=problems[:200], n_problems=len(problems))
CHECKS.mkdir(parents=True, exist_ok=True)
(CHECKS / 'pn9_completeness.json').write_text(json.dumps(res, indent=1))
print(json.dumps(dict(ok=res['ok'], n_problems=len(problems), summary=summary), indent=1))
sys.exit(0 if res['ok'] else 1)
