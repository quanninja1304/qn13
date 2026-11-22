"""P-N5 runner (rules PN5 v1 §3): one run per (algorithm, input), in the locked order, with the locked job states.

AVICI and CDFM are loaded and called as in the frozen P-N2 runner run2.py (2 threads; inputs already z-scored per column;
CDFM from_pretrained(threshold=None), predict(x, threshold=None, standardize=False)).
PC and GES are called as in run2_classical.py (1 thread). Each job runs in a worker process with a 900 s limit:
  over the limit -> 'timeout'. Allowed only on descriptive inputs; on a main input (k0, its rerun, k20_e0) the runner stops.
Budget (rules §3): PN5 only. Before each job, if more than 3 h have passed since the first ok 'pn5_start' header of the
freeze gate, the runner writes a 'budget_stop' record and stops.
Every job ends with exactly one record: ok, timeout or error. A job with an ok or timeout record is never rerun.
usage: run5.py <avici|cdfm|pc|ges> <PN5|DEV5> [--limit N]
  -> pn5_out/<alg>/<key>.npz (arrays + meta), pn5_out/<alg>/log_<set>.jsonl
exit codes: 0 done; 1 refused; 2 stopped by a main-input timeout; 3 budget stop.
"""
import os, sys, time, json, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('alg', choices=['avici', 'cdfm', 'pc', 'ges']); ap.add_argument('set', choices=['PN5', 'DEV5'])
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    T = '2' if a.alg in ('avici', 'cdfm') else '1'
    for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
        os.environ[v] = T
    os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                      XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
    if os.name == 'nt':   # keep the system awake while this process runs (P-N2 lesson); no effect on results
        import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
    import numpy as np
    import psutil
    from common5 import (ART, OUT5, MAIN, LIMIT_S, BUDGET_S, jobs5, key5, assemble5, draw_seed, sha, xr_file)

    budget_start = None
    if a.set == 'PN5':
        hp = OUT5 / 'pn5_run_header.json'
        hdr = json.loads(hp.read_text()) if hp.exists() else []
        starts = [h for h in hdr if h['label'] == 'pn5_start' and h['ok']]
        if not starts:
            print('REFUSED: no ok pn5_start freeze-gate header; run through run_pn5.sh', flush=True)
            return 1
        budget_start = float(starts[0]['time_unix'])

    out_dir = OUT5 / a.alg
    out_dir.mkdir(parents=True, exist_ok=True)
    logp = out_dir / f'log_{a.set}.jsonl'
    ended = set()
    if logp.exists():
        for l in logp.read_text(encoding='utf-8').splitlines():
            if l.strip():
                r_ = json.loads(l)
                if r_.get('status') in ('ok', 'timeout'):
                    ended.add(r_['key'])
    jobs = [j for j in jobs5(a.set, a.alg, extra_rep=(a.set == 'DEV5')) if key5(*j) not in ended]
    if a.limit:
        jobs = jobs[:a.limit]
    print(f'{a.alg} {a.set}: {len(jobs)} to run', flush=True)
    if not jobs:
        return 0
    log = open(logp, 'a', encoding='utf-8')
    proc = psutil.Process()
    t_runner = time.time()
    ENV = ART / 'n1_models_cpu'

    fn, pool, ctx = None, None, None
    if a.alg == 'avici':
        import avici
        m = avici.load_pretrained(checkpoint_dir=str(ENV / 'checkpoints/avici/scm-v0'), expects_counts=False)
        fn = lambda x: dict(probs=np.asarray(m(x=x), dtype=np.float64))
    elif a.alg == 'cdfm':
        import torch; torch.set_num_threads(int(T))
        from cdfm import CDFM
        mdl = CDFM.from_pretrained(str(ENV / 'checkpoints/cdfm'), device='cpu', threshold=None)

        def fn(x):
            r = mdl.predict(x, threshold=None, standardize=False)
            return dict(probs=np.asarray(r.probabilities, np.float64), logits=np.asarray(r.logits, np.float64),
                        adj_native=np.asarray(r.adjacency, np.int8), threshold=float(r.threshold))
    else:
        import multiprocessing as mp
        from classical5 import run_classical, worker_peak_mb
        ctx = mp.get_context('spawn')
        pool = ctx.Pool(1)

    rc = 0
    for i, (table, cond, r, rep) in enumerate(jobs):
        key = key5(table, cond, r, rep)
        if budget_start is not None and time.time() - budget_start > BUDGET_S:
            rec = dict(key=key, set=a.set, alg=a.alg, status='budget_stop', elapsed_run_s=round(time.time() - budget_start, 1))
            log.write(json.dumps(rec) + '\n'); log.flush()
            print(f'BUDGET STOP before {key}: {rec["elapsed_run_s"]} s since pn5_start > {BUDGET_S} s', flush=True)
            rc = 3
            break
        X, rb, pad = assemble5(a.set, table, cond, r)
        xf = xr_file(table)
        if not xf.exists() or sha(np.load(xf)) != rb['XR_sha']:
            print(f'REFUSED: X_R of {table} differs from the saved gate copy {xf.name}', flush=True)
            rc = 1
            break
        rec = dict(key=key, set=a.set, alg=a.alg, table=table, cond=cond, r=r, rep=rep, main=cond in MAIN,
                   d=int(X.shape[1]), dT=int(rb['XR'].shape[1]), input_sha=sha(X), xr_sha=rb['XR_sha'],
                   seed=None if pad is None else draw_seed(a.set, table, r),
                   pad_edges=None if pad is None else pad['n_edges'], pad_isolated=None if pad is None else pad['n_isolated'],
                   threads=int(T))
        arrays, worker_mb = {}, None
        t0 = time.perf_counter()
        if pool is None:
            try:
                arrays = fn(X)
                status = 'ok'
            except Exception as ex:
                import traceback
                status = 'error: ' + repr(ex)
                print(traceback.format_exc(), flush=True)
        else:
            res = pool.apply_async(run_classical, (a.alg, X))
            try:
                arrays = dict(skel=res.get(timeout=LIMIT_S))
                status = 'ok'
                try:
                    worker_mb = pool.apply_async(worker_peak_mb).get(timeout=60)
                except Exception:
                    worker_mb = None
            except mp.TimeoutError:
                pool.terminate(); pool.join(); pool = ctx.Pool(1)
                status = 'timeout'
            except Exception as ex:
                status = 'error: ' + repr(ex)
        mi = proc.memory_info()
        rec.update(status=status, runtime_s=round(time.perf_counter() - t0, 2), rss_mb=round(mi.rss / 2 ** 20, 1),
                   peak_wset_mb=round(getattr(mi, 'peak_wset', 0) / 2 ** 20, 1), worker_peak_wset_mb=worker_mb,
                   elapsed_run_s=round(time.time() - (budget_start or t_runner), 1))
        if status == 'ok':
            np.savez_compressed(out_dir / f'{key}.npz', meta=np.array(json.dumps(rec, default=int)), **arrays)
        log.write(json.dumps(rec, default=int) + '\n'); log.flush()
        print(f"[{i + 1}/{len(jobs)}] {key} d={X.shape[1]} {rec['runtime_s']}s {status} (run {rec['elapsed_run_s']}s)", flush=True)
        if status == 'timeout' and rec['main']:
            print(f'STOP: timeout on a main input ({key}); rules PN5 §3 require stopping and reporting', flush=True)
            rc = 2
            break
    if pool is not None:
        pool.close(); pool.join()
    log.close()
    return rc


if __name__ == '__main__':
    sys.exit(main())
