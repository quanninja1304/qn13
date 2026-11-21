"""P-N3 Part B runner (rules v1 §2): AVICI on the 20 EXP2 linear systems, inputs e0 and e_T, 19 configurations.

Configurations: PLAIN, V0-all, KO-all, V0-l and KO-l for l = 1..8. One fresh model instance per configuration
(fresh jit caches; the trace guard in avici_patch.run refuses stale traces). Every PLAIN output is also compared
bitwise with the frozen P-N2 EXP2 output (extended gate B0). No metric is computed here.
usage: partB_run.py  ->  pn3_out/avici_iv/<sys>__<cond>__<cfg>.npz, pn3_out/avici_iv/log.jsonl
"""
import os, sys, time, json
T = '2'
for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[v] = T
os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                  XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
from pathlib import Path
PN3 = Path(__file__).resolve().parent
sys.path.insert(0, str(PN3)); sys.path.insert(0, str(PN3.parents[1] / 'n2_runs' / 'pn2'))
if os.name == 'nt':   # keep the system awake while this process runs; no effect on results
    import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
import numpy as np
from common2 import *
import avici_patch as ap

OUT_IV = PN3.parent / 'pn3_out' / 'avici_iv'; OUT_IV.mkdir(parents=True, exist_ok=True)
log = open(OUT_IV / 'log.jsonl', 'a', encoding='utf-8')
from partB_run_configs import CONFIGS
SYS = [(s, ci, seed) for s, ci, seed in systems2('EXP2') if CELLS[ci][2] == 'lin']
inputs = {}
for sid, ci, seed in SYS:
    for cond in ('e0', rep_cond(ci)):
        X, t, _ = assemble2(sid, ci, seed, cond)
        inputs[(sid, cond)] = (X, t['x'].shape[1], ci)
print(f'{len(CONFIGS)} configurations x {len(inputs)} inputs', flush=True)
t_all = time.perf_counter()
for name, mode, layers in CONFIGS:
    todo = [(k, v) for k, v in inputs.items() if not (OUT_IV / f'{k[0]}__{k[1]}__{name}.npz').exists()]
    if not todo:
        continue
    model = ap.make_model()
    for (sid, cond), (X, dT, ci) in todo:
        t0 = time.perf_counter()
        status, rec = 'ok', []
        try:
            p, rec = ap.run(model, X, mode=mode, layers=layers, dT=dT)
        except Exception as e:
            status = 'error: ' + repr(e)
        dt = time.perf_counter() - t0
        meta = dict(sys=sid, cond=cond, cfg=name, mode=mode, layers=list(layers), dT=dT, D=int(X.shape[1]), input_sha=sha(X),
                    status=status, runtime_s=round(dt, 2), traced=bool(rec))
        if status == 'ok':
            if name == 'PLAIN':
                p0 = np.asarray(np.load(OUT2 / 'avici' / f'{key2(sid, cond, "plain")}.npz')['probs'])
                meta['bitwise_vs_PN2'] = bool(np.array_equal(p, p0))
            np.savez_compressed(OUT_IV / f'{sid}__{cond}__{name}.npz', probs=p, meta=np.array(json.dumps(meta)))
        log.write(json.dumps(meta) + '\n'); log.flush()
        print(f"[{name}] {sid} {cond} D={X.shape[1]} {dt:.1f}s {status}{' traced' if rec else ''}", flush=True)
print('done', round(time.perf_counter() - t_all, 1), 's', flush=True)
