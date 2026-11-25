"""P-N9 / Study 8 self-test of the reading, completeness and main-run code paths, before the freeze.

Why: gate G6 only exercises the components that the DEV outputs allow (6 of 11; no SEA, no FoundCause at n = 500), and the
main-run path of the runners (header check, budget, resume) is not used in DEV at all. This script runs those paths on
synthetic outputs with random graphs, and on DEV inputs for the runners. It generates no held-out input (system seeds
990000+, never used elsewhere; random graphs instead of the simulator) and reads no DEV output value.

Parts (usage: python -I selftest9.py [reading] [completeness] [runners]; default all three):
  reading       analyze9.py PN9 on synthetic outputs of 120 systems in five scenarios; every component (theta, se, df, p,
                Holm, label), every descriptive value and rho are compared with an independent implementation in this file;
                planned labels are checked in the clear-cut scenarios; the figures of scenario 'effects' are kept
  completeness  completeness9.py on synthetic logs: passes on complete data, fails on each injected fault
  runners       run9.py (AVICI), run9_sea.py, run9_classical.py in mode R1 on DEV inputs: refusal without a header, outputs
                bitwise equal to the DEV outputs, resume, budget stop, refusal of an invalid existing output
Writes reports/n9_sample_size_2026-11-24/checks/selftest9.json; exit 0 only if every check passed.
"""
import json
import math
import os
import runpy
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ------------------------------------------------------------------ driver: run one P-N9 script with redirected paths
if len(sys.argv) > 1 and sys.argv[1] == '--drive':
    _, _, script, cfgfile, *args = sys.argv
    cfg = json.loads(Path(cfgfile).read_text())
    sys.argv = [script, *args]
    if script in ('run9.py',):                           # thread settings must precede numpy, as in the script itself
        for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
            os.environ[v] = '2'
    import numpy as np
    import common9 as C
    tmp = Path(cfg['tmp'])
    C.OUT9, C.WORK9, C.RUNS9, C.REPORT = tmp / 'pn9_out', tmp / 'pn9_work', tmp, tmp / 'report'
    C.SETS9['PN9'] = dict(base=cfg['base'], reps=cfg['reps'], off=cfg['off'])
    if cfg.get('budget'):
        C.BUDGET_H.clear()
        C.BUDGET_H.update(cfg['budget'])
    if cfg.get('fake_inputs'):
        def _fake(sysid, ci, seed, n):
            dT = C.CELLS[ci][0]
            rng = np.random.default_rng([seed, n])
            return dict(k0=rng.standard_normal((4, dT)).astype(np.float32),
                        A20=rng.standard_normal((4, dT + C.K)).astype(np.float32), g=np.zeros((dT, dT), np.int8), dT=dT,
                        seed_used=seed, rejected=[])
        C.inputs_at = _fake
    if cfg.get('graphs'):
        _G = np.load(cfg['graphs'])
        C.target_raw = lambda sysid, ci, seed: dict(g=_G[sysid], x=None)
    runpy.run_path(str(HERE / script), run_name='__main__')
    sys.exit(0)

import numpy as np
from scipy import stats
import common9 as C
import stats9 as S

PY = sys.executable
ROOT = C.RUNS9 / 'pn9_selftest'
BASE = 990000                                             # selftest system seeds (no P-N9 set uses them)
CHECKS_REAL = C.REPORT / 'checks'
results, t0 = {}, time.time()


def drive(script, cfg, *args):
    f = Path(cfg['tmp']) / 'cfg.json'
    f.write_text(json.dumps(cfg))
    return subprocess.run([PY, '-I', str(HERE / 'selftest9.py'), '--drive', script, str(f), *args], capture_output=True,
                          text=True, encoding='utf-8', errors='replace')


def systems():
    return [(f'PN9-c{ci}-r{r}', ci, BASE + 1000 * ci + r, C.N_PER_CELL * ci + r) for ci in range(8) for r in range(C.N_PER_CELL)]


# ------------------------------------------------------------------ synthetic outputs
def make_graphs(seed):
    rng = np.random.default_rng(seed)
    G = {}
    for sysid, ci, s, i in systems():
        d, e = C.CELLS[ci][0], C.CELLS[ci][1]
        perm = rng.permutation(d)
        g = np.zeros((d, d), np.int8)
        iu = np.triu_indices(d, 1)
        pick = rng.random(len(iu[0])) < min(0.9, 2 * d * e / (d * (d - 1)))
        if not pick.any():
            pick[0] = True
        for a, b in zip(iu[0][pick], iu[1][pick]):
            g[perm[a], perm[b]] = 1
        G[sysid] = g
    return G


