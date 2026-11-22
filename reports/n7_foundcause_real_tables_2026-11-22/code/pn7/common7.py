"""P-N7 common (rules PN7 v1, locked 7bc40f8): sets, jobs, inputs, FoundCause calls, schedule checks.

Frozen modules imported unchanged (rules §10): P-N5 common5.py (real-table and DEV5 stand-in inputs; it imports P-N2
common2.py and P-N1 common.py); P-N1 metrics.py (skel_native) and fc_adapter.py (predict_sched).
"""
import sys, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RUNS7 = HERE.parent                                   # artifacts/n7_runs
ART = RUNS7.parent                                    # artifacts
REPO = ART.parent                                     # safety_prior
ENV = ART / 'n1_models_cpu'
OUT7 = RUNS7 / 'pn7_out'
OUT5 = ART / 'n5_runs' / 'pn5_out'
OUT1 = ART / 'n1_runs' / 'pn1_out'
REPORT = REPO / 'reports' / 'n7_foundcause_real_tables_2026-11-22'
INPUTS5 = REPO / 'reports' / 'n5_real_data_consistency_2026-11-22' / 'checks' / 'inputs5.json'
for _sub in ('n5_runs/pn5', 'n1_runs/pn1'):            # frozen modules ahead of site-packages
    if str(ART / _sub) not in sys.path:
        sys.path.insert(1, str(ART / _sub))
import common5 as C5                                   # frozen P-N5 (imports frozen P-N2 common2 and P-N1 common)
from common import sha                                 # frozen P-N1

TABLES = ('sachs', 'wine')
R_DRAWS = 20                                           # rules §1: all 20 P-N5 draws
DEV_DRAWS = 2                                          # rules §7: the two DEV5 draws
BASES_REF = (1042, 2042, 3042, 4042)                   # rules §3
DEV_BASES_REF = (1042,)                                # rules §7, G7: one base on DEV7
THREADS = 4                                            # as P-N1's FoundCause runs
BUDGET_S = 3 * 3600                                    # per run (rules §10)
ADAPTER_TOL = 1e-6                                     # rules §2 (P-N1 condition)
FC_KW = dict(n_runs=10, temperature=1.0, max_samples=5000)
FC_SRC = ENV / 'repos' / 'foundcause' / 'foundcause.py'
FC_CKPT = ENV / 'checkpoints' / 'foundcause' / 'checkpoint.pt'
P1_DEV = dict(sysid='DEV-c0-r0', ci=0, seed=100000, key='DEV-c0-r0__-__k0__main')   # G2 reference (P-N1 DEV)
COMPARE = ('probs', 'adj_native', 'agreement', 'threshold', 'C')
DT = 11


def jobs7(set_name, table=None):
    """Ordered jobs (rules §6-§8). k0 checks first (rerun, adapter at base 42), then the padded draws, then the
    schedule reference. DEV7 adds the P-N1 DEV input for G2 at the end."""
    if set_name == 'DEV7':
        t, draws, bases, s5 = 'standin', DEV_DRAWS, DEV_BASES_REF, 'DEV5'
    else:
        assert table in TABLES
        t, draws, bases, s5 = table, R_DRAWS, BASES_REF, 'PN5'
    out = [dict(set=set_name, s5=s5, table=t, cond='k0', r=None, variant='api'),
           dict(set=set_name, s5=s5, table=t, cond='k0', r=None, variant='rep'),
           dict(set=set_name, s5=s5, table=t, cond='k0', r=None, variant='sched42')]
    out += [dict(set=set_name, s5=s5, table=t, cond='k20_e0', r=r, variant='api') for r in range(draws)]
    out += [dict(set=set_name, s5=s5, table=t, cond='k0', r=None, variant=f'sched{b}') for b in bases]
    if set_name == 'DEV7':
        out.append(dict(set='DEV7', s5=None, table='p1dev', cond='k0', r=None, variant='api'))
    return out


def input_key(j):
    if j['table'] == 'p1dev':
        return P1_DEV['key']
    return C5.key5(j['table'], j['cond'], j['r'])


def key7(j):
    return f"{input_key(j)}__{j['variant']}"


def base_of(j):
    v = j['variant']
    return None if v in ('api', 'rep') else int(v[len('sched'):])


