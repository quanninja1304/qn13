"""Decisive comparison before RG2: the ellipsoid statistic T against box confidence regions after whitening. See RG3b_report_vi.md.

All methods are the same test inversion (Thm 1): reject m if no u in R_n^eta(m) lies in the confidence region for zeta_n.
  T      : ||A^{-1/2}(z-u)||^2 <= c_hat            A = Sigma_hat + lambda I, c_hat weighted chi-square (Thm 3, lambda = max(n^-1/3, .1) at K=24, .5 at K=70)
  W_innov: max_k |(A^-1 (z-u))_k| / s_k <= t       s_k^2 = (A^-1 Sigma_hat A^-1)_kk, t = simulated MaxT .95 quantile given Sigma_hat
  W_zca  : same with A^{-1/2} in place of A^-1
  BoxMaxT: max_k |z_k-u_k| <= t, no whitening, simulated MaxT quantile (closed form)
  BL1    : max_k |z_k-u_k| <= t_K, Bonferroni (closed form)

READING RULES, FIXED BEFORE THE FULL RUN (project-management choices, not statistical standards). One quick run (6 SCMs, 2-10 reps per SCM) came
first and changed two things, neither related to which method wins: stage 0 went from 800 to 3000 replicates, since the maximum over many truths of
a correct 0.05 procedure would often exceed 0.065 at 800; and the size condition on the primary runs became alpha + 3 SE instead of a flat 0.065,
since those runs have few replicates. A cheap infeasibility certificate was added to speed up the LPs; it cannot change any decision.
  Stage 0 picks lambda_W using size only, with no power measured: the smallest lambda in {.1,.25,.5,1,2} whose largest size over the stage-0
    truths at n >= 500 is at most 0.065. If none qualifies, lambda = 2 and the method is flagged. W_innov is the primary box; W_zca is secondary.
  Primary comparison: 40 fresh random SCMs, p=4, K=24, eta = beta, n in {500, 1000, 2000}, mean paired difference in certification over SCMs.
    "T clear"  : T - W_innov >= +0.05 and diff - 2 SE > 0 at 2 or more of the 3 n.
    "W clear"  : T - W_innov <= -0.05 and diff + 2 SE < 0 at 2 or more of the 3 n.
    otherwise  : "no clear difference".
    "neither beats BL1": for both T and W_innov, at every n, diff to BL1 < 0.05 or diff - 2 SE <= 0.
    A method whose pooled FWER or pooled size exceeds alpha + 3 SE at some n cannot be declared clear.
  Mapping: T clear -> RG2 with T and chi-bar. W clear or no clear difference -> chi-square shape is unnecessary, reassess novelty before investing.
    Neither beats BL1 -> negative-result memo, move to T4.
  Secondary, descriptive only: K=70 arm on local DAG families; the two S1 scenarios; W_zca; BoxMaxT.

Models that the bounded search cannot decide count as surviving for every method, so certification is a lower bound and false assertions are not
inflated. BoxMaxT and BL1 are exact. Exploratory: RG2, if it happens, must use fresh SCMs and seeds.

Run: python -P -E RG3b_T_vs_whitened_box.py [--quick] [--resume] [--workers=N]
--resume reuses stage 0 and the finished primary rows of RG3b_outputs.json. SCM draws and job seeds are deterministic, so resuming draws the same SCMs.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("g3", HERE / "RG3_S1_checks.py")
g3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g3)
fu, rg = g3.fu, g3.rg

QUICK = "--quick" in sys.argv
SEED = 20261107
ALPHA = 0.05
WORKERS = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--workers=")), 3)
RESUME = "--resume" in sys.argv
LAMS = (.1, .25, .5, 1.0, 2.0)
OUT = HERE / "RG3b_outputs.json"
_G0 = {}


def g0(K, M):
    key = (K, M)
    if key not in _G0:
        _G0[key] = np.random.default_rng(SEED + 77 + K).standard_normal((M, K))
    return _G0[key]


def whiten(S_, lam, kind):
    """Return (Mat, s, draws) for the box |Mat (z-u)|_k <= t s_k; draws are row vectors with covariance Mat Sigma Mat'."""
    w, V = np.linalg.eigh(S_)
    w = np.clip(w, 0, None)
    if kind == "innov":
        Mat = (V / (w + lam)) @ V.T
        root = V * (np.sqrt(w) / (w + lam))
    elif kind == "zca":
        Mat = (V / np.sqrt(w + lam)) @ V.T
        root = V * (np.sqrt(w) / np.sqrt(w + lam))
    else:
        Mat = np.eye(len(w))
        root = V * np.sqrt(w)
    s = np.sqrt(np.maximum(np.sum(root**2, axis=1), 1e-14))
    return Mat, s, root