def pairs_of(g):
    return {(i, j) for i in range(len(g)) for j in range(i + 1, len(g)) if g[i, j] or g[j, i]}


def perturb(rng, true, d, n_drop, n_add):
    """Skeleton as a set of pairs: the true one without n_drop edges and with n_add wrong edges."""
    t = sorted(true)
    drop = {t[k] for k in rng.permutation(len(t))[:min(n_drop, len(t))]}
    out = [(i, j) for i in range(d) for j in range(i + 1, d) if (i, j) not in true]
    add = {out[k] for k in rng.permutation(len(out))[:min(n_add, len(out))]}
    return (true - drop) | add


def prob_matrix(rng, sk, d, D, thr=0.5):
    """Random pair probabilities whose skeleton at threshold thr is exactly sk on the target block."""
    P = rng.random((D, D)) * thr * 0.9
    np.fill_diagonal(P, 0)
    for i, j in sk:
        a, b = (i, j) if rng.random() < 0.5 else (j, i)
        P[a, b] = thr + (1 - thr) * (0.05 + 0.9 * rng.random())
    return P


def write(model, key, rec, **arrays):
    f = OUT / model / f'{key}.npz'
    f.parent.mkdir(parents=True, exist_ok=True)
    C.save_npz(f, meta=np.array(json.dumps(rec)), **arrays)


def out_arrays(model, rng, sk, d, D):
    if model == 'avici':
        return dict(probs=prob_matrix(rng, sk, d, D))
    if model in ('cdfm', 'foundcause'):
        thr = float(rng.uniform(0.3, 0.7)) if model == 'cdfm' else 0.5
        P = prob_matrix(rng, sk, d, D, thr)
        a = (P > thr).astype(np.int8)
        return dict(probs=P, adj_native=a, threshold=thr, **(dict(logits=P) if model == 'cdfm' else dict(agreement=P, C=P)))
    if model == 'sea':
        return dict(prob=prob_matrix(rng, sk, d, D))
    m = np.zeros((D, D), np.int8)
    for i, j in sk:
        m[i, j] = m[j, i] = 1
    return dict(skel=m)


def scenario_drops(name, model, n, rng):
    """Number of true edges lost at k = 20 beyond k = 0 (the size of the effect) for one system."""
    nn = C.GRIDS[model]
    pos = math.log2(n / min(nn)) / math.log2(max(nn) / min(nn))
    noise = int(rng.integers(0, 2))
    if name == 'null':
        return noise if rng.random() < 0.5 else 0
    if name == 'zero':
        return 0
    if name == 'effects':
        return {'avici': 2 + noise if n == 200 else 5 + noise, 'cdfm': int(round(5 * (1 - pos))) + noise, 'foundcause': 4 + noise,
                'sea': 4, 'pc': noise, 'ges': noise}[model]
    if name == 'ushape':
        return {'avici': 5 + noise if n == 200 else 1 + noise, 'cdfm': int(round(6 * abs(2 * pos - 1))) + noise,
                'foundcause': int(round(6 * abs(2 * pos - 1))), 'sea': int(round(6 * abs(2 * pos - 1))), 'pc': noise,
                'ges': noise}[model]
    if name == 'both':                                     # a trend inside the margins: both labels of a pair
        x = {'avici': 0.5 if n == 200 else 1.4, 'cdfm': 2.6 * (1 - pos), 'foundcause': 1.8 * (1 - pos), 'sea': 2.4 - 1.4 * pos,
             'pc': 0.3, 'ges': 0.3}[model]
        return int(np.floor(x + rng.random()))
    return int(rng.integers(0, 6))                         # 'noisy'


def build_outputs(name, seed, G):
    rng = np.random.default_rng([seed, 17])
    for sysid, ci, s, i in systems():
        g = G[sysid]
        d, D1 = len(g), len(g) + C.K
        true = pairs_of(g)
        for model in C.ALL:
            if model in C.CLASSICAL and ci not in C.LINEAR:
                continue
            for lev, n in enumerate(C.GRIDS[model]):
                base_drop = 0 if name == 'zero' else int(rng.integers(0, 2))
                s0 = perturb(rng, true, d, base_drop, 0 if name == 'zero' else int(rng.integers(0, 2)))
                eff = scenario_drops(name, model, n, rng)
                t0_ = sorted(s0 & true)
                lost = {t0_[k] for k in rng.permutation(len(t0_))[:eff]}
                s1 = s0 - lost if name != 'noisy' else perturb(rng, true, d, eff, int(rng.integers(0, 4)))
                base = dict(status='ok', n=n)
                if model == 'sea':
                    a = C.seed_a(i, lev)
                    write('sea', C.key_of(sysid, n, 'k0', a), dict(base, seed=a), **out_arrays('sea', rng, s0, d, d))
                    write('sea', C.key_of(sysid, n, 'A20', a), dict(base, seed=a), **out_arrays('sea', rng, s1, d, D1))
                    for m in range(1, C.M_REF + 1):
                        b = C.seed_b(i, lev, m)
                        sr = s0 if name == 'zero' else s0 ^ ({sorted(s0)[0]} if s0 and rng.random() < 0.5 else set())
                        write('sea', C.key_of(sysid, n, 'k0', b), dict(base, seed=b), **out_arrays('sea', rng, sr, d, d))
                else:
                    write(model, C.key_of(sysid, n, 'k0'), base, **out_arrays(model, rng, s0, d, d))
                    write(model, C.key_of(sysid, n, 'A20'), base, **out_arrays(model, rng, s1, d, D1))


