"""Recheck of T on the K=70 arm of RG3b_T_vs_whitened_box.py: same SCMs, same seeds, larger node cap, both bounds.

Reason: in the main run T left about 1.16 undecided models per replicate at K=70, n=1000, and undecided models count as surviving, so cert_T = 0.28
was only a lower bound. Here cert_lower counts undecided models as surviving and cert_upper counts them as rejected. No method other than T is rerun.
Writes RG3b_k70_recheck.json.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bb", HERE / "RG3b_T_vs_whitened_box.py")
bb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bb)
g3, fu, rg, SEED = bb.g3, bb.fu, bb.rg, bb.SEED


def job(j):
    qs, R, n, beta, truth, usable, PI, notf, lamT, seed, N, cap, scm = j
    K = len(qs)
    rng = np.random.default_rng(seed)
    Z, Sh, _ = rg.batch_z_sigma(rg.sample_cov_batch(R, n, N, rng), qs, n)
    nk = np.array([n - len(S) - 3 for (_, _, S) in qs], float)
    delta = np.sqrt(nk) * beta
    false_tg = (~truth) & notf.any(axis=0)
    relevant = usable | false_tg
    order = np.argsort(-(notf & relevant).sum(axis=1))
    tail = rg.WeightedTail(K, SEED + 3 + K)
    I_all = np.arange(K)
    lo = up = am = fw_up = 0.0
    done = 0
    t0 = time.time()
    for b in range(N):
        if time.time() - t0 > cap:
            break
        done += 1
        z, S_ = Z[b], Sh[b]
        az = np.abs(z)
        sup = np.maximum((az * PI).max(axis=1), (np.maximum(delta - az, 0) * (~PI)).max(axis=1))
        Wsq, wts = rg.metric_ridge(S_, lamT)
        w_s = np.sort(wts)[::-1]
        chat = tail.quantile(w_s[w_s > 1e-10])
        cache = {}

        def st(i):
            if i not in cache:
                if sup[i] ** 2 / (1 + lamT) > chat:
                    cache[i] = "reject"
                else:
                    I = I_all[PI[i]]
                    if len(I) and float(z[I] @ np.linalg.solve(S_[np.ix_(I, I)] + lamT * np.eye(len(I)), z[I])) > chat:
                        cache[i] = "reject"
                    else:
                        val, _, proven = g3.d2_exact(z, delta, Wsq, PI[i], node_cap=3000, stop_below=chat)
                        cache[i] = "accept" if val <= chat else ("reject" if proven else "ambiguous")
            return cache[i]

        a_lo, n_amb = bb.decide_family(st, order, notf, relevant)
        a_up, _ = bb.decide_family(lambda i: "reject" if st(i) == "ambiguous" else st(i), order, notf, relevant)
        d_u = max(int(usable.sum()), 1)
        lo += float((a_lo & usable).sum()) / d_u
        up += float((a_up & usable).sum()) / d_u
        am += n_amb
        fw_up += bool((a_up & false_tg).any())
    d = max(done, 1)
    return {"scm": scm, "n": n, "reps": done, "cert_lower": lo / d, "cert_upper": up / d, "ambiguous": am / d, "FWER_upper": fw_up / d, "seconds": time.time() - t0, "beta": beta}


def main():
    rng = np.random.default_rng(SEED)
    qs4, qs5 = rg.all_queries(4, 2), rg.all_queries(5, 2)
    fam4 = g3.FamilyL(4, qs4, latent=True)
    bb.random_truths(fam4, qs4, 6, rng)       # stage 0 draws
    bb.random_truths(fam4, qs4, 40, rng)      # primary draws
    jobs = []
    got = 0
    while got < 12:
        B = np.zeros((5, 5))
        order = rng.permutation(5)
        for a, b_ in itertools.combinations(range(5), 2):
            if rng.random() < .3:
                B[order[b_], order[a]] = rng.choice([-1, 1]) * rng.uniform(.2, .8)
        A = B.T != 0
        if A.sum() == 0:
            continue
        R = g3.build_truth(5, B)
        rho = rg.rho_vec(R, qs5)
        pst = g3.pattern_truth(A, None, qs5)
        if not all((abs(rho[k]) > 1e-9) == (pst[k] == 0) for k in range(70)):
            continue
        fam = fu.Family(fu.local_dags(A, 2), qs5)
        truth = ~fam.false_at(A)
        usable = truth & (~fam.notf[fam.pid[pst]]) & fam.notf.any(axis=0)
        if not usable.any():
            continue
        beta = min(abs(math.atanh(rho[k])) for k in range(70) if pst[k] == 0)
        for n in (1000, 5000):
            jobs.append((qs5, R, n, beta, truth, usable, fam.PI, fam.notf, .5, SEED + 4000 + got * 7 + n, 30, 240, got))
        got += 1
    main_run = json.loads((HERE / "RG3b_outputs.json").read_text(encoding="utf-8"))["K70"]
    stored = {(r["scm"], r["n"]): r for r in main_run}
    for j in jobs:
        assert abs(stored[(j[12], j[2])]["beta"] - j[3]) < 1e-12, "SCM mismatch with the main run"
    print("SCMs match the main run (beta identical)", flush=True)
    rows = []
    with ProcessPoolExecutor(3) as ex:
        for r in ex.map(job, jobs):
            m = stored[(r["scm"], r["n"])]
            r["main_cert_T"], r["main_reps"] = m["cert"]["T"], m["reps"]
            r["W_zca"], r["W_innov"], r["BoxMaxT"], r["BL1"] = m["cert"]["W_zca"], m["cert"]["W_innov"], m["cert"]["BoxMaxT"], m["cert"]["BL1"]
            rows.append(r)
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
            (HERE / "RG3b_k70_recheck.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    for n in (1000, 5000):
        s = [r for r in rows if r["n"] == n]
        print("MEAN n=", n, {k: round(float(np.mean([r[k] for r in s])), 3) for k in ("cert_lower", "cert_upper", "main_cert_T", "W_zca", "W_innov", "BoxMaxT", "BL1", "ambiguous", "FWER_upper")}, flush=True)


if __name__ == "__main__":
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    main()
