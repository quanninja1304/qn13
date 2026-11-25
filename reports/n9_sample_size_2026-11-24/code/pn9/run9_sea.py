"""P-N9 / Study 8 SEA runner (rules PN9 v1 §1, §6-§8): one SEA input per fresh process, sequential, resume by key.

As the frozen Study 7 runner (n8_runs/pn8/run8.py): for each job, build the input, write data.npy / DAG.npy and a one-row
CSV, call SEA's own inference script through the frozen sea_wrapper8.py in the SEA environment (python -E -s), read the
result, check the adapter (layout of `true`; AUROC when defined) and save prob[i, j] = P(i -> j) with a metadata record.
No metric is computed here. Stops at the first failed job or failed adapter check, and at the run's budget.
usage (Study 1 model environment): python -I run9_sea.py <DEV|G2|G3|G5|R1|R2|R3|R4> [--limit N]
  G5: the zero-DAG job (output must not depend on the graph file) and the Study 7 reproduction job.
"""
import os
import sys
import json
import time
import pickle
import shutil
import subprocess
import argparse
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.name == 'nt':   # keep the system awake while this process runs; no effect on results
    import ctypes
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
ap = argparse.ArgumentParser()
ap.add_argument('mode', choices=('DEV', 'G2', 'G3', 'G5', 'R1', 'R2', 'R3', 'R4'))
ap.add_argument('--limit', type=int, default=0)
a = ap.parse_args()
import numpy as np
from sklearn.metrics import roc_auc_score
from common9 import *

(OUT9 / 'sea').mkdir(parents=True, exist_ok=True)
WORK9.mkdir(parents=True, exist_ok=True)
log = open(OUT9 / f'log_sea_{a.mode}.jsonl', 'a', encoding='utf-8')
hdr_file = OUT9 / 'pn9_run_header.json'
t_start = time.time()
budget = None
if a.mode in ('R1', 'R2', 'R3', 'R4'):   # main runs only (not REPRO)
    hdrs = [h for h in (json.loads(hdr_file.read_text()) if hdr_file.exists() else []) if h['label'] == f'pn9_start_sea_{a.mode}']
    if not hdrs or not hdrs[-1]['ok']:
        sys.exit(f'no successful start header for sea {a.mode}')
    t_start = hdrs[-1]['time_unix']
    budget = BUDGET_H['sea'][a.mode] * 3600


def build(job):
    """(X float32, G int64, X sha, d_T). Study 7 reproduction: the frozen P-N8 builder."""
    if job['role'] == 'repro8':
        X, G, xsha, dT, perm = C8.build(job)
        assert perm is None
        return X, G, xsha, dT
    d = inputs_at(job['sysid'], job['ci'], job['sys_seed'], job['n'])
    X = np.ascontiguousarray(d[job['cond']], dtype=np.float32)
    G = full_graph(d['g'], X.shape[1])
    if job.get('zero_dag'):
        G = np.zeros_like(G)
    return X, G, sha(X), d['dT']


def run_one(job):
    X, G, xsha, dT = build(job)
    D = X.shape[1]
    d = WORK9 / job['key']
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    np.save(d / 'data.npy', X)
    np.save(d / 'DAG.npy', G.astype(np.int64))
    with open(d / 'one.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['fp_data', 'fp_graph', 'fp_regime', 'split'])
        w.writerow([(d / 'data.npy').as_posix(), (d / 'DAG.npy').as_posix(), '', 'test'])
    cmd = [str(C8.SEA_PY), '-E', '-s', '-W', 'ignore', str(C8.WRAPPER), str(C8.SEA_SRC), str(d / 'one.csv'),
           str(d / 'res.pkl'), str(job['seed']), str(d / 'wrap.json')]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=str(WORK9), capture_output=True, text=True, timeout=3600)
        code, tail = p.returncode, (p.stdout + p.stderr)[-3000:]
    except subprocess.TimeoutExpired:
        code, tail = 'timeout', ''
    wall_total = time.time() - t0
    base = {k: job[k] for k in job if k not in ('key',)}
    if code != 0 or not (d / 'res.pkl').exists():
        (OUT9 / 'errors').mkdir(exist_ok=True)
        (OUT9 / 'errors' / f"{job['key']}.txt").write_text(str(tail), encoding='utf-8')
        return dict(base, key=job['key'], mode=a.mode, status=f'error: exit {code}', D=D, dT=dT, input_sha=xsha,
                    wall_total_s=round(wall_total, 1)), None
    res = pickle.load(open(d / 'res.pkl', 'rb'))
    assert list(res) == [job['key']], (list(res), job['key'])   # SEA keys results by the input folder name
    m = res[job['key']]
    prob, t_vec, p_vec = C8.unpack(m, D)
    layout_ok = bool(np.array_equal(t_vec, C8.expected_true(G)))
    auc_ok = None
    if 0 < t_vec.sum() < len(t_vec):
        auc_ok = bool(abs(roc_auc_score(t_vec, p_vec) - float(m['auc'][0])) < 1e-6)
    wrap = json.loads((d / 'wrap.json').read_text(encoding='utf-8'))
    rec = dict(base, key=job['key'], mode=a.mode, status='ok', D=D, dT=dT, rows=int(X.shape[0]), input_sha=xsha,
               layout_ok=layout_ok, auc_ok=auc_ok, sea_auc=float(m['auc'][0]), sea_time_s=float(m['time'][0]),
               wall_s=wrap['wall_s'], peak_wset_mb=wrap['peak_wset_mb'], wall_total_s=round(wall_total, 1), n_inputs=len(res))
    shutil.rmtree(d)
    return rec, prob


if a.mode == 'DEV':
    jobs = dev_jobs('sea')[0]
elif a.mode in ('G2', 'G3', 'G5'):
    jobs = [j for j in dev_jobs('sea')[1] if j['gate'] == a.mode]
    if a.mode == 'G5':
        jobs.append(repro8_job())
else:
    jobs = run_jobs('sea', a.mode)
todo = [j for j in jobs if not (out_path('sea', j['key']).exists() and is_done('sea', j['key'], build(j)[2]))]
if a.limit:
    todo = todo[:a.limit]
print(f'sea {a.mode}: {len(jobs)} planned jobs, {len(todo)} to run', flush=True)
for k, job in enumerate(todo):
    if budget is not None and time.time() - t_start > budget:
        log.write(json.dumps(dict(key=job['key'], status='budget_stop', elapsed_s=round(time.time() - t_start, 1))) + '\n')
        log.flush()
        print(f"BUDGET STOP before {job['key']}", flush=True)
        sys.exit(2)
    rec, prob = run_one(job)
    if rec['status'] == 'ok':
        save_npz(out_path('sea', job['key']), prob=prob, meta=np.array(json.dumps(rec)))
    log.write(json.dumps(rec) + '\n')
    log.flush()
    print(f"[{k + 1}/{len(todo)}] {job['key']} n={rec.get('rows')} D={rec.get('D')} {rec.get('wall_total_s')}s "
          f"peak={rec.get('peak_wset_mb', 0):.0f}MB {rec['status']} layout={rec.get('layout_ok')} auc={rec.get('auc_ok')}",
          flush=True)
    if rec['status'] != 'ok' or rec.get('layout_ok') is False or rec.get('auc_ok') is False:
        print('STOP: job failed or adapter check failed (rules §6, §8)', flush=True)
        sys.exit(3)
print(f'sea {a.mode}: done in {time.time() - t_start:.0f} s', flush=True)
