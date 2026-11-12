"""P0d (descriptive, no causal discovery): how many TS-G1 units survive the declared exclusion rules.

Unit = two gauged chains (a1->a2), (b1->b2), no shared node, no shared ancestor, no path between them.
Exclusion: any of the 4 series with >10% missing over 2019-2023 at native resolution.
Strata by min haversine distance between chains: near <= D_near, far >= D_far.
Sampling: seed 20261109, each chain used at most 3 times, up to 100 units per stratum.
Also reports DWD hourly station availability within R_rain km of each unit's chains.

Usage: python -P -E P0d_unit_feasibility.py <artifacts/ts_causalrivers>
"""
import json
import sys
from itertools import combinations
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from P0_descriptive import haversine_km, load_graph  # noqa: E402

ROOT = Path(sys.argv[1])
PROD = ROOT / "product"
OUT = Path(__file__).with_name("P0d_outputs.json")
SEED = 20261109


def dwd_hourly_active(path):
    rows = []
    for line in path.read_bytes().decode("latin1").splitlines()[2:]:
        parts = line.split()
        if len(parts) >= 6 and int(parts[1]) <= 20190101 and int(parts[2]) >= 20231231:
            rows.append((parts[0], float(parts[5]), float(parts[4])))  # id, lon, lat
    return rows


def sample_units(pairs, n, rng, cap=3):
    order = rng.permutation(len(pairs))
    used, out = {}, []
    for k in order:
        a, b, d = pairs[k]
        if used.get(a, 0) >= cap or used.get(b, 0) >= cap:
            continue
        out.append((a, b, d))
        used[a] = used.get(a, 0) + 1
        used[b] = used.get(b, 0) + 1
        if len(out) == n:
            break
    return out


def main():
    G = load_graph(PROD / "rivers_east_germany.p")
    pos = {x: (G.nodes[x]["p"][1], G.nodes[x]["p"][0]) for x in G.nodes}  # (lon, lat)
    header = pd.read_csv(PROD / "rivers_ts_east_germany.csv", nrows=0).columns
    ts = pd.read_csv(PROD / "rivers_ts_east_germany.csv", index_col=0,
                     dtype={c: np.float32 for c in header[1:]})
    ts.index = pd.to_datetime(ts.index)
    miss = ts.loc["2019-01-01":"2023-12-31"].isna().mean()
    ok_nodes = {int(c) for c, m in miss.items() if m <= 0.10}
    del ts

    anc = {x: nx.ancestors(G, x) | {x} for x in G.nodes}
    chains = [e for e in G.edges if e[0] in ok_nodes and e[1] in ok_nodes]
    chain_anc = {c: anc[c[0]] | anc[c[1]] for c in chains}
    pairs = []
    for a, b in combinations(chains, 2):
        if set(a) & set(b) or chain_anc[a] & chain_anc[b]:
            continue
        d = min(haversine_km(pos[u], pos[v]) for u in a for v in b)
        pairs.append((a, b, d))

    stations = dwd_hourly_active(ROOT / "dwd" / "stations_hourly.txt")
    st_xy = np.array([(lon, lat) for _, lon, lat in stations])

    def n_stations_within(chain, r):
        return int(sum(1 for lon, lat in st_xy
                       if min(haversine_km(pos[u], (lon, lat)) for u in chain) <= r))

    out = {"n_chains_after_missing_filter": len(chains), "n_disconnected_pairs": len(pairs)}
    for d_near, d_far in [(30, 150), (50, 150)]:
        near = [p for p in pairs if p[2] <= d_near]
        far = [p for p in pairs if p[2] >= d_far]
        rng = np.random.default_rng(SEED)
        s_near = sample_units(near, 100, rng)
        s_far = sample_units(far, 100, rng)
        key = f"near<={d_near}_far>={d_far}"
        out[key] = {"candidate_pairs_near": len(near), "candidate_pairs_far": len(far),
                    "sampled_near": len(s_near), "sampled_far": len(s_far)}
        for r in (10, 20):
            cover = [min(n_stations_within(a, r), n_stations_within(b, r)) for a, b, _ in s_near + s_far]
            out[key][f"units_with_>=1_dwd_station_per_chain_within_{r}km"] = int(sum(c >= 1 for c in cover))
        print(key, out[key], flush=True)
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
