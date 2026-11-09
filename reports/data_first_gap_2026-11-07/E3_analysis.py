"""Reads E3_results.jsonl and applies rule L3 declared in E3_internal_scores.py, on whatever is complete. A cell counts only if all 23 configurations are present for that replicate. Writes E3_summary.json."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
rows = [json.loads(x) for x in (HERE / "E3_results.jsonl").read_text(encoding="utf-8").splitlines()]
err = [r for r in rows if "error" in r]
d = pd.DataFrame([r for r in rows if "error" not in r]).drop_duplicates(["data", "n", "rep", "algo", "param"])
print("records", len(rows), "errors", len(err), err[:2])
cover = d.groupby(["data", "n", "rep"]).size().rename("configs").reset_index()
print(cover.to_string())
d["cfg"] = d.algo + "_" + d.param.astype(str)
d = d.merge(cover, on=["data", "n", "rep"])
complete = d[d.configs >= 23].copy()
SCORES = {"stability": 1, "heldout": 1, "bic": 1, "lovo": -1}
out = {"coverage": cover.to_dict("records"), "cells": []}
for (data, n), g in complete.groupby(["data", "n"]):
    line = {"data": data, "n": int(n), "reps": int(g.rep.nunique())}
    regrets, gains, rhos, picked = {}, {}, {}, {}
    for s, sign in SCORES.items():
        rg, gn, rh, pk = [], [], [], []
        for rep, h in g.groupby("rep"):
            h = h.dropna(subset=[s])
            if len(h) < 10:
                continue
            best = h.f1.max()
            pick = h.loc[(sign * h[s]).idxmax()]
            default = h[h.cfg == "GES_1.0"].f1
            rg.append(best - pick.f1)
            gn.append(pick.f1 - (default.iloc[0] if len(default) else np.nan))
            rh.append(spearmanr(sign * h[s], h.f1).statistic)
            pk.append(pick.cfg)
        if rg:
            regrets[s], gains[s], rhos[s], picked[s] = float(np.mean(rg)), float(np.mean(gn)), float(np.mean(rh)), pk
    line.update(best_f1=float(g.groupby("rep").f1.max().mean()), median_f1=float(g.groupby("rep").f1.median().mean()), default_f1=float(g[g.cfg == "GES_1.0"].f1.mean()), regret=regrets, gain=gains, spearman=rhos, picked=picked)
    out["cells"].append(line)
    print(f"\n{data} n={n} reps={line['reps']}: best {line['best_f1']:.3f} median {line['median_f1']:.3f} default GES {line['default_f1']:.3f}")
    for s in regrets:
        print(f"  {s:10s} regret {regrets[s]:.3f} gain {gains[s]:+.3f} spearman {rhos[s]:+.2f} picks {picked[s]}")
ch = {c["n"]: c for c in out["cells"] if c["data"] == "chamber"}
verdict = "NOT EVALUABLE"
if 4000 in ch and 8000 in ch:
    ss = [s for s in SCORES if s in ch[4000]["regret"] and s in ch[8000]["regret"]]
    pain = all(ch[n]["regret"][s] >= .10 and ch[n]["gain"][s] < .02 for s in ss for n in (4000, 8000))
    nop = any(all(ch[n]["regret"][s] < .05 for n in (4000, 8000)) for s in ss)
    verdict = "PAIN" if pain else ("NO PAIN" if nop else "MIXED")
elif 4000 in ch:
    verdict = "NOT EVALUABLE by L3: n = 8000 incomplete. n = 4000 only is reported as partial evidence"
print("\nL3:", verdict)
out["L3"] = verdict
print("\nby configuration, chamber: precision, recall, F1, edges per n")
c = d[d.data == "chamber"].groupby(["algo", "param", "n"])[["prec", "rec", "f1", "k"]].mean().round(3).unstack("n")
pd.set_option("display.width", 260, "display.max_columns", 40)
print(c.to_string())
out["by_config_chamber"] = {str(k): {str(a): float(b) for a, b in v.items() if not pd.isna(b)} for k, v in c.to_dict("index").items()}
(HERE / "E3_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
