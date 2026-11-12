"""P-B analysis per PA_PB_reading_rules_vi.md section 3.5 (RB0-RB4). Writes PB_analysis_outputs.json and prints verdicts.

Aggregation (rules section 7, clarification 8, fixed before reading any P-B metric):
- per graph and type: mean of Prop over that graph's injections of the type;
- Prop(T) = mean over graphs that have type T; DeltaL = max(Prop(T2), Prop(T3)) - Prop(T1) on synthetic graphs;
- CI: 2000 bootstrap resamples of synthetic graphs (seed 20261112), recomputing DeltaL on each resample;
- RB3 Silent share pooled over T2/T3 injections with Prop > 0.
"""
import json
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
TYPES = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
B_RESAMPLES = 2000
SEED = 20261112


def load():
    recs = [json.loads(line) for line in (HERE / "PB_results.jsonl").read_text(encoding="utf-8").splitlines()]
    errs = []
    p = HERE / "PB_errors.jsonl"
    if p.exists():
        errs = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    return recs, errs


def per_graph(recs, source):
    g = defaultdict(lambda: defaultdict(list))
    for r in recs:
        if r["source"] != source or r["type"] == "baseline":
            continue
        g[r["graph_id"]][r["type"]].append(r["Prop"])
    return {gid: {t: sum(v) / len(v) for t, v in d.items()} for gid, d in g.items()}


def type_means(pg, gids):
    out = {}
    for t in TYPES:
        vals = [pg[g][t] for g in gids if t in pg[g]]
        out[t] = (sum(vals) / len(vals)) if vals else None
    return out


def delta_l(m):
    cands = [m[t] for t in ("T2", "T3") if m[t] is not None]
    if not cands or m["T1"] is None:
        return None
    return max(cands) - m["T1"]


def pct(xs, q):
    xs = sorted(xs)
    i = q * (len(xs) - 1)
    lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def main():
    recs, errs = load()
    out = {"n_records": len(recs), "n_graph_errors_or_timeouts": len(errs)}
    base = [r for r in recs if r["type"] == "baseline"]
    # RB0
    rb0_i = [r for r in base if r["ref_equal_fci_oracle"] is not True]
    rb0_base_err = [r for r in base if r["FA"] or r["FNA"]]
    rb0_ii = [r for r in recs if r["type"] in ("T6", "T7") and (r["FA"] or r["FNA"] or r.get("Skel", 0))]
    out["RB0"] = {"n_baseline": len(base), "baseline_not_equal_ref": [(r["graph_id"], r["ref_equal_fci_oracle"]) for r in rb0_i],
                  "baseline_with_errors": [r["graph_id"] for r in rb0_base_err],
                  "T6_T7_with_errors": [(r["graph_id"], r["type"], r["pair"]) for r in rb0_ii],
                  "pass": not rb0_i and not rb0_base_err and not rb0_ii}
    # RB1 (descriptive), per source
    rb1 = {}
    for src in ("synthetic", "bnlearn"):
        rows = [r for r in recs if r["source"] == src and r["type"] in TYPES]
        rb1[src] = {}
        for t in TYPES:
            rr = [r for r in rows if r["type"] == t]
            if rr:
                rb1[src][t] = {"n_injections": len(rr), "n_graphs": len({r["graph_id"] for r in rr}),
                               "share_prop_gt0": sum(r["Prop"] > 0 for r in rr) / len(rr),
                               "mean_prop": sum(r["Prop"] for r in rr) / len(rr),
                               "mean_FA": sum(r["FA"] for r in rr) / len(rr), "mean_FNA": sum(r["FNA"] for r in rr) / len(rr),
                               "share_conflict": sum(r["Conflict"] for r in rr) / len(rr)}
    out["RB1"] = rb1
    # RB2 on synthetic
    pg = per_graph(recs, "synthetic")
    gids = sorted(pg)
    m = type_means(pg, gids)
    dl = delta_l(m)
    rng = random.Random(SEED)
    boots = []
    for _ in range(B_RESAMPLES):
        sample = [rng.choice(gids) for _ in gids]
        mb = type_means(pg, sample)
        d = delta_l(mb)
        if d is not None:
            boots.append(d)
    ci = (pct(boots, 0.025), pct(boots, 0.975))
    if dl >= 0.5 and ci[0] > 0:
        verdict = "LATENT-SPECIFIC HARM"
    elif dl < 0.5 and (ci[0] <= 0 <= ci[1] or ci[1] < 0):
        verdict = "NO LATENT-SPECIFIC HARM"
    else:
        verdict = "INCONCLUSIVE"
    out["RB2"] = {"n_graphs": len(gids), "graphs_with_T2": sum("T2" in pg[g] for g in gids), "type_means": m,
                  "argmax": max(("T2", "T3"), key=lambda t: -1e9 if m[t] is None else m[t]),
                  "DeltaL": dl, "ci95": ci, "verdict": verdict}
    # RB3
    rows = [r for r in recs if r["source"] == "synthetic" and r["type"] in ("T2", "T3") and r["Prop"] > 0]
    silent = sum(r["Silent"] for r in rows) / len(rows) if rows else None
    by_type = {t: (lambda rr: (sum(r["Silent"] for r in rr) / len(rr)) if rr else None)([r for r in rows if r["type"] == t])
               for t in ("T2", "T3")}
    out["RB3"] = {"n_propagating": len(rows), "silent_share": silent, "by_type": by_type,
                  "verdict": "SILENT" if silent is not None and silent >= 0.5 else "NOT SILENT"}
    # RB4 descriptive: rules, distance, by grid cell, overrides
    rb4 = {"rule_counts": {}, "dist_mean_given_prop": {}, "by_cell": {}, "overrides": {}}
    for t in TYPES:
        rr = [r for r in recs if r["source"] == "synthetic" and r["type"] == t]
        rc = defaultdict(int)
        for r in rr:
            for k_, v in r["Rule"].items():
                rc[k_] += v
        rb4["rule_counts"][t] = dict(rc)
        rp = [r["Dist"] for r in rr if r["Prop"] > 0]
        rb4["dist_mean_given_prop"][t] = (sum(rp) / len(rp)) if rp else None
        rb4["overrides"][t] = sum(r["conflicts"]["override"] > 0 for r in rr)
    cells = defaultdict(lambda: defaultdict(list))
    for r in recs:
        if r["source"] == "synthetic" and r["type"] in TYPES:
            cells[f'{r["observed"]}|{r["latent_ratio"]}|{r["mean_degree"]}'][r["type"]].append(r["Prop"])
    rb4["by_cell"] = {c: {t: sum(v) / len(v) for t, v in d.items()} for c, d in cells.items()}
    pgb = per_graph(recs, "bnlearn")
    rb4["bnlearn_type_means"] = type_means(pgb, sorted(pgb))
    rb4["bnlearn_n_units"] = len(pgb)
    out["RB4"] = rb4
    (HERE / "PB_analysis_outputs.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("n_records", "n_graph_errors_or_timeouts")}, indent=1))
    print("RB0", json.dumps(out["RB0"], default=str)[:1500])
    print("RB2", json.dumps(out["RB2"], default=str))
    print("RB3", json.dumps(out["RB3"], default=str))


if __name__ == "__main__":
    main()