def maxt(root, s, M=3000, alpha=ALPHA):
    G = g0(root.shape[0], M)
    return float(np.quantile(np.max(np.abs(G @ root.T) / s, axis=1), 1 - alpha))


def lp_feasible(Mat_D, lo, hi, bounds, c):
    res = optimize.linprog(c, A_ub=np.vstack([Mat_D, -Mat_D]), b_ub=np.concatenate([hi, -lo]), bounds=bounds, method="highs")
    if res.status == 0:
        return True, res.x
    return False, None


def box_status(z, Mat, s, t, pat, delta, node_cap=30, Ainv=None):
    """Is there u in R(pat) with |Mat(z-u)|_k <= t s_k for all k? Returns 'accept', 'reject' or 'ambiguous'.

    Ainv = Mat^-1. With y = Mat(z-u) the block I needs (Ainv y)_I = z_I, so for any c supported on I, |c'z| <= t sum_j |(Ainv'c)_j| s_j.
    A violation proves infeasibility without an LP (Farkas certificate); it only skips LPs that would answer the same."""
    if Ainv is not None:
        I = np.where(pat)[0]
        if len(I):
            cc = np.zeros(len(z))
            cc[I] = np.linalg.solve(Ainv[np.ix_(I, I)], z[I])
            if abs(cc[I] @ z[I]) > t * float(np.abs(Ainv.T @ cc) @ s) * (1 + 1e-9):
                return "reject"
    a = Mat @ z
    lo, hi = a - t * s, a + t * s
    D = np.where(~pat)[0]
    if len(D) == 0:
        return "accept" if ((lo <= 0) & (hi >= 0)).all() else "reject"
    M_D = Mat[:, D]
    dd = delta[D]
    s0 = np.where(z[D] >= 0, 1.0, -1.0)
    c = -s0

    def bnds(sg):
        return [(dd[j], None) if sg[j] > 0 else ((None, -dd[j]) if sg[j] < 0 else (None, None)) for j in range(len(D))]

    ok, _ = lp_feasible(M_D, lo, hi, bnds(s0), c)
    if ok:
        return "accept"
    ok, x = lp_feasible(M_D, lo, hi, bnds(np.zeros(len(D))), c)
    if not ok:
        return "reject"
    stack = [np.zeros(len(D))]
    nodes = 0
    while stack:
        if nodes >= node_cap:
            return "ambiguous"
        nodes += 1
        sg = stack.pop()
        ok, x = lp_feasible(M_D, lo, hi, bnds(sg), -np.where(sg != 0, sg, s0))
        if not ok:
            continue
        viol = np.where((sg == 0) & (np.abs(x) < dd - 1e-9))[0]
        if len(viol) == 0:
            return "accept"
        j = viol[np.argmax(dd[viol] - np.abs(x[viol]))]
        for sign in (1.0, -1.0):
            ch = sg.copy()
            ch[j] = sign
            stack.append(ch)
    return "reject"


def decide_family(status_fn, order, notf, relevant):
    covered = np.zeros(notf.shape[1], bool)
    any_surv = False
    amb = 0
    for i in order:
        if not (notf[i] & relevant & ~covered).any():
            continue
        r = status_fn(i)
        if r != "reject":
            covered |= notf[i]
            any_surv = True
            amb += r == "ambiguous"
    asserted = (relevant & ~covered) if any_surv else np.zeros(notf.shape[1], bool)
    return asserted, amb


