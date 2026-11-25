"""P-N9 / Study 8 common (rules PN9 v1, locked 5146c74): sets, sample-size grids, seeds, inputs at each n, job lists,
output paths, readings of saved outputs.

Frozen modules imported unchanged:
  - P-N1 common.py (CELLS, cfg_path, zscore, sha) and metrics.py (skel_native, f1, flips);
  - P-N8 common8.py (SEA paths and wrapper, SEA output unpacking, SEA skeleton, flips, f1), which itself imports the
    frozen P-N2 common2.py and P-N5 common5.py.
Everything is deterministic given the seeds. No metric is computed here except readings of saved outputs.
"""
import os
import sys
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RUNS9 = HERE.parent                                   # artifacts/n9_runs
ART = RUNS9.parent                                    # artifacts
REPO = ART.parent                                     # safety_prior
OUT9 = RUNS9 / 'pn9_out'
WORK9 = RUNS9 / 'pn9_work'
ENV = ART / 'n1_models_cpu'
REPORT = REPO / 'reports' / 'n9_sample_size_2026-11-24'
OUT1 = ART / 'n1_runs' / 'pn1_out'                    # Study 1 saved outputs (adapter reproduction, G5)
OUT8 = ART / 'n8_runs' / 'pn8_out'                    # Study 7 saved outputs (adapter reproduction, G5)
for _sub in ('n8_runs/pn8', 'n1_runs/pn1'):           # frozen modules ahead of site-packages
    if str(ART / _sub) not in sys.path:
        sys.path.insert(1, str(ART / _sub))
import common8 as C8                                  # frozen P-N8 (imports frozen P-N2, P-N5 and P-N1 common)
from common import CELLS, cfg_path, zscore, sha       # frozen P-N1
import metrics as M1                                  # frozen P-N1

# ---------------------------------------------------------------- design (rules §2)
NMAX = 20000
K = 20
N_PER_CELL = 15
M_REF = 4
PAD_TAG = (20261125, 9)
SETS9 = {'PN9': dict(base=730000, reps=N_PER_CELL, off=0),
         'DEV9': dict(base=720000, reps=2, off=1_000_000)}
GRIDS = {'avici': (100, 200, 500, 1000),
         'cdfm': (100, 200, 500, 1000, 2000, 4000),
         'foundcause': (125, 200, 500),
         'sea': (500, 1000, 2000, 5000, 20000),
         'pc': (100, 125, 200, 500, 1000, 2000, 4000, 5000, 20000),
         'ges': (100, 125, 200, 500, 1000, 2000, 4000)}
MODELS = ('avici', 'cdfm', 'foundcause')
CLASSICAL = ('pc', 'ges')
ALL = MODELS + ('sea',) + CLASSICAL
THREADS = {'avici': 2, 'cdfm': 2, 'foundcause': 4}   # as Study 1 (saved metadata), needed for bitwise reproduction
LINEAR = tuple(ci for ci in range(8) if CELLS[ci][2] == 'lin')                # 0, 2, 4, 6
RUN_CELLS = {'R1': (0, 2), 'R2': (1, 3), 'R3': (4, 6), 'R4': (5, 7)}          # rules §8: four runs by cell pair
for _r, _cs in RUN_CELLS.items():
    assert all(CELLS[c][0] == (10 if _r in ('R1', 'R2') else 20) for c in _cs)
    assert all(CELLS[c][2] == ('lin' if _r in ('R1', 'R3') else 'rff') for c in _cs)
MEM_LIMIT_MB = 6.0 * 1024                             # rules §6, G3: 6.0 GB of 7.8 GB
# rules §8: stop mark per model and run in hours, 1.5 x the G4 estimate rounded up to 0.1 h (checks/gates9.json,
# G4.proposed_BUDGET_H); filled after the DEV gate and before the code was frozen
BUDGET_H = {
    'avici': dict(R1=0.5, R2=0.5, R3=0.5, R4=0.5),
    'cdfm': dict(R1=3.9, R2=3.9, R3=5.8, R4=5.8),
    'foundcause': dict(R1=13.9, R2=13.9, R3=17.9, R4=17.9),
    'sea': dict(R1=6.3, R2=6.3, R3=8.1, R4=8.1),
    'pc': dict(R1=0.1, R3=0.1),
    'ges': dict(R1=0.1, R3=0.5)}
