"""P1 preparation for TS-G1 (follows TS_G1_reading_rules_vi.md, locked 10/11/2026).

1. Rebuild the declared 200 units (near <= 30 km, far >= 150 km, seed 20261109, cap 3), identical to
   P0d's first configuration.
2. Select DWD hourly precipitation stations active over 2019-2023 within R_rain = 20 km of any node of a
   unit's chains; download their historical zips (opendata.dwd.de, "Frei").
3. Parse to an hourly matrix 2019-01-01 00:00 .. 2023-12-31 23:00 (UTC, as provided by DWD).
4. Build per-unit 6-hour datasets: 4 river series (mean, CausalRivers-style rounding), linear interpolation,
   rain proxies (mean over stations within 20 km of the chain, then 6-hour sum), z-score.

Usage: python -P -E P1_prepare.py <artifacts/ts_causalrivers>
Outputs: P1_units.json (in this folder); <root>/p1/unit_XXX.npz (data, not in Git).
"""
import io
import json
import sys
import time
import urllib.request
import zipfile
from itertools import combinations
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from P0_descriptive import haversine_km, load_graph  # noqa: E402
from P0d_unit_feasibility import dwd_hourly_active, sample_units  # noqa: E402

ROOT = Path(sys.argv[1])
PROD = ROOT / "product"
DWD = ROOT / "dwd"
HOURLY = DWD / "hourly"
P1DIR = ROOT / "p1"
HERE = Path(__file__).parent
SEED = 20261109
D_NEAR, D_FAR, R_RAIN, CAP, N_UNITS = 30.0, 150.0, 20.0, 3, 100
BASE = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/precipitation/historical/"
START, END = "2019-01-01", "2023-12-31 23:59"


def build_units(G, ok_nodes, pos):
    anc = {x: nx.ancestors(G, x) | {x} for x in G.nodes}
    chains = [e for e in G.edges if e[0] in ok_nodes and e[1] in ok_nodes]
    chain_anc = {c: anc[c[0]] | anc[c[1]] for c in chains}
    pairs = []
    for a, b in combinations(chains, 2):
        if set(a) & set(b) or chain_anc[a] & chain_anc[b]:
            continue
        d = min(haversine_km(pos[u], pos[v]) for u in a for v in b)
        pairs.append((a, b, d))
    near = [p for p in pairs if p[2] <= D_NEAR]
    far = [p for p in pairs if p[2] >= D_FAR]
    rng = np.random.default_rng(SEED)
    s_near = sample_units(near, N_UNITS, rng, cap=CAP)
    s_far = sample_units(far, N_UNITS, rng, cap=CAP)
    units = []
    for stratum, sel in (("near", s_near), ("far", s_far)):
        for a, b, d in sel:
            units.append({"id": len(units), "stratum": stratum, "chain_a": list(a), "chain_b": list(b),
                          "min_dist_km": d})
    return units


