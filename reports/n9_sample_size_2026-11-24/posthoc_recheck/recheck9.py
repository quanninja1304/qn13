"""P-N9 / Study 8 post hoc recheck (rules PN9 v1 §9, step 5): a second reading of the saved outputs, written again from the
rules, and compared entry by entry with checks/pn9_reading.json of the frozen analyze9.py.

Written and tested on synthetic data on 27 Nov 2026, before any P-N9 output was read.

Independence. This file imports neither analyze9.py, stats9.py nor common9.py, and none of the frozen readers (Study 1
metrics.py, Study 7 common8.py, stats8.py, stats7.py). The plan (systems, seeds, levels, keys), the NATIVE readings, F1,
flips, Δp, Δ, the stratified t, the p-values, Holm, the labels and the size labels are written again from rules §2-§4 and
the definitions they cite. Shared with the frozen code: the Study 1 cell list, z-score and hash (frozen Study 1
common.py), the data generator (avici.simulate_data with the Study 1 cell configs), numpy and scipy. Limit: the same author
wrote analyze9.py.

Checks:
 1. plan (rules §2.1, §2.3, §2.4): every planned output exists; its metadata match the plan (key, model, sysid, cell,
    system index and seed, n, cond, rows = n, D, d_T, status ok, set, main-run mode; SEA: seed, level, adapter flags);
    its arrays have the expected names and shapes and are finite;
 2. inputs (rules §2.1, §2.2): each system is rebuilt with the generator, the padding formula and the z-scoring of
    Study 1; the input hash in each output's metadata must match the rebuilt input; the true graph is the rebuilt one;
 3. reading (rules §3, §4): per system and level, then the 11 components, Holm, labels and sizes, and the descriptive
    tables, counts and rho;
 4. comparison with pn9_reading.json: every entry (relative tolerance 1e-9, absolute 1e-12; the 11 p-values with the
    relative tolerance only); labels, Holm decisions and counts exactly; Holm ranks and thresholds when the p-values have
    no ties; the eight figure files exist.
Writes checks/pn9_posthoc_recheck.json; exit 0 only if every check passes and every compared entry agrees.
usage (Study 1 model environment): python -I recheck9.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent                                            # reports/n9_sample_size_2026-11-24
ART = REPORT.parents[1] / 'artifacts'
sys.path.insert(1, str(ART / 'n1_runs' / 'pn1'))
from common import CELLS, cfg_path, zscore, sha                 # frozen Study 1: cell list, configs, z-score, hash

# ---------------------------------------------------------------- design, from the rules
N_CELLS, REPS, K, M_REF, NMAX = 8, 15, 20, 4, 20000           # §2.1, §2.4
GRID = {'avici': (100, 200, 500, 1000), 'cdfm': (100, 200, 500, 1000, 2000, 4000), 'foundcause': (125, 200, 500),
        'sea': (500, 1000, 2000, 5000, 20000), 'pc': (100, 125, 200, 500, 1000, 2000, 4000, 5000, 20000),
        'ges': (100, 125, 200, 500, 1000, 2000, 4000)}         # §2.3
NEURAL, CLASSIC = ('avici', 'cdfm', 'foundcause'), ('pc', 'ges')
MODELS = NEURAL + ('sea',) + CLASSIC
LINEAR = tuple(c for c in range(N_CELLS) if CELLS[c][2] == 'lin')
assert LINEAR == (0, 2, 4, 6) and all(CELLS[c][0] in (10, 20) for c in range(N_CELLS))      # §2.1
M_H, M_D = 0.05, 1.0                                            # §4.1
C_SLOPE = {'cdfm': M_H / math.log2(4000 / 100), 'foundcause': M_H / math.log2(500 / 125), 'sea': M_D / math.log2(20000 / 500)}
PAD_TAG = (20261125, 9)                                         # §2.1
ARRAYS = {'avici': ('probs',), 'cdfm': ('probs', 'adj_native', 'threshold'), 'foundcause': ('probs', 'adj_native'),
          'sea': ('prob',), 'pc': ('skel',), 'ges': ('skel',)}
RTOL, ATOL = 1e-9, 1e-12
FIG_NAMES = [f'pn9_fig_{f}.{e}' for f in ('main', 'linear', 'flips', 'sea_delta') for e in ('png', 'pdf')]


def systems():
    """(sysid, cell, r, unit index i, system seed s_i) of the 120 held-out systems (§2.1)."""
    return [(f'PN9-c{c}-r{r}', c, r, REPS * c + r, 730000 + 1000 * c + r) for c in range(N_CELLS) for r in range(REPS)]


def seed_a(i, l):
    return 740000 + 10 * i + l                                  # §2.4


def seed_b(i, l, m):
    return 750000 + 100 * i + 10 * l + m                        # §2.4


def key(sysid, n, cond, seed=None):
    return f'{sysid}__n{n}__{cond}' + ('' if seed is None else f'__s{seed}')


def planned(model, sysid, c, i):
    """[(n, level index, cond, seed, key)] of one model on one system (main outputs only; reruns are not read)."""
    if model in CLASSIC and c not in LINEAR:
        return []
    out = []
    for l, n in enumerate(GRID[model]):
        if model == 'sea':
            a = seed_a(i, l)
            out += [(n, l, 'k0', a, key(sysid, n, 'k0', a)), (n, l, 'A20', a, key(sysid, n, 'A20', a))]
            out += [(n, l, 'k0', seed_b(i, l, m), key(sysid, n, 'k0', seed_b(i, l, m))) for m in range(1, M_REF + 1)]
        else:
            out += [(n, l, 'k0', None, key(sysid, n, 'k0')), (n, l, 'A20', None, key(sysid, n, 'A20'))]
    return out


# ---------------------------------------------------------------- data (§2.1, §2.2)
def study1_generator(c, s):
    """Target block of one system: the Study 1 generator with NMAX rows; a target with no edge is replaced by seed + 500."""
    from avici import simulate_data
    dT, e, mech = CELLS[c]
    seed, rejected = s, []
    while True:
        g, x, _ = simulate_data(d=dT, n=NMAX, seed=seed, path=str(cfg_path(e, mech)))
        if np.asarray(g).sum() > 0:
            break
        rejected.append(seed)
        seed += 500
    return np.asarray(g).astype(np.int8), np.asarray(x, np.float64), seed, rejected


def padding(s):
    return np.random.default_rng(np.random.SeedSequence([s, *PAD_TAG])).standard_normal((NMAX, K))


def input_hashes(x, pad, n):
    """Hashes of k0 and A20 at level n: the first n rows, z-scored on those rows as in Study 1."""
    tx = zscore(x[:n])
    return sha(zscore(tx)), sha(zscore(np.concatenate([tx, zscore(pad[:n])], 1)))


# ---------------------------------------------------------------- readings (§1, §3)
_IU = {}


def iu(d):
    if d not in _IU:
        _IU[d] = np.triu_indices(d, 1)
    return _IU[d]


def skel(model, o, dT, how='native', thr=None):
    """Upper-triangle skeleton vector of the target block."""
    if model in CLASSIC:
        a = np.asarray(o['skel'])[:dT, :dT] != 0
        s = a | a.T
    elif model == 'sea':
        p = np.asarray(o['prob'], float)[:dT, :dT]
        s = (p + p.T) > 0.5 if how == 'alt' else np.maximum(p, p.T) > 0.5
    elif model == 'avici' or how == 'fixed':
        p = np.asarray(o['probs'], float)[:dT, :dT]
        s = np.maximum(p, p.T) > 0.5
    elif how == 'frozen':
        a = np.asarray(o['probs'], float)[:dT, :dT] > thr
        np.fill_diagonal(a, False)
        s = a | a.T
    else:
        a = np.asarray(o['adj_native'])[:dT, :dT] != 0
        s = a | a.T
    return s[iu(dT)]


def f1(s, t):
    tp, fp, fn = int((s & t).sum()), int((s & ~t).sum()), int((~s & t).sum())
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


def flips(s1, s0):
    return int((s1 != s0).sum())


def dp(p1, p0, dT):
    d = np.abs(np.asarray(p1, float)[:dT, :dT] - np.asarray(p0, float)[:dT, :dT])
    return float(d[~np.eye(dT, dtype=bool)].mean())


def values(model, o0, o1, refs, g):
    """Per-system values at one level (§3)."""
    dT = g.shape[0]
    t = ((g + g.T) > 0)[iu(dT)]
    s0, s1 = skel(model, o0, dT), skel(model, o1, dT)
    v = dict(f1_0=f1(s0, t), f1_1=f1(s1, t), flips=flips(s1, s0))
    v['H'] = v['f1_0'] - v['f1_1']
    if model not in CLASSIC:
        pk = 'prob' if model == 'sea' else 'probs'
        v['dp'] = dp(o1[pk], o0[pk], dT)
    if model == 'cdfm':
        v['H_fixed'] = f1(skel(model, o0, dT, 'fixed'), t) - f1(skel(model, o1, dT, 'fixed'), t)
        v['H_frozen'] = v['f1_0'] - f1(skel(model, o1, dT, 'frozen', float(o0['threshold'])), t)
    if model == 'sea':
        sr = [skel(model, r, dT) for r in refs]
        v['delta'] = float(np.mean([flips(s1, x) - flips(s0, x) for x in sr]))
        v['flips_seed'] = float(np.mean([flips(s0, x) for x in sr]))
        v['dp_seed'] = float(np.mean([dp(r['prob'], o0['prob'], dT) for r in refs]))
        a0, a1, ar = skel(model, o0, dT, 'alt'), skel(model, o1, dT, 'alt'), [skel(model, r, dT, 'alt') for r in refs]
        v['delta_alt'] = float(np.mean([flips(a1, x) - flips(a0, x) for x in ar]))
        v['H_alt'] = f1(a0, t) - f1(a1, t)
    return v


# ---------------------------------------------------------------- statistics (§4.2)
def strat(vals, cells):
    """Stratified mean over the cells present, equal weights, SE^2 = sum w^2 s_c^2 / n_c, Welch-Satterthwaite df.
    None for fewer than two values. SE = 0: degenerate, p = 1."""
    if len(vals) <= 1:
        return None
    by = {}
    for x, c in zip(vals, cells):
        if not math.isnan(x):
            by.setdefault(c, []).append(float(x))
    cs = sorted(by)
    w = 1.0 / len(cs)
    ns = [len(by[c]) for c in cs]
    means = [float(np.mean(by[c])) for c in cs]
    a = [w * w * (float(np.var(by[c], ddof=1)) if len(by[c]) > 1 else 0.0) / len(by[c]) for c in cs]
    theta, se2 = w * sum(means), sum(a)
    r = dict(theta=theta, se=math.sqrt(se2), n_by_cell=ns, cell_means=means)
    if se2 <= 0:
        return dict(r, degenerate=True, df=None, ci95=[theta, theta])
    den = sum(x * x / (n - 1) for x, n in zip(a, ns) if n > 1)
    df = se2 * se2 / den if den > 0 else math.inf
    q = float(stats.t.ppf(0.975, df))
    return dict(r, degenerate=False, df=df, ci95=[theta - q * r['se'], theta + q * r['se']])


def usable(r):
    return r is not None and not r['degenerate']


def p_upper(r, c):                       # H0: theta <= c
    return float(stats.t.sf((r['theta'] - c) / r['se'], r['df'])) if usable(r) else 1.0


def p_lower(r, c):                       # H0: theta >= c
    return float(stats.t.cdf((r['theta'] - c) / r['se'], r['df'])) if usable(r) else 1.0


def p_two(r):                            # H0: theta = 0
    return min(1.0, 2 * min(p_upper(r, 0.0), p_lower(r, 0.0))) if usable(r) else 1.0


def p_equiv(r, m):                       # H0: |theta| >= m (TOST, the larger one-sided p)
    return max(p_upper(r, -m), p_lower(r, m)) if usable(r) else 1.0


def ols_slope(levels, ys):
    return float(np.polyfit(np.log2(np.asarray(levels, float)), np.asarray(ys, float), 1)[0])


def holm(p, alpha=0.05):
    """{id: (rank, threshold, rejected)}; step-down, stops at the first non-rejection; ties broken by id."""
    order = sorted(p, key=lambda k: (p[k], k))
    out, go = {}, True
    for j, k in enumerate(order):
        thr = alpha / (len(order) - j)
        go = go and p[k] <= thr
        out[k] = (j + 1, thr, go)
    return out


def size_of(ci, m):
    lo, hi = ci
    sign = 'POS' if lo > 0 else ('NEG' if hi < 0 else 'NONE')
    return [sign, 'SMALL' if lo > -m and hi < m else ('LARGE' if lo > m or hi < -m else 'UNCLEAR')]


# ---------------------------------------------------------------- comparison
class Cmp:
    def __init__(self):
        self.n, self.bad = 0, []

    def num(self, path, a, b):
        self.n += 1
        if a is None or b is None:
            ok = a is None and b is None
        elif isinstance(a, bool) or isinstance(b, bool):
            ok = a is b
        else:
            a, b = float(a), float(b)
            ok = (math.isnan(a) and math.isnan(b)) or a == b or abs(a - b) <= max(ATOL, RTOL * max(abs(a), abs(b)))
        if not ok:
            self.bad.append(f'{path}: recheck {a!r}, analyze9 {b!r}')

    def pval(self, path, a, b):
        """p-values: relative tolerance only, so that a wrong tail or margin is caught even when both p are tiny."""
        self.n += 1
        if a is None or b is None:
            ok = a is None and b is None
        else:
            a, b = float(a), float(b)
            ok = a == b or (a <= 1e-300 and b <= 1e-300) or abs(a - b) <= RTOL * max(abs(a), abs(b))
        if not ok:
            self.bad.append(f'{path}: recheck {a!r}, analyze9 {b!r}')

    def exact(self, path, a, b):
        self.n += 1
        if a != b:
            self.bad.append(f'{path}: recheck {a!r}, analyze9 {b!r}')

    def strat(self, path, mine, theirs):
        if mine is None or theirs is None:
            self.exact(f'{path} (present)', mine is not None, theirs is not None)
            return
        for f in ('theta', 'se', 'df'):
            self.num(f'{path}.{f}', mine[f], theirs.get(f))
        self.exact(f'{path}.degenerate', mine['degenerate'], theirs.get('degenerate'))
        self.exact(f'{path}.n_by_cell', mine['n_by_cell'], theirs.get('n_by_cell'))
        for j, (x, y) in enumerate(zip(mine['cell_means'], theirs.get('cell_means', []))):
            self.num(f'{path}.cell_means[{j}]', x, y)
        for j, (x, y) in enumerate(zip(mine['ci95'], theirs.get('ci95') or [None, None])):
            self.num(f'{path}.ci95[{j}]', x, y)


# ---------------------------------------------------------------- main
def run(out_dir, checks_dir, figs_dir, graph_of=None, generator=study1_generator, check_inputs=True):
    """graph_of(sysid, c, s) -> true graph, used only when check_inputs is False (synthetic tests); otherwise the true graph
    is the one rebuilt by the generator."""
    problems, n_out = [], {m: 0 for m in MODELS}
    PS = {m: {} for m in MODELS}                               # model -> sysid -> dict(c, lin, by_n)
    for sysid, c, r, i, s in systems():
        dT = CELLS[c][0]
        if check_inputs:
            g, x, seed_used, rejected = generator(c, s)
            pad = padding(s)
            want_sha = {}
        else:
            g = np.asarray(graph_of(sysid, c, s)).astype(np.int8)
        if g.shape != (dT, dT):
            problems.append(f'{sysid}: true graph shape {g.shape}')
            continue
        for model in MODELS:
            outs = {}
            for n, l, cond, seed, k in planned(model, sysid, c, i):
                f = out_dir / model / f'{k}.npz'
                if not f.exists():
                    problems.append(f'{model} {k}: missing output')
                    continue
                with np.load(f, allow_pickle=False) as z:
                    o = {a: z[a] for a in z.files}
                meta = json.loads(str(o.pop('meta')))
                n_out[model] += 1
                D = dT + (K if cond == 'A20' else 0)
                want = dict(key=k, model=model, sysid=sysid, ci=c, r=r, i=i, sys_seed=s, n=n, cond=cond, rows=n, D=D, dT=dT,
                            status='ok', set='PN9')
                if model == 'sea':
                    want.update(seed=seed, level=l, layout_ok=True)
                bad = [f'{a}={meta.get(a)!r} (plan {b!r})' for a, b in want.items() if meta.get(a) != b]
                if meta.get('mode') not in ('R1', 'R2', 'R3', 'R4'):
                    bad.append(f"mode={meta.get('mode')!r}")
                if model == 'sea' and meta.get('auc_ok') is False:
                    bad.append('auc_ok=False')
                if not set(ARRAYS[model]) <= set(o):
                    bad.append(f'arrays {sorted(o)}')
                for a in ARRAYS[model]:
                    if a not in o:
                        continue
                    arr = np.asarray(o[a])
                    if a == 'threshold':
                        if arr.shape != () or not np.isfinite(arr):
                            bad.append('threshold not a finite scalar')
                    elif arr.shape != (D, D) or not np.isfinite(arr.astype(float)).all():
                        bad.append(f'{a} shape {arr.shape} or not finite')
                if check_inputs:
                    if (n, cond) not in want_sha:
                        h0, h1 = input_hashes(x, pad, n)
                        want_sha[(n, 'k0')], want_sha[(n, 'A20')] = h0, h1
                    if meta.get('input_sha') != want_sha[(n, cond)]:
                        bad.append('input hash differs from the input rebuilt from the rules')
                    if 'seed_used' in meta and (meta['seed_used'] != seed_used or meta.get('rejected') != rejected):
                        bad.append('seed_used or rejected differs from the generator')
                if bad:
                    problems.append(f'{model} {k}: ' + '; '.join(bad))
                    continue
                outs[(n, cond, seed)] = o
            if model in CLASSIC and c not in LINEAR:
                continue
            rec = dict(c=c, lin=c in LINEAR, by_n={})
            for l, n in enumerate(GRID[model]):
                sd = seed_a(i, l) if model == 'sea' else None
                o0, o1 = outs.get((n, 'k0', sd)), outs.get((n, 'A20', sd))
                refs = [outs.get((n, 'k0', seed_b(i, l, m))) for m in range(1, M_REF + 1)] if model == 'sea' else []
                if o0 is None or o1 is None or any(x_ is None for x_ in refs):
                    continue
                rec['by_n'][n] = values(model, o0, o1, refs, g)
            PS[model][sysid] = rec

    # ------------------------------------------------------------ per-system collections
    def vals(m, n, field, lin_only=False):
        v = [(rec['by_n'][n][field], rec['c']) for rec in PS[m].values() if n in rec['by_n'] and (rec['lin'] or not lin_only)]
        return [a for a, _ in v], [b for _, b in v]

    def contrast(m, n, n0, field):
        v = [(rec['by_n'][n][field] - rec['by_n'][n0][field], rec['c']) for rec in PS[m].values()
             if n in rec['by_n'] and n0 in rec['by_n']]
        return [a for a, _ in v], [b for _, b in v]

    def slopes(m, levels, field):
        v = [(ols_slope(levels, [rec['by_n'][n][field] for n in levels]), rec['c']) for rec in PS[m].values()
             if all(n in rec['by_n'] for n in levels)]
        return [a for a, _ in v], [b for _, b in v]

    # ------------------------------------------------------------ the 11 components (§4.2)
    gC, gF, gS = GRID['cdfm'], GRID['foundcause'], GRID['sea']
    R, P = {}, {}
    R['A1'] = strat(*vals('avici', 200, 'H'))
    P['A1'] = p_upper(R['A1'], 0.0)
    R['A2d'] = strat(*contrast('avici', 500, 200, 'H'))
    P['A2d'] = p_two(R['A2d'])
    R['A2s'] = R['A2d']
    P['A2s'] = p_equiv(R['A2s'], M_H)
    R['C1'] = strat(*vals('cdfm', 4000, 'H'))
    P['C1'] = p_upper(R['C1'], 0.0)
    R['C2s'] = strat(*slopes('cdfm', gC, 'H'))
    P['C2s'] = p_lower(R['C2s'], -C_SLOPE['cdfm'])
    R['F1s'] = strat(*slopes('foundcause', gF, 'H'))
    P['F1s'] = p_lower(R['F1s'], -C_SLOPE['foundcause'])
    R['S1'] = strat(*vals('sea', 20000, 'delta'))
    P['S1'] = p_upper(R['S1'], 0.0)
    R['S2s'] = strat(*slopes('sea', gS, 'delta'))
    P['S2s'] = p_lower(R['S2s'], -C_SLOPE['sea'])
    RL = {}
    for cid, m, levels, field, mg in (('C2t', 'cdfm', (100, 200, 1000, 2000, 4000), 'H', M_H),
                                      ('F1t', 'foundcause', (125, 200), 'H', M_H),
                                      ('S2t', 'sea', (1000, 2000, 5000, 20000), 'delta', M_D)):
        RL[cid] = {n: strat(*contrast(m, n, 500, field)) for n in levels}
        P[cid] = max(p_equiv(x, mg) for x in RL[cid].values()) if all(x is not None for x in RL[cid].values()) else None
    order = ('A1', 'A2d', 'A2s', 'C1', 'C2s', 'C2t', 'F1s', 'F1t', 'S1', 'S2s', 'S2t')
    computable = all(P[cid] is not None and (cid in RL or R[cid] is not None) for cid in order)
    H = holm({cid: P[cid] for cid in order}) if computable else None
    labels, size = {}, {}
    if H:
        rej = {cid: H[cid][2] for cid in order}
        for cid, mg in (('A1', M_H), ('C1', M_H), ('S1', M_D)):
            labels[cid] = ('PERSISTS' if R[cid]['theta'] >= mg else 'PRESENT_BELOW_MARGIN') if rej[cid] else 'NOT_CONFIRMED'
        a2 = set()
        if rej['A2d']:
            a2.add('HIGHER' if R['A2d']['theta'] > 0 else 'LOWER')
        if rej['A2s']:
            a2.add('SIMILAR')
        labels['A2'] = a2 or {'UNCLEAR'}
        for t, (s_id, t_id) in (('C2', ('C2s', 'C2t')), ('F1', ('F1s', 'F1t')), ('S2', ('S2s', 'S2t'))):
            labels[t] = {x for x, ok in (('SHRINKS', rej[s_id]), ('STABLE', rej[t_id])) if ok} or {'UNCLEAR'}
        size = {cid: size_of(R[cid]['ci95'], mg) for cid, mg in (('A1', M_H), ('C1', M_H), ('S1', M_D), ('A2d', M_H))}
    else:
        problems.append('not every component is computable')

    # ------------------------------------------------------------ descriptive (§3)
    fields = {m: ['H', 'flips', 'f1_0', 'f1_1'] + (['dp'] if m not in CLASSIC else []) +
              (['H_fixed', 'H_frozen'] if m == 'cdfm' else []) +
              (['delta', 'delta_alt', 'H_alt', 'flips_seed', 'dp_seed'] if m == 'sea' else []) for m in MODELS}
    desc = {m: {n: {f: strat(*vals(m, n, f)) for f in fields[m]} for n in GRID[m]} for m in MODELS}
    desc_lin = {m: {n: strat(*vals(m, n, 'H', lin_only=True)) for n in GRID[m]} for m in NEURAL + ('sea',)}
    beyond = {}
    for m in NEURAL + ('sea',):
        beyond[m] = {}
        for n in GRID[m]:
            v, cc = [], []
            for sysid, rec in PS[m].items():
                q1, q2 = PS['pc'].get(sysid), PS['ges'].get(sysid)
                if rec['lin'] and n in rec['by_n'] and q1 and q2 and n in q1['by_n'] and n in q2['by_n']:
                    v.append(rec['by_n'][n]['H'] - max(q1['by_n'][n]['H'], q2['by_n'][n]['H']))
                    cc.append(rec['c'])
            beyond[m][n] = strat(v, cc)
    counts = {m: {n: sum(n in rec['by_n'] for rec in PS[m].values()) for n in GRID[m]} for m in MODELS}
    rho = {}
    for m in MODELS:
        field = 'delta' if m == 'sea' else 'H'
        rows = [[rec['by_n'][n][field] for n in GRID[m]] for rec in PS[m].values() if all(n in rec['by_n'] for n in GRID[m])]
        if len(rows) > 2:
            with np.errstate(divide='ignore', invalid='ignore'):
                rho[m] = np.corrcoef(np.asarray(rows, float).T).tolist()
        else:
            rho[m] = None

    # ------------------------------------------------------------ comparison with the frozen reading
    cm = Cmp()
    jf = checks_dir / 'pn9_reading.json'
    if not jf.exists():
        problems.append('pn9_reading.json missing')
        J = None
    else:
        J = json.loads(jf.read_text())
    if J is not None:
        cm.exact('set', J.get('set'), 'PN9')
        mg = J.get('margins', {})
        for f, v in (('H', M_H), ('delta', M_D), ('c_C', C_SLOPE['cdfm']), ('c_F', C_SLOPE['foundcause']), ('c_S', C_SLOPE['sea'])):
            cm.num(f'margins.{f}', v, mg.get(f))
        for m in MODELS:
            for n in GRID[m]:
                cm.exact(f'counts.{m}.{n}', counts[m][n], (J.get('counts', {}).get(m) or {}).get(str(n)))
        JC = J.get('components', {})
        cm.exact('components (ids)', sorted(JC), sorted(order))
        ties = len(set(P[c] for c in order if P[c] is not None)) < len(order)
        for cid in order:
            jc = JC.get(cid, {})
            cm.pval(f'{cid}.p', P[cid], jc.get('p'))
            if cid in RL:
                jl = jc.get('res_by_level') or {}
                cm.exact(f'{cid}.levels', sorted(str(n) for n in RL[cid]), sorted(jl))
                for n, x in RL[cid].items():
                    cm.strat(f'{cid}.res_by_level.{n}', x, jl.get(str(n)))
            else:
                cm.strat(f'{cid}.res', R[cid], jc.get('res'))
            if H:
                jh = jc.get('holm') or {}
                cm.exact(f'{cid}.holm.rejected', H[cid][2], jh.get('rejected'))
                if not ties:
                    cm.exact(f'{cid}.holm.rank', H[cid][0], jh.get('rank'))
                    cm.num(f'{cid}.holm.threshold', H[cid][1], jh.get('threshold'))
        JL = J.get('labels', {})
        for t, v in labels.items():
            got = JL.get(t)
            got = set(got.split(' + ')) if isinstance(got, str) and t in ('A2', 'C2', 'F1', 'S2') else got
            cm.exact(f'labels.{t}', v, got)
        cm.exact('labels (ids)', sorted(JL), sorted(labels))
        for cid, v in size.items():
            cm.exact(f'size.{cid}', v, (J.get('size') or {}).get(cid))
        JD = J.get('descriptive', {})
        for m in MODELS:
            for n in GRID[m]:
                jd = (JD.get(m) or {}).get(str(n)) or {}
                cm.exact(f'descriptive.{m}.{n} (fields)', sorted(fields[m]), sorted(jd))
                for f in fields[m]:
                    cm.strat(f'descriptive.{m}.{n}.{f}', desc[m][n][f], jd.get(f))
        for name, table in (('descriptive_linear', desc_lin), ('beyond_classical_linear', beyond)):
            JT = J.get(name, {})
            for m in table:
                for n in GRID[m]:
                    cm.strat(f'{name}.{m}.{n}', table[m][n], (JT.get(m) or {}).get(str(n)))
        for m in MODELS:
            a, b = rho[m], (J.get('rho') or {}).get(m)
            if a is None or b is None:
                cm.exact(f'rho.{m} (present)', a is not None, b is not None)
                continue
            cm.exact(f'rho.{m} (shape)', np.shape(a), np.shape(b))
            if np.shape(a) == np.shape(b):
                for x in range(len(a)):
                    for y in range(len(a)):
                        cm.num(f'rho.{m}[{x}][{y}]', a[x][y], b[x][y])
        miss = [f for f in FIG_NAMES if not (figs_dir / f).exists()]
        if miss:
            problems.append(f'figure files missing: {miss}')

    res = dict(ok=not problems and not cm.bad and J is not None, written='27 Nov 2026, before any P-N9 output was read',
               checks=dict(outputs_read=n_out, inputs_checked=check_inputs, n_problems=len(problems), problems=problems[:200]),
               comparison=dict(n_compared=cm.n, n_mismatches=len(cm.bad), mismatches=cm.bad[:200]),
               recheck=dict(p={c: P[c] for c in order},
                            holm=None if H is None else {c: dict(rank=H[c][0], threshold=H[c][1], rejected=H[c][2]) for c in order},
                            labels={t: (sorted(v) if isinstance(v, set) else v) for t, v in labels.items()}, size=size,
                            estimates={c: (None if R.get(c) is None else dict(theta=R[c]['theta'], se=R[c]['se'], df=R[c]['df'],
                                                                         ci95=R[c]['ci95'])) for c in order if c not in RL}),
               analyze9_labels=None if J is None else J.get('labels'))
    checks_dir.mkdir(parents=True, exist_ok=True)
    (checks_dir / 'pn9_posthoc_recheck.json').write_bytes((json.dumps(res, indent=1, default=float) + '\n').encode('utf-8'))
    return res


if __name__ == '__main__':
    r = run(ART / 'n9_runs' / 'pn9_out', REPORT / 'checks', ART / 'n9_runs' / 'figures')
    print(json.dumps(dict(ok=r['ok'], outputs_read=r['checks']['outputs_read'], n_problems=r['checks']['n_problems'],
                          n_compared=r['comparison']['n_compared'], n_mismatches=r['comparison']['n_mismatches'],
                          first_problems=r['checks']['problems'][:5], first_mismatches=r['comparison']['mismatches'][:5]), indent=1))
    sys.exit(0 if r['ok'] else 1)
