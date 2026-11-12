"""P-B runner (rules section 3): oracle FCI with one typed injected guess per run.

Synthetic: generate_dag(observed, latent_ratio, mean_degree, seed) on the grid {10, 15} x {0.2, 0.4} x {2.0, 3.0},
50 seeds per cell, seed = 20261112 + 1000 * cell + i. bnlearn: units from P0_verify_mag (hide_variables), deduplicated
by latent set (rules section 7, 12/11 clarification).

Per graph: one baseline run plus up to 5 eligible pairs per type T1..T7 (seeded per graph). Output: PB_results.jsonl
(one line per run), resumable by (source, graph_id, type, pair).

Usage: python -P -E PB_run.py <artifacts/llm_prior_p17/bnlearn> [--only synthetic|bnlearn] [--workers 3]
"""
from __future__ import annotations

import json
import multiprocessing as mp
import random
import sys
import time
from collections import deque
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "src"))

RESULTS = HERE / "PB_results.jsonl"
GRID = [(o, lr, md) for o in (10, 15) for lr in (0.2, 0.4) for md in (2.0, 3.0)]
SEEDS_PER_CELL = 50
BASE_SEED = 20261112
MAX_PAIRS = 5
NETWORKS = ["asia", "cancer", "earthquake", "survey", "sachs", "child", "insurance", "alarm", "hailfinder", "hepar2"]
HIDE_SEEDS = [1, 2, 3]
TIMEOUT_S = 600


def pair_types(adj, anc, k):
    """Eligible ordered injections per type. adj: set of (a, b) a<b adjacent in MAG."""
    D, B, I, N = [], [], [], []
    for a in range(k):
        for b in range(a + 1, k):
            a_b, b_a = a in anc[b], b in anc[a]
            if (a, b) in adj:
                if a_b:
                    D.append((a, b))
                elif b_a:
                    D.append((b, a))
                else:
                    B.append((a, b))
            elif a_b:
                I.append((a, b))
            elif b_a:
                I.append((b, a))
            else:
                N.append((a, b))
    return D, B, I, N


def injections_for(adj, anc, k, rng):
    D, B, I, N = pair_types(adj, anc, k)
    out = []

    def pick(lst):
        lst = sorted(lst)
        return rng.sample(lst, min(MAX_PAIRS, len(lst)))

    for a, b in pick(D):  # true a --> b
        out.append(("T1", {"kind": "directed", "a": b, "b": a}))
    for a, b in pick(B):
        x, y = (a, b) if rng.random() < 0.5 else (b, a)
        out.append(("T2", {"kind": "directed", "a": x, "b": y}))
    for a, b in pick(D):
        out.append(("T3", {"kind": "bidirected", "a": a, "b": b}))
    for a, b in pick(I):  # a ancestor of b, non-adjacent
        out.append(("T4", {"kind": "directed", "a": a, "b": b}))
    for a, b in pick(N):
        x, y = (a, b) if rng.random() < 0.5 else (b, a)
        out.append(("T5", {"kind": "directed", "a": x, "b": y}))
    for a, b in pick(D):
        out.append(("T6", {"kind": "directed", "a": a, "b": b}))
    for a, b in pick(B):
        out.append(("T7", {"kind": "bidirected", "a": a, "b": b}))
    return out, {"D": len(D), "B": len(B), "I": len(I), "N": len(N)}


