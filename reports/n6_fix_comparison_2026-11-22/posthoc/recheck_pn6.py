"""Independent re-computation of the P-N6 reading from the raw outputs (rules PN6 v1 §3-§6).

Does not import measures6.py, stats6.py, analyze6.py, screen.py or P-N1 metrics.py. Compares with pn6_reading.json,
which the frozen analyze6.py wrote. Rebuilds the screening partitions from the cached HSIC p-values and the two
recorded alpha levels. Uses the frozen P-N1 generator (common.target) only for the true target graphs, and the frozen
P-N4 copy of the CDFM threshold selector (selector4.thr) only to define the LOCAL control. Runs no model; writes
nothing; prints numbers only. It does not change any locked label.

usage: python -I recheck_pn6.py <artifacts dir>
"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats
from scipy.sparse.csgraph import connected_components

ART = Path(sys.argv[1]).resolve()
OUT6, OUT5 = ART / 'n6_runs' / 'pn6_out', ART / 'n5_runs' / 'pn5_out'
for sub in ('n4_runs/pn4', 'n1_runs/pn1'):
    sys.path.insert(0, str(ART / sub))
from common import CELLS, target          # frozen P-N1: true target graphs only
import selector4 as SEL                   # frozen P-N4: LOCAL control definition only

BASE, REPS, K, MARGIN_NI = 480000, 15, 20, 0.03
AL = json.loads((OUT6 / 'alpha6.json').read_text())
ALPHA = dict(RL=float(AL['alpha_L']), RH=float(AL['alpha_H']))
FAM = {c: CELLS[c][2] for c in range(8)}
DELTA = dict(Q0=0.03, Q_A20=0.03, Q_S20=0.03, G_A20=0.03, G_S20=0.03, dm_A20=1.5, dm_S20=1.5)
for m in ('phi_k0', 'phi_A20', 'phi_S20', 'sigma_A20', 'sigma_S20'):
    DELTA[m] = 1.5
MEAS = list(DELTA)


# ---------------------------------------------------------------- skeleton and measure rules (rules §3-§4)
def thr_or(P, tau):
    A = np.asarray(P, float) > tau
    np.fill_diagonal(A, False)
    return A | A.T


def adj_or(A):
    A = np.array(A) != 0
    np.fill_diagonal(A, False)
    return A | A.T


def up(S):
    return S[np.triu_indices(S.shape[0], 1)]


def flips(a, b):
    return int((up(a) != up(b)).sum())


def edges(S):
    return int(up(S).sum())


def f1(S, g):
    t = up((g + g.T) > 0)
    s = up(S)
    tp, fp, fn = int((t & s).sum()), int((~t & s).sum()), int((t & ~s).sum())
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


def load(model, key):
    z = np.load(OUT6 / model / f'{key}.npz', allow_pickle=False)
    d = {n: z[n] for n in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


def r_skel(model, o):
    return thr_or(o['probs_T'], 0.5) if model == 'avici' else adj_or(o['adj_T'])


def plain_skel(model, o, dT):
    return thr_or(o['probs'][:dT, :dT], 0.5) if model == 'avici' else adj_or(o['adj_native'][:dT, :dT])


# ---------------------------------------------------------------- screening rebuilt from cached p-values (rules §3)
def partition(p, arm):
    D = p.shape[0]
    a = ALPHA[arm] if arm == 'RL' else ALPHA[arm] / (D * (D - 1) / 2)
    R = np.asarray(p, float) < a
    np.fill_diagonal(R, False)
    R = R | R.T
    _, lab = connected_components(R.astype(np.int8), directed=False)
    return R, lab


def canon(lab):
    first = {}
    return [first.setdefault(int(L), i) for i, L in enumerate(lab)]


def screen(p, arm, dT, g):
    R, lab = partition(p, arm)
    D = len(lab)
    tl = set(lab[:dT].tolist())
    merged = sum(1 for v in range(dT, D) if lab[v] in tl)
    out = dict(lab=lab, merged=merged, mixed=merged > 0, false_cross=int(R[:dT, dT:].sum()) if D > dT else 0,
               n_target_components=len(tl))
    if g is not None:
        sk = (g + g.T) > 0
        out['split'] = int(sum(1 for i, j in zip(*np.triu_indices(dT, 1)) if sk[i, j] and lab[i] != lab[j]))
    return out


def pv(key):
    return np.load(OUT6 / 'pvals' / f'{key}.npz', allow_pickle=False)['p']


# ---------------------------------------------------------------- statistics (rules §5-§6)
def strat(cells, bound=0.0):
    w = 1.0 / len(cells)
    mu = [float(np.mean(x)) for x in cells]
    var = [float(np.var(x, ddof=1)) for x in cells]
    n = [len(x) for x in cells]
    est = w * sum(mu)
    terms = [w * w * v / k for v, k in zip(var, n)]
    se = float(np.sqrt(sum(terms)))
    if se == 0:
        return dict(est=est, se=0.0, p=1.0, ci=(est, est), deg=True)
    df = se ** 4 / sum(t * t / (k - 1) for t, k in zip(terms, n))
    q = stats.t.ppf(0.975, df)
    return dict(est=est, se=se, df=df, p=float(stats.t.sf((est - bound) / se, df)), ci=(est - q * se, est + q * se),
                deg=False)


def size_label(ci, d):
    lo, hi = ci
    sign = 'POS' if lo > 0 else ('NEG' if hi < 0 else 'NONE')
    size = 'SMALL' if (lo > -d and hi < d) else ('LARGE' if (lo > d or hi < -d) else 'UNCLEAR')
    return [sign, size]


def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - a / 2, k + 1, n - k))
    return [lo, hi]


# ---------------------------------------------------------------- synthetic systems
FIXES = dict(avici=('plain', 'RL', 'RH'), cdfm=('plain', 'RL', 'RH', 'FIXED', 'FROZEN', 'LOCAL'))
per = defaultdict(lambda: defaultdict(list))          # (model, fam, fix) -> cell -> [measure dicts]
p62 = defaultdict(lambda: defaultdict(list))          # fam -> cell -> [phi_FROZEN(S20) - phi_RL(S20)]
scr = defaultdict(list)                               # (fam, arm, cond) -> [screen dicts]
part_mismatch, sigma_mix = 0, defaultdict(lambda: dict(mixed=[0, 0], not_mixed=[0, 0]))
for ci in range(8):
    dT, eT, fam = CELLS[ci]
    conds = {'k0': 'k0', 'A20': 'e0', 'S20': f'e{eT}'}
    for r in range(REPS):
        sid = f'PN6-c{ci}-r{r}'
        g = target(sid, ci, BASE + 1000 * ci + r)['g']
        sc = {}
        for arm in ('RL', 'RH'):
            for c, n in conds.items():
                s = screen(pv(f'{sid}__{n}'), arm, dT, g)
                sc[(arm, c)] = s
                scr[(fam, arm, c)].append(s)
        for model in ('avici', 'cdfm'):
            S, P = {}, {}
            for c, n in conds.items():
                o = load(model, f'{sid}__{n}__plain')
                P[c] = o
                S[('plain', c)] = plain_skel(model, o, dT)
                for arm in ('RL', 'RH'):
                    ro = load(model, f'{sid}__{n}__{arm}')
                    S[(arm, c)] = r_skel(model, ro)
                    part_mismatch += int(canon(ro['labels']) != canon(sc[(arm, c)]['lab']))
            if model == 'cdfm':
                tau0 = float(P['k0']['threshold'])
                for c in conds:
                    PT = np.asarray(P[c]['probs'][:dT, :dT], float)
                    S[('FIXED', c)] = thr_or(PT, 0.5)
                    S[('FROZEN', c)] = thr_or(PT, tau0)
                    S[('LOCAL', c)] = thr_or(PT, SEL.thr(PT))
            p0 = S[('plain', 'k0')]
            f0 = f1(p0, g)
            for fx in FIXES[model]:
                ms = dict(Q0=f1(S[(fx, 'k0')], g) - f0, phi_k0=flips(S[(fx, 'k0')], p0))
                for c in ('A20', 'S20'):
                    fc = f1(S[(fx, c)], g)
                    ms[f'Q_{c}'] = fc - f0
                    ms[f'G_{c}'] = fc - f1(S[('plain', c)], g)
                    ms[f'phi_{c}'] = flips(S[(fx, c)], p0)
                    ms[f'sigma_{c}'] = flips(S[(fx, c)], S[(fx, 'k0')])
                    ms[f'dm_{c}'] = edges(S[(fx, c)]) - edges(p0)
                    if fx == 'RL':
                        k = 'mixed' if sc[('RL', c)]['mixed'] else 'not_mixed'
                        sigma_mix[(model, fam, c)][k][0] += 1
                        sigma_mix[(model, fam, c)][k][1] += int(ms[f'sigma_{c}'] > 0)
                per[(model, fam, fx)][ci].append(ms)
            if model == 'cdfm':
                p62[fam][ci].append(flips(S[('FROZEN', 'S20')], p0) - flips(S[('RL', 'S20')], p0))

ref = json.loads((OUT6 / 'pn6_reading.json').read_text())
worst = defaultdict(float)


def note(cat, a, b):
    if a is None or b is None:
        return
    worst[cat] = max(worst[cat], abs(float(a) - float(b)))


# ---------------------------------------------------------------- hypotheses
H = {}
for model, tag in (('avici', 'A'), ('cdfm', 'C')):
    for fam in ('lin', 'rff'):
        cells = per[(model, fam, 'RL')]
        q0 = strat([[m['Q0'] for m in cells[c]] for c in sorted(cells)], -MARGIN_NI)
        qa = strat([[m['Q_A20'] for m in cells[c]] for c in sorted(cells)], -MARGIN_NI)
        H[f'P6-1{tag}-{fam}'] = dict(p=max(q0['p'], qa['p']), q0=q0, qa=qa, deg=q0['deg'] or qa['deg'])
for fam in ('lin', 'rff'):
    d = strat([p62[fam][c] for c in sorted(p62[fam])], 0.0)
    H[f'P6-2C-{fam}'] = dict(p=d['p'], d=d, deg=d['deg'])
order = sorted(H, key=lambda h: H[h]['p'])
stop = False
for i, h in enumerate(order):
    thr = 0.05 / (len(order) - i)
    rej = (not stop) and H[h]['p'] <= thr and not H[h]['deg']
    stop = stop or not rej
    H[h].update(rank=i + 1, thr=thr, label='CONFIRMED' if rej else 'NOT_CONFIRMED')
print('== hypotheses (recheck vs frozen reading)')
lab_mismatch = 0
for h in sorted(H):
    x, y = H[h], ref['hypotheses'][h]
    lab_mismatch += int(x['label'] != y['label']) + int(x['rank'] != y['holm_rank'])
    note('hyp_p', x['p'], y['p'])
    if 'q0' in x:
        for a, b in (('q0', 'Q0'), ('qa', 'QA20')):
            note('hyp_est', x[a]['est'], y[b]['estimate'])
            note('hyp_ci', x[a]['ci'][0], y[b]['ci95'][0]); note('hyp_ci', x[a]['ci'][1], y[b]['ci95'][1])
        print(f"{h}: Q0 {x['q0']['est']:+.4f} [{x['q0']['ci'][0]:+.4f}, {x['q0']['ci'][1]:+.4f}] p {x['q0']['p']:.3g} | "
              f"QA20 {x['qa']['est']:+.4f} [{x['qa']['ci'][0]:+.4f}, {x['qa']['ci'][1]:+.4f}] p {x['qa']['p']:.3g} | "
              f"p {x['p']:.3g} rank {x['rank']} {x['label']} (frozen: {y['label']}, p {y['p']:.3g})")
    else:
        note('hyp_est', x['d']['est'], y['estimate'])
        note('hyp_ci', x['d']['ci'][0], y['ci95'][0]); note('hyp_ci', x['d']['ci'][1], y['ci95'][1])
        print(f"{h}: diff {x['d']['est']:+.3f} [{x['d']['ci'][0]:+.3f}, {x['d']['ci'][1]:+.3f}] p {x['p']:.3g} rank "
              f"{x['rank']} {x['label']} (frozen: {y['label']}, p {y['p']:.3g})")

# ---------------------------------------------------------------- descriptive
desc_lab_mismatch, share_mismatch, worst_mismatch = 0, 0, 0
for (model, fam, fx), cells in sorted(per.items()):
    y = ref['descriptive'][f'{model}|{fam}|{fx}']
    for m in MEAS:
        s = strat([[v[m] for v in cells[c]] for c in sorted(cells)], 0.0)
        note('desc_est', s['est'], y[m]['estimate'])
        note('desc_ci', s['ci'][0], y[m]['ci95'][0]); note('desc_ci', s['ci'][1], y[m]['ci95'][1])
        desc_lab_mismatch += int(size_label(s['ci'], DELTA[m]) != list(y[m]['label']))
    for c in ('A20', 'S20'):
        ks = sum(int(v[f'sigma_{c}'] > 0) for cc in cells for v in cells[cc])
        n = sum(len(cells[cc]) for cc in cells)
        yy = y[f'share_sigma_pos_{c}']
        share_mismatch += int(ks != yy['k'] or n != yy['n'])
        note('share_ci', cp(ks, n)[0], yy['ci95'][0]); note('share_ci', cp(ks, n)[1], yy['ci95'][1])
    wa = max(abs(v[f'dm_{c}']) for cc in cells for v in cells[cc] for c in ('A20', 'S20'))
    worst_mismatch += int(wa != y['worst_abs_dm'])

# ---------------------------------------------------------------- screening
scr_mismatch = 0
for (fam, arm, c), ss in sorted(scr.items()):
    for model in ('avici', 'cdfm'):
        y = ref['screening'][f'{model}|{fam}|{arm}|{c}']
        note('screen', np.mean([s['merged'] for s in ss]), y['merged_mean'])
        note('screen', np.mean([s['split'] for s in ss]), y['split_mean'])
        note('screen', np.mean([s['false_cross'] for s in ss]), y['false_cross_mean'])
        scr_mismatch += int(sum(s['mixed'] for s in ss) != y['n_mixed'])
for (model, fam, c), d in sorted(sigma_mix.items()):
    y = ref['screening'][f'{model}|{fam}|RL|{c}|sigma_by_mixing']
    for k in ('mixed', 'not_mixed'):
        scr_mismatch += int(d[k] != [y[k]['n'], y[k]['sigma_pos']])

# ---------------------------------------------------------------- real tables
real_mismatch = 0
for model in ('avici', 'cdfm'):
    for t in ('sachs', 'wine'):
        z = np.load(OUT5 / model / f'{t}__k0.npz', allow_pickle=False)
        ref0 = plain_skel(model, {n: z[n] for n in z.files}, 11)
        for arm in ('RL', 'RH'):
            y = ref['real_tables'][f'{model}|{t}|{arm}']
            o0 = load(model, f'{t}__k0__{arm}')
            s0 = r_skel(model, o0)
            real_mismatch += int(flips(s0, ref0) != y['phi_k0'])
            sc0 = screen(pv(f'{t}__k0'), arm, 11, None)
            real_mismatch += int(sc0['n_target_components'] != y['k0_target_components'])
            for c in ('k20_e0', 'k40_e0'):
                sig, phi, mer = [], [], []
                for r in range(20):
                    o = load(model, f'{t}__{c}__r{r:02d}__{arm}')
                    s = r_skel(model, o)
                    sig.append(flips(s, s0)); phi.append(flips(s, ref0))
                    scx = screen(pv(f'{t}__{c}__r{r:02d}'), arm, 11, None)
                    mer.append(scx['merged'])
                    part_mismatch += int(canon(o['labels']) != canon(scx['lab']))
                yc = y[c]
                note('real', np.mean(sig), yc['sigma']['mean']); note('real', np.mean(phi), yc['phi']['mean'])
                note('real', np.mean(mer), yc['merged']['mean'])
                real_mismatch += int(max(sig) != yc['sigma']['max']) + int(max(phi) != yc['phi']['max'])
                ks = sum(int(v > 0) for v in sig)
                real_mismatch += int(ks != yc['share_sigma_pos']['k'])
                note('share_ci', cp(ks, 20)[0], yc['share_sigma_pos']['ci95'][0])
                note('share_ci', cp(ks, 20)[1], yc['share_sigma_pos']['ci95'][1])

print('\n== agreement with the frozen reading')
print('max |difference| by category:', {k: float(f'{v:.3g}') for k, v in sorted(worst.items())})
print('hypothesis label or Holm-rank mismatches:', lab_mismatch)
print('descriptive size-label mismatches:', desc_lab_mismatch, '| share k/n mismatches:', share_mismatch,
      '| worst |dm| mismatches:', worst_mismatch)
print('screening count mismatches:', scr_mismatch, '| real-table mismatches:', real_mismatch)
print('saved partitions that differ from the partition rebuilt from cached p-values:', part_mismatch)
