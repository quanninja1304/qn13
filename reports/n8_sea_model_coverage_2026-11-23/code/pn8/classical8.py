"""P-N8 / Study 7 classical controls (rules PN8 v1 §2): PC (Fisher-z, alpha 0.05, stable) and GES (Gaussian BIC) from
causal-learn, at k0 and A20 on linear systems only; the same calls as the frozen P-N2 run2_classical.py.
Saves the skeleton of the output graph on the full table. Real-table controls are Study 4's outputs (not rerun).
usage (Study 1 model environment): python -I classical8.py <pc|ges> <PN8|DEV8>
"""
import os, sys, time, json, argparse
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('MKL_NUM_THREADS', '1')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.name == 'nt':
    import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
ap = argparse.ArgumentParser(); ap.add_argument('alg'); ap.add_argument('set')
a = ap.parse_args()
import numpy as np
from common8 import *

out_dir = OUT8 / 'classical' / a.alg
out_dir.mkdir(parents=True, exist_ok=True)
log = open(out_dir / f'log_{a.set}.jsonl', 'a', encoding='utf-8')


def skel_of(G):
    m = np.asarray(G.graph)
    return ((m != 0) | (m.T != 0)).astype(np.int8)


def run(x):
    if a.alg == 'pc':
        from causallearn.search.ConstraintBased.PC import pc
        return skel_of(pc(x.astype(np.float64), 0.05, 'fisherz', stable=True, show_progress=False).G)
    from causallearn.search.ScoreBased.GES import ges
    return skel_of(ges(x.astype(np.float64), score_func='local_score_BIC')['G'])


def ckey(sysid, cond):
    return f'{sysid}__{cond}'


jl = [(s, ci, sseed, c) for s, ci, sseed, i in systems8(a.set) if ci in LINEAR for c in ('k0', 'A20')]
todo = [j for j in jl if not (out_dir / f'{ckey(j[0], j[3])}.npz').exists()]
print(f'{a.alg} {a.set}: {len(jl)} jobs, {len(todo)} to run', flush=True)
for n, (sid, ci, sseed, cond) in enumerate(todo):
    X, G, dT, g = syn_input(sid, ci, sseed, cond)
    t0 = time.perf_counter()
    try:
        sk, status = run(X), 'ok'
    except Exception as e:
        sk, status = None, 'error: ' + repr(e)
    rec = dict(key=ckey(sid, cond), status=status, runtime_s=round(time.perf_counter() - t0, 2), D=X.shape[1], dT=dT,
               input_sha=sha(X), cond=cond, alg=a.alg)
    if status == 'ok':
        np.savez_compressed(out_dir / f"{rec['key']}.npz", skel=sk, meta=np.array(json.dumps(rec)))
    log.write(json.dumps(rec) + '\n'); log.flush()
    print(f"[{n + 1}/{len(todo)}] {rec['key']} D={X.shape[1]} {rec['runtime_s']}s {status}", flush=True)
    if status != 'ok':
        sys.exit(3)
