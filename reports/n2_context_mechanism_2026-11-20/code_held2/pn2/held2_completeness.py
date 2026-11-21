"""P-N2 HELD2 completeness check, required before reading (rules held2 v1 §6).

Checks: 1440 outputs (per model 360 plain + 360 R); no failed job in the HELD2 logs; the input SHA of every output matches
the regenerated input; the freeze gate wrote ok=true at held2_start and held2_end with the same freeze commit and hash.
usage: held2_completeness.py  ->  pn2_out/held2_completeness.json (exit 1 if anything fails)
"""
import sys, json
import numpy as np
from held2 import *

bad, rep, files = [], {}, {}
for m in ('avici', 'cdfm'):
    for arm in ('plain', 'R'):
        f = sorted((OUT2 / m).glob(f'HELD2-*__{arm}.npz'))
        files[(m, arm)] = f
        rep[f'{m}_{arm}'] = len(f)
        if len(f) != 360:
            bad.append(f'{m} {arm}: {len(f)} outputs, expected 360')
        lp = OUT2 / m / f'log_HELD2_{arm}.jsonl'
        if not lp.exists():
            bad.append(f'missing log {m}/{lp.name}')
            continue
        e = [json.loads(l) for l in lp.read_text(encoding='utf-8').splitlines() if l.strip()]
        n_err = sum(1 for r in e if r['status'] != 'ok')
        rep[f'{m}_{arm}_failed_in_log'] = n_err
        if n_err:
            bad.append(f'{m}/{lp.name}: {n_err} failed jobs')
rep['total_outputs'] = sum(len(v) for v in files.values())
sha_of = {}
for sid, ci, seed in systems_held2():
    for cond in conds_held2(ci):
        X, _, _ = assemble2(sid, ci, seed, cond)
        sha_of[(sid, cond)] = sha(X)
mism = 0
for (m, arm), fl in files.items():
    for f in fl:
        sid, cond, _ = f.stem.split('__')
        meta = json.loads(str(np.load(f, allow_pickle=False)['meta']))
        if (sid, cond) not in sha_of or meta['input_sha'] != sha_of[(sid, cond)]:
            mism += 1
            bad.append(f'input sha mismatch {m} {f.name}')
rep['input_sha_mismatches'] = mism
hp = OUT2 / 'held2_run_header.json'
hdr = json.loads(hp.read_text()) if hp.exists() else []
last = {h['label']: h for h in hdr if h['label'] in ('held2_start', 'held2_end')}
for lab in ('held2_start', 'held2_end'):
    if lab not in last or not last[lab]['ok']:
        bad.append(f'freeze gate {lab} missing or not ok')
if len(last) == 2 and (last['held2_start']['freeze_commit'] != last['held2_end']['freeze_commit'] or
                       last['held2_start']['sha256sums_sha'] != last['held2_end']['sha256sums_sha']):
    bad.append('freeze commit or SHA256SUMS hash differs between start and end')
rep['freeze_gate'] = {lab: dict(ok=h['ok'], freeze_commit=h['freeze_commit'], time_local=h['time_local']) for lab, h in last.items()}
rep['ok'] = not bad
rep['problems'] = bad
(OUT2 / 'held2_completeness.json').write_text(json.dumps(rep, indent=1))
print(json.dumps(rep, indent=1))
sys.exit(1 if bad else 0)