# ------------------------------------------------------------------ independent reading
def ind_load(model, key):
    z = np.load(OUT / model / f'{key}.npz', allow_pickle=False)
    return {k: z[k] for k in z.files if k != 'meta'}


def ind_skel(model, o, d, rule='native', thr=None):
    s = set()
    for i in range(d):
        for j in range(i + 1, d):
            if model in ('pc', 'ges'):
                on = o['skel'][i, j] != 0 or o['skel'][j, i] != 0
            elif model == 'avici' or rule == 'fixed':
                on = max(o['probs'][i, j], o['probs'][j, i]) > 0.5
            elif rule == 'frozen':
                on = o['probs'][i, j] > thr or o['probs'][j, i] > thr
            elif model == 'sea':
                on = (o['prob'][i, j] + o['prob'][j, i] > 0.5) if rule == 'alt' else max(o['prob'][i, j], o['prob'][j, i]) > 0.5
            else:
                on = o['adj_native'][i, j] != 0 or o['adj_native'][j, i] != 0
            if on:
                s.add((i, j))
    return s


def ind_f1(s, t):
    tp = len(s & t)
    if tp == 0:
        return 0.0
    pr, rc = tp / len(s), tp / len(t)
    return 2 * pr * rc / (pr + rc)


def ind_dp(p1, p0, d):
    return float(np.mean([abs(p1[i, j] - p0[i, j]) for i in range(d) for j in range(d) if i != j]))


def ind_values(G):
    V = {}
    for sysid, ci, s, i in systems():
        t, d = pairs_of(G[sysid]), len(G[sysid])
        for model in C.ALL:
            if model in C.CLASSICAL and ci not in C.LINEAR:
                continue
            for lev, n in enumerate(C.GRIDS[model]):
                if model == 'sea':
                    o0, o1 = (ind_load('sea', f'{sysid}__n{n}__{c}__s{740000 + 10 * i + lev}') for c in ('k0', 'A20'))
                    refs = [ind_load('sea', f'{sysid}__n{n}__k0__s{750000 + 100 * i + 10 * lev + m}') for m in (1, 2, 3, 4)]
                else:
                    o0, o1 = (ind_load(model, f'{sysid}__n{n}__{c}') for c in ('k0', 'A20'))
                s0, s1 = ind_skel(model, o0, d), ind_skel(model, o1, d)
                v = dict(f1_0=ind_f1(s0, t), f1_1=ind_f1(s1, t), flips=len(s0 ^ s1))
                v['H'] = v['f1_0'] - v['f1_1']
                if model not in C.CLASSICAL:
                    pk = 'prob' if model == 'sea' else 'probs'
                    v['dp'] = ind_dp(o1[pk], o0[pk], d)
                if model == 'cdfm':
                    v['H_fixed'] = ind_f1(ind_skel(model, o0, d, 'fixed'), t) - ind_f1(ind_skel(model, o1, d, 'fixed'), t)
                    v['H_frozen'] = v['f1_0'] - ind_f1(ind_skel(model, o1, d, 'frozen', float(o0['threshold'])), t)
                if model == 'sea':
                    sr = [ind_skel('sea', r, d) for r in refs]
                    v['delta'] = sum(len(s1 ^ x) - len(s0 ^ x) for x in sr) / 4
                    v['flips_seed'] = sum(len(s0 ^ x) for x in sr) / 4
                    v['dp_seed'] = sum(ind_dp(r['prob'], o0['prob'], d) for r in refs) / 4
                    a0, a1, ar = ind_skel('sea', o0, d, 'alt'), ind_skel('sea', o1, d, 'alt'), [ind_skel('sea', r, d, 'alt') for r in refs]
                    v['delta_alt'] = sum(len(a1 ^ x) - len(a0 ^ x) for x in ar) / 4
                    v['H_alt'] = ind_f1(a0, t) - ind_f1(a1, t)
                V[(model, sysid, n)] = dict(v, ci=ci)
    return V


