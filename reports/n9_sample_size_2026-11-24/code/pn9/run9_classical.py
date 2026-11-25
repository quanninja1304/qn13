"""P-N9 / Study 8 classical baselines on linear systems (rules PN9 v1 §1): PC (Fisher-z, alpha 0.05, stable) and GES
(Gaussian BIC), both from causal-learn. The calls and the skeleton replicate the frozen Study 1 runner
(n1_runs/pn1/run_classical.py, run() and skel()). Saves the skeleton of the output graph on the full table. No metric.
usage (Study 1 model environment): python -I run9_classical.py <pc|ges> <DEV|G2|G3|REPRO|R1|R3> [--limit N]
"""
import os
import sys
import time
import json
import argparse

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.name == 'nt':
    import ctypes
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
ap = argparse.ArgumentParser()
ap.add_argument('alg', choices=('pc', 'ges'))
ap.add_argument('mode', choices=('DEV', 'G2', 'G3', 'REPRO', 'R1', 'R3'))
ap.add_argument('--limit', type=int, default=0)
a = ap.parse_args()
import numpy as np
from common9 import *

(OUT9 / a.alg).mkdir(parents=True, exist_ok=True)
log = open(OUT9 / f'log_{a.alg}_{a.mode}.jsonl', 'a', encoding='utf-8')
hdr_file = OUT9 / 'pn9_run_header.json'
t_start = time.time()
budget = None
if a.mode in ('R1', 'R2', 'R3', 'R4'):   # main runs only (not REPRO)
    hdrs = [h for h in (json.loads(hdr_file.read_text()) if hdr_file.exists() else []) if h['label'] == f'pn9_start_{a.alg}_{a.mode}']
    if not hdrs or not hdrs[-1]['ok']:
        sys.exit(f'no successful start header for {a.alg} {a.mode}')
    t_start = hdrs[-1]['time_unix']
    budget = BUDGET_H[a.alg][a.mode] * 3600


def skel(G):
    m = np.asarray(G.graph)
    return ((m != 0) | (m.T != 0)).astype(np.int8)


def run(x):
    from causallearn.search.ConstraintBased.PC import pc
    if a.alg == 'pc':
        cg = pc(x.astype(np.float64), 0.05, 'fisherz', stable=True, show_progress=False)
        return skel(cg.G)
    from causallearn.search.ScoreBased.GES import ges
    r = ges(x.astype(np.float64), score_func='local_score_BIC')
    return skel(r['G'])


def build(job):
    if job['role'] == 'repro1':
        from common import assemble                           # frozen P-N1 (n = 500)
        x, t, gp, note = assemble(job['sysid'], job['ci'], job['seed'], job['typ'], job['k'])
        return x, t['x'].shape[1], dict(seed_used=int(t['seed_used']))
    d = inputs_at(job['sysid'], job['ci'], job['sys_seed'], job['n'])
    return d[job['cond']], d['dT'], dict(seed_used=d['seed_used'], rejected=d['rejected'])


if a.mode == 'DEV':
    jobs = dev_jobs(a.alg)[0]
elif a.mode in ('G2', 'G3'):
    jobs = [j for j in dev_jobs(a.alg)[1] if j['gate'] == a.mode]
elif a.mode == 'REPRO':
    jobs = repro1_jobs(a.alg)
else:
    jobs = run_jobs(a.alg, a.mode)
todo = [j for j in jobs if not (out_path(a.alg, j['key']).exists() and is_done(a.alg, j['key'], sha(build(j)[0])))]
if a.limit:
    todo = todo[:a.limit]
print(f'{a.alg} {a.mode}: {len(jobs)} planned jobs, {len(todo)} to run', flush=True)
for i, job in enumerate(todo):
    if budget is not None and time.time() - t_start > budget:
        log.write(json.dumps(dict(key=job['key'], status='budget_stop', elapsed_s=round(time.time() - t_start, 1))) + '\n')
        log.flush()
        print(f"BUDGET STOP before {job['key']}", flush=True)
        sys.exit(2)
    x, dT, extra = build(job)
    t0 = time.perf_counter()
    try:
        sk, status = run(x), 'ok'
    except Exception as e:
        sk, status = None, 'error: ' + repr(e)
    dt = time.perf_counter() - t0
    rec = {k: job[k] for k in job if k not in ('key',)}
    rec.update(key=job['key'], mode=a.mode, status=status, runtime_s=round(dt, 3), D=int(x.shape[1]), dT=int(dT),
               rows=int(x.shape[0]), input_sha=sha(x), peak_wset_mb=round(peak_wset_mb(), 1), **extra)
    if status == 'ok':
        save_npz(out_path(a.alg, job['key']), skel=sk, meta=np.array(json.dumps(rec)))
    log.write(json.dumps(rec) + '\n')
    log.flush()
    print(f"[{i + 1}/{len(todo)}] {job['key']} n={x.shape[0]} D={x.shape[1]} {dt:.1f}s peak={rec['peak_wset_mb']:.0f}MB {status}",
          flush=True)
    if status != 'ok':
        print('STOP: job failed (rules §8)', flush=True)
        sys.exit(3)
print(f'{a.alg} {a.mode}: done in {time.time() - t_start:.0f} s', flush=True)
