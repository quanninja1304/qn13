"""Post hoc check of a threat to the T4-L pilot's reading. Oracle only.

Threat. The pilot limits conditioning sets to size 3 and has no possible-d-sep phase, for every method. The listwise target is denser, so it may need larger sets. If the truncated procedure makes false
claims in the oracle for regime O, then "methods nearer the listwise target make more false claims" could be an artifact of the truncation and not a property of the target.

Compared on graphs from the pilot's generator (p = 10, mech = mixed), in the oracle:
  Complete3, LW3, Naive3   PC-stable with order at most 3, as in the pilot.
  LWall, Naiveall          exhaustive separating sets over all subsets of the other variables (O.fci), which needs neither truncation nor possible-d-sep. Same claim extraction.
Reading, fixed before the first run: if LW3 has false claims on more than 10% of graphs while LWall has none, the truncation contributes and the claim "the listwise target itself hurts" is not established
by the pilot. Does not change the K8 verdict, which is about the declared procedure.

Run: python -P -E T4L_truncation_oracle_check.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import T4L_algorithm_pilot as Q  # noqa: E402
import T4_oracle_checks as O  # noqa: E402
from T4L_pilot_diagnostics import claim_sets, m  # noqa: E402

SEED = 20261114
N = 60
keys = ("Complete3", "LW3", "Naive3", "LWall", "Naiveall")
agg = {k: dict(false=0, true=0, graphs_false=0, edges=0) for k in keys}
t0 = time.time()
for i in range(N):
    rng = np.random.default_rng(np.random.SeedSequence([SEED, i]))
    g, w, plan, order, ell = Q.make_graph(10, rng, mech="mixed", rho=.25)
    Ov = list(range(10))
    full = (1 << 10) - 1

    def lw(x, y, W):
        return g.sep(x, y, m(W), full)

    def nv(x, y, W):
        return g.sep(x, y, m(W), (1 << x) | (1 << y) | m(W))

    def cp(x, y, W):
        return g.dsep_raw(x, y, m(W))

    Ps = {"Complete3": Q.orient(Q.skeleton(Ov, cp)), "LW3": Q.orient(Q.skeleton(Ov, lw)), "Naive3": Q.orient(Q.skeleton(Ov, nv)), "LWall": O.fci(Ov, lw), "Naiveall": O.fci(Ov, nv)}
    for k, P in Ps.items():
        F, T, _, _ = claim_sets(g, P, 10)
        agg[k]["false"] += len(F)
        agg[k]["true"] += len(T)
        agg[k]["graphs_false"] += len(F) > 0
        agg[k]["edges"] += sum(len(P.adj[v]) for v in Ov) // 2
    if i % 10 == 0:
        print(i, round(time.time() - t0), flush=True)
out = {k: {kk: vv / N for kk, vv in v.items()} for k, v in agg.items()}
for k, v in out.items():
    print(k, {kk: round(vv, 3) for kk, vv in v.items()})
art = out["LW3"]["graphs_false"] > .10 and out["LWall"]["graphs_false"] == 0
print("truncation contributes by the declared reading:", art)
(HERE / "T4L_truncation_oracle_outputs.json").write_text(json.dumps(dict(seed=SEED, graphs=N, per_graph=out, truncation_contributes=art), indent=1), encoding="utf-8")