def ind_strat(x, c):
    cells = sorted(set(c))
    theta = sum(sum(v for v, k in zip(x, c) if k == cell) / sum(1 for k in c if k == cell) for cell in cells) / len(cells)
    var, den = 0.0, 0.0
    for cell in cells:
        v = [a for a, k in zip(x, c) if k == cell]
        mu = sum(v) / len(v)
        a = sum((q - mu) ** 2 for q in v) / (len(v) - 1) / len(v) / len(cells) ** 2
        var += a
        den += a ** 2 / (len(v) - 1)
    if var == 0:
        return dict(theta=theta, se=0.0, df=None)
    se, df = math.sqrt(var), var ** 2 / den
    q = stats.t.ppf(0.975, df)
    return dict(theta=theta, se=se, df=df, ci95=[theta - q * se, theta + q * se])


def up(r, c):       # p for H0: theta <= c
    return 1.0 if r['df'] is None else float(stats.t.cdf((c - r['theta']) / r['se'], r['df']))


def lo(r, c):       # p for H0: theta >= c
    return 1.0 if r['df'] is None else float(stats.t.cdf((r['theta'] - c) / r['se'], r['df']))


def ind_reading(V):
    sysc = [(s, ci) for s, ci, _, _ in systems()]
    lin = [(s, ci) for s, ci in sysc if ci in (0, 2, 4, 6)]

    def get(model, n, f, sel=sysc):
        return [V[(model, s, n)][f] for s, _ in sel], [ci for _, ci in sel]

    def diff(model, n, n0, f):
        return [V[(model, s, n)][f] - V[(model, s, n0)][f] for s, _ in sysc], [ci for _, ci in sysc]

    def slope(model, f):
        lv = C.GRIDS[model]
        return [float(np.polyfit([math.log2(n) for n in lv], [V[(model, s, n)][f] for n in lv], 1)[0]) for s, _ in sysc], \
            [ci for _, ci in sysc]
    R, P = {}, {}
    for cid, (m, n, f) in {'A1': ('avici', 200, 'H'), 'C1': ('cdfm', 4000, 'H'), 'S1': ('sea', 20000, 'delta')}.items():
        R[cid] = ind_strat(*get(m, n, f))
        P[cid] = up(R[cid], 0)
    R['A2d'] = R['A2s'] = ind_strat(*diff('avici', 500, 200, 'H'))
    P['A2d'] = min(1.0, 2 * min(up(R['A2d'], 0), lo(R['A2d'], 0)))
    P['A2s'] = max(up(R['A2d'], -0.05), lo(R['A2d'], 0.05)) if R['A2d']['df'] is not None else 1.0
    cs = {'C2s': ('cdfm', 'H', 0.05 / math.log2(40)), 'F1s': ('foundcause', 'H', 0.05 / 2), 'S2s': ('sea', 'delta', 1 / math.log2(40))}
    for cid, (m, f, c) in cs.items():
        R[cid] = ind_strat(*slope(m, f))
        P[cid] = lo(R[cid], -c)
    ts = {'C2t': ('cdfm', 'H', (100, 200, 1000, 2000, 4000), 0.05), 'F1t': ('foundcause', 'H', (125, 200), 0.05),
          'S2t': ('sea', 'delta', (1000, 2000, 5000, 20000), 1.0)}
    for cid, (m, f, lv, mg) in ts.items():
        rs = [ind_strat(*diff(m, n, 500, f)) for n in lv]
        P[cid] = max(1.0 if r['df'] is None else max(up(r, -mg), lo(r, mg)) for r in rs)
    order, rej, alive = sorted(P, key=lambda k: P[k]), {}, True
    for k, cid in enumerate(order):
        alive = alive and P[cid] <= 0.05 / (len(order) - k)
        rej[cid] = alive
    L = {}
    for cid, mg in (('A1', 0.05), ('C1', 0.05), ('S1', 1.0)):
        L[cid] = 'NOT_CONFIRMED' if not rej[cid] else ('PERSISTS' if R[cid]['theta'] >= mg else 'PRESENT_BELOW_MARGIN')
    a2 = (['SIMILAR'] if rej['A2s'] else []) + ([('HIGHER' if R['A2d']['theta'] > 0 else 'LOWER')] if rej['A2d'] else [])
    L['A2'] = ' + '.join(a2) or 'UNCLEAR'
    for t in ('C2', 'F1', 'S2'):
        L[t] = ' + '.join((['SHRINKS'] if rej[t + 's'] else []) + (['STABLE'] if rej[t + 't'] else [])) or 'UNCLEAR'
    D = {}
    for m in C.ALL:
        sel = lin if m in C.CLASSICAL else sysc
        for n in C.GRIDS[m]:
            for f in V[(m, sel[0][0], n)]:
                if f != 'ci':
                    D[(m, n, f)] = ind_strat(*get(m, n, f, sel))
    B = {}
    for m in C.MODELS + ('sea',):
        for n in C.GRIDS[m]:
            if n in C.GRIDS['ges']:
                B[(m, n)] = ind_strat([V[(m, s, n)]['H'] - max(V[('pc', s, n)]['H'], V[('ges', s, n)]['H']) for s, _ in lin],
                                      [ci for _, ci in lin])
    rho = {}
    for m in C.ALL:
        sel = lin if m in C.CLASSICAL else sysc
        f = 'delta' if m == 'sea' else 'H'
        rho[m] = [[float(np.corrcoef([V[(m, s, a)][f] for s, _ in sel], [V[(m, s, b)][f] for s, _ in sel])[0, 1])
                   for b in C.GRIDS[m]] for a in C.GRIDS[m]]
    return R, P, rej, L, D, B, rho


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b)) or (math.isnan(a) and math.isnan(b))


