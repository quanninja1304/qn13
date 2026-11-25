"""P-N8 / Study 7 common (rules PN8 v1, locked 49558ae): sets, seeds, inputs, job lists, SEA output reading.

Frozen modules imported unchanged: P-N1 common.py (target generator, CELLS, sha) and metrics.py (f1, dp, f1_full_graph);
P-N2 common2.py (padding generator, assemble2); P-N5 common5.py (real-table and DEV5 stand-in inputs).
Everything is deterministic given the seeds. No metric is computed here except the SEA output unpacking.
"""
import sys, json, pickle
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RUNS8 = HERE.parent                                   # artifacts/n8_runs
ART = RUNS8.parent                                    # artifacts
REPO = ART.parent                                     # safety_prior
OUT8 = RUNS8 / 'pn8_out'
WORK8 = RUNS8 / 'pn8_work'
OUT5 = ART / 'n5_runs' / 'pn5_out'
SEA_SRC = RUNS8 / 'sea_src'
SEA_PY = RUNS8 / 'sea_env' / 'Scripts' / 'python.exe'
WRAPPER = HERE / 'sea_wrapper8.py'
REPORT = REPO / 'reports' / 'n8_sea_model_coverage_2026-11-23'
INPUTS5 = REPO / 'reports' / 'n5_real_data_consistency_2026-11-22' / 'checks' / 'inputs5.json'
for _sub in ('n5_runs/pn5', 'n2_runs/pn2', 'n1_runs/pn1'):   # frozen modules ahead of site-packages
    if str(ART / _sub) not in sys.path:
        sys.path.insert(1, str(ART / _sub))
import common5 as C5                                  # frozen P-N5
import common2 as C2                                  # frozen P-N2
from common import CELLS, sha                         # frozen P-N1
import metrics as M1                                  # frozen P-N1 (f1, f1_full_graph, dp)

N_PER_CELL = 15                                       # rules §2
M_REF = 4                                             # rules §2
SETS8 = {'PN8': dict(base=500000, reps=N_PER_CELL, off=0),
         'DEV8': dict(base=510000, reps=2, off=1_000_000)}   # rules §2 (dev seeds + 1 000 000), §6 (2 per cell)
TABLES = ('sachs', 'wine')                            # j = 0, 1 (rules §2)
R_DRAWS = 20
DEV5_DRAWS = 2                                        # rules §6: the two frozen DEV5 draws
LINEAR = tuple(ci for ci in range(8) if CELLS[ci][2] == 'lin')     # 0, 2, 4, 6
RUN_CELLS = {'A1': (0, 2), 'A2': (1, 3), 'A3': (4, 6), 'A4': (5, 7)}  # rules §8
for _r, _cs in RUN_CELLS.items():
    assert all(CELLS[c][0] == (10 if _r in ('A1', 'A2') else 20) for c in _cs)
    assert all(CELLS[c][2] == ('lin' if _r in ('A1', 'A3') else 'rff') for c in _cs)
BUDGET_H = {'A1': 2.1, 'A2': 2.1, 'A3': 3.0, 'A4': 3.0, 'B': 2.5, 'IL': 0.8, 'DEV': 2.0}   # rules §8 (1.5 x estimate)
CONDS_A = ('k0', 'A20', 'S20')
MARGIN = {'P8-1': 1.0, 'P8-1S': 1.0, 'P8-2': 0.05, 'P8-3': 0.05, 'P8-4S': 1.0, 'P8-4W': 1.0}   # rules §4
HYPS = tuple(MARGIN)


# ---------------------------------------------------------------- seeds (rules §2)
def seed_a(i, off=0):
    return 600000 + i + off


def seed_b(i, m, off=0):
    return 610000 + 10 * i + m + off


def seed_ar(j, r, off=0):
    return 620000 + 100 * j + r + off


def seed_br(j, r, m, off=0):
    return 630000 + 1000 * j + 10 * r + m + off


def systems8(set_name):
    s = SETS8[set_name]
    return [(f'{set_name}-c{ci}-r{r}', ci, s['base'] + 1000 * ci + r, N_PER_CELL * ci + r)
            for ci in range(8) for r in range(s['reps'])]


# ---------------------------------------------------------------- inputs
def c2_cond(ci, cond):
    return {'k0': 'k0', 'A20': 'e0', 'S20': C2.rep_cond(ci)}[cond]