def download(fname, dest, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(BASE + fname, timeout=120) as r:
                dest.write_bytes(r.read())
            zipfile.ZipFile(dest).testzip()
            return True
        except Exception as e:  # noqa: BLE001
            print("retry", fname, k, type(e).__name__, flush=True)
            time.sleep(5 * (k + 1))
    return False


def parse_hourly(path):
    z = zipfile.ZipFile(path)
    name = [n for n in z.namelist() if n.startswith("produkt_rr_stunde")][0]
    df = pd.read_csv(io.BytesIO(z.read(name)), sep=";", skipinitialspace=True, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    t = pd.to_datetime(df["MESS_DATUM"].str.strip(), format="%Y%m%d%H")
    v = pd.to_numeric(df["R1"], errors="coerce").astype("float32")
    v[v <= -999] = np.nan
    s = pd.Series(v.values, index=t)
    s = s[~s.index.duplicated()]
    return s.loc[START:END]


def to6h_mean(df):
    g = df.copy()
    g.index = g.index.round("6h")
    return g.groupby(level=0).mean()


def main():
    G = load_graph(PROD / "rivers_east_germany.p")
    pos = {x: (G.nodes[x]["p"][1], G.nodes[x]["p"][0]) for x in G.nodes}  # (lon, lat)
    header = pd.read_csv(PROD / "rivers_ts_east_germany.csv", nrows=0).columns
    ts = pd.read_csv(PROD / "rivers_ts_east_germany.csv", index_col=0,
                     dtype={c: np.float32 for c in header[1:]})
    ts.index = pd.to_datetime(ts.index)
    ts = ts.loc[START:END]
    miss = ts.isna().mean()
    ok_nodes = {int(c) for c, m in miss.items() if m <= 0.10}

    units = build_units(G, ok_nodes, pos)
    stations = dwd_hourly_active(DWD / "stations_hourly.txt")
    for u in units:
        for key in ("chain_a", "chain_b"):
            u[f"rain_{key}"] = [sid for sid, lon, lat in stations
                                if min(haversine_km(pos[n], (lon, lat)) for n in u[key]) <= R_RAIN]
    need = sorted({s for u in units for k in ("rain_chain_a", "rain_chain_b") for s in u[k]})
    print("units", len(units), "stations needed", len(need), flush=True)

    listing = (DWD / "hourly_hist_listing.txt").read_text().split()
    fname = {f.split("_")[2]: f for f in listing}
    HOURLY.mkdir(parents=True, exist_ok=True)
    rain = {}
    missing_files = []
    for i, sid in enumerate(need):
        f = fname.get(sid)
        if f is None:
            missing_files.append(sid)
            continue
        dest = HOURLY / f
        if not dest.exists() and not download(f, dest):
            missing_files.append(sid)
            continue
        rain[sid] = parse_hourly(dest)
        if i % 25 == 0:
            print("dwd", i, "/", len(need), flush=True)
    hidx = pd.date_range(START, "2023-12-31 23:00", freq="h")
    R = pd.DataFrame({k: v.reindex(hidx) for k, v in rain.items()})

    P1DIR.mkdir(parents=True, exist_ok=True)
    river_cols = sorted({n for u in units for n in u["chain_a"] + u["chain_b"]})
    river6 = to6h_mean(ts[[str(n) for n in river_cols]]).interpolate(method="linear", limit_direction="both")
    del ts
    for u in units:
        cols = [str(n) for n in u["chain_a"] + u["chain_b"]]
        X = river6[cols]
        proxies = []
        for key in ("rain_chain_a", "rain_chain_b"):
            ids = [s for s in u[key] if s in R.columns]
            u[key + "_used"] = ids
            r = R[ids].mean(axis=1, skipna=True)                       # areal mean, hourly
            r = r.interpolate(method="linear", limit_direction="both")  # gaps where all stations missing
            r.index = r.index.floor("6h")
            proxies.append(r.groupby(level=0).sum(min_count=1))        # 6-hour sum
        P = pd.concat(proxies, axis=1).reindex(X.index)
        P = P.interpolate(method="linear", limit_direction="both")
        Z = pd.concat([X, P], axis=1).to_numpy(dtype=np.float64)
        Z = (Z - Z.mean(axis=0)) / Z.std(axis=0)
        u["n_time"] = int(Z.shape[0])
        u["n_nan_after_prep"] = int(np.isnan(Z).sum())
        np.savez_compressed(P1DIR / f"unit_{u['id']:03d}.npz", Z=Z, cols=np.array(cols + ["rain_a", "rain_b"]))
    out = {"units": units, "dwd_stations_needed": len(need), "dwd_missing_files": missing_files,
           "river_time_index_tz": "naive (assumed UTC; not documented by CausalRivers)"}
    (HERE / "P1_units.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("done; missing dwd files:", missing_files)


if __name__ == "__main__":
    main()
