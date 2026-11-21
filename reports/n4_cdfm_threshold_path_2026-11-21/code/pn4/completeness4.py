"""P-N4 completeness check, required before reading (rules PN4 v1 §7).

Checks: 400 CDFM outputs (80 systems x 5 inputs); no failed job in the PN4 log; the input SHA of every output matches the
regenerated input; the target block is bitwise identical across the five inputs of each system; the freeze gate wrote
ok = true at pn4_start and pn4_end with the same freeze commit, SHA256SUMS hash and dependency hash; the copied selector
reproduces every stored threshold within 1e-12 (gate G3).
usage: completeness4.py [--set PN4|DEV4]  ->  pn4_out/pn4_completeness.json (exit 1 if anything fails)
  DEV4 only tests this script before the freeze (output dev4_completeness_test.json; its freeze-gate items fail by design).
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common4 import *
from selector4 import thr as thr_copy

ap = argparse.ArgumentParser(); ap.add_argument('--set', default='PN4', choices=['PN4', 'DEV4']); a = ap.parse_args()
SET = a.set
n_expected = 5 * len(systems4(SET))
bad, rep = [], dict(set=SET)
files = sorted((OUT4 / 'cdfm').glob(f'{SET}-*.npz'))
rep['n_outputs'] = len(files)
if len(files) != n_expected:
    bad.append(f'{len(files)} outputs, expected {n_expected}')
lp = OUT4 / 'cdfm' / f'log_{SET}.jsonl'
if not lp.exists():
    bad.append(f'missing log_{SET}.jsonl')
else:
    e = [json.loads(l) for l in lp.read_text(encoding='utf-8').splitlines() if l.strip()]
    rep['log_lines'] = len(e)
    rep['failed_in_log'] = sum(1 for r in e if r['status'] != 'ok')
    if rep['failed_in_log']:
        bad.append(f"{rep['failed_in_log']} failed jobs in log")
mism, tgt_bad, worst = 0, 0, 0.0
for sid, ci, seed in systems4(SET):
    tshas = set()
    for cond in conds4(ci):
        f = OUT4 / 'cdfm' / f'{key4(sid, cond)}.npz'
        if not f.exists():
            bad.append(f'missing {f.name}')
            continue
        X, t, _ = assemble4(sid, ci, seed, cond)          # asserts the target block is bitwise identical to k0
        z = np.load(f, allow_pickle=False)
        meta = json.loads(str(z['meta']))
        if meta['input_sha'] != sha(X):
            mism += 1; bad.append(f'input sha mismatch {f.name}')
        tshas.add(meta['target_sha'])
        worst = max(worst, abs(thr_copy(np.asarray(z['probs'], float)) - float(z['threshold'])))
    if len(tshas) != 1:
        tgt_bad += 1; bad.append(f'target_sha differs across inputs of {sid}')
rep.update(input_sha_mismatches=mism, systems_with_target_sha_mismatch=tgt_bad, selector_reproduction_max_abs=worst)
if worst > 1e-12:
    bad.append(f'selector reproduction {worst:.3g} > 1e-12')
hp = OUT4 / 'pn4_run_header.json'
hdr = json.loads(hp.read_text()) if hp.exists() else []
last = {h['label']: h for h in hdr if h['label'] in ('pn4_start', 'pn4_end')}
for lab in ('pn4_start', 'pn4_end'):
    if lab not in last or not last[lab]['ok']:
        bad.append(f'freeze gate {lab} missing or not ok')
if len(last) == 2 and any(last['pn4_start'][q] != last['pn4_end'][q] for q in ('freeze_commit', 'sha256sums_sha', 'deps_sha')):
    bad.append('freeze commit, SHA256SUMS hash or dependency hash differs between start and end')
rep['freeze_gate'] = {lab: dict(ok=h['ok'], freeze_commit=h['freeze_commit'], time_local=h['time_local']) for lab, h in last.items()}
rep['ok'] = not bad
rep['problems'] = bad
(OUT4 / ('pn4_completeness.json' if SET == 'PN4' else 'dev4_completeness_test.json')).write_text(json.dumps(rep, indent=1))
print(json.dumps(rep, indent=1))
sys.exit(1 if bad else 0)