def syn_input(sysid, ci, seed, cond):
    """(X float32 n x D, DAG int64 D x D, d_T, target graph) for a synthetic system; frozen P-N2 assemble2."""
    X, t, pad = C2.assemble2(sysid, ci, seed, c2_cond(ci, cond))
    D, dT = X.shape[1], t['g'].shape[0]
    G = np.zeros((D, D), dtype=np.int64)
    G[:dT, :dT] = t['g']
    if pad is not None:
        G[dT:, dT:] = pad['g']
    return np.ascontiguousarray(X, dtype=np.float32), G, dT, np.asarray(t['g'])


_standin_g = None


def standin_graph():
    global _standin_g
    if _standin_g is None:
        from avici import simulate_data
        _standin_g, _, _ = simulate_data(d=11, n=C5.N_ROWS, seed=999000, path=str(C5.cfg_path(2, 'rff')))
    return np.asarray(_standin_g)


def real_input(set5, table, cond, r=None):
    """Real table (PN5) or DEV5 stand-in; cond 'k0' or 'k20_e0'. Real tables get an all-zero DAG (rules §6, G1)."""
    X, rb, pad = C5.assemble5(set5, table, cond, r)
    D, dT = X.shape[1], rb['XR'].shape[1]
    G = np.zeros((D, D), dtype=np.int64)
    if table == 'standin':
        G[:dT, :dT] = standin_graph()
    return np.ascontiguousarray(X, dtype=np.float32), G, dT


def perm_of(tag, i, D):
    """Column permutation, rules §6: G3 tag 3 (DEV system i), interleaved branch tag 4 (main system i)."""
    return np.random.default_rng([20261123, tag, i]).permutation(D)


def build(job):
    """Input written for SEA: (X_in, G_in, X_original_sha, d_T, perm or None)."""
    if job['kind'] == 'syn':
        X, G, dT, _ = syn_input(job['sysid'], job['ci'], job['sys_seed'], job['cond'])
    else:
        X, G, dT = real_input(job['set5'], job['table'], job['cond'], job.get('r'))
    xsha = sha(X)
    perm = None
    if job.get('perm_tag') is not None:
        perm = perm_of(job['perm_tag'], job['i'], X.shape[1])
        X, G = np.ascontiguousarray(X[:, perm]), G[np.ix_(perm, perm)]
    if job.get('zero_dag'):
        G = np.zeros_like(G)
    return X, G, xsha, dT, perm


# ---------------------------------------------------------------- jobs
def _job(key, **kw):
    return dict(key=key, **kw)


def syn_jobs(set_name, cells, off):
    jl = []
    for sysid, ci, sseed, i in systems8(set_name):
        if ci not in cells:
            continue
        a = seed_a(i, off)
        base = dict(kind='syn', set=set_name, sysid=sysid, ci=ci, sys_seed=sseed, i=i, r=int(sysid.rsplit('-r', 1)[1]))
        for cond in CONDS_A:
            jl.append(_job(f'{sysid}__{cond}__s{a}', role='main', cond=cond, seed=a, **base))
        for m in range(1, M_REF + 1):
            b = seed_b(i, m, off)
            jl.append(_job(f'{sysid}__k0__s{b}', role='ref', cond='k0', seed=b, m=m, **base))
    return jl


def real_jobs(set5, tables, draws, off):
    jl = []
    for table in tables:
        j = C5.TABLES[table]['j'] if table in C5.TABLES else 0
        for r in range(draws):
            a = seed_ar(j, r, off)
            base = dict(kind='real', set5=set5, table=table, j=j, r=r, i=r)
            jl.append(_job(f'{set5}-{table}__k0__r{r:02d}__s{a}', role='main_k0', cond='k0', seed=a, **base))
            jl.append(_job(f'{set5}-{table}__k20_e0__r{r:02d}__s{a}', role='main', cond='k20_e0', seed=a, **base))
            for m in range(1, M_REF + 1):
                b = seed_br(j, r, m, off)
                jl.append(_job(f'{set5}-{table}__k0__r{r:02d}__s{b}', role='ref', cond='k0', seed=b, m=m, **base))
    return jl


def rerun_of(job):
    return dict(job, key=job['key'] + '__rerun', role='rerun', of=job['key'])


