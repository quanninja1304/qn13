"""P-N5 (rules PN5 v1, locked 2026-11-22 at commit 99197d8): real tables, preprocessing, padding, inputs and job lists.

Imports the frozen P-N2 module common2.py and, through it, the frozen P-N1 module common.py, unchanged.
Deterministic given the two data files and the seeds. No model is called and no metric is computed here.

Rules PN5 v1:
  §1  each data file is checked against the manifest SHA-256 before it is parsed; 500 rows are chosen with
      SeedSequence([20261122, j]); the real block is X_R = zscore(normal-score(rows)) (float32), computed once and reused;
  §2  padding = zscore(pad_data(...)) of the frozen P-N2 generator (RFF, s = 1), seed 460000 + 1000 j + r;
      every input is [X_R | P], concatenated without re-standardizing the table;
  §3  job lists in the locked order (main inputs first), GES without k = 40 structured.
"""
import io, sys, csv, json, hashlib
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
RUNS5 = HERE.parent                                   # artifacts/n5_runs
ART = RUNS5.parent                                    # artifacts
REPO = ART.parent                                     # safety_prior
OUT5 = RUNS5 / 'pn5_out'
DATA = ART / 'data_real'
MANIFEST = REPO / 'reports' / 'n5_real_data_consistency_2026-11-22' / 'manifest' / 'data_manifest.json'
sys.path.insert(0, str(ART / 'n2_runs' / 'pn2'))
from common2 import N, zscore, sha, pad_params, pad_graph, pad_data, padding2   # frozen P-N2 (and P-N1 via common2)
from common import cfg_path                                                     # frozen P-N1 (DEV5 stand-in config)

N_ROWS = 500
assert N == N_ROWS, 'padding generator row count must equal the number of selected rows'
SELECT_SEED = 20261122
KS = (20, 40)
ES = (0, 2)                                           # e = 0: Gaussian padding; e = 2: structured ER-RFF padding
LIMIT_S = 900                                         # PC and GES wall-clock limit per job (rules §3)
BUDGET_S = 3 * 3600                                   # run budget (rules §3)
ALGS = ('avici', 'cdfm', 'pc', 'ges')
MODELS = ('avici', 'cdfm')
CLASSICAL = ('pc', 'ges')

TABLES = {
    'sachs': dict(j=0, path=DATA / 'sachs_zenodo_7681811' / 'extracted' / 'cd3cd28.csv', delim=',', drop=(),
                  mkey='sachs', idx_sha16='c2914a4f8500a51f', excess_dup=0),
    'wine': dict(j=1, path=DATA / 'uci_wine_quality_186' / 'extracted' / 'winequality-white.csv', delim=';',
                 drop=('quality',), mkey='wine_white', idx_sha16='1335a9a588b6d5e3', excess_dup=10),
}
LETTER = {'sachs': 'S', 'wine': 'W', 'standin': 'X'}
SETS5 = {'PN5': dict(tables=('sachs', 'wine'), base=460000, draws=20),
         'DEV5': dict(tables=('standin',), base=470000, draws=2)}   # DEV5: gates only (rules §8)
CONDS = ['k0'] + [f'k{k}_e{e}' for k in KS for e in ES]           # k0, k20_e0, k20_e2, k40_e0, k40_e2
MAIN = ('k0', 'k20_e0')                                           # main inputs (rules §3)


def file_sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def manifest():
    return json.loads(MANIFEST.read_text(encoding='utf-8'))


def load_raw(table):
    """float64 matrix of the used variables in file order, and their names. Refuses if the SHA-256 differs."""
    T = TABLES[table]
    b = T['path'].read_bytes()
    if hashlib.sha256(b).hexdigest() != manifest()[T['mkey']]['member_used']['sha256']:
        raise RuntimeError(f'{table}: data file SHA-256 differs from the manifest; reading refused')
    rows = list(csv.reader(io.StringIO(b.decode('utf-8'), newline=''), delimiter=T['delim']))
    hdr, body = rows[0], rows[1:]
    keep = [i for i, h in enumerate(hdr) if h not in T['drop']]
    X = np.array([[float(r[i]) for i in keep] for r in body], dtype=np.float64)
    return X, [hdr[i] for i in keep]


