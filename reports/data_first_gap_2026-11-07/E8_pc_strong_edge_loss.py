"""E8: why does PC lose strong edges on the chamber at n = 10000? Descriptive and post hoc, no reading rule.

Hypothesis, formed after seeing E2: sensors are near-noiseless readings of the same light. Conditioning on sibling sensors nearly blocks an actuator's effect on a sensor, so a small correlation given a redundant proxy gets read as independence. This would be a known kind of problem (near-determinism, measurement error as a blurred separator) appearing on a real system.
Measured for strong reference edges (red, green, blue to sensors):
  which separating sets PC used to delete them, and whether they contain a sensor;
  the partial correlation given that set, on all rows;
  whether deletion persists in knock-outs from E6: LIN_PERM (linear, residuals permuted) and in LIN_NOISE, the same with sensor noise multiplied by 5, which makes proxies less redundant.
Run: python -P -E E8_pc_strong_edge_loss.py
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(k, "1")
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import E2_graph_level_real_data as E2  # noqa: E402
from causallearn.search.ConstraintBased.PC import pc  # noqa: E402

X, cols, edges = E2.load_chamber()
N, p = X.shape
X = (X - X.mean(0)) / X.std(0)
idx = {c: i for i, c in enumerate(cols)}
truth = {(idx[a], idx[b]) for a, b in edges}
parents = {i: sorted(a for a, b in truth if b == i) for i in range(p)}
sensors = {i for i in range(p) if parents[i]}
rgb = {idx["red"], idx["green"], idx["blue"]}
strong = {(a, b) for a, b in truth if a in rgb}
rng = np.random.default_rng(20261114)


def linear_knock(noise=1.0):
    D = X.copy()
    for i in sensors:
        A = np.column_stack([np.ones(N), X[:, parents[i]]])
        b, *_ = np.linalg.lstsq(A, X[:, i], rcond=None)
        f = A @ b
        r = X[:, i] - f
        D[:, i] = f + noise * r[rng.permutation(N)]
    return D


def pcorr(D, a, b, S):
    A = np.column_stack([np.ones(len(D))] + [D[:, s] for s in S])
    Q, _ = np.linalg.qr(A)
    ra = D[:, a] - Q @ (Q.T @ D[:, a])
    rb = D[:, b] - Q @ (Q.T @ D[:, b])
    return float(ra @ rb / np.sqrt((ra @ ra) * (rb @ rb)))


out = {}
for name, D in (("REAL", X), ("LIN_PERM", linear_knock(1.0)), ("LIN_NOISE_x5", linear_knock(5.0))):
    r2 = {cols[i]: float(1 - np.var(D[:, i] - np.column_stack([np.ones(N), D[:, parents[i]]]) @ np.linalg.lstsq(np.column_stack([np.ones(N), D[:, parents[i]]]), D[:, i], rcond=None)[0]) / np.var(D[:, i])) for i in sorted(sensors)}
    cg = pc(D, .05, "fisherz", True, 0, -1, show_progress=False, verbose=False)
    G = cg.G.graph
    kept = {(a, b) for a, b in strong if G[a, b] != 0}
    lost = strong - kept
    rows = []
    for a, b in sorted(lost):
        sep = cg.sepset[a, b] or cg.sepset[b, a]
        S = list(sep[0]) if sep else []
        rows.append(dict(edge=f"{cols[a]}->{cols[b]}", sepset=[cols[s] for s in S], sensor_in_sepset=any(s in sensors for s in S), marginal_r=pcorr(D, a, b, []), r_given_other_parents=pcorr(D, a, b, [x for x in parents[b] if x != a]), r_given_sepset=pcorr(D, a, b, S)))
    print(f"\n{name}: strong edges kept {len(kept)}/{len(strong)}; lost {len(lost)}; total edges {int((G != 0).sum() / 2)}; median linear R2 of sensors {np.median(list(r2.values())):.3f}")
    print("  lost with a sensor in the separating set:", sum(r["sensor_in_sepset"] for r in rows), "of", len(rows))
    for r in rows[:8]:
        print(f"  {r['edge']:16s} r given other parents {r['r_given_other_parents']:+.3f}; marginal {r['marginal_r']:+.3f}; given sepset {r['r_given_sepset']:+.3f}; sepset {r['sepset']}")
    out[name] = dict(kept=len(kept), total=len(strong), lost_rows=rows, sensor_r2=r2)
(HERE / "E8_outputs.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
