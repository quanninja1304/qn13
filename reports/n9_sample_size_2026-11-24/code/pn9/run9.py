"""P-N9 / Study 8 runner for AVICI, CDFM and FoundCause (rules PN9 v1 §1, §6-§8).

One process per invocation, jobs run sequentially, one forward per input, raw outputs saved, resume by key. The model
loading and calls replicate the frozen Study 1 runner (n1_runs/pn1/run_model.py, load()) line for line; thread counts
as Study 1 (AVICI 2, CDFM 2, FoundCause 4). No metric is computed here.

usage (Study 1 model environment): python -I run9.py <avici|cdfm|foundcause> <DEV|G2|G3|REPRO|R1|R2|R3|R4> [--limit N]
  DEV    timing jobs of the development set (rules §6, G4)
  G2     rerun of the first DEV job, in this fresh process (G2)
  G3     the memory job alone, in this fresh process (G3)
  REPRO  Study 1 inputs rebuilt with the frozen P-N1 assemble (G5: outputs must equal Study 1's saved outputs bitwise)
  R1-R4  main runs (need a successful start header from verify_freeze9.py; budget clock from that header)
"""
import os
import sys
import time
import json
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('model', choices=('avici', 'cdfm', 'foundcause'))
ap.add_argument('mode', choices=('DEV', 'G2', 'G3', 'REPRO', 'R1', 'R2', 'R3', 'R4'))
ap.add_argument('--limit', type=int, default=0)
a = ap.parse_args()
NT = {'avici': 2, 'cdfm': 2, 'foundcause': 4}[a.model]               # = common9.THREADS[model] (checked below)
T = str(NT)
for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[v] = T
os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                  XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.name == 'nt':   # keep the system awake while this process runs; no effect on results
    import ctypes
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
import numpy as np
from common9 import *

assert NT == THREADS[a.model], (NT, THREADS)

out_dir = OUT9 / a.model
out_dir.mkdir(parents=True, exist_ok=True)
log = open(OUT9 / f'log_{a.model}_{a.mode}.jsonl', 'a', encoding='utf-8')
hdr_file = OUT9 / 'pn9_run_header.json'
t_start = time.time()
budget = None
if a.mode in ('R1', 'R2', 'R3', 'R4'):   # main runs only (not REPRO)
    hdrs = [h for h in (json.loads(hdr_file.read_text()) if hdr_file.exists() else [])
            if h['label'] == f'pn9_start_{a.model}_{a.mode}']
    if not hdrs or not hdrs[-1]['ok']:
        sys.exit(f'no successful start header for {a.model} {a.mode}')
    t_start = hdrs[-1]['time_unix']
    budget = BUDGET_H[a.model][a.mode] * 3600


def load_model():
    """Replicates load() of the frozen Study 1 runner."""
    if a.model == 'avici':
        import avici
        m = avici.load_pretrained(checkpoint_dir=str(ENV / 'checkpoints/avici/scm-v0'), expects_counts=False)
        return lambda x: dict(probs=np.asarray(m(x=x), dtype=np.float64))
    import torch
    torch.set_num_threads(NT)
    if a.model == 'cdfm':
        from cdfm import CDFM
        m = CDFM.from_pretrained(str(ENV / 'checkpoints/cdfm'), device='cpu', threshold=None)

        def f(x):
            r = m.predict(x, threshold=None, standardize=False)   # external z-score, as Study 1
            return dict(probs=np.asarray(r.probabilities, np.float64), logits=np.asarray(r.logits, np.float64),
                        adj_native=np.asarray(r.adjacency, np.int8), threshold=float(r.threshold))
        return f
    sys.path.insert(0, str(ENV / 'repos/foundcause'))
    import foundcause as fcm
    ck = torch.load(ENV / 'checkpoints/foundcause/checkpoint.pt', map_location='cpu', weights_only=True, mmap=True)
    with torch.device('meta'):
        m = fcm.CausalDiscoveryTransformer(fcm.ModelConfig())
    m.load_state_dict(ck['model_state_dict'], strict=True, assign=True)
    m.eval()

    def f(x):
        with torch.inference_mode():   # untouched package API: schedule base 42, 10 runs, temperature 1.0
            o = fcm.predict(m, x, torch.device('cpu'), n_runs=10, temperature=1.0, max_samples=5000)
        return dict(probs=np.asarray(o['probabilities'], np.float64), adj_native=np.asarray(o['adjacency'], np.int8),
                    agreement=np.asarray(o['agreement'], np.float64), threshold=float(o['threshold']),
                    C=np.asarray(o['C'], np.float64), dropped=np.asarray(o['dropped'], np.int64),
                    n_duplicates=len(o['duplicates']))
    return f


def build(job):
    """Input of a job: (x, dT, meta extras)."""
    if job['role'] == 'repro1':
        from common import assemble                           # frozen P-N1 (n = 500)
        x, t, gp, note = assemble(job['sysid'], job['ci'], job['seed'], job['typ'], job['k'])
        return x, t['x'].shape[1], dict(seed_used=int(t['seed_used']))
    d = inputs_at(job['sysid'], job['ci'], job['sys_seed'], job['n'])
    return d[job['cond']], d['dT'], dict(seed_used=d['seed_used'], rejected=d['rejected'])


if a.mode == 'DEV':
    jobs = dev_jobs(a.model)[0]
elif a.mode in ('G2', 'G3'):
    jobs = [j for j in dev_jobs(a.model)[1] if j['gate'] == a.mode]
elif a.mode == 'REPRO':
    jobs = repro1_jobs(a.model)
else:
    jobs = run_jobs(a.model, a.mode)
todo = [j for j in jobs if not (out_path(a.model, j['key']).exists() and is_done(a.model, j['key'], sha(build(j)[0])))]
if a.limit:
    todo = todo[:a.limit]
print(f'{a.model} {a.mode}: {len(jobs)} planned jobs, {len(todo)} to run (threads {NT})', flush=True)
fn = load_model() if todo else None
for i, job in enumerate(todo):
    if budget is not None and time.time() - t_start > budget:
        rec = dict(key=job['key'], status='budget_stop', elapsed_s=round(time.time() - t_start, 1))
        log.write(json.dumps(rec) + '\n')
        log.flush()
        print(f"BUDGET STOP before {job['key']}", flush=True)
        sys.exit(2)
    x, dT, extra = build(job)
    t0 = time.perf_counter()
    try:
        r = fn(x)
        status = 'ok'
    except Exception as e:
        import traceback
        r, status = {}, 'error: ' + repr(e)
        print(traceback.format_exc(), flush=True)
    dt = time.perf_counter() - t0
    rec = {k: job[k] for k in job if k not in ('key',)}
    rec.update(key=job['key'], mode=a.mode, status=status, runtime_s=round(dt, 3), D=int(x.shape[1]), dT=int(dT),
               rows=int(x.shape[0]), input_sha=sha(x), threads=NT, peak_wset_mb=round(peak_wset_mb(), 1), **extra)
    if status == 'ok':
        save_npz(out_path(a.model, job['key']), meta=np.array(json.dumps(rec)), **r)
    log.write(json.dumps(rec) + '\n')
    log.flush()
    print(f"[{i + 1}/{len(todo)}] {job['key']} n={x.shape[0]} D={x.shape[1]} {dt:.1f}s peak={rec['peak_wset_mb']:.0f}MB {status}",
          flush=True)
    if status != 'ok':
        print('STOP: job failed (rules §8)', flush=True)
        sys.exit(3)
print(f'{a.model} {a.mode}: done in {time.time() - t_start:.0f} s', flush=True)