EXPECT = {'effects': {'A1': 'PERSISTS', 'A2': 'HIGHER', 'C2': 'SHRINKS', 'F1': 'STABLE', 'S1': 'PERSISTS', 'S2': 'STABLE'},
          'null': {'A2': 'SIMILAR', 'C2': 'STABLE', 'F1': 'STABLE', 'S2': 'STABLE'},
          'ushape': {'A2': 'LOWER', 'C2': 'UNCLEAR', 'F1': 'UNCLEAR', 'S2': 'UNCLEAR'},
          'zero': {'A1': 'NOT_CONFIRMED', 'A2': 'UNCLEAR', 'C1': 'NOT_CONFIRMED', 'C2': 'UNCLEAR', 'F1': 'UNCLEAR',
                   'S1': 'NOT_CONFIRMED', 'S2': 'UNCLEAR'},
          'both': {}, 'noisy': {}}


def part_reading():
    global OUT
    res = {}
    for k, name in enumerate(EXPECT):
        tmp = ROOT / f'reading_{name}'
        if tmp.exists():
            shutil.rmtree(tmp)
        OUT = tmp / 'pn9_out'
        (tmp / 'report' / 'checks').mkdir(parents=True)
        G = make_graphs(100 + k)
        build_outputs(name, 200 + k, G)
        np.savez(tmp / 'graphs.npz', **G)
        cfg = dict(tmp=str(tmp), base=BASE, reps=15, off=0, graphs=str(tmp / 'graphs.npz'))
        refuse = drive('analyze9.py', cfg, 'PN9')
        (tmp / 'report/checks/pn9_completeness.json').write_text(json.dumps(dict(ok=False)))
        refuse2 = drive('analyze9.py', cfg, 'PN9')
        (tmp / 'report/checks/pn9_completeness.json').write_text(json.dumps(dict(ok=True)))
        p = drive('analyze9.py', cfg, 'PN9')
        r = dict(refuses_without_completeness=refuse.returncode != 0 and 'no reading' in refuse.stderr,
                 refuses_if_failed=refuse2.returncode != 0 and 'no reading' in refuse2.stderr, returncode=p.returncode)
        if p.returncode != 0:
            r['stderr'] = p.stderr[-1500:]
            res[name] = dict(ok=False, **r)
            continue
        J = json.loads((tmp / 'report/checks/pn9_reading.json').read_text())
        V = ind_values(G)
        R, P, rej, L, D, B, rho = ind_reading(V)
        bad = []
        for cid, c in J['components'].items():
            if not close(c['p'], P[cid], 1e-7) or c['holm']['rejected'] is not bool(rej[cid]):
                bad.append(f"{cid}: p {c['p']} vs {P[cid]}, rejected {c['holm']['rejected']} vs {rej[cid]}")
            if c['res'] is not None and cid in R:
                bad += [f'{cid}.{f}' for f in ('theta', 'se', 'df') if not close(c['res'][f], R[cid][f], 1e-8)]
        bad += [f'label {t}: {J["labels"].get(t)} vs {v}' for t, v in L.items() if J['labels'].get(t) != v]
        n_desc = 0
        for (m, n, f), v in D.items():
            q = J['descriptive'][m][str(n)].get(f)
            n_desc += 1
            if q is None or not close(q['theta'], v['theta'], 1e-8) or not close(q['se'], v['se'], 1e-8):
                bad.append(f'descriptive {m} {n} {f}')
        extra = sum(len(J['descriptive'][m][str(n)]) for m in C.ALL for n in C.GRIDS[m]) - n_desc
        if extra:
            bad.append(f'{extra} descriptive fields not covered by the independent reading')
        for (m, n), v in B.items():
            q = J['beyond_classical_linear'][m][str(n)]
            if q is None or not close(q['theta'], v['theta'], 1e-8):
                bad.append(f'beyond {m} {n}')
        for m in C.ALL:
            for x, y in zip(J['rho'][m], rho[m]):
                bad += [f'rho {m}' for u, w in zip(x, y) if not close(u, w, 1e-8)]
        for cid, mg in (('A1', 0.05), ('C1', 0.05), ('S1', 1.0), ('A2d', 0.05)):
            if R[cid]['df'] is not None:
                l_, h_ = R[cid]['ci95']
                want = 'SMALL' if l_ > -mg and h_ < mg else ('LARGE' if l_ > mg or h_ < -mg else 'UNCLEAR')
                if J['size'][cid][1] != want:
                    bad.append(f'size {cid}: {J["size"][cid]} vs {want}')
        miss = {t: (J['labels'].get(t), v) for t, v in EXPECT[name].items() if J['labels'].get(t) != v}
        figs = sorted(f.name for f in (tmp / 'figures').glob('*'))
        r.update(labels=J['labels'], n_descriptive_compared=n_desc, differences=bad[:20], n_differences=len(bad),
                 planned_labels_missed=miss, figures=figs)
        r['ok'] = bool(not bad and not miss and len(figs) == 8 and r['refuses_without_completeness'] and r['refuses_if_failed'])
        res[name] = r
        print(f"reading {name}: ok={r['ok']} labels={J['labels']} differences={len(bad)} ({time.time() - t0:.0f} s)", flush=True)
    return dict(ok=all(v['ok'] for v in res.values()), scenarios=res)


