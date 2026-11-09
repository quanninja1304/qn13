"""RG3 (analytic prevalence) and S1 (scenario search) for A'. See RG3_S1_report_vi.md.

READING RULES, DECLARED BEFORE ANY FULL RUN (project-management choices, not statistical standards):
  S1 succeeds if some (SCM, h) has FWER_CT >= 0.05 + 3 SE and R1 (ridge, projection threshold, abstain) certifies at least 0.20 of the
     true Q-identifiable non-vacuous features, both measured on that same SCM.
  RG3 "chi-square has an advantage" in a cell if at least 20% of SCMs have mean efficiency gain >= 1.25 against the best valid box method,
     where gain = n*_box / n*_method and n* is the sample size for 90% power against the hardest competitor of a feature.
  RG3 "signal is effectively one-coordinate" in a cell if the median of ENC_range is below 1.5 (defined below).
  VALIDATION RULE: an analytic gain of T counts only if the real-data validation agrees: R1 certifies at least 0.10 more of the true
     Q-identifiable features than BL1, averaged over the validation SCMs, at some n, with FWER_R1 <= alpha + 3 SE.
  Recommendation: stop A' if S1 fails, or if the valid chi-square methods have no validated advantage in every cell.

CHANGE AFTER THE FIRST QUICK RUN (no full run had happened): ENC as first defined came out near 0.06, impossible for its intended meaning,
  because the null-space part of the signal is multiplied by 1/lambda. Replaced by ENC_range (computed on the part of v in range(Sigma)) plus
  frac_null, the share of d^2 coming from null(Sigma). The local search for d^2 was replaced by exact branch and bound, and the real-data
  validation rule was added, because the quick run showed T gains too large to accept from a first-order calculation alone.

RG3 method (no data simulated; working model at the population Sigma; signal and delta both scale with sqrt(n)):
  theta = (atanh rho_k), eta = beta(P, m*) (the largest eta the truth allows), metric A = Sigma + lam I.
  For a competitor m' the sample size needed for 90% power is n = req / NCP:
    BL1       : req (t_K + z_b)^2, NCP sup-norm distance^2 to R(m')
    Bonf      : per model, alpha/2 on block I' (max theta_k^2), alpha/2 on D' one-sided (max (eta-|theta_k|)_+^2), the better part
    InnovMax  : as Bonf, block part replaced by the max of standardised A_I^-1 theta_I
    Hybrid    : as Bonf, block part replaced by the ridge chi-square on I' (noncentral chi-square with Satterthwaite df)
    T@c_hat   : statistic d^2(z, m'), projection threshold (sqrt(c)+z_b)^2 / d^2. d^2 by branch and bound; if the node cap stops it the
                value is an upper bound, which favours T (share reported as frac_unproven).
    T@1df     : same d^2 with threshold chi2_1: not a valid procedure, an optimistic bound on anything built on T (favours chi-square).
  n*(f) = max over m' in M_notf of n(m'); the box comparator is the best of BL1, Bonf, InnovMax per feature.
  At the minimiser v of the hardest competitor under T, split d^2 into the part in range(Sigma) and the part in null(Sigma).
  frac_null = null part / d^2. The null part is first-order noiseless: it measures that R(m') has no point on the tangent plane of the
  attainable set at z, i.e. it uses algebraic relations among the queries, not noise reduction.
  ENC_range = range part / max_k ((A^-1 v_r)_k^2 / (A^-1 Sigma A^-1)_kk), v_r the range part of v. Near 1: one whitened coordinate carries it.
  Limits: one competitor at a time, first-order working model, no finite-sample effects. This is not a power simulation.

M = DAGs on V plus at most one latent confounder between a pair. This covers the patterns of those latent projections, not all MAGs.

Run: python -P -E RG3_S1_checks.py [--quick] [G V S]   (G = RG3, V = real-data validation, S = S1)
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("fu", HERE / "RG1_followup_checks.py")
fu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fu)
rg = fu.rg

QUICK = "--quick" in sys.argv
SEED = 20261106
ALPHA = 0.05
ZB = float(stats.norm.ppf(.9))
results: dict = {"meta": {"quick": QUICK, "seed": SEED}}


class FamilyL:
    """Patterns of DAGs on p observed variables with at most one latent confounder."""

    def __init__(self, p, qs, latent=True):
        t0 = time.time()
        self.p, self.qs = p, qs
        qp = fu.prep(qs)
        feats = list(itertools.permutations(range(p), 2))
        self.feats = feats
        L = len(feats)
        pid, notf_rows, pats = {}, [], []
        pairs = list(itertools.combinations(range(p), 2))
        for A in rg.all_dags(p):
            pa0 = [sum(1 << u for u in range(p) if A[u, v]) for v in range(p)]
            an = rg.ancestors_matrix(A)
            row = np.zeros(2 * L, bool)
            for j, (x, y) in enumerate(feats):
                row[j if not an[x, y] else j + L] = True
            for c in ([None] + pairs if latent else [None]):
                pa = pa0 + [0]
                if c is not None:
                    pa[c[0]] |= 1 << p
                    pa[c[1]] |= 1 << p
                pt = tuple(int(fu.dsep_fast(pa, x, y, m)) for (x, y, m) in qp)
                i = pid.get(pt)
                if i is None:
                    pid[pt] = len(pats)
                    pats.append(pt)
                    notf_rows.append(row.copy())
                else:
                    notf_rows[i] |= row
        self.pid, self.upats = pid, pats
        self.PI = np.array(pats, dtype=bool)
        self.notf = np.array(notf_rows)
        print(f"family p={p} K={len(qs)} latent={latent}: patterns={len(pats)}, {time.time() - t0:.0f}s", flush=True)

    def feature_truth(self, A):
        an = rg.ancestors_matrix(A[: self.p, : self.p])
        L = len(self.feats)
        tr = np.zeros(2 * L, bool)
        for j, (x, y) in enumerate(self.feats):
            tr[j] = bool(an[x, y])
            tr[j + L] = not an[x, y]
        return tr


def build_truth(p, B_obs, conf=None, c_w=(0.5, 0.5)):
    """Correlation of the observed variables of a linear SEM; B_obs[v,u] = weight of u -> v; optional latent confounder."""
    B = np.zeros((p + 1, p + 1))
    B[:p, :p] = B_obs
    if conf is not None:
        B[conf[0], p], B[conf[1], p] = c_w
    Inv = np.linalg.inv(np.eye(p + 1) - B)
    C = (Inv @ Inv.T)[:p, :p]
    d = np.sqrt(np.diag(C))
    return C / np.outer(d, d)


def pattern_truth(A_obs, conf, qs):
    p = A_obs.shape[0]
    pa = [sum(1 << u for u in range(p) if A_obs[u, v]) for v in range(p)] + [0]
    if conf is not None:
        pa[conf[0]] |= 1 << p
        pa[conf[1]] |= 1 << p
    return tuple(int(fu.dsep_fast(pa, x, y, m)) for (x, y, m) in fu.prep(qs))


@lru_cache(maxsize=None)
def req_ncx(df10, c10):
    df, c = max(df10 / 10, .1), c10 / 10
    f = lambda nc: stats.ncx2.sf(c, df, nc) - .9
    return float(optimize.brentq(f, 1e-6, 1e4))


def satter(w, alpha):
    w = w[w > 1e-10]
    g = (w**2).sum() / w.sum()
    df = w.sum() ** 2 / (w**2).sum()
    return float(g * stats.chi2.ppf(1 - alpha, df)), float(df), float(g)


def closed_form_n(theta, eta, Sig, lam, PI):
    """Per-pattern n for the closed-form methods."""
    K, Np = len(theta), PI.shape[0]
    at = np.abs(theta)
    tK = float(stats.norm.isf(ALPHA / (2 * K)))
    gapD = np.maximum(eta - at, 0)
    out = {k: np.full(Np, np.inf) for k in ("BL1", "Bonf", "Innov", "Hybrid")}
    S_val = np.zeros(Np)
    idx = np.arange(K)
    for i in range(Np):
        I = idx[PI[i]]
        Dd = idx[~PI[i]]
        a1 = ALPHA / 2 if len(I) and len(Dd) else ALPHA
        n_D = np.inf
        if len(Dd):
            g = gapD[Dd].max()
            if g > 0:
                n_D = (float(stats.norm.isf(a1 / len(Dd))) + ZB) ** 2 / g**2
        sup = max(at[I].max() if len(I) else 0.0, gapD[Dd].max() if len(Dd) else 0.0)
        if sup > 0:
            out["BL1"][i] = (tK + ZB) ** 2 / sup**2
        n_b = n_i = n_h = np.inf
        if len(I):
            th = theta[I]
            if np.abs(th).max() > 1e-12:
                t = float(stats.norm.isf(a1 / (2 * len(I))))
                n_b = (t + ZB) ** 2 / (th**2).max()
                SI = Sig[np.ix_(I, I)]
                AI = SI + lam * np.eye(len(I))
                x = np.linalg.solve(AI, th)
                Ainv = np.linalg.inv(AI)
                var = np.einsum("ij,jk,ki->i", Ainv, SI, Ainv)
                std = np.max(x**2 / np.maximum(var, 1e-12))
                n_i = (t + ZB) ** 2 / std
                w = np.clip(np.linalg.eigvalsh(SI), 0, None)
                w = w / (w + lam)
                c, df, g = satter(w, a1)
                nc = th @ x
                S_val[i] = nc
                # noncentral chi-square on the scale of the statistic: nc/g against c/g with df
                n_h = req_ncx(int(round(df * 10)), int(round(c / g * 10))) * g / nc
        out["Bonf"][i] = min(n_b, n_D)
        out["Innov"][i] = min(n_i, n_D)
        out["Hybrid"][i] = min(n_h, n_D)
    return out, S_val


def d2_exact(z, delta, Wsq, pat_bool, node_cap=4000, stop_below=None):
    """inf over R(m) of ||Wsq (z-u)||^2 by branch and bound on signs of the dependent coordinates.

    Relaxation: undecided coordinates are free (a valid lower bound); branch on the coordinate most violating |u_k| >= delta_k.
    Returns (value, residual v, proven). If stop_below is given, stops as soon as a feasible value <= stop_below is found."""
    K = len(z)
    D = np.where(~pat_bool)[0]
    if len(D) == 0:
        return float(np.sum((Wsq @ z) ** 2)), z.copy(), True
    base = Wsq @ z
    cols = Wsq[:, D]
    dd = delta[D]
    best, best_u = np.inf, None

    def feasible_value(sg):
        A_ = cols * sg
        x, rn = optimize.nnls(A_, base - A_ @ dd, maxiter=30 * max(len(D), 3))
        return rn**2, sg * (dd + x)

    s0 = np.where(z[D] >= 0, 1.0, -1.0)
    best, best_u = feasible_value(s0)
    if stop_below is not None and best <= stop_below:
        v = z.copy()
        v[D] -= best_u
        return float(best), v, True
    stack = [np.zeros(len(D))]
    nodes = 0
    proven = True
    while stack:
        if nodes >= node_cap:
            proven = False
            break
        nodes += 1
        sg = stack.pop()
        fixed = sg != 0
        free = np.where(~fixed)[0]
        A_f = cols[:, fixed] * sg[fixed]
        b_ = base - A_f @ dd[fixed]
        A_ = np.hstack([A_f, cols[:, free], -cols[:, free]])
        x, rn = optimize.nnls(A_, b_, maxiter=30 * max(A_.shape[1], 3))
        val = rn**2
        if val >= best - 1e-12:
            continue
        nf = int(fixed.sum())
        u = np.zeros(len(D))
        u[fixed] = sg[fixed] * (dd[fixed] + x[:nf])
        u[free] = x[nf:nf + len(free)] - x[nf + len(free):]
        viol = np.where((~fixed) & (np.abs(u) < dd - 1e-10))[0]
        if len(viol) == 0:
            best, best_u = val, u
            if stop_below is not None and best <= stop_below:
                break
            continue
        j = viol[np.argmax(dd[viol] - np.abs(u[viol]))]
        for sign in ((1.0, -1.0) if u[j] < 0 else (-1.0, 1.0)):      # visit the closer sign last popped first
            ch = sg.copy()
            ch[j] = sign
            stack.append(ch)
    v = z.copy()
    v[D] -= best_u
    return float(best), v, proven


def analyse_scm(fam, R, Atrue, conf, lam, node_cap=4000):
    qs = fam.qs
    K = len(qs)
    Sig = rg.sigma_closed(R, qs)
    rho = rg.rho_vec(R, qs)
    pstar = pattern_truth(Atrue, conf, qs)
    if not all((abs(rho[k]) > 1e-9) == (pstar[k] == 0) for k in range(K)) or pstar not in fam.pid:
        return None
    theta = np.arctanh(rho)
    dep = [abs(theta[k]) for k in range(K) if pstar[k] == 0]
    if not dep:
        return None
    eta = float(min(dep))
    mstar = fam.pid[pstar]
    truth = fam.feature_truth(np.pad(Atrue, (0, 1)))
    usable = truth & (~fam.notf[mstar]) & fam.notf.any(axis=0)
    if not usable.any():
        return {"eta": eta, "n_features": 0}
    w, V = np.linalg.eigh(Sig)
    w = np.clip(w, 0, None)
    Wsq = (V / np.sqrt(w + lam)) @ V.T
    Om = (V / (w + lam)) @ V.T
    wts = w / (w + lam)
    chat, _, _ = satter(wts, ALPHA)
    PI = fam.PI
    PI_other = PI.copy()
    cf, S_val = closed_form_n(theta, eta, Sig, lam, PI_other)
    at = np.abs(theta)
    sup = np.maximum((at * PI).max(axis=1), (np.maximum(eta - at, 0) * (~PI)).max(axis=1))
    LB = np.maximum(S_val, sup**2 / (1 + lam))
    cache = {}

    def d2_of(i):
        if i not in cache:
            cache[i] = d2_exact(theta, np.full(K, eta), Wsq, PI[i], node_cap=node_cap)
        return cache[i]

    rows = []
    Om_S_Om = Om @ Sig @ Om
    for j in np.where(usable)[0]:
        comp = np.where(fam.notf[:, j])[0]
        nstar = {k: float(cf[k][comp].max()) for k in cf}
        order = comp[np.argsort(LB[comp])]
        best, arg = np.inf, None
        for i in order:
            if LB[i] >= best:
                break
            v = d2_of(i)[0]
            if v < best:
                best, arg = v, i
        if arg is None or best <= 1e-14:
            continue
        v = d2_of(arg)[1]
        keep = w > 1e-8
        vr = (V[:, keep] @ (V[:, keep].T @ v))
        null_part = float(np.sum((V[:, ~keep].T @ v) ** 2) / lam)
        range_part = max(best - null_part, 0.0)
        stat = (Om @ vr) ** 2 / np.maximum(np.diag(Om_S_Om), 1e-12)
        enc = range_part / max(stat.max(), 1e-14)
        box = min(nstar["BL1"], nstar["Bonf"], nstar["Innov"])
        rows.append({"box": box, "BL1": nstar["BL1"], "Bonf": nstar["Bonf"], "Innov": nstar["Innov"], "Hybrid": nstar["Hybrid"],
                     "T_chat": (math.sqrt(chat) + ZB) ** 2 / best, "T_1df": (1.96 + ZB) ** 2 / best, "ENC_range": enc, "frac_null": null_part / best,
                     "unproven": not d2_of(arg)[2], "delta_coords": int((PI[arg] != PI[mstar]).sum())})
    if not rows:
        return {"eta": eta, "n_features": 0}
    return {"eta": eta, "n_features": len(rows), "rows": rows}


def random_scm(p, dens, latent, rng):
    order = rng.permutation(p)
    B = np.zeros((p, p))
    for a, b in itertools.combinations(range(p), 2):
        if rng.random() < dens:
            u, v = order[a], order[b]
            B[v, u] = rng.choice([-1, 1]) * rng.uniform(.2, .8)
    conf = None
    cw = (0.5, 0.5)
    if latent:
        i, j = rng.choice(p, 2, replace=False)
        conf = (int(i), int(j))
        cw = tuple(rng.choice([-1, 1], 2) * rng.uniform(.3, .8, 2))
    return B, conf, cw


def run_rg3():
    print("\n=== RG3: analytic efficiency on random SCMs ===", flush=True)
    rng = np.random.default_rng(SEED + 1)
    cells = []
    fams = {}
    for p, c, lam, Nscm, cap in ((4, 2, .1, 200, 4000), (5, 2, .5, 25, 300)):
        if QUICK:
            Nscm = 8 if p == 4 else 1
        qs = rg.all_queries(p, c)
        fams[p] = FamilyL(p, qs, latent=True)
        fam = fams[p]
        for dens, latent in itertools.product((.3, .6), (False, True)):
            t0 = time.time()
            agg = []
            n_try = n_skip = n_nofeat = 0
            while len(agg) < Nscm and n_try < 6 * Nscm and time.time() - t0 < (40 if QUICK else 600):
                n_try += 1
                B, conf, cw = random_scm(p, dens, latent, rng)
                R = build_truth(p, B, conf, cw)
                r = analyse_scm(fam, R, B.T != 0, conf, lam, node_cap=cap)
                if r is None:
                    n_skip += 1
                    continue
                if r["n_features"] == 0:
                    n_nofeat += 1
                    continue
                agg.append(r)
            if not agg:
                continue

            def scm_mean_gain(key):
                return np.array([np.mean([min(x["box"] / max(x[key], 1e-12), 1e6) for x in r["rows"] if np.isfinite(x["box"])] or [0]) for r in agg])

            allrows = [x for r in agg for x in r["rows"]]

            def med(key):
                return float(np.median([x[key] for x in allrows]))

            def frac_n(key, lim):
                return float(np.mean([x[key] <= lim for x in allrows]))

            cell = {"p": p, "K": len(qs), "lambda": lam, "density": dens, "latent": latent, "SCMs_with_features": len(agg), "tried": n_try, "unfaithful_or_skipped": n_skip, "no_Qid_feature": n_nofeat,
                    "features_per_SCM": float(np.mean([r["n_features"] for r in agg])), "median_eta": float(np.median([r["eta"] for r in agg]))}
            for key in ("BL1", "Bonf", "Innov", "Hybrid", "T_chat", "T_1df"):
                cell[f"median_n*_{key}"] = med(key)
                cell[f"frac_n*<=5000_{key}"] = frac_n(key, 5000)
            for key in ("Hybrid", "T_chat", "T_1df"):
                g = scm_mean_gain(key)
                cell[f"median_gain_{key}"] = float(np.median(g))
                cell[f"frac_SCM_gain>=1.25_{key}"] = float(np.mean(g >= 1.25))
            cell["median_ENC_range"] = med("ENC_range")
            cell["frac_ENC_range<1.5"] = float(np.mean([x["ENC_range"] < 1.5 for x in allrows]))
            cell["median_frac_null"] = med("frac_null")
            cell["frac_unproven"] = float(np.mean([x["unproven"] for x in allrows]))
            cell["median_raw_diff_coords"] = med("delta_coords")
            cell["seconds"] = time.time() - t0
            cells.append(cell)
            print("RG3 " + ", ".join(f"{k}={v:.3g}" if isinstance(v, float) else f"{k}={v}" for k, v in cell.items()), flush=True)
    results["RG3"] = cells
    return fams


def run_validation(fams):
    """Does the analytic gain of T appear on real Gaussian data? Exploratory: separate seed from any later RG2."""
    print("\n=== Validation of the RG3 gain on simulated Gaussian data ===", flush=True)
    rng = np.random.default_rng(SEED + 5)
    p = 4
    qs = rg.all_queries(p, 2)
    K = len(qs)
    fam = fams.get(p) or FamilyL(p, qs, latent=True)
    fams[p] = fam
    tail = rg.WeightedTail(K, SEED + 6)
    tK = float(stats.norm.isf(ALPHA / (2 * K)))
    Nscm, Nrep = (3, 15) if QUICK else (24, 100)
    out = []
    scms = []
    while len(scms) < Nscm:
        B, conf, cw = random_scm(p, .3 if len(scms) % 2 == 0 else .6, len(scms) % 4 >= 2, rng)
        R = build_truth(p, B, conf, cw)
        A = B.T != 0
        pst = pattern_truth(A, conf, qs)
        rho = rg.rho_vec(R, qs)
        if not all((abs(rho[k]) > 1e-9) == (pst[k] == 0) for k in range(K)) or pst not in fam.pid or sum(pst) == K:
            continue
        truth = fam.feature_truth(np.pad(A, (0, 1)))
        usable = truth & (~fam.notf[fam.pid[pst]]) & fam.notf.any(axis=0)
        if usable.any():
            scms.append((R, pst, truth, usable, min(abs(math.atanh(rho[k])) for k in range(K) if pst[k] == 0)))
    t00 = time.time()
    for n in (200, 500, 1000, 2000, 5000):
        lam = max(n ** (-1 / 3), .1)
        nk = np.array([n - len(S) - 3 for (_, _, S) in qs], float)
        tot = {"R1": [], "BL1": [], "FW_R1": [], "FW_BL1": [], "amb": []}
        for R, pst, truth, usable, beta in scms:
            if time.time() - t00 > (60 if QUICK else 1800):
                break
            delta = np.sqrt(nk) * beta
            false_tg = (~truth) & fam.notf.any(axis=0)
            Z, Sh, _ = rg.batch_z_sigma(rg.sample_cov_batch(R, n, Nrep, rng), qs, n)
            c_r = c_b = f_r = f_b = am = 0.0
            for b in range(Nrep):
                z, S_ = Z[b], Sh[b]
                Wsq, wts = rg.metric_ridge(S_, lam)
                w_s = np.sort(wts)[::-1]
                chat = tail.quantile(w_s[w_s > 1e-10])
                az = np.abs(z)
                PI = fam.PI
                sup = np.maximum((az * PI).max(axis=1), (np.maximum(delta - az, 0) * (~PI)).max(axis=1))
                sb = sup <= tK
                aB = (~fam.notf[sb].any(axis=0)) if sb.any() else np.zeros(fam.notf.shape[1], bool)
                c_b += (aB & usable).sum() / usable.sum()
                f_b += bool((aB & false_tg).any())
                surv, amb = [], []
                for i in np.where(sup**2 / (1 + lam) <= chat)[0]:
                    val, _, proven = d2_exact(z, delta, Wsq, PI[i], node_cap=400, stop_below=chat)
                    if val <= chat:
                        surv.append(i)
                    elif not proven:
                        amb.append(i)
                am += len(amb)
                allm = surv + amb       # ambiguous counted as surviving: cert_R1 is a lower bound
                if allm:
                    aR = ~fam.notf[allm].any(axis=0)
                    c_r += (aR & usable).sum() / usable.sum()
                    f_r += bool((aR & false_tg).any())
            tot["R1"].append(c_r / Nrep); tot["BL1"].append(c_b / Nrep); tot["FW_R1"].append(f_r / Nrep); tot["FW_BL1"].append(f_b / Nrep); tot["amb"].append(am / Nrep)
        if tot["R1"]:
            diff = np.array(tot["R1"]) - np.array(tot["BL1"])
            row = {"n": n, "SCMs": len(tot["R1"]), "reps_per_SCM": Nrep, "cert_R1": float(np.mean(tot["R1"])), "cert_BL1": float(np.mean(tot["BL1"])), "mean_diff": float(diff.mean()),
                   "se_diff_over_SCMs": float(diff.std(ddof=1) / math.sqrt(len(diff))) if len(diff) > 1 else None, "SCMs_R1_better": int((diff > 0).sum()), "SCMs_BL1_better": int((diff < 0).sum()),
                   "FWER_R1": float(np.mean(tot["FW_R1"])), "max_SCM_FWER_R1": float(np.max(tot["FW_R1"])), "FWER_BL1": float(np.mean(tot["FW_BL1"])), "mean_ambiguous": float(np.mean(tot["amb"]))}
            out.append(row)
            print("VAL " + ", ".join(f"{k}={v:.3g}" if isinstance(v, float) else f"{k}={v}" for k, v in row.items()), flush=True)
    results["validation"] = out


def canon_topologies(p, latent=True):
    seen, out = set(), []
    perms = list(itertools.permutations(range(p)))
    pairs = list(itertools.combinations(range(p), 2))
    for A in rg.all_dags(p):
        for c in ([None] + pairs if latent else [None]):
            keys = []
            for pm in perms:
                pm = list(pm)
                Ap = A[np.ix_(pm, pm)]
                inv = {v: i for i, v in enumerate(pm)}
                cp = None if c is None else tuple(sorted((inv[c[0]], inv[c[1]])))
                keys.append((Ap.tobytes(), cp))
            k = min(keys, key=lambda t: (t[0], t[1] or ()))
            if k not in seen:
                seen.add(k)
                out.append((A, c))
    return out


def run_s1(fams):
    print("\n=== S1: scenario search ===", flush=True)
    rng = np.random.default_rng(SEED + 2)
    n = 2000
    p = 4
    qs = rg.all_queries(p, 2)
    K = len(qs)
    fam = fams.get(p) or FamilyL(p, qs, latent=True)
    tops = canon_topologies(p)
    print(f"topologies p=4 up to relabelling: {len(tops)}", flush=True)
    nk = np.array([n - len(S) - 3 for (_, _, S) in qs], float)
    N1 = 800 if QUICK else 4000
    hs = (2.0, 3.0, 4.0, 5.0, 6.0)
    cand, stage1 = [], []
    t0 = time.time()
    for ti, (A, conf) in enumerate(tops):
        if QUICK and ti % 12:
            continue
        if A.sum() == 0 and conf is None:
            continue
        pstar = pattern_truth(A, conf, qs)
        if pstar not in fam.pid:
            continue
        truth = fam.feature_truth(np.pad(A, (0, 1)))
        mstar = fam.pid[pstar]
        usable = truth & (~fam.notf[mstar]) & fam.notf.any(axis=0)
        false_tg = (~truth) & fam.notf.any(axis=0)

        def make(b):
            return build_truth(p, b * A.T.astype(float), conf, (b, b))

        def beta_of(b):
            rr = rg.rho_vec(make(b), qs)
            if not all((abs(rr[k]) > 1e-9) == (pstar[k] == 0) for k in range(K)):
                return -1.0
            d = [abs(math.atanh(rr[k])) for k in range(K) if pstar[k] == 0]
            return min(d) if d else -1.0

        grid = np.geomspace(.01, 2.5, 40)
        vals = np.array([beta_of(g) for g in grid])
        for h in hs:
            tgt = h / math.sqrt(n)
            idx = np.where((vals[:-1] >= 0) & (vals[1:] >= 0) & (vals[:-1] < tgt) & (vals[1:] >= tgt))[0]
            if len(idx) == 0:
                continue
            b = optimize.brentq(lambda x: beta_of(x) - tgt, grid[idx[0]], grid[idx[0] + 1])
            R = make(b)
            if np.linalg.eigvalsh(R).min() < .02:
                continue
            Z = rg.batch_z_sigma(rg.sample_cov_batch(R, n, N1, rng), qs, n, want_sigma=False)[0]
            ph = np.abs(Z) < np.sqrt(nk) * tgt / 2
            codes, counts = np.unique(ph.astype(np.int8), axis=0, return_counts=True)
            bad = 0
            for code, cnt in zip(codes, counts):
                i = fam.pid.get(tuple(int(v) for v in code))
                if i is not None and ((~fam.notf[i]) & false_tg).any():
                    bad += cnt
            fw = bad / N1
            stage1.append((ti, h, fw, int(usable.sum())))
            if fw >= ALPHA + 3 * math.sqrt(ALPHA * (1 - ALPHA) / N1) and usable.any():
                cand.append({"top": ti, "edges": [(int(u), int(v)) for u, v in zip(*np.where(A))], "conf": conf, "h": h, "b": float(b), "FWER_CT_stage1": fw, "n_usable_features": int(usable.sum())})
    print(f"stage 1: {len(stage1)} (topology, h) pairs, {len(cand)} candidates with CT above alpha and Q-identifiable features, {time.time() - t0:.0f}s", flush=True)
    hist = {h: [x[2] for x in stage1 if x[1] == h] for h in hs}
    results["S1_stage1"] = {"pairs": len(stage1), "candidates": len(cand), "by_h": {str(h): {"pairs": len(v), "max_FWER_CT": float(max(v)) if v else None, "frac_above_alpha_3SE": float(np.mean([x >= ALPHA + 3 * math.sqrt(ALPHA * (1 - ALPHA) / N1) for x in v])) if v else None} for h, v in hist.items()}}
    print(results["S1_stage1"], flush=True)
    # Stage 2: largest h first, since R1 needs a large h; fresh data for the CT estimate
    cand.sort(key=lambda c: (-c["h"], -c["FWER_CT_stage1"]))
    tail = rg.WeightedTail(K, SEED + 3)
    t2 = time.time()
    rows = []
    N2 = 40 if QUICK else 300
    lam = n ** (-1 / 3)
    for c in cand[: (4 if QUICK else 60)]:
        if time.time() - t2 > (60 if QUICK else 2400):
            break
        A, conf = tops[c["top"]]
        R = build_truth(p, c["b"] * A.T.astype(float), conf, (c["b"], c["b"]))
        pstar = pattern_truth(A, conf, qs)
        truth = fam.feature_truth(np.pad(A, (0, 1)))
        mstar = fam.pid[pstar]
        usable = truth & (~fam.notf[mstar]) & fam.notf.any(axis=0)
        false_tg = (~truth) & fam.notf.any(axis=0)
        eta = c["h"] / math.sqrt(n)
        delta = np.sqrt(nk) * eta
        Zb = rg.batch_z_sigma(rg.sample_cov_batch(R, n, 20000 if not QUICK else 2000, rng), qs, n, want_sigma=False)[0]
        ph = np.abs(Zb) < delta / 2
        codes, counts = np.unique(ph.astype(np.int8), axis=0, return_counts=True)
        bad = sum(cnt for code, cnt in zip(codes, counts) if (i := fam.pid.get(tuple(int(v) for v in code))) is not None and ((~fam.notf[i]) & false_tg).any())
        fw_ct = bad / Zb.shape[0]
        Z, Sh, _ = rg.batch_z_sigma(rg.sample_cov_batch(R, n, N2, rng), qs, n)
        cert_r1 = cert_b = fw_r1 = fw_b = amb_total = 0.0
        tK = float(stats.norm.isf(ALPHA / (2 * K)))
        t3 = time.time()
        done = 0
        for b in range(N2):
            if time.time() - t3 > (15 if QUICK else 60):
                break
            done += 1
            z, S_ = Z[b], Sh[b]
            Wsq, wts = rg.metric_ridge(S_, lam)
            w_s = np.sort(wts)[::-1]
            chat = tail.quantile(w_s[w_s > 1e-10])
            az = np.abs(z)
            PI = fam.PI
            sup = np.maximum((az * PI).max(axis=1), (np.maximum(delta - az, 0) * (~PI)).max(axis=1))
            sb = sup <= tK
            aB = (~fam.notf[sb].any(axis=0)) if sb.any() else np.zeros(fam.notf.shape[1], bool)
            cert_b += (aB & usable).sum() / usable.sum()
            fw_b += bool((aB & false_tg).any())
            alive = np.where(sup**2 / (1 + lam) <= chat)[0]
            surv, amb = [], []
            I_all = np.arange(K)
            for i in alive:
                I = I_all[PI[i]]
                Sv = float(z[I] @ np.linalg.solve(S_[np.ix_(I, I)] + lam * np.eye(len(I)), z[I])) if len(I) else 0.0
                if Sv > chat:
                    continue
                D = I_all[~PI[i]]
                inactive = (az[D] >= delta[D] + math.sqrt(Sv)).all() if len(D) else True
                if inactive:
                    surv.append(i)
                    continue
                val, _, proven = d2_exact(z, delta, Wsq, PI[i], node_cap=400, stop_below=chat)
                if val <= chat:
                    surv.append(i)
                elif not proven:
                    amb.append(i)
            amb_total += len(amb)
            # Ambiguous models are counted as surviving: conservative for certification, so cert_R1 is a lower bound
            allm = surv + amb
            if allm:
                aR = ~fam.notf[allm].any(axis=0)
                cert_r1 += (aR & usable).sum() / usable.sum()
                fw_r1 += bool((aR & false_tg).any())
        d = max(done, 1)
        row = dict(c)
        row.update({"FWER_CT": fw_ct, "cert_R1_lower_bound": cert_r1 / d, "FWER_R1": fw_r1 / d, "cert_BL1": cert_b / d, "FWER_BL1": fw_b / d, "reps": done, "mean_ambiguous": amb_total / d})
        rows.append(row)
        print("S1 " + ", ".join(f"{k}={v:.3g}" if isinstance(v, float) else f"{k}={v}" for k, v in row.items()), flush=True)
    se = math.sqrt(ALPHA * (1 - ALPHA) / 20000)
    hit = [r for r in rows if r["FWER_CT"] >= ALPHA + 3 * se and r["cert_R1_lower_bound"] >= .20]
    results["S1_stage2"] = rows
    results["S1_hits"] = hit
    print(f"S1 hits by the declared rule: {len(hit)} of {len(rows)} candidates examined", flush=True)


def save():
    if not QUICK:
        out = HERE / "RG3_S1_outputs.json"
        out.write_text(json.dumps(results, indent=1, default=lambda o: (o.item() if hasattr(o, "item") else str(o))), encoding="utf-8")


if __name__ == "__main__":
    t0 = time.time()
    sel = [a for a in sys.argv[1:] if a in ("G", "V", "S")] or ["G", "V", "S"]
    fams = {}
    if "G" in sel:
        fams = run_rg3()
        save()
    if "V" in sel:
        run_validation(fams)
        save()
    if "S" in sel:
        run_s1(fams)
    results["meta"]["runtime_sec"] = time.time() - t0
    save()
    print(f"runtime {time.time() - t0:.1f}s", flush=True)
