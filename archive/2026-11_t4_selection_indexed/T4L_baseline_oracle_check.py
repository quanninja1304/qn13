"""Oracle check of the simplest baseline for T4-L: FCI with the missingness indicators as ordinary variables (test-wise deletion on O and R).

Why. The audit found that MVPC Step 2 is "equivalent to performing TD-PC on V and R" (Tu et al. 2019). If FCI on O and R avoids the false claims of naive test-wise FCI over O,
T4-L has no reason to exist. Oracle only, no finite-sample claim. FCI here is the R0-R4 version from T4_oracle_checks.py.

Baseline variants:
  NaiveO   FCI on O, each query in the smallest regime.
  NaiveOR  FCI on O and R, each query in the smallest regime of its O variables. A query with R_i and O_i together is not testable, since R_i is constant on rows with O_i; it is treated
           as "no separation found". Same restriction as MVPC Step 2, which tests R_i and V_j given subsets excluding V_i. R_i and O_i are nonadjacent by assumption and give no orientation.
  NaiveOR+ NaiveOR with the known fact that indicators have no children: every edge into an indicator has an arrowhead at the indicator, set before orientation.
  LW       FCI at regime O (Strobl Algorithm 1 in the oracle), the sound comparator.
Claims are scored on pairs of O variables only, with the same claim extraction as T4_oracle_checks.py.

READING RULE, FIXED BEFORE THE FIRST RUN (project-management choice):
  T4-L is subsumed if NaiveOR or NaiveOR+ has false claims on at most 10% as many graphs as NaiveO, and at least 90% of the true claims of NaiveO, summed over MNAR cells q in {.1, .3}.
  Otherwise the baseline does not subsume it in the oracle. A pass says nothing about finite samples.

CHANGE AFTER THE FIRST QUICK RUN (disclosed in the audit report). The first version treated the pair (R_i, O_i) as "no separation found". That forced a spurious edge R_i - O_i for every i, and
R0 then oriented false arrowheads from it: the q = 0 control showed false claims on 191 graphs, where none are possible from missingness. That version was unfair to the baseline, so its numbers
are not evidence. The reading rule is unchanged. Control now required: NaiveOR and NaiveOR+ must have no false claim at q = 0.

Run: python -P -E T4L_baseline_oracle_check.py [--quick]
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
SEED = 20261110


def m(W):
    return sum(1 << v for v in W)


def fci_or(g, background):
    """FCI on O and R. R_i is node p + i. R_i and O_i are nonadjacent by assumption, as in MVPC (no self-masking), and their pair gives no orientation."""
    p = g.p
    nodes = list(range(2 * p))

    def indep(a, b, W):
        involved = set(W) | {a, b}
        obs = {v for v in involved if v < p}
        for r in (v for v in involved if v >= p):
            if r - p in obs:
                return False  # R_i is constant on rows with O_i, so the query cannot be tested
        return g.dsep_raw(a, b, m(W) | g.rmask(m(obs)))

    forbid = [(i, p + i) for i in range(p)]
    return O.fci(nodes, indep, forbid=forbid, arrow_into=(lambda v: v >= p) if background else None)


def claims_on_O(P, p):
    ne, na, a = O.claims(P)
    return ({c for c in ne if c[0] < p and c[1] < p}, {c for c in na if c[0] < p and c[1] < p}, {c for c in a if c[0] < p and c[1] < p})


def main():
    rng = np.random.default_rng(SEED)
    keys = ("LW", "NaiveO", "NaiveOR", "NaiveOR+")
    rows = []
    for p, Ng in ((4, 40 if QUICK else 400), (5, 10 if QUICK else 100)):
        for dens, q, cr in itertools.product((.3, .5), (0.0, .1, .3), (0.0, .5)):
            tr = dict.fromkeys(keys, 0)
            bad = dict.fromkeys(keys, 0)
            t0 = time.time()
            for _ in range(Ng):
                g = O.random_mdag(p, dens, q, .5, cr, rng)
                Ov = list(range(p))
                full = (1 << p) - 1
                res = {}
                res["LW"] = O.claims(O.fci(Ov, lambda x, y, W, g=g: g.sep(x, y, m(W), full)))
                res["NaiveO"] = O.claims(O.fci(Ov, lambda x, y, W, g=g: g.sep(x, y, m(W), (1 << x) | (1 << y) | m(W))))
                res["NaiveOR"] = claims_on_O(fci_or(g, False), p)
                res["NaiveOR+"] = claims_on_O(fci_or(g, True), p)
                for k in keys:
                    ne, na, a = res[k]
                    t, f, _ = O.score(g, ne, na, O.closure(a, Ov))
                    tr[k] += t
                    bad[k] += f > 0
            rows.append({"p": p, "density": dens, "q": q, "Rc": cr, "graphs": Ng, "true_per_graph": {k: tr[k] / Ng for k in keys}, "graphs_false": bad})
            print(f"p={p} d={dens} q={q} Rc={cr} N={Ng}: true " + " ".join(f"{k}={tr[k] / Ng:.2f}" for k in keys) + f" | false graphs {bad} | {time.time() - t0:.0f}s", flush=True)
    mnar = [r for r in rows if r["q"] in (.1, .3)]
    tot = {k: {"false": sum(r["graphs_false"][k] for r in mnar), "true": sum(r["true_per_graph"][k] * r["graphs"] for r in mnar)} for k in keys}
    def subsumed(k):
        return tot[k]["false"] <= .1 * tot["NaiveO"]["false"] and tot[k]["true"] >= .9 * tot["NaiveO"]["true"]
    v = {k: subsumed(k) for k in ("NaiveOR", "NaiveOR+")}
    print("totals over MNAR cells:", tot, flush=True)
    print("subsumed by the declared rule:", v, flush=True)
    q0 = [r for r in rows if r["q"] == 0.0]
    print("control q=0, graphs with a false claim:", {k: sum(r["graphs_false"][k] for r in q0) for k in keys}, flush=True)
    if not QUICK:
        (HERE / "T4L_baseline_oracle_outputs.json").write_text(json.dumps({"seed": SEED, "rows": rows, "totals": tot, "subsumed": v}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