# ------------------------------------------------------------------ completeness9 on synthetic logs
def fake_sha(seed, ci, n, cond):
    rng = np.random.default_rng([seed, n])
    k0 = rng.standard_normal((4, C.CELLS[ci][0])).astype(np.float32)
    a20 = rng.standard_normal((4, C.CELLS[ci][0] + C.K)).astype(np.float32)
    return C.sha(k0 if cond == 'k0' else a20)


def part_completeness():
    global OUT
    tmp = ROOT / 'completeness'
    if tmp.exists():
        shutil.rmtree(tmp)
    OUT = tmp / 'pn9_out'
    (tmp / 'report' / 'checks').mkdir(parents=True)
    old = dict(C.SETS9['PN9'])
    C.SETS9['PN9'] = dict(base=BASE, reps=15, off=0)
    hdr, logs = [], {}
    for m in C.ALL:
        for run in (('R1', 'R3') if m in C.CLASSICAL else tuple(C.RUN_CELLS)):
            hdr += [dict(label=f'pn9_start_{m}_{run}', ok=True, time_unix=0), dict(label=f'pn9_end_{m}_{run}', ok=True, time_unix=1)]
            recs = []
            for j in C.run_jobs(m, run):
                rec = {k: v for k, v in j.items()}
                rec.update(status='ok', input_sha=fake_sha(j['sys_seed'], j['ci'], j['n'], j['cond']))
                if m == 'sea':
                    rec.update(layout_ok=True, auc_ok=True)
                src = j.get('of', j['key'])
                val = np.frombuffer(src.encode()[:16].ljust(16), np.uint8).reshape(4, 4)
                write(m, j['key'], rec, **({'prob': val} if m == 'sea' else {'probs': val}))
                recs.append(rec)
            logs[(m, run)] = recs
    C.SETS9['PN9'] = old

    def save(L, H):
        (OUT / 'pn9_run_header.json').write_text(json.dumps(H))
        for (m, run), recs in L.items():
            (OUT / f'log_{m}_{run}.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in recs), encoding='utf-8')
    cfg = dict(tmp=str(tmp), base=BASE, reps=15, off=0, fake_inputs=True)

    def run(label):
        p = drive('completeness9.py', cfg)
        f = tmp / 'report/checks/pn9_completeness.json'
        J = json.loads(f.read_text()) if f.exists() else dict(ok=None, problems=[p.stderr[-500:]])
        return p.returncode, J['ok'], J['problems']
    save(logs, hdr)
    rc, ok, prob = run('complete')
    summ = json.loads((tmp / 'report/checks/pn9_completeness.json').read_text())['summary']
    planned = {m: sum(v['planned'] for k, v in summ.items() if k.rsplit('_', 1)[0] == m) for m in C.ALL}
    want = {'avici': 960 + 8, 'cdfm': 1440 + 8, 'foundcause': 720 + 8, 'sea': 3600 + 8, 'pc': 1080 + 4, 'ges': 840 + 4}
    res = dict(complete=dict(ok=bool(rc == 0 and ok is True), problems=prob[:3]), planned=planned, planned_matches_rules=planned == want)
    print('completeness, complete data:', res['complete'], planned, flush=True)
    import copy
    faults = {}

    def fault(name, mutate, expect):
        L, H = copy.deepcopy(logs), copy.deepcopy(hdr)
        undo = mutate(L, H)
        save(L, H)
        rc_, ok_, pr_ = run(name)
        if undo:
            undo()
        faults[name] = dict(detected=bool(rc_ == 1 and ok_ is False and any(expect in x for x in pr_)), n_problems=len(pr_),
                            first=pr_[:1])
        print('fault', name, faults[name]['detected'], flush=True)

    def rm_output(L, H):
        f = OUT / 'avici' / f"{L[('avici', 'R2')][3]['key']}.npz"
        g = f.with_suffix('.bak')
        f.rename(g)
        return lambda: g.rename(f)

    def change_rerun(L, H):
        k = next(r for r in L[('cdfm', 'R4')] if r['role'] == 'rerun')
        f = OUT / 'cdfm' / f"{k['key']}.npz"
        keep = f.read_bytes()
        C.save_npz(f, meta=np.array(json.dumps(k)), probs=np.zeros((4, 4), np.uint8))
        return lambda: f.write_bytes(keep)
    fault('missing output', rm_output, 'has 1 records or no output')
    fault('duplicate record', lambda L, H: L[('pc', 'R1')].append(dict(L[('pc', 'R1')][0])), 'has 2 records')
    fault('missing record', lambda L, H: L[('ges', 'R3')].pop(5) and None, 'has 0 records')
    fault('wrong input hash', lambda L, H: L[('foundcause', 'R3')][7].update(input_sha='0' * 16), 'input hash differs')
    fault('wrong level', lambda L, H: L[('cdfm', 'R1')][4].update(n=123), 'level or seed differs')
    fault('wrong SEA seed', lambda L, H: L[('sea', 'R1')][4].update(seed=1), 'level or seed differs')
    fault('budget stop record', lambda L, H: L[('sea', 'R4')].append(dict(key=L[('sea', 'R4')][9]['key'], status='budget_stop')),
          'non-ok records')
    fault('error record', lambda L, H: L[('avici', 'R1')].append(dict(key='x', status='error: y')), 'non-ok records')
    fault('rerun differs', change_rerun, 'differs from')
    fault('SEA layout', lambda L, H: L[('sea', 'R2')][11].update(layout_ok=False), 'adapter check')
    fault('SEA auc', lambda L, H: L[('sea', 'R3')][11].update(auc_ok=False), 'adapter check')
    fault('missing end header', lambda L, H: H.remove(next(h for h in H if h['label'] == 'pn9_end_sea_R2')), 'freeze header')
    fault('failed start header', lambda L, H: next(h for h in H if h['label'] == 'pn9_start_ges_R1').update(ok=False), 'freeze header')
    fault('unplanned record', lambda L, H: L[('pc', 'R3')].append(dict(L[('pc', 'R3')][0], key='unplanned')), 'unplanned jobs')
    save(logs, hdr)
    rc, ok, prob = run('restored')
    res['restored_passes'] = bool(rc == 0 and ok is True)
    res['faults'] = faults
    res['ok'] = bool(res['complete']['ok'] and res['planned_matches_rules'] and res['restored_passes'] and
                     all(v['detected'] for v in faults.values()))
    return res


# ------------------------------------------------------------------ main-run path of the runners, on DEV inputs
def part_runners():
    res = {}
    plans = (('run9.py', ('avici', 'R1'), 'avici', 4), ('run9_classical.py', ('pc', 'R1'), 'pc', 4),
             ('run9_classical.py', ('ges', 'R1'), 'ges', 4), ('run9_sea.py', ('R1',), 'sea', 2))
    for script, args, model, limit in plans:
        tmp = ROOT / f'runner_{model}'
        if tmp.exists():
            shutil.rmtree(tmp)
        out = tmp / 'pn9_out'
        out.mkdir(parents=True)
        b = {m: {r: 5.0 for r in C.RUN_CELLS} for m in C.ALL}
        cfg = dict(tmp=str(tmp), base=720000, reps=2, off=1_000_000, budget=b)      # PN9 names on DEV systems
        r = {}
        p = drive(script, cfg, *args, '--limit', str(limit))
        r['refuses_without_header'] = p.returncode != 0 and 'no successful start header' in p.stderr
        (out / 'pn9_run_header.json').write_text(json.dumps([dict(label=f'pn9_start_{model}_R1', ok=False, time_unix=time.time())]))
        p = drive(script, cfg, *args, '--limit', str(limit))
        r['refuses_failed_header'] = p.returncode != 0 and 'no successful start header' in p.stderr
        (out / 'pn9_run_header.json').write_text(json.dumps([dict(label=f'pn9_start_{model}_R1', ok=True, time_unix=time.time())]))
        p1 = drive(script, cfg, *args, '--limit', str(limit // 2))
        n1 = len(list((out / model).glob('*.npz')))
        p2 = drive(script, cfg, *args, '--limit', str(limit // 2))
        made = sorted((out / model).glob('*.npz'))
        r['run_and_resume'] = [p1.returncode, p2.returncode, n1, len(made)]
        same, compared = True, 0
        for f in made:
            ref = C.OUT9 / model / f.name.replace('PN9-', 'DEV9-')
            z1, z2 = np.load(f, allow_pickle=False), np.load(ref, allow_pickle=False)
            same &= set(z1.files) == set(z2.files) and all(np.array_equal(z1[k], z2[k]) for k in z1.files if k != 'meta')
            m1, m2 = json.loads(str(z1['meta'])), json.loads(str(z2['meta']))
            same &= m1['input_sha'] == m2['input_sha']
            compared += 1
        r['equal_to_dev_bitwise'] = bool(same and compared == limit)
        r['no_part_files'] = not list((out / model).glob('*.part'))
        # budget stop: a start time long in the past
        (out / 'pn9_run_header.json').write_text(json.dumps([dict(label=f'pn9_start_{model}_R1', ok=True, time_unix=1.0)]))
        p = drive(script, cfg, *args, '--limit', '1')
        r['budget_stop'] = p.returncode == 2 and 'BUDGET STOP' in p.stdout
        # an existing output with another input hash is refused, not overwritten
        (out / 'pn9_run_header.json').write_text(json.dumps([dict(label=f'pn9_start_{model}_R1', ok=True, time_unix=time.time())]))
        f = made[0]
        z = np.load(f, allow_pickle=False)
        arrays = {k: z[k] for k in z.files if k != 'meta'}
        meta = dict(json.loads(str(z['meta'])), input_sha='0' * 16)
        z.close()
        C.save_npz(f, meta=np.array(json.dumps(meta)), **arrays)
        before = f.read_bytes()
        p = drive(script, cfg, *args, '--limit', '1')
        r['refuses_invalid_output'] = p.returncode != 0 and 'is not valid' in p.stderr and f.read_bytes() == before
        f.write_bytes(b'broken')
        p = drive(script, cfg, *args, '--limit', '1')
        r['refuses_broken_output'] = p.returncode != 0 and 'is not valid' in p.stderr
        r['ok'] = bool(r['refuses_without_header'] and r['refuses_failed_header'] and
                       r['run_and_resume'] == [0, 0, limit // 2, limit] and r['equal_to_dev_bitwise'] and r['no_part_files'] and
                       r['budget_stop'] and r['refuses_invalid_output'] and r['refuses_broken_output'])
        if not r['ok']:
            r['tail'] = (p1.stdout + p1.stderr + p2.stdout + p2.stderr)[-1500:]
        res[model] = r
        print('runner', model, r['ok'], f'({time.time() - t0:.0f} s)', flush=True)
    return dict(ok=all(v['ok'] for v in res.values()), by_runner=res)


if __name__ == '__main__':
    want = [x for x in sys.argv[1:] if x in ('reading', 'completeness', 'runners')] or ['reading', 'completeness', 'runners']
    ROOT.mkdir(parents=True, exist_ok=True)
    fj = CHECKS_REAL / 'selftest9.json'
    prev = json.loads(fj.read_text()) if fj.exists() else {}
    prev['statistics'] = dict(pvalue_helpers_worst=S.check_pvalues(), strat8_vs_frozen_study2_worst=S.S8.check_against_frozen())
    prev['statistics']['ok'] = all(v < 1e-9 for v in prev['statistics'].values())
    for part in want:
        prev[part] = {'reading': part_reading, 'completeness': part_completeness, 'runners': part_runners}[part]()
    prev['ok'] = all(prev.get(k, {}).get('ok') is True for k in ('statistics', 'reading', 'completeness', 'runners'))
    fj.write_text(json.dumps(prev, indent=1))
    print(json.dumps({k: prev[k]['ok'] for k in ('statistics', 'reading', 'completeness', 'runners') if k in prev}), 'ok:', prev['ok'])
    sys.exit(0 if all(prev[k]['ok'] for k in want) and prev['statistics']['ok'] else 1)
