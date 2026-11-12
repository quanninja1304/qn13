"""P-A analysis per PA_PB_reading_rules_vi.md section 4.5-4.6 and section 7 items 15-17. Committed before any LLM call.

Run only after all three families have finished (rule 17).
Usage: python -P -E PA_analysis.py <artifacts/llm_prior_p17>

Definitions fixed here:
- Q-GRAPH parse: lines "X -> Y" (bullets/backticks tolerated); names mapped back to the observed variables (PSEUDO via the
  prompt's name_map); unknown names and self-loops are dropped and counted. A response is "parsable" if it yields >= 1 valid
  edge and >= 90% of non-empty lines are valid edges (RA0 needs >= 90% parsable responses per family x format).
- FP_B, FP_N, FP_I: share of ALL pairs of that class in the unit (not only the Q-PAIR sample) that have an edge in either
  direction in the guessed graph. TP_D / Rev_D: share of D pairs with the edge in the true ancestral / reversed direction.
- Q-PAIR: first letter a-e; (a)/(b) mapped to the named direction. FP_B^pair = share of sampled B pairs answered a or b.
- Unit -> network mean -> mean over networks; 95% percentile bootstrap over networks, 2000 resamples, seed 20261112.
  DeltaFP uses only units that have both B and N pairs. RA2 and RA3 are paired within unit.
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from p17_common import classify_pairs, mag_from_dag, parse_bif  # noqa: E402

FAMILIES = ["openai", "deepseek", "llama"]
SEED, B = 20261112, 2000
LETTER = re.compile(r"^\W*\(?([a-eA-E])\b")
EDGE = re.compile(r"^\s*[-*\d.)]*\s*`?([^`\s][^`]*?)`?\s*->\s*`?([^`]*?)`?\s*$")


def family_file(raw_dir, fam):
    if fam == "deepseek":
        cands = [raw_dir / "deepseek_official.jsonl", raw_dir / "deepseek_openrouter.jsonl"]
        present = [c for c in cands if c.exists()]
        if len(present) > 1:
            raise RuntimeError("both DeepSeek channels have data; rule 15 forbids mixing channels")
        return present[0] if present else None
    p = raw_dir / f"{fam}.jsonl"
    return p if p.exists() else None


def parse_graph(text, name_map):
    inv = {v.lower(): k for k, v in name_map.items()}
    lines = [ln for ln in (text or "").splitlines() if ln.strip()]
    edges, bad = set(), 0
    for ln in lines:
        m = EDGE.match(ln)
        if not m:
            bad += 1
            continue
        a, b = inv.get(m.group(1).strip().strip('"').lower()), inv.get(m.group(2).strip().strip('"').lower())
        if a is None or b is None or a == b:
            bad += 1
            continue
        edges.add((a, b))
    parsable = bool(edges) and (len(lines) - bad) >= 0.9 * len(lines)
    return edges, parsable


def boot_ci(per_net, stat=lambda xs: sum(xs) / len(xs)):
    nets = sorted(per_net)
    if not nets:
        return None, (None, None)
    est = stat([per_net[n] for n in nets])
    rng = random.Random(SEED)
    bs = sorted(stat([per_net[rng.choice(nets)] for _ in nets]) for _ in range(B))
    return est, (bs[int(0.025 * B)], bs[int(0.975 * B) - 1])


def net_means(unit_vals, unit_net):
    acc = defaultdict(list)
    for u, v in unit_vals.items():
        if v is not None:
            acc[unit_net[u]].append(v)
    return {n: sum(v) / len(v) for n, v in acc.items()}


def main():
    root = Path(sys.argv[1])
    prompts = [json.loads(line) for line in (root / "pa_prompts.jsonl").read_text(encoding="utf-8").splitlines()]
    pid = {f'{p["unit"]}|{p["cond"]}|{p["format"]}|{p.get("pair_index", "-")}': p for p in prompts}
    stats = json.loads((HERE / "PA_prompt_stats.json").read_text(encoding="utf-8"))
    truth, unit_net = {}, {}
    for u in stats["units"]:
        g = parse_bif(root / "bnlearn" / f'{u["network"]}.bif')
        obs = [v for v in g.nodes if v not in set(u["latent"])]
        mag = mag_from_dag(g, obs)
        anc = {v: __import__("networkx").ancestors(g, v) for v in obs}
        truth[u["unit"]] = {"classes": classify_pairs(g, obs, mag), "anc": anc}
        unit_net[u["unit"]] = u["network"]
    out = {"families": {}}
    for fam in FAMILIES:
        f = family_file(root / "llm_raw", fam)
        if f is None:
            out["families"][fam] = {"status": "no data"}
            continue
        recs = [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines()]
        recs = [r for r in recs if r["status"] == "ok"]
        res = {"file": f.name, "n_ok": len(recs)}
        parse = {k: [0, 0] for k in ("Q-GRAPH", "Q-PAIR")}
        m = {cond: defaultdict(dict) for cond in ("KEEP", "PSEUDO")}
        pair_ans = {cond: defaultdict(lambda: defaultdict(list)) for cond in ("KEEP", "PSEUDO")}
        for r in recs:
            p = pid[r["id"]]
            if p["format"] == "Q-GRAPH":
                edges, ok = parse_graph(r["text"], p["name_map"])
                parse["Q-GRAPH"][1] += 1
                parse["Q-GRAPH"][0] += ok
                if not ok:
                    continue
                t = truth[p["unit"]]
                und = {frozenset(e) for e in edges}
                cls = defaultdict(list)
                for pair, c in t["classes"].items():
                    cls[c].append(pair)
                fp = lambda c: (sum(pr in und for pr in cls[c]) / len(cls[c])) if cls[c] else None  # noqa: E731
                tp = rev = 0
                for pr in cls["D"]:
                    a, b = tuple(pr)
                    x, y = (a, b) if a in t["anc"][b] else (b, a)
                    tp += (x, y) in edges
                    rev += (y, x) in edges
                nD = len(cls["D"]) or None
                m[p["cond"]][p["unit"]] = {"FP_B": fp("B"), "FP_N": fp("N"), "FP_I": fp("I"),
                                           "TP_D": tp / nD if nD else None, "Rev_D": rev / nD if nD else None}
            else:
                mt = LETTER.match((r["text"] or "").strip())
                parse["Q-PAIR"][1] += 1
                parse["Q-PAIR"][0] += mt is not None
                if mt:
                    pair_ans[p["cond"]][p["unit"]][p["true_class"]].append(mt.group(1).lower())
        res["parse_rate"] = {k: (v[0] / v[1] if v[1] else None) for k, v in parse.items()}
        res["RA0"] = {k: (v is not None and v >= 0.9) for k, v in res["parse_rate"].items()}

        def unit_metric(cond, key):
            return {u: d.get(key) for u, d in m[cond].items()}

        def dfp(cond):
            return {u: (d["FP_B"] - d["FP_N"]) if d.get("FP_B") is not None and d.get("FP_N") is not None else None
                    for u, d in m[cond].items()}
        dk, dp = dfp("KEEP"), dfp("PSEUDO")
        est, ci = boot_ci(net_means(dk, unit_net))
        res["RA1"] = {"DeltaFP_KEEP": est, "ci95": ci, "pass": bool(est is not None and est >= 0.10 and ci[0] > 0)}
        diff = {u: dk[u] - dp[u] for u in dk if dk.get(u) is not None and dp.get(u) is not None}
        e2, c2 = boot_ci(net_means(diff, unit_net))
        res["RA2"] = {"DeltaFP_PSEUDO": boot_ci(net_means(dp, unit_net))[0], "KEEP_minus_PSEUDO": e2, "ci95": c2,
                      "pass": bool(e2 is not None and c2[0] > 0)}
        fpb_pair = {u: (sum(a in ("a", "b") for a in d["B"]) / len(d["B"])) if d.get("B") else None
                    for u, d in pair_ans["KEEP"].items()}
        fpb_graph = unit_metric("KEEP", "FP_B")
        d3 = {u: fpb_graph[u] - fpb_pair[u] for u in fpb_pair if fpb_pair[u] is not None and fpb_graph.get(u) is not None}
        e3, c3 = boot_ci(net_means(d3, unit_net))
        res["RA3"] = {"FP_B_graph_minus_pair": e3, "ci95": c3,
                      "verdict": "FIXABLE BY ASKING" if (e3 is not None and e3 >= 0.10 and c3[0] > 0) else "NOT FIXABLE BY ASKING"}
        ra4 = {}
        for cond in ("KEEP", "PSEUDO"):
            for key in ("FP_B", "FP_N", "FP_I", "TP_D", "Rev_D"):
                ra4[f"{cond}|{key}"] = boot_ci(net_means(unit_metric(cond, key), unit_net))
            dist = defaultdict(lambda: defaultdict(int))
            for u, d in pair_ans[cond].items():
                for c, answers in d.items():
                    for a in answers:
                        dist[c][a] += 1
            ra4[f"{cond}|Q-PAIR_answer_distribution_by_true_class"] = {c: dict(v) for c, v in dist.items()}
        ra4["per_network_TP_D"] = {cond: net_means(unit_metric(cond, "TP_D"), unit_net) for cond in ("KEEP", "PSEUDO")}
        res["RA4"] = ra4
        res["valid_for_RA1"] = res["RA0"]["Q-GRAPH"]
        out["families"][fam] = res
    valid = [f for f in FAMILIES if out["families"][f].get("valid_for_RA1")]
    passes = [f for f in valid if out["families"][f]["RA1"]["pass"] and out["families"][f]["RA2"]["pass"]]
    raw_pass = [f for f in valid if out["families"][f]["RA1"]["pass"]]
    need = 2
    if len(valid) == 3:
        verdict = "H-TYPE CONFIRMED" if len(passes) >= need else ("INCONCLUSIVE (RA2)" if len(raw_pass) >= need else "H-TYPE NOT CONFIRMED")
    elif len(valid) == 2:
        verdict = "H-TYPE CONFIRMED" if len(passes) == 2 else ("INCONCLUSIVE (RA2)" if len(raw_pass) == 2 else "H-TYPE NOT CONFIRMED")
    else:
        verdict = "NOT READABLE (fewer than two valid families)"
    out["decision"] = {"valid_families": valid, "RA1_pass": raw_pass, "RA1_and_RA2_pass": passes, "verdict": verdict}
    (HERE / "PA_analysis_outputs.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps(out["decision"], indent=1))
    for fam in FAMILIES:
        r = out["families"][fam]
        print(fam, {k: r.get(k) for k in ("n_ok", "parse_rate", "RA1", "RA2", "RA3")})


if __name__ == "__main__":
    main()
