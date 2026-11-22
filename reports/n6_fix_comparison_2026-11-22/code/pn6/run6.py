"""P-N6 runner (rules PN6 v1 §3, §10). One process per (task, set); jobs run sequentially.

usage: run6.py <pvals|avici|cdfm> <PN6|DEV6> [plain|RL|RH|fullRL|fullRH|oracle|rep] [--limit N]
  pvals  : HSIC p-values (frozen P-N2 p_hsic) of every input of the set, cached in pn6_out/pvals/; no model
  plain  : model on the whole input (synthetic inputs only)
  RL, RH : pairwise decisions with the locked alpha (pn6_out/alpha6.json), connected components, model on every
           component that contains a target variable (the evaluated outputs); for PN6 also the real-table inputs
  fullRL, fullRH (DEV6): as RL/RH, and the model also runs on every other component with >= 2 variables, to time the
           target-agnostic pipeline (rules §10, G9); only timings are used
  oracle (DEV6): model on the target block alone of padded inputs (G4)
  rep    (DEV6): reruns of one k0 and one padded input for plain, RL and RH (G8)
Model calls as P-N1, P-N2 and P-N5 (rules §3): AVICI scm-v0 (expects_counts=False); CDFM threshold=None,
predict(threshold=None, standardize=False); 2 threads. Component inputs are the table's columns, unchanged.
PN6 only: refuses to run without an ok 'pn6_start' freeze-gate header; before each job, writes 'budget_stop' and exits
with code 3 if more than 3 h have passed since that header.
"""
import os, sys, time, json, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ORACLE_KEYS = (('DEV6-c0-r0', 'e0'), ('DEV6-c0-r0', 'e1'), ('DEV6-c7-r1', 'e0'), ('DEV6-c7-r1', 'e2'))
REP_KEYS = (('DEV6-c0-r0', 'k0'), ('DEV6-c7-r1', 'e2'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('task', choices=['pvals', 'avici', 'cdfm']); ap.add_argument('set', choices=['PN6', 'DEV6'])
    ap.add_argument('arm', nargs='?', default=None, choices=[None, 'plain', 'RL', 'RH', 'fullRL', 'fullRH', 'oracle', 'rep'])
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    if a.task != 'pvals' and a.arm is None:
        ap.error('model tasks need an arm')
    if a.arm in ('fullRL', 'fullRH', 'oracle', 'rep') and a.set != 'DEV6':
        ap.error(f'{a.arm} runs on DEV6 only')
    T = '2'
    for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
        os.environ[v] = T
    os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                      XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
    if os.name == 'nt':   # keep the system awake while this process runs (P-N2 lesson); no effect on results
        import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
    import numpy as np
    import psutil
    from common6 import (ART, OUT6, BUDGET_S, items6, syn_items, base_key, key6, k0_of, assemble6, pval_file,
                         load_pvals, reject, alphas, target_components, screen_stats, sha, SCR)

    budget_start = None
    if a.set == 'PN6':
        hp = OUT6 / 'pn6_run_header.json'
        hdr = json.loads(hp.read_text()) if hp.exists() else []
        starts = [h for h in hdr if h['label'] == 'pn6_start' and h['ok']]
        if not starts:
            print('REFUSED: no ok pn6_start freeze-gate header; run through run_pn6.sh', flush=True)
            return 1
        budget_start = float(starts[0]['time_unix'])

    # ---- job list
    if a.task == 'pvals':
        jobs = [(it, None) for it in items6(a.set)]
        out_dir, logname = OUT6 / 'pvals', f'log_{a.set}.jsonl'
    else:
        arm = a.arm
        if arm == 'plain':
            jobs = [(it, 'plain') for it in syn_items(a.set)]
        elif arm in ('RL', 'RH'):
            jobs = [(it, arm) for it in items6(a.set)]
        elif arm in ('fullRL', 'fullRH'):
            jobs = [(it, arm) for it in syn_items('DEV6')]
        elif arm == 'oracle':
            jobs = [(it, 'oracle') for it in syn_items('DEV6') if (it['sid'], it['cond']) in ORACLE_KEYS]
        else:
            jobs = [(it, f'{b}__rep') for b in ('plain', 'RL', 'RH') for it in syn_items('DEV6') if (it['sid'], it['cond']) in REP_KEYS]
        out_dir, logname = OUT6 / a.task, f'log_{a.set}_{arm}.jsonl'
    out_dir.mkdir(parents=True, exist_ok=True)
    logp = out_dir / logname
    keyf = (lambda it, arm: base_key(it)) if a.task == 'pvals' else key6
    done = set()
    if logp.exists():
        for l in logp.read_text(encoding='utf-8').splitlines():
            if l.strip():
                r_ = json.loads(l)
                if r_.get('status') == 'ok':
                    done.add(r_['key'])
    jobs = [j for j in jobs if keyf(*j) not in done]
    if a.limit:
        jobs = jobs[:a.limit]
    print(f'{a.task} {a.set} {a.arm or ""}: {len(jobs)} to run', flush=True)
    if not jobs:
        return 0
    log = open(logp, 'a', encoding='utf-8')
    proc = psutil.Process()
    t_runner = time.time()

    fn = None
    if a.task != 'pvals':
        ENV = ART / 'n1_models_cpu'
        if a.task == 'avici':
            import avici
            m = avici.load_pretrained(checkpoint_dir=str(ENV / 'checkpoints/avici/scm-v0'), expects_counts=False)
            fn = lambda x: dict(probs=np.asarray(m(x=x), dtype=np.float64))
        else:
            import torch; torch.set_num_threads(int(T))
            from cdfm import CDFM
            mdl = CDFM.from_pretrained(str(ENV / 'checkpoints/cdfm'), device='cpu', threshold=None)

            def fn(x):
                r = mdl.predict(x, threshold=None, standardize=False)
                return dict(probs=np.asarray(r.probabilities, np.float64), logits=np.asarray(r.logits, np.float64),
                            adj_native=np.asarray(r.adjacency, np.int8), threshold=float(r.threshold))
        al = alphas() if a.arm not in ('plain', 'oracle') else None

    for i, (it, arm) in enumerate(jobs):
        key = keyf(it, arm)
        if budget_start is not None and time.time() - budget_start > BUDGET_S:
            rec = dict(key=key, set=a.set, task=a.task, arm=arm, status='budget_stop', elapsed_run_s=round(time.time() - budget_start, 1))
            log.write(json.dumps(rec) + '\n'); log.flush()
            print(f'BUDGET STOP before {key}', flush=True)
            return 3
        X, dT, info = assemble6(it)
        rec = dict(key=key, set=a.set, task=a.task, arm=arm, kind=it['kind'], cond=it['cond'],
                   sys=it.get('sid'), table=it.get('table'), r=it.get('r'), d=int(X.shape[1]), dT=dT, input_sha=sha(X))
        arrays, t0 = {}, time.perf_counter()
        try:
            if a.task == 'pvals':
                p = SCR.p_hsic(X)
                meta = dict(input_sha=rec['input_sha'], D=int(X.shape[1]), dT=dT, seconds=round(time.perf_counter() - t0, 3))
                np.savez(pval_file(it), p=p, meta=np.asarray(json.dumps(meta)))
            else:
                base_arm = arm.replace('__rep', '').replace('full', '')
                if base_arm == 'plain':
                    arrays = fn(X)
                elif base_arm == 'oracle':
                    arrays = fn(np.ascontiguousarray(X[:, :dT]))
                else:
                    p, pm = load_pvals(it)
                    if pm['input_sha'] != rec['input_sha']:
                        raise RuntimeError('cached p-values belong to another input')
                    R = reject(p, base_arm, al[base_arm])
                    lab = SCR.components(R)
                    st = screen_stats(lab, R, dT, info['g'])
                    probs_T = np.zeros((dT, dT)); adj_T = np.zeros((dT, dT), np.int8)
                    thr_c, comps, comp_sha, calls, tm = [], [], [], 0, 0.0
                    for idx in target_components(lab, dT):
                        comps.append([int(v) for v in idx])
                        if len(idx) < 2:
                            continue
                        xi = np.ascontiguousarray(X[:, idx])
                        comp_sha.append(sha(xi))
                        tc = time.perf_counter(); r = fn(xi); tm += time.perf_counter() - tc; calls += 1
                        loc = [q for q, v in enumerate(idx) if v < dT]
                        tv = idx[loc]
                        probs_T[np.ix_(tv, tv)] = r['probs'][np.ix_(loc, loc)]
                        if a.task == 'cdfm':
                            adj_T[np.ix_(tv, tv)] = r['adj_native'][np.ix_(loc, loc)]
                            thr_c.append(r['threshold'])
                    other_s, n_other = 0.0, 0
                    if arm.startswith('full'):
                        tl = set(lab[:dT].tolist())
                        for L in sorted(set(lab.tolist()) - tl):
                            idx = np.where(lab == L)[0]
                            if len(idx) >= 2:
                                tc = time.perf_counter(); fn(np.ascontiguousarray(X[:, idx])); other_s += time.perf_counter() - tc; n_other += 1
                    arrays = dict(probs_T=probs_T, labels=lab.astype(np.int64), target_decisions=R[:dT, :dT].astype(np.uint8),
                                  comp_sha=np.asarray(comp_sha, dtype='<U64'))
                    if a.task == 'cdfm':
                        arrays.update(adj_T=adj_T, thr_components=np.asarray(thr_c, np.float64))
                    rec.update(alpha=al[base_arm], n_model_calls=calls, target_components=comps, model_s=round(tm, 3),
                               other_components_s=round(other_s, 3), n_other_components=n_other, pvals_s=pm['seconds'], **st)
                np.savez(out_dir / f'{key}.npz', meta=np.asarray(json.dumps(rec)), **arrays)
            status = 'ok'
        except Exception as e:
            import traceback
            status = 'error: ' + repr(e)
            print(traceback.format_exc(), flush=True)
        mi = proc.memory_info()
        rec.update(status=status, runtime_s=round(time.perf_counter() - t0, 2), rss_mb=round(mi.rss / 2 ** 20, 1),
                   peak_wset_mb=round(getattr(mi, 'peak_wset', 0) / 2 ** 20, 1),
                   elapsed_run_s=round(time.time() - (budget_start or t_runner), 1))
        log.write(json.dumps(rec) + '\n'); log.flush()
        print(f"[{i + 1}/{len(jobs)}] {key} d={X.shape[1]} {rec['runtime_s']}s {status} (run {rec['elapsed_run_s']}s)", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