def assemble7(j):
    """(X, d_T). Real tables and the DEV5 stand-in: frozen assemble5 (asserts the bitwise real block). G2: the frozen
    P-N1 assemble of DEV-c0-r0 at k = 0."""
    if j['table'] == 'p1dev':
        from common import assemble
        x, t, _, _ = assemble(P1_DEV['sysid'], P1_DEV['ci'], P1_DEV['seed'], '-', 0)
        return np.ascontiguousarray(x), int(t['x'].shape[1])
    X, rb, _ = C5.assemble5(j['s5'], j['table'], j['cond'], j['r'])
    return np.ascontiguousarray(X), int(rb['XR'].shape[1])


def load_fc():
    """FoundCause exactly as P-N1 run_model.py (rules §2): package API or the frozen P-N1 adapter."""
    import torch
    torch.set_num_threads(THREADS)
    sys.path.insert(0, str(ENV / 'repos' / 'foundcause'))
    import foundcause as fcm
    from fc_adapter import predict_sched                # frozen P-N1
    ck = torch.load(FC_CKPT, map_location='cpu', weights_only=True, mmap=True)
    with torch.device('meta'):
        m = fcm.CausalDiscoveryTransformer(fcm.ModelConfig())
    m.load_state_dict(ck['model_state_dict'], strict=True, assign=True)
    m.eval()

    def call(x, base=None):
        with torch.inference_mode():
            if base is None:
                o = fcm.predict(m, x, torch.device('cpu'), **FC_KW)
            else:
                o = predict_sched(m, x, torch.device('cpu'), base=base, **FC_KW)
        return dict(probs=np.asarray(o['probabilities'], np.float64), adj_native=np.asarray(o['adjacency'], np.int8),
                    agreement=np.asarray(o['agreement'], np.float64), threshold=np.float64(o['threshold']),
                    C=np.asarray(o['C'], np.float64), dropped=np.asarray(o['dropped'], np.int64),
                    n_duplicates=np.int64(len(o['duplicates'])))
    return call


def out_file(j):
    return OUT7 / 'foundcause' / f'{key7(j)}.npz'


def load_out(j):
    z = np.load(out_file(j), allow_pickle=False)
    d = {n: z[n] for n in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


# ---- schedule checks (rules §6, G3c): no model call
SCHED_LINES = (
    'n_take = int(np.ceil(0.9 * min(n_orig, max_samples))) if n_orig > 50 else min(n_orig, max_samples)',
    'rng_eval = np.random.RandomState(42 + run_i)',
    'X_use = X[rng_eval.choice(n_orig, n_take, replace=False)]',
    'col_perm = rng_eval.permutation(d)',
)


def schedule_source_check():
    """The row-subsampling and permutation lines of the hashed package source, once each and in this order."""
    src = FC_SRC.read_text(encoding='utf-8')
    start = src.index('def predict(model, X, device')
    nxt = src.find('\ndef ', start + 1)
    body = src[start:] if nxt < 0 else src[start:nxt]
    pos = [body.find(s) for s in SCHED_LINES]
    counts = [body.count(s) for s in SCHED_LINES]
    ok = all(c == 1 for c in counts) and all(p >= 0 for p in pos) and pos[1] < pos[2] < pos[3]
    return dict(ok=bool(ok), counts=counts, positions=pos)


def row_indices(n_orig, base=42, n_runs=FC_KW['n_runs'], max_samples=FC_KW['max_samples']):
    """Rows used by each run of the schedule, by the package's own formula (SCHED_LINES)."""
    n_take = int(np.ceil(0.9 * min(n_orig, max_samples))) if n_orig > 50 else min(n_orig, max_samples)
    out = []
    for run_i in range(n_runs):
        rng = np.random.RandomState(base + run_i)
        out.append(rng.choice(n_orig, n_take, replace=False) if n_take < n_orig else np.arange(n_orig))
    return out


def max_abs_diff(a, b):
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    if a.shape != b.shape:
        return float('inf')
    return float(np.max(np.abs(a - b))) if a.size else 0.0


def bitwise_equal(o1, o2, keys=COMPARE):
    return all(np.array_equal(np.asarray(o1[k]), np.asarray(o2[k])) for k in keys)
