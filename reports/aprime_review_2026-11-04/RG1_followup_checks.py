"""RG1 follow-up checks after the independent review (RG1_independent_review_vi.md).

Re-measures the reviewer's main numbers with separate code and fills the gaps the review listed.
Not RG2: no power comparison across methods on an alternative suite (table U is formula-style, one competitor, working model).

Run:  python -P -E RG1_followup_checks.py [--quick] [P Q R T U V W]
Writes RG1_followup_outputs.json next to this file (partial runs write RG1_followup_outputs_partial.json).

  P  M1  eta > beta: R1 / CT / BL1 on a weak collider; CT FWER on the weak chain with many replicates
  Q  M7  oracle and plain-pinv size along a = c/sqrt(n); stored predictions for the RG1 section 8.1 table
  R  M2  size of W_n at K = 70, 165, 616 for several lambda; hard truncation; per-model block seminorm size
  T  M2  true family-wise false certification at K = 70 (all DAGs) and K = 165 (local DAG family), bracketed
  U  M3  required signal for 90% power, one added-independence competitor, ridge metric, valid thresholds only
  V  M8  size under n*lambda -> infinity but sqrt(n)*lambda -> 0
  W  M4, Thm 6c  necessary condition for blindness; block seminorm is not blind; chi-bar at the least favourable point; Gaussian data
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rg", HERE / "RG1_numeric_checks.py")
rg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rg)

QUICK = "--quick" in sys.argv
SEED = 20261105
ALPHA = 0.05
results: dict = {"meta": {"quick": QUICK, "seed": SEED, "alpha": ALPHA}}
failures: list[str] = []
n_pass = 0
Q2, Q6 = rg.QS2, rg.QS6


def check(name, cond, detail=""):
    global n_pass
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if cond:
        n_pass += 1
    else:
        failures.append(f"{name}: {detail}")


def lam13(n):
    return n ** (-1 / 3)


# ---------------------------------------------------------------- fast d-separation with bit masks
def bits(m):
    while m:
        b = m & -m
        yield b.bit_length() - 1
        m ^= b


def dsep_fast(pa, x, y, Smask):
    anc = (1 << x) | (1 << y) | Smask
    frontier = anc
    while frontier:
        b = frontier & -frontier
        frontier ^= b
        new = pa[b.bit_length() - 1] & ~anc
        anc |= new
        frontier |= new
    adj = [0] * len(pa)
    for v in bits(anc):
        pm = pa[v]
        adj[v] |= pm
        for u in bits(pm):
            adj[u] |= (1 << v) | (pm & ~(1 << u))
    allowed = anc & ~Smask
    seen = 1 << x
    frontier = seen
    while frontier:
        b = frontier & -frontier
        frontier ^= b
        nb = adj[b.bit_length() - 1] & allowed & ~seen
        if (nb >> y) & 1:
            return False
        seen |= nb
        frontier |= nb
    return True


def pattern_fast(A, qs_prepared):
    p = A.shape[0]
    pa = [sum(1 << u for u in range(p) if A[u, v]) for v in range(p)]
    return tuple(int(dsep_fast(pa, x, y, m)) for (x, y, m) in qs_prepared)


def prep(qs):
    return [(x, y, sum(1 << s for s in S)) for (x, y, S) in qs]


class Family:
    """Unique Q-patterns of a DAG list, with for each ancestral feature (and negation) the patterns where it can be false."""

    def __init__(self, dags, qs):
        qp = prep(qs)
        p = dags[0].shape[0]
        self.p = p
        pats = [pattern_fast(A, qp) for A in dags]
        self.upats = sorted(set(pats))
        self.pid = {pt: i for i, pt in enumerate(self.upats)}
        self.PI = np.array(self.upats, dtype=bool)
        feats = [(x, y) for x, y in itertools.permutations(range(p), 2)]
        self.feat_names = [f"{x}inAn{y}" for x, y in feats] + [f"{x}notinAn{y}" for x, y in feats]
        F = len(self.feat_names)
        self.notf = np.zeros((len(self.upats), F), bool)
        self.anc_list = []
        for A, pt in zip(dags, pats):
            an = rg.ancestors_matrix(A)
            i = self.pid[pt]
            for j, (x, y) in enumerate(feats):
                if not an[x, y]:
                    self.notf[i, j] = True        # "x in An(y)" false here
                else:
                    self.notf[i, j + len(feats)] = True
        self.feats = feats

    def false_at(self, A):
        an = rg.ancestors_matrix(A)
        L = len(self.feats)
        out = np.zeros(2 * L, bool)
        for j, (x, y) in enumerate(self.feats):
            out[j] = not an[x, y]
            out[j + L] = bool(an[x, y])
        return out


# ==============================================================================================
# P: eta > beta
# ==============================================================================================
def check_P():
    print("\n=== P: eta > beta (M1) ===", flush=True)
    rng = np.random.default_rng(SEED + 1)
    fam = Family(rg.all_dags(3), Q6)
    Bm = [[0, 0, 0], [0, 0, 0], [.5, .05, 0]]
    R = rg.cov_from_sem(Bm)
    Atrue = rg.scm_adj(Bm)
    pstar = pattern_fast(Atrue, prep(Q6))
    rho = rg.rho_vec(R, Q6)
    beta = min(abs(math.atanh(rho[k])) for k in range(6) if pstar[k] == 0)
    falsef = fam.false_at(Atrue)
    qid_true = (~falsef) & (~fam.notf[fam.pid[pstar]]) & fam.notf.any(axis=0)
    tail = rg.WeightedTail(6, SEED + 11)
    tK = float(stats.norm.isf(ALPHA / 12))
    rows = []
    N = 150 if QUICK else 600
    for eta, grid in ((0.2, (200, 500, 1000, 2000, 5000, 10000, 20000, 50000)), (0.04, (1000, 5000, 20000, 50000, 100000))):
        for n in grid:
            nk = np.array([n - len(S) - 3 for (_, _, S) in Q6], float)
            delta = np.sqrt(nk) * eta
            Z, Sh, _ = rg.batch_z_sigma(rg.sample_cov_batch(R, n, N, rng), Q6, n)
            c = {"R1": 0, "R1raw": 0, "CT": 0, "BL1": 0}
            cert = {"R1": 0, "CT": 0, "BL1": 0}
            emp = 0
            for b in range(N):
                Wsq, wts = rg.metric_ridge(Sh[b], lam13(n))
                chat = tail.quantile(np.sort(wts)[::-1])
                d2 = np.array([rg.dist2_nnls(Z[b], pt, delta, Wsq) for pt in fam.upats])
                surv = d2 <= chat
                emp += not surv.any()
                sup = np.array([rg.sup_dist(Z[b], pt, delta) for pt in fam.upats])
                sb = sup <= tK
                ph = tuple(int(abs(Z[b, k]) < delta[k] / 2) for k in range(6))
                sets = {"R1": surv, "BL1": sb, "CT": np.array([pt == ph for pt in fam.upats])}
                for key, s in sets.items():
                    asserted = (~fam.notf[s].any(axis=0)) if s.any() else np.zeros(fam.notf.shape[1], bool)
                    c[key] += bool((asserted & falsef).any())
                    cert[key] += float((asserted & qid_true).sum()) / max(int(qid_true.sum()), 1)
                raw = (~fam.notf[surv].any(axis=0)) if surv.any() else np.ones(fam.notf.shape[1], bool)
                c["R1raw"] += bool((raw & falsef).any())
            row = {"eta": eta, "beta": beta, "n": n, "FWER_CT": c["CT"] / N, "FWER_R1": c["R1"] / N, "FWER_R1_no_abstain": c["R1raw"] / N, "FWER_BL1": c["BL1"] / N,
                   "cert_CT": cert["CT"] / N, "cert_R1": cert["R1"] / N, "cert_BL1": cert["BL1"] / N, "P_empty": emp / N, "reps": N}
            rows.append(row)
            print(f"P eta={eta} beta={beta:.3f} n={n}: FWER CT={row['FWER_CT']:.3f} R1={row['FWER_R1']:.3f} R1raw={row['FWER_R1_no_abstain']:.3f} BL1={row['FWER_BL1']:.3f} | cert CT={row['cert_CT']:.3f} R1={row['cert_R1']:.3f} BL1={row['cert_BL1']:.3f} | empty={row['P_empty']:.3f}", flush=True)
    # CT on the weak chain, vectorised, many replicates
    chain_rows = []
    NC = 5000 if QUICK else 50000
    n = 2000
    idx = {pt: i for i, pt in enumerate(fam.upats)}
    for h in (1.0, 2.0, 3.0, 4.0, 6.0):
        def build(b):
            return [[0, 0, 0], [0, 0, b], [b, 0, 0]]

        def beta_of(b):
            rr = rg.rho_vec(rg.cov_from_sem(build(b)), Q6)
            return abs(math.atanh(rr[0]))   # X-Y marginal is the weakest link of this chain
        b_sol = optimize.brentq(lambda b: beta_of(b) - h / math.sqrt(n), 1e-4, 3.0)
        Bx = build(b_sol)
        Ac = rg.scm_adj(Bx)
        ff = fam.false_at(Ac)
        Z = rg.batch_z_sigma(rg.sample_cov_batch(rg.cov_from_sem(Bx), n, NC, rng), Q6, n, want_sigma=False)[0]
        nk = np.array([n - len(S) - 3 for (_, _, S) in Q6], float)
        ph = np.abs(Z) < np.sqrt(nk) * (h / math.sqrt(n)) / 2
        codes, counts = np.unique(ph.astype(int), axis=0, return_counts=True)
        bad = 0
        for code, cnt in zip(codes, counts):
            i = idx.get(tuple(int(v) for v in code))
            if i is not None and ((~fam.notf[i]) & ff & fam.notf.any(axis=0)).any():
                bad += cnt
        chain_rows.append({"h": h, "FWER_CT": bad / NC, "reps": NC})
        print(f"P chain h={h}: FWER CT={bad / NC:.4f}", flush=True)
    hi = [r for r in rows if r["eta"] == 0.2]
    check("P.R1 with abstain can far exceed alpha when eta > 2 beta", max(r["FWER_R1"] for r in hi) > 0.5, str(max(r["FWER_R1"] for r in hi)))
    check("P.CT stays wrong at large n when eta > 2 beta, R1 recovers through empty C_n", hi[-1]["FWER_CT"] > 0.9 and hi[-1]["FWER_R1"] < 0.05, f"CT {hi[-1]['FWER_CT']:.3f}, R1 {hi[-1]['FWER_R1']:.3f}")
    results["P"] = {"collider": rows, "chain_CT": chain_rows}


# ==============================================================================================
# Q: oracle / pinv along a = c/sqrt(n)
# ==============================================================================================
def check_Q():
    print("\n=== Q: oracle and plain pinv on rank-drop paths (M7), predictions for section 8.1 ===", flush=True)
    rng = np.random.default_rng(SEED + 2)
    N = 2_000_000
    u = rng.standard_normal(N)
    g1, g2 = rng.standard_normal(N), rng.standard_normal(N)
    c2 = stats.chi2.ppf(.95, 2)

    def tail(x):
        return float(np.mean(x > c2))

    pred = {"V0 a=b=0: U^2+(wv)^2/(w^2+v^2)": tail(u**2 + (g1 * g2) ** 2 / (g1**2 + g2**2)),
            "oracle a=1/sqrt(n), b=0: U^2+(wv)^2": tail(u**2 + ((1 + g1) * g2) ** 2),
            "V0 a=1/sqrt(n), b=0": tail(u**2 + ((1 + g1) * g2) ** 2 / ((1 + g1) ** 2 + g2**2)),
            "oracle a=b=1/sqrt(n): U^2+(wv-1)^2/2": tail(u**2 + ((1 + g1) * (1 + g2) - 1) ** 2 / 2),
            "V0 a=b=1/sqrt(n)": tail(u**2 + ((1 + g1) * (1 + g2) - 1) ** 2 / ((1 + g1) ** 2 + (1 + g2) ** 2))}
    print(pred, flush=True)
    t2 = rg.WeightedTail(2, SEED + 21)
    rows = []
    B = 4000 if QUICK else 20000
    n = 5000
    for c in (.05, .1, .25, .5, 1.0):
        a = c / math.sqrt(n)
        R = np.array([[1, 0, a], [0, 1, 0], [a, 0, 1.0]])
        r = rg.size_grid(R, Q2, n, B, rng, t2, lam_funcs={"n^-1/3": lam13}, r_generic=2)
        lim = tail(u**2 + ((c + g1) * g2 / c) ** 2)
        rows.append({"path": "a=c/sqrt(n),b=0", "c": c, "oracle": r["oracle_seminorm"], "limit_oracle": lim, "pinv": r["pinv_plain"], "ridge": r["ridge[n^-1/3]"], "trunc": r["trunc"]})
        print(f"Q a=c/sqrt(n) c={c}: oracle={r['oracle_seminorm']:.4f} (limit {lim:.4f}) pinv={r['pinv_plain']:.4f} ridge={r['ridge[n^-1/3]']:.4f} trunc={r['trunc']:.4f}", flush=True)
    for c in (1.0, 1.5, 2.0, 3.0):
        a = c / math.sqrt(n)
        R = np.array([[1, a * a, a], [a * a, 1, a], [a, a, 1.0]])
        r = rg.size_grid(R, Q2, n, B, rng, t2, lam_funcs={"n^-1/3": lam13}, r_generic=2)
        w, v = c + g1, c + g2
        lim = tail(u**2 + (w * v - c * c) ** 2 / (w**2 + v**2))
        rows.append({"path": "a=b=c/sqrt(n)", "c": c, "oracle": r["oracle_seminorm"], "pinv": r["pinv_plain"], "limit_pinv": lim, "ridge": r["ridge[n^-1/3]"], "trunc": r["trunc"]})
        print(f"Q a=b=c/sqrt(n) c={c}: oracle={r['oracle_seminorm']:.4f} pinv={r['pinv_plain']:.4f} (limit {lim:.4f}) ridge={r['ridge[n^-1/3]']:.4f} trunc={r['trunc']:.4f}", flush=True)
    results["Q"] = {"predictions": pred, "rows": rows}


# ==============================================================================================
# R: size at large K
# ==============================================================================================
def chain_sem(p, b=.4):
    B = np.zeros((p, p))
    for i in range(1, p):
        B[i, i - 1] = b
    return B


def large_K_cell(R, A_true, qs, n, B, lams, rng, tail):
    K = len(qs)
    Z, Sh, _ = rg.batch_z_sigma(rg.sample_cov_batch(R, n, B, rng), qs, n)
    zeta = rg.pop_zeta(R, qs, n)
    E = Z - zeta
    w, V = np.linalg.eigh(Sh)
    w = np.clip(w, 0, None)
    Pv = np.einsum("bji,bj->bi", V, E) ** 2
    out = {}
    for name, lam in lams.items():
        stat = np.sum(Pv / (w + lam), axis=1)
        wts = (w / (w + lam))[:, ::-1]
        rej = [tail.reject(stat[b], wts[b][wts[b] > 1e-10]) for b in range(B)]
        out[f"ridge[{name}]"] = float(np.mean(rej))
    tau = n ** (-1 / 4)
    keep = w > tau
    stat = np.sum(Pv * keep / np.where(keep, w, 1.0), axis=1)
    rhat = np.maximum(keep.sum(axis=1), 1)
    out["trunc"] = float(np.mean(stat > stats.chi2.ppf(.95, rhat)))
    # per-model block seminorm at the true pattern (candidate from the review, M4)
    pat = pattern_fast(A_true, prep(qs))
    I = [k for k in range(K) if pat[k] == 1]
    if I:
        wI, VI = np.linalg.eigh(Sh[:, I][:, :, I])
        kI = wI > tau
        PI = np.einsum("bji,bj->bi", VI, Z[:, I]) ** 2
        st = np.sum(PI * kI / np.where(kI, wI, 1.0), axis=1)
        out["block_seminorm_I"] = float(np.mean(st > stats.chi2.ppf(.95, np.maximum(kI.sum(axis=1), 1))))
        out["block_I_size"] = len(I)
    out["reps"] = B
    return out


def check_R():
    print("\n=== R: size of W_n at large K (M2) ===", flush=True)
    rng = np.random.default_rng(SEED + 3)
    rows = []
    for p, c, Bb, ns in ((5, 2, 2000, (200, 500, 1000, 5000)), (6, 2, 1000, (200, 500, 1000, 5000)), (8, 2, 150, (200, 1000))):
        qs = rg.all_queries(p, c)
        K = len(qs)
        B = max(Bb // 5, 40) if QUICK else Bb
        tail = rg.WeightedTail(K, SEED + 30 + p)
        A0 = np.zeros((p, p), bool)
        for name, R, Atrue in (("identity", np.eye(p), A0), ("chain .4", rg.cov_from_sem(chain_sem(p)), rg.scm_adj(chain_sem(p)))):
            for n in ns:
                t0 = time.time()
                lams = {"n^-1/3": lam13(n), "0.5": .5, "2": 2.0}
                r = large_K_cell(R, Atrue, qs, n, B, lams, rng, tail)
                r.update({"K": K, "p": p, "truth": name, "n": n})
                rows.append(r)
                print(f"R K={K} {name} n={n}: ridge n^-1/3={r['ridge[n^-1/3]']:.3f} .5={r['ridge[0.5]']:.3f} 2={r['ridge[2]']:.3f} | trunc={r['trunc']:.3f} | block={r.get('block_seminorm_I', float('nan')):.3f} (|I|={r.get('block_I_size')}) | {time.time() - t0:.0f}s", flush=True)
    results["R"] = rows


# ==============================================================================================
# T: true family-wise false certification at large K
# ==============================================================================================
def decide(z, D, delta, Wsq, chat, lam, cap=8):
    """Decide d^2(z, m) <= chat. A sign opposite to z_k needs |z_k - u_k| >= |z_k| + delta_k, which costs more than chat whenever
    (|z_k|+delta_k)^2/(1+lam) > chat (Prop 5(i)), so those signs are pruned rigorously. The rest are enumerated if at most cap remain."""
    if len(D) == 0:
        return "accept" if float(np.sum((Wsq @ z) ** 2)) <= chat else "reject"
    base = Wsq @ z
    cols = Wsq[:, D]
    s0 = np.where(z[D] >= 0, 1.0, -1.0)

    def val(sg):
        A_ = cols * sg
        return optimize.nnls(A_, base - A_ @ delta[D], maxiter=30 * max(len(D), 3))[1] ** 2

    if val(s0) <= chat:
        return "accept"
    free = np.where((np.abs(z[D]) + delta[D]) ** 2 / (1 + lam) <= chat)[0]
    if len(free) > cap:
        free = free[np.argsort(np.abs(z[D][free]))][:cap]   # heuristic subset: a failure here stays ambiguous
        exact = False
    else:
        exact = True
    for flips in itertools.product((False, True), repeat=len(free)):
        if not any(flips):
            continue
        sg = s0.copy()
        sg[free[np.array(flips)]] *= -1
        if val(sg) <= chat:
            return "accept"
    return "reject" if exact else "ambiguous"


def status_family(z, Sh, lam, delta, fam, chat, falsef, Wsq):
    """Return (rejected_for_sure, certain_accept_indices, ambiguous_indices), with early stop once no false feature can be asserted."""
    PI = fam.PI
    az = np.abs(z)
    sup = np.maximum((az * PI).max(axis=1), (np.maximum(delta - az, 0) * (~PI)).max(axis=1))
    alive = np.where(sup**2 / (1 + lam) <= chat)[0]
    S = np.full(len(alive), np.inf)
    I_all = np.arange(len(z))
    for j, i in enumerate(alive):
        I = I_all[PI[i]]
        S[j] = float(z[I] @ np.linalg.solve(Sh[np.ix_(I, I)] + lam * np.eye(len(I)), z[I])) if len(I) else 0.0
    order = np.argsort(S)
    acc, amb = [], []
    covered = np.zeros(fam.notf.shape[1], bool)
    target = falsef & fam.notf.any(axis=0)
    for j in order:
        if S[j] > chat:
            break
        i = alive[j]
        D = I_all[~PI[i]]
        inactive = (az[D] >= delta[D] + math.sqrt(S[j])).all() if len(D) else True
        res = "accept" if inactive else decide(z, D, delta, Wsq, chat, lam)
        if res == "accept":
            acc.append(i)
            covered |= fam.notf[i]
            if (covered | ~target).all():
                return acc, amb, True
        elif res == "ambiguous":
            amb.append(i)
    return acc, amb, False


def local_dags(A0, depth):
    p = A0.shape[0]
    pairs = list(itertools.combinations(range(p), 2))
    seen = {A0.tobytes(): A0}
    front = [A0]
    for _ in range(depth):
        nxt = []
        for A in front:
            for i, j in pairs:
                for state in (0, 1, 2):
                    B = A.copy()
                    B[i, j] = state == 1
                    B[j, i] = state == 2
                    if B.tobytes() in seen:
                        continue
                    Rr = B.copy()
                    for _k in range(p):
                        Rr = Rr | (Rr @ B)
                    if np.diag(Rr).any():
                        continue
                    seen[B.tobytes()] = B
                    nxt.append(B)
        front = nxt
    return list(seen.values())


def check_T():
    print("\n=== T: true FWER at large K, bracketed (M2) ===", flush=True)
    rng = np.random.default_rng(SEED + 4)
    rows = []
    tails = {}

    def sem(p, edges):
        B = np.zeros((p, p))
        for u, v, w in edges:
            B[v, u] = w
        return B

    def local(topology, p, h, n):
        """Weights b on the given edges such that the weakest dependent coordinate has sqrt(n)*|atanh rho| = h."""
        qs = rg.all_queries(p, 2)
        A0 = rg.scm_adj(sem(p, [(u, v, 1.0) for u, v in topology]))
        pt = pattern_fast(A0, prep(qs))

        def beta_of(bb):
            rr = rg.rho_vec(rg.cov_from_sem(sem(p, [(u, v, bb) for u, v in topology])), qs)
            return min(abs(math.atanh(rr[k])) for k in range(len(qs)) if pt[k] == 0)
        target = h / math.sqrt(n)
        grid = np.geomspace(1e-3, 3.0, 60)          # beta(b) need not be monotone: take the first crossing; None if h is not attainable
        vals = [beta_of(g) - target for g in grid]
        for g0, g1, v0, v1 in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
            if v0 < 0 <= v1:
                bs = optimize.brentq(lambda bb: beta_of(bb) - target, g0, g1)
                return sem(p, [(u, v, bs) for u, v in topology])
        print(f"skip {topology} h={h} n={n}: not attainable", flush=True)
        return None

    chain3 = [(0, 1), (1, 2)]
    coll3 = [(0, 2), (1, 2)]
    two = [(0, 1), (2, 3)]
    longp = [(0, 2), (1, 2), (2, 3), (3, 4)]
    t0 = time.time()
    qs5 = rg.all_queries(5, 2)
    fam5 = Family(rg.all_dags(5), qs5)
    print(f"family p=5: K={len(qs5)}, patterns={len(fam5.upats)}, built in {time.time() - t0:.0f}s", flush=True)
    qs6 = rg.all_queries(6, 2)
    fam_cache = {}

    def fam_local(p, qs, top):
        # A smaller family is the conservative choice: if f is asserted in M, then C_n(M') is inside M_f for every M' in M,
        # so f is also asserted in M' whenever C_n(M') is non-empty. The FWER on the local family therefore upper-bounds that on M,
        # except for replicates where the local confidence set is empty.
        key = (p, tuple(top))
        if key not in fam_cache:
            A0 = rg.scm_adj(sem(p, [(u, v, 1.0) for u, v in top]))
            d = local_dags(A0, 1 if QUICK else 2)
            fam_cache[key] = Family(d, qs)
            print(f"local family p={p} {top}: DAGs={len(d)}, patterns={len(fam_cache[key].upats)}", flush=True)
        return fam_cache[key]

    N5, N6 = (60, 40) if QUICK else (400, 300)
    configs = []
    for n in (200, 500, 1000, 5000):
        configs.append((fam5, qs5, "all DAGs", "two edges .5 (fixed)", sem(5, [(u, v, .5) for u, v in two]), n, N5, ("n^-1/3",)))
    for n in (500, 1000, 5000):
        for h in (3.0, 6.0):
            for nm, top in (("chain3", chain3), ("collider3", coll3), ("two edges", two)):
                lams = ("n^-1/3", "2") if (h == 3.0 and n == 1000) else ("n^-1/3",)
                configs.append((fam_local(5, qs5, top), qs5, "local DAGs depth 2", f"{nm} local h={h:g}", local(top, 5, h, n), n, N5, lams))
    for n in (500, 1000):
        for nm, top in (("chain3", chain3), ("collider3", coll3)):
            configs.append((fam_local(6, qs6, top), qs6, "local DAGs depth 2", f"{nm} local h=3", local(top, 6, 3.0, n), n, N6, ("n^-1/3",)))
    TIME_CAP = 20 if QUICK else 180
    for fam, qs, famname, nm, Bm, n, N, lamset in configs:
        if Bm is None:
            continue
        K = len(qs)
        tail = tails.setdefault(K, rg.WeightedTail(K, SEED + 40 + K))
        R = rg.cov_from_sem(Bm)
        Atrue = rg.scm_adj(Bm)
        pstar = pattern_fast(Atrue, prep(qs))
        rho = rg.rho_vec(R, qs)
        faithful = all((abs(rho[k]) > 1e-10) == (pstar[k] == 0) for k in range(K))
        beta = min(abs(math.atanh(rho[k])) for k in range(K) if pstar[k] == 0)
        falsef = fam.false_at(Atrue)
        nk = np.array([n - len(S) - 3 for (_, _, S) in qs], float)
        delta = np.sqrt(nk) * beta
        for lamname in lamset:
            lam = lam13(n) if lamname == "n^-1/3" else float(lamname)
            t1 = time.time()
            Z, Sh, _ = rg.batch_z_sigma(rg.sample_cov_batch(R, n, N, rng), qs, n)
            zeta = rg.pop_zeta(R, qs, n)
            hi = lo = wexc = done = 0
            for b in range(N):
                if time.time() - t1 > TIME_CAP:
                    break
                done += 1
                Wsq, wts = rg.metric_ridge(Sh[b], lam)
                w_s = np.sort(wts)[::-1]
                w_s = w_s[w_s > 1e-10]
                chat = tail.quantile(w_s)
                if float(np.sum((Wsq @ (Z[b] - zeta)) ** 2)) <= chat:
                    continue                        # m* survives, so no false assertion is possible (Thm 1)
                wexc += 1
                acc, amb, stopped = status_family(Z[b], Sh[b], lam, delta, fam, chat, falsef, Wsq)
                if stopped:
                    continue
                target = falsef & fam.notf.any(axis=0)
                n_cert = (~fam.notf[acc].any(axis=0)) if acc else np.ones(fam.notf.shape[1], bool)
                allm = acc + amb
                n_all = (~fam.notf[allm].any(axis=0)) if allm else np.ones(fam.notf.shape[1], bool)
                if allm and (n_cert & target).any():    # ambiguous treated as rejected: upper bound
                    hi += 1
                if acc and (n_all & target).any():      # ambiguous treated as surviving: lower bound
                    lo += 1
            row = {"K": K, "family": famname, "n_patterns": len(fam.upats), "truth": nm, "faithful_on_Q": faithful, "beta": beta, "sqrt_n_beta": beta * math.sqrt(n), "n": n, "lambda": lamname, "reps": done,
                   "P(W_n>c)": wexc / done, "FWER_lower": lo / done, "FWER_upper": hi / done}
            rows.append(row)
            print(f"T K={K} {famname} | {nm} n={n} lam={lamname} sqrt(n)beta={beta * math.sqrt(n):.2f} faithful={faithful} reps={done}: P(W>c)={wexc / done:.3f} FWER in [{lo / done:.3f},{hi / done:.3f}] | {time.time() - t1:.0f}s", flush=True)
    results["T"] = rows


# ==============================================================================================
# U: required signal, ridge metric, valid thresholds
# ==============================================================================================
def check_U():
    print("\n=== U: required h^2 for 90% power, one added-independence competitor (M3) ===", flush=True)
    rng = np.random.default_rng(SEED + 5)
    Nd = 40000 if QUICK else 200000
    zb = float(stats.norm.ppf(.9))
    configs = [(6, 3, 3, 1, 2), (18, 6, 4, 1, 2), (24, 6, 4, 2, 3), (70, 10, 5, 2, 3), (70, 10, 5, 2, 6)]
    R2grid = (0.0, .1, .25, .5, .75, .9, .99)
    rows = []
    for K, r, p, c, Ip in configs:
        qs = rg.all_queries(p, c)
        Sfull = rg.sigma_closed(rg.cov_from_sem(chain_sem(p)), qs)
        for lam in (.1, .5):
            w_full = np.linalg.eigvalsh(Sfull)
            w_full = np.clip(w_full, 0, None)
            wf = np.sort(w_full / (w_full + lam))[::-1]
            wf = wf[wf > 1e-10]
            GG = rng.standard_normal((Nd, len(wf))) ** 2
            c_proj = float(np.quantile(GG @ wf, .95))
            for R2 in R2grid:
                m = Ip - 1
                Sg = np.eye(Ip)
                cvec = math.sqrt(R2 / m) * np.ones(m)
                Sg[-1, :m] = Sg[:m, -1] = cvec
                if R2 > 0.999:
                    continue
                Ainv = np.linalg.inv(Sg + lam * np.eye(Ip))
                ws = np.linalg.eigvalsh(Sg)
                wI = ws / (ws + lam)
                GI = rng.standard_normal((Nd, Ip))
                c_hyb = float(np.quantile((GI**2) @ wI, 1 - ALPHA / 2))
                L = np.linalg.cholesky(Sg)
                X = GI @ L.T

                def req(thr):
                    def pow_(h):
                        Xh = X.copy()
                        Xh[:, -1] += h
                        return float(np.mean(np.einsum("ij,jk,ik->i", Xh, Ainv, Xh) > thr)) - .9
                    return optimize.brentq(pow_, 0, 60, xtol=1e-3) ** 2

                # valid box competitors: BL1 at level alpha over K; per-model Bonferroni with the same alpha/2 budget on the block;
                # whitened contrast with ridge coefficient, Bonferroni over the block
                tK = float(stats.norm.isf(ALPHA / (2 * K)))
                tI = float(stats.norm.isf(ALPHA / 2 / (2 * Ip)))
                b_hat = cvec / (1 + lam)
                var = 1 - 2 * float(cvec @ b_hat) + float(b_hat @ b_hat)
                row = {"K": K, "r": r, "|I'|": Ip, "lambda": lam, "R2": R2, "h2_R1_projection": req(c_proj), "h2_hybrid_chi2": req(c_hyb), "h2_BL1": (tK + zb) ** 2, "h2_per_model_Bonf": (tI + zb) ** 2,
                       "h2_whitened_contrast": (tI + zb) ** 2 * var, "h2_NP_bound": (float(stats.norm.isf(ALPHA)) + zb) ** 2 * (1 - R2), "c_projection": c_proj, "c_hybrid": c_hyb}
                rows.append(row)
                print("U " + ", ".join(f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}" for k, v in row.items()), flush=True)
    results["U"] = rows


# ==============================================================================================
# V: n*lambda -> infinity with sqrt(n)*lambda -> 0
# ==============================================================================================
def check_V():
    print("\n=== V: Thm 3 under n*lambda -> infinity only (M8) ===", flush=True)
    rng = np.random.default_rng(SEED + 6)
    rows = []
    t2 = rg.WeightedTail(2, SEED + 61)
    t24 = rg.WeightedTail(24, SEED + 62)
    lf = {"n^-3/4": (lambda n: n ** (-3 / 4)), "n^-1/3": lam13}
    B = 2000 if QUICK else 10000
    for n in (1000, 5000, 20000, 100000):
        for aname, a in (("0", 0.0), ("n^-1/2", n ** -.5), ("n^-3/8", n ** (-3 / 8)), ("0.3", .3)):
            R = np.array([[1, 0, a], [0, 1, 0], [a, 0, 1.0]])
            r = rg.size_grid(R, Q2, n, B, rng, t2, lam_funcs=lf, r_generic=2)
            rows.append({"Q": "Q2", "n": n, "a": aname, "ridge_n^-3/4": r["ridge[n^-3/4]"], "ridge_n^-1/3": r["ridge[n^-1/3]"]})
            print(f"V Q2 n={n} a={aname}: ridge n^-3/4={r['ridge[n^-3/4]']:.4f} n^-1/3={r['ridge[n^-1/3]']:.4f}", flush=True)
        R4 = rg.cov_from_sem([[0, 0, 0, 0], [.5, 0, 0, 0], [.4, 0, 0, 0], [0, .3, .6, 0]])
        r = rg.size_grid(R4, rg.all_queries(4, 2), n, B // 4, rng, t24, lam_funcs=lf, r_generic=6)
        rows.append({"Q": "K=24", "n": n, "ridge_n^-3/4": r["ridge[n^-3/4]"], "ridge_n^-1/3": r["ridge[n^-1/3]"]})
        print(f"V K=24 n={n}: ridge n^-3/4={r['ridge[n^-3/4]']:.4f} n^-1/3={r['ridge[n^-1/3]']:.4f}", flush=True)
    results["V"] = rows


# ==============================================================================================
# W: M4 and chi-bar
# ==============================================================================================
def check_W():
    print("\n=== W: necessary condition for blindness, block seminorm, chi-bar (M4, Thm 6c) ===", flush=True)
    rng = np.random.default_rng(SEED + 7)
    R4 = np.array([[1, .35, .25, .3], [.35, 1, .2, .4], [.25, .2, 1, .45], [.3, .4, .45, 1.0]])
    dags4 = rg.all_dags(4)
    out = {"necessary": []}
    for c in (1, 2):
        qs = rg.all_queries(4, c)
        Sig = rg.sigma_closed(R4, qs)
        pats = {pattern_fast(A, prep(qs)) for A in dags4}
        r = rg.rank_num(Sig)
        blind = cand = viol = 0
        for pt in pats:
            f = rg.blind_conditions(Sig, pt)
            D = len(pt) - sum(pt)
            isb = f[0] and f[1]
            blind += isb
            cand += D > r
            viol += isb and not D > r
        out["necessary"].append({"K": len(qs), "rank": r, "patterns": len(pats), "blind": blind, "patterns_with_|D|>r": cand, "blind_without_|D|>r": viol})
        print(out["necessary"][-1], flush=True)
        check(f"W.|D|>r is necessary for blindness, K={len(qs)}", viol == 0)
    # block seminorm is not blind on the extreme example of RG1 section 8.3
    R_g = np.array([[1, .3, .5], [.3, 1, .4], [.5, .4, 1.0]])
    Sig = rg.sigma_closed(R_g, Q6)
    z = np.array([5.0, 40.0, 7.0, 6.0, 8.0, 9.0])
    I = [1]
    w, V = np.linalg.eigh(Sig[np.ix_(I, I)])
    S_block = float((V.T @ z[I]) @ ((V.T @ z[I]) / w))
    check("W.block seminorm sees the violation", abs(S_block - 1600) < 1e-9, f"{S_block:.1f}")
    out["block_example"] = S_block
    # chi-bar at the least favourable point: delta large, zeta at the vertex, working model
    S3 = np.array([[1, .4, .3], [.4, 1, .5], [.3, .5, 1.0]])
    wv, Vv = np.linalg.eigh(S3)
    Wsq3 = (Vv / np.sqrt(wv)) @ Vv.T
    Ncal = 5000 if QUICK else 40000
    cal = rng.multivariate_normal(np.zeros(3), S3, size=Ncal)
    q = {}
    for s in itertools.product((1.0, -1.0), repeat=2):
        A_ = Wsq3[:, [1, 2]] * np.array(s)
        vals = [optimize.nnls(A_, Wsq3 @ g)[1] ** 2 for g in cal]
        q[s] = float(np.quantile(vals, .95))
    cbar = max(q.values())
    delta = np.array([25.0, 25.0, 25.0])
    grid = []
    Nev = 5000 if QUICK else 40000
    for s, qv in q.items():
        zeta = np.array([0.0, s[0] * 25.0, s[1] * 25.0])
        Zv = rng.multivariate_normal(zeta, S3, size=Nev)
        v = np.array([rg.dist2_nnls(zz, (1, 0, 0), delta, Wsq3) for zz in Zv])
        grid.append({"sign": s, "q_sigma": qv, "P(reject) at c_bar": float(np.mean(v > cbar)), "P(reject) at own q_sigma": float(np.mean(v > qv))})
        print("W.LFC", grid[-1], flush=True)
    se = math.sqrt(ALPHA * (1 - ALPHA) / Nev)
    check("W.chi-bar reaches alpha at the worst vertex and never exceeds it", abs(max(g["P(reject) at c_bar"] for g in grid) - ALPHA) < 4 * se + 0.005 and max(g["P(reject) at c_bar"] for g in grid) <= ALPHA + 4 * se,
          str([round(g["P(reject) at c_bar"], 4) for g in grid]))
    out["chi_bar_LFC"] = {"c_bar": cbar, "grid": grid}
    # chi-bar on Gaussian data, |D| = 5: weak collider with the XY|Z coordinate at its boundary; c_bar calibrated at the population Sigma
    fam_rows = []
    n = 2000
    for h in (2.0, 4.0, 8.0):
        def build(b):
            return [[0, 0, 0], [0, 0, 0], [b, b, 0]]

        def beta_of(b):
            rr = rg.rho_vec(rg.cov_from_sem(build(b)), Q6)
            return abs(math.atanh(rr[1]))
        b_sol = optimize.brentq(lambda b: beta_of(b) - h / math.sqrt(n), 1e-4, 3.0)
        R = rg.cov_from_sem(build(b_sol))
        lam = lam13(n)
        St = rg.sigma_closed(R, Q6)
        Wsq, wts = rg.metric_ridge(St, lam)
        pat = (1, 0, 0, 0, 0, 0)
        nk = np.array([n - len(S) - 3 for (_, _, S) in Q6], float)
        delta = np.sqrt(nk) * (h / math.sqrt(n))
        G = rng.multivariate_normal(np.zeros(6), St, size=1000 if QUICK else 4000, check_valid="ignore")
        qs_ = []
        for s in itertools.product((1.0, -1.0), repeat=5):
            A_ = Wsq[:, 1:] * np.array(s)
            qs_.append(float(np.quantile([optimize.nnls(A_, Wsq @ g)[1] ** 2 for g in G], .95)))
        cbar_g = max(qs_)
        N = 500 if QUICK else 3000
        Z, Sh, _ = rg.batch_z_sigma(rg.sample_cov_batch(R, n, N, rng), Q6, n)
        rej = rej_I = 0
        wI = np.array([1 / (1 + lam)])
        cI = float(stats.chi2.ppf(.95, 1)) * wI[0]
        for b in range(N):
            Wb, _ = rg.metric_ridge(Sh[b], lam)
            d2 = rg.dist2_nnls(Z[b], pat, delta, Wb)
            rej += d2 > cbar_g
            rej_I += d2 > cI
        row = {"h": h, "b": b_sol, "c_bar": cbar_g, "c_I_pointwise": cI, "P(reject m*) chi-bar": rej / N, "P(reject m*) pointwise threshold": rej_I / N, "reps": N}
        fam_rows.append(row)
        print("W.Gaussian", row, flush=True)
    out["chi_bar_gaussian"] = fam_rows
    results["W"] = out


if __name__ == "__main__":
    t0 = time.time()
    table = {"P": check_P, "Q": check_Q, "R": check_R, "T": check_T, "U": check_U, "V": check_V, "W": check_W}
    selected = [a for a in sys.argv[1:] if a in table]
    for key in (selected or list(table)):
        tk = time.time()
        table[key]()
        print(f"--- check {key} done in {time.time() - tk:.1f}s", flush=True)
    results["meta"].update({"runtime_sec": time.time() - t0, "n_pass": n_pass, "failed_assertions": failures})
    out = HERE / ("RG1_followup_outputs_partial.json" if selected else "RG1_followup_outputs.json")
    out.write_text(json.dumps(results, indent=1, default=lambda o: (o.item() if hasattr(o, "item") else str(o))), encoding="utf-8")
    print(f"\nWrote {out}  runtime {time.time() - t0:.1f}s  PASS={n_pass} FAIL={len(failures)}")
    for f in failures:
        print("  FAILED:", f)
