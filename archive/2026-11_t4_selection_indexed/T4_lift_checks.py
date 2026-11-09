"""T4 follow-up: regime lifting by indicator tests. See T4_kill_test_vi.md.

Idea under test. Rows complete on U have x, y, W observed, and the indicators R_j for j outside U are observed on every row. So
    x indep R* | y, W  on rows complete on U      (R* = 1 when all variables in U' minus U are observed)
is testable on those rows. Together with x indep y | W on the same rows it gives x indep y | W on rows complete on U', by plain probability:
P(x | y,W,U,R*=1) = P(x | y,W,U) = P(x | W,U), and averaging over y gives P(x | W,U,R*=1) = P(x | W,U). No faithfulness and no Assumption 1 are needed for this direction.
Hypothesis: indicator tests have more power than a direct re-test on rows complete on U', because the selection-induced x-y dependence is of higher order in the
missingness effects than the x-R* dependence. This is a hypothesis, not a result.

PART L (oracle). L1 soundness: sep at U and joint lift certificate imply sep at U'. L2 one-step equivalence: for one indicator j, given sep at U,
    sep at U+j iff (R_j sep x | y,W at U) or (R_j sep y | x,W at U).   L3 coverage: how many listwise separations have a joint certificate from the smallest regime; how many
    need a chain.  Reading: L1 and L2 must have 0 violations.

PART K6R (oracle). Rerun the MNAR cells of p = 6 with 400 graphs and p = 7 with 100 graphs with bootstrap intervals. Reading: K6 stands only if PP/SepOnly >= 1.10 with
    the lower 95% bootstrap limit above 1.05 in at least one cell. New seeds, cells otherwise as in T4_oracle_checks.py.

PART P (finite sample, query level, linear Gaussian). Triple x, y, z. x, y MCAR 20%, z missing by R_z with logit a + f. Five extra variables MCAR 15% define the listwise rows.
    A: z -> x, y isolated, f = b(y + z). Declaring x *-> z <-* y is FALSE. This is the naive failure.
    B: x -> z <- y, f = b y. Claim TRUE, separation holds at rows xyz.
    C: x -> z <- y, f = b(x + y). Claim TRUE for the DAG, but x, y are dependent at rows xyz, so the regime target gives no orientation. Descriptive only.
    D: z -> x, y isolated, f = b y z. Claim FALSE. Adversarial for a main-effects indicator model.
    E: as D with f = b sin(3y) z. Claim FALSE. Descriptive only, not in any rule; added after the code-test run (40 reps, 2 n values), thresholds unchanged.
    Rules for declaring the v-structure, all alpha = .05, all need dep(x,z), dep(y,z) on rows complete on the pair, and:
      Naive     sep(x,y) on rows xy.
      PerProof  sep(x,y) on rows xy and on rows xyz (the per-proof recheck).
      M1global  sep(x,y) on rows xy and on listwise rows (Strobl Algorithm 1 applied to this query).
      Lift1     sep(x,y) on rows xy and on those rows R_z indep x | y or R_z indep y | x, logistic score test, main effects.
      Lift2     same, indicator model has squares and the x y product: tested terms (x, x^2, xy) given (y, y^2), and symmetric.
      LiftG     as Lift1 with R* = R_z and all extras observed (same target as M1global).
    READING RULES K7, FIXED BEFORE THE FIRST RUN (project-management choices):
      Positive if: in family A at least 3 cells have PerProof false rate >= .10 and Lift1 <= half of it, and in family B Lift1 true rate >= PerProof - .03 in every cell.
      No-go if: no cell in A has Lift1 <= .75 PerProof among cells with PerProof >= .05.   Otherwise weak.
      Fragile if: in family D Lift1 exceeds PerProof by more than .05 in any cell. Lift2 is then the candidate and must not exceed PerProof by more than .02 in any D cell, and must meet
      the Positive rule in A and B itself; otherwise the mechanism is reported as depending on a correct indicator model.

Run: python -P -E T4_lift_checks.py [--quick]
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import T4_oracle_checks as O  # noqa: E402

QUICK = "--quick" in sys.argv
SEED = 20261109
res = {"meta": {"quick": QUICK, "seed": SEED}}
fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if not cond:
        fails.append(name)


def save():
    if not QUICK:
        (HERE / "T4_lift_outputs.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")


# ------------------------------------------------------------------ Part L
def lift_joint(g, x, y, W, U, Ut):
    """x or y separated from all R_j (j in Ut minus U) given the other, W, R_U."""
    C = W | g.rmask(U)
    ext = list(O.bits(Ut & ~U))
    a = all(g.dsep_raw(x, g.R(j), C | (1 << y)) for j in ext)
    b = all(g.dsep_raw(y, g.R(j), C | (1 << x)) for j in ext)
    return a or b


def part_L():
    print("\n=== L: lift certificate, oracle ===", flush=True)
    rng = np.random.default_rng(SEED + 1)
    st = {"L1_n": 0, "L1_viol": 0, "L2_n": 0, "L2_viol": 0}
    rows = {}
    for gi in range(300 if QUICK else 4000):
        p = int(rng.choice([3, 4, 5]))
        q = float(rng.choice([.1, .3, .6]))
        g = O.random_mdag(p, rng.choice([.3, .5, .7]), q, .4, .4, rng, .2)
        full = (1 << p) - 1
        cell = rows.setdefault(q, {"lw_sep": 0, "joint_from_smallest": 0, "direct_needed": 0, "sep_small_dep_lw": 0, "false_cert": 0})
        for x, y in itertools.combinations(range(p), 2):
            pair = (1 << x) | (1 << y)
            for W in O.subsets(full & ~pair):
                U0 = pair | W
                for E in O.subsets(full & ~U0):
                    U = U0 | E
                    if not g.sep(x, y, W, U):
                        continue
                    for E2 in O.subsets(full & ~U):
                        if E2 == 0:
                            continue
                        Ut = U | E2
                        st["L1_n"] += 1
                        if lift_joint(g, x, y, W, U, Ut) and not g.sep(x, y, W, Ut):
                            st["L1_viol"] += 1
                        if bin(E2).count("1") == 1:
                            st["L2_n"] += 1
                            if lift_joint(g, x, y, W, U, Ut) != g.sep(x, y, W, Ut):
                                st["L2_viol"] += 1
                if U0 == full:
                    continue
                if g.sep(x, y, W, U0):
                    cert = lift_joint(g, x, y, W, U0, full)
                    if g.sep(x, y, W, full):
                        cell["lw_sep"] += 1
                        cell["joint_from_smallest"] += cert
                        cell["direct_needed"] += not cert
                    else:
                        cell["sep_small_dep_lw"] += 1
                        cell["false_cert"] += cert
    print(st, flush=True)
    for q, c in sorted(rows.items()):
        print(f"q={q}: {c}; coverage of listwise separations by one joint certificate {c['joint_from_smallest'] / max(c['lw_sep'], 1):.3f}", flush=True)
    check("L1 soundness", st["L1_viol"] == 0 and st["L1_n"] > 0, str(st))
    check("L2 one-step equivalence", st["L2_viol"] == 0 and st["L2_n"] > 0, str(st))
    check("L3 no false certificate", all(c["false_cert"] == 0 for c in rows.values()))
    res["L"] = {"stats": st, "coverage_by_q": {str(k): v for k, v in rows.items()}}
    save()


# ------------------------------------------------------------------ Part K6R
def part_K6R():
    print("\n=== K6R: PP vs SepOnly with more graphs ===", flush=True)
    rng = np.random.default_rng(SEED + 2)
    out = []
    plan = ((6, 15 if QUICK else 400), (7, 3 if QUICK else 100))
    for p, Ng in plan:
        for dens, q, cr in itertools.product((.3, .5), (.1, .3), (0.0, .5)):
            pp, so, lwu, t0 = [], [], [], time.time()
            fp = 0
            for _ in range(Ng):
                g = O.random_mdag(p, dens, q, .5, cr, rng)
                o, _info = O.run_methods(g)
                pp.append(o["PP"][0])
                so.append(o["SepOnly"][0])
                lwu.append(o["LWu"][0])
                fp += o["PP"][1] > 0
            pp, so, lwu = np.array(pp, float), np.array(so, float), np.array(lwu, float)
            idx = rng.integers(0, Ng, size=(2000, Ng))
            boot = pp[idx].mean(1) / np.maximum(so[idx].mean(1), 1e-9)
            r = {"p": p, "density": dens, "q": q, "Rc": cr, "graphs": Ng, "PP": pp.mean(), "SepOnly": so.mean(), "LWu": lwu.mean(), "ratio": pp.mean() / max(so.mean(), 1e-9),
                 "ci": [float(np.quantile(boot, .025)), float(np.quantile(boot, .975))], "frac_PP_gt_Sep": float((pp > so).mean()), "PP_false_graphs": fp, "sec": time.time() - t0}
            out.append(r)
            print(f"K6R p={p} d={dens} q={q} Rc={cr} N={Ng}: LWu={r['LWu']:.2f} Sep={r['SepOnly']:.2f} PP={r['PP']:.2f} ratio={r['ratio']:.3f} CI [{r['ci'][0]:.3f},{r['ci'][1]:.3f}] PP>Sep {r['frac_PP_gt_Sep']:.2f} false {fp} | {r['sec']:.0f}s", flush=True)
            res["K6R"] = {"rows": out, "partial": True}
            save()
    stand = [r for r in out if r["ratio"] >= 1.10 and r["ci"][0] > 1.05]
    verdict = "K6 stands" if stand else "K6 does not stand"
    print(f"K6R verdict: {verdict}; cells passing {len(stand)}/{len(out)}", flush=True)
    check("K6R PP has no false claim", all(r["PP_false_graphs"] == 0 for r in out))
    res["K6R"] = {"rows": out, "verdict": verdict, "cells_passing": len(stand)}
    save()


# ------------------------------------------------------------------ Part P
def pcorr_p(a, b):
    from scipy.stats import norm
    n = a.size
    if n < 5:
        return 1.0
    r = np.corrcoef(a, b)[0, 1]
    if not np.isfinite(r):
        return 1.0
    r = np.clip(r, -.999999, .999999)
    return float(2 * norm.sf(abs(np.arctanh(r)) * np.sqrt(n - 3)))


def score_p(R, Z, Q):
    """Logistic score test of Q given Z (Z includes the intercept)."""
    from scipy.stats import chi2
    n1 = R.sum()
    if n1 < 5 or n1 > R.size - 5:
        return 1.0
    b = np.zeros(Z.shape[1])
    b[0] = np.log(n1 / (R.size - n1))
    for _ in range(12):
        eta = np.clip(Z @ b, -25, 25)
        mu = 1 / (1 + np.exp(-eta))
        w = np.maximum(mu * (1 - mu), 1e-9)
        A = (Z * w[:, None]).T @ Z
        try:
            step = np.linalg.solve(A, Z.T @ (R - mu))
        except np.linalg.LinAlgError:
            return 1.0
        b = b + step
        if np.max(np.abs(step)) < 1e-6:
            break
    eta = np.clip(Z @ b, -25, 25)
    mu = 1 / (1 + np.exp(-eta))
    w = np.maximum(mu * (1 - mu), 1e-9)
    U = Q.T @ (R - mu)
    A = (Z * w[:, None]).T @ Z
    C = (Q * w[:, None]).T @ Z
    V = (Q * w[:, None]).T @ Q - C @ np.linalg.solve(A, C.T)
    try:
        s = float(U @ np.linalg.solve(V, U))
    except np.linalg.LinAlgError:
        return 1.0
    return float(chi2.sf(max(s, 0.0), Q.shape[1]))


def simulate(fam, n, b, a, rng, beta=.5, rho_xy=.2, rho_extra=.15, k=5):
    ex, ey, ez = rng.standard_normal((3, n))
    if fam in ("A", "D", "E"):
        z = ez
        y = ey
        x = beta * z + np.sqrt(1 - beta ** 2) * ex
    else:
        x, y = ex, ey
        z = beta * x + beta * y + np.sqrt(1 - 2 * beta ** 2) * ez
    f = {"A": b * (y + z), "B": b * y, "C": b * (x + y), "D": b * y * z, "E": b * np.sin(3 * y) * z}[fam]
    Rz = rng.random(n) < 1 / (1 + np.exp(-(a + f)))
    Rx, Ry = rng.random((2, n)) >= rho_xy
    Rex = (rng.random((k, n)) >= rho_extra).all(0)
    return x, y, z, Rx, Ry, Rz, Rex


def run_rep(fam, n, b, a, rng, alpha=.05):
    x, y, z, Rx, Ry, Rz, Rex = simulate(fam, n, b, a, rng)
    rxy = Rx & Ry
    rxz = Rx & Rz
    ryz = Ry & Rz
    rxyz = rxy & Rz
    rlw = rxyz & Rex
    dep = pcorr_p(x[rxz], z[rxz]) < alpha and pcorr_p(y[ryz], z[ryz]) < alpha
    sep0 = pcorr_p(x[rxy], y[rxy]) >= alpha
    out = dict.fromkeys(("Naive", "PerProof", "M1global", "Lift1", "Lift2", "LiftG"), False)
    if not (dep and sep0):
        return out, rlw.sum(), rxyz.sum(), rxy.sum()
    out["Naive"] = True
    out["PerProof"] = pcorr_p(x[rxyz], y[rxyz]) >= alpha
    out["M1global"] = pcorr_p(x[rlw], y[rlw]) >= alpha
    xr, yr = x[rxy], y[rxy]
    m = xr.size
    one = np.ones(m)
    R1 = Rz[rxy].astype(float)
    RG = (Rz & Rex)[rxy].astype(float)

    def lift(R):
        px = score_p(R, np.c_[one, yr], xr[:, None])
        if px >= alpha:
            return True
        return score_p(R, np.c_[one, xr], yr[:, None]) >= alpha

    out["Lift1"] = lift(R1)
    out["LiftG"] = lift(RG)
    px2 = score_p(R1, np.c_[one, yr, yr ** 2], np.c_[xr, xr ** 2, xr * yr])
    out["Lift2"] = px2 >= alpha or score_p(R1, np.c_[one, xr, xr ** 2], np.c_[yr, yr ** 2, xr * yr]) >= alpha
    return out, rlw.sum(), rxyz.sum(), rxy.sum()


def part_P():
    print("\n=== P: finite sample, query level ===", flush=True)
    rng = np.random.default_rng(SEED + 3)
    reps = 40 if QUICK else 400
    ns = (1000, 4000) if QUICK else (500, 1000, 2000, 5000)
    bs = (1.0,) if QUICK else (.5, 1.0, 1.5, 2.0)
    As = (0.0,) if QUICK else (0.0, -1.5)
    rows = []
    keys = ("Naive", "PerProof", "M1global", "Lift1", "Lift2", "LiftG")
    for fam, a, b, n in itertools.product("ABCDE", As, bs, ns):
        t0 = time.time()
        tot = dict.fromkeys(keys, 0)
        rl = rx = rp = 0
        for _ in range(reps):
            o, l, xz, xy = run_rep(fam, n, b, a, rng)
            for k in keys:
                tot[k] += o[k]
            rl += l
            rx += xz
            rp += xy
        rate = {k: tot[k] / reps for k in keys}
        rows.append({"fam": fam, "a": a, "b": b, "n": n, "reps": reps, "claim_rate": rate, "rows_listwise": rl / reps, "rows_xyz": rx / reps, "rows_xy": rp / reps})
        print(f"P {fam} a={a} b={b} n={n}: " + " ".join(f"{k}={rate[k]:.3f}" for k in keys) + f" | rows lw/xyz/xy {rl / reps:.0f}/{rx / reps:.0f}/{rp / reps:.0f} | {time.time() - t0:.0f}s", flush=True)
        res["P"] = {"rows": rows, "partial": True}
        save()

    def verdict(key):
        A = [r for r in rows if r["fam"] == "A"]
        B = [r for r in rows if r["fam"] == "B"]
        good = [r for r in A if r["claim_rate"]["PerProof"] >= .10 and r["claim_rate"][key] <= .5 * r["claim_rate"]["PerProof"]]
        any75 = [r for r in A if r["claim_rate"]["PerProof"] >= .05 and r["claim_rate"][key] <= .75 * r["claim_rate"]["PerProof"]]
        bok = all(r["claim_rate"][key] >= r["claim_rate"]["PerProof"] - .03 for r in B)
        v = "positive" if len(good) >= 3 and bok else ("no-go" if not any75 else "weak")
        return {"verdict": v, "cells_half": len(good), "cells_75": len(any75), "family_B_ok": bok, "cells_A_with_PerProof_ge_10": sum(r["claim_rate"]["PerProof"] >= .10 for r in A)}

    D = [r for r in rows if r["fam"] == "D"]
    frag1 = max((r["claim_rate"]["Lift1"] - r["claim_rate"]["PerProof"] for r in D), default=0)
    frag2 = max((r["claim_rate"]["Lift2"] - r["claim_rate"]["PerProof"] for r in D), default=0)
    v = {"Lift1": verdict("Lift1"), "Lift2": verdict("Lift2"), "LiftG_vs_rule_with_PerProof": verdict("LiftG"), "D_max_excess_Lift1": frag1, "D_max_excess_Lift2": frag2,
         "Lift1_fragile": frag1 > .05, "Lift2_within_tolerance": frag2 <= .02}
    print("K7:", v, flush=True)
    res["P"] = {"rows": rows, "K7": v}
    save()


if __name__ == "__main__":
    t0 = time.time()
    part_L()
    part_P()
    part_K6R()
    res["meta"].update({"runtime_sec": time.time() - t0, "failed": fails})
    save()
    print(f"runtime {time.time() - t0:.0f}s failed={fails}")
