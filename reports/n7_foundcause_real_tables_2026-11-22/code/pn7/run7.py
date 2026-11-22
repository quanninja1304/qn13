"""P-N7 runner (rules PN7 v1 §2, §6-§10). One process per run; FoundCause jobs run sequentially, nothing in parallel.

usage: run7.py DEV7
       run7.py PN7 --table sachs|wine
DEV7: the DEV5 stand-in table (k0, rerun, adapter at base 42, two Gaussian draws at k = 20, one schedule base) and the
      P-N1 DEV input DEV-c0-r0 at k = 0 for G2.
PN7 : one table: k0, rerun, adapter at base 42, the 20 Gaussian draws at k = 20, four schedule bases. Refuses to run
      without an ok 'pn7_start_<table>' freeze-gate header; before each job, writes 'budget_stop' and exits with code 3
      if more than 3 h have passed since that header.
Early stops (rules §6; exit code 4): the k0 rerun is not bitwise identical to the first k0 call; the adapter at base 42
differs from the package API by more than 1e-6 at k0.
FoundCause as P-N1 (rules §2): package API predict(n_runs=10, temperature=1.0, max_samples=5000), 4 threads.
"""
import os, sys, time, json, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('set', choices=['DEV7', 'PN7'])
    ap.add_argument('--table', choices=['sachs', 'wine'], default=None)
    a = ap.parse_args()
    if a.set == 'PN7' and a.table is None:
        ap.error('PN7 needs --table')
    T = '4'
    for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
        os.environ[v] = T
    os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                      XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
    if os.name == 'nt':   # keep the system awake while this process runs (P-N2 lesson); no effect on results
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
    import numpy as np
    import psutil
    from common7 import (OUT7, BUDGET_S, THREADS, ADAPTER_TOL, COMPARE, jobs7, key7, input_key, base_of, assemble7,
                         load_fc, out_file, load_out, max_abs_diff, bitwise_equal, sha)

    budget_start = None
    run_label = 'dev7' if a.set == 'DEV7' else f'pn7_{a.table}'
    if a.set == 'PN7':
        hp = OUT7 / 'pn7_run_header.json'
        hdr = json.loads(hp.read_text()) if hp.exists() else []
        starts = [h for h in hdr if h['label'] == f'pn7_start_{a.table}' and h['ok']]
        if not starts:
            print(f'REFUSED: no ok pn7_start_{a.table} freeze-gate header; run through run_pn7.sh', flush=True)
            return 1
        budget_start = float(starts[-1]['time_unix'])

    jobs = jobs7(a.set, a.table)
    out_dir = OUT7 / 'foundcause'
    out_dir.mkdir(parents=True, exist_ok=True)
    logp = out_dir / f'log_{run_label}.jsonl'
    done = set()
    if logp.exists():
        for line in logp.read_text(encoding='utf-8').splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get('status') == 'ok':
                    done.add(r['key'])
    todo = [j for j in jobs if key7(j) not in done]
    print(f'{run_label}: {len(jobs)} jobs, {len(todo)} to run', flush=True)
    log = open(logp, 'a', encoding='utf-8')
    proc = psutil.Process()
    t_runner = time.time()
    fn = load_fc() if todo else None
    first_k0 = {}
    for i, j in enumerate(todo):
        key = key7(j)
        if budget_start is not None and time.time() - budget_start > BUDGET_S:
            rec = dict(key=key, status='budget_stop', elapsed_run_s=round(time.time() - budget_start, 1))
            log.write(json.dumps(rec) + '\n'); log.flush()
            print(f'BUDGET STOP before {key}', flush=True)
            return 3
        t0 = time.perf_counter()
        X, dT = assemble7(j)
        rec = dict(key=key, input_key=input_key(j), set=j['set'], table=j['table'], cond=j['cond'], r=j['r'],
                   variant=j['variant'], base=base_of(j), d=int(X.shape[1]), dT=dT, n=int(X.shape[0]),
                   input_sha=sha(X), threads=THREADS)
        stop = None
        try:
            o = fn(X, base_of(j))
            np.savez(out_file(j), meta=np.asarray(json.dumps(rec)), **o)
            status = 'ok'
            if j['cond'] == 'k0' and j['table'] != 'p1dev':
                if j['variant'] != 'api' and j['table'] not in first_k0:     # resumed run: the k0 API output on disk
                    first_k0[j['table']] = load_out(dict(j, variant='api'))
                if j['variant'] == 'api':
                    first_k0[j['table']] = o
                elif j['variant'] == 'rep':
                    rec['rerun_bitwise'] = bool(bitwise_equal(o, first_k0[j['table']]))
                    if not rec['rerun_bitwise']:
                        stop = 'k0 rerun is not bitwise identical (rules §6)'
                elif j['variant'] == 'sched42':
                    dev = {k: max_abs_diff(o[k], first_k0[j['table']][k]) for k in ('probs', 'agreement', 'adj_native')}
                    rec['adapter42_max_abs_diff'] = dev
                    if max(dev.values()) > ADAPTER_TOL:
                        stop = f'adapter at base 42 differs from the API by more than {ADAPTER_TOL} (rules §6)'
        except Exception as e:
            import traceback
            status = 'error: ' + repr(e)
            print(traceback.format_exc(), flush=True)
        mi = proc.memory_info()
        rec.update(status=status, runtime_s=round(time.perf_counter() - t0, 2), rss_mb=round(mi.rss / 2 ** 20, 1),
                   peak_wset_mb=round(getattr(mi, 'peak_wset', 0) / 2 ** 20, 1),
                   elapsed_run_s=round(time.time() - (budget_start or t_runner), 1))
        if stop:
            rec['stop'] = stop
        log.write(json.dumps(rec) + '\n'); log.flush()
        print(f"[{i + 1}/{len(todo)}] {key} d={X.shape[1]} {rec['runtime_s']}s {status} (run {rec['elapsed_run_s']}s)",
              flush=True)
        if status != 'ok':
            return 2
        if stop:
            print(f'STOP: {stop}', flush=True)
            return 4
    return 0


if __name__ == '__main__':
    sys.exit(main())
