"""E7: does scoring against an audited reference change the conclusions? Post hoc illustration on E2 and E3 outputs; no reading rule, no new runs.

Audit of the chamber reference, from E1 and E2b, not from any algorithm's output:
  remove from the reference: the 12 LED edges, whose partial correlation is below .02 and whose gain in held-out R2 is about 0 at n = 10000. No method could find them here.
  neutral pairs: the 3 same-sensor pairs ir_i, vis_i, with conditional correlation about .7. Dependence is real, so reporting an adjacency is not an error; they count neither as true nor false positives.
Raw scoring is what a benchmark would report. Compares F1 and ranks of methods, per n, on E2 results.
Limit: audit decisions come from this same data set, so this shows how much the choice matters; it is not an independent evaluation.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import E2_graph_level_real_data as E2  # noqa: E402

_, cols, edges = E2.load_chamber()
idx = {c: i for i, c in enumerate(cols)}
sk = {(min(idx[a], idx[b]), max(idx[a], idx[b])) for a, b in edges}
led = {(min(idx[a], idx[b]), max(idx[a], idx[b])) for a, b in edges if a.startswith("l_")}
audited = sk - led
neutral = {(min(idx[f"ir_{i}"], idx[f"vis_{i}"]), max(idx[f"ir_{i}"], idx[f"vis_{i}"])) for i in (1, 2, 3)}
print("reference edges", len(sk), "LED removed", len(led), "audited", len(audited), "neutral pairs", len(neutral))
rows = []
for line in (HERE / "E2_results.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    if r["data"] != "chamber" or "edges" not in r:
        continue
    es = {(min(i, j), max(i, j)) for i, j, _ in r["edges"]}
    e2 = es - neutral
    tp = len(e2 & audited)
    p = tp / len(e2) if e2 else float("nan")
    rc = tp / len(audited)
    f = 2 * tp / (len(e2) + len(audited))
    rows.append(dict(method=r["method"], n=r["n"], raw_f1=r["f1"], raw_prec=r["prec"], raw_rec=r["rec"], aud_f1=f, aud_prec=p, aud_rec=rc))
d = pd.DataFrame(rows)
pd.set_option("display.width", 220)
t = d.groupby(["method", "n"]).mean(numeric_only=True).round(3)
for m in ("raw_f1", "aud_f1", "aud_prec", "aud_rec"):
    print(f"\n{m}\n" + t[m].unstack("n").to_string())
out = {}
for n, g in d.groupby("n"):
    a = g.groupby("method").mean(numeric_only=True)
    out[int(n)] = dict(spearman_rank_raw_vs_audited=float(spearmanr(a.raw_f1, a.aud_f1).statistic), best_raw=a.raw_f1.idxmax(), best_audited=a.aud_f1.idxmax(), raw_order=list(a.raw_f1.sort_values(ascending=False).index), audited_order=list(a.aud_f1.sort_values(ascending=False).index), ceiling_raw_recall=len(audited) / len(sk))
    print(f"\nn={n}: rank correlation raw vs audited {out[int(n)]['spearman_rank_raw_vs_audited']:.2f}\n  raw     {out[int(n)]['raw_order']}\n  audited {out[int(n)]['audited_order']}")
print("\nMax raw recall if a method found every detectable edge and nothing else:", round(len(audited) / len(sk), 3), "; raw F1 then:", round(2 * len(audited) / (len(audited) + len(sk)), 3))
(HERE / "E7_outputs.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
