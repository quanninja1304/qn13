"""Post hoc diagnostics for the T4-L pilot. Written AFTER the K8 verdict (NO-GO) was known. Does not change that verdict. Explanatory only, no reading rule.

Question: why did LiftG2 not reduce false claims, when it did in the one-triple simulation?
D1 floor: how many false orientation claims remain with no missing data at all (Complete)? False claims of a method that Complete does not make are called attributable to missingness.
D2 dose: same with the additive mechanism at three times the effect size.
D3 query level, against the oracle target: among queries not rejected on test-wise rows, how often does each confirmation rule agree with the true separation in the listwise regime?
   If Lift matches the target better than M1 but gives no better claims, the listwise target itself is what does not help.
Cells: p = 10, rho = .25, mech in {mixed, add, add3}, n in {1000, 4000, 20000}, 30 graphs each. New seeds.

Run: python -P -E T4L_pilot_diagnostics.py [--quick]
"""
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
QUICK = "--quick" in sys.argv
import T4L_algorithm_pilot as Q  # noqa: E402
import T4_oracle_checks as O  # noqa: E402

SEED = 20261113
ALPHA = .05
OUT = HERE / "T4L_pilot_diagnostics.json"


def claim_sets(g, P, p):
    ne, na, a = O.claims(P)
    keep = lambda s: {c for c in s if c[0] < p and c[1] < p}
    ne, na, a = keep(ne), keep(na), O.closure(keep(a), list(range(p)))
    false = {("NA",) + c for c in na if g.in_an(c[0], 1 << c[1])} | {("A",) + c for c in a if not g.in_an(c[0], 1 << c[1])}
    true = {("NA",) + c for c in na if not g.in_an(c[0], 1 << c[1])} | {("A",) + c for c in a if g.in_an(c[0], 1 << c[1])}
    return false, true, len(ne), sum(g.obs_edge(*c) for c in ne)


def m(W):
    return sum(1 << v for v in W)


def main():
    cells = list(itertools.product(("mixed", "add", "add3"), (1000, 4000, 20000)))
    N = 2 if QUICK else 30
    rows = []
    # resume: a first run was stopped for low memory after 4 of 9 cells; seeds depend only on the cell, so finished cells are kept and not recomputed
    if OUT.exists() and not QUICK:
        rows = json.loads(OUT.read_text(encoding="utf-8"))["rows"]
    done = {(r["mech"], r["n"]) for r in rows}
    print("cells already done:", sorted(done), flush=True)
    t00 = time.time()
    for mech, n in cells:
        if (mech, n) in done:
            continue
        agg = {}
        conf = {k: dict(sep_when_target_sep=0, sep_when_target_dep=0, dep_when_target_sep=0, dep_when_target_dep=0) for k in ("M1", "LiftG1", "LiftG2")}
        t0 = time.time()
        lw_rows = []
        for i in range(N):
            rng = np.random.default_rng(np.random.SeedSequence([SEED, {"mixed": 0, "add": 1, "add3": 2}[mech], n, i]))
            p = 10
            g, w, plan, order, ell = Q.make_graph(p, rng, mech="add" if mech == "add3" else mech, rho=.25)
            if mech == "add3":
                for d in plan.values():
                    d["b"] *= 3
            X, R = Q.sample(g, w, plan, order, ell, n, .25, rng)
            lw_rows.append(int(R.all(1).sum()))
            ts = Q.Tests(X, R)
            tc = Q.Tests(X, np.ones_like(R))
            Ov = list(range(p))
            full = (1 << p) - 1
            queries = []

            def d_c(x, y, W):
                return tc.fz(x, y, m(W), 0) >= ALPHA

            def d_n(x, y, W):
                s = ts.fz(x, y, m(W), (1 << x) | (1 << y) | m(W)) >= ALPHA
                if s:
                    queries.append((x, y, W))
                return s

            def d_lw(x, y, W):
                return ts.fz(x, y, m(W), full) >= ALPHA

            def d_nq(x, y, W):
                return ts.fz(x, y, m(W), (1 << x) | (1 << y) | m(W)) >= ALPHA

            def d_m1(x, y, W):
                return d_nq(x, y, W) and d_lw(x, y, W)

            def d_l(flex):
                return lambda x, y, W: d_nq(x, y, W) and Q.lift_rule(ts, x, y, m(W), (1 << x) | (1 << y) | m(W), flex)

            sets = {}
            sets["Complete"] = claim_sets(g, Q.orient(Q.skeleton(Ov, d_c)), p)
            sets["Naive"] = claim_sets(g, Q.orient(Q.skeleton(Ov, d_n)), p)
            sets["LW"] = claim_sets(g, Q.orient(Q.skeleton(Ov, d_lw)), p)
            sets["M1"] = claim_sets(g, Q.orient(Q.skeleton(Ov, d_m1)), p)
            sets["LiftG1"] = claim_sets(g, Q.orient(Q.skeleton(Ov, d_l(False))), p)
            sets["LiftG2"] = claim_sets(g, Q.orient(Q.skeleton(Ov, d_l(True))), p)
            Fc = sets["Complete"][0]
            for k, (F, T, ne, nef) in sets.items():
                a = agg.setdefault(k, dict(false=0, true=0, attributable=0, ne=0, ne_false=0))
                a["false"] += len(F)
                a["true"] += len(T)
                a["attributable"] += len(F - Fc)
                a["ne"] += ne
                a["ne_false"] += nef
            for x, y, W in queries:
                Wm = m(W)
                target = g.sep(x, y, Wm, full)
                dec = {"M1": d_lw(x, y, W), "LiftG1": Q.lift_rule(ts, x, y, Wm, (1 << x) | (1 << y) | Wm, False), "LiftG2": Q.lift_rule(ts, x, y, Wm, (1 << x) | (1 << y) | Wm, True)}
                for k, s in dec.items():
                    conf[k][("sep" if s else "dep") + "_when_target_" + ("sep" if target else "dep")] += 1
            del ts, tc
        row = dict(mech=mech, n=n, graphs=N, listwise_rows=float(np.mean(lw_rows)), per_graph={k: {kk: vv / N for kk, vv in v.items()} for k, v in agg.items()}, confirm_confusion=conf, seconds=time.time() - t0)
        rows.append(row)
        print(f"{mech} n={n} rows={row['listwise_rows']:.0f}: " + " ".join(f"{k}={v['false']:.1f}/{v['true']:.1f}/attr {v['attributable']:.1f}" for k, v in row["per_graph"].items()) + f" | {row['seconds']:.0f}s", flush=True)
        for k, c in conf.items():
            ts_ = c["sep_when_target_sep"] + c["dep_when_target_sep"]
            td = c["sep_when_target_dep"] + c["dep_when_target_dep"]
            print(f"   {k}: target sep {ts_}, wrongly dep {c['dep_when_target_sep'] / max(ts_, 1):.3f} | target dep {td}, wrongly sep {c['sep_when_target_dep'] / max(td, 1):.3f}", flush=True)
        if not QUICK:
            OUT.write_text(json.dumps(dict(seed=SEED, rows=rows), indent=1), encoding="utf-8")
    print("finished", time.time() - t00)


if __name__ == "__main__":
    main()