def job_size(job):
    """Stage 0: size of the box statistic at the true zeta_n."""
    R, qs, n, N, lam, kind, seed = job
    rng = np.random.default_rng(seed)
    Z, Sh, _ = rg.batch_z_sigma(rg.sample_cov_batch(R, n, N, rng), qs, n)
    zeta = rg.pop_zeta(R, qs, n)
    rej = 0
    for b in range(N):
        Mat, s, root = whiten(Sh[b], lam, kind)
        rej += float(np.max(np.abs(Mat @ (Z[b] - zeta)) / s)) > maxt(root, s)
    return {"K": len(qs), "n": n, "lambda": lam, "kind": kind, "size": rej / N, "reps": N}


def job_eval(job):
    """Evaluate all methods on one SCM at one n, on the same replicates."""
    qs, R, n, beta, truth, usable, PI, notf, lamT, lamW, seed, N, cap = job
    K = len(qs)
    rng = np.random.default_rng(seed)
    Z, Sh, _ = rg.batch_z_sigma(rg.sample_cov_batch(R, n, N, rng), qs, n)
    zeta = rg.pop_zeta(R, qs, n)
    nk = np.array([n - len(S) - 3 for (_, _, S) in qs], float)
    delta = np.sqrt(nk) * beta
    false_tg = (~truth) & notf.any(axis=0)
    relevant = usable | false_tg
    order = np.argsort(-(notf & relevant).sum(axis=1))
    tail = rg.WeightedTail(K, SEED + 3 + K)
    tK = float(stats.norm.isf(ALPHA / (2 * K)))
    names = ("T", "W_innov", "W_zca", "BoxMaxT", "BL1")
    cert = dict.fromkeys(names, 0.0)
    fw = dict.fromkeys(names, 0.0)
    size = {"T": 0.0, "W_innov": 0.0, "W_zca": 0.0}
    amb = dict.fromkeys(names, 0.0)
    t0 = time.time()
    done = 0
    I_all = np.arange(K)
    for b in range(N):
        if time.time() - t0 > cap:
            break
        done += 1
        z, S_ = Z[b], Sh[b]
        az = np.abs(z)
        sup = np.maximum((az * PI).max(axis=1), (np.maximum(delta - az, 0) * (~PI)).max(axis=1))
        # T
        Wsq, wts = rg.metric_ridge(S_, lamT)
        w_s = np.sort(wts)[::-1]
        chat = tail.quantile(w_s[w_s > 1e-10])
        size["T"] += float(np.sum((Wsq @ (z - zeta)) ** 2)) > chat

        def st_T(i):
            if sup[i] ** 2 / (1 + lamT) > chat:
                return "reject"
            I = I_all[PI[i]]
            if len(I) and float(z[I] @ np.linalg.solve(S_[np.ix_(I, I)] + lamT * np.eye(len(I)), z[I])) > chat:
                return "reject"
            val, _, proven = g3.d2_exact(z, delta, Wsq, PI[i], node_cap=400, stop_below=chat)
            return "accept" if val <= chat else ("reject" if proven else "ambiguous")

        res = {"T": decide_family(st_T, order, notf, relevant)}
        # whitened boxes
        for nm, kind in (("W_innov", "innov"), ("W_zca", "zca")):
            Mat, s, root = whiten(S_, lamW[kind], kind)
            t = maxt(root, s)
            size[nm] += float(np.max(np.abs(Mat @ (z - zeta)) / s)) > t
            Ainv = np.linalg.inv(Mat)
            res[nm] = decide_family(lambda i: box_status(z, Mat, s, t, PI[i], delta, Ainv=Ainv), order, notf, relevant)
        # unwhitened boxes, closed form
        _, s_r, root_r = whiten(S_, 0.0, "raw")
        t_r = maxt(root_r, s_r)
        res["BoxMaxT"] = decide_family(lambda i: "accept" if sup[i] <= t_r else "reject", order, notf, relevant)
        res["BL1"] = decide_family(lambda i: "accept" if sup[i] <= tK else "reject", order, notf, relevant)
        for nm in names:
            a, am = res[nm]
            cert[nm] += float((a & usable).sum()) / max(int(usable.sum()), 1)
            fw[nm] += bool((a & false_tg).any())
            amb[nm] += am
    d = max(done, 1)
    return {"n": n, "K": K, "reps": done, "cert": {k: v / d for k, v in cert.items()}, "fwer": {k: v / d for k, v in fw.items()},
            "size": {k: v / d for k, v in size.items()}, "ambiguous": {k: v / d for k, v in amb.items()}, "seconds": time.time() - t0}


