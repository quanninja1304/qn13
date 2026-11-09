"""E1: are conditional independence tests calibrated on real physical data, where the independences are known?

Data: Causal Chamber light tunnel, lt_interventions_standard_v1, uniform_reference.csv (10000 rows, about one hour at 2 Hz, md5 of the archive 476664d024f88e8b7640998bb5e9ee33; Gamella, Peters, Buhlmann).
Ground truth: edges in causalchamber 0.2.8, parsed into causal_chamber_ground_truth_edges.json. Authors validated them empirically; they are not guaranteed exhaustive, and part 3 below checks that.

Null query classes, each d-separated in the ground-truth graph restricted to the varying columns:
  N1  actuator vs actuator, empty set. Both are set by a random generator, so this is a control for the test itself.
  N2  actuator vs sensor that is not its descendant, empty set. Physical null.
  N2c same pair given the parents of the sensor. Physical null with sensor variance removed.
  N3  sensor vs sensor given the union of their parents. Physical null; any residual dependence means an unmodelled shared cause, misfit of the parent function, or a missing edge.
Power class:
  P   actuator to sensor with an edge in the graph, given the other parents of the sensor.

Tests: Fisher z (linear Gaussian, what PC/FCI usually run), and GCM (Shah and Peters) with cross-fitted gradient boosting, which removes most functional misfit from the conditioning step.
Parts: (1) rejection rate at alpha = .05 by class and n, random subsamples; (2) mechanism checks at n = 10000: timestamp as extra conditioning variable, lag-1 autocorrelation of residuals, effect sizes, permutation placebo;
(3) do the interventional files confirm the supposed non-effects? Two-sample Kolmogorov-Smirnov test of each non-descendant sensor between each intervention file and the reference, compared with descendants.

READING RULE L1, FIXED BEFORE THE FIRST RUN (project-management choice):
  VALID control: N1 rejection stays at or below .10 at every n for both tests. If not, stop: the test is broken.
  PAIN if for N2c or N3, under GCM at n = 10000, rejection >= .20 and it is at least twice the rate at n = 1000, and the partial correlations rejected are small (median |r| < .10).
  This would mean real-data CI tests reject known independences more as data grows, for effects too small to matter.
  NO PAIN if under GCM all physical null classes stay at or below .10 at n = 10000.
  Otherwise MIXED. Fisher z failing alone is misfit of a linear test, which is known, and does not count as PAIN.

Run: python -P -E E1_ci_calibration_chamber.py [--quick]. Data folder: env GAP_DATA.
"""
from __future__ import annotations

import glob
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
import networkx as nx  # noqa: E402
from scipy import stats  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor as HGB  # noqa: E402

QUICK = "--quick" in sys.argv
HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("GAP_DATA", os.path.join(os.environ["TEMP"], "gap_work", "data")))
FILES = DATA / "cc_lt_int" / "x" / "lt_interventions_standard_v1"
SEED = 20261107
ALPHA = .05
OUT = HERE / ("E1_outputs_quick.json" if QUICK else "E1_outputs.json")
res: dict = {"meta": {"seed": SEED, "quick": QUICK, "alpha": ALPHA}}


def save():
    OUT.write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")


def load_graph(cols):
    e = json.load(open(HERE / "causal_chamber_ground_truth_edges.json"))["lt_standard"]
    g = nx.DiGraph()
    g.add_nodes_from(cols)
    g.add_edges_from([(a, b) for a, b in e if a in cols and b in cols])
    return g


def fisher(x, y, Z):
    n = len(x)
    A = np.column_stack([np.ones(n)] + ([Z] if Z is not None and Z.size else []))
    Q, _ = np.linalg.qr(A)
    rx = x - Q @ (Q.T @ x)
    ry = y - Q @ (Q.T @ y)
    den = math.sqrt(float(rx @ rx) * float(ry @ ry))
    if den < 1e-12:
        return 1.0, 0.0
    r = float(rx @ ry) / den
    r = max(min(r, .9999999), -.9999999)
    df = n - A.shape[1] - 1
    return float(math.erfc(abs(math.atanh(r)) * math.sqrt(max(df, 1)) / math.sqrt(2))), r