G3_SYSTEM = 'c6'                                      # DEV system of cell 6 (d_T = 20, linear): D = 40 at k = 20
G3_N = {'avici': 1000, 'cdfm': 4000, 'foundcause': 500, 'sea': 20000, 'ges': 4000}


def systems9(set_name):
    """(sysid, cell, system seed, unit index i = 15 c + r) for a set (rules §2.1, §2.5)."""
    s = SETS9[set_name]
    return [(f'{set_name}-c{ci}-r{r}', ci, s['base'] + 1000 * ci + r, N_PER_CELL * ci + r)
            for ci in range(8) for r in range(s['reps'])]


# ---------------------------------------------------------------- data (rules §2.1, §2.2)
_tcache, _pcache = {}, {}


def target_raw(sysid, ci, seed):
    """Target block of one system, generated once with NMAX rows by the frozen Study 1 generator settings (AVICI
    simulator, cell config of Study 1, observational data only). Study 1's rejection rule: a target with 0 edges is
    replaced by seed + 500 (logged in 'rejected')."""
    if sysid in _tcache:
        return _tcache[sysid]
    from avici import simulate_data
    dT, e, m = CELLS[ci]
    s, rejected = seed, []
    while True:
        g, x, _ = simulate_data(d=dT, n=NMAX, seed=s, path=str(cfg_path(e, m)))
        if g.sum() > 0:
            break
        rejected.append(s)
        s += 500
    if len(_tcache) >= 4:
        _tcache.clear()
    res = dict(g=np.asarray(g).astype(np.int8), x=np.asarray(x, np.float64), seed_used=int(s), rejected=rejected,
               cell=CELLS[ci])
    _tcache[sysid] = res
    return res


def padding_raw(sysid, seed):
    """20 independent standard Gaussian columns with NMAX rows: rng = default_rng(SeedSequence([s_i, 20261125, 9]))."""
    if sysid not in _pcache:
        if len(_pcache) >= 4:
            _pcache.clear()
        rng = np.random.default_rng(np.random.SeedSequence([seed, *PAD_TAG]))
        _pcache[sysid] = rng.standard_normal((NMAX, K))
    return _pcache[sysid]


def clear_caches():
    _tcache.clear()
    _pcache.clear()


def inputs_at(sysid, ci, seed, n):
    """Inputs at sample size n: the first n rows of the target block and of the padding, each column z-scored on those
    n rows exactly as Study 1 (target z-scored, k0 = zscore(target), A20 = zscore([target | zscore(padding)])).
    Returns dict(k0, A20 float32, g int8, dT, seed_used, rejected). Asserts the target block is bitwise identical."""
    assert 1 < n <= NMAX
    t = target_raw(sysid, ci, seed)
    tx = zscore(t['x'][:n])
    x0 = zscore(tx)
    pz = zscore(padding_raw(sysid, seed)[:n])
    xa = zscore(np.concatenate([tx, pz], 1))
    dT = tx.shape[1]
    assert np.ascontiguousarray(xa[:, :dT]).tobytes() == x0.tobytes(), f'target block not bitwise identical ({sysid}, n={n})'
    return dict(k0=np.ascontiguousarray(x0), A20=np.ascontiguousarray(xa), g=t['g'], dT=dT, seed_used=t['seed_used'],
                rejected=t['rejected'])


def full_graph(g, D):
    """D x D DAG: target graph in the target block, no edge elsewhere (Gaussian padding has no edges)."""
    G = np.zeros((D, D), dtype=np.int64)
    G[:g.shape[0], :g.shape[0]] = g
    return G


# ---------------------------------------------------------------- SEA seeds (rules §2.4, §2.5)
def seed_a(i, l, off=0):
    return 740000 + 10 * i + l + off


def seed_b(i, l, m, off=0):
    return 750000 + 100 * i + 10 * l + m + off


# ---------------------------------------------------------------- jobs
def key_of(sysid, n, cond, seed=None):
    return f'{sysid}__n{n}__{cond}' + ('' if seed is None else f'__s{seed}')


