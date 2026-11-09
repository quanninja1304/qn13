"""E6: why does precision fall with n on the chamber? Knock-out of each candidate cause on the real data.

Actuators stay as measured. Each sensor is rebuilt from its documented parents, then given its own residuals permuted across rows, which destroys any dependence between the residuals of different sensors:
  REAL         data as measured.
  NL_PERM      sensor = boosted fit of documented parents + permuted residual. Keeps nonlinearity and real noise shape; removes residual dependence between sensors.
  LIN_PERM     sensor = linear fit of documented parents + permuted residual. Removes nonlinearity and residual dependence. The documented graph holds exactly, with linear mechanisms.
  NL_SHARED    NL_PERM plus the real residuals of the same-sensor pairs moved together: for sensors ir_i, vis_i the same row permutation is used. Restores only the strong same-sensor residual dependence.
Fits use a separate half of the rows; rows are then generated from all rows, in-sample residuals are out-of-fold.

READING RULE L5, FIXED BEFORE THE FIRST RUN (project-management choice). For BOSS, GES, DirectLiNGAM: drop = precision at n = 1000 minus precision at n = 10000, averaged over methods.
  RESIDUAL DEPENDENCE is the main cause if drop(REAL) >= .08 and drop(NL_PERM) <= .03.
  NONLINEARITY is the main cause if drop(NL_PERM) >= .08 and drop(LIN_PERM) <= .03.
  MIXED otherwise. In LIN_PERM the drop is expected near 0; a large drop would mean the estimators or my scoring are at fault, and voids the reading.

Run: python -P -E E6_knockout_attribution.py
"""
import json
import os
import sys
import time
from pathlib import Path

for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(k, "1")
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor as HGB

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import E2_graph_level_real_data as E2  # noqa: E402

X, cols, edges = E2.load_chamber()
N, p = X.shape
idx = {c: i for i, c in enumerate(cols)}
truth = {(idx[a], idx[b]) for a, b in edges}
parents = {i: sorted(a for a, b in truth if b == i) for i in range(p)}
sensors = [i for i in range(p) if parents[i]]
sk = {(min(a, b), max(a, b)) for a, b in truth}
rng0 = np.random.default_rng(20261111)


def oof_fit(i, linear):
    """Out-of-fold fitted values of sensor i from its documented parents."""
    y = X[:, i]
    Z = X[:, parents[i]]
    perm = rng0.permutation(N)
    fit = np.zeros(N)
    for k in range(2):
        te = perm[k::2]
        tr = perm[(k + 1) % 2::2]
        if linear:
            A = np.column_stack([np.ones(len(tr)), Z[tr]])
            b, *_ = np.linalg.lstsq(A, y[tr], rcond=None)
            fit[te] = np.column_stack([np.ones(len(te)), Z[te]]) @ b
        else:
            fit[te] = HGB(max_iter=200, random_state=0).fit(Z[tr], y[tr]).predict(Z[te])
    return fit


FIT = {"lin": {i: oof_fit(i, True) for i in sensors}, "nl": {i: oof_fit(i, False) for i in sensors}}
RES = {k: {i: X[:, i] - FIT[k][i] for i in sensors} for k in FIT}


def build(mode, rng):
    if mode == "REAL":
        return X.copy()
    D = X.copy()
    kind = "lin" if mode == "LIN_PERM" else "nl"
    shared = {}
    for i in sensors:
        name = cols[i]
        if mode == "NL_SHARED" and name[:2] in ("ir", "vi"):
            key = name[-1]
            perm = shared.setdefault(key, rng.permutation(N))
        else:
            perm = rng.permutation(N)
        D[:, i] = FIT[kind][i] + RES[kind][i][perm]
    return D


results = []
t0 = time.time()
algos = ["BOSS", "GES", "DirectLiNGAM"]
for mode in ("REAL", "NL_PERM", "LIN_PERM", "NL_SHARED"):
    for n in (1000, 4000, 10000):
        reps = 1 if n == N and mode == "REAL" else 3
        for rep in range(reps):
            rng = np.random.default_rng(np.random.SeedSequence([20261112, n, rep, len(mode)]))
            D = build(mode, rng)
            sub = D if n == N else D[rng.choice(N, n, replace=False)]
            for a in algos:
                E = E2.run_algo(a, sub)
                s = E2.score(E, truth)
                fp = [e for e in E if e not in sk]
                results.append(dict(mode=mode, n=n, rep=rep, algo=a, false_edges=len(fp), **s))
    print(mode, f"{time.time() - t0:.0f}s", flush=True)
(HERE / "E6_results.json").write_text(json.dumps(results, indent=0), encoding="utf-8")
agg = {}
for r in results:
    agg.setdefault((r["mode"], r["algo"], r["n"]), []).append(r)
print("\nprecision / recall / false edges")
out = {}
for mode in ("REAL", "NL_PERM", "LIN_PERM", "NL_SHARED"):
    for a in algos:
        line = []
        for n in (1000, 4000, 10000):
            v = agg[(mode, a, n)]
            line.append(f"n={n}: {np.mean([x['prec'] for x in v]):.3f}/{np.mean([x['rec'] for x in v]):.3f}/{np.mean([x['false_edges'] for x in v]):.1f}")
        print(f"{mode:10s} {a:13s} " + "  ".join(line))
    drop = float(np.mean([np.mean([x["prec"] for x in agg[(mode, a, 1000)]]) - np.mean([x["prec"] for x in agg[(mode, a, 10000)]]) for a in algos]))
    out[mode] = drop
print("\nmean precision drop, n = 1000 to 10000:", {k: round(v, 3) for k, v in out.items()})
if out["LIN_PERM"] > .05:
    v = "VOID: estimators lose precision with n even in the well-specified knock-out"
elif out["REAL"] >= .08 and out["NL_PERM"] <= .03:
    v = "RESIDUAL DEPENDENCE"
elif out["NL_PERM"] >= .08 and out["LIN_PERM"] <= .03:
    v = "NONLINEARITY"
else:
    v = "MIXED"
print("L5:", v)
(HERE / "E6_summary.json").write_text(json.dumps(dict(drops=out, verdict=v), indent=1), encoding="utf-8")
