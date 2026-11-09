"""E5: when residual dependence between sensors is real, do methods that allow latent confounding describe it correctly?

E1 found sensor pairs dependent given all documented parents. The chamber authors say edges mean interventional effects and that unmeasured confounding exists, so such a pair should not be reported as a directed causal edge.
Physically a sensor reading cannot cause another sensor reading here: sensors have no outgoing edges in the documented graph, and no such effect is known. This is background knowledge, not a measurement from these data.

Counted over sensor-sensor adjacencies, by n: directed (a causal claim: wrong under the assumption above), undirected or unresolved, and bidirected or circle marks (compatible with latent confounding).
Methods: PC, GES, BOSS (DAG or CPDAG assumption), FCI with Fisher z at alpha .05 and .001 (causal-learn). Descriptive, no reading rule.

Run: python -P -E E5_latent_aware_chamber.py
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
from causallearn.search.ConstraintBased.FCI import fci  # noqa: E402
from causallearn.search.ConstraintBased.PC import pc  # noqa: E402
from causallearn.search.PermutationBased.BOSS import boss  # noqa: E402
from causallearn.search.ScoreBased.GES import ges  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
X, cols, edges = E2.load_chamber()
idx = {c: i for i, c in enumerate(cols)}
parents = {i: 0 for i in range(len(cols))}
for a, b in edges:
    parents[idx[b]] += 1
sensor = {i: parents[i] > 0 for i in range(len(cols))}
ref = {(min(idx[a], idx[b]), max(idx[a], idx[b])) for a, b in edges}


def classify(G):
    """causal-learn endpoints: -1 tail, 1 arrow, 2 circle. G[i,j] is the mark at i on edge i-j."""
    c = Counter()
    p = G.shape[0]
    pairs = []
    for i in range(p):
        for j in range(i + 1, p):
            a, b = G[i, j], G[j, i]
            if a == 0 and b == 0:
                continue
            if not (sensor[i] and sensor[j]):
                continue
            if (a == -1 and b == 1) or (a == 1 and b == -1):
                k = "directed"
            elif a == 1 and b == 1:
                k = "bidirected"
            elif a == -1 and b == -1:
                k = "undirected"
            elif a == 2 or b == 2:
                k = "circle"
            else:
                k = "other"
            c[k] += 1
            pairs.append((cols[i], cols[j], k))
    return c, pairs


out = {}
for n in (1000, 4000, 10000):
    agg = {}
    reps = 1 if n == X.shape[0] else 3
    for rep in range(reps):
        rr = np.random.default_rng(np.random.SeedSequence([20261110, n, rep]))
        sub = X if n == X.shape[0] else X[rr.choice(X.shape[0], n, replace=False)]
        D = (sub - sub.mean(0)) / sub.std(0)
        runs = {"PC .05": lambda: pc(D, .05, "fisherz", True, 0, -1, show_progress=False, verbose=False).G.graph,
                "GES": lambda: ges(D)["G"].graph,
                "BOSS": lambda: boss(D, verbose=False).graph,
                "FCI .05": lambda: fci(D, "fisherz", .05, depth=-1, verbose=False, show_progress=False)[0].graph,
                "FCI .001": lambda: fci(D, "fisherz", .001, depth=-1, verbose=False, show_progress=False)[0].graph}
        for m, f in runs.items():
            c, pairs = classify(f())
            a = agg.setdefault(m, Counter())
            for k, v in c.items():
                a[k] += v
            if n == X.shape[0]:
                out.setdefault("pairs_n10000", {})[m] = pairs
    out[str(n)] = {m: {k: v / reps for k, v in a.items()} for m, a in agg.items()}
    print(n, out[str(n)], flush=True)
(HERE / "E5_outputs.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("same-sensor pairs at n=10000:", {m: [p for p in v if p[0][-1] == p[1][-1] and p[0][:2] in ("ir", "vi") and p[1][:2] in ("ir", "vi")] for m, v in out["pairs_n10000"].items()})
