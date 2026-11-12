"""P1 runs for TS-G1: VAR-Granger, PCMCI+, LPCMCI on 200 units x {L, O} x {6H, 24H}.

Follows TS_G1_reading_rules_vi.md (locked 10/11/2026) plus the clarifications logged in its section 8
before any run. Each job runs in its own process with a 300 s timeout; 3 workers; BLAS single-threaded.
Results are appended to P1_results.jsonl (resumable).

Usage: python -P -E P1_run.py <artifacts/ts_causalrivers> [--res 6H|24H|both]
"""
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"

import numpy as np  # noqa: E402

HERE = Path(__file__).parent
RESULTS = HERE / "P1_results.jsonl"
TIMEOUT = 300.0
WORKERS = 3
ALPHA = 0.01
TAU = {"6H": 4, "24H": 1}
N_RIVER = 4


def load_unit(root, uid, res):
    d = np.load(Path(root) / "p1" / f"unit_{uid:03d}.npz", allow_pickle=False)
    Z = d["Z"]
    if res == "24H":
        n = (Z.shape[0] // 4) * 4
        blocks = Z[:n].reshape(-1, 4, Z.shape[1])
        Z = np.concatenate([blocks[:, :, :N_RIVER].mean(axis=1), blocks[:, :, N_RIVER:].sum(axis=1)], axis=1)
        Z = (Z - Z.mean(axis=0)) / Z.std(axis=0)
    return Z


def link_assumptions_observed(n_vars, tau_max):
    """Rain variables (index >= N_RIVER) are exogenous: no river -> rain links."""
    la = {j: {} for j in range(n_vars)}
    for j in range(n_vars):
        for i in range(n_vars):
            for tau in range(0, tau_max + 1):
                if i == j and tau == 0:
                    continue
                i_rain, j_rain = i >= N_RIVER, j >= N_RIVER
                if j_rain and not i_rain:
                    if tau == 0:
                        la[j][(i, 0)] = "<?-"  # mirror of rain -?> river
                    continue
                if tau > 0:
                    la[j][(i, -tau)] = "-?>"
                elif i_rain and not j_rain:
                    la[j][(i, 0)] = "-?>"
                else:
                    la[j][(i, 0)] = "o?o"
    return la


def run_var(Z, tau_max):
    from statsmodels.tsa.api import VAR
    fit = VAR(Z).fit(maxlags=tau_max, trend="c")
    n = Z.shape[1]
    g = np.full((n, n, tau_max + 1), "", dtype="<U3")
    for j in range(N_RIVER):
        for i in range(n):
            if i == j:
                continue
            p = fit.test_causality(caused=j, causing=[i], kind="f").pvalue
            if p < ALPHA:
                g[i, j, 1] = "-->"  # summary-level Granger claim (lag not resolved)
    return g


def run_tigramite(Z, tau_max, method, observed):
    from tigramite import data_processing as pp
    from tigramite.independence_tests.parcorr import ParCorr
    df = pp.DataFrame(Z)
    la = link_assumptions_observed(Z.shape[1], tau_max) if observed else None
    if method == "pcmciplus":
        from tigramite.pcmci import PCMCI
        r = PCMCI(dataframe=df, cond_ind_test=ParCorr(), verbosity=0).run_pcmciplus(
            tau_min=0, tau_max=tau_max, pc_alpha=ALPHA, link_assumptions=la)
    else:
        from tigramite.lpcmci import LPCMCI
        r = LPCMCI(dataframe=df, cond_ind_test=ParCorr(), verbosity=0).run_lpcmci(
            tau_max=tau_max, pc_alpha=ALPHA, link_assumptions=la)
    return r["graph"]


def job(root, uid, cond, method, res, q):
    try:
        Z = load_unit(root, uid, res)
        if cond == "L":
            Z = Z[:, :N_RIVER]
        elif np.corrcoef(Z[:, N_RIVER], Z[:, N_RIVER + 1])[0, 1] > 0.999:
            Z = Z[:, :N_RIVER + 1]  # identical rain proxies (same station set): keep one shared rain variable
        tau_max = TAU[res]
        t0 = time.perf_counter()
        if method == "var":
            g = run_var(Z, tau_max)
        else:
            g = run_tigramite(Z, tau_max, method, observed=(cond == "O"))
        dt = time.perf_counter() - t0
        q.put({"status": "ok", "runtime_s": dt, "graph": np.asarray(g).tolist()})
    except Exception as e:  # noqa: BLE001
        q.put({"status": "error", "error": f"{type(e).__name__}: {e}"})


def main():
    root = sys.argv[1]
    res_arg = sys.argv[sys.argv.index("--res") + 1] if "--res" in sys.argv else "both"
    resolutions = ["6H", "24H"] if res_arg == "both" else [res_arg]
    units = json.loads((HERE / "P1_units.json").read_text(encoding="utf-8"))["units"]
    done = set()
    if RESULTS.exists():
        for line in RESULTS.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["unit"], r["cond"], r["method"], r["res"]))
    jobs = [(u["id"], c, m, res) for res in resolutions for u in units for c in ("L", "O")
            for m in ("var", "pcmciplus", "lpcmci") if (u["id"], c, m, res) not in done]
    print("jobs to run:", len(jobs), flush=True)
    ctx = mp.get_context("spawn")
    running = []
    with open(RESULTS, "a", encoding="utf-8") as fout:
        while jobs or running:
            while jobs and len(running) < WORKERS:
                uid, cond, method, res = jobs.pop(0)
                q = ctx.Queue()
                p = ctx.Process(target=job, args=(root, uid, cond, method, res, q))
                p.start()
                running.append((p, q, time.time(), (uid, cond, method, res)))
            still = []
            for p, q, t0, key in running:
                out = None
                try:
                    out = q.get_nowait()
                except Exception:  # noqa: BLE001
                    pass
                if out is None and time.time() - t0 > TIMEOUT + 30:  # +30 s spawn/import allowance
                    p.terminate()
                    out = {"status": "timeout", "runtime_s": TIMEOUT}
                if out is None:
                    still.append((p, q, t0, key))
                    continue
                p.join(timeout=5)
                rec = {"unit": key[0], "cond": key[1], "method": key[2], "res": key[3], **out}
                fout.write(json.dumps(rec) + "\n")
                fout.flush()
            running = still
            time.sleep(0.2)
    print("all jobs finished", flush=True)


if __name__ == "__main__":
    main()
