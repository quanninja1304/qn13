"""Test of completeness9b.py (P-N9 amendment 2) on synthetic logs and outputs with redirected paths, as part_completeness
of selftest9.py and test_completeness9a.py: fake inputs, no P-N9 output is read. Cases that must pass: no listed record;
the real situation (one GES R1 budget stop and one SEA R3 timeout); one SEA R3 timeout; two SEA R3 timeouts. Every other
case is an injected fault that must be caught. Runs at idle priority. Writes the synthetic data under the scratch folder
given as argv[1] and the result to test_completeness9b.json next to this file.
usage (Study 1 model environment): python -I test_completeness9b.py <scratch dir>
"""
import copy
import ctypes
import json
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PN9 = HERE.parents[2] / 'artifacts' / 'n9_runs' / 'pn9'
C9B = HERE / 'completeness9b.py'
sys.path.insert(0, str(PN9))
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)   # IDLE, inherited by children
BASE = 990000

if len(sys.argv) > 2 and sys.argv[1] == '--drive':
    cfg = json.loads(Path(sys.argv[2]).read_text())
    import numpy as np
    import common9 as C
    tmp = Path(cfg['tmp'])
    C.OUT9, C.WORK9, C.RUNS9, C.REPORT = tmp / 'pn9_out', tmp / 'pn9_work', tmp, tmp / 'report'
    C.SETS9['PN9'] = dict(base=BASE, reps=15, off=0)

    def _fake(sysid, ci, seed, n):
        dT = C.CELLS[ci][0]
        rng = np.random.default_rng([seed, n])
        return dict(k0=rng.standard_normal((4, dT)).astype(np.float32),
                    A20=rng.standard_normal((4, dT + C.K)).astype(np.float32), g=np.zeros((dT, dT), np.int8), dT=dT,
                    seed_used=seed, rejected=[])
    C.inputs_at = _fake
    sys.argv = [str(C9B), cfg['stops'], cfg['errors']]
    runpy.run_path(str(C9B), run_name='__main__')
    sys.exit(0)

import numpy as np
import common9 as C

TMP = Path(sys.argv[1]) / 'c9b'
if TMP.exists():
    shutil.rmtree(TMP)
OUT = TMP / 'pn9_out'
(TMP / 'report' / 'checks').mkdir(parents=True)
OUT.mkdir(parents=True)


def fake_sha(seed, ci, n, cond):
    rng = np.random.default_rng([seed, n])
    k0 = rng.standard_normal((4, C.CELLS[ci][0])).astype(np.float32)
    a20 = rng.standard_normal((4, C.CELLS[ci][0] + C.K)).astype(np.float32)
    return C.sha(k0 if cond == 'k0' else a20)


def write(model, key, rec, **arrays):
    f = OUT / model / f'{key}.npz'
    f.parent.mkdir(parents=True, exist_ok=True)
    C.save_npz(f, meta=np.array(json.dumps(rec)), **arrays)


C.SETS9['PN9'] = dict(base=BASE, reps=15, off=0)
hdr, logs, t = [], {}, 0
for m in C.ALL:
    for run in (('R1', 'R3') if m in C.CLASSICAL else tuple(C.RUN_CELLS)):
        hdr.append(dict(label=f'pn9_start_{m}_{run}', ok=True, time_unix=t))
        recs = []
        for j in C.run_jobs(m, run):
            rec = dict(j)
            rec.update(status='ok', input_sha=fake_sha(j['sys_seed'], j['ci'], j['n'], j['cond']))
            if m == 'sea':
                rec.update(layout_ok=True, auc_ok=True)
            src = j.get('of', j['key'])
            val = np.frombuffer(src.encode()[:16].ljust(16), np.uint8).reshape(4, 4)
            write(m, j['key'], rec, **({'prob': val} if m == 'sea' else {'probs': val}))
            recs.append(rec)
        logs[(m, run)] = recs
        hdr.append(dict(label=f'pn9_end_{m}_{run}', ok=True, time_unix=t + 10))
        t += 100
print('synthetic data written', sum(len(v) for v in logs.values()), flush=True)


