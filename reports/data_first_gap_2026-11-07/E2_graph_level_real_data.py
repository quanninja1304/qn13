"""E2: what do standard discovery algorithms achieve on real data, how does it change with n, and do they beat simple baselines?

Data sets:
  chamber  Causal Chamber light tunnel uniform_reference, 20 varying columns, documented ground truth. Actuators are randomized by design, so orientation of actuator edges is easy for any exogeneity-aware method.
  sachs    Flow cytometry, cyto_full_data.csv, 7466 rows, log1p. Scored against the consensus network, which is DISPUTED as truth (Brouillard et al. 2025). Rows pool 9 conditions. No claim of graph accuracy without this caveat.
  sachs_c1 First 853 rows of the same file, which by the published condition sizes correspond to one condition. The row-to-condition mapping is inferred from sizes, not documented in the file.

Algorithms (causal-learn): PC with Fisher z at alpha .05, .01, .001; GES with BIC; GRaSP; BOSS; DirectLiNGAM. Defaults otherwise. Same data subsamples for all.
Baselines:
  CorrBH   marginal correlations with Benjamini-Hochberg at .05.
  CorrK    the k largest |marginal correlation|, k = number of edges of the method compared. Compared to each method by name.
  PCorrBH  full-order partial correlations (precision matrix) with Benjamini-Hochberg at .05, a one-shot estimator with no search.
  Empty    no edges. RandomK: expected scores of a random graph with k edges, computed in closed form.
Metrics: skeleton precision, recall, F1 against the reference edges. Directed: among reference edges found in the skeleton, share with the correct direction; undirected edges counted as half.
n grid: 250, 500, 1000, 2000, 4000, 7000 (reps 5) and all rows (1 rep), chamber; 250, 500, 853 sachs_c1; 500, 1000, 2000, 4000, 7466 sachs.

READING RULE L2, FIXED BEFORE THE FIRST RUN (project-management choice):
  REVERSAL if, on chamber, for PC at .05 or GES, precision at the largest n is lower than at n = 1000 by >= .10 and recall rose by less than .10.
  NO SKILL on a data set if the best algorithm's skeleton F1 at the largest n exceeds the best of CorrBH, PCorrBH and the paired CorrK by less than .05.
  SATURATED if on chamber every algorithm's F1 stops improving (change < .02) between n = 2000 and the largest n and F1 < .90: more data does not help.
  These are descriptive flags for ranking candidate gaps, not a verdict on any method.

Run: python -P -E E2_graph_level_real_data.py [--quick]. Appends to E2_results.jsonl so a stopped run can continue.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(k, "1")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from causallearn.search.ConstraintBased.PC import pc  # noqa: E402
from causallearn.search.FCMBased import lingam  # noqa: E402
from causallearn.search.PermutationBased.BOSS import boss  # noqa: E402
from causallearn.search.PermutationBased.GRaSP import grasp  # noqa: E402
from causallearn.search.ScoreBased.GES import ges  # noqa: E402

QUICK = "--quick" in sys.argv
HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("GAP_DATA", os.path.join(os.environ["TEMP"], "gap_work", "data")))
SEED = 20261108
OUT = HERE / ("E2_results_quick.jsonl" if QUICK else "E2_results.jsonl")


def load_chamber():
    d = pd.read_csv(DATA / "cc_lt_int" / "x" / "lt_interventions_standard_v1" / "uniform_reference.csv")
    meta = ("timestamp", "config", "counter", "flag", "intervention", "camera", "v_board", "v_reg")
    cols = [c for c in d.columns if c not in meta and d[c].std() > 0]
    e = json.load(open(HERE / "causal_chamber_ground_truth_edges.json"))["lt_standard"]
    return d[cols].to_numpy(float), cols, [(a, b) for a, b in e if a in cols and b in cols]


def load_sachs():
    d = pd.read_csv(DATA / "sachs" / "cyto_full_data.csv")
    e = json.load(open(HERE / "sachs_consensus_edges.json"))["edges"]
    return np.log1p(d.to_numpy(float)), list(d.columns), [tuple(x) for x in e]


def from_causallearn(G):
    """Returns dict of edges {(i, j): kind}, i < j, kind in '>', '<', '-', '<>'."""
    out = {}
    p = G.shape[0]
    for i in range(p):
        for j in range(i + 1, p):
            a, b = G[i, j], G[j, i]
            if a == 0 and b == 0:
                continue
            if a == -1 and b == 1:
                out[(i, j)] = ">"
            elif a == 1 and b == -1:
                out[(i, j)] = "<"
            elif a == -1 and b == -1:
                out[(i, j)] = "-"
            else:
                out[(i, j)] = "o"
    return out


def run_algo(name, X):
    X = (X - X.mean(0)) / X.std(0)
    if name.startswith("PC"):
        a = float(name.split("_")[1])
        return from_causallearn(pc(X, a, "fisherz", True, 0, -1, show_progress=False, verbose=False).G.graph)
    if name == "GES":
        return from_causallearn(ges(X)["G"].graph)
    if name == "GRaSP":
        return from_causallearn(grasp(X, verbose=False).graph)
    if name == "BOSS":
        return from_causallearn(boss(X, verbose=False).graph)
    if name == "DirectLiNGAM":
        m = lingam.DirectLiNGAM()
        m.fit(X)
        A = np.abs(m.adjacency_matrix_) > 1e-8   # adaptive lasso output: A[i, j] != 0 means j -> i
        out = {}
        p = A.shape[0]
        for i in range(p):
            for j in range(i + 1, p):
                if A[j, i]:
                    out[(i, j)] = ">"
                elif A[i, j]:
                    out[(i, j)] = "<"
        return out
    raise ValueError(name)


def bh(p, q=.05):
    p = np.asarray(p)
    o = np.argsort(p)
    th = q * (np.arange(1, len(p) + 1)) / len(p)
    k = np.nonzero(p[o] <= th)[0]
    keep = np.zeros(len(p), bool)
    if len(k):
        keep[o[: k[-1] + 1]] = True
    return keep


def pair_stats(X):
    n, p = X.shape
    C = np.corrcoef(X.T)
    iu = np.triu_indices(p, 1)
    r = C[iu]
    z = np.arctanh(np.clip(r, -.999999, .999999)) * math.sqrt(n - 3)
    pv = np.array([math.erfc(abs(v) / math.sqrt(2)) for v in z])
    P = np.linalg.pinv(C)
    d = np.sqrt(np.diag(P))
    pr = -(P / np.outer(d, d))[iu]
    zp = np.arctanh(np.clip(pr, -.999999, .999999)) * math.sqrt(max(n - p - 1, 1))
    pp = np.array([math.erfc(abs(v) / math.sqrt(2)) for v in zp])
    return iu, r, pv, pr, pp


def score(edges, truth):
    """edges: dict (i,j)->kind. truth: set of (a,b) directed index pairs."""
    tru_sk = {(min(a, b), max(a, b)) for a, b in truth}
    es = set(edges)
    tp = len(es & tru_sk)
    prec = tp / len(es) if es else float("nan")
    rec = tp / len(tru_sk)
    f1 = 2 * tp / (len(es) + len(tru_sk)) if (es or tru_sk) else 0.0
    orient = 0.0
    for (i, j) in es & tru_sk:
        k = edges[(i, j)]
        right = ">" if (i, j) in truth else "<"
        orient += 1.0 if k == right else (0.5 if k in ("-", "o") else 0.0)
    return dict(k=len(es), prec=prec, rec=rec, f1=f1, orient=orient / tp if tp else float("nan"))


def main():
    rng = np.random.default_rng(SEED)
    Xc, cc, ec = load_chamber()
    Xs, cs, es = load_sachs()
    sets = {"chamber": (Xc, cc, ec, (1000, 10000) if QUICK else (250, 500, 1000, 2000, 4000, 7000, 10000)),
            "sachs": (Xs, cs, es, (1000, 7466) if QUICK else (500, 1000, 2000, 4000, 7466)),
            "sachs_c1": (Xs[:853], cs, es, (853,) if QUICK else (250, 500, 853))}
    algos = ["PC_0.05", "PC_0.01", "PC_0.001", "GES", "GRaSP", "BOSS", "DirectLiNGAM"]
    done = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["data"], r["n"], r["rep"], r["method"]))
    with OUT.open("a", encoding="utf-8") as fh:
        for name, (X, cols, edges, ns) in sets.items():
            idx = {c: i for i, c in enumerate(cols)}
            truth = {(idx[a], idx[b]) for a, b in edges}
            p = X.shape[1]
            print(name, "rows", X.shape[0], "p", p, "edges", len(truth), "max possible", p * (p - 1) // 2, flush=True)
            for n in ns:
                reps = 1 if n >= X.shape[0] else (1 if QUICK else 5)
                for rep in range(reps):
                    rr = np.random.default_rng(np.random.SeedSequence([SEED, n, rep, len(name)]))
                    sub = X if n >= X.shape[0] else X[rr.choice(X.shape[0], n, replace=False)]
                    iu, r, pv, pr, pp = pair_stats(sub)
                    base = {}
                    base["CorrBH"] = {(int(iu[0][t]), int(iu[1][t])): "-" for t in np.flatnonzero(bh(pv))}
                    base["PCorrBH"] = {(int(iu[0][t]), int(iu[1][t])): "-" for t in np.flatnonzero(bh(pp))}
                    base["Empty"] = {}
                    for m, E in base.items():
                        s = score(E, truth)
                        fh.write(json.dumps(dict(data=name, n=n, rep=rep, method=m, secs=0.0, **s)) + "\n")
                    order = np.argsort(-np.abs(r))
                    for a in algos:
                        if (name, n, rep, a) in done:
                            continue
                        t0 = time.time()
                        try:
                            E = run_algo(a, sub)
                        except Exception as ex:  # recorded, not hidden
                            fh.write(json.dumps(dict(data=name, n=n, rep=rep, method=a, error=repr(ex)[:200])) + "\n")
                            print("ERROR", name, n, rep, a, repr(ex)[:160], flush=True)
                            continue
                        s = score(E, truth)
                        k = len(E)
                        Ek = {(int(iu[0][t]), int(iu[1][t])): "-" for t in order[:k]}
                        sk = score(Ek, truth)
                        tp_random = k * len(truth) / (p * (p - 1) / 2)
                        fh.write(json.dumps(dict(data=name, n=n, rep=rep, method=a, secs=round(time.time() - t0, 2), corrk_f1=sk["f1"], corrk_prec=sk["prec"], random_prec=len(truth) / (p * (p - 1) / 2), random_f1=2 * tp_random / (k + len(truth)) if k + len(truth) else 0.0, edges=[[int(i), int(j), kind] for (i, j), kind in E.items()], **s)) + "\n")
                        fh.flush()
                        print(name, n, rep, a, f"{time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
