"""Phase 0 check for rules section 2.3: the An-set adjacency criterion must match the exhaustive check on every graph
with |O| <= 12 (bnlearn with hidden variables, and random DAGs). Also reports pair-class counts per unit.

Usage: python -I P0_verify_mag.py <artifacts/llm_prior_p17/bnlearn>
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from p17_common import (MARK_BIDIRECTED, classify_pairs, hide_variables, mag_from_dag, parse_bif, random_dag,  # noqa: E402
                        verify_adjacency_criterion)

NETWORKS = ["asia", "cancer", "earthquake", "survey", "sachs", "child", "insurance", "alarm", "hailfinder", "hepar2"]
HIDE_SEEDS = [1, 2, 3]


def main():
    root = Path(sys.argv[1])
    out = {"bnlearn": [], "random": [], "criterion_mismatches": 0, "checked_exhaustively": 0}
    for name in NETWORKS:
        g = parse_bif(root / f"{name}.bif")
        for s in HIDE_SEEDS:
            h = hide_variables(g, s)
            rec = {"network": name, "n_nodes": g.number_of_nodes(), "n_edges": g.number_of_edges(), "seed": s,
                   "draws": h["draws"], "seed_used": h["seed_used"]}
            if h["latent"] is None:
                rec["status"] = "no_B_pair_after_redraws"
                out["bnlearn"].append(rec)
                continue
            obs = h["observed"]
            t0 = time.perf_counter()
            mag = mag_from_dag(g, obs)
            rec["t_mag_s"] = round(time.perf_counter() - t0, 3)
            classes = classify_pairs(g, obs, mag)
            counts = {c: 0 for c in "DBIN"}
            for c in classes.values():
                counts[c] += 1
            rec.update({"n_latent": len(h["latent"]), "n_observed": len(obs), "latent": sorted(h["latent"]), "pairs": counts,
                        "n_mag_edges": len(mag)})
            if len(obs) <= 12:
                ok = verify_adjacency_criterion(g, obs)
                out["checked_exhaustively"] += 1
                out["criterion_mismatches"] += 0 if ok else 1
                rec["criterion_ok"] = ok
            out["bnlearn"].append(rec)
            print(name, s, rec.get("criterion_ok", "n/a"), counts, flush=True)
    # random DAGs: 8..12 nodes, 30% latent, mean degree 2 and 3
    for n in (8, 10, 12):
        for md in (2.0, 3.0):
            for seed in range(20):
                g = random_dag(n, md, 20261112 + 1000 * n + 100 * int(md) + seed)
                h = hide_variables(g, seed)
                if h["latent"] is None:
                    out["random"].append({"n": n, "md": md, "seed": seed, "status": "no_B_pair"})
                    continue
                ok = verify_adjacency_criterion(g, h["observed"])
                out["checked_exhaustively"] += 1
                out["criterion_mismatches"] += 0 if ok else 1
                mag = mag_from_dag(g, h["observed"])
                out["random"].append({"n": n, "md": md, "seed": seed, "criterion_ok": ok,
                                      "n_B": sum(1 for _, m in mag.values() if m == MARK_BIDIRECTED)})
    print("checked exhaustively:", out["checked_exhaustively"], "mismatches:", out["criterion_mismatches"])
    Path(__file__).with_name("P0_verify_mag_outputs.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
