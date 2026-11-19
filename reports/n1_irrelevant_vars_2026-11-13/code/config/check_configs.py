"""Config check only: graph family, acyclicity, realized edges, orientation. No model, no metric."""
import sys, json, hashlib
from pathlib import Path
import numpy as np
from avici import simulate_data
cfg = Path(sys.argv[1]); out = {}
for f in sorted(cfg.glob('er*-gauss.yaml')):
    e = int(f.name[2]); rows = []
    for d in (5, 10, 20, 30):
        edges = []; ok = True; orient = []
        for seed in range(20):
            g, x, _ = simulate_data(d=d, n=500, seed=900000 + seed, path=str(f))
            assert g.shape == (d, d) and x.shape == (500, d) and np.isfinite(x).all()
            # acyclic: nilpotent
            m = g.copy(); 
            for _ in range(d): m = (m @ g > 0).astype(int)
            ok &= (m.sum() == 0) and (np.trace(g) == 0)
            edges.append(int(g.sum()))
            # orientation: sources (no incoming under g[i,j]=i->j means column sum 0)
            roots = np.flatnonzero(g.sum(0) == 0)
            orient.append(len(roots))
        rows.append(dict(d=d, expected=min(e * d, 0.99 * d * (d - 1) / 2), mean_edges=float(np.mean(edges)), min=min(edges), max=max(edges), acyclic=bool(ok), zero_edge_graphs=int(sum(v == 0 for v in edges))))
    out[f.name] = dict(sha256=hashlib.sha256(f.read_bytes()).hexdigest(), rows=rows)
# orientation convention: linear, d=2-chain check via regression is not needed; read avici docs: g[i,j]=1 means i->j
print(json.dumps(out, indent=1)); (cfg / 'config_check.json').write_text(json.dumps(out, indent=1))
