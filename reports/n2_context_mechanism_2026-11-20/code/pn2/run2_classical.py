"""P-N2 classical baselines (rules v1 §4): PC (Fisher-z, alpha 0.05, stable) and GES (Gaussian BIC), as in P-N1.
Linear systems only, conditions k0, e0, e_T, e3. Saves the skeleton of the output graph on the full table.

usage: run2_classical.py <pc|ges> <DEV2|EXP2> [--limit N]
"""
import os, sys, time, json, argparse
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('MKL_NUM_THREADS', '1')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.name == 'nt':   # keep the system awake while this process runs (DEV2: one job slept 7.15 h); no effect on results
    import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
ap = argparse.ArgumentParser(); ap.add_argument('alg'); ap.add_argument('set'); ap.add_argument('--limit', type=int, default=0)
a = ap.parse_args()
import numpy as np
from common2 import *

out_dir = OUT2 / a.alg
out_dir.mkdir(parents=True, exist_ok=True)
log = open(out_dir / f'log_{a.set}.jsonl', 'a', encoding='utf-8')


def skel(G):
    m = np.asarray(G.graph)
    return ((m != 0) | (m.T != 0)).astype(np.int8)


def run(x):
    if a.alg == 'pc':
        from causallearn.search.ConstraintBased.PC import pc
        return skel(pc(x.astype(np.float64), 0.05, 'fisherz', stable=True, show_progress=False).G)
    from causallearn.search.ScoreBased.GES import ges
    return skel(ges(x.astype(np.float64), score_func='local_score_BIC')['G'])


jl = [(s, ci, seed, c) for s, ci, seed in systems2(a.set) if CELLS[ci][2] == 'lin'
      for c in ('k0', 'e0', rep_cond(ci), 'e3')]
todo = [j for j in jl if not (out_dir / f'{key2(j[0], j[3], "plain")}.npz').exists()]
if a.limit:
    todo = todo[:a.limit]
print(f'{a.alg} {a.set}: {len(jl)} jobs, {len(todo)} to run', flush=True)
for i, (sid, ci, seed, cond) in enumerate(todo):
    X, t, pad = assemble2(sid, ci, seed, cond)
    t0 = time.perf_counter()
    try:
        sk, status = run(X), 'ok'
    except Exception as e:
        sk, status = None, 'error: ' + repr(e)
    rec = dict(key=key2(sid, cond, 'plain'), status=status, runtime_s=round(time.perf_counter() - t0, 2), d=X.shape[1],
               dT=t['x'].shape[1], input_sha=sha(X), cond=cond)
    if status == 'ok':
        np.savez_compressed(out_dir / f"{rec['key']}.npz", skel=sk, meta=np.array(json.dumps(rec)))
    log.write(json.dumps(rec) + '\n'); log.flush()
    print(f"[{i+1}/{len(todo)}] {rec['key']} d={X.shape[1]} {rec['runtime_s']}s {status}", flush=True)
