"""P-N2 EXP2 completeness check, run before reading (user instruction 21/11; not part of the frozen pipeline).

Checks: 1440 outputs (AVICI 640, CDFM 640, PC 80, GES 80); no failed job in any EXP2 log; input SHA of every output
matches the regenerated input; screening variants complete (1120 rows); the freeze gate wrote ok=true at exp2_start and
exp2_end with the same freeze commit and SHA256SUMS hash.
usage: exp2_completeness.py  ->  pn2_out/exp2_completeness.json (exit 1 if anything fails)
"""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pn2'))
from common2 import *

SYS = systems2('EXP2')
bad, rep = [], {}
expect = {('avici', 'plain'): 320, ('avici', 'R'): 320, ('cdfm', 'plain'): 320, ('cdfm', 'R'): 320}
files = {}
for (m, arm), n in expect.items():
    f = sorted((OUT2 / m).glob(f'EXP2-*__{arm}.npz'))
    files[(m, arm)] = f
    rep[f'{m}_{arm}'] = len(f)
    if len(f) != n:
        bad.append(f'{m} {arm}: {len(f)} outputs, expected {n}')
for alg in ('pc', 'ges'):
    f = sorted((OUT2 / alg).glob('EXP2-*__plain.npz'))
    files[(alg, 'plain')] = f
    rep[alg] = len(f)
    if len(f) != 80:
        bad.append(f'{alg}: {len(f)} outputs, expected 80')
rep['total_outputs'] = sum(len(v) for v in files.values())
errs = 0
for lp in [OUT2 / m / f'log_EXP2_{arm}.jsonl' for m in ('avici', 'cdfm') for arm in ('plain', 'R')] + \
          [OUT2 / alg / 'log_EXP2.jsonl' for alg in ('pc', 'ges')]:
    if not lp.exists():
        bad.append(f'missing log {lp.name} in {lp.parent.name}')
        continue
    e = [json.loads(l) for l in lp.read_text(encoding='utf-8').splitlines() if l.strip()]
    n_err = sum(1 for r in e if r['status'] != 'ok')
    errs += n_err
    if n_err:
        bad.append(f'{lp.parent.name}/{lp.name}: {n_err} failed jobs')
rep['failed_jobs_in_logs'] = errs
# input SHA of every output
sha_of = {}
for sid, ci, seed in SYS:
    for cond in CONDS:
        X, _, _ = assemble2(sid, ci, seed, cond)
        sha_of[(sid, cond)] = sha(X)
mism = 0
for (m, arm), fl in files.items():
    for f in fl:
        sid, cond, _ = f.stem.split('__')
        meta = json.loads(str(np.load(f, allow_pickle=False)['meta']))
        if meta['input_sha'] != sha_of[(sid, cond)]:
            mism += 1
            bad.append(f'input sha mismatch {m} {f.name}')
rep['input_sha_mismatches'] = mism
sv = OUT2 / 'exp2_screen_variants.json'
if sv.exists():
    rows = json.loads(sv.read_text())['rows']
    rep['screen_variant_rows'] = len(rows)
    if len(rows) != 1120:
        bad.append(f'screen variants: {len(rows)} rows, expected 1120')
else:
    bad.append('exp2_screen_variants.json missing')
hdr = json.loads((OUT2 / 'exp2_run_header.json').read_text())
last = {h['label']: h for h in hdr if h['label'] in ('exp2_start', 'exp2_end')}
for lab in ('exp2_start', 'exp2_end'):
    h = last.get(lab)
    if h is None or not h['ok']:
        bad.append(f'freeze gate {lab} missing or not ok')
if len(last) == 2 and (last['exp2_start']['freeze_commit'] != last['exp2_end']['freeze_commit'] or
                       last['exp2_start']['sha256sums_sha'] != last['exp2_end']['sha256sums_sha']):
    bad.append('freeze commit or SHA256SUMS hash differs between start and end')
rep['freeze_gate'] = {lab: dict(ok=h['ok'], freeze_commit=h['freeze_commit'], time_local=h['time_local']) for lab, h in last.items()}
rep['ok'] = not bad
rep['problems'] = bad
(OUT2 / 'exp2_completeness.json').write_text(json.dumps(rep, indent=1))
print(json.dumps(rep, indent=1))
sys.exit(1 if bad else 0)