def random_truths(fam, qs, count, rng, min_eig=.02):
    p = fam.p
    K = len(qs)
    out = []
    i = 0
    while len(out) < count:
        B, conf, cw = g3.random_scm(p, .3 if i % 2 == 0 else .6, i % 4 >= 2, rng)
        i += 1
        R = g3.build_truth(p, B, conf, cw)
        if np.linalg.eigvalsh(R).min() < min_eig:
            continue
        A = B.T != 0
        pst = g3.pattern_truth(A, conf, qs)
        rho = rg.rho_vec(R, qs)
        if not all((abs(rho[k]) > 1e-9) == (pst[k] == 0) for k in range(K)) or pst not in fam.pid or sum(pst) == K:
            continue
        truth = fam.feature_truth(np.pad(A, (0, 1)))
        usable = truth & (~fam.notf[fam.pid[pst]]) & fam.notf.any(axis=0)
        if not usable.any():
            continue
        beta = min(abs(math.atanh(rho[k])) for k in range(K) if pst[k] == 0)
        out.append({"R": R, "truth": truth, "usable": usable, "beta": beta, "edges": [(int(u), int(v)) for u, v in zip(*np.where(A))], "conf": conf})
    return out


def pick_lambda(rows, K, kind):
    for lam in LAMS:
        v = [r["size"] for r in rows if r["K"] == K and r["kind"] == kind and r["lambda"] == lam and r["n"] >= 500]
        if v and max(v) <= 0.065:
            return lam, False
    return 2.0, True


