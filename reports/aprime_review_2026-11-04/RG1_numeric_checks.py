"""RG1 numeric cross-checks for the R1 proof (see RG1_R1_proof_vi.md).

Purpose: try to BREAK the statements proved on paper, using code paths independent of the derivations
(finite-difference Jacobians, raw-data simulation, the Day-2 active-set solver, Neyman-Pearson formulas).
This is NOT RG2 (no power comparison across methods on an alternative suite) and NOT a causal pilot.
Only hand-specified 3-variable SCMs are simulated; DAG patterns for p<=4 are used for linear algebra only.

Run:  python -P -E RG1_numeric_checks.py [--quick]
Writes RG1_numeric_outputs.json next to this file. Seeds are fixed below (base SEED + check offset).

Check map (statement labels refer to RG1_R1_proof_vi.md):
  A  Lemma 1, Prop 2      closed-form Sigma vs finite differences vs Monte Carlo; unit diagonal; rank
  B  Theorem 4            seminorm blindness on true d-separation patterns (p=3,4)
  C  Thm 2/3, Prop 3      null calibration: oracle / hard truncation / ridge / plain pinv, incl. rank-drop paths
  D  Thm 1, 3, 5          family-wise false certification on p=3 DAG family; deterministic inclusion check
  E  Theorem 7            R2: monotonicity, Lipschitz, simultaneous-in-eta event, upper bound on beta
  F  Prop 5, 6, Thm 6     sup-norm bound, Schur identity, inactive certificate, interlacing, solver cross-check
  G  Prop 5, 8            threshold table (chi2_r vs Bonferroni); required noncentrality; NP upper bound
  H  Prop 7               consistent thresholding (CT) vs R1: pointwise vs local regime
  I  Thm 6                R1' pointwise threshold: valid pointwise, invalid in local regime; chi-bar threshold exact
  J  Prop 3, Thm 3 remark Day-2 ridge FAR explained quantitatively by the n*lambda rate condition
  K  Thm 2, Thm 3         adversarial truths: near-singular R, rank drop with rho_XY != 0, two weak links (added after the first full run;
                          every check has its own seed, so running K alone gives the same numbers as a run of all checks)
  L  Cor 4.1              feature-level blindness when M is restricted to sparse DAGs (linear algebra only; added after the main run)
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np
import scipy
from scipy import integrate, optimize, stats

QUICK = "--quick" in sys.argv
HERE = Path(__file__).resolve().parent
OUT = HERE / "RG1_numeric_outputs.json"
SEED = 20261104
NMC = 4000 if QUICK else 20000      # replicates for null-calibration grids
NFAM = 400 if QUICK else 2000       # replicates for family-wise checks (each is ~250 small NNLS)
NR2 = 40 if QUICK else 300          # replicates for eta-profile checks
MTAB = 40000                        # draws in the fixed table used for weighted chi-square tails
ALPHA = 0.05
NGRID = (200, 1000, 5000)
results: dict = {"meta": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
                          "platform": platform.platform(), "quick": QUICK, "NMC": NMC, "NFAM": NFAM, "NR2": NR2,
                          "MTAB": MTAB, "alpha": ALPHA, "seed": SEED}}
failures: list[str] = []
n_pass = 0


def check(name: str, cond: bool, detail=""):
    global n_pass
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if cond:
        n_pass += 1
    else:
        failures.append(f"{name}: {detail}")


def lam_main(n):      # pre-declared main ridge rate: lambda_n -> 0, sqrt(n) lambda_n -> infinity
    return n ** (-1 / 3)


def tau_main(n):      # pre-declared main truncation rate: tau_n -> 0, sqrt(n) tau_n -> infinity
    return n ** (-1 / 4)


# ----------------------------------------------------------------------------------------------
# Queries, closed-form Sigma (Lemma 1), sampling
# ----------------------------------------------------------------------------------------------
QS2 = [(0, 1, ()), (0, 1, (2,))]
QS6 = [(0, 1, ()), (0, 1, (2,)), (0, 2, ()), (0, 2, (1,)), (1, 2, ()), (1, 2, (0,))]


def all_queries(p, c):
    qs = []
    for i, j in itertools.combinations(range(p), 2):
        rest = [v for v in range(p) if v not in (i, j)]
        for size in range(c + 1):
            for S in itertools.combinations(rest, size):
                qs.append((i, j, S))
    return qs


def batch_resid_coefs(Cb, x, S):
    """Unit-variance residual of x on S as a linear form a^T V, for a batch of covariance matrices."""
    B, p = Cb.shape[0], Cb.shape[1]
    a = np.zeros((B, p))
    a[:, x] = 1.0
    if S:
        S = list(S)
        sol = np.linalg.solve(Cb[:, S][:, :, S], Cb[:, S, x][..., None])[..., 0]
        a[:, S] = -sol
    var = np.einsum("bi,bij,bj->b", a, Cb, a)
    return a / np.sqrt(var)[:, None]


def batch_z_sigma(Cb, qs, n=None, want_sigma=True):
    """Fisher-z vector (if n given) and closed-form Sigma (Isserlis) for a batch. Scale invariant by construction."""
    K, B = len(qs), Cb.shape[0]
    ax, ay, Cax, Cay, rho = [], [], [], [], np.zeros((B, K))
    for k, (x, y, S) in enumerate(qs):
        a1, a2 = batch_resid_coefs(Cb, x, S), batch_resid_coefs(Cb, y, S)
        c1, c2 = np.einsum("bij,bj->bi", Cb, a1), np.einsum("bij,bj->bi", Cb, a2)
        ax.append(a1); ay.append(a2); Cax.append(c1); Cay.append(c2)
        rho[:, k] = np.einsum("bi,bi->b", a1, c2)
    z = None
    if n is not None:
        nk = np.array([n - len(S) - 3 for (_, _, S) in qs], float)
        z = np.sqrt(nk)[None, :] * np.arctanh(rho)
    if not want_sigma:
        return z, None, rho
    Sig = np.zeros((B, K, K))
    for k in range(K):
        for l in range(k, K):
            a = np.einsum("bi,bi->b", ax[k], Cax[l])
            b = np.einsum("bi,bi->b", ax[k], Cay[l])
            c = np.einsum("bi,bi->b", ay[k], Cax[l])
            d = np.einsum("bi,bi->b", ay[k], Cay[l])
            rk, rl = rho[:, k], rho[:, l]
            num = (a * d + b * c) - rl * (a * c + b * d) - rk * (a * b + c * d) + 0.5 * rk * rl * (a * a + b * b + c * c + d * d)
            Sig[:, k, l] = Sig[:, l, k] = num / ((1 - rk * rk) * (1 - rl * rl))
    return z, Sig, rho


def sigma_closed(C, qs):
    return batch_z_sigma(C[None], qs)[1][0]


def pop_zeta(R, qs, n):
    return batch_z_sigma(R[None], qs, n, want_sigma=False)[0][0]


def rho_vec(R, qs):
    return batch_z_sigma(R[None], qs, None, want_sigma=False)[2][0]


def sample_cov_batch(R, n, B, rng):
    """Exact sampling of the sample covariance of n iid N(0,R) rows: (n-1) C_hat ~ Wishart(n-1, R) (Bartlett)."""
    p = R.shape[0]
    L = np.linalg.cholesky(R)
    nu = n - 1
    A = np.zeros((B, p, p))
    for i in range(p):
        A[:, i, i] = np.sqrt(rng.chisquare(nu - i, size=B))
        for j in range(i):
            A[:, i, j] = rng.standard_normal(B)
    M = L[None] @ A
    return (M @ np.swapaxes(M, 1, 2)) / nu


def cov_from_sem(order_coefs):
    """order_coefs: p x p strictly lower-triangular-in-topological-order weight matrix B, V = B V + e, Var(e)=1. Returns correlation."""
    B = np.asarray(order_coefs, float)
    p = B.shape[0]
    Inv = np.linalg.inv(np.eye(p) - B)
    C = Inv @ Inv.T
    d = np.sqrt(np.diag(C))
    return C / np.outer(d, d)


# ----------------------------------------------------------------------------------------------
# Graph helpers (DAG only; used for patterns and ancestral features)
# ----------------------------------------------------------------------------------------------
def all_dags(p):
    pairs = list(itertools.combinations(range(p), 2))
    out = []
    for cfg in itertools.product((0, 1, 2), repeat=len(pairs)):
        A = np.zeros((p, p), bool)     # A[i,j] = i -> j
        for (i, j), c in zip(pairs, cfg):
            if c == 1:
                A[i, j] = True
            elif c == 2:
                A[j, i] = True
        R_ = A.copy()
        for _ in range(p):
            R_ = R_ | (R_ @ A)
        if not np.any(np.diag(R_)):
            out.append(A)
    return out


def ancestors_matrix(A):
    R_ = A.copy()
    for _ in range(A.shape[0]):
        R_ = R_ | (R_ @ A)
    return R_


def d_separated(A, x, y, S):
    """Ancestral moral graph criterion (self-contained implementation)."""
    p = A.shape[0]
    anc = ancestors_matrix(A)
    keep = {x, y} | set(S)
    for v in list(keep):
        keep |= {u for u in range(p) if anc[u, v]}
    und = np.zeros((p, p), bool)
    for c in keep:
        pars = [u for u in keep if A[u, c]]
        for u in pars:
            und[u, c] = und[c, u] = True
        for u, w in itertools.combinations(pars, 2):
            und[u, w] = und[w, u] = True
    seen, stack = {x}, [x]
    while stack:
        v = stack.pop()
        for w in keep:
            if und[v, w] and w not in seen and w not in S:
                if w == y:
                    return False
                seen.add(w)
                stack.append(w)
    return True


def pattern_of(A, qs):
    return tuple(int(d_separated(A, x, y, S)) for (x, y, S) in qs)


# ----------------------------------------------------------------------------------------------
# Metrics and distances
# ----------------------------------------------------------------------------------------------
def metric_ridge(Sig, lam):
    w, V = np.linalg.eigh(Sig)
    w = np.clip(w, 0, None)
    Wsqrt = (V / np.sqrt(w + lam)) @ V.T
    return Wsqrt, w / (w + lam)


def metric_seminorm(Sig, tau):
    """Hard-truncated Sigma^+ square root (r x K) with truncation level tau."""
    w, V = np.linalg.eigh(Sig)
    keep = w > tau
    return (V[:, keep] / np.sqrt(w[keep])).T, int(keep.sum())


def dist2_nnls(z, pat, delta, Wsqrt):
    """inf_{u in R(pat)} ||Wsqrt (z-u)||^2 by exact NNLS over sign orthants of the dependent coordinates."""
    K = len(z)
    Dp = [k for k in range(K) if pat[k] == 0]
    base = Wsqrt @ z
    if not Dp:
        return float(base @ base)
    best = math.inf
    cols = Wsqrt[:, Dp]
    d = np.asarray(delta)[Dp]
    for signs in itertools.product((1.0, -1.0), repeat=len(Dp)):
        s = np.array(signs)
        A = cols * s
        b = base - A @ d
        _, rn = optimize.nnls(A, b, maxiter=50 * max(len(Dp), 3))
        best = min(best, rn * rn)
        if best <= 1e-22:
            return 0.0
    return best


def sup_dist(z, pat, delta):
    """Sup-norm distance from z to R(pat) (coordinate-wise product set)."""
    v = 0.0
    for k in range(len(z)):
        v = max(v, abs(z[k]) if pat[k] == 1 else max(delta[k] - abs(z[k]), 0.0))
    return v


def schur_stat(z, pat, Sig, lam):
    I = [k for k in range(len(z)) if pat[k] == 1]
    if not I:
        return 0.0
    A = Sig[np.ix_(I, I)] + lam * np.eye(len(I))
    return float(z[I] @ np.linalg.solve(A, z[I]))


def rank_num(M, tol=1e-9):
    return int(np.linalg.matrix_rank(M, tol=tol)) if M.size else 0


def blind_conditions(Sig, pat, tol=1e-8):
    """Theorem 4: (B1) range(Sigma) cap C_I = {0}; (B2) e_k not in range(Sigma)+C_I for every dependent k."""
    K = Sig.shape[0]
    w, V = np.linalg.eigh(Sig)
    U = V[:, w > tol]
    I = [k for k in range(K) if pat[k] == 1]
    Dp = [k for k in range(K) if pat[k] == 0]
    E = np.eye(K)
    base = np.hstack([U, E[:, I]])
    r_base = rank_num(base)
    b1 = r_base == U.shape[1] + len(I)
    b2 = all(rank_num(np.hstack([base, E[:, [k]]])) == r_base + 1 for k in Dp)
    return bool(b1), bool(b2), U.shape[1]


class WeightedTail:
    """Tail P(sum_j w_j g_j^2 > t) through a fixed table of draws (common random numbers)."""

    def __init__(self, K, seed):
        self.G2 = np.random.default_rng(seed).standard_normal((MTAB, K)) ** 2

    def quantile(self, w_sorted_desc, alpha=ALPHA):
        return float(np.quantile(self.G2[:, : len(w_sorted_desc)] @ w_sorted_desc, 1 - alpha))

    def reject(self, stat, w_sorted_desc, alpha=ALPHA):
        return float(np.mean(self.G2[:, : len(w_sorted_desc)] @ w_sorted_desc > stat)) < alpha


# ==============================================================================================
# A: closed-form Sigma
# ==============================================================================================
def num_jac_sigma(R, qs, h=1e-6):
    """Independent path: finite-difference gradient of atanh(rho_k) wrt the covariance + Wishart cov 2 tr(H C H C)."""
    p = R.shape[0]

    def g(C):
        return np.arctanh(rho_vec(C, qs))

    K = len(qs)
    grads = np.zeros((K, p, p))
    for i in range(p):
        for j in range(i, p):
            E = np.zeros((p, p))
            E[i, j] = E[j, i] = 1.0
            d = (g(R + h * E) - g(R - h * E)) / (2 * h)
            # symmetric gradient H with <H, E_ij> = d
            for k in range(K):
                grads[k, i, j] = grads[k, j, i] = d[k] if i == j else d[k] / 2
    S = np.zeros((K, K))
    for k in range(K):
        for l in range(K):
            S[k, l] = 2 * np.trace(grads[k] @ R @ grads[l] @ R)
    return S, grads


def check_A():
    print("\n=== A: closed-form Sigma (Lemma 1, Prop 2) ===")
    out = []
    rng = np.random.default_rng(SEED + 1)
    Rs = {"identity": np.eye(3),
          "generic": np.array([[1, .3, .5], [.3, 1, .4], [.5, .4, 1.0]]),
          "chain": cov_from_sem([[0, 0, 0], [.5, 0, 0], [0, .6, 0]]),
          "collider": cov_from_sem([[0, 0, 0], [0, 0, 0], [.6, .5, 0]])}
    for name, R in Rs.items():
        for qname, qs in (("QS2", QS2), ("QS6", QS6)):
            Sc = sigma_closed(R, qs)
            Sn, _ = num_jac_sigma(R, qs)
            err = float(np.max(np.abs(Sc - Sn)))
            check(f"A.closed-vs-FD {name}/{qname}", err < 1e-6, f"max err {err:.2e}")
            check(f"A.unit-diagonal {name}/{qname}", float(np.max(np.abs(np.diag(Sc) - 1))) < 1e-12)
            w = np.linalg.eigvalsh(Sc)
            check(f"A.PSD {name}/{qname}", w.min() > -1e-12, f"min eig {w.min():.2e}")
            rec = {"R": name, "Q": qname, "max_err_FD": err, "eigs": w.tolist(), "rank": int((w > 1e-9).sum())}
            out.append(rec)
        # rank: QS6 contains all marginals => rank == d = 3 at every R
        check(f"A.rank-QS6=d {name}", rank_num(sigma_closed(R, QS6)) == 3)
    # Prop 2 on p=4: rank <= d, equals d when all marginals are in Q; gradient-span dimension agrees
    R4 = cov_from_sem([[0, 0, 0, 0], [.5, 0, 0, 0], [.4, 0, 0, 0], [0, .3, .6, 0]])
    for c in (1, 2):
        qs = all_queries(4, c)
        S4 = sigma_closed(R4, qs)
        _, grads = num_jac_sigma(R4, qs)
        rk_grad = rank_num(grads.reshape(len(qs), -1), tol=1e-5)
        check(f"A.rank p=4 c={c}", rank_num(S4) == 6 == rk_grad, f"K={len(qs)} rank={rank_num(S4)} grad-span={rk_grad}")
    # rank-drop: QS2 at a=b=0 has rank 1, generic 2; r = sqrt(1-a^2)(formula R')
    for a in (0.0, 0.3, 0.6, 0.9):
        R = np.array([[1, 0, a], [0, 1, 0], [a, 0, 1.0]])
        S = sigma_closed(R, QS2)
        check(f"A.R-prime a={a}", abs(S[0, 1] - math.sqrt(1 - a * a)) < 1e-12, f"{S[0, 1]:.6f}")
    # Monte Carlo vs closed form, including raw-data path vs Bartlett path
    R = Rs["generic"]
    n = 2000
    B = 2000 if QUICK else 8000
    Z = batch_z_sigma(sample_cov_batch(R, n, B, rng), QS6, n, want_sigma=False)[0]
    C_mc = np.cov(Z, rowvar=False)
    sc = np.array([math.sqrt(n - len(S) - 3) for (_, _, S) in QS6])
    S_th = sigma_closed(R, QS6) * np.outer(sc, sc) / n
    rel = float(np.max(np.abs(C_mc - S_th)))
    check("A.MC-vs-closed (generic,QS6,n=2000)", rel < (0.15 if QUICK else 0.07), f"max abs err {rel:.3f}")
    # raw data (independent of the Bartlett sampler)
    Lc = np.linalg.cholesky(R)
    nr = 300
    Br = 500 if QUICK else 2500
    raw = np.zeros((Br, 6))
    for b in range(Br):
        X = rng.standard_normal((nr, 3)) @ Lc.T
        raw[b] = batch_z_sigma(np.cov(X, rowvar=False)[None], QS6, nr, want_sigma=False)[0][0]
    bart = batch_z_sigma(sample_cov_batch(R, nr, Br, rng), QS6, nr, want_sigma=False)[0]
    diff_mean = float(np.max(np.abs(raw.mean(0) - bart.mean(0)) / (raw.std(0) * math.sqrt(2 / Br))))
    diff_sd = float(np.max(np.abs(raw.std(0) / bart.std(0) - 1)))
    check("A.raw-data-vs-Bartlett", diff_mean < 4.5 and diff_sd < 0.12, f"max mean z-gap {diff_mean:.2f}, max sd ratio dev {diff_sd:.3f}")
    # second-order size of the component outside range(Sigma): ||(I-P)(z-zeta)|| = O_p(n^-1/2)
    so = []
    for n in NGRID:
        Cb = sample_cov_batch(np.eye(3), n, 2000, rng)
        Z = batch_z_sigma(Cb, QS6, n, want_sigma=False)[0]
        zeta = pop_zeta(np.eye(3), QS6, n)
        w, V = np.linalg.eigh(sigma_closed(np.eye(3), QS6))
        Nb = V[:, w < 1e-9]
        val = float(np.median(np.linalg.norm((Z - zeta) @ Nb, axis=1)))
        so.append({"n": n, "median_norm_outside_range": val, "times_sqrt_n": val * math.sqrt(n)})
        print(f"A.second-order n={n}: median ||(I-P)(z-zeta)||={val:.4f}, x sqrt(n)={val * math.sqrt(n):.3f}")
    check("A.second-order scale", so[-1]["median_norm_outside_range"] < so[0]["median_norm_outside_range"] / 3,
          "outside-range component shrinks like n^-1/2")
    results["A"] = {"table": out, "second_order": so}


# ==============================================================================================
# B: seminorm blindness on d-separation patterns
# ==============================================================================================
def check_B():
    print("\n=== B: seminorm blindness (Theorem 4) ===")
    rng = np.random.default_rng(SEED + 2)
    dags3 = all_dags(3)
    check("B.count 3-node DAGs = 25", len(dags3) == 25)
    pats3 = sorted({pattern_of(A, QS6) for A in dags3})
    check("B.count MEC patterns p=3 = 11", len(pats3) == 11, str(len(pats3)))
    out = {"p3": []}
    R_gen = np.array([[1, .3, .5], [.3, 1, .4], [.5, .4, 1.0]])
    for rname, R in (("generic", R_gen), ("identity", np.eye(3))):
        Sig = sigma_closed(R, QS6)
        Wsemi, r = metric_seminorm(Sig, 1e-9)
        delta = np.full(6, 8.0)
        for pat in pats3:
            b1, b2, rr = blind_conditions(Sig, pat)
            blind = b1 and b2
            vals = []
            for _ in range(8 if QUICK else 25):
                z = rng.normal(scale=6.0, size=6)
                vals.append(dist2_nnls(z, pat, delta, Wsemi))
            vmax = float(np.max(vals))
            if blind:
                check(f"B.blind => d2=0 {rname} pat={pat}", vmax < 1e-16, f"max d2 {vmax:.2e}")
            else:
                check(f"B.non-blind => d2>0 somewhere {rname} pat={pat}", vmax > 1e-6, f"max d2 {vmax:.3g}")
            out["p3"].append({"R": rname, "pattern": pat, "B1": b1, "B2": b2, "blind": blind, "rank": rr,
                              "n_indep": sum(pat), "max_d2_seminorm": vmax})
    # Blatant violation: chain pattern with X indep Y|Z while z_{XY|Z} is huge => seminorm distance still 0
    Sig = sigma_closed(R_gen, QS6)
    Wsemi, _ = metric_seminorm(Sig, 1e-9)
    pat_chain = (0, 1, 0, 0, 0, 0)
    z = np.array([5.0, 40.0, 7.0, 6.0, 8.0, 9.0])
    d_semi = dist2_nnls(z, pat_chain, np.full(6, 2.0), Wsemi)
    Wr, _ = metric_ridge(Sig, lam_main(1000))
    d_ridge = dist2_nnls(z, pat_chain, np.full(6, 2.0), Wr)
    check("B.blatant violation invisible to seminorm", d_semi < 1e-16, f"z_(XY|Z)=40, seminorm d2={d_semi:.2e}")
    check("B.same violation visible to ridge (CS bound)", d_ridge >= 40.0 ** 2 / (1 + lam_main(1000)) - 1e-9, f"ridge d2={d_ridge:.1f}")
    out["blatant"] = {"z": z.tolist(), "seminorm": d_semi, "ridge_lam": lam_main(1000), "ridge": d_ridge}
    # Prevalence on p=4 (linear algebra only, no data)
    R4 = np.array([[1, .35, .25, .3], [.35, 1, .2, .4], [.25, .2, 1, .45], [.3, .4, .45, 1.0]])   # generic PD point
    check("B.R4 PD", np.linalg.eigvalsh(R4).min() > 0.1)
    dags4 = all_dags(4)
    check("B.count 4-node DAGs = 543", len(dags4) == 543, str(len(dags4)))
    prev = []
    for c in (1, 2):
        qs = all_queries(4, c)
        Sig4 = sigma_closed(R4, qs)
        pats = sorted({pattern_of(A, qs) for A in dags4})
        flags = [blind_conditions(Sig4, pat) for pat in pats]
        nblind = sum(1 for f in flags if f[0] and f[1])
        byI = {}
        for pat, f in zip(pats, flags):
            byI.setdefault(sum(pat), [0, 0])
            byI[sum(pat)][0] += 1
            byI[sum(pat)][1] += int(f[0] and f[1])
        prev.append({"c": c, "K": len(qs), "rank": flags[0][2], "n_patterns": len(pats), "n_blind": nblind,
                     "by_n_indep": {str(k): {"patterns": v[0], "blind": v[1]} for k, v in sorted(byI.items())}})
        print(f"B.p=4 c={c}: K={len(qs)}, rank={flags[0][2]}, patterns={len(pats)}, blind={nblind}")
    check("B.count MEC patterns p=4 c=2 = 185", prev[1]["n_patterns"] == 185, str(prev[1]["n_patterns"]))
    out["p4_prevalence"] = prev
    results["B"] = out


# ==============================================================================================
# C: null calibration of the quadratic form W_n
# ==============================================================================================
def size_grid(R, qs, n, B, rng, tail, oracle=True, lam_funcs=None, r_generic=None):
    """Return rejection rates P(W_n > threshold) under the truth R for each variant of the quadratic form."""
    lam_funcs = lam_funcs or {"n^-1/3": lam_main}
    K = len(qs)
    Cb = sample_cov_batch(R, n, B, rng)
    Z, Sh, _ = batch_z_sigma(Cb, qs, n)
    zeta = pop_zeta(R, qs, n)
    E = Z - zeta
    w_all, V_all = np.linalg.eigh(Sh)
    w_all = np.clip(w_all, 0, None)
    Pv = np.einsum("bji,bj->bi", V_all, E) ** 2        # squared coordinates in eigenbasis of Sigma-hat
    res = {}
    # ridge with plug-in weighted calibration
    for lname, lf in lam_funcs.items():
        lam = lf(n)
        stat = np.sum(Pv / (w_all + lam), axis=1)
        wts = (w_all / (w_all + lam))[:, ::-1]        # descending
        rej = np.array([tail.reject(stat[b], wts[b]) for b in range(B)])
        res[f"ridge[{lname}]"] = float(rej.mean())
    # hard truncation with chi2_{r_hat}
    tau = tau_main(n)
    keep = w_all > tau
    rhat = keep.sum(axis=1)
    stat = np.sum(Pv * keep / np.where(keep, w_all, 1.0), axis=1)
    res["trunc"] = float(np.mean(stat > stats.chi2.ppf(1 - ALPHA, np.maximum(rhat, 1))))
    res["rhat_mean"] = float(rhat.mean())
    # plain pseudo-inverse of Sigma-hat with numerical tolerance only, chi2 with generic rank
    keep0 = w_all > 1e-10
    stat0 = np.sum(Pv * keep0 / np.where(keep0, w_all, 1.0), axis=1)
    rg = r_generic if r_generic is not None else int(np.median(keep0.sum(axis=1)))
    res["pinv_plain"] = float(np.mean(stat0 > stats.chi2.ppf(1 - ALPHA, rg)))
    res["pinv_df"] = rg
    if oracle:
        St = sigma_closed(R, qs)
        wt, Vt = np.linalg.eigh(St)
        kt = wt > 1e-9
        Pinv = (Vt[:, kt] / wt[kt]) @ Vt[:, kt].T
        stat_o = np.einsum("bi,ij,bj->b", E, Pinv, E)
        res["oracle_seminorm"] = float(np.mean(stat_o > stats.chi2.ppf(1 - ALPHA, int(kt.sum()))))
        res["true_rank"] = int(kt.sum())
        res["true_smallest_pos_eig"] = float(wt[kt].min())
    res["mc_se_at_alpha"] = math.sqrt(ALPHA * (1 - ALPHA) / B)
    return res


def check_C():
    print("\n=== C: null calibration of W_n (Thm 2, Thm 3, Prop 3) ===")
    rng = np.random.default_rng(SEED + 3)
    lamf = {"n^-1/3": lam_main, "n^-1/4": (lambda n: n ** (-1 / 4)), "0.05": (lambda n: 0.05)}
    # Table check of the weighted-tail helper
    tail2 = WeightedTail(2, SEED + 31)
    check("C.tail-table chi2_2", abs(tail2.quantile(np.array([1., 1.])) - stats.chi2.ppf(.95, 2)) < 0.1)
    # Rank-drop path for QS2: a_n -> 0 at several rates (truth pattern (1,1), Z may be independent)
    q2_rows = []
    for n in NGRID:
        lam = lam_main(n)
        tau = tau_main(n)
        for aname, a in (("0", 0.0), ("n^-1/2", n ** -0.5), ("sqrt(2 lam)", math.sqrt(2 * lam)), ("sqrt(2 tau)", math.sqrt(2 * tau)),
                         ("n^-1/4", n ** -0.25), ("0.3", 0.3), ("0.6", 0.6), ("0.9", 0.9)):
            if a >= 0.999:
                continue
            R = np.array([[1, 0, a], [0, 1, 0], [a, 0, 1.0]])
            row = size_grid(R, QS2, n, NMC, rng, tail2, lam_funcs=lamf, r_generic=2)
            row.update({"n": n, "a_name": aname, "a": a})
            q2_rows.append(row)
            print(f"C.QS2 n={n} a={aname}({a:.3f}): ridge n^-1/3={row['ridge[n^-1/3]']:.4f} n^-1/4={row['ridge[n^-1/4]']:.4f} "
                  f"0.05={row['ridge[0.05]']:.4f} | trunc={row['trunc']:.4f} (rhat {row['rhat_mean']:.2f}) | "
                  f"pinv={row['pinv_plain']:.4f} | oracle={row['oracle_seminorm']:.4f}", flush=True)
    # Exact limit at a=0 for the plain pseudo-inverse: u^2 + (1/4) chi2_1 (Prop 3 / Glonek; Drton-Xiao Thm 2.3)
    c2 = stats.chi2.ppf(.95, 2)
    tail_th = integrate.quad(lambda u: 2 * stats.norm.pdf(u) * (stats.chi2.sf(4 * max(c2 - u * u, 0.0), 1) if u * u < c2 else 1.0),
                             0, 8, limit=200, points=[math.sqrt(c2)])[0]
    mc5000 = [r for r in q2_rows if r["n"] == 5000 and r["a_name"] == "0"][0]["pinv_plain"]
    print(f"C.plain pinv at a=0: theoretical tail P(chi2_1 + chi2_1/4 > {c2:.3f}) = {tail_th:.5f}; MC at n=5000: {mc5000:.5f}; Day-2 toy: 0.018 (n=200), 0.014 (n=1000)")
    se = math.sqrt(tail_th * (1 - tail_th) / NMC)
    check("C.plain pinv limit matches chi2_1+chi2_1/4", abs(mc5000 - tail_th) < 4 * se + 0.002, f"{mc5000:.4f} vs {tail_th:.4f}")
    # Over-complete Q (rank known): p=3 K=6; p=4 K=18, K=24; several truths
    over_rows = []
    tail6, tail18, tail24 = WeightedTail(6, SEED + 32), WeightedTail(18, SEED + 33), WeightedTail(24, SEED + 34)
    truths3 = {"identity": np.eye(3), "generic": np.array([[1, .3, .5], [.3, 1, .4], [.5, .4, 1.0]]),
               "chain": cov_from_sem([[0, 0, 0], [.5, 0, 0], [0, .6, 0]]), "collider": cov_from_sem([[0, 0, 0], [0, 0, 0], [.6, .5, 0]])}
    for n in NGRID:
        for name, R in truths3.items():
            row = size_grid(R, QS6, n, NMC // 2, rng, tail6, lam_funcs=lamf, r_generic=3)
            row.update({"n": n, "truth": name, "K": 6})
            over_rows.append(row)
            print(f"C.QS6 n={n} {name}: ridge n^-1/3={row['ridge[n^-1/3]']:.4f} n^-1/4={row['ridge[n^-1/4]']:.4f} 0.05={row['ridge[0.05]']:.4f} | "
                  f"trunc={row['trunc']:.4f} | pinv={row['pinv_plain']:.4f} | oracle={row['oracle_seminorm']:.4f}", flush=True)
    R4 = cov_from_sem([[0, 0, 0, 0], [.5, 0, 0, 0], [.4, 0, 0, 0], [0, .3, .6, 0]])
    for n in NGRID:
        for c, tail in ((1, tail18), (2, tail24)):
            qs = all_queries(4, c)
            row = size_grid(R4, qs, n, NMC // 4, rng, tail, lam_funcs={"n^-1/3": lam_main}, r_generic=6)
            row.update({"n": n, "truth": "p4-diamond", "K": len(qs)})
            over_rows.append(row)
            print(f"C.p4 K={len(qs)} n={n}: ridge n^-1/3={row['ridge[n^-1/3]']:.4f} | trunc={row['trunc']:.4f} | pinv={row['pinv_plain']:.4f} | oracle={row['oracle_seminorm']:.4f}", flush=True)
    # Pre-declared acceptance at n=5000 for the theorems (Thm 2 pointwise rows; Thm 3 all rows)
    tol = 0.02 if QUICK else 0.015
    for r in q2_rows:
        if r["n"] == 5000:
            check(f"C.Thm3 ridge size n=5000 QS2 a={r['a_name']}", abs(r["ridge[n^-1/3]"] - ALPHA) < tol, f"{r['ridge[n^-1/3]']:.4f}")
    for r in over_rows:
        if r["n"] == 5000:
            check(f"C.Thm3 ridge size n=5000 {r['truth']} K={r['K']}", abs(r["ridge[n^-1/3]"] - ALPHA) < tol, f"{r['ridge[n^-1/3]']:.4f}")
            check(f"C.Thm2 trunc size n=5000 {r['truth']} K={r['K']}", abs(r["trunc"] - ALPHA) < tol, f"{r['trunc']:.4f}")
    results["C"] = {"QS2_rank_drop_path": q2_rows, "overcomplete": over_rows, "pinv_limit_theory_tail": tail_th}


# ==============================================================================================
# D: family-wise false certification on a p=3 DAG family
# ==============================================================================================
SCMS = {
    "S1_chain": ([[0, 0, 0], [0, 0, .5], [.5, 0, 0]], "X->Z->Y"),       # V=(X,Y,Z): Z=.5X, Y=.5Z
    "S2_collider": ([[0, 0, 0], [0, 0, 0], [.4, .4, 0]], "X->Z<-Y"),
    "S3_single_edge": ([[0, 0, 0], [0, 0, 0], [.5, 0, 0]], "X->Z, Y isolated"),
    "S4_complete": ([[0, 0, 0], [.3, 0, .3], [.3, 0, 0]], "X->Z->Y, X->Y"),
}


def family_p3():
    dags = all_dags(3)
    pats = [pattern_of(A, QS6) for A in dags]
    anc = [ancestors_matrix(A) for A in dags]
    feats = []
    for x, y in itertools.permutations(range(3), 2):
        feats.append((f"{x}inAn{y}", [bool(a[x, y]) for a in anc]))
        feats.append((f"{x}notinAn{y}", [not a[x, y] for a in anc]))
    return dags, pats, feats


def scm_adj(Bmat):
    return (np.asarray(Bmat).T != 0)     # B[i,j] != 0 means j -> i, so A[j,i] True


def check_D():
    print("\n=== D: family-wise false certification (Thm 1, Thm 3, Thm 5) ===")
    rng = np.random.default_rng(SEED + 4)
    dags, pats, feats = family_p3()
    upats = sorted(set(pats))
    pid = {p: i for i, p in enumerate(upats)}
    tail = WeightedTail(6, SEED + 41)
    rows = []
    for sname, (Bm, desc) in SCMS.items():
        R = cov_from_sem(Bm)
        Atrue = scm_adj(Bm)
        idx_true = [i for i, A in enumerate(dags) if np.array_equal(A, Atrue)]
        check(f"D.true DAG in family {sname}", len(idx_true) == 1)
        mstar = idx_true[0]
        rho = rho_vec(R, QS6)
        pat_star = pats[mstar]
        check(f"D.faithful on Q {sname}", all((abs(rho[k]) < 1e-12) == (pat_star[k] == 1) for k in range(6)), str(np.round(rho, 3)))
        beta = min((abs(math.atanh(rho[k])) for k in range(6) if pat_star[k] == 0), default=math.inf)
        for n in NGRID:
            nk = np.array([n - len(S) - 3 for (_, _, S) in QS6], float)
            eta_opts = {"pointwise n^-1/4/2": n ** (-1 / 4) / 2}
            if math.isfinite(beta):
                eta_opts["boundary beta"] = beta
                if sname == "S1_chain":
                    eta_opts["misspecified 2beta"] = 2 * beta
            for ename, eta in eta_opts.items():
                delta = np.sqrt(nk) * eta
                lam = lam_main(n)
                Cb = sample_cov_batch(R, n, NFAM, rng)
                Z, Sh, _ = batch_z_sigma(Cb, QS6, n)
                zeta = pop_zeta(R, QS6, n)
                in_region = all((abs(zeta[k]) < 1e-9) if pat_star[k] == 1 else (abs(zeta[k]) >= delta[k] - 1e-12) for k in range(6))
                n_false = n_false_abstain = n_w_exceed = n_inclusion_viol = 0
                cert_true_counts, denom_true = 0, 0
                empty_conf = 0
                semi_cert, semi_den = 0, 0
                for b in range(NFAM):
                    Wsq, wts = metric_ridge(Sh[b], lam)
                    wts_d = np.sort(wts)[::-1]
                    c_hat = tail.quantile(wts_d)
                    d2 = np.array([dist2_nnls(Z[b], p, delta, Wsq) for p in upats])
                    Wn = float(np.sum((Wsq @ (Z[b] - zeta)) ** 2))
                    n_w_exceed += Wn > c_hat
                    is_empty = d2.min() > c_hat
                    empty_conf += is_empty
                    any_false = False
                    for fname, truth in feats:
                        notf = {pid[pats[i]] for i, t in enumerate(truth) if not t}
                        T = min((d2[j] for j in notf), default=math.inf)
                        asserted = T > c_hat
                        if truth[mstar]:
                            # report only non-vacuous and Q-identifiable true features
                            qid = pid[pat_star] not in notf
                            if qid and notf:
                                denom_true += 1
                                cert_true_counts += bool(asserted and not is_empty)
                        elif asserted:
                            any_false = True
                    n_false += any_false
                    n_false_abstain += any_false and not is_empty
                    if b < 100:
                        # same data, truncated seminorm (contract C-c): expected to certify nothing when a blind pattern is in M_notf
                        Wsemi, r_semi = metric_seminorm(Sh[b], tau_main(n))
                        csemi = float(stats.chi2.ppf(1 - ALPHA, max(r_semi, 1)))
                        d2s = np.array([dist2_nnls(Z[b], p, delta, Wsemi) for p in upats])
                        for fname, truth in feats:
                            notf = {pid[pats[i]] for i, t in enumerate(truth) if not t}
                            if truth[mstar] and notf and pid[pat_star] not in notf:
                                semi_den += 1
                                semi_cert += bool(min(d2s[j] for j in notf) > csemi)
                    if any_false and in_region and not (Wn > c_hat):
                        n_inclusion_viol += 1
                row = {"scm": sname, "desc": desc, "n": n, "eta_rule": ename, "eta": eta, "beta": beta, "zeta_in_R(m*)": bool(in_region),
                       "FWER_false_cert": n_false / NFAM, "FWER_with_abstain_on_empty": n_false_abstain / NFAM,
                       "P(W_n>c_hat)": n_w_exceed / NFAM, "inclusion_violations": n_inclusion_viol,
                       "P(empty confidence set)": empty_conf / NFAM,
                       "cert_rate_true_Qid_nonvacuous": (cert_true_counts / denom_true if denom_true else None),
                       "cert_rate_seminorm_same_data": (semi_cert / semi_den if semi_den else None),
                       "mc_se": math.sqrt(ALPHA * (1 - ALPHA) / NFAM)}
                rows.append(row)
                print(f"D.{sname} n={n} eta={ename}({eta:.3f}) inR={in_region}: FWER={row['FWER_false_cert']:.4f} FWER_abstain={row['FWER_with_abstain_on_empty']:.4f} P(W>c)={row['P(W_n>c_hat)']:.4f} "
                      f"viol={n_inclusion_viol} empty={row['P(empty confidence set)']:.4f} certTrue={row['cert_rate_true_Qid_nonvacuous']} certSemi={row['cert_rate_seminorm_same_data']}", flush=True)
                check(f"D.inclusion false-cert => W_n>c ({sname},n={n},{ename})", n_inclusion_viol == 0 or not in_region)
                if in_region:
                    check(f"D.FWER<=P(W>c) ({sname},n={n},{ename})", row["FWER_false_cert"] <= row["P(W_n>c_hat)"] + 1e-12)
                if row["cert_rate_seminorm_same_data"] is not None:
                    check(f"D.seminorm certifies nothing ({sname},n={n},{ename})", row["cert_rate_seminorm_same_data"] == 0.0)
    results["D"] = rows


# ==============================================================================================
# E: R2
# ==============================================================================================
def eta_star_pattern(z, pat, nk, Wsq, c_hat, eta_hi=None, tol=1e-5):
    """inf{eta >= 0: d_eta^2(z, pat) > c_hat}; +inf if never (no dependent coordinate and d2 <= c_hat)."""
    Dp = [k for k in range(len(z)) if pat[k] == 0]
    d0 = dist2_nnls(z, pat, np.zeros(len(z)), Wsq)
    if d0 > c_hat:
        return 0.0
    if not Dp:
        return math.inf
    lo, hi = 0.0, 0.05 if eta_hi is None else eta_hi
    while dist2_nnls(z, pat, np.sqrt(nk) * hi, Wsq) <= c_hat:
        lo, hi = hi, hi * 2
        if hi > 1e4:
            return math.inf
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if dist2_nnls(z, pat, np.sqrt(nk) * mid, Wsq) > c_hat:
            hi = mid
        else:
            lo = mid
    return hi


def check_E():
    print("\n=== E: R2 eta-profile (Theorem 7) ===")
    rng = np.random.default_rng(SEED + 5)
    dags, pats, feats = family_p3()
    upats = sorted(set(pats))
    pid = {p: i for i, p in enumerate(upats)}
    tail = WeightedTail(6, SEED + 51)
    # monotonicity + Lipschitz on random instances
    mono_viol, lip_viol, nchk = 0, 0, 0
    grid = np.array([0, .02, .05, .1, .2, .4, .8])
    for _ in range(30 if QUICK else 150):
        z = rng.normal(scale=4, size=6)
        Sig = sigma_closed(np.array([[1, .3, .5], [.3, 1, .4], [.5, .4, 1.0]]), QS6)
        lam = 0.1
        Wsq, _ = metric_ridge(Sig, lam)
        Winv = Wsq.T @ Wsq
        nk = np.array([997., 996., 997., 996., 997., 996.])
        pat = upats[rng.integers(len(upats))]
        ds = [math.sqrt(dist2_nnls(z, pat, np.sqrt(nk) * e, Wsq)) for e in grid]
        for i in range(len(grid) - 1):
            nchk += 1
            mono_viol += ds[i + 1] < ds[i] - 1e-7
            # Lipschitz constant: max over sign vectors of ||t||_W, bounded by operator norm * ||sqrt(nk)||
            L = math.sqrt(np.linalg.eigvalsh(Winv).max()) * float(np.linalg.norm(np.sqrt(nk)))
            lip_viol += abs(ds[i + 1] - ds[i]) > L * (grid[i + 1] - grid[i]) + 1e-7
    check("E.monotone d_eta", mono_viol == 0, f"{nchk} steps")
    check("E.Lipschitz d_eta", lip_viol == 0, f"{nchk} steps")
    # simultaneous event: on E_n = {W_n <= c_hat}: eta*(f) >= beta for all false f, and beta <= eta_bar
    rows = []
    for sname, n in (("S1_chain", 1000), ("S2_collider", 1000), ("S2_collider", 5000), ("S4_complete", 1000), ("S1_chain", 200)):
        Bm, desc = SCMS[sname]
        R = cov_from_sem(Bm)
        Atrue = scm_adj(Bm)
        mstar = [i for i, A in enumerate(dags) if np.array_equal(A, Atrue)][0]
        rho = rho_vec(R, QS6)
        pat_star = pats[mstar]
        beta = min(abs(math.atanh(rho[k])) for k in range(6) if pat_star[k] == 0)
        nk = np.array([n - len(S) - 3 for (_, _, S) in QS6], float)
        lam = lam_main(n)
        Cb = sample_cov_batch(R, n, NR2, rng)
        Z, Sh, _ = batch_z_sigma(Cb, QS6, n)
        zeta = pop_zeta(R, QS6, n)
        viol_f, viol_bar, on_event = 0, 0, 0
        n_eta_star_true, sum_scaled = 0, 0.0
        for b in range(NR2):
            Wsq, wts = metric_ridge(Sh[b], lam)
            c_hat = tail.quantile(np.sort(wts)[::-1])
            etas = np.array([eta_star_pattern(Z[b], p, nk, Wsq, c_hat) for p in upats])
            eta_bar = float(np.max(etas))
            Wn = float(np.sum((Wsq @ (Z[b] - zeta)) ** 2))
            if Wn <= c_hat:
                on_event += 1
                viol_bar += beta > eta_bar + 1e-4
                for fname, truth in feats:
                    notf = {pid[pats[i]] for i, t in enumerate(truth) if not t}
                    if not notf:
                        continue
                    es = float(max(etas[j] for j in notf))
                    if not truth[mstar]:
                        viol_f += es < beta - 1e-4
                    elif pid[pat_star] not in notf and es < math.inf:
                        n_eta_star_true += 1
                        sum_scaled += es * math.sqrt(n)
        row = {"scm": sname, "n": n, "beta": beta, "beta_scaled_sqrt_n": beta * math.sqrt(n), "P(E_n)": on_event / NR2,
               "violations_false_f": viol_f, "violations_beta_le_etabar": viol_bar,
               "mean_sqrtn_etastar_true_Qid": (sum_scaled / n_eta_star_true if n_eta_star_true else None)}
        rows.append(row)
        print(f"E.{sname} n={n}: beta={beta:.3f} P(E_n)={row['P(E_n)']:.3f} viol_false={viol_f} viol_bar={viol_bar} mean sqrt(n) eta*(true Qid)={row['mean_sqrtn_etastar_true_Qid']}", flush=True)
        check(f"E.simultaneous false-f bound ({sname},n={n})", viol_f == 0)
        check(f"E.beta<=eta_bar ({sname},n={n})", viol_bar == 0)
    results["E"] = rows


# ==============================================================================================
# F: deterministic inequalities and cross-check with the Day-2 solver
# ==============================================================================================
def load_toy():
    spec = importlib.util.spec_from_file_location("a1_toy", HERE / "A1_toy_mechanism_validation.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_F():
    print("\n=== F: deterministic inequalities, solver cross-check (Prop 5, Prop 6, Thm 6) ===")
    rng = np.random.default_rng(SEED + 6)
    toy = load_toy()
    Rg = np.array([[1, .3, .5], [.3, 1, .4], [.5, .4, 1.0]])
    Sig = sigma_closed(Rg, QS6)
    pats = sorted(set(pattern_of(A, QS6) for A in all_dags(3)))
    tail = WeightedTail(6, SEED + 61)
    N = 200 if QUICK else 1000
    viol_sup = viol_schur = viol_inact = n_inact = 0
    for _ in range(N):
        z = rng.normal(scale=rng.choice([1.0, 4.0, 12.0]), size=6)
        delta = np.full(6, float(rng.choice([0.5, 2.0, 6.0])))
        lam = float(rng.choice([0.01, 0.1, 0.5]))
        Wsq, _ = metric_ridge(Sig, lam)
        pat = pats[rng.integers(len(pats))]
        d2 = dist2_nnls(z, pat, delta, Wsq)
        viol_sup += d2 < sup_dist(z, pat, delta) ** 2 / (1 + lam) - 1e-8
        S = schur_stat(z, pat, Sig, lam)
        viol_schur += d2 < S - 1e-8
        Dp = [k for k in range(6) if pat[k] == 0]
        if all(abs(z[k]) >= delta[k] + math.sqrt(S) for k in Dp):
            n_inact += 1
            viol_inact += abs(d2 - S) > 1e-7 * max(1, S)
    check("F.sup-norm lower bound d2 >= dist_inf^2/(1+lam)", viol_sup == 0, f"{N} random")
    # Thm 5(ii): d^2(z,m') >= (max_{k in Delta} gap_k - ||z-zeta||_inf)_+^2 / (1+lam), for zeta in R(m*)
    viol_sep = n_sep = 0
    for _ in range(N):
        pa, pb = pats[rng.integers(len(pats))], pats[rng.integers(len(pats))]
        if pa == pb:
            continue
        eta_d = float(rng.choice([0.5, 2.0, 6.0]))
        delta = np.full(6, eta_d)
        lam = float(rng.choice([0.01, 0.1, 0.5]))
        Wsq, _ = metric_ridge(Sig, lam)
        zeta = np.array([0.0 if pa[k] == 1 else rng.choice([-1, 1]) * (eta_d + abs(rng.normal(scale=3.0))) for k in range(6)])
        z = zeta + rng.normal(size=6)
        gaps = [abs(zeta[k]) if (pb[k] == 1 and pa[k] == 0) else eta_d for k in range(6) if pa[k] != pb[k]]
        lb = max(max(gaps) - float(np.max(np.abs(z - zeta))), 0.0) ** 2 / (1 + lam)
        n_sep += 1
        viol_sep += dist2_nnls(z, pb, delta, Wsq) < lb - 1e-8
    check("F.finite-form separation bound (Thm 5 ii)", viol_sep == 0, f"{n_sep} random")
    # Prop 6(iii): chain rule for S on I' = I + {k}
    viol_chain = 0
    for _ in range(200):
        z = rng.normal(scale=3.0, size=6)
        lam = float(rng.choice([0.01, 0.1, 0.5]))
        perm = rng.permutation(6)
        m_I = int(rng.integers(1, 5))
        I, k = list(perm[:m_I]), int(perm[m_I])
        A = Sig + lam * np.eye(6)
        AII = A[np.ix_(I, I)]
        b = np.linalg.solve(AII, A[np.ix_(I, [k])])[:, 0]
        cond_var = A[k, k] - float(A[k, I] @ b)
        lhs = float(z[I + [k]] @ np.linalg.solve(A[np.ix_(I + [k], I + [k])], z[I + [k]]))
        rhs = float(z[I] @ np.linalg.solve(AII, z[I])) + (z[k] - float(b @ z[I])) ** 2 / cond_var
        viol_chain += abs(lhs - rhs) > 1e-8 * max(1, abs(lhs))
    check("F.chain rule S_{I+k} = S_I + residual^2/cond_var", viol_chain == 0)
    # Prop 4(b): at eta=0 the complete pattern has distance 0 for any z, under any PD metric
    Wsq, _ = metric_ridge(Sig, 0.1)
    d_complete = [dist2_nnls(rng.normal(scale=5.0, size=6), (0, 0, 0, 0, 0, 0), np.zeros(6), Wsq) for _ in range(20)]
    check("F.eta=0: complete pattern has d2=0", max(d_complete) < 1e-16, f"max {max(d_complete):.1e}")
    check("F.Schur S_m <= T_m", viol_schur == 0, f"{N} random")
    check("F.inactive certificate T_m == S_m", viol_inact == 0, f"{n_inact} instances met the premise")
    # Interlacing: threshold of the I-block <= threshold of the full matrix (common random numbers)
    lam = 0.1
    viol_int = 0
    full = np.sort(metric_ridge(Sig, lam)[1])[::-1]
    c_full = tail.quantile(full)
    for pat in pats:
        I = [k for k in range(6) if pat[k] == 1]
        if not I:
            continue
        wI = np.sort(metric_ridge(Sig[np.ix_(I, I)], lam)[1])[::-1]
        check_w = np.all(wI <= full[: len(wI)] + 1e-12)
        c_I = tail.quantile(wI)
        viol_int += (not check_w) or (c_I > c_full + 1e-12)
    check("F.interlacing c_I <= c_full", viol_int == 0)
    # NNLS distance vs Day-2 active-set enumeration vs SLSQP multistart (independent paths), PD metric
    viol_enum = viol_slsqp = 0
    M = 30 if QUICK else 120
    for it in range(M):
        A_ = rng.normal(size=(3, 3))
        S3 = A_ @ A_.T + 0.3 * np.eye(3)
        d = np.sqrt(np.diag(S3))
        S3 = S3 / np.outer(d, d)
        z = rng.normal(scale=2.0, size=3)
        delta = np.abs(rng.normal(1.5, 0.5, size=3)) + 0.2
        pat = tuple(int(x) for x in rng.integers(0, 2, size=3))
        P = np.linalg.inv(S3)
        w, V = np.linalg.eigh(S3)
        Wsq = (V / np.sqrt(w)) @ V.T
        a = dist2_nnls(z, pat, delta, Wsq)
        b = toy.dist2(z, pat, delta, P)
        viol_enum += abs(a - b) > 1e-7 * max(1, abs(b))
        if it < (8 if QUICK else 20):
            c = toy.slsqp_reference(z, pat, delta, P, rng, starts=4)
            viol_slsqp += abs(a - c) > 1e-4 * max(1, abs(c))
    check("F.NNLS == Day-2 active-set enumeration", viol_enum == 0, f"{M} random")
    check("F.NNLS == SLSQP multistart", viol_slsqp == 0)
    results["F"] = {"sup_bound_violations": int(viol_sup), "schur_violations": int(viol_schur), "inactive_instances": int(n_inact),
                    "inactive_violations": int(viol_inact), "interlacing_violations": int(viol_int)}


# ==============================================================================================
# G: thresholds and required noncentrality (analytic)
# ==============================================================================================
def check_G():
    print("\n=== G: threshold geometry (Prop 5, Prop 8) ===")
    rows = []
    for p, c in ((3, 1), (4, 1), (4, 2), (5, 1), (5, 2), (5, 3), (6, 2), (8, 2), (10, 2), (10, 3), (15, 2), (20, 2)):
        K = len(all_queries(p, c)) if p <= 10 else math.comb(p, 2) * sum(math.comb(p - 2, s) for s in range(c + 1))
        r = math.comb(p, 2)
        cr = float(stats.chi2.ppf(1 - ALPHA, r))
        tK = float(stats.norm.isf(ALPHA / (2 * K)))
        Kcrit = ALPHA / (2 * stats.norm.sf(math.sqrt(cr)))
        rows.append({"p": p, "order": c, "K": K, "r": r, "c_r": cr, "t_K^2": tK * tK, "ratio c_r/t_K^2": cr / (tK * tK), "K_crit(r)": float(Kcrit),
                     "K_full": math.comb(p, 2) * 2 ** (p - 2)})
        print(f"G.p={p} c={c}: K={K} r={r} c_r={cr:.2f} t_K^2={tK * tK:.2f} ratio={cr / (tK * tK):.2f} K_crit={Kcrit:.3g} K_full={math.comb(p, 2) * 2 ** (p - 2)}")
    # For p>=3: even the largest possible Q (all CI queries) stays below K_crit(r), up to p=30
    ok = True
    for p in range(3, 31):
        r = math.comb(p, 2)
        logs = stats.norm.logsf(math.sqrt(stats.chi2.ppf(1 - ALPHA, r)))
        log_kcrit = math.log(ALPHA / 2) - logs
        log_kfull = math.log(r) + (p - 2) * math.log(2)
        ok = ok and (log_kfull < log_kcrit)
    check("G.K_full(p) < K_crit(r) for p=3..30 (projection never beats Bonferroni on one coordinate)", ok)
    # Required noncentrality for 90% power, single-coordinate competitor with |I'| constraints, K=70, r=10, |I'|=3
    pow_t = 0.90

    def ncp_needed(df, cval):
        f = lambda nc: stats.ncx2.sf(cval, df, nc) - pow_t
        return float(optimize.brentq(f, 1e-6, 400))

    configs = []
    for (K, r, Iprime) in ((6, 3, 1), (6, 3, 2), (18, 6, 2), (24, 6, 3), (70, 10, 3), (70, 10, 6)):
        cr = float(stats.chi2.ppf(1 - ALPHA, r))
        cI = float(stats.chi2.ppf(1 - ALPHA, Iprime))
        tK = float(stats.norm.isf(ALPHA / (2 * K)))
        tI = float(stats.norm.isf(ALPHA / (2 * Iprime)))
        zb = float(stats.norm.ppf(pow_t))
        row = {"K": K, "r": r, "|I'|": Iprime,
               "NCP_R1_projection": ncp_needed(Iprime, cr),
               "NCP_R1prime_per_model": ncp_needed(Iprime, cI),
               "h2_BL1_Bonferroni_K (no gain from R^2)": (tK + zb) ** 2,
               "h2_per_model_Bonferroni": (tI + zb) ** 2,
               "NCP_NP_oracle": (float(stats.norm.isf(ALPHA)) + zb) ** 2}
        row["breakeven_R2_R1_vs_BL1"] = max(0.0, 1 - row["h2_BL1_Bonferroni_K (no gain from R^2)"] / row["NCP_R1_projection"])
        row["breakeven_R2_R1prime_vs_per_model_Bonf"] = max(0.0, 1 - row["h2_per_model_Bonferroni"] / row["NCP_R1prime_per_model"])
        configs.append(row)
        print("G.NCP " + ", ".join(f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}" for k, v in row.items()))
    # Prop 7(iii): local-regime boundary h_CT = 2 t_K, and the corresponding eta at n = 1000, 5000
    hct = []
    for K in (6, 18, 24, 40, 70, 80):
        t = float(stats.norm.isf(ALPHA / (2 * K)))
        hct.append({"K": K, "h_CT=2t_K": 2 * t, "eta_at_n1000": 2 * t / math.sqrt(1000), "eta_at_n5000": 2 * t / math.sqrt(5000)})
        print(f"G.h_CT K={K}: {2 * t:.2f}  (eta: n=1000 {2 * t / math.sqrt(1000):.3f}, n=5000 {2 * t / math.sqrt(5000):.3f})")
    # Prop 8(ii): under the working model the statistic for a single-coordinate competitor is noncentral chi-square
    rng = np.random.default_rng(SEED + 9)
    S3 = np.array([[1, .4, .3], [.4, 1, .5], [.3, .5, 1.0]])    # I={0}, k=1, coordinate 2 stays dependent in both models
    ncp_rows = []
    for zeta_k in (0.0, 2.0, 4.0):
        zeta = np.array([0.0, zeta_k, 60.0])                    # coordinate 2 far from its constraint: inactive
        Z = rng.multivariate_normal(zeta, S3, size=4000 if QUICK else 40000)
        P = np.linalg.inv(S3[:2, :2])
        stat = np.einsum("ij,jk,ik->i", Z[:, :2], P, Z[:, :2])
        r2 = S3[0, 1] ** 2
        ncp = zeta_k ** 2 / (1 - r2)
        c = stats.chi2.ppf(.95, 2)
        emp, th = float(np.mean(stat > c)), float(stats.ncx2.sf(c, 2, ncp) if ncp > 0 else stats.chi2.sf(c, 2))
        ncp_rows.append({"zeta_k": zeta_k, "NCP": ncp, "empirical_tail": emp, "theory_tail": th})
        check(f"G.noncentral law zeta_k={zeta_k}", abs(emp - th) < 0.01 + 0.02 * QUICK, f"{emp:.4f} vs {th:.4f}")
    results["G"] = {"threshold_table": rows, "required_ncp": configs, "h_CT": hct, "noncentral_check": ncp_rows}


# ==============================================================================================
# H: consistent thresholding (CT) vs R1
# ==============================================================================================
def check_H():
    print("\n=== H: CT baseline (Prop 7) ===")
    rng = np.random.default_rng(SEED + 7)
    dags, pats, feats = family_p3()
    upats = sorted(set(pats))
    pid = {p: i for i, p in enumerate(upats)}
    tail = WeightedTail(6, SEED + 71)
    rows = []

    def evaluate(R, Bm, n, eta, label, Nrep):
        Atrue = scm_adj(Bm)
        mstar = [i for i, A in enumerate(dags) if np.array_equal(A, Atrue)][0]
        pat_star = pats[mstar]
        nk = np.array([n - len(S) - 3 for (_, _, S) in QS6], float)
        delta = np.sqrt(nk) * eta
        Cb = sample_cov_batch(R, n, Nrep, rng)
        Z, Sh, _ = batch_z_sigma(Cb, QS6, n)
        fw = {"R1": 0, "CT": 0}
        tr = {"R1": 0, "CT": 0}
        den = 0
        lam = lam_main(n)
        for b in range(Nrep):
            Wsq, wts = metric_ridge(Sh[b], lam)
            c_hat = tail.quantile(np.sort(wts)[::-1])
            d2 = np.array([dist2_nnls(Z[b], p, delta, Wsq) for p in upats])
            nonempty = d2.min() <= c_hat
            # CT: threshold at the midpoint delta/2 in the fixed-eta/local form; output pattern (if not in family: abstain)
            pi_hat = tuple(int(abs(Z[b, k]) < delta[k] / 2) for k in range(6))
            any_false = {"R1": False, "CT": False}
            for fname, truth in feats:
                notf = {pid[pats[i]] for i, t in enumerate(truth) if not t}
                r1 = nonempty and min((d2[j] for j in notf), default=math.inf) > c_hat
                inM = pi_hat in pid
                ct = inM and pid[pi_hat] not in notf and bool(notf)
                if truth[mstar]:
                    if notf and pid[pat_star] not in notf:
                        den += 1
                        tr["R1"] += r1
                        tr["CT"] += ct
                else:
                    any_false["R1"] |= r1
                    any_false["CT"] |= ct
            fw["R1"] += any_false["R1"]
            fw["CT"] += any_false["CT"]
        row = {"label": label, "n": n, "eta": eta, "sqrt_n_eta": eta * math.sqrt(n), "FWER_R1": fw["R1"] / Nrep, "FWER_CT": fw["CT"] / Nrep,
               "power_R1": tr["R1"] / den if den else None, "power_CT": tr["CT"] / den if den else None, "Nrep": Nrep}
        rows.append(row)
        print(f"H.{label} n={n} sqrt(n)eta={row['sqrt_n_eta']:.2f}: FWER R1={row['FWER_R1']:.4f} CT={row['FWER_CT']:.4f} | power R1={row['power_R1']} CT={row['power_CT']}", flush=True)
        return row

    Nrep = 200 if QUICK else 1000
    # Scenario note: a first quick run used S1_chain for pointwise power (its MEC has no Q-identifiable ancestral feature, so the
    # denominator is empty) and a collider for the local FWER check (wrong patterns assert nothing false there). Both were wrong
    # scenarios for the claim being tested, not failures of Prop 7; the collider rows are kept below because they are informative.
    # Pointwise: fixed SCM, eta_n -> 0 with eta_n <= beta at all n. Prop 7: CT FWER -> 0 and power -> 1.
    Bm = SCMS["S2_collider"][0]
    R = cov_from_sem(Bm)
    last = None
    for n in (200, 1000, 5000, 20000):
        last = evaluate(R, Bm, n, 0.5 * n ** (-1 / 4), "pointwise S2 eta=0.5 n^-1/4", Nrep)
    check("H.CT pointwise: FWER small at n=20000", last["FWER_CT"] <= 0.01, str(last["FWER_CT"]))
    check("H.CT pointwise: power near 1 at n=20000", last["power_CT"] is not None and last["power_CT"] >= 0.99, str(last["power_CT"]))
    # 'Eventually' is silent at finite n: same rate class but eta_n > beta until n is large (S1, beta = 0.222)
    Bm1 = SCMS["S1_chain"][0]
    R1_ = cov_from_sem(Bm1)
    for n in (200, 1000, 5000, 20000):
        evaluate(R1_, Bm1, n, 1.5 * n ** (-1 / 4), "pointwise S1 eta=1.5 n^-1/4 (too large until n~2000)", Nrep)
    # Local regime: h = sqrt(n) eta fixed, P changes with n; eta sits exactly at the boundary beta(P_n)
    n = 2000

    def local_scm(kind, h):
        def build(b):
            return [[0, 0, 0], [0, 0, 0], [b, b, 0]] if kind == "collider" else [[0, 0, 0], [0, 0, b], [b, 0, 0]]

        def beta_of(b):
            Bx = build(b)
            Rl = cov_from_sem(Bx)
            rr = rho_vec(Rl, QS6)
            pt = pattern_of(scm_adj(Bx), QS6)
            return min(abs(math.atanh(rr[k])) for k in range(6) if pt[k] == 0)
        target = h / math.sqrt(n)
        b_sol = optimize.brentq(lambda b: beta_of(b) - target, 1e-4, 3.0)
        return build(b_sol), target, b_sol

    loc_chain, loc_coll = [], []
    for h in (2.0, 3.0, 4.0, 6.0, 8.0):
        Bx, target, b_sol = local_scm("chain", h)
        loc_chain.append(evaluate(cov_from_sem(Bx), Bx, n, target, f"local chain h={h} (b={b_sol:.3f})", Nrep))
        Bx, target, b_sol = local_scm("collider", h)
        loc_coll.append(evaluate(cov_from_sem(Bx), Bx, n, target, f"local collider h={h} (b={b_sol:.3f})", Nrep))
    se = math.sqrt(ALPHA * (1 - ALPHA) / Nrep)
    check("H.local chain h=2: CT FWER exceeds alpha", loc_chain[0]["FWER_CT"] > ALPHA + 3 * se, f"CT {loc_chain[0]['FWER_CT']:.3f}")
    check("H.local chain h=2..8: R1 FWER <= alpha + 3 SE", all(r["FWER_R1"] <= ALPHA + 3 * se for r in loc_chain), str([r["FWER_R1"] for r in loc_chain]))
    check("H.local h=8: CT FWER back below alpha", loc_chain[-1]["FWER_CT"] <= ALPHA, f"CT {loc_chain[-1]['FWER_CT']:.3f}")
    results["H"] = rows


# ==============================================================================================
# I: R1' thresholds
# ==============================================================================================
def check_I():
    print("\n=== I: R1' per-model thresholds (Thm 6) ===")
    rng = np.random.default_rng(SEED + 8)
    out = {}
    # I1: pointwise threshold on true Gaussian data (true pattern, eta_n -> 0)
    tail = WeightedTail(6, SEED + 81)
    rows = []
    for sname in ("S1_chain", "S2_collider", "S3_single_edge"):
        Bm, _ = SCMS[sname]
        R = cov_from_sem(Bm)
        pat_star = pattern_of(scm_adj(Bm), QS6)
        I = [k for k in range(6) if pat_star[k] == 1]
        for n in NGRID:
            nk = np.array([n - len(S) - 3 for (_, _, S) in QS6], float)
            eta = n ** (-1 / 4) / 2
            delta = np.sqrt(nk) * eta
            lam = lam_main(n)
            NN = NFAM
            Cb = sample_cov_batch(R, n, NN, rng)
            Z, Sh, _ = batch_z_sigma(Cb, QS6, n)
            rej = 0
            eq = 0
            for b in range(NN):
                Wsq, _ = metric_ridge(Sh[b], lam)
                T = dist2_nnls(Z[b], pat_star, delta, Wsq)
                S = schur_stat(Z[b], pat_star, Sh[b], lam)
                eq += abs(T - S) < 1e-7 * max(1, S)
                wI = np.sort(metric_ridge(Sh[b][np.ix_(I, I)], lam)[1])[::-1]
                rej += T > tail.quantile(wI)
            rows.append({"scm": sname, "n": n, "df_I": len(I), "P(reject m*)": rej / NN, "P(T==S)": eq / NN})
            print(f"I.pointwise {sname} n={n}: |I|={len(I)} P(reject m*)={rej / NN:.4f} P(T=S)={eq / NN:.4f}", flush=True)
    out["pointwise"] = rows
    r5 = [r for r in rows if r["n"] == 5000]
    check("I.R1' pointwise size near alpha at n=5000", all(abs(r["P(reject m*)"] - ALPHA) < 0.02 for r in r5), str([r["P(reject m*)"] for r in r5]))
    # I2: the same threshold in the local regime (active constraints): invalid
    K = 2
    S2 = np.array([[1, .5], [.5, 1.0]])
    Wsq = np.linalg.cholesky(np.linalg.inv(S2)).T
    NN = NMC
    Zl = rng.multivariate_normal([0.0, 3.0], S2, size=NN)     # I={0}, D={1}, zeta at vertex with delta=3
    Tl = np.array([dist2_nnls(z, (1, 0), np.array([3.0, 3.0]), Wsq) for z in Zl])
    far = float(np.mean(Tl > stats.chi2.ppf(.95, 1)))
    check("I.R1' pointwise threshold invalid at active boundary", far > ALPHA + 3 * math.sqrt(ALPHA * (1 - ALPHA) / NN), f"P(reject m*)={far:.4f} at nominal {ALPHA}")
    c_05 = stats.chi2.ppf(.95, 1)
    mix = 0.5 * ALPHA + 0.5 * float(stats.chi2.sf(c_05, 2))
    check("I.active-boundary law = (chi2_1 + chi2_2)/2 mixture", abs(far - mix) < 4 * math.sqrt(mix * (1 - mix) / NN), f"{far:.4f} vs {mix:.4f}")
    # I3: chi-bar threshold, working model, K=3, I={0}, D={1,2}: exact validity over a grid of zeta in R(m)
    S3 = np.array([[1, .4, .3], [.4, 1, .5], [.3, .5, 1.0]])
    w, V = np.linalg.eigh(S3)
    Wsq3 = (V / np.sqrt(w)) @ V.T
    delta = np.array([2.0, 2.0, 2.0])
    Ncal = 4000 if QUICK else 20000
    cal = np.random.default_rng(SEED + 82).multivariate_normal(np.zeros(3), S3, size=Ncal)
    q_sigma = {}
    for s in itertools.product((1.0, -1.0), repeat=2):
        vals = []
        for g in cal:
            # T0^sigma(g) = dist^2(g, {v: v_0=0, s_k v_k >= 0}) by NNLS
            A = Wsq3[:, [1, 2]] * np.array(s)
            _, rn = optimize.nnls(A, Wsq3 @ g)
            vals.append(rn * rn)
        q_sigma[s] = float(np.quantile(vals, 0.95))
    c_bar = max(q_sigma.values())
    c1, c3 = stats.chi2.ppf(.95, 1), stats.chi2.ppf(.95, 3)
    check("I.chi-bar threshold between chi2_df(I) and chi2_r", c1 - 0.2 <= c_bar <= c3 + 0.2, f"{c1:.2f} <= {c_bar:.2f} <= {c3:.2f}")
    grid = []
    for z0 in ([0, 2, 2], [0, 2, -2], [0, -2, -2], [0, 2.5, 2], [0, 4, 2], [0, 8, 8], [0, 2, 8], [0, -8, 2]):
        zeta = np.array(z0, float)
        Nev = 4000 if QUICK else 12000
        Zv = rng.multivariate_normal(zeta, S3, size=Nev)
        Tv = np.array([dist2_nnls(z, (1, 0, 0), delta, Wsq3) for z in Zv])
        fr = float(np.mean(Tv > c_bar))
        grid.append({"zeta": z0, "P(reject m)": fr})
        print(f"I.chi-bar zeta={z0}: P(reject m)={fr:.4f} (c_bar={c_bar:.3f})", flush=True)
    se = math.sqrt(ALPHA * (1 - ALPHA) / (4000 if QUICK else 12000))
    check("I.chi-bar valid on grid", all(g["P(reject m)"] <= ALPHA + 4 * se for g in grid), f"max {max(g['P(reject m)'] for g in grid):.4f}")
    out.update({"local_invalid_FAR": far, "chi_bar": {"c_bar": c_bar, "q_by_sign": {str(k): v for k, v in q_sigma.items()}, "c_df_I": float(c1), "c_r": float(c3), "grid": grid}})
    results["I"] = out


# ==============================================================================================
# J: Day-2 ridge results vs the n*lambda condition
# ==============================================================================================
def check_J():
    print("\n=== J: Day-2 ridge FAR explained by n*lambda (Thm 3 remark) ===")
    rng = np.random.default_rng(SEED + 10)
    toy = json.loads((HERE / "A1_toy_outputs.json").read_text(encoding="utf-8"))
    rows_toy = toy["C"]["C2_first_order_duplicate"]
    N = 200000 if QUICK else 2000000
    u, v, w = rng.standard_normal(N), rng.standard_normal(N), rng.standard_normal(N)
    c1 = stats.chi2.ppf(.95, 1)
    out = []
    for n in (200, 1000):
        rec = [r for r in rows_toy if r["a"] == 0.0 and r["n"] == n][0]
        for lam, key in ((1e-1, "ridge0.1"), (1e-2, "ridge0.01"), (1e-3, "ridge0.001"), (1e-4, "ridge0.0001")):
            # a=0, oracle Sigma=[[1,1],[1,1]]: W = 2 u^2/(2+lam) + (wv)^2/(2 n lam) to leading order
            stat = 2 * u * u / (2 + lam) + (w * v) ** 2 / (2 * n * lam)
            pred = float(np.mean(stat > c1))
            obs = rec[key]["FAR_trueModel_chi2_rank"]
            out.append({"n": n, "lambda": lam, "n_lambda": n * lam, "predicted_FAR": pred, "Day2_observed_FAR": obs})
            print(f"J.n={n} lam={lam:g} (n*lam={n * lam:g}): predicted FAR={pred:.3f}, Day-2 observed={obs:.3f}")
            check(f"J.prediction matches Day-2 n={n} lam={lam:g}", abs(pred - obs) < 0.03, f"{pred:.3f} vs {obs:.3f}")
    results["J"] = out


# ==============================================================================================
# K: adversarial truths for the null calibration
# ==============================================================================================
def equi3(rho):
    return (1 - rho) * np.eye(3) + rho * np.ones((3, 3))


def check_K():
    print("\n=== K: adversarial truths (Thm 2, Thm 3): how far does the asymptotics reach at finite n? ===")
    rng = np.random.default_rng(SEED + 11)
    lamf = {"n^-1/3": lam_main, "n^-1/4": (lambda n: n ** (-1 / 4))}
    tail2, tail6 = WeightedTail(2, SEED + 111), WeightedTail(6, SEED + 112)
    rows = []
    for n in NGRID:
        cases = [("Q2 rank drop, rho_XY=0.5", np.array([[1, .5, 0], [.5, 1, 0], [0, 0, 1.0]]), QS2, tail2, 2),
                 ("Q2 two weak links a=b=n^-1/2", np.array([[1, n ** -1.0, n ** -.5], [n ** -1.0, 1, n ** -.5], [n ** -.5, n ** -.5, 1.0]]), QS2, tail2, 2),
                 ("Q2 equi 0.9", equi3(.9), QS2, tail2, 2),
                 ("Q6 equi 0.9 (lambda_min=0.1)", equi3(.9), QS6, tail6, 3),
                 ("Q6 equi 0.97 (lambda_min=0.03)", equi3(.97), QS6, tail6, 3),
                 ("Q6 strong marginal 0.8", np.array([[1, .8, .3], [.8, 1, .3], [.3, .3, 1.0]]), QS6, tail6, 3)]
        for name, R, qs, tail, rg in cases:
            row = size_grid(R, qs, n, NMC // 2, rng, tail, lam_funcs=lamf, r_generic=rg)
            row.update({"n": n, "case": name, "lambda_min_R": float(np.linalg.eigvalsh(R).min())})
            rows.append(row)
            print(f"K.{name} n={n}: ridge n^-1/3={row['ridge[n^-1/3]']:.4f} n^-1/4={row['ridge[n^-1/4]']:.4f} | trunc={row['trunc']:.4f} (rhat {row['rhat_mean']:.2f}) | "
                  f"pinv={row['pinv_plain']:.4f} | oracle={row['oracle_seminorm']:.4f} (rank {row['true_rank']})", flush=True)
    # Pre-declared: at n=5000 the ridge size stays within 0.02 of alpha on these truths
    for r in rows:
        if r["n"] == 5000:
            check(f"K.ridge size n=5000 {r['case']}", abs(r["ridge[n^-1/3]"] - ALPHA) < 0.02, f"{r['ridge[n^-1/3]']:.4f}")
    results["K"] = rows


# ==============================================================================================
# L: feature-level blindness for restricted model families
# ==============================================================================================
def check_L():
    print("\n=== L: feature-level blindness when M is restricted to DAGs with at most e edges (Cor 4.1) ===")
    R4 = np.array([[1, .35, .25, .3], [.35, 1, .2, .4], [.25, .2, 1, .45], [.3, .4, .45, 1.0]])
    R4b = np.array([[1, -.2, .3, .15], [-.2, 1, .25, -.35], [.3, .25, 1, .2], [.15, -.35, .2, 1.0]])
    dags = all_dags(4)
    rows = []
    for Rname, R in (("R4", R4), ("R4b", R4b)):
        check(f"L.{Rname} PD", np.linalg.eigvalsh(R).min() > 0.1)
        for c in (1, 2):
            qs = all_queries(4, c)
            Sig = sigma_closed(R, qs)
            pat_all = [pattern_of(A, qs) for A in dags]
            flags = {pt: blind_conditions(Sig, pt) for pt in set(pat_all)}
            blind = {pt: (f[0] and f[1]) for pt, f in flags.items()}
            anc = [ancestors_matrix(A) for A in dags]
            edges = [int(A.sum()) for A in dags]
            for emax in (1, 2, 3, 4, 5, 6):
                idx = [i for i in range(len(dags)) if edges[i] <= emax]
                n_feat = n_zero = 0
                n_pat_blind = len({pat_all[i] for i in idx if blind[pat_all[i]]})
                n_pat = len({pat_all[i] for i in idx})
                for x, y in itertools.permutations(range(4), 2):
                    for neg in (False, True):
                        notf = [i for i in idx if bool(anc[i][x, y]) == neg]       # models where the feature is false
                        yesf = [i for i in idx if bool(anc[i][x, y]) != neg]
                        if not notf or not yesf:
                            continue                                                 # vacuous or unassertable within M
                        n_feat += 1
                        n_zero += any(blind[pat_all[i]] for i in notf)
                row = {"R": Rname, "order": c, "K": len(qs), "max_edges": emax, "n_models": len(idx), "n_patterns": n_pat, "n_blind_patterns": n_pat_blind,
                       "n_nonvacuous_features": n_feat, "n_features_T_identically_0": n_zero}
                rows.append(row)
                print(f"L.{Rname} c={c} K={len(qs)} e<={emax}: models={len(idx)} patterns={n_pat} blind={n_pat_blind} | features={n_feat} with T==0: {n_zero}", flush=True)
    # Pre-declared: with at least 2 edges allowed, every non-vacuous ancestral feature (and negation) is blind at K=24
    check("L.K=24, e>=2: all features blind", all(r["n_features_T_identically_0"] == r["n_nonvacuous_features"] for r in rows if r["K"] == 24 and r["max_edges"] >= 2),
          str([(r["R"], r["max_edges"], r["n_features_T_identically_0"], r["n_nonvacuous_features"]) for r in rows if r["K"] == 24 and r["max_edges"] >= 2]))
    results["L"] = rows


if __name__ == "__main__":
    t0 = time.time()
    selected = [a for a in sys.argv[1:] if a in list("ABCDEFGHIJKL")]
    table = {"A": check_A, "B": check_B, "C": check_C, "D": check_D, "E": check_E, "F": check_F, "G": check_G, "H": check_H, "I": check_I, "J": check_J, "K": check_K, "L": check_L}
    for key in (selected or list(table)):
        tk = time.time()
        table[key]()
        print(f"--- check {key} done in {time.time() - tk:.1f}s", flush=True)
    results["meta"]["runtime_sec"] = time.time() - t0
    results["meta"]["n_pass"] = n_pass
    results["meta"]["failed_assertions"] = failures
    if selected:
        OUT = HERE / "RG1_numeric_outputs_partial.json"
    OUT.write_text(json.dumps(results, indent=1, default=lambda o: (o.item() if hasattr(o, "item") else str(o))), encoding="utf-8")
    print(f"\nWrote {OUT}  runtime {time.time() - t0:.1f}s  PASS={n_pass} FAIL={len(failures)}")
    for f in failures:
        print("  FAILED:", f)
