"""E2b: anatomy of errors on the chamber. Descriptive, no reading rule. Uses E2_results.jsonl only.

False edges are split by type (sensor-sensor, actuator-sensor, actuator-actuator). Missed edges are split by the parent's kind. For missed reference edges and false sensor-sensor edges the effect size on the full data is reported:
partial correlation given the other reference parents, and a nonparametric equivalent (share of residual variance explained by adding the variable to a boosted model), so that weak and nonlinear effects can be told apart.
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(k, "1")
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor as HGB

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import E2_graph_level_real_data as E2  # noqa: E402

X, cols, edges = E2.load_chamber()
X = (X - X.mean(0)) / X.std(0)
idx = {c: i for i, c in enumerate(cols)}
truth = {(idx[a], idx[b]) for a, b in edges}
sk = {(min(a, b), max(a, b)) for a, b in truth}
parents = {i: [a for a, b in truth if b == i] for i in range(len(cols))}
is_sensor = {i: bool(parents[i]) for i in range(len(cols))}
rows = [json.loads(x) for x in (HERE / "E2_results.jsonl").read_text(encoding="utf-8").splitlines()]
rows = [r for r in rows if r["data"] == "chamber" and "edges" in r]
out = {}
print("mean false edges by type and missed reference edges, per run")
for m in ("PC_0.05", "GES", "BOSS", "GRaSP", "DirectLiNGAM"):
    for n in (1000, 4000, 10000):
        rs = [r for r in rows if r["method"] == m and r["n"] == n]
        ty = Counter()
        missed = Counter()
        for r in rs:
            es = {(i, j) for i, j, _ in r["edges"]}
            for i, j in es - sk:
                ty["S-S" if is_sensor[i] and is_sensor[j] else ("A-A" if not is_sensor[i] and not is_sensor[j] else "A-S")] += 1
            for a, b in sk - es:
                pa, ch = (a, b) if (a, b) in truth else (b, a)
                missed[cols[pa][:3] if cols[pa][:2] in ("l_", "po") else "rgb"] += 1
        k = len(rs)
        print(f"{m:13s} n={n:5d} false: " + " ".join(f"{t}={ty[t] / k:.1f}" for t in ("S-S", "A-S", "A-A")) + " | missed by parent kind: " + " ".join(f"{t}={v / k:.1f}" for t, v in sorted(missed.items())), flush=True)
        out[f"{m} {n}"] = {"false": {t: ty[t] / k for t in ("S-S", "A-S", "A-A")}, "missed": {t: v / k for t, v in missed.items()}}

# per reference edge effect sizes on the full data
print("\nreference edges: partial r given other parents; boosted gain in R2 from adding the parent")
rng = np.random.default_rng(3)
tr = rng.permutation(len(X))
a, b = tr[:7000], tr[7000:]


def r2(Xa, ya, Xb, yb):
    if Xa.shape[1] == 0:
        return 0.0
    m = HGB(max_iter=200, random_state=0).fit(Xa, ya)
    p = m.predict(Xb)
    return 1 - float(((yb - p) ** 2).mean() / yb.var())


table = []
for pa_, ch in sorted(truth, key=lambda e: (e[1], e[0])):
    others = [p for p in parents[ch] if p != pa_]
    Z = np.column_stack([np.ones(len(X))] + [X[:, o] for o in others])
    Q, _ = np.linalg.qr(Z)
    rx = X[:, pa_] - Q @ (Q.T @ X[:, pa_])
    ry = X[:, ch] - Q @ (Q.T @ X[:, ch])
    pr = float(rx @ ry / np.sqrt((rx @ rx) * (ry @ ry)))
    base = r2(X[a][:, others], X[a, ch], X[b][:, others], X[b, ch])
    full = r2(X[a][:, others + [pa_]], X[a, ch], X[b][:, others + [pa_]], X[b, ch])
    found = np.mean([any({i, j} == {pa_, ch} for i, j, _ in r["edges"]) for r in rows if r["method"] in ("GES", "BOSS", "DirectLiNGAM") and r["n"] >= 7000])
    table.append(dict(parent=cols[pa_], child=cols[ch], partial_r=pr, gain_r2=full - base, found_rate=float(found)))
for t in table:
    print(f"{t['parent']:6s} -> {t['child']:8s} partial r {t['partial_r']:+.3f}  gain R2 {t['gain_r2']:+.3f}  found by linear score methods at n>=7000: {t['found_rate']:.2f}")
out["reference_edges"] = table
pr = np.array([abs(t["partial_r"]) for t in table])
gn = np.array([t["gain_r2"] for t in table])
fd = np.array([t["found_rate"] for t in table])
print("\nedges with |partial r| < .05:", int((pr < .05).sum()), "of", len(pr), "| of which gain R2 >= .01 (real but nonlinear):", int(((pr < .05) & (gn >= .01)).sum()))
print("found rate: |r|>=.05 ->", round(float(fd[pr >= .05].mean()), 3), " |r|<.05 ->", round(float(fd[pr < .05].mean()), 3) if (pr < .05).any() else None)
out["summary"] = {"n_edges": len(pr), "abs_r_below_05": int((pr < .05).sum()), "nonlinear_gain_among_them": int(((pr < .05) & (gn >= .01)).sum()), "found_rate_strong": float(fd[pr >= .05].mean()), "found_rate_weak": float(fd[pr < .05].mean()) if (pr < .05).any() else None}
(HERE / "E2b_outputs.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
