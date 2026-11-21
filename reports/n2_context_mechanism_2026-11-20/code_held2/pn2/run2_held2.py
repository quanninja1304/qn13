"""P-N2 HELD2 model runner (rules held2 v1 §1): plain inputs and the R arm, inputs k0, e0, e_T only. No metric here.

Copy of the frozen run2.py (fddfadd) with the job list restricted to HELD2 (rules held2 §1); model calls, screening,
output format and keep-awake are unchanged.
usage: run2_held2.py <avici|cdfm> HELD2 <plain|R> [--threads T] [--only S] [--limit N]
  plain : one forward per (system, condition) input                  -> <sys>__<cond>__plain.npz
  R     : screening with the locked test/alpha, model per component  -> <sys>__<cond>__R.npz
Model calls are copied from the frozen P-N1 runner (run_model.py): AVICI scm-v0, CDFM with threshold=None, external z-score.
"""
import os, sys, time, json, argparse
ap = argparse.ArgumentParser()
ap.add_argument('model'); ap.add_argument('set', choices=['HELD2']); ap.add_argument('arm', choices=['plain', 'R'])
ap.add_argument('--threads', type=int, default=2); ap.add_argument('--only', default=''); ap.add_argument('--limit', type=int, default=0)
a = ap.parse_args()
T = str(a.threads)
for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[v] = T
os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                  XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.name == 'nt':   # keep the system awake while this process runs (DEV2: one job slept 7.15 h); no effect on results
    import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
import numpy as np
from held2 import *
from screen import screen

ENV = ART / 'n1_models_cpu'
out_dir = OUT2 / a.model
out_dir.mkdir(parents=True, exist_ok=True)
log = open(out_dir / f'log_{a.set}_{a.arm}.jsonl', 'a', encoding='utf-8')
def load():
    if a.model == 'avici':
        import avici
        m = avici.load_pretrained(checkpoint_dir=str(ENV / 'checkpoints/avici/scm-v0'), expects_counts=False)
        return lambda x: dict(probs=np.asarray(m(x=x), dtype=np.float64))
    if a.model == 'cdfm':
        import torch; torch.set_num_threads(a.threads)
        from cdfm import CDFM
        m = CDFM.from_pretrained(str(ENV / 'checkpoints/cdfm'), device='cpu', threshold=None)
        def f(x):
            r = m.predict(x, threshold=None, standardize=False)
            return dict(probs=np.asarray(r.probabilities, np.float64), logits=np.asarray(r.logits, np.float64),
                        adj_native=np.asarray(r.adjacency, np.int8), threshold=float(r.threshold))
        return f
    raise ValueError(a.model)


def jobs():
    jl = [(s, ci, seed, c) for s, ci, seed in systems_held2() for c in conds_held2(ci)]
    if a.only:
        jl = [j for j in jl if a.only in key2(j[0], j[3], a.arm)]
    return jl


alpha = json.loads((OUT2 / 'alpha.json').read_text()) if a.arm == 'R' else None
todo = [j for j in jobs() if not (out_dir / f'{key2(j[0], j[3], a.arm)}.npz').exists()]
if a.limit:
    todo = todo[:a.limit]
print(f'{a.model} {a.set} {a.arm}: {len(todo)} to run', flush=True)
fn = load() if todo else None
for i, (sid, ci, seed, cond) in enumerate(todo):
    X, t, pad = assemble2(sid, ci, seed, cond)
    dT = t['x'].shape[1]
    rec = dict(key=key2(sid, cond, a.arm), sys=sid, cond=cond, arm=a.arm, d=X.shape[1], dT=dT, input_sha=sha(X),
               target_sha=sha(t['x0']), seed_used=int(t['seed_used']), threads=a.threads,
               pad_edges=None if pad is None else pad['n_edges'], pad_isolated=None if pad is None else pad['n_isolated'])
    arrays = {}
    t0 = time.perf_counter()
    try:
        if a.arm in ('plain', 'rep'):
            arrays = fn(X)
        elif a.arm == 'oracle':
            arrays = fn(np.ascontiguousarray(X[:, :dT]))
        else:
            mech = CELLS[ci][2]
            test = 'fisherz' if mech == 'lin' else 'hsic'
            ts = time.perf_counter()
            sc = screen(X, test, alpha[test], dT, t['g'])
            rec.update(test=test, alpha=alpha[test], screen_seconds=round(time.perf_counter() - ts, 3),
                       **{q: sc[q] for q in ('merged', 'split', 'false_cross', 'n_target_components', 'n_true_edges', 'k')})
            lab = sc['lab']
            probs_T = np.zeros((dT, dT)); adj_T = np.zeros((dT, dT), np.int8)
            thr_c, comps, calls = [], [], 0
            for L in sorted(set(lab[:dT].tolist())):
                idx = np.where(lab == L)[0]
                comps.append(idx.tolist())
                if len(idx) < 2:
                    continue
                r = fn(np.ascontiguousarray(X[:, idx]))
                calls += 1
                loc = [q for q, v in enumerate(idx) if v < dT]
                tv = idx[loc]
                probs_T[np.ix_(tv, tv)] = r['probs'][np.ix_(loc, loc)]
                if a.model == 'cdfm':
                    adj_T[np.ix_(tv, tv)] = r['adj_native'][np.ix_(loc, loc)]
                    thr_c.append(r['threshold'])
            arrays = dict(probs_T=probs_T, labels=lab.astype(np.int64))
            if a.model == 'cdfm':
                arrays.update(adj_native_T=adj_T, thr_components=np.asarray(thr_c, np.float64))
            rec.update(n_model_calls=calls, target_components=comps)
        status = 'ok'
    except Exception as e:
        import traceback
        status = 'error: ' + repr(e)
        print(traceback.format_exc(), flush=True)
    rec.update(status=status, runtime_s=round(time.perf_counter() - t0, 2))
    if status == 'ok':
        np.savez_compressed(out_dir / f"{rec['key']}.npz", meta=np.array(json.dumps(rec, default=int)), **arrays)
    log.write(json.dumps(rec, default=int) + '\n'); log.flush()
    print(f"[{i+1}/{len(todo)}] {rec['key']} d={X.shape[1]} {rec['runtime_s']}s {status}", flush=True)
