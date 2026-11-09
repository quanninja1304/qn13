"""E3: on real data with a usable reference graph, can a practitioner pick a good operating point without the truth?

Every discovery run needs a choice of algorithm and sparsity level, and in practice there is no ground truth to tune against. This measures whether internal scores pick well.

Data: chamber (documented ground truth) decides; sachs (consensus, disputed) is descriptive only. Rows outside the fit sample form a held-out set.
Configurations at each n: PC at alpha in {.05, .01, .001, 1e-5, 1e-8}; PC with an effect-size floor tau in {.02, .05, .1}, implemented as the alpha that corresponds to |partial r| = tau at conditioning size 2; GES and BOSS with BIC multiplier
lambda in {1, 2, 4, 8, 16, 32}; GRaSP with lambda in {1, 4, 16}. Multiplier 1 is standard BIC, which is lambda_value = .5 in causal-learn (the code passes .5 times the multiplier; caught before the first full run).
Internal scores, no access to the reference graph:
  stability   mean pairwise Jaccard of skeletons over 6 half-samples, as in stability selection style checks.
  heldout     mean held-out Gaussian log-likelihood of the graph (consistent DAG extension, linear fit on the fit sample).
  bic         BIC of the same fit on the fit sample.
  lovo        simplified leave-one-variable-out error after Schkoda et al. 2025: for 10 random pairs (X, Y), run the method without Y and without X, adjust for the union of parents of X and Y found there, predict corr(X, Y) on a separate third of the data
              and compare with the observed correlation on the last third. Not the authors' code: it does not apply their pair-exclusion lemmas. Compared with their random-adjustment baseline is left out here.
Self-compatibility (Faller et al. 2024) is not implemented in this pass and is not evaluated.
Outcome: skeleton F1 against the reference edges, and precision, recall.

READING RULE L3, FIXED BEFORE THE FIRST RUN (project-management choice). On chamber, per n in {4000, 8000}, averaged over 3 replicates:
  regret(score) = best F1 in the grid - F1 of the configuration the score selects; gain(score) = F1 selected - F1 of the default (the better of PC .05 and GES lambda = 1, chosen without truth as: GES lambda = 1).
  PAIN if for every score, at both n: regret >= .10 and gain < .02. No internal score beats the default by a useful margin and a much better configuration exists.
  NO PAIN if some score has regret < .05 at both n. Then selection is solved by a simple score and this gap is not worth pursuing.
  Otherwise MIXED.
  Also read, not part of the verdict: does a fixed configuration exist whose precision does not decay with n, which would show whether simple thresholds cure the decay seen in E2?

Run: python -P -E E3_internal_scores.py [--quick]. Appends to E3_results.jsonl.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys
import time
from pathlib import Path

for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(k, "1")
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
QUICK = "--quick" in sys.argv
import E2_graph_level_real_data as E2  # noqa: E402
from causallearn.search.ConstraintBased.PC import pc  # noqa: E402
from causallearn.search.PermutationBased.BOSS import boss  # noqa: E402
from causallearn.search.PermutationBased.GRaSP import grasp  # noqa: E402
from causallearn.search.ScoreBased.GES import ges  # noqa: E402

SEED = 20261109
OUT = HERE / ("E3_results_quick.jsonl" if QUICK else "E3_results.jsonl")


def configs():
    c = [("PC", a) for a in (.05, .01, .001, 1e-5, 1e-8)]
    c += [("PCtau", t) for t in (.02, .05, .1)]
    c += [("GES", l) for l in (1, 2, 4, 8, 16, 32)]
    c += [("BOSS", l) for l in (1, 2, 4, 8, 16, 32)]
    c += [("GRaSP", l) for l in (1, 4, 16)]
    return c


def run(cfg, X):
    name, v = cfg
    X = (X - X.mean(0)) / X.std(0)
    n = X.shape[0]
    if name == "PC":
        return E2.from_causallearn(pc(X, v, "fisherz", True, 0, -1, show_progress=False, verbose=False).G.graph)
    if name == "PCtau":
        a = math.erfc(math.atanh(v) * math.sqrt(max(n - 5, 1)) / math.sqrt(2))
        a = max(a, 1e-300)
        return E2.from_causallearn(pc(X, a, "fisherz", True, 0, -1, show_progress=False, verbose=False).G.graph)
    if name == "GES":
        return E2.from_causallearn(ges(X, parameters={"lambda_value": .5 * v}, lambda_value=.5 * v)["G"].graph)
    if name == "BOSS":
        return E2.from_causallearn(boss(X, parameters={"lambda_value": .5 * v}, verbose=False).graph)
    if name == "GRaSP":
        return E2.from_causallearn(grasp(X, parameters={"lambda_value": .5 * v}, verbose=False).graph)
    raise ValueError(name)


def parents_from(edges, p):
    """Consistent parent sets: directed edges kept, others oriented along a topological order of the directed part."""
    pa = {i: set() for i in range(p)}
    und = []
    for (i, j), k in edges.items():
        if k == ">":
            pa[j].add(i)
        elif k == "<":
            pa[i].add(j)
        else:
            und.append((i, j))
    order, seen, tmp = [], set(), set()

    def visit(v):
        if v in seen or v in tmp:
            return
        tmp.add(v)
        for u in pa[v]:
            visit(u)
        tmp.discard(v)
        seen.add(v)
        order.append(v)

    for v in range(p):
        visit(v)
    pos = {v: i for i, v in enumerate(order)}
    for i, j in und:
        if pos[i] < pos[j]:
            pa[j].add(i)
        else:
            pa[i].add(j)
    return pa


def gauss_scores(edges, Xtr, Xte):
    p = Xtr.shape[1]
    mu, sd = Xtr.mean(0), Xtr.std(0)
    A, B = (Xtr - mu) / sd, (Xte - mu) / sd
    pa = parents_from(edges, p)
    ll, bic = 0.0, 0.0
    n = len(A)
    for v in range(p):
        P = sorted(pa[v])
        if P:
            beta, *_ = np.linalg.lstsq(A[:, P], A[:, v], rcond=None)
            r, rt = A[:, v] - A[:, P] @ beta, B[:, v] - B[:, P] @ beta
        else:
            r, rt = A[:, v], B[:, v]
        s2 = max(float(r @ r) / n, 1e-9)
        ll += float(-.5 * (math.log(2 * math.pi * s2) + (rt @ rt) / len(rt) / s2))
        bic += float(-n * math.log(s2) - len(P) * math.log(n))
    return ll, bic


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def lovo_error(cfg, X, rng, pairs=10):
    n, p = X.shape
    idx = rng.permutation(n)
    a, b, c = np.array_split(idx, 3)
    errs = []
    pl = list(itertools.combinations(range(p), 2))
    for t in rng.choice(len(pl), min(pairs, len(pl)), replace=False):
        x, y = pl[int(t)]
        keepx = [v for v in range(p) if v != y]
        keepy = [v for v in range(p) if v != x]
        Ex = run(cfg, X[np.ix_(a, keepx)])
        Ey = run(cfg, X[np.ix_(b, keepy)])
        pax = parents_from(Ex, len(keepx))[keepx.index(x)]
        pay = parents_from(Ey, len(keepy))[keepy.index(y)]
        Z = sorted({keepx[i] for i in pax} | {keepy[i] for i in pay})
        D = X[c]
        D = (D - D.mean(0)) / D.std(0)
        obs = float(np.mean(D[:, x] * D[:, y]))
        if Z:
            A = (X[a] - X[a].mean(0)) / X[a].std(0)
            B = (X[b] - X[b].mean(0)) / X[b].std(0)
            rxz = A[:, x] @ A[:, Z] / len(A)
            ryz = B[:, y] @ B[:, Z] / len(B)
            Czz = np.cov(np.vstack([A[:, Z], B[:, Z]]).T).reshape(len(Z), len(Z))
            pred = float(rxz @ np.linalg.solve(Czz + 1e-8 * np.eye(len(Z)), ryz))
        else:
            pred = 0.0
        errs.append(abs(pred - obs))
    return float(np.mean(errs))


def main():
    Xc, cc, ec = E2.load_chamber()
    Xs, cs, es = E2.load_sachs()
    sets = {"chamber": (Xc, cc, ec, (1000, 8000) if QUICK else (1000, 4000, 8000)), "sachs": (Xs, cs, es, (1000,) if QUICK else (1000, 3000, 6000))}
    done = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["data"], r["n"], r["rep"], r["algo"], r["param"]))
    t00 = time.time()
    cfgs = configs()[:5] + configs()[8:10] if QUICK else configs()
    with OUT.open("a", encoding="utf-8") as fh:
        for name, (X, cols, edges, ns) in sets.items():
            idx = {c: i for i, c in enumerate(cols)}
            truth = {(idx[a], idx[b]) for a, b in edges}
            for n, rep in itertools.product(ns, range(1 if QUICK else 3)):
                rr = np.random.default_rng(np.random.SeedSequence([SEED, n, rep, len(name)]))
                perm = rr.permutation(X.shape[0])
                tr, te = X[perm[:n]], X[perm[n:]]
                for cfg in cfgs:
                    key = (name, n, rep, cfg[0], cfg[1])
                    if key in done:
                        continue
                    t0 = time.time()
                    try:
                        E = run(cfg, tr)
                        s = E2.score(E, truth)
                        ll, bic = gauss_scores(E, tr, te)
                        runs = []
                        for b in range(2 if QUICK else 6):
                            sub = rr.choice(n, n // 2, replace=False)
                            runs.append(run(cfg, tr[sub]))
                        stab = float(np.mean([jaccard(u, v) for u, v in itertools.combinations(runs, 2)]))
                        lv = lovo_error(cfg, tr, rr, pairs=2 if QUICK else 10) if rep == 0 else None
                        fh.write(json.dumps(dict(data=name, n=n, rep=rep, algo=cfg[0], param=cfg[1], stability=stab, heldout=ll, bic=bic, lovo=lv, secs=round(time.time() - t0, 1), **s)) + "\n")
                        fh.flush()
                    except Exception as ex:  # recorded, not hidden
                        fh.write(json.dumps(dict(data=name, n=n, rep=rep, algo=cfg[0], param=cfg[1], error=repr(ex)[:200])) + "\n")
                        print("ERROR", key, repr(ex)[:160], flush=True)
                    print(name, n, rep, cfg, f"{time.time() - t0:.1f}s total {time.time() - t00:.0f}s", flush=True)


if __name__ == "__main__":
    main()