def save(L, H, stops, errors):
    (OUT / 'pn9_run_header.json').write_text(json.dumps(H))
    for (m, run), recs in L.items():
        (OUT / f'log_{m}_{run}.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in recs), encoding='utf-8')
    (TMP / 'stops.json').write_text(json.dumps(dict(stops=stops)))
    (TMP / 'errors.json').write_text(json.dumps(dict(records=errors)))


def drive():
    cfgf = TMP / 'cfg.json'
    cfgf.write_text(json.dumps(dict(tmp=str(TMP), stops=str(TMP / 'stops.json'), errors=str(TMP / 'errors.json'))))
    p = subprocess.run([sys.executable, '-I', __file__, '--drive', str(cfgf)], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    f = TMP / 'report' / 'checks' / 'pn9_completeness.json'
    J = json.loads(f.read_text()) if f.exists() else dict(ok=None, problems=[p.stderr[-800:]])
    fz = TMP / 'report' / 'checks' / 'pn9_completeness_frozen.json'
    FZ = json.loads(fz.read_text()) if fz.exists() else dict(ok=None)
    return p.returncode, J, FZ


def new_header(H, m, run):
    i = max(k for k, h in enumerate(H) if h['label'] == f'pn9_start_{m}_{run}')
    H.insert(i + 1, dict(label=f'pn9_start_{m}_{run}', ok=True, time_unix=H[i]['time_unix'] + 1))


def stop_at(L, H, m, run, idx, elapsed, extra_header=True):
    """A budget_stop record before the record at position idx, as in the real GES R1 log, and a new start header."""
    k = L[(m, run)][idx]['key']
    L[(m, run)].insert(idx, dict(key=k, status='budget_stop', elapsed_s=elapsed))
    if extra_header:
        new_header(H, m, run)
    return dict(model=m, run=run, key=k, elapsed_s=elapsed)


def error_at(L, H, m, run, idx, wall, extra_header=True, keep_ok=True, status='error: exit timeout'):
    """An error record before the record at position idx, as in the real SEA R3 log, and a new start header."""
    ok = L[(m, run)][idx]
    err = {a: v for a, v in ok.items() if a not in ('status', 'layout_ok', 'auc_ok')}
    err.update(status=status, wall_total_s=wall)
    L[(m, run)].insert(idx, err)
    if not keep_ok:
        L[(m, run)].pop(idx + 1)
    if extra_header:
        new_header(H, m, run)
    return dict(model=m, run=run, key=ok['key'], status=status, wall_total_s=wall)


results = {}


def case(name, mutate, want_ok, want_text=None):
    L, H = copy.deepcopy(logs), copy.deepcopy(hdr)
    stops, errors, undo = mutate(L, H)
    save(L, H, stops, errors)
    rc, J, FZ = drive()
    probs = J.get('problems', [])
    good = (J.get('ok') is want_ok) and (rc == (0 if want_ok else 1)) and (want_text is None or any(want_text in x for x in probs))
    if undo:
        undo()
    results[name] = dict(pass_=good, ok=J.get('ok'), rc=rc, frozen_ok=FZ.get('ok'), n_problems=len(probs), first=probs[:2])
    print(('PASS ' if good else 'FAIL ') + name, json.dumps(results[name])[:400], flush=True)


g1 = next(i for i, r in enumerate(logs[('ges', 'R1')]) if r['role'] == 'main' and r['n'] == 4000 and r['cond'] == 'k0')
s3 = [i for i, r in enumerate(logs[('sea', 'R3')]) if r['role'] == 'main' and r['cond'] == 'A20' and r['n'] == 5000]
s3_rerun = next(i for i, r in enumerate(logs[('sea', 'R3')]) if r['role'] == 'rerun')
s4 = next(i for i, r in enumerate(logs[('sea', 'R4')]) if r['role'] == 'main' and r['cond'] == 'A20')
fc = next(i for i, r in enumerate(logs[('foundcause', 'R3')]) if r['role'] == 'main')


def real(L, H):                    # one GES R1 budget stop and one SEA R3 timeout, as in the real runs
    return [stop_at(L, H, 'ges', 'R1', g1, 373.3)], [error_at(L, H, 'sea', 'R3', s3[20], 23409.8)], None


def sea_only(L, H):
    return [], [error_at(L, H, 'sea', 'R3', s3[20], 23409.8)], None


def sea_two(L, H):
    a = error_at(L, H, 'sea', 'R3', s3[3], 3601.0)
    b = error_at(L, H, 'sea', 'R3', s3[25] + 1, 5000.5)
    return [], [a, b], None


def sea_rerun_job(L, H):
    return [], [error_at(L, H, 'sea', 'R3', s3_rerun, 4000.0)], None


def unlisted(L, H):
    error_at(L, H, 'sea', 'R3', s3[20], 23409.8)
    return [], [], None


def absent(L, H):
    return [], [dict(model='sea', run='R3', key=L[('sea', 'R3')][s3[20]]['key'], status='error: exit timeout',
                     wall_total_s=23409.8)], None


def other_wall(L, H):
    e = error_at(L, H, 'sea', 'R3', s3[20], 23409.8)
    return [], [dict(e, wall_total_s=23409.9)], None


def no_header(L, H):
    return [], [error_at(L, H, 'sea', 'R3', s3[20], 23409.8, extra_header=False)], None


def wrong_seed(L, H):
    e = error_at(L, H, 'sea', 'R3', s3[20], 23409.8)
    L[('sea', 'R3')][s3[20] + 1]['seed'] += 1
    return [], [e], None


def bad_layout(L, H):
    e = error_at(L, H, 'sea', 'R3', s3[20], 23409.8)
    L[('sea', 'R3')][s3[20] + 1]['layout_ok'] = False
    return [], [e], None


def no_ok(L, H):
    return [], [error_at(L, H, 'sea', 'R3', s3[20], 23409.8, keep_ok=False)], None


def fc_error(L, H):
    return [], [error_at(L, H, 'foundcause', 'R3', fc, 5000.0)], None


def other_status(L, H):
    return [], [error_at(L, H, 'sea', 'R3', s3[20], 23409.8, status='error: exit 1')], None


def sea_r4(L, H):
    return [], [error_at(L, H, 'sea', 'R4', s4, 4000.0)], None


def sea_budget_stop(L, H):
    return [stop_at(L, H, 'sea', 'R3', s3[20], 30000.0)], [], None


def ges_unlisted(L, H):
    stop_at(L, H, 'ges', 'R1', g1, 373.3)
    return [], [error_at(L, H, 'sea', 'R3', s3[20], 23409.8)], None


def wrong_hash(L, H):
    e = error_at(L, H, 'sea', 'R3', s3[20], 23409.8)
    L[('sea', 'R3')][s3[20] + 1]['input_sha'] = '0' * 16
    return [], [e], None


def rerun_differs(L, H):
    e = error_at(L, H, 'sea', 'R3', s3_rerun, 4000.0)
    r = L[('sea', 'R3')][s3_rerun + 1]
    f = OUT / 'sea' / f"{r['key']}.npz"
    keep = f.read_bytes()
    C.save_npz(f, meta=np.array(json.dumps(r)), prob=np.zeros((4, 4), np.uint8))
    return [], [e], lambda: f.write_bytes(keep)


def missing_output(L, H):
    s, e, _ = real(L, H)
    f = OUT / 'avici' / f"{L[('avici', 'R2')][3]['key']}.npz"
    g = f.with_suffix('.bak')
    f.rename(g)
    return s, e, lambda: g.rename(f)


def failed_end(L, H):
    s, e, _ = real(L, H)
    next(h for h in reversed(H) if h['label'] == 'pn9_end_sea_R3')['ok'] = False
    return s, e, None


case('complete data, nothing listed', lambda L, H: ([], [], None), True)
case('real situation: GES R1 stop and SEA R3 timeout', real, True)
case('one SEA R3 timeout', sea_only, True)
case('two SEA R3 timeouts', sea_two, True)
case('SEA R3 timeout of a rerun job, rerun identical', sea_rerun_job, True)
case('unlisted SEA timeout', unlisted, False, 'differ from the listed')
case('listed timeout absent from the logs', absent, False, 'differ from the listed')
case('listed timeout with another wall_total_s', other_wall, False, 'differ from the listed')
case('no new start header after the timeout', no_header, False, 'successful start headers')
case('SEA seed of the later record differs', wrong_seed, False, 'SEA seed or adapter check')
case('SEA adapter check of the later record fails', bad_layout, False, 'SEA seed or adapter check')
case('timeout without a later ok record', no_ok, False, 'not one ok record')
case('FoundCause error listed', fc_error, False, 'outside the scope')
case('SEA error with another status listed', other_status, False, 'outside the scope')
case('SEA R4 timeout listed', sea_r4, False, 'outside the scope')
case('SEA budget stop listed', sea_budget_stop, False, 'outside the scope')
case('GES stop unlisted while the SEA timeout is listed', ges_unlisted, False, 'differ from the listed')
case('wrong input hash on the job after the timeout', wrong_hash, False, 'input hash differs')
case('rerun after a timeout differs from the original', rerun_differs, False, 'rerun differs')
case('listed records plus an unrelated missing output', missing_output, False, 'not explained')
case('listed records plus a failed end header', failed_end, False, 'not explained')
ok = all(v['pass_'] for v in results.values())
print('ALL PASS' if ok else 'SOME FAIL', sum(v['pass_'] for v in results.values()), 'of', len(results))
(HERE / 'test_completeness9b.json').write_bytes((json.dumps(dict(ok=ok, cases=results), indent=1) + '\n').encode('utf-8'))
shutil.rmtree(TMP)
sys.exit(0 if ok else 1)
