"""P-N1 classical baselines: PC (Fisher-z, alpha 0.05, stable), GES (Gaussian BIC), oracle-PC (d-separation on G_T (+) G_P).

usage: run_classical.py <pc|ges|oracle> <phase: dev|E1|E2|oracle> [--limit N]
Saves the skeleton of the output graph (CPDAG) on the full table. No metric is computed here.
"""
import os, sys, time, json, argparse
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('MKL_NUM_THREADS', '1')
sys.path.insert(0, os.path.dirname(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('alg'); ap.add_argument('phase'); ap.add_argument('--limit', type=int, default=0)
ap.add_argument('--only', default='')
a = ap.parse_args()
import numpy as np, networkx as nx
from common import *
from jobs import jobs_for

out_dir = OUT / a.alg; out_dir.mkdir(parents=True, exist_ok=True)
log = open(out_dir / f'log_{a.phase}.jsonl', 'a', encoding='utf-8')


def skel(G):
    m = np.asarray(G.graph)
    return ((m != 0) | (m.T != 0)).astype(np.int8)


def run(x, g_full):
    from causallearn.search.ConstraintBased.PC import pc
    if a.alg == 'pc':
        cg = pc(x.astype(np.float64), 0.05, 'fisherz', stable=True, show_progress=False)
        return skel(cg.G)
    if a.alg == 'oracle':
        dag = nx.DiGraph(); dag.add_nodes_from(range(g_full.shape[0]))
        dag.add_edges_from([(int(i), int(j)) for i, j in zip(*np.nonzero(g_full))])
        cg = pc(np.zeros((1, g_full.shape[0])), 0.05, 'd_separation', true_dag=dag, stable=True, show_progress=False)
        return skel(cg.G)
    from causallearn.search.ScoreBased.GES import ges
    r = ges(x.astype(np.float64), score_func='local_score_BIC')
    return skel(r['G'])


if a.phase == 'oracle':   # RN0.5: 20 graph-only systems, types A and B at k = 20, plus k = 0
    jl = []
    for s, ci, seed in systems('ORACLE'):
        for typ, k in (('-', 0), ('A', 20), ('B', 20)):
            jl.append(dict(key=job_key(s, typ, k), sysid=s, ci=ci, seed=seed, typ=typ, k=k))
else:
    jl = jobs_for('pc', a.phase)
    jl = [j for j in jl if j['key'].endswith('__main') or j['key'].endswith('__rep')]
if a.only:
    jl = [j for j in jl if a.only in j['key']]
todo = [j for j in jl if not (out_dir / f"{j['key']}.npz").exists()]
if a.limit:
    todo = todo[:a.limit]
print(f'{a.alg} {a.phase}: {len(jl)} jobs, {len(todo)} to run', flush=True)
for i, j in enumerate(todo):
    x, t, gp, note = assemble(j['sysid'], j['ci'], j['seed'], j['typ'], j['k'])
    dT = t['x'].shape[1]; k = x.shape[1] - dT
    g_full = np.zeros((dT + k, dT + k), np.int8); g_full[:dT, :dT] = t['g']; g_full[dT:, dT:] = gp
    t0 = time.perf_counter()
    try:
        sk = run(x, g_full); status = 'ok'
    except Exception as e:
        sk, status = None, 'error: ' + repr(e)
    dt = time.perf_counter() - t0
    rec = dict(key=j['key'], status=status, runtime_s=round(dt, 2), d=x.shape[1], dT=dT, input_sha=sha(x), note=note)
    if status == 'ok':
        np.savez_compressed(out_dir / f"{j['key']}.npz", skel=sk, meta=np.array(json.dumps(rec)))
    log.write(json.dumps(rec) + '\n'); log.flush()
    print(f"[{i+1}/{len(todo)}] {j['key']} d={x.shape[1]} {dt:.1f}s {status}", flush=True)
