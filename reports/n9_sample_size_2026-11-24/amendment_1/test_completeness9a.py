"""Test of completeness9a.py (P-N9 amendment 1) on synthetic logs and outputs with redirected paths, as part_completeness of
selftest9.py: fake inputs, no P-N9 output is read. 15 cases: 4 must pass (no stop; one listed GES R1 stop; two listed GES R3
stops; a listed stop of a rerun job) and 11 injected faults must be caught. Runs at idle priority. Writes the synthetic data
under the scratch folder given as argv[1] and the result to test_completeness9a.json next to this file.
usage (Study 1 model environment): python -I test_completeness9a.py <scratch dir>
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
C9A = HERE / 'completeness9a.py'
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
    sys.argv = [str(C9A), cfg['allowed']]
    runpy.run_path(str(C9A), run_name='__main__')
    sys.exit(0)

import numpy as np
import common9 as C

TMP = Path(sys.argv[1]) / 'c9a'
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


def save(L, H, allowed):
    (OUT / 'pn9_run_header.json').write_text(json.dumps(H))
    for (m, run), recs in L.items():
        (OUT / f'log_{m}_{run}.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in recs), encoding='utf-8')
    (TMP / 'allowed.json').write_text(json.dumps(dict(stops=allowed)))


def drive():
    cfgf = TMP / 'cfg.json'
    cfgf.write_text(json.dumps(dict(tmp=str(TMP), allowed=str(TMP / 'allowed.json'))))
    p = subprocess.run([sys.executable, '-I', __file__, '--drive', str(cfgf)], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    f = TMP / 'report' / 'checks' / 'pn9_completeness.json'
    J = json.loads(f.read_text()) if f.exists() else dict(ok=None, problems=[p.stderr[-800:]])
    fz = TMP / 'report' / 'checks' / 'pn9_completeness_frozen.json'
    FZ = json.loads(fz.read_text()) if fz.exists() else dict(ok=None)
    return p.returncode, J, FZ


def stop_at(L, H, m, run, idx, elapsed, extra_header=True, keep_ok=True):
    """Insert a budget_stop record before the record at position idx, as in the real GES R1 log, and a new start header."""
    key = L[(m, run)][idx]['key']
    L[(m, run)].insert(idx, dict(key=key, status='budget_stop', elapsed_s=elapsed))
    if not keep_ok:
        L[(m, run)].pop(idx + 1)
    if extra_header:
        i = max(k for k, h in enumerate(H) if h['label'] == f'pn9_start_{m}_{run}')
        H.insert(i + 1, dict(label=f'pn9_start_{m}_{run}', ok=True, time_unix=H[i]['time_unix'] + 1))
    return dict(model=m, run=run, key=key, elapsed_s=elapsed)


results = {}


def case(name, mutate, want_ok, want_text=None):
    L, H = copy.deepcopy(logs), copy.deepcopy(hdr)
    allowed, undo = mutate(L, H)
    save(L, H, allowed)
    rc, J, FZ = drive()
    probs = J.get('problems', [])
    good = (J.get('ok') is want_ok) and (rc == (0 if want_ok else 1)) and (want_text is None or any(want_text in x for x in probs))
    if undo:
        undo()
    results[name] = dict(pass_=good, ok=J.get('ok'), rc=rc, frozen_ok=FZ.get('ok'), n_problems=len(probs), first=probs[:2])
    print(('PASS ' if good else 'FAIL ') + name, json.dumps(results[name])[:400], flush=True)


GES_R1 = len(logs[('ges', 'R1')])
idx_main = next(i for i, r in enumerate(logs[('ges', 'R1')]) if r['role'] == 'main' and r['n'] == 4000 and r['cond'] == 'k0')
idx_rerun = next(i for i, r in enumerate(logs[('ges', 'R1')]) if r['role'] == 'rerun')


def none(L, H):
    return [], None


def one_stop(L, H):
    return [stop_at(L, H, 'ges', 'R1', idx_main, 373.3)], None


def two_stops_r3(L, H):
    a = stop_at(L, H, 'ges', 'R3', 100, 1801.2)
    b = stop_at(L, H, 'ges', 'R3', 300, 1800.4)
    return [a, b], None


def unlisted(L, H):
    stop_at(L, H, 'ges', 'R1', idx_main, 373.3)
    return [], None


def listed_absent(L, H):
    return [dict(model='ges', run='R1', key=L[('ges', 'R1')][idx_main]['key'], elapsed_s=373.3)], None


def wrong_elapsed(L, H):
    s = stop_at(L, H, 'ges', 'R1', idx_main, 373.3)
    return [dict(s, elapsed_s=373.4)], None


def no_new_header(L, H):
    return [stop_at(L, H, 'ges', 'R1', idx_main, 373.3, extra_header=False)], None


def extra_error(L, H):
    s = stop_at(L, H, 'ges', 'R1', idx_main, 373.3)
    L[('ges', 'R1')].append(dict(key=L[('ges', 'R1')][5]['key'], status='error: x'))
    return [s], None


def stop_without_ok(L, H):
    return [stop_at(L, H, 'ges', 'R1', idx_main, 373.3, keep_ok=False)], None


def sea_stop(L, H):
    return [stop_at(L, H, 'sea', 'R2', 50, 22000.0)], None


def bad_hash_after_stop(L, H):
    s = stop_at(L, H, 'ges', 'R1', idx_main, 373.3)
    L[('ges', 'R1')][idx_main + 1]['input_sha'] = '0' * 16
    return [s], None


def rerun_differs_after_stop(L, H):
    s = stop_at(L, H, 'ges', 'R1', idx_rerun, 373.3)
    r = L[('ges', 'R1')][idx_rerun + 1]
    f = OUT / 'ges' / f"{r['key']}.npz"
    keep = f.read_bytes()
    C.save_npz(f, meta=np.array(json.dumps(r)), probs=np.zeros((4, 4), np.uint8))
    return [s], lambda: f.write_bytes(keep)


def rerun_stop_ok(L, H):
    return [stop_at(L, H, 'ges', 'R1', idx_rerun, 373.3)], None


def other_problem(L, H):
    s = stop_at(L, H, 'ges', 'R1', idx_main, 373.3)
    f = OUT / 'avici' / f"{L[('avici', 'R2')][3]['key']}.npz"
    g = f.with_suffix('.bak')
    f.rename(g)
    return [s], lambda: g.rename(f)


def end_header_failed(L, H):
    s = stop_at(L, H, 'ges', 'R1', idx_main, 373.3)
    next(h for h in reversed(H) if h['label'] == 'pn9_end_ges_R1')['ok'] = False
    return [s], None


case('complete data, no stop', none, True)
case('one listed GES R1 stop', one_stop, True)
case('two listed GES R3 stops', two_stops_r3, True)
case('listed stop of a rerun job, rerun identical', rerun_stop_ok, True)
case('unlisted stop', unlisted, False, 'differ from the listed stops')
case('listed stop absent from the logs', listed_absent, False, 'differ from the listed stops')
case('listed stop with another elapsed_s', wrong_elapsed, False, 'differ from the listed stops')
case('no new start header after the stop', no_new_header, False, 'successful start headers')
case('stop plus an error record', extra_error, False, 'not explained')
case('stop without a later ok record', stop_without_ok, False, 'not one ok record')
case('stop of another model (SEA)', sea_stop, False, 'outside GES')
case('wrong input hash on the job after the stop', bad_hash_after_stop, False, 'input hash differs')
case('rerun after a stop differs from the original', rerun_differs_after_stop, False, 'rerun differs')
case('stop plus an unrelated missing output', other_problem, False, 'not explained')
case('stop plus a failed end header', end_header_failed, False, 'not explained')
ok = all(v['pass_'] for v in results.values())
print('ALL PASS' if ok else 'SOME FAIL', sum(v['pass_'] for v in results.values()), 'of', len(results))
(HERE / 'test_completeness9a.json').write_text(json.dumps(dict(ok=ok, cases=results), indent=1) + chr(10))