def select_idx(n_total, j):
    rng = np.random.default_rng(np.random.SeedSequence([SELECT_SEED, j]))
    return np.sort(rng.choice(n_total, N_ROWS, replace=False)).astype(np.int64)


def normal_score(x):
    """Rank-based normal scores per column: average ranks for ties, then Phi^-1(r / (n + 1)) (rules §1)."""
    n = x.shape[0]
    return stats.norm.ppf(stats.rankdata(x, method='average', axis=0) / (n + 1))


_RB = {}


def real_block(table):
    """X_R (500 x 11, float32), computed once per process. 'standin' is the DEV5 synthetic table (rules §8)."""
    if table in _RB:
        return _RB[table]
    if table == 'standin':
        from avici import simulate_data
        _, x, _ = simulate_data(d=11, n=N_ROWS, seed=999000, path=str(cfg_path(2, 'rff')))
        raw = np.asarray(x, np.float64)
        names = [f'V{i}' for i in range(raw.shape[1])]
        idx = np.arange(N_ROWS, dtype=np.int64)
        sub = raw
    else:
        raw, names = load_raw(table)
        idx = select_idx(raw.shape[0], TABLES[table]['j'])
        sub = raw[idx]
    XR = np.ascontiguousarray(zscore(normal_score(sub)))
    _RB[table] = dict(XR=XR, names=names, idx=idx, n_total=int(raw.shape[0]), idx_sha=sha(idx), XR_sha=sha(XR),
                      n_excess_duplicates=int(sub.shape[0] - len({tuple(r) for r in sub})))
    return _RB[table]


def xr_file(table):
    return OUT5 / 'inputs' / f'{table}_XR.npy'


def draw_seed(set_name, table, r):
    j = TABLES[table]['j'] if table in TABLES else 0
    return SETS5[set_name]['base'] + 1000 * j + r


def pad_block(seed, k, e):
    """Padding block of one draw: the three frozen P-N2 functions with k as a parameter, z-scored once (rules §2)."""
    P = pad_params(seed, 'rff', k=k)
    g = pad_graph(P, float(e), k=k)
    x64 = pad_data(P, g, 'rff', 1.0)
    deg = g.sum(0) + g.sum(1)
    return dict(P=np.ascontiguousarray(zscore(x64)), g=g, x64=x64, n_edges=int(g.sum()), n_isolated=int((deg == 0).sum()))


def parse(cond):
    k, e = cond.split('_')
    return int(k[1:]), int(e[1:])


def alg_conds(alg):
    return [c for c in CONDS if not (alg == 'ges' and c == 'k40_e2')]   # GES scope (rules §3)


def key5(table, cond, r=None, rep=False):
    return f'{table}__{cond}' + ('' if r is None else f'__r{r:02d}') + ('__rep' if rep else '')


def jobs5(set_name, alg, extra_rep=False):
    """Ordered jobs (table, cond, r, rep) of one algorithm (rules §3): all main inputs first, then the others.
    extra_rep (DEV5 only, gate G6) appends a rerun of one D = 51 input."""
    S = SETS5[set_name]
    main, rest = [], []
    for t in S['tables']:
        main += [(t, 'k0', None, False), (t, 'k0', None, True)] + [(t, 'k20_e0', r, False) for r in range(S['draws'])]
        rest += [(t, c, r, False) for c in alg_conds(alg) if c not in MAIN for r in range(S['draws'])]
    out = main + rest
    if extra_rep:
        out.append((S['tables'][0], 'k40_e0', 0, True))
    return out


def assemble5(set_name, table, cond, r=None):
    """Input of (table, condition, draw): X_R alone for k0, else [X_R | P] without re-standardizing (rules §2)."""
    rb = real_block(table)
    XR = rb['XR']
    if cond == 'k0':
        return XR, rb, None
    k, e = parse(cond)
    pad = pad_block(draw_seed(set_name, table, r), k, e)
    X = np.ascontiguousarray(np.concatenate([XR, pad['P']], 1))
    dT = XR.shape[1]
    assert X.dtype == np.float32 and X.shape == (N_ROWS, dT + k)
    assert np.ascontiguousarray(X[:, :dT]).tobytes() == XR.tobytes(), 'real block not bitwise identical to X_R'
    assert np.ascontiguousarray(X[:, dT:]).tobytes() == pad['P'].tobytes(), 'padding block not bitwise identical'
    return X, rb, pad