def jobs9(model, set_name, cells=None, systems=None, levels=None, sea_refs=M_REF):
    """Planned jobs of one model on one set, ordered by system, level, input. Classical baselines: linear systems only.
    SEA: per level, k0 and A20 at seed a_{i,l} plus sea_refs reference runs of k0 at b_{i,l,m}."""
    s = SETS9[set_name]
    grid = GRIDS[model] if levels is None else tuple(levels)
    jl = []
    for sysid, ci, sseed, i in systems9(set_name):
        if cells is not None and ci not in cells:
            continue
        if systems is not None and sysid not in systems:
            continue
        if model in CLASSICAL and ci not in LINEAR:
            continue
        r = int(sysid.rsplit('-r', 1)[1])
        for n in grid:
            base = dict(model=model, set=set_name, sysid=sysid, ci=ci, sys_seed=sseed, i=i, r=r, n=n)
            if model == 'sea':
                lev = GRIDS['sea'].index(n)
                a = seed_a(i, lev, s['off'])
                for cond in ('k0', 'A20'):
                    jl.append(dict(key=key_of(sysid, n, cond, a), role='main', cond=cond, seed=a, level=lev, **base))
                for m in range(1, sea_refs + 1):
                    b = seed_b(i, lev, m, s['off'])
                    jl.append(dict(key=key_of(sysid, n, 'k0', b), role='ref', cond='k0', seed=b, m=m, level=lev, **base))
            else:
                for cond in ('k0', 'A20'):
                    jl.append(dict(key=key_of(sysid, n, cond), role='main', cond=cond, **base))
    return jl


def rerun_of(job):
    return dict(job, key=job['key'] + '__rerun', role='rerun', of=job['key'])


def run_jobs(model, run):
    """Main run (rules §8): cells of the run; at the end, a rerun of k0 at the smallest level of the first system of each
    cell (rules §7)."""
    jl = jobs9(model, 'PN9', cells=RUN_CELLS[run])
    firsts = []
    for ci in RUN_CELLS[run]:
        cand = [j for j in jl if j['ci'] == ci and j['r'] == 0 and j['cond'] == 'k0' and j['role'] == 'main']
        if cand:
            firsts.append(min(cand, key=lambda j: j['n']))
    return jl + [rerun_of(j) for j in firsts]


DEV_TIMING_SYSTEMS = ('DEV9-c0-r0', 'DEV9-c3-r0', 'DEV9-c4-r0', 'DEV9-c7-r0')   # one per (d_T, family) corner


def dev_jobs(model):
    """DEV plan (rules §6; feasibility only). Returns (timing jobs, special jobs). Special jobs: G2 rerun; G3 memory job
    (run alone in a fresh process); G5 adapter jobs (zero DAG for SEA)."""
    g3 = f'DEV9-{G3_SYSTEM}-r0'
    if model in ('avici', 'cdfm'):
        timing = jobs9(model, 'DEV9')
    elif model == 'foundcause':
        timing = jobs9(model, 'DEV9', systems=DEV_TIMING_SYSTEMS, levels=(125, 200))
    elif model == 'sea':
        timing = jobs9(model, 'DEV9', systems=DEV_TIMING_SYSTEMS, levels=(500, 20000), sea_refs=1)
    else:
        timing = jobs9(model, 'DEV9')
    special = []
    first = timing[0]
    special.append(dict(rerun_of(first), gate='G2'))
    if model in G3_N:
        n = G3_N[model]
        if model == 'sea':
            lev = GRIDS['sea'].index(n)
            i = N_PER_CELL * int(G3_SYSTEM[1:])
            a = seed_a(i, lev, SETS9['DEV9']['off'])
            mem = dict(key=key_of(g3, n, 'A20', a) + '__mem', model=model, set='DEV9', sysid=g3, ci=int(G3_SYSTEM[1:]),
                       sys_seed=SETS9['DEV9']['base'] + 1000 * int(G3_SYSTEM[1:]), i=i, r=0, n=n, role='mem', cond='A20',
                       seed=a, level=lev, gate='G3')
        else:
            ci = int(G3_SYSTEM[1:])
            mem = dict(key=key_of(g3, n, 'A20') + '__mem', model=model, set='DEV9', sysid=g3, ci=ci,
                       sys_seed=SETS9['DEV9']['base'] + 1000 * ci, i=N_PER_CELL * ci, r=0, n=n, role='mem', cond='A20',
                       gate='G3')
        special.append(mem)
    if model == 'sea':
        special.append(dict(first, key=first['key'] + '__zdag', role='zerodag', zero_dag=True, of=first['key'], gate='G5'))
    return timing, special


