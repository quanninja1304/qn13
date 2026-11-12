"""P1 analysis for TS-G1: metrics q1-q4, runtime, and reading rules R0-R4 (TS_G1_reading_rules_vi.md, sec. 5-6,
with the clarifications logged in sec. 8 before any run).

Unit variable order: 0=a1, 1=a2, 2=b1, 3=b2 (true edges a1->a2, b1->b2), 4=rain_a, 5=rain_b (condition O only).
Usage: python -P -E P1_analysis.py
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
CROSS = [(0, 2), (0, 3), (1, 2), (1, 3)]
TRUE = [(0, 1), (2, 3)]
HIT_DAG = {"-->", "o-o", "x-x"}       # PCMCI+ / VAR: oriented correctly or unoriented
HIT_PAG = {"-->", "o->"}              # LPCMCI
B_BOOT, SEED = 2000, 20261109


def metrics(graph, method):
    g = np.array(graph)
    taus = range(g.shape[2])
    adj = [any(g[i, j, t] != "" or g[j, i, t] != "" for t in taus) for i, j in CROSS]
    claim = [any(g[i, j, t] == "-->" or g[j, i, t] == "-->" for t in taus) for i, j in CROSS]
    bidir = [any(g[i, j, t] == "<->" or g[j, i, t] == "<->" for t in taus) for i, j in CROSS]
    hitset = HIT_PAG if method == "lpcmci" else HIT_DAG
    rec = [any(g[i, j, t] in hitset for t in taus) for i, j in TRUE]
    return {"q1": np.mean(adj), "q2": np.mean(claim), "q3": np.mean(rec), "q4": np.mean(bidir)}


def boot_ci(x, rng):
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return [float("nan")] * 2
    idx = rng.integers(0, len(x), size=(B_BOOT, len(x)))
    m = x[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def boot_diff_unpaired(x, y, rng):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ix = rng.integers(0, len(x), size=(B_BOOT, len(x)))
    iy = rng.integers(0, len(y), size=(B_BOOT, len(y)))
    d = x[ix].mean(axis=1) - y[iy].mean(axis=1)
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def main():
    units = {u["id"]: u for u in json.loads((HERE / "P1_units.json").read_text(encoding="utf-8"))["units"]}
    rows = [json.loads(l) for l in (HERE / "P1_results.jsonl").read_text(encoding="utf-8").splitlines()]
    M = {}            # (res, cond, method, unit) -> metrics or None
    RT = {}
    status = defaultdict(lambda: defaultdict(int))
    for r in rows:
        key = (r["res"], r["cond"], r["method"], r["unit"])
        st = r["status"]
        if st == "ok" and r.get("runtime_s", 0) > 300:
            st = "timeout"
        status[(r["res"], r["cond"], r["method"])][st] += 1
        RT[key] = r.get("runtime_s", 300.0)
        M[key] = metrics(r["graph"], r["method"]) if st == "ok" else None

    rng = np.random.default_rng(SEED)
    out = {"status_counts": {"|".join(k): dict(v) for k, v in status.items()}, "tables": {}, "rules": {}}

    def vals(res, cond, method, stratum, q):
        return [M[(res, cond, method, u)][q] for u in units if units[u]["stratum"] == stratum
                and M.get((res, cond, method, u)) is not None]

    def paired(res, c1, m1, c2, m2, stratum, q):
        xs = []
        for u in units:
            if units[u]["stratum"] != stratum:
                continue
            a, b = M.get((res, c1, m1, u)), M.get((res, c2, m2, u))
            if a is not None and b is not None:
                xs.append(a[q] - b[q])
        return xs

    for res in ("6H", "24H"):
        tab = {}
        for cond in ("L", "O"):
            for method in ("var", "pcmciplus", "lpcmci"):
                for stratum in ("near", "far"):
                    k = f"{cond}|{method}|{stratum}"
                    tab[k] = {"n": len(vals(res, cond, method, stratum, "q1"))}
                    for q in ("q1", "q2", "q3", "q4"):
                        v = vals(res, cond, method, stratum, q)
                        tab[k][q] = float(np.mean(v)) if v else float("nan")
                        tab[k][q + "_ci"] = boot_ci(v, rng)
                    rts = [RT[(res, cond, method, u)] for u in units if units[u]["stratum"] == stratum
                           and (res, cond, method, u) in RT]
                    tab[k]["runtime_median_s"] = float(np.median(rts)) if rts else float("nan")
        out["tables"][res] = tab

    res = "6H"
    T = out["tables"][res]
    R = {}
    n_near = min(T[f"L|{m}|near"]["n"] for m in ("var", "pcmciplus", "lpcmci"))
    n_far = min(T[f"L|{m}|far"]["n"] for m in ("var", "pcmciplus", "lpcmci"))
    R["R0"] = {"n_near_min": n_near, "n_far_min": n_far, "pass": n_near >= 60 and n_far >= 60}

    vn, vf = vals(res, "L", "var", "near", "q1"), vals(res, "L", "var", "far", "q1")
    d1 = float(np.mean(vn) - np.mean(vf))
    ci1 = boot_diff_unpaired(vn, vf, rng)
    R["R1"] = {"var_q1_near_minus_far": d1, "ci": ci1, "pass": d1 >= 0.10 and ci1[0] > 0}

    x2 = paired(res, "L", "pcmciplus", "O", "pcmciplus", "near", "q2")
    d2 = float(np.mean(x2))
    ci2 = boot_ci(x2, rng)
    R["R2"] = {"pcmciplus_near_q2_L_minus_O": d2, "ci": ci2, "n_paired": len(x2), "pass": d2 >= 0.05 and ci2[0] > 0}

    xf = paired(res, "L", "pcmciplus", "L", "lpcmci", "near", "q2")
    xr = paired(res, "L", "pcmciplus", "L", "lpcmci", "near", "q3")
    dfalse, drec = float(np.mean(xf)), float(np.mean(xr))
    t_l = T["L|lpcmci|near"]["runtime_median_s"]
    t_p = T["L|pcmciplus|near"]["runtime_median_s"]
    n_timeout_l = status[(res, "L", "lpcmci")].get("timeout", 0)
    costly_time = t_l > 60 and t_l > 10 * t_p
    if dfalse < 0.05:
        verdict = "GAP-A"
    elif drec >= 0.10 or costly_time:
        verdict = "GAP-B"
    else:
        verdict = "NO METHOD GAP"
    R["R3"] = {"delta_false": dfalse, "delta_false_ci": boot_ci(xf, rng), "delta_recall": drec,
               "delta_recall_ci": boot_ci(xr, rng), "n_paired": len(xf),
               "runtime_median_lpcmci_s": t_l, "runtime_median_pcmciplus_s": t_p,
               "lpcmci_timeouts_L_6H": n_timeout_l, "verdict": verdict}
    sanity = {m: {"q2_near": T[f"L|{m}|near"]["q2"], "q2_far": T[f"L|{m}|far"]["q2"],
                  "far_lt_near": T[f"L|{m}|far"]["q2"] < T[f"L|{m}|near"]["q2"]}
              for m in ("var", "pcmciplus", "lpcmci")}
    R["R3_sanity"] = sanity
    R["R4_note"] = "24H tables in tables['24H']; corrected Confounder set counts in P0_outputs.json (106/1170 vs 24/361)."
    out["rules"] = R
    (HERE / "P1_analysis_outputs.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out["rules"], indent=2))
    print(json.dumps(out["status_counts"], indent=1))


if __name__ == "__main__":
    main()