def run_jobs(run):
    """Planned jobs of one run, in execution order (reruns last; rules §7)."""
    if run in RUN_CELLS:
        jl = syn_jobs('PN8', RUN_CELLS[run], 0)
        firsts = [j for j in jl if j['role'] == 'main' and j['cond'] == 'k0' and j['r'] == 0]
        return jl + [rerun_of(j) for j in firsts]
    if run == 'B':
        jl = real_jobs('PN5', TABLES, R_DRAWS, 0)
        firsts = [j for j in jl if j['role'] == 'main_k0' and j['r'] == 0]
        return jl + [rerun_of(j) for j in firsts]
    if run == 'IL':     # contingency of G3 (rules §6): A20 interleaved, r < 5, seed a_i
        jl = []
        for sysid, ci, sseed, i in systems8('PN8'):
            r = int(sysid.rsplit('-r', 1)[1])
            if r < 5:
                a = seed_a(i)
                jl.append(_job(f'{sysid}__A20__s{a}__il', kind='syn', set='PN8', sysid=sysid, ci=ci, sys_seed=sseed, i=i,
                               r=r, role='interleave', cond='A20', seed=a, perm_tag=4, of=f'{sysid}__A20__s{a}'))
        return jl
    if run == 'DEV':
        off = SETS8['DEV8']['off']
        jl = []
        for job in syn_jobs('DEV8', tuple(range(8)), off):
            if job['r'] == 0 or (job['role'] == 'main' and job['cond'] == 'k0'):   # r = 1: k0 only (G4)
                jl.append(job)
        for job in [j for j in jl if j['r'] == 0 and j['cond'] == 'A20']:          # G3
            jl.append(dict(job, key=job['key'] + '__perm', role='perm', perm_tag=3, of=job['key']))
            a2 = job['seed'] + 500000
            jl.append(dict(job, key=f"{job['sysid']}__A20__s{a2}", role='seedalt', seed=a2, of=job['key']))
        jl += real_jobs('DEV5', ('standin',), DEV5_DRAWS, off)
        k0 = next(j for j in jl if j['key'].startswith('DEV8-c0-r0__k0__'))
        jl.append(rerun_of(k0))                                                    # G1 rerun
        jl.append(dict(k0, key=k0['key'] + '__zdag', role='zerodag', zero_dag=True, of=k0['key']))   # G1 graph check
        return jl
    raise ValueError(run)


# ---------------------------------------------------------------- outputs
def out_path(job_or_key, run=None):
    key = job_or_key if isinstance(job_or_key, str) else job_or_key['key']
    return OUT8 / 'sea' / f'{key}.npz'


def load_out(key):
    z = np.load(out_path(key), allow_pickle=False)
    return dict(prob=z['prob'] if 'prob' in z.files else None, meta=json.loads(str(z['meta'])))


def unpack(res_key_entry, D):
    """SEA pred = [P(i->j) for i<j] + [P(j->i) for i<j]; returns prob[i, j] = P(i -> j), and the true vector."""
    p = np.asarray(res_key_entry['pred'][0], np.float64)
    t = np.asarray(res_key_entry['true'][0], np.float64)
    P = D * (D - 1) // 2
    assert p.shape == (2 * P,) and t.shape == (2 * P,), (p.shape, P)
    iu = np.triu_indices(D, 1)
    F, B = np.zeros((D, D)), np.zeros((D, D))
    F[iu], B[iu] = p[:P], p[P:]
    return F + B.T, t, p


def expected_true(G):
    iu = np.triu_indices(G.shape[0], 1)
    return np.concatenate([G[iu], G.T[iu]]).astype(np.float64)


def unpermute(prob, perm):
    if perm is None:
        return prob
    out = np.empty_like(prob)
    out[np.ix_(perm, perm)] = prob            # P_orig[perm[a], perm[b]] = P_perm[a, b] (rules §6, G3)
    return out


# ---------------------------------------------------------------- readings (rules §1, §3)
def skel(prob, dT, alt=False):
    """Upper-triangle skeleton vector of the target block. NATIVE: max(P(i->j), P(j->i)) > 0.5;
    alternative (sensitivity, rules §1): 1 - P(no edge) = P(i->j) + P(j->i) > 0.5."""
    a = prob[:dT, :dT]
    s = (a + a.T) > 0.5 if alt else np.maximum(a, a.T) > 0.5
    return s[np.triu_indices(dT, 1)]


def as_matrix(vec, dT):
    m = np.zeros((dT, dT), dtype=np.int8)
    m[np.triu_indices(dT, 1)] = vec
    return m


def flips(s1, s0):
    return int((np.asarray(s1) != np.asarray(s0)).sum())


def f1(svec, g):
    return float(M1.f1(as_matrix(svec, g.shape[0]), np.asarray(g)))
