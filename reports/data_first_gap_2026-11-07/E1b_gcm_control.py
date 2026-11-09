"""E1b: is the GCM rejection of sensor-sensor nulls in E1 real dependence, or error of the boosted regression?

Same N3 queries and same GCM as E1, at n = 10000, on knock-out data built as in E6 (NL_PERM): sensors = out-of-fold boosted fit of documented parents + residual permuted per sensor. Residual dependence is absent by construction, nonlinearity remains.
This control is favorable to the regressor, because the mechanism it must learn is itself a boosted fit, but it is what can be done with these data.

READING RULE L6, FIXED BEFORE THE FIRST RUN (project-management choice): over 3 knock-out draws,
  REAL DEPENDENCE if rejection in the control <= .10 while E1 on the measured data gave .361. The small residual dependences in E1 then are not test error.
  TEST ARTEFACT if rejection in the control >= .25: E1 cannot separate dependence from regression error.
  UNCLEAR otherwise.

Run: python -P -E E1b_gcm_control.py
"""
import json
import os
import sys
from pathlib import Path

for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(k, "1")
import numpy as np
import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import E1_ci_calibration_chamber as E1  # noqa: E402
import E2_graph_level_real_data as E2  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor as HGB  # noqa: E402

X, cols, edges = E2.load_chamber()
X = (X - X.mean(0)) / X.std(0)
N = len(X)
idx = {c: i for i, c in enumerate(cols)}
g = nx.DiGraph()
g.add_nodes_from(cols)
g.add_edges_from(edges)
sensors = [c for c in cols if g.in_degree(c) > 0]
Q = []
for i, a in enumerate(sensors):
    for b in sensors[i + 1:]:
        Q.append((a, b, tuple(sorted(set(g.predecessors(a)) | set(g.predecessors(b))))))
rng = np.random.default_rng(20261113)
fit = {}
for c in sensors:
    P = [idx[v] for v in g.predecessors(c)]
    y, Z = X[:, idx[c]], X[:, P]
    perm = rng.permutation(N)
    f = np.zeros(N)
    for k in range(2):
        te, tr = perm[k::2], perm[(k + 1) % 2::2]
        f[te] = HGB(max_iter=200, random_state=0).fit(Z[tr], y[tr]).predict(Z[te])
    fit[c] = f
out = []
for draw in range(3):
    D = X.copy()
    for c in sensors:
        r = X[:, idx[c]] - fit[c]
        D[:, idx[c]] = fit[c] + r[rng.permutation(N)]
    rej = 0
    rows = []
    for a, b, S in Q:
        Z = D[:, [idx[s] for s in S]]
        p, r = E1.gcm(D[:, idx[a]], D[:, idx[b]], Z, rng)
        rej += p < .05
        rows.append((a, b, float(p), float(r)))
    rate = rej / len(Q)
    top = sorted(rows, key=lambda x: -abs(x[3]))[:4]
    print("draw", draw, "rejection", round(rate, 3), "max |r| pairs", [(a, b, round(r, 3)) for a, b, p, r in top], flush=True)
    out.append(dict(draw=draw, rejection=rate, rows=rows))
m = float(np.mean([o["rejection"] for o in out]))
v = "REAL DEPENDENCE" if m <= .10 else ("TEST ARTEFACT" if m >= .25 else "UNCLEAR")
print("mean control rejection", round(m, 3), "versus .361 on measured data -> L6:", v)
(HERE / "E1b_outputs.json").write_text(json.dumps(dict(mean_rejection=m, verdict=v, draws=out), indent=0), encoding="utf-8")
