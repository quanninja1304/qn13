"""A' Day 2 -- minimal toy mechanism validation / falsification.

Scope: TOY ONLY, authorized by A1_mathematical_contract_v2.md section 9 (TOY-WITH-CAVEATS).
Frozen toy spec (v2-toy-1):
  * statistic vector z in R^K; working model z ~ N(zeta, Sigma) with Sigma common to all hypotheses;
  * region R(m) = {z' : z'_k = 0 if pat_k = 1 (independent); |z'_k| >= delta_k if pat_k = 0};
  * dist2_P(z, R) = inf_{z' in R} (z - z')^T P (z - z'), P = weight (precision) matrix:
      'inv'     : P = Sigma^{-1}                (requires PD)
      'diag'    : P = diag(1/Sigma_kk)           (ACI-type diagonal control, contract P3)
      'pinv'    : P = Sigma^+  (seminorm, convention C-c)
      'support' : P = Sigma^+ and z - z' in range(Sigma), else +inf (convention C-b, original P5)
      'ridge'   : P = (Sigma + lam I)^{-1}       (convention C-d)
  * D(f) = dist2(z, R(M_notf)) - dist2(z, R(M_f));  T(f) = dist2(z, R(M_notf)).
Changes from original proposal: see A1_toy_results.md section 1.

Run:  python -P -E A1_toy_mechanism_validation.py  [--quick]
Writes A1_toy_outputs.json next to this file. Seeds are fixed below.
"""
from __future__ import annotations

import itertools
import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np
import scipy
from scipy import optimize, stats

QUICK = "--quick" in sys.argv
OUT = Path(__file__).with_name("A1_toy_outputs.json")
SEED_CALIB = 101   # exploratory: threshold calibration only
SEED_EVAL = 202    # evaluation
SEED_DATA = 303    # Gaussian-data experiments (C)
SEED_REF = 404     # random instances for independent solver check
NMC = 4000 if QUICK else 20000
NDATA = 1000 if QUICK else 4000
INF = math.inf
results: dict = {"meta": {
    "python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
    "platform": platform.platform(), "quick": QUICK, "NMC": NMC, "NDATA": NDATA,
    "seeds": {"calib": SEED_CALIB, "eval": SEED_EVAL, "data": SEED_DATA, "ref": SEED_REF},
    "spec": "v2-toy-1"}}
failures: list[str] = []


