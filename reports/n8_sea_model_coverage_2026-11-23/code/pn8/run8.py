"""P-N8 / Study 7 runner (rules PN8 v1 §1, §6–§8): one SEA input per fresh process, sequential, resume by key.

For each planned job of a run: build the input with the frozen builders, write data.npy / DAG.npy and a one-row CSV,
call SEA's own inference script through sea_wrapper8.py in the SEA environment (python -E -s), read the result file,
check the adapter (layout of `true`; AUROC when defined), map permuted outputs back to the original variable order and
save prob[i, j] = P(i -> j) with a metadata record. No metric is computed here.
Stops at the first failed job (rules §8) and at the run's budget (clock = time of the run's start header, rules §8).
usage (Study 1 model environment): python -I run8.py <DEV|A1|A2|A3|A4|B|IL> [--limit N]
"""
import os, sys, json, time, pickle, shutil, subprocess, argparse, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.name == 'nt':   # keep the system awake while this process runs; no effect on results
    import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
ap = argparse.ArgumentParser(); ap.add_argument('run'); ap.add_argument('--limit', type=int, default=0)
a = ap.parse_args()
import numpy as np
from sklearn.metrics import roc_auc_score
from common8 import *

(OUT8 / 'sea').mkdir(parents=True, exist_ok=True)
WORK8.mkdir(parents=True, exist_ok=True)
log = open(OUT8 / f'log_{a.run}.jsonl', 'a', encoding='utf-8')
hdr_file = OUT8 / 'pn8_run_header.json'
t_start = time.time()
if a.run != 'DEV':        # main runs: the clock starts at this run's start header (written by verify_freeze8.py)
    hdrs = [h for h in (json.loads(hdr_file.read_text()) if hdr_file.exists() else []) if h['label'] == f'pn8_start_{a.run}']
    if not hdrs or not hdrs[-1]['ok']:
        sys.exit(f'no successful start header for run {a.run}')
    t_start = hdrs[-1]['time_unix']
budget = BUDGET_H[a.run] * 3600


def record(job, **kw):
    rec = {k: job[k] for k in job if k not in ('key',)}
    rec.update(key=job['key'], run=a.run, **kw)
    return rec


def run_one(job):
    X, G, xsha, dT, perm = build(job)
    D = X.shape[1]
    d = WORK8 / job['key']
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    np.save(d / 'data.npy', X)
    np.save(d / 'DAG.npy', G.astype(np.int64))
    with open(d / 'one.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['fp_data', 'fp_graph', 'fp_regime', 'split'])
        w.writerow([(d / 'data.npy').as_posix(), (d / 'DAG.npy').as_posix(), '', 'test'])
    cmd = [str(SEA_PY), '-E', '-s', '-W', 'ignore', str(WRAPPER), str(SEA_SRC), str(d / 'one.csv'), str(d / 'res.pkl'),
           str(job['seed']), str(d / 'wrap.json')]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=str(WORK8), capture_output=True, text=True, timeout=1800)
        code, tail = p.returncode, (p.stdout + p.stderr)[-3000:]
    except subprocess.TimeoutExpired:
        code, tail = 'timeout', ''
    wall_total = time.time() - t0
    if code != 0 or not (d / 'res.pkl').exists():
        (OUT8 / 'errors').mkdir(exist_ok=True)
        (OUT8 / 'errors' / f"{job['key']}.txt").write_text(str(tail), encoding='utf-8')
        return record(job, status=f'error: exit {code}', D=D, dT=dT, input_sha=xsha, wall_total_s=round(wall_total, 1)), None
    res = pickle.load(open(d / 'res.pkl', 'rb'))
    assert list(res) == [job['key']], (list(res), job['key'])          # SEA keys results by the input folder name
    m = res[job['key']]
    prob_in, t_vec, p_vec = unpack(m, D)
    layout_ok = bool(np.array_equal(t_vec, expected_true(G)))
    auc_ok = None
    if 0 < t_vec.sum() < len(t_vec):
        auc_ok = bool(abs(roc_auc_score(t_vec, p_vec) - float(m['auc'][0])) < 1e-6)
    wrap = json.loads((d / 'wrap.json').read_text(encoding='utf-8'))
    prob = unpermute(prob_in, perm)
    rec = record(job, status='ok', D=D, dT=dT, input_sha=xsha, input_written_sha=sha(X), layout_ok=layout_ok,
                 auc_ok=auc_ok, sea_auc=float(m['auc'][0]), sea_time_s=float(m['time'][0]), wall_s=wrap['wall_s'],
                 peak_wset_mb=wrap['peak_wset_mb'], wall_total_s=round(wall_total, 1), n_inputs=len(res),
                 perm=None if perm is None else [int(v) for v in perm])
    shutil.rmtree(d)
    return rec, prob


jobs = run_jobs(a.run)
todo = [j for j in jobs if not out_path(j).exists()]
if a.limit:
    todo = todo[:a.limit]
print(f'{a.run}: {len(jobs)} planned jobs, {len(todo)} to run', flush=True)
for n, job in enumerate(todo):
    if time.time() - t_start > budget:
        rec = record(job, status='budget_stop', elapsed_s=round(time.time() - t_start, 1))
        log.write(json.dumps(rec) + '\n'); log.flush()
        print(f'BUDGET STOP before {job["key"]}', flush=True)
        sys.exit(2)
    rec, prob = run_one(job)
    if rec['status'] == 'ok':
        np.savez_compressed(out_path(job), prob=prob, meta=np.array(json.dumps(rec)))
    log.write(json.dumps(rec) + '\n'); log.flush()
    print(f"[{n + 1}/{len(todo)}] {job['key']} D={rec.get('D')} {rec.get('wall_total_s')}s {rec['status']}"
          f" layout={rec.get('layout_ok')} auc={rec.get('auc_ok')}", flush=True)
    if rec['status'] != 'ok' or rec.get('layout_ok') is False or rec.get('auc_ok') is False:
        print('STOP: job failed or adapter check failed (rules §6, §8)', flush=True)
        sys.exit(3)
print(f'{a.run}: done in {time.time() - t_start:.0f} s since start', flush=True)