def main():
    t0 = time.time()
    results = {"meta": {"quick": QUICK, "seed": SEED, "workers": WORKERS, "resumed": RESUME}}
    prior = json.loads(OUT.read_text(encoding="utf-8")) if (RESUME and OUT.exists()) else {}

    def save():
        if not QUICK:
            OUT.write_text(json.dumps(results, indent=1, default=lambda o: (o.item() if hasattr(o, "item") else str(o))), encoding="utf-8")

    rng = np.random.default_rng(SEED)
    qs4 = rg.all_queries(4, 2)
    qs5 = rg.all_queries(5, 2)
    fam4 = g3.FamilyL(4, qs4, latent=True)
    with ProcessPoolExecutor(WORKERS) as ex:
        # ---- stage 0: size only, no power
        truths0 = [(x["R"], qs4) for x in random_truths(fam4, qs4, 2 if QUICK else 6, rng)]
        truths0.append((np.array([[1, .9, .9, .9], [.9, 1, .9, .9], [.9, .9, 1, .9], [.9, .9, .9, 1.0]]), qs4))
        truths0 += [(np.eye(5), qs5), (rg.cov_from_sem(fu.chain_sem(5)), qs5)]
        jobs0 = []
        N0 = 100 if QUICK else 3000
        for ti, (R, qs) in enumerate(truths0):
            for n in ((500, 1000, 2000) if len(qs) == 24 else (1000, 5000)):
                for lam in LAMS:
                    for kind in ("innov", "zca"):
                        jobs0.append((R, qs, n, N0, lam, kind, SEED + 1000 + ti * 10 + n))
        rows0 = prior["stage0"]["rows"] if "stage0" in prior else list(ex.map(job_size, jobs0))
        table = {}
        for r in rows0:
            table.setdefault((r["K"], r["kind"], r["lambda"]), {}).setdefault(r["n"], []).append(r["size"])
        for k in sorted(table):
            print("SIZE K={} {} lam={}: ".format(*k) + ", ".join(f"n={n}: max {max(v):.3f}" for n, v in sorted(table[k].items())), flush=True)
        lamW = {}
        flags = {}
        for K in (24, 70):
            lamW[K] = {}
            for kind in ("innov", "zca"):
                lamW[K][kind], flags[f"{K}_{kind}"] = pick_lambda(rows0, K, kind)
        print("lambda_W chosen before any power was measured:", lamW, "flags:", flags, f"| {time.time() - t0:.0f}s", flush=True)
        results["stage0"] = {"rows": rows0, "lambda_W": {str(k): v for k, v in lamW.items()}, "flags": flags}
        save()
        # ---- primary: 40 fresh SCMs
        Nscm, Nrep, cap = (6, 10, 25) if QUICK else (40, 60, 120)
        scms = random_truths(fam4, qs4, Nscm, rng)
        jobs, keys = [], []
        for si, x in enumerate(scms):
            for n in (500, 1000, 2000):
                lamT = max(n ** (-1 / 3), .1)
                jobs.append((qs4, x["R"], n, x["beta"], x["truth"], x["usable"], fam4.PI, fam4.notf, lamT, lamW[24], SEED + 2000 + si * 7 + n, Nrep, cap))
                keys.append(si)
        rows = list(prior.get("primary", []))
        finished = {(r["scm"], r["n"]) for r in rows}
        todo = [(k, j) for k, j in zip(keys, jobs) if (k, j[2]) not in finished]
        print(f"primary: {len(finished)} jobs reused, {len(todo)} to run", flush=True)
        keys, jobs = [t[0] for t in todo], [t[1] for t in todo]
        for key, r in zip(keys, ex.map(job_eval, jobs)):
            r["scm"] = key
            r["beta"] = scms[key]["beta"]
            r["edges"], r["conf"] = scms[key]["edges"], scms[key]["conf"]
            rows.append(r)
            results["primary"] = rows
            if len(rows) % 3 == 0:
                save()
            print(f"P scm={key} n={r['n']} reps={r['reps']} beta={r['beta']:.3f} cert " + " ".join(f"{k}={v:.2f}" for k, v in r["cert"].items()) + f" | {r['seconds']:.0f}s | total {time.time() - t0:.0f}s", flush=True)
        results["primary"] = rows
        save()
        # ---- secondary: S1 scenarios
        prev = json.loads((HERE / "RG3_S1_outputs.json").read_text(encoding="utf-8"))
        s1rows = []
        jobs = []
        info = []
        for hit in prev.get("S1_hits", []):
            A = np.zeros((4, 4), bool)
            for u, v in hit["edges"]:
                A[u, v] = True
            conf = tuple(hit["conf"]) if hit["conf"] else None
            b = hit["b"]
            R = g3.build_truth(4, b * A.T.astype(float), conf, (b, b))
            truth = fam4.feature_truth(np.pad(A, (0, 1)))
            pst = g3.pattern_truth(A, conf, qs4)
            usable = truth & (~fam4.notf[fam4.pid[pst]]) & fam4.notf.any(axis=0)
            jobs.append((qs4, R, 2000, hit["h"] / math.sqrt(2000), truth, usable, fam4.PI, fam4.notf, max(2000 ** (-1 / 3), .1), lamW[24], SEED + 3000 + len(jobs), 30 if QUICK else 200, 40 if QUICK else 900))
            info.append({"edges": hit["edges"], "conf": hit["conf"], "h": hit["h"], "FWER_CT_earlier": hit["FWER_CT"]})
        for meta, r in zip(info, ex.map(job_eval, jobs)):
            r.update(meta)
            s1rows.append(r)
            print(f"S1 {meta} reps={r['reps']} cert " + " ".join(f"{k}={v:.2f}" for k, v in r["cert"].items()) + " FWER " + " ".join(f"{k}={v:.3f}" for k, v in r["fwer"].items()) + " amb " + " ".join(f"{k}={v:.2f}" for k, v in r["ambiguous"].items()), flush=True)
        results["S1"] = s1rows
        save()
        # ---- secondary: K=70, local DAG family
        Nk, Nrep7, cap7 = (2, 6, 25) if QUICK else (12, 30, 200)
        jobs, keys, inf = [], [], []
        got = 0
        while got < Nk:
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
            fam = fu.Family(fu.local_dags(A, 1 if QUICK else 2), qs5)
            truth = ~fam.false_at(A)
            usable = truth & (~fam.notf[fam.pid[pst]]) & fam.notf.any(axis=0)
            if not usable.any():
                continue
            beta = min(abs(math.atanh(rho[k])) for k in range(70) if pst[k] == 0)
            for n in (1000, 5000):
                jobs.append((qs5, R, n, beta, truth, usable, fam.PI, fam.notf, .5, lamW[70], SEED + 4000 + got * 7 + n, Nrep7, cap7))
                keys.append(got)
            inf.append({"edges": [(int(u), int(v)) for u, v in zip(*np.where(A))], "beta": beta, "patterns": len(fam.upats)})
            got += 1
        k70 = []
        for key, r in zip(keys, ex.map(job_eval, jobs)):
            r["scm"] = key
            r.update(inf[key])
            k70.append(r)
            print(f"K70 scm={key} n={r['n']} reps={r['reps']} beta={r['beta']:.3f} cert " + " ".join(f"{k}={v:.2f}" for k, v in r["cert"].items()) + f" | {r['seconds']:.0f}s", flush=True)
        results["K70"] = k70
        save()

    # ---- verdict by the declared rule
    def paired(rows_, n, a, b):
        d = np.array([r["cert"][a] - r["cert"][b] for r in rows_ if r["n"] == n])
        return float(d.mean()), float(d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan")

    prim = results["primary"]
    summ = []
    for n in (500, 1000, 2000):
        sub = [r for r in prim if r["n"] == n]
        row = {"n": n, "SCMs": len(sub), "mean_reps": float(np.mean([r["reps"] for r in sub]))}
        for k in ("T", "W_innov", "W_zca", "BoxMaxT", "BL1"):
            row[f"cert_{k}"] = float(np.mean([r["cert"][k] for r in sub]))
            row[f"FWER_{k}"] = float(np.average([r["fwer"][k] for r in sub], weights=[r["reps"] for r in sub]))
            row[f"ambiguous_{k}"] = float(np.mean([r["ambiguous"][k] for r in sub]))
        for k in ("T", "W_innov", "W_zca"):
            row[f"size_{k}"] = float(np.average([r["size"][k] for r in sub], weights=[r["reps"] for r in sub]))
        for a, b in (("T", "W_innov"), ("T", "W_zca"), ("T", "BL1"), ("W_innov", "BL1"), ("T", "BoxMaxT"), ("W_innov", "BoxMaxT")):
            row[f"diff_{a}-{b}"], row[f"se_{a}-{b}"] = paired(prim, n, a, b)
        summ.append(row)
        print("SUMMARY " + ", ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}" for k, v in row.items()), flush=True)
    results["summary"] = summ

    def clean(meth, row):
        tot = row["SCMs"] * row["mean_reps"]
        lim = ALPHA + 3 * math.sqrt(ALPHA * (1 - ALPHA) / max(tot, 1))
        return row[f"FWER_{meth}"] <= lim and row[f"size_{meth}"] <= lim

    t_clear = sum(r["diff_T-W_innov"] >= .05 and r["diff_T-W_innov"] - 2 * r["se_T-W_innov"] > 0 for r in summ)
    w_clear = sum(r["diff_T-W_innov"] <= -.05 and r["diff_T-W_innov"] + 2 * r["se_T-W_innov"] < 0 for r in summ)
    t_ok, w_ok = all(clean("T", r) for r in summ), all(clean("W_innov", r) for r in summ)
    neither = all((r["diff_T-BL1"] < .05 or r["diff_T-BL1"] - 2 * r["se_T-BL1"] <= 0) and (r["diff_W_innov-BL1"] < .05 or r["diff_W_innov-BL1"] - 2 * r["se_W_innov-BL1"] <= 0) for r in summ)
    verdict = "T clear" if (t_clear >= 2 and t_ok) else ("W clear" if (w_clear >= 2 and w_ok) else "no clear difference")
    results["verdict"] = {"T_vs_W": verdict, "neither_beats_BL1": bool(neither), "T_clear_at_n": int(t_clear), "W_clear_at_n": int(w_clear), "T_valid": bool(t_ok), "W_valid": bool(w_ok)}
    print("VERDICT", results["verdict"], flush=True)
    results["meta"]["runtime_sec"] = time.time() - t0
    save()
    print(f"runtime {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    main()