# ---------------------------------------------------------------- Study 1 / Study 7 reproduction inputs (G5)
REPRO1 = {'sysid': 'HELD-c0-r0', 'ci': 0, 'seed': 300000}    # Study 1 held-out system of cell 0 (linear), base 300000


def repro1_jobs(model):
    """Study 1 inputs rebuilt with the frozen P-N1 assemble (n = 500): k0 and A20; FoundCause k0 only (time)."""
    conds = (('-', 0),) if model == 'foundcause' else (('-', 0), ('A', 20))
    return [dict(key=f"S1REPRO__{REPRO1['sysid']}__{typ}__k{k}__main", model=model, role='repro1', typ=typ, k=k,
                 of=f"{REPRO1['sysid']}__{typ}__k{k}__main", gate='G5', **REPRO1) for typ, k in conds]


def repro8_job():
    """Study 7 input PN8-c0-r0, k0, seed a_0 = 600000, rebuilt with the frozen P-N8 builder."""
    return dict(key='S7REPRO__PN8-c0-r0__k0__s600000', model='sea', role='repro8', kind='syn', set='PN8', sysid='PN8-c0-r0',
                ci=0, sys_seed=500000, i=0, r=0, cond='k0', seed=600000, of='PN8-c0-r0__k0__s600000', gate='G5')


# ---------------------------------------------------------------- outputs and readings
def out_path(model, key):
    return OUT9 / model / f'{key}.npz'


def load(model, key):
    f = out_path(model, key)
    if not f.exists():
        return None
    z = np.load(f, allow_pickle=False)
    d = {kk: z[kk] for kk in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


def save_npz(path, **arrays):
    """Atomic save: a run killed while saving leaves only a .part file, never a truncated .npz."""
    tmp = path.with_name(path.name + '.part')
    with open(tmp, 'wb') as f:
        np.savez_compressed(f, **arrays)
    os.replace(tmp, path)


def is_done(model, key, input_sha):
    """Resume rule (rules §1): skip a job only if its output exists, is readable and has this key and input hash. An output
    that exists but does not match stops the runner; it is never overwritten."""
    if not out_path(model, key).exists():
        return False
    try:
        meta = load(model, key)['meta']
        ok = meta['key'] == key and meta['input_sha'] == input_sha
    except Exception as e:
        ok = False
        print('unreadable output', key, repr(e), flush=True)
    if not ok:
        sys.exit(f'existing output of {key} is not valid (key, input hash or file): check it and remove it by hand')
    return True


def skeleton(model, out, dT):
    """dT x dT 0/1 skeleton of the target block with the NATIVE reading (rules §1)."""
    if model in MODELS:
        return M1.skel_native(model, out, dT)
    if model == 'sea':
        return C8.as_matrix(C8.skel(out['prob'], dT), dT)
    s = np.asarray(out['skel'])[:dT, :dT]
    return ((s + s.T) > 0).astype(np.int8)


def f1(model, out, g):
    return float(M1.f1(skeleton(model, out, g.shape[0]), np.asarray(g)))


def flips(model, out1, out0, dT):
    return int(M1.flips(skeleton(model, out1, dT), skeleton(model, out0, dT)))


# ---------------------------------------------------------------- process memory (Windows), as the P-N8 SEA wrapper
def peak_wset_mb():
    import ctypes
    import ctypes.wintypes as wt

    class PMC(ctypes.Structure):
        _fields_ = [('cb', wt.DWORD), ('PageFaultCount', wt.DWORD), ('PeakWorkingSetSize', ctypes.c_size_t),
                    ('WorkingSetSize', ctypes.c_size_t), ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                    ('QuotaPagedPoolUsage', ctypes.c_size_t), ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                    ('QuotaNonPagedPoolUsage', ctypes.c_size_t), ('PagefileUsage', ctypes.c_size_t),
                    ('PeakPagefileUsage', ctypes.c_size_t)]
    pmc = PMC()
    pmc.cb = ctypes.sizeof(PMC)
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    k32.GetCurrentProcess.restype = wt.HANDLE
    k32.K32GetProcessMemoryInfo.argtypes = [wt.HANDLE, ctypes.POINTER(PMC), wt.DWORD]
    k32.K32GetProcessMemoryInfo.restype = wt.BOOL
    assert k32.K32GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb), 'GetProcessMemoryInfo failed'
    return pmc.PeakWorkingSetSize / 2 ** 20
