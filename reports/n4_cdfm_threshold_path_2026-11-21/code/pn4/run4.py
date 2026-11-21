"""P-N4 CDFM runner (rules PN4 v1 §1): one forward per (system, input). No metric is computed here.

CDFM is loaded and called exactly as in the frozen P-N2 runner run2_held2.py (16ea97f): from_pretrained(threshold=None),
predict(x, threshold=None, standardize=False) after the external z-score. Threads, keep-awake and output layout follow it.
usage: run4.py <PN4|DEV4> [--threads 2] [--only S] [--limit N]
  -> pn4_out/cdfm/<sys>__<cond>.npz (probs, logits, adj_native, threshold, meta), pn4_out/cdfm/log_<set>.jsonl
"""
import os, sys, time, json, argparse
ap = argparse.ArgumentParser()
ap.add_argument('set', choices=['PN4', 'DEV4']); ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--only', default=''); ap.add_argument('--limit', type=int, default=0)
a = ap.parse_args()
T = str(a.threads)
for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[v] = T
os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                  XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.name == 'nt':   # keep the system awake while this process runs (P-N2 DEV2 lesson); no effect on results
    import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
import numpy as np
import psutil
from common4 import *

ENV = ART / 'n1_models_cpu'
out_dir = OUT4 / 'cdfm'
out_dir.mkdir(parents=True, exist_ok=True)
log = open(out_dir / f'log_{a.set}.jsonl', 'a', encoding='utf-8')
proc = psutil.Process()


def load():
    import torch; torch.set_num_threads(a.threads)
    from cdfm import CDFM
    m = CDFM.from_pretrained(str(ENV / 'checkpoints/cdfm'), device='cpu', threshold=None)

    def f(x):
        r = m.predict(x, threshold=None, standardize=False)
        return dict(probs=np.asarray(r.probabilities, np.float64), logits=np.asarray(r.logits, np.float64),
                    adj_native=np.asarray(r.adjacency, np.int8), threshold=float(r.threshold))
    return f


jobs = [(s, ci, seed, c) for s, ci, seed in systems4(a.set) for c in conds4(ci)]
if a.only:
    jobs = [j for j in jobs if a.only in key4(j[0], j[3])]
todo = [j for j in jobs if not (out_dir / f'{key4(j[0], j[3])}.npz').exists()]
if a.limit:
    todo = todo[:a.limit]
print(f'cdfm {a.set}: {len(todo)} to run', flush=True)
fn = load() if todo else None
for i, (sid, ci, seed, cond) in enumerate(todo):
    X, t, pad = assemble4(sid, ci, seed, cond)
    dT = t['x'].shape[1]
    k, e = (0, None) if cond == 'k0' else parse(cond)
    rec = dict(key=key4(sid, cond), sys=sid, cond=cond, k=k, e=e, d=int(X.shape[1]), dT=int(dT), input_sha=sha(X),
               target_sha=sha(t['x0']), seed_used=int(t['seed_used']), threads=a.threads,
               pad_edges=None if pad is None else pad['n_edges'], pad_isolated=None if pad is None else pad['n_isolated'])
    arrays = {}
    t0 = time.perf_counter()
    try:
        arrays = fn(X)
        status = 'ok'
    except Exception as ex:
        import traceback
        status = 'error: ' + repr(ex)
        print(traceback.format_exc(), flush=True)
    mi = proc.memory_info()
    rec.update(status=status, runtime_s=round(time.perf_counter() - t0, 2), rss_mb=round(mi.rss / 2 ** 20, 1),
               peak_wset_mb=round(getattr(mi, 'peak_wset', 0) / 2 ** 20, 1))
    if status == 'ok':
        np.savez_compressed(out_dir / f"{rec['key']}.npz", meta=np.array(json.dumps(rec, default=int)), **arrays)
    log.write(json.dumps(rec, default=int) + '\n'); log.flush()
    print(f"[{i + 1}/{len(todo)}] {rec['key']} d={X.shape[1]} {rec['runtime_s']}s {status}", flush=True)