def check(name: str, cond: bool, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        failures.append(f"{name}: {detail}")


# ----------------------------------------------------------------------------------------------
# Core: exact distance to a union-of-polyhedra region by active-set enumeration
# ----------------------------------------------------------------------------------------------
def weight_matrix(Sigma, mode, lam=None):
    """Return (P, N) where N is a basis of null(Sigma) for 'support' mode (else None)."""
    K = Sigma.shape[0]
    if mode == "inv":
        return np.linalg.inv(Sigma), None
    if mode == "diag":
        return np.diag(1.0 / np.diag(Sigma)), None
    if mode == "ridge":
        return np.linalg.inv(Sigma + lam * np.eye(K)), None
    w, V = np.linalg.eigh(Sigma)
    tol = max(K, 1) * np.finfo(float).eps * max(w.max(), 1.0) * 1e3
    keep = w > tol
    P = (V[:, keep] / w[keep]) @ V[:, keep].T
    if mode == "pinv":
        return P, None
    if mode == "support":
        return P, V[:, ~keep]
    raise ValueError(mode)


def dist2(z, pat, delta, P, N=None, tol=1e-9):
    """inf_{z' in R(pat)} (z-z')^T P (z-z'), with optional constraint N^T (z - z') = 0.

    Exact for PD P: every candidate is a feasible point, and the global optimum's active set is
    enumerated (states: free / active at +delta / active at -delta for each dependent coordinate).
    For singular P the min-norm least-squares minimizer is used on free coordinates (documented
    limitation; only used for convention C-c/C-b illustrations)."""
    z = np.asarray(z, float)
    K = len(z)
    I = [k for k in range(K) if pat[k] == 1]
    Dp = [k for k in range(K) if pat[k] == 0]
    best = INF
    for states in itertools.product((0, 1, -1), repeat=len(Dp)):
        fixed = I + [Dp[j] for j, s in enumerate(states) if s != 0]
        fval = np.array([0.0] * len(I) + [s * delta[Dp[j]] for j, s in enumerate(states) if s != 0])
        free = [Dp[j] for j, s in enumerate(states) if s == 0]
        v = np.zeros(K)
        v[fixed] = z[fixed] - fval
        if free:
            PUU = P[np.ix_(free, free)]
            rhs = -P[np.ix_(free, fixed)] @ v[fixed] if fixed else np.zeros(len(free))
            if N is None or N.shape[1] == 0:
                vU = np.linalg.lstsq(PUU, rhs, rcond=None)[0]
            else:
                NU, NF = N[free, :], N[fixed, :]
                A = np.block([[2 * PUU, NU], [NU.T, np.zeros((N.shape[1], N.shape[1]))]])
                b = np.concatenate([2 * rhs, -(NF.T @ v[fixed]) if fixed else np.zeros(N.shape[1])])
                vU = np.linalg.lstsq(A, b, rcond=None)[0][: len(free)]
            v[free] = vU
            zprime_free = z[free] - vU
            if np.any(np.abs(zprime_free) < np.asarray(delta)[free] - 1e-10):
                continue
        if N is not None and N.shape[1] > 0:
            if np.linalg.norm(N.T @ v) > tol * max(1.0, np.linalg.norm(z)):
                continue
        val = float(v @ P @ v)
        best = min(best, val)
    return best


def dist2_set(z, pats, delta, P, N=None):
    return min((dist2(z, p, delta, P, N) for p in pats), default=INF)


def D_score(z, pats_f, pats_notf, delta, P, N=None):
    a, b = dist2_set(z, pats_notf, delta, P, N), dist2_set(z, pats_f, delta, P, N)
    if math.isinf(a) and math.isinf(b):
        return float("nan")  # undefined (inf - inf), contract section 1.3
    return a - b


# Closed forms (independent derivations, contract eq. 4.2 and P3)
def p4_closed_full(z, r, delta):
    """dist2(z,R(1,1)) - dist2(z,R(1,0)) for Sigma=[[1,r],[r,1]]  (eq. 4.2)."""
    t = z[1] - r * z[0]
    return (t * t - max(delta - abs(t), 0.0) ** 2) / (1 - r * r)


def p4_closed_diag(z, delta):
    return z[1] ** 2 - max(delta - abs(z[1]), 0.0) ** 2


def slsqp_reference(z, pat, delta, P, rng, starts=12):
    """Independent numerical reference: SLSQP over each sign orthant, multistart."""
    K = len(z)
    Dp = [k for k in range(K) if pat[k] == 0]
    I = [k for k in range(K) if pat[k] == 1]
    best = INF
    for signs in itertools.product((1, -1), repeat=len(Dp)):
        cons = [{"type": "eq", "fun": (lambda x, k=k: x[k])} for k in I]
        cons += [{"type": "ineq", "fun": (lambda x, k=k, s=s: s * x[k] - delta[k])} for k, s in zip(Dp, signs)]
        for _ in range(starts):
            x0 = z + rng.normal(size=K)
            for k, s in zip(Dp, signs):
                x0[k] = s * (delta[k] + abs(rng.normal()))
            for k in I:
                x0[k] = 0.0
            res = optimize.minimize(lambda x: (z - x) @ P @ (z - x), x0, jac=lambda x: -2 * P @ (z - x),
                                    constraints=cons, method="SLSQP", options={"ftol": 1e-14, "maxiter": 500})
            if res.success:
                ok = all(abs(res.x[k]) < 1e-6 for k in I) and all(s * res.x[k] >= delta[k] - 1e-6 for k, s in zip(Dp, signs))
                if ok:
                    best = min(best, float(res.fun))
    return best


# ----------------------------------------------------------------------------------------------
# Gaussian helpers (Experiment C)
# ----------------------------------------------------------------------------------------------
def pcorr_from_R(R, i, j, S):
    idx = [i, j] + list(S)
    Pm = np.linalg.inv(R[np.ix_(idx, idx)])
    return -Pm[0, 1] / math.sqrt(Pm[0, 0] * Pm[1, 1])


def fisher_z_vec(R, n, qs):
    return np.array([math.sqrt(n - len(S) - 3) * math.atanh(pcorr_from_R(R, i, j, S)) for (i, j, S) in qs])


def corr_asym_cov(R):
    """Asymptotic covariance of sqrt(n)(r_ij - rho_ij) for Gaussian data (Pearson-type formula)."""
    p = R.shape[0]
    pairs = [(i, j) for i in range(p) for j in range(i + 1, p)]
    r = R

    def c(i, j, k, l):
        return (0.5 * r[i, j] * r[k, l] * (r[i, k] ** 2 + r[i, l] ** 2 + r[j, k] ** 2 + r[j, l] ** 2)
                + r[i, k] * r[j, l] + r[i, l] * r[j, k]
                - r[i, j] * (r[i, k] * r[i, l] + r[j, k] * r[j, l])
                - r[k, l] * (r[i, k] * r[j, k] + r[i, l] * r[j, l]))
    return pairs, np.array([[c(*a, *b) for b in pairs] for a in pairs])


def delta_sigma_z(R, qs, h=1e-6):
    """Delta-method asymptotic covariance of the Fisher-z vector (unit-scaled)."""
    pairs, C = corr_asym_cov(R)
    J = np.zeros((len(qs), len(pairs)))
    g = lambda RR: np.array([math.atanh(pcorr_from_R(RR, i, j, S)) for (i, j, S) in qs])
    for m, (i, j) in enumerate(pairs):
        Rp, Rm = R.copy(), R.copy()
        Rp[i, j] += h; Rp[j, i] += h; Rm[i, j] -= h; Rm[j, i] -= h
        J[:, m] = (g(Rp) - g(Rm)) / (2 * h)
    return J @ C @ J.T


def sample_corr(X):
    return np.corrcoef(X, rowvar=False)


# ==============================================================================================
# Experiment A -- deterministic algebra
# ==============================================================================================
def experiment_A():
    print("\n=== Experiment A: deterministic algebra (mathematical illustration, fixed z) ===")
    out = {"rows": []}
    pats_f, pats_nf = [(1, 0)], [(1, 1)]
    for delta0 in (1.0, 3.0):
        delta = np.array([delta0, delta0])
        for z in ([2.0, 1.8], [-2.0, 1.8], [2.0, -1.8], [0.5, 2.5], [2.5, 0.5]):
            z = np.array(z)
            for r in (0.0, 0.3, -0.3, 0.6, -0.6, 0.9, -0.9):
                S = np.array([[1, r], [r, 1.0]])
                Pf, _ = weight_matrix(S, "inv")
                Pd, _ = weight_matrix(S, "diag")
                Dfull = D_score(z, pats_f, pats_nf, delta, Pf)
                Ddiag = D_score(z, pats_f, pats_nf, delta, Pd)
                cf, cd = p4_closed_full(z, r, delta0), p4_closed_diag(z, delta0)
                t = z[1] - r * z[0]
                branch = "inactive" if abs(t) >= delta0 else "active"
                out["rows"].append({"delta": delta0, "z": z.tolist(), "r": r, "D_full": Dfull, "closed_full": cf,
                                    "D_diag": Ddiag, "closed_diag": cd, "branch": branch})
                check(f"A.P4 closed-form full  d={delta0} z={z.tolist()} r={r}", abs(Dfull - cf) < 1e-9, f"{Dfull:.6f} vs {cf:.6f} ({branch})")
                check(f"A.P3 closed-form diag  d={delta0} z={z.tolist()} r={r}", abs(Ddiag - cd) < 1e-9)
                if r == 0.0:
                    check(f"A.r0 diag==full d={delta0} z={z.tolist()}", abs(Dfull - Ddiag) < 1e-12)
    # z-dependence of the full score through z1 (non-separability) -- active and inactive
    ns = []
    for delta0, z2 in ((1.0, 1.8), (3.0, 1.8)):
        vals = [p4_closed_full(np.array([z1, z2]), 0.6, delta0) for z1 in (-2, 0, 2)]
        ns.append({"delta": delta0, "z2": z2, "z1_grid": [-2, 0, 2], "D_full": vals})
        check(f"A.nonseparable d={delta0}", max(vals) - min(vals) > 1e-6, str(np.round(vals, 4)))
    out["nonseparability"] = ns
    # Near singular r -> +-1 at fixed z
    lim = []
    for z in ([2.0, 1.8], [2.0, 2.0], [-2.0, 2.0]):
        row = {"z": z, "values": {}}
        for r in (0.9, 0.99, 0.999, 0.9999, -0.9, -0.99, -0.999, -0.9999):
            S = np.array([[1, r], [r, 1.0]])
            row["values"][str(r)] = D_score(np.array(z), pats_f, pats_nf, np.array([1.0, 1.0]), np.linalg.inv(S))
            row.setdefault("cond", {})[str(r)] = float(np.linalg.cond(S))
        lim.append(row)
    out["near_singular"] = lim
    # Exact duplicate: K=2 (q1,q2) vs K=3 (q1,q2,q2dup)
    dup = []
    for r in (0.0, 0.6):
        S2 = np.array([[1, r], [r, 1.0]])
        L = np.array([[1, 0], [0, 1], [0, 1.0]])
        S3 = L @ S2 @ L.T
        for z2v in ([2.0, 1.8], [0.5, 2.5]):
            z2 = np.array(z2v); z3 = L @ z2
            d2 = np.array([1.0, 1.0]); d3 = np.array([1.0, 1.0, 1.0])
            base = D_score(z2, [(1, 0)], [(1, 1)], d2, np.linalg.inv(S2))
            P3s, N3 = weight_matrix(S3, "support")
            sup = D_score(z3, [(1, 0, 0)], [(1, 1, 1)], d3, P3s, N3)
            P3p, _ = weight_matrix(S3, "pinv")
            pin = D_score(z3, [(1, 0, 0)], [(1, 1, 1)], d3, P3p)
            naive = D_score(z3, [(1, 0, 0)], [(1, 1, 1)], d3, np.eye(3))   # additive, counts q2 twice
            dedup = D_score(z2, [(1, 0)], [(1, 1)], d2, np.eye(2))           # elementary dedup control
            dup.append({"r": r, "z": z2v, "K2_full": base, "K3_support": sup, "K3_pinv": pin,
                        "K3_naive_diag": naive, "K2_dedup_diag": dedup})
            check(f"A.P5 duplicate invariance (support) r={r} z={z2v}", abs(sup - base) < 1e-8, f"{sup:.6f} vs {base:.6f}")
            # Convention C-c (seminorm) is NOT expected to preserve P5 when a beta-min constraint is active:
            # the null direction (0,1,-1) lets z'_2 != z'_3 satisfy |.|>=delta at zero cost. Recorded, not asserted.
            t_star = z2[1] - r * z2[0]
            dup[-1]["active_branch"] = bool(abs(t_star) < 1.0)
            dup[-1]["pinv_equals_base"] = bool(abs(pin - base) < 1e-8)
            print(f"INFO A.P5 under C-c (pinv) r={r} z={z2v}: K3_pinv={pin:.6f} K2={base:.6f} active={abs(t_star) < 1.0}")
    out["duplicate"] = dup
    # Independent reference: SLSQP on random K=3 instances (inv mode)
    rng = np.random.default_rng(SEED_REF)
    ref = []
    for it in range(8 if QUICK else 25):
        A_ = rng.normal(size=(3, 3)); S = A_ @ A_.T + 0.3 * np.eye(3); d = np.sqrt(np.diag(S)); S = S / np.outer(d, d)
        z = rng.normal(scale=2.0, size=3); delta = np.abs(rng.normal(1.5, 0.5, size=3)) + 0.2
        pat = tuple(int(x) for x in rng.integers(0, 2, size=3))
        P = np.linalg.inv(S)
        a = dist2(z, pat, delta, P); b = slsqp_reference(z, pat, delta, P, rng)
        ref.append({"pat": pat, "enum": a, "slsqp": b})
        check(f"A.ref enum vs SLSQP #{it} pat={pat}", abs(a - b) < 1e-5 * max(1, abs(b)), f"{a:.8f} vs {b:.8f}")
    out["reference_check"] = ref
    # P7: subset search is anti-conservative for T
    rng = np.random.default_rng(SEED_REF + 1)
    p7 = 0
    for _ in range(200):
        z = rng.normal(scale=2, size=3); delta = np.ones(3)
        allp = list(itertools.product((0, 1), repeat=3)); sub = allp[: rng.integers(1, len(allp))]
        p7 += dist2_set(z, sub, delta, np.eye(3)) >= dist2_set(z, allp, delta, np.eye(3)) - 1e-12
    check("A.P7 subset distance >= full-set distance (200 random)", p7 == 200)
    results["A"] = out


# ==============================================================================================
# Experiment B -- sampling under the Gaussian working model (still toy)
# ==============================================================================================
def equicorr(K, r):
    return (1 - r) * np.eye(K) + r * np.ones((K, K))


def far(scores, c):
    s = np.asarray(scores); s = s[~np.isnan(s)]
    p = float(np.mean(s > c)); se = math.sqrt(p * (1 - p) / len(s))
    return p, se


def experiment_B():
    print("\n=== Experiment B: Monte Carlo under the working model (toy) ===")
    out = {}
    rs = (0.0, 0.3, 0.6, 0.9, -0.6)
    # Configs: models differ in 1 coordinate (CE3) or in 2 coordinates (genuine double counting)
    configs = {"B1_one_coord": ([(1, 0)], [(1, 1)]), "B2_two_coord": ([(0, 0)], [(1, 1)])}
    for delta0 in (1.5, 3.0):
        delta = np.array([delta0, delta0])
        for cname, (pf, pnf) in configs.items():
            # calibrate transfer thresholds at r=0 (exploratory seed)
            rngc = np.random.default_rng(SEED_CALIB)
            Zc = rngc.multivariate_normal(np.zeros(2), np.eye(2), size=NMC)
            cal = {}
            for meth in ("full", "diag"):
                P = np.eye(2)
                cal[f"D_{meth}"] = float(np.quantile([D_score(z, pf, pnf, delta, P) for z in Zc], 0.95))
            rows = []
            for r in rs:
                S = np.array([[1, r], [r, 1.0]])
                rng = np.random.default_rng(SEED_EVAL)
                Z = rng.multivariate_normal(np.zeros(2), S, size=NMC)   # null: truth = (1,1) => f false
                Pf, Pd = np.linalg.inv(S), np.diag(1 / np.diag(S))
                Df = [D_score(z, pf, pnf, delta, Pf) for z in Z]
                Dd = [D_score(z, pf, pnf, delta, Pd) for z in Z]
                Tf = [dist2_set(z, pnf, delta, Pf) for z in Z]
                Td = [dist2_set(z, pnf, delta, Pd) for z in Z]
                c2 = stats.chi2.ppf(0.95, 2)
                row = {"r": r,
                       "FAR_Dfull_transfer": far(Df, cal["D_full"]), "FAR_Ddiag_transfer": far(Dd, cal["D_diag"]),
                       "FAR_Tfull_chi2": far(Tf, c2), "FAR_Tdiag_chi2": far(Td, c2),
                       "mean_Dfull": float(np.mean(Df)), "mean_Ddiag": float(np.mean(Dd)),
                       "q95_Dfull": float(np.quantile(Df, .95)), "q95_Ddiag": float(np.quantile(Dd, .95)),
                       "kendall_tau_Dfull_vs_Ddiag": float(stats.kendalltau(Df[:3000], Dd[:3000])[0])}
                rows.append(row)
                print(f"{cname} delta={delta0} r={r:+.1f}: FAR D_full(transfer)={row['FAR_Dfull_transfer'][0]:.4f} "
                      f"D_diag(transfer)={row['FAR_Ddiag_transfer'][0]:.4f}  T_full(chi2_2)={row['FAR_Tfull_chi2'][0]:.4f} "
                      f"T_diag(chi2_2)={row['FAR_Tdiag_chi2'][0]:.4f}  tau={row['kendall_tau_Dfull_vs_Ddiag']:.3f}")
            out[f"{cname}_delta{delta0}"] = {"calibrated_thresholds_r0": cal, "rows": rows}
    # B3: redundancy count K with equicorrelation, threshold transfer from (K=1, r=0) vs rank-aware chi2_K
    print("-- B3: redundancy (equicorrelated K) --")
    b3 = []
    c_ref = stats.chi2.ppf(0.95, 1)   # = exact 95% quantile of T at K=1 (T = z^2)
    for K in (1, 2, 4, 8):
        for r in (0.0, 0.5, 0.9):
            if K == 1 and r > 0:
                continue
            S = equicorr(K, r)
            rng = np.random.default_rng(SEED_EVAL + K)
            Z = rng.multivariate_normal(np.zeros(K), S, size=NMC)
            Tf = np.einsum("ij,jk,ik->i", Z, np.linalg.inv(S), Z)      # dist2 to all-independent region {0}
            Td = np.sum(Z ** 2, axis=1)
            row = {"K": K, "r": r,
                   "FAR_Tfull_transfer": far(Tf, c_ref), "FAR_Tdiag_transfer": far(Td, c_ref),
                   "FAR_Tfull_chi2K": far(Tf, stats.chi2.ppf(.95, K)), "FAR_Tdiag_chi2K": far(Td, stats.chi2.ppf(.95, K))}
            b3.append(row)
            print(f"K={K} r={r}: transfer FAR full={row['FAR_Tfull_transfer'][0]:.3f} diag={row['FAR_Tdiag_transfer'][0]:.3f} | "
                  f"chi2_K FAR full={row['FAR_Tfull_chi2K'][0]:.3f} diag={row['FAR_Tdiag_chi2K'][0]:.3f}")
    out["B3_redundancy"] = b3
    # B4: estimated Sigma (Wishart noise as a stand-in for estimation error), K=8, r=0.9
    print("-- B4: estimated Sigma-hat ~ Wishart(nu, Sigma)/nu --")
    b4 = []
    K, r = 8, 0.9
    S = equicorr(K, r)
    for nu in (20, 50, 200, 1000, None):
        rng = np.random.default_rng(SEED_EVAL + 99)
        Tvals, conds = [], []
        for _ in range(NMC // 4):
            z = rng.multivariate_normal(np.zeros(K), S)
            Sh = S if nu is None else stats.wishart.rvs(df=nu, scale=S / nu, random_state=rng)
            conds.append(np.linalg.cond(Sh))
            Tvals.append(float(z @ np.linalg.solve(Sh, z)))
        row = {"nu": nu, "FAR_Tfull_chi2_8": far(Tvals, stats.chi2.ppf(.95, K)), "median_cond": float(np.median(conds))}
        b4.append(row)
        print(f"nu={nu}: FAR(T_full, chi2_8)={row['FAR_Tfull_chi2_8'][0]:.4f}  median cond={row['median_cond']:.1f}")
    out["B4_estimated_sigma"] = b4
    results["B"] = out


# ==============================================================================================
# Experiment C -- estimation, dimensionality, model relevance (Gaussian data)
# ==============================================================================================
def experiment_C():
    print("\n=== Experiment C: Gaussian data, rank, first-order duplicates, implicit evidence ===")
    out = {}
    qs6 = [(0, 1, ()), (0, 1, (2,)), (0, 2, ()), (0, 2, (1,)), (1, 2, ()), (1, 2, (0,))]
    # C1: rank of Sigma (delta method) and MC covariance of z for K=6 > p(p-1)/2 = 3
    c1 = []
    for name, R in (("empty", np.eye(3)), ("generic", np.array([[1, .3, .5], [.3, 1, .4], [.5, .4, 1]]))):
        Sd = delta_sigma_z(R, qs6)
        ev_delta = np.linalg.eigvalsh(Sd)
        Lc = np.linalg.cholesky(R)
        for n in (200, 1000, 5000):
            rng = np.random.default_rng(SEED_DATA + n)
            Zs = np.array([fisher_z_vec(sample_corr(rng.normal(size=(n, 3)) @ Lc.T), n, qs6) for _ in range(NDATA)])
            C = np.cov(Zs, rowvar=False)
            ev = np.linalg.eigvalsh(C)
            # compare MC covariance to delta-method (scaled by sqrt(n-|S|-3) factors ~ sqrt(n))
            sc = np.array([math.sqrt(n - len(S) - 3) for (_, _, S) in qs6])
            Sd_n = Sd * np.outer(sc, sc) / n
            rel = float(np.max(np.abs(C - Sd_n)) / np.max(np.abs(Sd_n)))
            row = {"R": name, "n": n, "eig_delta": ev_delta.tolist(), "eig_MC": ev.tolist(), "max_rel_err_MC_vs_delta": rel,
                   "n_times_small_eigs": (n * ev[:3]).tolist()}
            c1.append(row)
            print(f"C1 {name} n={n}: MC eig={np.round(ev, 4)}  n*small={np.round(n * ev[:3], 2)}  rel.err vs delta={rel:.3f}")
        check(f"C1 delta-method rank = 3 ({name})", int(np.sum(ev_delta > 1e-8)) == 3, str(np.round(ev_delta, 6)))
    out["C1_rank"] = c1
    # C2: first-order duplicate. X->Z (a), Y isolated. Q = {X⊥Y, X⊥Y|Z}; truth pattern (1,1)
    q2 = [(0, 1, ()), (0, 1, (2,))]
    c2 = []
    for a in (0.0, 0.3, 0.6, 0.9):
        R = np.array([[1, 0, a], [0, 1, 0], [a, 0, 1.0]])
        Lc = np.linalg.cholesky(R)
        r_th = math.sqrt(1 - a * a)
        for n in (200, 1000):
            rng = np.random.default_rng(SEED_DATA + 7 * n + int(100 * a))
            Zs, Shs = [], []
            for _ in range(NDATA):
                Rh = sample_corr(rng.normal(size=(n, 3)) @ Lc.T)
                Zs.append(fisher_z_vec(Rh, n, q2)); Shs.append(delta_sigma_z(Rh, q2))
            Zs = np.array(Zs)
            r_mc = float(np.corrcoef(Zs.T)[0, 1])
            Sor = delta_sigma_z(R, q2)
            delta = np.array([3.0, 3.0])
            # distance of the TRUE model (1,1): calibration of 'true-model rejection' at chi2 thresholds
            row = {"a": a, "n": n, "r_theory": r_th, "r_MC": r_mc, "frac_z1_ne_z2": float(np.mean(np.abs(Zs[:, 0] - Zs[:, 1]) > 1e-12))}
            for mode, lam in (("support", None), ("pinv", None), ("ridge", 1e-1), ("ridge", 1e-2), ("ridge", 1e-3), ("ridge", 1e-4)):
                if a > 0 and mode != "pinv" and mode != "support":
                    continue
                P, N = weight_matrix(Sor, mode, lam)
                vals = np.array([dist2(z, (1, 1), delta, P, N) for z in Zs])
                rk = int(np.linalg.matrix_rank(Sor, tol=1e-9))
                key = mode if lam is None else f"ridge{lam:g}"
                finite = vals[np.isfinite(vals)]
                row[key] = {"frac_inf": float(np.mean(~np.isfinite(vals))),
                            "FAR_trueModel_chi2_rank": (float(np.mean(finite > stats.chi2.ppf(.95, rk))) if len(finite) else None),
                            "FAR_trueModel_chi2_2": (float(np.mean(finite > stats.chi2.ppf(.95, 2))) if len(finite) else None),
                            "median": (float(np.median(finite)) if len(finite) else None)}
            # plug-in Sigma-hat (delta method at the sample correlations)
            vals = np.array([float(z @ np.linalg.solve(Sh, z)) for z, Sh in zip(Zs, Shs)])
            row["plugin_inv"] = {"FAR_trueModel_chi2_2": float(np.mean(vals > stats.chi2.ppf(.95, 2))),
                                 "median_cond": float(np.median([np.linalg.cond(Sh) for Sh in Shs])),
                                 "q99": float(np.quantile(vals, .99))}
            c2.append(row)
            print(f"C2 a={a} n={n}: r_MC={r_mc:.4f} (theory {r_th:.4f})  " + "  ".join(
                f"{k}:inf={v['frac_inf']:.2f},FAR={v['FAR_trueModel_chi2_rank']}" for k, v in row.items() if isinstance(v, dict) and 'frac_inf' in v)
                + f"  plugin FAR={row['plugin_inv']['FAR_trueModel_chi2_2']:.4f} cond={row['plugin_inv']['median_cond']:.1f}")
            if a > 0:
                check(f"C2 r_MC~sqrt(1-a^2) a={a} n={n}", abs(r_mc - r_th) < 0.03, f"{r_mc:.4f} vs {r_th:.4f}")
    out["C2_first_order_duplicate"] = c2
    # C3: Proposition E -- GLS residual equals -z_{YZ|X} to first order
    c3 = []
    a = 0.6; r = math.sqrt(1 - a * a)
    R = np.array([[1, 0, a], [0, 1, 0], [a, 0, 1.0]]); Lc = np.linalg.cholesky(R)
    for n in (200, 1000, 5000):
        rng = np.random.default_rng(SEED_DATA + 11 * n)
        res, zyz = [], []
        for _ in range(NDATA):
            Rh = sample_corr(rng.normal(size=(n, 3)) @ Lc.T)
            z1, z2 = fisher_z_vec(Rh, n, q2)
            res.append((z2 - r * z1) / math.sqrt(1 - r * r))
            zyz.append(fisher_z_vec(Rh, n, [(1, 2, (0,))])[0])
        cc = float(np.corrcoef(res, zyz)[0, 1])
        c3.append({"a": a, "n": n, "corr_GLSresid_zYZgivenX": cc})
        print(f"C3 n={n}: corr((z2-r z1)/sqrt(1-r^2), z_YZ|X) = {cc:.4f}")
    check("C3 Proposition E (corr < -0.95 at n=5000)", c3[-1]["corr_GLSresid_zYZgivenX"] < -0.95, str(c3[-1]))
    out["C3_prop_E"] = c3
    # C4: realizability of P4 pattern pair, non-monotonicity of CI in conditioning
    # m_b: X->Z<-Y (collider): X⊥Y holds, X⊥Y|Z fails.
    b1, b2 = 0.6, 0.5
    cov = np.array([[1, 0, b1], [0, 1, b2], [b1, b2, b1 ** 2 + b2 ** 2 + 1.0]])
    d = np.sqrt(np.diag(cov)); Rb = cov / np.outer(d, d)
    pc_marg, pc_cond = pcorr_from_R(Rb, 0, 1, ()), pcorr_from_R(Rb, 0, 1, (2,))
    out["C4_realizability"] = {"m_b_collider_rho_XY": pc_marg, "m_b_collider_rho_XY|Z": pc_cond,
                               "m_a_pattern": "(1,1) with X->Z, Y isolated", "m_b_pattern": "(1,0)"}
    check("C4 collider realizes pattern (1,0)", abs(pc_marg) < 1e-12 and abs(pc_cond) > 0.1, f"{pc_marg:.3g}, {pc_cond:.4f}")
    # Sigma under m_b differs from Sigma under m_a (common-Sigma working assumption A3)
    out["C4_realizability"]["Sigma_z_under_m_b"] = delta_sigma_z(Rb, q2).tolist()
    out["C4_realizability"]["Sigma_z_under_m_a(a=0.6)"] = delta_sigma_z(np.array([[1, 0, .6], [0, 1, 0], [.6, 0, 1.]]), q2).tolist()
    results["C"] = out


# ==============================================================================================
# Experiment E -- beta-min eta misspecification (working model, K=2)
# ==============================================================================================
def experiment_eta():
    print("\n=== Experiment E: beta-min eta sensitivity (working model) ===")
    rows = []
    r = 0.5; S = np.array([[1, r], [r, 1.0]]); P = np.linalg.inv(S)
    true_eff = 0.1                     # atanh rho of the true weak dependence on q2
    for n in (200, 1000, 5000):
        zeta = np.array([0.0, math.sqrt(n - 4) * true_eff])
        rng = np.random.default_rng(SEED_EVAL + n)
        Z = rng.multivariate_normal(zeta, S, size=NMC // 4)
        for eta in (0.05, 0.1, 0.15, 0.2, 0.3):
            delta = np.array([math.sqrt(n - 3) * eta, math.sqrt(n - 4) * eta])
            D = np.array([D_score(z, [(1, 0)], [(1, 1)], delta, P) for z in Z])  # truth: f (pattern (1,0)) holds
            rows.append({"n": n, "eta": eta, "true_effect": true_eff, "mean_D": float(np.mean(D)),
                         "P(D<0)_wrong_sign": float(np.mean(D < 0))})
            print(f"n={n} eta={eta}: mean D={np.mean(D):9.2f}   P(D<0)={np.mean(D < 0):.3f}")
    results["E_eta"] = rows


if __name__ == "__main__":
    t0 = time.time()
    experiment_A()
    experiment_B()
    experiment_C()
    experiment_eta()
    results["meta"]["runtime_sec"] = time.time() - t0
    results["meta"]["failed_assertions"] = failures
    OUT.write_text(json.dumps(results, indent=1, default=lambda o: o if not isinstance(o, float) or math.isfinite(o) else str(o)), encoding="utf-8")
    print(f"\nWrote {OUT}  runtime {time.time() - t0:.1f}s  failed assertions: {len(failures)}")
    for f in failures:
        print("  FAILED:", f)