def distances(adj, k, sources):
    nbr = {i: set() for i in range(k)}
    for a, b in adj:
        nbr[a].add(b)
        nbr[b].add(a)
    dist = {s: 0 for s in sources}
    q = deque(sources)
    while q:
        u = q.popleft()
        for v in nbr[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def graph_job(spec, q):
    """Run baseline + all injections for one graph; put list of records on q."""
    try:
        import networkx as nx
        from pb_fci_typed import errors, relabel, run, skeleton_and_sepsets
        if spec["source"] == "synthetic":
            from safety_prior.graphs import generate_dag
            gg = generate_dag(spec["observed"], spec["latent_ratio"], spec["mean_degree"], spec["seed"])
            dag, _ = relabel(gg.dag, gg.observed)
            k = len(gg.observed)
        else:
            from p17_common import parse_bif
            g = parse_bif(Path(spec["bif"]))
            dag, _ = relabel(g, spec["observed_names"])
            k = len(spec["observed_names"])
        adj, sep, anc = skeleton_and_sepsets(dag, k)
        rng = random.Random(spec["seed"] * 7 + 13)
        injs, counts = injections_for(adj, anc, k, rng)
        recs = []
        base = run(dag, k)
        fa, fna, _ = errors(base["M"], anc, k)
        ref_equal = None
        try:
            import contextlib
            import io
            import numpy as np
            from causallearn.search.ConstraintBased.FCI import fci
            with contextlib.redirect_stdout(io.StringIO()):
                Gref, _ = fci(np.zeros((k + 5, k)), independence_test_method="d_separation", true_dag=dag,
                              show_progress=False, node_names=[f"X{i}" for i in range(k)])
            ref_equal = bool(np.array_equal(np.array(Gref.graph, dtype=int), base["M"]))
        except Exception as e:  # noqa: BLE001
            ref_equal = f"ref_error: {type(e).__name__}: {e}"
        recs.append({**spec_key(spec), "type": "baseline", "pair": None, "FA": fa, "FNA": fna, "Prop": fa + fna,
                     "pair_counts": counts, "k": k, "n_adj": len(adj), "ref_equal_fci_oracle": ref_equal,
                     "circles": int((base["M"] == 2).sum())})
        for typ, inj in injs:
            t0 = time.perf_counter()
            r = run(dag, k, inj)
            ex = (inj["a"], inj["b"])
            fa, fna, wrong = errors(r["M"], anc, k, exclude=ex)
            d = distances(adj, k, [inj["a"], inj["b"]])
            dist = max((min(d.get(u, 99), d.get(v, 99)) for u, v in wrong), default=0)
            conflict = int(r["conflicts"]["blocked_collider"] > 0 or r["conflicts"]["added_on_sepset_pair"] > 0
                           or r["conflicts"]["override"] > 0)
            rules = {}
            for (x, y), rule in r["origin"].items():
                if (min(x, y), max(x, y)) in wrong and {x, y} != set(ex):
                    x_anc_y = x in anc[y]
                    m = int(r["M"][x, y])
                    if (m == -1 and not x_anc_y) or (m == 1 and x_anc_y):
                        rules[rule] = rules.get(rule, 0) + 1
            # injected-edge own correctness (reported, not part of Prop)
            recs.append({**spec_key(spec), "type": typ, "pair": [inj["a"], inj["b"]], "kind": inj["kind"],
                         "FA": fa, "FNA": fna, "Prop": fa + fna, "Dist": dist, "Conflict": conflict,
                         "conflicts": r["conflicts"], "Silent": int(fa + fna > 0 and conflict == 0),
                         "Rule": rules, "Skel": 0, "k": k, "runtime_s": round(time.perf_counter() - t0, 4)})
        q.put({"status": "ok", "records": recs})
    except Exception as e:  # noqa: BLE001
        import traceback
        q.put({"status": "error", "error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-1500:],
               "key": spec_key(spec)})


def spec_key(spec):
    keys = ("source", "graph_id", "observed", "latent_ratio", "mean_degree", "seed", "network", "hide_seed")
    return {k: spec[k] for k in keys if k in spec}


def build_specs(bn_root, only):
    specs = []
    if only in (None, "synthetic"):
        for c, (o, lr, md) in enumerate(GRID):
            for i in range(SEEDS_PER_CELL):
                seed = BASE_SEED + 1000 * c + i
                specs.append({"source": "synthetic", "graph_id": f"syn_{c}_{i}", "observed": o, "latent_ratio": lr,
                              "mean_degree": md, "seed": seed})
    if only in (None, "bnlearn"):
        from p17_common import hide_variables, parse_bif
        for name in NETWORKS:
            g = parse_bif(Path(bn_root) / f"{name}.bif")
            seen = set()
            for s in HIDE_SEEDS:
                h = hide_variables(g, s)
                if h["latent"] is None:
                    continue
                key = frozenset(h["latent"])
                if key in seen:
                    continue
                seen.add(key)
                specs.append({"source": "bnlearn", "graph_id": f"{name}_{s}", "network": name, "hide_seed": s,
                              "seed": BASE_SEED + 7 * s + sum(map(ord, name)), "bif": str(Path(bn_root) / f"{name}.bif"),
                              "observed_names": h["observed"]})
    return specs


def main():
    bn_root = sys.argv[1]
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 3
    specs = build_specs(bn_root, only)
    done = set()
    if RESULTS.exists():
        for line in RESULTS.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add(r["graph_id"])
    todo = [s for s in specs if s["graph_id"] not in done]
    print("graphs total", len(specs), "to run", len(todo), flush=True)
    ctx = mp.get_context("spawn")
    running = []
    n_done = 0
    with open(RESULTS, "a", encoding="utf-8") as fout, open(HERE / "PB_errors.jsonl", "a", encoding="utf-8") as ferr:
        while todo or running:
            while todo and len(running) < workers:
                s = todo.pop(0)
                q = ctx.Queue()
                p = ctx.Process(target=graph_job, args=(s, q))
                p.start()
                running.append((p, q, time.time(), s))
            still = []
            for p, q, t0, s in running:
                out = None
                try:
                    out = q.get_nowait()
                except Exception:  # noqa: BLE001
                    pass
                if out is None and time.time() - t0 > TIMEOUT_S:
                    p.terminate()
                    out = {"status": "timeout", "key": spec_key(s)}
                if out is None:
                    still.append((p, q, t0, s))
                    continue
                p.join(timeout=5)
                if out["status"] == "ok":
                    for rec in out["records"]:
                        fout.write(json.dumps(rec) + "\n")
                    fout.flush()
                else:
                    ferr.write(json.dumps({"graph_id": s["graph_id"], **out}) + "\n")
                    ferr.flush()
                n_done += 1
                if n_done % 25 == 0:
                    print("graphs done", n_done, flush=True)
            running = still
            time.sleep(0.1)
    print("all graphs finished", flush=True)


if __name__ == "__main__":
    main()