def cf_resid(y, Z, rng, folds=2):
    n = len(y)
    if Z is None or Z.size == 0:
        return y - y.mean()
    idx = rng.permutation(n)
    out = np.zeros(n)
    for k in range(folds):
        te = idx[k::folds]
        tr = np.setdiff1d(idx, te, assume_unique=False)
        m = HGB(max_iter=150, learning_rate=.1, max_leaf_nodes=31, random_state=int(rng.integers(1 << 30)))
        m.fit(Z[tr], y[tr])
        out[te] = y[te] - m.predict(Z[te])
    return out


def gcm_from_resid(rx, ry):
    R = rx * ry
    s = R.std()
    if s < 1e-12:
        return 1.0, 0.0
    t = math.sqrt(len(R)) * R.mean() / s
    d = math.sqrt(float(rx @ rx) * float(ry @ ry))
    return float(math.erfc(abs(t) / math.sqrt(2))), float(rx @ ry) / max(d, 1e-12)


def gcm(x, y, Z, rng):
    return gcm_from_resid(cf_resid(x, Z, rng), cf_resid(y, Z, rng))


def queries(g, actuators, sensors):
    qs = {k: [] for k in ("N1", "N2", "N2c", "N3", "P")}
    for i, a in enumerate(actuators):
        for b in actuators[i + 1:]:
            qs["N1"].append((a, b, ()))
    for a in actuators:
        for y in sensors:
            pa = tuple(sorted(g.predecessors(y)))
            if a in nx.ancestors(g, y):
                if a in pa:
                    qs["P"].append((a, y, tuple(p for p in pa if p != a)))
                continue
            assert nx.is_d_separator(g, {a}, {y}, set())
            qs["N2"].append((a, y, ()))
            assert nx.is_d_separator(g, {a}, {y}, set(pa))
            qs["N2c"].append((a, y, pa))
    for i, y1 in enumerate(sensors):
        for y2 in sensors[i + 1:]:
            pa = tuple(sorted(set(g.predecessors(y1)) | set(g.predecessors(y2))))
            assert nx.is_d_separator(g, {y1}, {y2}, set(pa))
            qs["N3"].append((y1, y2, pa))
    return qs


