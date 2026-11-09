"""T4-L pilot at algorithm level. See T4L_pilot_report_vi.md.

Task, same for every method: from data with missing values output graph claims over the observed variables O, under Assumption 1 of Strobl et al. 2018 (indicators have no children), with latent
confounders allowed, alpha = .05, conditioning sets up to size 3 drawn from current adjacencies (PC-stable skeleton), no possible-d-sep phase, orientation by R0-R4 only.
Absolute counts therefore understate full FCI, for every method alike. Scored against the true DAG.

DATA. Random DAG on O and latents, expected degree 2.5 among O, round(.15 p) latents with two observed children each, weights +-U(.3,.7), Gaussian noise, columns standardized. 60% of variables
incomplete, target missing rate rho. Each incomplete variable: 1 or 2 parents from O (itself allowed), latent parent with prob .2, effect b ~ U(.5,1.5), intercept solved for the rate rho.
  mech = mcar   : no dependence (control).
  mech = add    : logit = a + b * mean of +-z_parent.
  mech = mixed  : each indicator draws one of add, interaction (b z1 z2), even (b (z1^2 - 1)), mcar with equal probability. This is the cell that decides.
GRID. p in {10, 20}, mech as above, rho in {.1, .25}, n in {1000, 4000}. Graphs per cell: 30 at p = 10, 12 at p = 20. Each method sees the same data.

METHODS.
  LW        all tests on listwise rows.
  Naive     test-wise, no confirmation.
  M1        Strobl Algorithm 1: reject at test-wise rows means dependent; otherwise re-test on listwise rows.
  LiftG1    M1 with the listwise re-test replaced by the indicator chain below, main-effects indicator model.
  LiftG2    same, indicator model with squares and products. PRIMARY, because the main-effects model was fragile in T4_lift_checks.py.
  PP        naive skeleton; R0 only after re-testing the separation on rows complete on {x,y,z}+W; no R1-R4 because composing them across regimes is unsound (T4_oracle_checks.py).
  PPL2      PP with the re-test replaced by the one-step indicator test, flexible model.
  Flag      naive skeleton; indicator neighbours learned by test-wise tests of R_i against V_j; an edge is flagged if both endpoints share an indicator neighbour or a neighbour that has one;
            no R0 from flagged edges. Cheapest version of the "do not trust this edge" idea of MVPC Step 3. Not the MVPC correction.
  MI        multiple imputation (5 linear-Gaussian chained imputations, 5 cycles) with z pooled by Rubin's rules, in the spirit of Witte et al. 2022 and micd. Own implementation.
  FCI-R     FCI on O and R with known arrowheads at R, test-wise rows, p = 10 only (cost). No edge R_i - O_i.
  MVPC      causal-learn's MVPC, only in a separate stratum: no latents, no variable causing its own indicator. Stronger assumptions and CPDAG output, so it is not in the decision rule.

INDICATOR CHAIN for a query x,y|W not rejected on rows complete on U = {x,y}+W. T = variables outside U with some missingness on those rows. Repeat: for each j in T test R_j against x given y,W and
against y given x,W on the current rows, Bonferroni alpha/|T| within the step. If both sides reject for some j, return dependent (one-step equivalence plus monotonicity). If one side has no rejection for
any j, return separated (Didelez et al. 2010 Thm 6). Otherwise move one j with a clean y side into U and continue. In the oracle this equals the listwise separation exactly (check V1).
The test is a score test of a linear probability model (m R^2 against chi-square), not logistic as in T4_lift_checks.py, for speed. Check V3 compares the two.

CLAIMS. Orientation claims: non-ancestor (no possibly-directed path) and pure ancestor (tail with an arrowhead at the same node, with transitive closure). Skeleton claims (no direct edge) reported apart.

READING RULES K8, FIXED BEFORE THE FIRST RUN. Thresholds are those proposed in T4_kill_test_vi.md section 8, made operational; project-management choices, not signed off by the user.
Pool the mixed cells: compute the ratio of mean counts per p, then average p = 10 and p = 20.
  (a) LiftG2 false orientation claims <= .70 of M1, with upper bootstrap 95% limit below 1.
  (b) LiftG2 true orientation claims >= .90 of M1.
  (c) No simple baseline ties or beats LiftG2. A baseline b ties or beats if false(b) <= 1.1 false(LiftG2) and true(b) >= .95 true(LiftG2). Baselines: LW, Naive, Flag, PP, MI, and FCI-R judged on p = 10 only.
  GO if (a), (b), (c) hold. NO-GO if (a) fails, or (c) fails. WEAK if (a) and (c) hold but (b) fails.
  Secondary, not in the verdict: same comparisons per cell and for add cells; LiftG1; PPL2 against PP; mcar control.
  Oracle checks V1 and V2 must pass, otherwise the code is wrong and the run is void.

Run: python -P -E T4L_algorithm_pilot.py [--quick] [--check-only]. Results are appended to T4L_pilot_results.jsonl so an interrupted run can continue.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys
import time
from pathlib import Path

for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"

import numpy as np  # noqa: E402
from scipy.stats import chi2  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import T4_oracle_checks as O  # noqa: E402

QUICK = "--quick" in sys.argv
CHECK_ONLY = "--check-only" in sys.argv
SEED = 20261111
ALPHA = .05
MAXORD = 3
OUT = HERE / ("T4L_pilot_quick.jsonl" if QUICK else "T4L_pilot_results.jsonl")


def bits_of(mask):
    return list(O.bits(mask))


# ---------------------------------------------------------------- data
def make_graph(p, rng, latent=True, no_self=False, mech="mixed", rho=.25):
    ell = int(round(.15 * p)) if latent else 0
    g = O.MDag(p, ell)
    order = [int(v) for v in rng.permutation(p)]
    prob = 2.5 / (p - 1)
    weights = {}
    for a, b in itertools.combinations(range(p), 2):
        if rng.random() < prob:
            u, v = order[a], order[b]
            g.add(u, v)
            weights[(u, v)] = float(rng.choice([-1, 1]) * rng.uniform(.3, .7))
    for k in range(ell):
        i, j = rng.choice(p, 2, replace=False)
        for c in (int(i), int(j)):
            g.add(2 * p + k, c)
            weights[(2 * p + k, c)] = float(rng.choice([-1, 1]) * rng.uniform(.3, .7))
    plan = {}
    for i in (int(v) for v in rng.choice(p, int(round(.6 * p)), replace=False)):
        kind = {"mcar": "mcar", "add": "add"}.get(mech) or str(rng.choice(["add", "int", "even", "mcar"]))
        if kind == "mcar":
            plan[i] = dict(kind=kind, pa=[], b=0.0, s=[])
            continue
        cand = [v for v in range(p) if not (no_self and v == i)]
        k = 2 if kind == "int" else (1 if kind == "even" else int(rng.integers(1, 3)))
        pa = [int(v) for v in rng.choice(cand, k, replace=False)]
        if latent and ell and rng.random() < .2:
            pa[0] = 2 * p + int(rng.integers(ell))
        for v in pa:
            g.add(v, g.R(i))
        plan[i] = dict(kind=kind, pa=pa, b=float(rng.uniform(.5, 1.5)), s=[float(rng.choice([-1, 1])) for _ in pa])
    return g, weights, plan, order, ell


def sample(g, weights, plan, order, ell, n, rho, rng):
    p = g.p
    N = 2 * p + ell
    V = {}
    for k in range(ell):
        V[2 * p + k] = rng.standard_normal(n)
    for v in order:
        x = rng.standard_normal(n)
        for u in O.bits(g.pa[v]):
            x = x + weights[(u, v)] * V[u]
        V[v] = (x - x.mean()) / x.std()
    X = np.column_stack([V[i] for i in range(p)])
    R = np.ones((n, p), dtype=bool)
    for i, d in plan.items():
        if d["kind"] == "mcar":
            f = np.zeros(n)
        elif d["kind"] == "add":
            f = d["b"] * sum(s * V[u] for s, u in zip(d["s"], d["pa"])) / len(d["pa"])
        elif d["kind"] == "int":
            f = d["b"] * V[d["pa"][0]] * V[d["pa"][1]]
        else:
            f = d["b"] * (V[d["pa"][0]] ** 2 - 1)
        lo, hi = -12.0, 12.0
        for _ in range(30):
            a = (lo + hi) / 2
            if np.mean(1 / (1 + np.exp(-(a + f)))) < 1 - rho:
                lo = a
            else:
                hi = a
        R[:, i] = rng.random(n) < 1 / (1 + np.exp(-(a + f)))
    return X, R


# ---------------------------------------------------------------- tests
class Tests:
    """All tests on one data set, cached across methods."""

    def __init__(self, X, R):
        self.X, self.R = X, R
        self.n, self.p = X.shape
        self.cache = {}
        self.rows_cache = {}
        self.Ri = R.astype(float)

    def rows(self, U):
        r = self.rows_cache.get(U)
        if r is None:
            if U == 0:
                r = np.arange(self.n)
            else:
                r = np.flatnonzero(self.R[:, bits_of(U)].all(1))
            if len(self.rows_cache) > 30000:
                self.rows_cache.clear()
            self.rows_cache[U] = r
        return r

    def fz(self, x, y, W, U):
        """p-value of x,y|W on rows complete on U. x,y,W index O."""
        if x > y:
            x, y = y, x
        key = (x, y, W, U)
        v = self.cache.get(key)
        if v is not None:
            return v
        rows = self.rows(U)
        cols = [x, y] + bits_of(W)
        m = len(rows)
        if m < len(cols) + 8:
            v = 1.0
        else:
            D = self.X[np.ix_(rows, cols)]
            D = D - D.mean(0)
            C = D.T @ D
            try:
                P = np.linalg.inv(C)
                r = -P[0, 1] / math.sqrt(P[0, 0] * P[1, 1])
                r = max(min(r, .9999999), -.9999999)
                v = math.erfc(abs(math.atanh(r)) * math.sqrt(m - len(cols) - 1) / math.sqrt(2))
            except (np.linalg.LinAlgError, ValueError):
                v = 1.0
        self.cache[key] = v
        return v

    def indicator_p(self, x, y, W, U, T, flexible):
        """For each j in T: p-value of R_j against x given y,W, and against y given x,W, on rows complete on U."""
        key = ("I", min(x, y), max(x, y), W, U, tuple(T), flexible)
        v = self.cache.get(key)
        if v is not None:
            return (v[0], v[1]) if x < y else (v[1], v[0])
        rows = self.rows(U)
        m = len(rows)
        wl = bits_of(W)
        a, b = min(x, y), max(x, y)
        Xa, Xb = self.X[rows, a], self.X[rows, b]
        XW = self.X[np.ix_(rows, wl)] if wl else np.empty((m, 0))
        RR = self.Ri[np.ix_(rows, T)]
        pa = self._score(RR, Xa, Xb, XW, flexible, m)
        pb = self._score(RR, Xb, Xa, XW, flexible, m)
        self.cache[key] = (pa, pb)
        return (pa, pb) if x < y else (pb, pa)

    @staticmethod
    def _score(RR, target, other, XW, flexible, m):
        """Score test of the terms in target for R, given other and W, linear probability model."""
        one = np.ones(m)
        if flexible:
            Z = np.column_stack([one, other, other ** 2, XW, XW ** 2])
            Qt = np.column_stack([target, target ** 2, target * other] + [target * XW[:, k] for k in range(XW.shape[1])])
        else:
            Z = np.column_stack([one, other, XW])
            Qt = target[:, None]
        if m < Z.shape[1] + Qt.shape[1] + 8:
            return np.ones(RR.shape[1])
        Qz, _ = np.linalg.qr(Z)
        Rres = RR - Qz @ (Qz.T @ RR)
        Tres = Qt - Qz @ (Qz.T @ Qt)
        Qq, _ = np.linalg.qr(Tres)
        expl = ((Qq.T @ Rres) ** 2).sum(0)
        tot = (Rres ** 2).sum(0)
        with np.errstate(divide="ignore", invalid="ignore"):
            stat = np.where(tot > 1e-12, m * expl / tot, 0.0)
        return chi2.sf(stat, Qt.shape[1])


def chain_decide(T_candidates, step, nonconstant, U0):
    """Indicator chain. step(U, T) gives boolean arrays (x side rejects, y side rejects). Returns True if separated. T_candidates are indices in O outside U0."""
    U = U0
    T = [j for j in T_candidates if nonconstant(U, j)]
    while T:
        rx, ry = step(U, T)
        if np.any(rx & ry):
            return False
        if not rx.any() or not ry.any():
            return True
        idx = int(np.flatnonzero(rx)[0])
        U |= 1 << T[idx]
        T = [j for j in T if j != T[idx] and nonconstant(U, j)]
    return True


def lift_rule(ts, x, y, W, U0, flexible):
    full = (1 << ts.p) - 1
    cand = bits_of(full & ~U0)

    def nonconstant(U, j):
        return not ts.R[ts.rows(U), j].all()

    def step(U, T):
        pa, pb = ts.indicator_p(x, y, W, U, T, flexible)
        ab = ALPHA / len(T)
        return pa < ab, pb < ab

    return chain_decide(cand, step, nonconstant, U0)


# ---------------------------------------------------------------- FCI, PC-stable skeleton then the orientation of T4_oracle_checks.py
def skeleton(nodes, decide, forbid=()):
    P = O.Pag(nodes)
    for a, b in itertools.combinations(nodes, 2):
        P.edge(a, b)
    forbid = {frozenset(pr) for pr in forbid}
    for pr in forbid:
        a, b = tuple(pr)
        P.un(a, b)
        P.sep[(a, b)] = P.sep[(b, a)] = None
    for k in range(MAXORD + 1):
        adj0 = {v: set(P.adj[v]) for v in nodes}
        any_tested = False
        for a, b in itertools.combinations(nodes, 2):
            if b not in P.adj[a]:
                continue
            done = False
            for src, dst in ((a, b), (b, a)):
                others = sorted(adj0[src] - {dst})
                if len(others) < k:
                    continue
                any_tested = True
                for W in itertools.combinations(others, k):
                    if decide(a, b, W):
                        P.un(a, b)
                        P.sep[(a, b)] = P.sep[(b, a)] = set(W)
                        done = True
                        break
                if done:
                    break
        if not any_tested:
            break
    return P


def orient(P, r0_ok=None, rules=True, arrow_into=None):
    vars_ = P.vars
    if arrow_into is not None:
        for b in vars_:
            if arrow_into(b):
                for a in P.adj[b]:
                    P.m[(a, b)] = ">"
    for z in vars_:
        for x, y in itertools.combinations(sorted(P.adj[z]), 2):
            if y not in P.adj[x] and P.sep[(x, y)] is not None and z not in P.sep[(x, y)]:
                if r0_ok is None or r0_ok(x, y, z, P.sep[(x, y)]):
                    P.m[(x, z)] = ">"
                    P.m[(y, z)] = ">"
    if not rules:
        return P
    changed = True
    while changed:
        changed = False
        for b in vars_:
            for a in P.adj[b]:
                if P.m[(a, b)] != ">":
                    continue
                for c in P.adj[b]:
                    if c == a or c in P.adj[a]:
                        continue
                    if P.m[(c, b)] == "o":
                        P.m[(c, b)] = "-"
                        P.m[(b, c)] = ">"
                        changed = True
        for a in vars_:
            for c in P.adj[a]:
                if P.m[(a, c)] != "o":
                    continue
                for b in P.adj[a] & P.adj[c]:
                    ab_dir = P.m[(a, b)] == ">" and P.m[(b, a)] == "-"
                    bc_dir = P.m[(b, c)] == ">" and P.m[(c, b)] == "-"
                    if (ab_dir and P.m[(b, c)] == ">") or (P.m[(a, b)] == ">" and bc_dir):
                        P.m[(a, c)] = ">"
                        changed = True
                        break
        for b in vars_:
            nb = sorted(P.adj[b])
            for a, c in itertools.combinations(nb, 2):
                if c in P.adj[a] or P.m[(a, b)] != ">" or P.m[(c, b)] != ">":
                    continue
                for d in P.adj[b]:
                    if d in (a, c) or P.m[(d, b)] != "o":
                        continue
                    if d in P.adj[a] and d in P.adj[c] and P.m[(a, d)] == "o" and P.m[(c, d)] == "o":
                        P.m[(d, b)] = ">"
                        changed = True
        for b in vars_:
            for c in P.adj[b]:
                if P.m[(c, b)] != "o":
                    continue
                for a in P.adj[b] & P.adj[c]:
                    if not (P.m[(b, a)] == ">" and P.m[(a, c)] == ">" and P.m[(c, a)] == "-"):
                        continue
                    stack = [(a, [b, a])]
                    fired = False
                    while stack and not fired:
                        cur, path = stack.pop()
                        for u in P.adj[cur]:
                            if u in path or u == c or P.m[(u, cur)] != ">":
                                continue
                            if u not in P.adj[c]:
                                if P.sep.get((u, c)) is not None:
                                    if b in P.sep[(u, c)]:
                                        P.m[(c, b)] = "-"
                                        P.m[(b, c)] = ">"
                                    else:
                                        P.m[(a, b)] = ">"
                                        P.m[(b, a)] = ">"
                                        P.m[(c, b)] = ">"
                                        P.m[(b, c)] = ">"
                                    changed = True
                                    fired = True
                                    break
                            elif P.m[(cur, u)] == ">" and P.m[(u, c)] == ">" and P.m[(c, u)] == "-":
                                stack.append((u, path + [u]))
                    if fired:
                        break
    return P


def score_kinds(g, ne, na, a):
    out = dict(NE_t=0, NE_f=0, NA_t=0, NA_f=0, A_t=0, A_f=0)
    for x, y in ne:
        out["NE_f" if g.obs_edge(x, y) else "NE_t"] += 1
    for z, x in na:
        out["NA_f" if g.in_an(z, 1 << x) else "NA_t"] += 1
    for z, y in a:
        out["A_t" if g.in_an(z, 1 << y) else "A_f"] += 1
    return out


def result(g, P, p):
    ne, na, a = O.claims(P)
    keep = lambda s: {c for c in s if c[0] < p and c[1] < p}
    return score_kinds(g, keep(ne), keep(na), O.closure(keep(a), list(range(p))))


# ---------------------------------------------------------------- methods
def m(W):
    return sum(1 << v for v in W)


def run_all(g, ts, include_fcir=True):
    p = g.p
    Ov = list(range(p))
    full = (1 << p) - 1
    res, secs = {}, {}

    def timed(name, fn):
        t0 = time.time()
        res[name] = fn()
        secs[name] = time.time() - t0

    def d_lw(x, y, W):
        return ts.fz(x, y, m(W), full) >= ALPHA

    def d_naive(x, y, W):
        return ts.fz(x, y, m(W), (1 << x) | (1 << y) | m(W)) >= ALPHA

    def d_m1(x, y, W):
        return d_naive(x, y, W) and d_lw(x, y, W)

    def d_lift(flex):
        def f(x, y, W):
            if not d_naive(x, y, W):
                return False
            return lift_rule(ts, x, y, m(W), (1 << x) | (1 << y) | m(W), flex)
        return f

    timed("LW", lambda: result(g, orient(skeleton(Ov, d_lw)), p))
    timed("Naive", lambda: result(g, orient(skeleton(Ov, d_naive)), p))
    timed("M1", lambda: result(g, orient(skeleton(Ov, d_m1)), p))
    timed("LiftG1", lambda: result(g, orient(skeleton(Ov, d_lift(False))), p))
    timed("LiftG2", lambda: result(g, orient(skeleton(Ov, d_lift(True))), p))

    def pp_ok(x, y, z, W):
        return ts.fz(x, y, m(W), (1 << x) | (1 << y) | (1 << z) | m(W)) >= ALPHA

    def ppl_ok(flex):
        def f(x, y, z, W):
            U = (1 << x) | (1 << y) | m(W)
            if ts.R[ts.rows(U), z].all():
                return True
            pa, pb = ts.indicator_p(x, y, m(W), U, [z], flex)
            return not (pa[0] < ALPHA and pb[0] < ALPHA)
        return f

    timed("PP", lambda: result(g, orient(skeleton(Ov, d_naive), r0_ok=pp_ok, rules=False), p))
    timed("PPL2", lambda: result(g, orient(skeleton(Ov, d_naive), r0_ok=ppl_ok(True), rules=False), p))

    def flag_method():
        P = skeleton(Ov, d_naive)
        nbr = {i: set() for i in range(p)}   # variable j -> indicators adjacent to it
        for i in range(p):
            if ts.R[:, i].all():
                continue
            for j in range(p):
                if j == i:
                    continue
                U = 1 << j
                sep = False
                others = sorted(P.adj[j] - {i})
                for k in range(3):
                    for S in itertools.combinations(others, k):
                        Um = U | m(S)
                        pa, _ = ts.indicator_p(j, S[0] if S else j, m(S[1:]) if S else 0, Um, [i], False) if S else (None, None)
                        if S:
                            pv = pa[0]
                        else:
                            r = ts.rows(U)
                            Ri = ts.Ri[r, i]
                            if Ri.std() < 1e-9:
                                pv = 1.0
                            else:
                                c = float(np.corrcoef(ts.X[r, j], Ri)[0, 1])
                                pv = math.erfc(abs(math.atanh(min(max(c, -.999999), .999999))) * math.sqrt(len(r) - 3) / math.sqrt(2))
                        if pv >= ALPHA:
                            sep = True
                            break
                    if sep:
                        break
                if not sep:
                    nbr[j].add(i)

        def flagged(a, b):
            if nbr[a] & nbr[b]:
                return True
            return any(nbr[c] for c in P.adj[a] & P.adj[b])

        def ok(x, y, z, W):
            return not (flagged(x, z) or flagged(y, z))

        return result(g, orient(P, r0_ok=ok), p)

    timed("Flag", flag_method)

    def mi_method():
        Xm = ts.X.copy()
        Xm[~ts.R] = np.nan
        rng = np.random.default_rng(int(abs(Xm[~np.isnan(Xm)][:3].sum()) * 1e6) % (2 ** 32))
        Cs = []
        miss = [i for i in range(p) if not ts.R[:, i].all()]
        means = np.nanmean(Xm, axis=0)
        for _ in range(5):
            D = np.where(np.isnan(Xm), means, Xm)
            for _c in range(5):
                for i in miss:
                    ob = ts.R[:, i]
                    A = np.column_stack([np.ones(ts.n), np.delete(D, i, 1)])
                    XtX = A[ob].T @ A[ob]
                    L = np.linalg.cholesky(XtX + 1e-8 * np.eye(A.shape[1]))
                    beta = np.linalg.solve(L.T, np.linalg.solve(L, A[ob].T @ D[ob, i]))
                    res_ = D[ob, i] - A[ob] @ beta
                    s2 = float(res_ @ res_) / max(ob.sum() - A.shape[1], 1)
                    bd = beta + math.sqrt(s2) * np.linalg.solve(L.T, rng.standard_normal(A.shape[1]))
                    D[~ob, i] = A[~ob] @ bd + rng.normal(0, math.sqrt(s2), int((~ob).sum()))
            Cs.append(np.corrcoef(D.T))
        cache = {}

        def d(x, y, W):
            key = (min(x, y), max(x, y), W)
            v = cache.get(key)
            if v is None:
                cols = [x, y] + list(W)
                zs = []
                for C in Cs:
                    P_ = np.linalg.inv(C[np.ix_(cols, cols)])
                    r = -P_[0, 1] / math.sqrt(P_[0, 0] * P_[1, 1])
                    zs.append(math.atanh(max(min(r, .9999999), -.9999999)))
                zs = np.array(zs)
                U_ = 1 / (ts.n - len(W) - 3)
                T_ = U_ + (1 + 1 / len(zs)) * zs.var(ddof=1)
                v = math.erfc(abs(zs.mean()) / math.sqrt(T_) / math.sqrt(2))
                cache[key] = v
            return v >= ALPHA

        return result(g, orient(skeleton(Ov, d)), p)

    timed("MI", mi_method)

    if include_fcir:
        def fcir_method():
            nodes = list(range(2 * p))

            def d(a, b, W):
                inv = set(W) | {a, b}
                obs = {v for v in inv if v < p}
                rs = sorted(v for v in inv if v >= p)
                if any(r - p in obs for r in rs):
                    return False
                rows = ts.rows(m(obs))
                if len(rows) < len(inv) + 8:
                    return True
                cols = []
                for v in (a, b, *W):
                    cols.append(ts.X[rows, v] if v < p else ts.Ri[rows, v - p])
                D = np.column_stack(cols)
                sd = D.std(0)
                if (sd < 1e-9).any():
                    return True
                D = D - D.mean(0)
                try:
                    P_ = np.linalg.inv(D.T @ D)
                except np.linalg.LinAlgError:
                    return True
                r = -P_[0, 1] / math.sqrt(P_[0, 0] * P_[1, 1])
                r = max(min(r, .9999999), -.9999999)
                return math.erfc(abs(math.atanh(r)) * math.sqrt(len(rows) - len(inv) - 1) / math.sqrt(2)) >= ALPHA

            P = skeleton(nodes, d, forbid=[(i, p + i) for i in range(p)])
            return result(g, orient(P, arrow_into=lambda v: v >= p), p)

        timed("FCI-R", fcir_method)
    return res, secs


def run_mvpc(g, X, R):
    from causallearn.search.ConstraintBased.PC import pc
    p = g.p
    D = X.copy()
    D[~R] = np.nan
    cg = pc(D, ALPHA, "mv_fisherz", True, 0, -1, mvpc=True, show_progress=False, verbose=False)
    G = cg.G.graph
    P = O.Pag(list(range(p)))
    ne = set()
    a_ = set()
    for i, j in itertools.combinations(range(p), 2):
        if G[i, j] == 0 and G[j, i] == 0:
            ne.add((i, j))
            continue
        P.edge(i, j)
        # causal-learn: G[i,j] = -1 and G[j,i] = 1 means i -> j
        if G[i, j] == -1 and G[j, i] == 1:
            P.m[(i, j)], P.m[(j, i)] = ">", "-"
            a_.add((i, j))
        elif G[j, i] == -1 and G[i, j] == 1:
            P.m[(j, i)], P.m[(i, j)] = ">", "-"
            a_.add((j, i))
    for i, j in ne:
        P.sep[(i, j)] = P.sep[(j, i)] = set()
    _, na, _ = O.claims(P)
    return score_kinds(g, ne, na, O.closure(a_, list(range(p))))


# ---------------------------------------------------------------- checks
def checks():
    print("=== V: oracle checks ===", flush=True)
    rng = np.random.default_rng(SEED + 1)
    # V1: chain equals listwise separation on every query
    st = dict(queries=0, mismatch=0, steps_gt1=0)
    for _ in range(100 if QUICK else 1500):
        p = int(rng.choice([4, 5, 6]))
        g = O.random_mdag(p, rng.choice([.3, .5]), rng.choice([.1, .3, .6]), .4, .4, rng, .2)
        full = (1 << p) - 1
        for x, y in itertools.combinations(range(p), 2):
            pair = (1 << x) | (1 << y)
            for W in O.subsets(full & ~pair):
                U0 = pair | W
                if not g.sep(x, y, W, U0):
                    continue
                count = [0]

                def step(U, T):
                    count[0] += 1
                    C = W | g.rmask(U)
                    rx = np.array([not g.dsep_raw(x, g.R(j), C | (1 << y)) for j in T])
                    ry = np.array([not g.dsep_raw(y, g.R(j), C | (1 << x)) for j in T])
                    return rx, ry

                dec = chain_decide(O.bits(full & ~U0), step, lambda U, j: True, U0)
                st["queries"] += 1
                st["steps_gt1"] += count[0] > 1
                st["mismatch"] += dec != g.sep(x, y, W, full)
    print("V1 chain versus listwise separation:", st, flush=True)
    v1 = st["mismatch"] == 0 and st["queries"] > 0

    # V2: oracle runs of the pilot FCI on small graphs. M1 and LiftG equal LW; PP has no false claim; report no-PDS effect.
    st2 = dict(graphs=0, lift_differs_from_lw=0, lw_false=0, pp_false=0, naive_false=0, flag_false=0)
    for _ in range(50 if QUICK else 400):
        p = int(rng.choice([5, 6]))
        g = O.random_mdag(p, rng.choice([.3, .5]), rng.choice([.1, .3]), .5, .3, rng)
        Ov = list(range(p))
        full = (1 << p) - 1

        def lw(x, y, W):
            return g.sep(x, y, m(W), full)

        def nv(x, y, W):
            return g.sep(x, y, m(W), (1 << x) | (1 << y) | m(W))

        def lf(x, y, W):
            if not nv(x, y, W):
                return False
            U0 = (1 << x) | (1 << y) | m(W)

            def step(U, T):
                C = m(W) | g.rmask(U)
                rx = np.array([not g.dsep_raw(x, g.R(j), C | (1 << y)) for j in T])
                ry = np.array([not g.dsep_raw(y, g.R(j), C | (1 << x)) for j in T])
                return rx, ry

            return chain_decide(O.bits(full & ~U0), step, lambda U, j: True, U0)

        A = result(g, orient(skeleton(Ov, lw)), p)
        B = result(g, orient(skeleton(Ov, lf)), p)
        N = result(g, orient(skeleton(Ov, nv)), p)
        ok = lambda x, y, z, W: g.sep(x, y, m(W), (1 << x) | (1 << y) | (1 << z) | m(W))
        P_ = result(g, orient(skeleton(Ov, nv), r0_ok=ok, rules=False), p)
        st2["graphs"] += 1
        st2["lift_differs_from_lw"] += A != B
        st2["lw_false"] += (A["NA_f"] + A["A_f"] + A["NE_f"]) > 0
        st2["pp_false"] += (P_["NA_f"] + P_["A_f"] + P_["NE_f"]) > 0
        st2["naive_false"] += (N["NA_f"] + N["A_f"] + N["NE_f"]) > 0
    print("V2 oracle FCI with order at most 3:", st2, flush=True)
    v2 = st2["lift_differs_from_lw"] == 0 and st2["graphs"] > 0
    # V3: score test in the linear probability model against logistic score test, one query, on the families of T4_lift_checks.py
    sys.argv_backup = sys.argv
    import T4_lift_checks as L
    rng3 = np.random.default_rng(SEED + 3)
    agree = {}
    for fam in "ABD":
        same = tot = 0
        for _ in range(40 if QUICK else 300):
            x, y, z, Rx, Ry, Rz, Rex = L.simulate(fam, 2000, 1.0, 0.0, rng3)
            r = Rx & Ry
            xr, yr = x[r], y[r]
            one = np.ones(xr.size)
            R1 = Rz[r].astype(float)
            log_cert = L.score_p(R1, np.c_[one, yr], xr[:, None]) >= ALPHA or L.score_p(R1, np.c_[one, xr], yr[:, None]) >= ALPHA
            pa = Tests._score(R1[:, None], xr, yr, np.empty((xr.size, 0)), False, xr.size)[0]
            pb = Tests._score(R1[:, None], yr, xr, np.empty((xr.size, 0)), False, xr.size)[0]
            lp_cert = pa >= ALPHA or pb >= ALPHA
            same += log_cert == lp_cert
            tot += 1
        agree[fam] = same / tot
    print("V3 agreement of certificates, linear probability against logistic:", agree, flush=True)
    return dict(V1=st, V2=st2, V3=agree, pass_V1=v1, pass_V2=v2)


# ---------------------------------------------------------------- main
def main():
    res = checks()
    (HERE / ("T4L_pilot_checks_quick.json" if QUICK else "T4L_pilot_checks.json")).write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("oracle checks pass:", res["pass_V1"], res["pass_V2"], flush=True)
    if CHECK_ONLY or not (res["pass_V1"] and res["pass_V2"]):
        return
    done = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add(tuple(r["cell"]) + (r["i"],))
    print("already done:", len(done), flush=True)
    ps = (10, 20)
    N = {10: 2 if QUICK else 30, 20: 1 if QUICK else 12}
    t00 = time.time()
    with OUT.open("a", encoding="utf-8") as fh:
        # p = 10 first so that a stopped run still has a complete smaller set; mixed before the others in each p
        for p, mech, rho, n in itertools.product(ps, ("mixed", "add", "mcar"), (.1, .25), (1000, 4000)):
            cell = (p, mech, rho, n)
            for i in range(N[p]):
                if cell + (i,) in done:
                    continue
                t0 = time.time()
                ss = np.random.SeedSequence([SEED, p, {"mixed": 0, "add": 1, "mcar": 2}[mech], int(rho * 100), n, i])
                rng = np.random.default_rng(ss)
                g, w, plan, order, ell = make_graph(p, rng, mech=mech, rho=rho)
                X, R = sample(g, w, plan, order, ell, n, rho, rng)
                ts = Tests(X, R)
                out, secs = run_all(g, ts, include_fcir=p == 10)
                rec = dict(cell=list(cell), i=i, stratum="main", listwise_rows=int(R.all(1).sum()), methods=out, secs={k: round(v, 2) for k, v in secs.items()})
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                del ts, X, R
                print(f"{cell} i={i} lw_rows={rec['listwise_rows']} {time.time() - t0:.1f}s (total {time.time() - t00:.0f}s)", flush=True)
        # MVPC stratum: no latents, no self-parent
        for mech, rho, n in itertools.product(("mixed", "add"), (.1, .25), (1000, 4000)):
            cell = ("mvpc", 10, mech, rho, n)
            for i in range(2 if QUICK else 20):
                if cell + (i,) in done:
                    continue
                t0 = time.time()
                ss = np.random.SeedSequence([SEED + 7, {"mixed": 0, "add": 1}[mech], int(rho * 100), n, i])
                rng = np.random.default_rng(ss)
                g, w, plan, order, ell = make_graph(10, rng, latent=False, no_self=True, mech=mech, rho=rho)
                X, R = sample(g, w, plan, order, ell, n, rho, rng)
                ts = Tests(X, R)
                out, secs = run_all(g, ts, include_fcir=False)
                try:
                    t1 = time.time()
                    out["MVPC"] = run_mvpc(g, X, R)
                    secs["MVPC"] = time.time() - t1
                except Exception as e:  # recorded, not hidden
                    out["MVPC"] = None
                    secs["MVPC_error"] = 0.0
                    print("MVPC failed:", repr(e)[:160], flush=True)
                rec = dict(cell=list(cell), i=i, stratum="mvpc", listwise_rows=int(R.all(1).sum()), methods=out, secs={k: round(v, 2) for k, v in secs.items()})
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                print(f"{cell} i={i} {time.time() - t0:.1f}s (total {time.time() - t00:.0f}s)", flush=True)
    print("finished", time.time() - t00, flush=True)


if __name__ == "__main__":
    main()
