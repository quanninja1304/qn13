"""P-N3 Part B gates B0-B5 (rules v1 §2). Runs before the code freeze; no pilot contrast is computed here.

usage: partB_gates.py  ->  pn3_out/partB_gates.json  (exit 1 if B0-B4 fail)
"""
import os, sys, time, json
T = '2'
for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[v] = T
os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                  XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / 'n2_runs' / 'pn2'))
import numpy as np
from common2 import *            # frozen P-N2 (EXP2 systems, inputs)
import avici_patch as ap

OUT3 = Path(ap.__file__).resolve().parents[1] / 'pn3_out'; OUT3.mkdir(parents=True, exist_ok=True)   # not HERE: common2 * import rebinds it
res, bad = {}, []
S = {s: (ci, seed) for s, ci, seed in systems2('EXP2')}
SYS_G = ['EXP2-c0-r0', 'EXP2-c2-r0']           # linear cells (10, 1, lin) and (10, 2, lin)

# B1: parameter tree identical in names, shapes and values to a fresh load of the checkpoint
import jax, avici
base = ap.base_model()
fresh = avici.load_pretrained(checkpoint_dir=str(ap.ENV / 'checkpoints/avici/scm-v0'), expects_counts=False)
la, ta = jax.tree_util.tree_flatten_with_path(base.params); lb, tb = jax.tree_util.tree_flatten_with_path(fresh.params)
same_struct = ta == tb and [str(p) for p, _ in la] == [str(p) for p, _ in lb]
same_vals = same_struct and all(np.asarray(x).shape == np.asarray(y).shape and np.array_equal(np.asarray(x), np.asarray(y))
                                for (_, x), (_, y) in zip(la, lb))
res['B1'] = dict(n_leaves=len(la), same_structure=bool(same_struct), same_values=bool(same_vals))
if not same_vals:
    bad.append('B1')

# inputs and original outputs (P-N2 EXP2 plain, produced by run2.py with the same threads/flags)
def orig(sid, cond):
    z = np.load(OUT2 / 'avici' / f'{key2(sid, cond, "plain")}.npz')
    return np.asarray(z['probs']), json.loads(str(z['meta']))

inputs = {}
for sid in SYS_G:
    ci, seed = S[sid]
    for cond in ('k0', 'e0', rep_cond(ci)):
        X, t, _ = assemble2(sid, ci, seed, cond)
        p0, meta = orig(sid, cond)
        assert meta['input_sha'] == sha(X), f'input sha mismatch {sid} {cond}'
        inputs[(sid, cond)] = (X, t['x'].shape[1], p0)

timing = []
def timed(model, X, **kw):
    t0 = time.perf_counter(); p, rec = ap.run(model, X, **kw); return p, rec, time.perf_counter() - t0

# B0 (PLAIN reproduces original outputs bitwise) and B4 (layer identification)
plain = ap.make_model(); b0, b4 = [], []
for (sid, cond), (X, dT, p0) in inputs.items():
    p, rec, dt = timed(plain, X, mode='PLAIN', dT=dT)
    b0.append(dict(sys=sid, cond=cond, bitwise=bool(np.array_equal(p, p0)), max_abs=float(np.abs(p - p0).max())))
    timing.append(dict(cfg='PLAIN', D=X.shape[1], seconds=round(dt, 2), traced=bool(rec)))
    if rec:
        D, n = X.shape[1], X.shape[0]
        ok = len(rec) == 16 and all((sl == D) if va else (sl == n) for _, va, sl in rec) and sum(va for _, va, _ in rec) == 8
        b4.append(dict(D=D, n_calls=len(rec), n_variable_axis=sum(va for _, va, _ in rec), axis_lengths_ok=bool(ok)))
res['B0'] = b0; res['B4'] = b4
if not all(x['bitwise'] for x in b0): bad.append('B0')
if not b4 or not all(x['axis_lengths_ok'] for x in b4): bad.append('B4')

# B2 (KO-all on padded inputs reproduces k0 target probabilities) and B3 (no-op at k0 for V0-all, KO-all)
ALL = range(1, 9)
b2, b3 = [], []
for mode in ('KO', 'V0'):
    mdl = ap.make_model()
    for (sid, cond), (X, dT, p0) in inputs.items():
        p, rec, dt = timed(mdl, X, mode=mode, layers=ALL, dT=dT)
        timing.append(dict(cfg=f'{mode}-all', D=X.shape[1], seconds=round(dt, 2), traced=bool(rec)))
        if cond == 'k0':
            b3.append(dict(mode=mode, sys=sid, bitwise_vs_plain=bool(np.array_equal(p, inputs[(sid, 'k0')][2]))))
        elif mode == 'KO':
            pk0 = inputs[(sid, 'k0')][2]
            b2.append(dict(sys=sid, cond=cond, max_abs_target_vs_k0=float(np.abs(p[:dT, :dT] - pk0).max())))
res['B2'] = b2; res['B3'] = b3
if not all(x['max_abs_target_vs_k0'] <= 1e-6 for x in b2): bad.append('B2')
if not all(x['bitwise_vs_plain'] for x in b3): bad.append('B3')

# B5 timing: one single-layer config to measure compile + cached run, then estimate the full pilot
mdl = ap.make_model(); X, dT, _ = inputs[('EXP2-c0-r0', 'e0')]
p, rec, t_first = timed(mdl, X, mode='V0', layers=[3], dT=dT)
p, rec2, t_cached = timed(mdl, X, mode='V0', layers=[3], dT=dT)
compile_s = max(t_first - t_cached, 0.0)
n_cfg, n_shapes, n_runs = 19, 2, 20 * 2 * 19 + 20
est_h = (n_cfg * n_shapes * compile_s + n_runs * max(t_cached, 4.6)) / 3600   # 4.6 s = P-N2 mean AVICI run time at k = 20
res['B5'] = dict(first_call_s=round(t_first, 2), cached_call_s=round(t_cached, 2), compile_s_est=round(compile_s, 2),
                 estimate_hours=round(est_h, 2), over_3h=bool(est_h > 3), timing=timing)
res['ok'] = not bad; res['failed'] = bad
(OUT3 / 'partB_gates.json').write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != 'B5'}, indent=1)); print('B5', {k: v for k, v in res['B5'].items() if k != 'timing'})
sys.exit(1 if bad else 0)