def main():
    t00 = time.time()
    rng = np.random.default_rng(SEED)
    d = pd.read_csv(FILES / "uniform_reference.csv")
    meta = ("timestamp", "config", "counter", "flag", "intervention", "camera", "v_board", "v_reg")
    varying = [c for c in d.columns if c not in meta and d[c].std() > 0]
    print("varying columns:", varying, flush=True)
    g = load_graph(varying)
    roots = [v for v in varying if g.in_degree(v) == 0]
    actuators = [v for v in roots if g.out_degree(v) > 0]
    sensors = [v for v in varying if g.in_degree(v) > 0]
    print("actuators", actuators, "\nsensors", sensors, "\nisolated", [v for v in varying if g.degree(v) == 0], flush=True)
    assert nx.is_directed_acyclic_graph(g)
    qs = queries(g, actuators, sensors)
    print({k: len(v) for k, v in qs.items()}, flush=True)
    res["design"] = {"varying": varying, "actuators": actuators, "sensors": sensors, "n_queries": {k: len(v) for k, v in qs.items()}, "n_rows": len(d)}
    X = {c: d[c].to_numpy(float) for c in varying}
    X = {c: (v - v.mean()) / v.std() for c, v in X.items()}
    N = len(d)
    ns = (1000, 10000) if QUICK else (250, 500, 1000, 2000, 4000, 7000, 10000)

    # Part 1a: Fisher z, all n, many subsamples
    print("\n=== part 1: Fisher z ===", flush=True)
    fz = {}
    for cls, Q in qs.items():
        fz[cls] = {}
        for n in ns:
            reps = 1 if n == N else (3 if QUICK else 30)
            rej = 0
            rs = []
            for _ in range(reps):
                idx = np.arange(N) if n == N else rng.choice(N, n, replace=False)
                for a, b, S in Q:
                    Z = np.column_stack([X[s][idx] for s in S]) if S else None
                    p, r = fisher(X[a][idx], X[b][idx], Z)
                    rej += p < ALPHA
                    rs.append(abs(r))
            fz[cls][n] = {"reject": rej / (reps * len(Q)), "median_abs_r": float(np.median(rs))}
        print(cls, {n: round(v["reject"], 3) for n, v in fz[cls].items()}, flush=True)
    res["fisher"] = fz
    save()

    # Part 1b: GCM, fewer n and replicates
    print("\n=== part 1: GCM ===", flush=True)
    gn = (1000, 10000) if QUICK else (1000, 4000, 10000)
    gc = {}
    detail = {}
    for cls in ("N1", "N2", "N2c", "N3", "P"):
        Q = qs[cls]
        if QUICK:
            Q = Q[:8]
        gc[cls] = {}
        for n in gn:
            reps = 1 if n == N else (1 if QUICK else 3)
            rej = 0
            rs = []
            rows = []
            for _ in range(reps):
                idx = np.arange(N) if n == N else rng.choice(N, n, replace=False)
                for a, b, S in Q:
                    Z = np.column_stack([X[s][idx] for s in S]) if S else None
                    p, r = gcm(X[a][idx], X[b][idx], Z, rng)
                    rej += p < ALPHA
                    rs.append(abs(r))
                    rows.append((a, b, len(S), p, r))
            gc[cls][n] = {"reject": rej / (reps * len(Q)), "median_abs_r": float(np.median(rs)), "median_abs_r_rejected": float(np.median([abs(x[4]) for x in rows if x[3] < ALPHA])) if any(x[3] < ALPHA for x in rows) else None}
            if n == N:
                detail[cls] = rows
            print(cls, n, {k: (round(v, 3) if v is not None else None) for k, v in gc[cls][n].items()}, f"{time.time() - t00:.0f}s", flush=True)
            res["gcm"] = gc
            save()
    res["gcm_detail_n10000"] = detail
    save()

    # Part 2: mechanism checks at full n, GCM, N3 and N2c
    print("\n=== part 2: mechanism checks at n = 10000 ===", flush=True)
    t = d["timestamp"].to_numpy(float)
    t = (t - t.mean()) / t.std()
    mech = {}
    for cls in ("N2c", "N3"):
        Q = qs[cls][:8] if QUICK else qs[cls]
        rej_t = rej_perm = rej_block = 0
        acx = []
        for a, b, S in Q:
            Z = np.column_stack([X[s] for s in S]) if S else None
            Zt = np.column_stack([Z, t]) if Z is not None else t[:, None]
            rx = cf_resid(X[a], Zt, rng)
            ry = cf_resid(X[b], Zt, rng)
            p, _ = gcm_from_resid(rx, ry)
            rej_t += p < ALPHA
            rej_perm += gcm_from_resid(rx[rng.permutation(N)], ry)[0] < ALPHA
            acx.append(float(np.corrcoef(rx[:-1], rx[1:])[0, 1]))
            # block-robust variance for GCM: means over blocks of 100 consecutive rows
            R = rx * ry
            blocks = R[: N - N % 100].reshape(-1, 100).mean(1)
            tb = math.sqrt(len(blocks)) * blocks.mean() / max(blocks.std(ddof=1), 1e-12)
            rej_block += math.erfc(abs(tb) / math.sqrt(2)) < ALPHA
        mech[cls] = {"reject_with_time_control": rej_t / len(Q), "reject_permutation_placebo": rej_perm / len(Q), "reject_block_variance": rej_block / len(Q), "median_lag1_autocorr_resid": float(np.median(acx))}
        print(cls, mech[cls], f"{time.time() - t00:.0f}s", flush=True)
    res["mechanism"] = mech
    save()

    # Part 3: interventional confirmation of supposed non-effects
    print("\n=== part 3: interventional check of the ground truth ===", flush=True)
    rows = []
    ref = d
    for f in sorted(glob.glob(str(FILES / "uniform_*.csv"))):
        name = os.path.basename(f)[8:-4]
        if name == "reference":
            continue
        di = pd.read_csv(f)
        changed = [c for c in varying + [v for v in ("osr_c", "v_c", "osr_angle_1", "osr_angle_2", "v_angle_1", "v_angle_2", "diode_ir_1", "diode_vis_1", "diode_ir_2", "diode_vis_2", "diode_ir_3", "diode_vis_3", "t_ir_1", "t_vis_1", "t_ir_2", "t_vis_2", "t_ir_3", "t_vis_3") if v in ref] if ref[c].std() == 0 and di[c].iloc[0] != ref[c].iloc[0] or (c in ref and abs(di[c].mean() - ref[c].mean()) / max(ref[c].std(), 1e-9) > 3 and c in actuators)]
        full = json.load(open(HERE / "causal_chamber_ground_truth_edges.json"))["lt_standard"]
        gf = nx.DiGraph(full)
        targets = [c for c in changed if c in gf]
        if not targets:
            rows.append(dict(file=name, targets=[], note="no target identified"))
            continue
        desc = set().union(*[nx.descendants(gf, c) for c in targets])
        for y in sensors:
            ks = stats.ks_2samp(ref[y].to_numpy(float), di[y].to_numpy(float))
            sd = ref[y].std()
            rows.append(dict(file=name, targets=targets, sensor=y, descendant=y in desc, ks_p=float(ks.pvalue), ks_d=float(ks.statistic), mean_shift_sd=float((di[y].mean() - ref[y].mean()) / sd), n=len(di)))
    res["interventional"] = rows
    R = pd.DataFrame([r for r in rows if "sensor" in r])
    if len(R):
        for desc, grp in R.groupby("descendant"):
            print("descendant" if desc else "NOT descendant", "pairs", len(grp), "KS reject", round((grp.ks_p < ALPHA).mean(), 3), "median |mean shift, SD|", round(grp.mean_shift_sd.abs().median(), 3), "median KS D", round(grp.ks_d.median(), 3), flush=True)
        res["interventional_summary"] = {("descendant" if k else "not_descendant"): {"pairs": len(v), "ks_reject": float((v.ks_p < ALPHA).mean()), "median_abs_shift_sd": float(v.mean_shift_sd.abs().median()), "median_ks_d": float(v.ks_d.median())} for k, v in R.groupby("descendant")}
    save()

    # Rule L1
    nq = N
    valid = all(fz["N1"][n]["reject"] <= .10 for n in fz["N1"]) and all(gc["N1"][n]["reject"] <= .10 for n in gc["N1"])
    pain_classes = []
    for cls in ("N2c", "N3"):
        v = gc[cls]
        r10k, r1k = v[nq]["reject"], v[1000]["reject"]
        small = v[nq]["median_abs_r_rejected"] is not None and v[nq]["median_abs_r_rejected"] < .10
        if r10k >= .20 and r10k >= 2 * max(r1k, 1e-9) and small:
            pain_classes.append(cls)
    nopain = all(gc[c][nq]["reject"] <= .10 for c in ("N2", "N2c", "N3"))
    verdict = "TEST BROKEN" if not valid else ("PAIN" if pain_classes else ("NO PAIN" if nopain else "MIXED"))
    res["L1"] = {"control_valid": bool(valid), "pain_classes": pain_classes, "verdict": verdict}
    print("L1:", res["L1"], f"runtime {time.time() - t00:.0f}s", flush=True)
    save()


if __name__ == "__main__":
    main()
