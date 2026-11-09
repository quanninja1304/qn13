"""Reads E2_results.jsonl and applies rule L2 declared in E2_graph_level_real_data.py. Writes E2_summary.json."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
rows = [json.loads(x) for x in (HERE / "E2_results.jsonl").read_text(encoding="utf-8").splitlines()]
errs = [r for r in rows if "error" in r]
print("records", len(rows), "errors", len(errs), errs[:3])
d = pd.DataFrame([{k: v for k, v in r.items() if k != "edges"} for r in rows if "error" not in r]).drop_duplicates(["data", "n", "rep", "method"])
algos = ["PC_0.05", "PC_0.01", "PC_0.001", "GES", "GRaSP", "BOSS", "DirectLiNGAM"]
out = {"table": {}, "flags": {}}
pd.set_option("display.width", 250)
for data, dd in d.groupby("data", sort=False):
    print("\n=====", data)
    for metric in ("f1", "prec", "rec", "k", "orient"):
        t = dd.pivot_table(index="method", columns="n", values=metric, aggfunc="mean").reindex([m for m in algos + ["CorrBH", "PCorrBH", "Empty"] if m in dd.method.unique()])
        print(f"\n{metric}\n" + t.round(3).to_string())
        out["table"].setdefault(data, {})[metric] = {str(k): {str(a): (None if pd.isna(b) else float(b)) for a, b in v.items()} for k, v in t.to_dict("index").items()}
    if "corrk_f1" in dd:
        t = dd.dropna(subset=["corrk_f1"]).pivot_table(index="method", columns="n", values="corrk_f1", aggfunc="mean")
        print("\npaired CorrK F1\n" + t.round(3).to_string())
        t2 = dd.dropna(subset=["random_f1"]).pivot_table(index="method", columns="n", values="random_f1", aggfunc="mean")
        print("\nRandomK F1 (expected)\n" + t2.round(3).to_string())
        out["table"][data]["corrk_f1"] = {str(k): {str(a): float(b) for a, b in v.items()} for k, v in t.to_dict("index").items()}
    mx = int(dd.n.max())
    last = dd[dd.n == mx].groupby("method").mean(numeric_only=True)
    best_alg = last.reindex(algos).f1.max()
    best_base = max(last.f1.get("CorrBH", 0), last.f1.get("PCorrBH", 0), last.reindex(algos).corrk_f1.max())
    flags = {"best_alg_f1": float(best_alg), "best_baseline_f1": float(best_base), "NO_SKILL": bool(best_alg - best_base < .05)}
    if data == "chamber":
        for m in ("PC_0.05", "GES"):
            a = dd[(dd.method == m) & (dd.n == 1000)][["prec", "rec"]].mean()
            b = dd[(dd.method == m) & (dd.n == mx)][["prec", "rec"]].mean()
            flags[f"REVERSAL_{m}"] = bool(a.prec - b.prec >= .10 and b.rec - a.rec < .10)
            flags[f"{m}_prec_1000_to_max"] = [float(a.prec), float(b.prec)]
            flags[f"{m}_rec_1000_to_max"] = [float(a.rec), float(b.rec)]
        s = []
        for m in algos:
            f2 = dd[(dd.method == m) & (dd.n == 2000)].f1.mean()
            fm = dd[(dd.method == m) & (dd.n == mx)].f1.mean()
            s.append(bool(abs(fm - f2) < .02 and fm < .90))
        flags["SATURATED_all"] = all(s)
    out["flags"][data] = flags
    print("\nflags:", flags)
print("\nmean seconds:\n" + d.groupby("method").secs.mean().round(2).to_string())
(HERE / "E2_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
