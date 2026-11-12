"""P0 (descriptive only, no causal discovery) for TS-G1.

P0a: recount CausalRivers "confounder" sets two ways and compare with the paper's Table 6
     (east: confounder-3 = 24, confounder-5 = 361).
     - code variant: current public code (subgraph of n nodes containing the confounder and all its
       successors; confounder kept).
     - paper variant: subgraph of n+1 nodes containing the confounder and all its successors, then
       the confounder removed.
P0b: DWD hourly precipitation station coverage near river stations (2019-2023).
P0c: missingness of river series and distance distribution of disconnected chain pairs.

Usage: python -P -E P0_descriptive.py <artifacts/ts_causalrivers>
Pickles are read with a restricted unpickler (networkx / builtins / numpy only).
"""
import io
import json
import math
import pickle
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1])
PROD = ROOT / "product"
OUT = Path(__file__).with_name("P0_outputs.json")

ALLOWED_PREFIXES = ("networkx.", "builtins", "collections", "numpy", "copyreg", "_codecs")


class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith(ALLOWED_PREFIXES):
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"blocked class {module}.{name}")


def load_graph(path: Path) -> nx.DiGraph:
    with open(path, "rb") as f:
        return SafeUnpickler(io.BytesIO(f.read())).load()


# --- verbatim re-implementation of CausalRivers get_all_subgraphs (tools/graph_sampling_tools.py) ---
def all_extensions(current_G, G, succ=True):
    extensions = []
    for node in current_G:
        [extensions.append(x) for x in list(G.predecessors(node)) if x not in current_G]
        if succ:
            [extensions.append(x) for x in list(G.successors(node)) if x not in current_G]
    return [current_G + [ex] for ex in set(extensions)]


def get_all_subgraphs(G, n_vars=5):
    # verbatim logic from CausalRivers HEAD (lines 82-102), comments removed
    full_stack = []
    for start_node in list(G.nodes):
        no_graphs = False
        graph_stack = [[start_node]]
        for step in range(n_vars - 1):
            res = [item for sublist in [all_extensions(g, G) for g in graph_stack] for item in sublist]
            if len(res) > 0:
                graph_stack = res
            else:
                no_graphs = True
        if not no_graphs:
            full_stack.append(graph_stack)
    return list(set(tuple(sorted(i)) for i in [item for sublist in full_stack for item in sublist]))


def confounder_sets(G, n_subgraph, remove):
    conf = [x for x in G.nodes if len(list(G.successors(x))) > 1]
    potential = get_all_subgraphs(G, n_vars=n_subgraph)
    out = []
    for con in conf:
        cands = [x for x in potential if con in x]
        for succ in G.successors(con):
            cands = [x for x in cands if succ in x]
        for x in cands:
            out.append(tuple(y for y in x if (y != con or not remove)))
    return out


def haversine_km(p, q):
    lon1, lat1, lon2, lat2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def main():
    out = {}
    files = sorted(p.name for p in PROD.iterdir())
    out["product_files"] = files
    G = load_graph(PROD / "rivers_east_germany.p")
    out["east_graph"] = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(),
                         "nodes_with_>1_successor": sum(1 for x in G if G.out_degree(x) > 1)}

    # P0a. get_all_subgraphs is exponential; it is the original authors' routine and runs for n<=6 here.
    p0a = {}
    for n in (3, 5):
        code = confounder_sets(G, n, remove=False)
        paper = confounder_sets(G, n + 1, remove=True)
        p0a[f"confounder_{n}"] = {
            "paper_table6": {3: 24, 5: 361}[n],
            "code_variant_count": len(code),
            "code_variant_contains_confounder": True,
            "paper_variant_count": len(paper),
        }
        print(n, p0a[f"confounder_{n}"], flush=True)
    out["P0a"] = p0a

    # P0c. river data missingness 2019-2023 at native resolution
    header = pd.read_csv(PROD / "rivers_ts_east_germany.csv", nrows=0).columns
    ts = pd.read_csv(PROD / "rivers_ts_east_germany.csv", index_col=0,
                     dtype={c: np.float32 for c in header[1:]})
    ts.index = pd.to_datetime(ts.index)
    ts = ts.loc["2019-01-01":"2023-12-31"]
    miss = ts.isna().mean()
    out["P0c_missing"] = {"n_series": int(ts.shape[1]), "n_steps": int(ts.shape[0]),
                          "frac_series_missing_gt_10pct": float((miss > 0.10).mean()),
                          "median_missing": float(miss.median())}

    # chains = gauged edges; disconnected pairs of chains: no path between any nodes, no common ancestor
    # node attribute p is (lat, lon) in the release (README says X=longitude, data show X~53 = latitude)
    pos = {x: (G.nodes[x]["p"][1], G.nodes[x]["p"][0]) for x in G.nodes}  # -> (lon, lat)
    anc = {x: nx.ancestors(G, x) | {x} for x in G.nodes}
    chains = list(G.edges)
    rng = np.random.default_rng(20261109)
    idx = rng.permutation(len(chains))
    dists = []
    tried = 0
    for i in idx[:400]:
        for j in idx[:400]:
            if i >= j:
                continue
            a, b = chains[i], chains[j]
            na, nb = set(a), set(b)
            if na & nb:
                continue
            union_a = set().union(*(anc[x] for x in na))
            union_b = set().union(*(anc[x] for x in nb))
            if union_a & union_b:  # shared ancestor or path between chains -> not disconnected
                continue
            tried += 1
            d = min(haversine_km(pos[u], pos[v]) for u in na for v in nb)
            dists.append(d)
    dists = np.array(dists)
    out["P0c_disconnected_chain_pairs_sampled"] = {
        "n_pairs": int(len(dists)),
        "le_30km": int((dists <= 30).sum()), "le_50km": int((dists <= 50).sum()),
        "ge_150km": int((dists >= 150).sum()),
        "quantiles_km": [float(q) for q in np.quantile(dists, [0.05, 0.25, 0.5, 0.75, 0.95])],
    }

    # P0b. DWD hourly precipitation stations active over 2019-2023
    st = ROOT / "dwd" / "stations_hourly.txt"
    rows = []
    for line in st.read_bytes().decode("latin1").splitlines()[2:]:
        parts = line.split()
        if len(parts) < 6:
            continue
        sid, von, bis, _h, lat, lon = parts[:6]
        if int(von) <= 20190101 and int(bis) >= 20231231:
            rows.append((sid, float(lon), float(lat)))
    near = []
    for x in G.nodes:
        d = min(haversine_km(pos[x], (lon, lat)) for _, lon, lat in rows)
        near.append(d)
    near = np.array(near)
    out["P0b_dwd_hourly"] = {"active_stations_2019_2023": len(rows),
                              "river_nodes_with_station_le_10km": float((near <= 10).mean()),
                              "river_nodes_with_station_le_20km": float((near <= 20).mean()),
                              "median_km_to_nearest": float(np.median(near))}
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
