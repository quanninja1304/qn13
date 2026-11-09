"""Analysis of T4L_pilot_results.jsonl by the K8 rule declared in T4L_algorithm_pilot.py. Written before the full run finished. Writes T4L_pilot_summary.json.

Run: python -P -E T4L_pilot_analysis.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
recs = [json.loads(x) for x in (HERE / "T4L_pilot_results.jsonl").read_text(encoding="utf-8").splitlines()]
main = [r for r in recs if r["stratum"] == "main"]
mv = [r for r in recs if r["stratum"] == "mvpc"]
METHODS = ["LW", "Naive", "M1", "LiftG1", "LiftG2", "PP", "PPL2", "Flag", "MI", "FCI-R"]
rng = np.random.default_rng(20261112)


def fals(m):
    return m["NA_f"] + m["A_f"]


def true(m):
    return m["NA_t"] + m["A_t"]


def pooled(mech, method_a, method_b, kind, ps=(10, 20), boot=None):
    """Average over p of the ratio of mean counts, method_a over method_b, on cells with this mech. boot: list of index arrays per p."""
    out = []
    for i, p in enumerate(ps):
        rows = [r for r in main if r["cell"][0] == p and r["cell"][1] == mech and method_a in r["methods"] and method_b in r["methods"]]
        fn = fals if kind == "false" else true
        a = np.array([fn(r["methods"][method_a]) for r in rows], float)
        b = np.array([fn(r["methods"][method_b]) for r in rows], float)
        if boot is not None:
            idx = boot[i]
            a, b = a[idx], b[idx]
        out.append(a.mean() / max(b.mean(), 1e-9))
    return float(np.mean(out))


def bootstrap(mech, a, b, kind, ps=(10, 20), B=4000):
    ns = [sum(1 for r in main if r["cell"][0] == p and r["cell"][1] == mech) for p in ps]
    vals = []
    for _ in range(B):
        idx = [rng.integers(0, n, n) for n in ns]
        vals.append(pooled(mech, a, b, kind, ps, idx))
    return [float(np.quantile(vals, .025)), float(np.quantile(vals, .975))]


summary = {"n_records": len(recs), "n_main": len(main), "n_mvpc": len(mv)}
print("records", len(recs), "main", len(main), "mvpc", len(mv))

# Cell table
cells = {}
for r in main:
    cells.setdefault(tuple(r["cell"]), []).append(r)
table = []
print("\ncell | graphs | listwise rows | method: false/true orientation claims per graph, false no-edge claims")
for cell in sorted(cells, key=lambda c: (c[0], ["mixed", "add", "mcar"].index(c[1]), c[2], c[3])):
    rows = cells[cell]
    d = {"cell": list(cell), "graphs": len(rows), "listwise_rows": float(np.mean([r["listwise_rows"] for r in rows]))}
    for m in METHODS:
        vals = [r["methods"][m] for r in rows if m in r["methods"]]
        if vals:
            d[m] = dict(false=float(np.mean([fals(v) for v in vals])), true=float(np.mean([true(v) for v in vals])), NE_f=float(np.mean([v["NE_f"] for v in vals])), NE_t=float(np.mean([v["NE_t"] for v in vals])))
    table.append(d)
    print(cell, len(rows), round(d["listwise_rows"]), " ".join(f"{m}={d[m]['false']:.1f}/{d[m]['true']:.1f}" for m in METHODS if m in d))
summary["cells"] = table

print("\nno-edge claims, false/true per graph")
for d in table:
    print(tuple(d["cell"]), " ".join(f"{m}={d[m]['NE_f']:.2f}/{d[m]['NE_t']:.1f}" for m in METHODS if m in d))

# K8
L = "LiftG2"
ra = pooled("mixed", L, "M1", "false")
ca = bootstrap("mixed", L, "M1", "false")
rb = pooled("mixed", L, "M1", "true")
cb = bootstrap("mixed", L, "M1", "true")
a_ok = ra <= .70 and ca[1] < 1
b_ok = rb >= .90
ties = {}
for bl in ["LW", "Naive", "Flag", "PP", "MI", "FCI-R"]:
    ps = (10,) if bl == "FCI-R" else (10, 20)
    f = pooled("mixed", bl, L, "false", ps)
    t = pooled("mixed", bl, L, "true", ps)
    ties[bl] = dict(false_ratio=f, true_ratio=t, ties_or_beats=bool(f <= 1.1 and t >= .95))
c_ok = not any(v["ties_or_beats"] for v in ties.values())
verdict = "GO" if a_ok and b_ok and c_ok else ("NO-GO" if (not a_ok or not c_ok) else "WEAK")
print(f"\nK8 mixed cells, LiftG2 over M1: false ratio {ra:.3f} CI {ca}, true ratio {rb:.3f} CI {cb}")
print("baselines over LiftG2:", ties)
print(f"(a) {a_ok} (b) {b_ok} (c) {c_ok} -> {verdict}")
summary["K8"] = dict(false_ratio=ra, false_ci=ca, true_ratio=rb, true_ci=cb, a=a_ok, b=b_ok, c=c_ok, baselines=ties, verdict=verdict)

# Secondary
sec = {}
for mech in ("mixed", "add", "mcar"):
    for a, b in (("LiftG2", "M1"), ("LiftG1", "M1"), ("PPL2", "PP"), ("PP", "M1"), ("PPL2", "M1"), ("Flag", "M1"), ("MI", "M1"), ("LW", "M1"), ("Naive", "M1")):
        sec[f"{mech}: {a} over {b}"] = dict(false=pooled(mech, a, b, "false"), true=pooled(mech, a, b, "true"))
    for p in (10, 20):
        sec[f"{mech} p={p}: LiftG2 over M1"] = dict(false=pooled(mech, "LiftG2", "M1", "false", (p,)), true=pooled(mech, "LiftG2", "M1", "true", (p,)))
print("\nsecondary ratios (false, true)")
for k, v in sec.items():
    print(f"  {k}: {v['false']:.3f} {v['true']:.3f}")
summary["secondary"] = sec

# Precision of orientation claims
print("\nprecision of orientation claims, pooled by mech and p")
prec = {}
for mech in ("mixed", "add", "mcar"):
    for p in (10, 20):
        rows = [r for r in main if r["cell"][0] == p and r["cell"][1] == mech]
        line = {}
        for m in METHODS:
            vals = [r["methods"][m] for r in rows if m in r["methods"]]
            if vals:
                f, t = sum(fals(v) for v in vals), sum(true(v) for v in vals)
                line[m] = dict(false=f / len(vals), true=t / len(vals), precision=t / max(t + f, 1))
        prec[f"{mech} p={p}"] = line
        print(f"  {mech} p={p}: " + " ".join(f"{m}={line[m]['precision']:.3f}({line[m]['true']:.1f})" for m in line))
summary["precision"] = prec

# Per-cell verdict of (a), (b) for mixed
print("\nper mixed cell LiftG2/M1 false, true")
for d in table:
    if d["cell"][1] == "mixed":
        print(" ", tuple(d["cell"]), f"{d['LiftG2']['false'] / max(d['M1']['false'], 1e-9):.2f} {d['LiftG2']['true'] / max(d['M1']['true'], 1e-9):.2f}")

# MVPC stratum
if mv:
    ms = ["LW", "Naive", "M1", "LiftG2", "PP", "PPL2", "Flag", "MI", "MVPC"]
    agg = {}
    for r in mv:
        k = r["cell"][2]
        for m in ms:
            v = r["methods"].get(m)
            if v:
                a = agg.setdefault((k, m), [0, 0, 0, 0, 0])
                a[0] += fals(v)
                a[1] += true(v)
                a[2] += v["NE_f"]
                a[3] += v["NE_t"]
                a[4] += 1
    print("\nMVPC stratum (no latents, no self-parent): false/true orientation, false/true no-edge, per graph")
    out = {}
    for (k, m), a in sorted(agg.items()):
        print(f"  {k} {m}: {a[0] / a[4]:.2f}/{a[1] / a[4]:.2f}  {a[2] / a[4]:.2f}/{a[3] / a[4]:.2f} n={a[4]}")
        out[f"{k} {m}"] = dict(false=a[0] / a[4], true=a[1] / a[4], NE_f=a[2] / a[4], NE_t=a[3] / a[4], graphs=a[4])
    summary["mvpc_stratum"] = out
secs = {}
for r in main:
    for k, v in r["secs"].items():
        secs.setdefault((r["cell"][0], k), []).append(v)
print("\nmean seconds per data set")
print({f"p={k[0]} {k[1]}": round(float(np.mean(v)), 2) for k, v in sorted(secs.items())})
summary["seconds"] = {f"p={k[0]} {k[1]}": float(np.mean(v)) for k, v in secs.items()}
(HERE / "T4L_pilot_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
