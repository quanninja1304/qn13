"""P-N1 model runner: one process per model, sequential jobs, one forward per input, raw outputs saved, resume by input hash.

usage: run_model.py <avici|cdfm|foundcause> <phase: dev|E1|E2> [--threads T] [--limit N]
No metric is computed here.
"""
import os, sys, time, json, argparse
ap = argparse.ArgumentParser()
ap.add_argument('model'); ap.add_argument('phase'); ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--limit', type=int, default=0); ap.add_argument('--only', default='')
a = ap.parse_args()
T = str(a.threads)
for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[v] = T
os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                  XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from common import *
from jobs import jobs_for

out_dir = OUT / a.model; out_dir.mkdir(parents=True, exist_ok=True)
log = open(out_dir / f'log_{a.phase}.jsonl', 'a', encoding='utf-8')


def load():
    if a.model == 'avici':
        import avici
        m = avici.load_pretrained(checkpoint_dir=str(ENV / 'checkpoints/avici/scm-v0'), expects_counts=False)
        return lambda x, sched: dict(probs=np.asarray(m(x=x), dtype=np.float64))
    if a.model == 'cdfm':
        import torch; torch.set_num_threads(a.threads)
        from cdfm import CDFM
        m = CDFM.from_pretrained(str(ENV / 'checkpoints/cdfm'), device='cpu', threshold=None)
        def f(x, sched):
            r = m.predict(x, threshold=None, standardize=False)   # external z-score (v2 §2)
            return dict(probs=np.asarray(r.probabilities, np.float64), logits=np.asarray(r.logits, np.float64),
                        adj_native=np.asarray(r.adjacency, np.int8), threshold=float(r.threshold))
        return f
    import torch; torch.set_num_threads(a.threads)
    sys.path.insert(0, str(ENV / 'repos/foundcause'))
    import foundcause as fcm
    from fc_adapter import predict_sched
    ck = torch.load(ENV / 'checkpoints/foundcause/checkpoint.pt', map_location='cpu', weights_only=True, mmap=True)
    with torch.device('meta'):
        m = fcm.CausalDiscoveryTransformer(fcm.ModelConfig())
    m.load_state_dict(ck['model_state_dict'], strict=True, assign=True); m.eval()
    def f(x, sched):
        with torch.inference_mode():
            if sched is None:   # untouched package API (schedule base 42)
                o = fcm.predict(m, x, torch.device('cpu'), n_runs=10, temperature=1.0, max_samples=5000)
            else:
                o = predict_sched(m, x, torch.device('cpu'), base=sched, n_runs=10, temperature=1.0, max_samples=5000)
        return dict(probs=np.asarray(o['probabilities'], np.float64), adj_native=np.asarray(o['adjacency'], np.int8),
                    agreement=np.asarray(o['agreement'], np.float64), threshold=float(o['threshold']),
                    C=np.asarray(o['C'], np.float64), dropped=np.asarray(o['dropped'], np.int64),
                    n_duplicates=len(o['duplicates']))
    return f


jl = jobs_for(a.model, a.phase)
if a.only:
    jl = [j for j in jl if a.only in j['key']]
todo = []
for j in jl:
    f = out_dir / f"{j['key']}.npz"
    if f.exists():
        continue
    todo.append(j)
if a.limit:
    todo = todo[:a.limit]
print(f'{a.model} {a.phase}: {len(jl)} jobs, {len(todo)} to run', flush=True)
fn = load() if todo else None
for i, j in enumerate(todo):
    x, t, gp, note = assemble(j['sysid'], j['ci'], j['seed'], j['typ'], j['k'], perm=j.get('perm'))
    t0 = time.perf_counter()
    try:
        r = fn(x, j.get('sched'))
        status = 'ok'
    except Exception as e:
        import traceback
        r, status = {}, 'error: ' + repr(e)
        print(traceback.format_exc(), flush=True)
    dt = time.perf_counter() - t0
    rec = dict(key=j['key'], status=status, runtime_s=round(dt, 2), d=x.shape[1], dT=t['x'].shape[1], input_sha=sha(x),
               target_sha=sha(t['x0']), threads=a.threads, note=note, seed_used=int(t['seed_used']))
    if status == 'ok':
        meta = np.array(json.dumps(rec))
        np.savez_compressed(out_dir / f"{j['key']}.npz", meta=meta, perm=np.asarray(j.get('perm', []), np.int64), **r)
    log.write(json.dumps(rec) + '\n'); log.flush()
    print(f"[{i+1}/{len(todo)}] {j['key']} d={x.shape[1]} {dt:.1f}s {status}", flush=True)
