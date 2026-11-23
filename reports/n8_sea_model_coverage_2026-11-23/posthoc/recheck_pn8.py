"""Independent recheck of the Study 7 reading (rules PN8 v1 §3–§4), written before any main output was read.

Recomputes the six hypothesis contrasts, their tests, Holm 0.05 and size labels from the raw outputs, with its own code:
no import of the Study 7 analysis modules (common8, stats8, analyze8) or of the frozen statistics. The only frozen code
used is the P-N1 target generator (`common.target`), to regenerate the true target graphs; system seeds and SEA seeds
are recomputed from the formulas of rules §2. Compares every value with pn8_reading.json.
usage (Study 1 model environment): python -I recheck_pn8.py <artifacts dir> [--dev]
  --dev: run on DEV8 / DEV5 outputs (r = 0 systems, stand-in as one table) and print no values
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy import stats

ART = Path(sys.argv[1]).resolve()
DEV = '--dev' in sys.argv
OUT = ART / 'n8_runs' / 'pn8_out'
sys.path.insert(1, str(ART / 'n1_runs' / 'pn1'))
from common import target, CELLS            # frozen P-N1 generator only

SET, BASE, REPS, OFF = ('DEV8', 510000, 1, 1_000_000) if DEV else ('PN8', 500000, 15, 0)
TAB = (('DEV5', 'standin', 0, 2),) if DEV else (('PN5', 'sachs', 0, 20), ('PN5', 'wine', 1, 20))
MARG = {'P8-1': 1.0, 'P8-1S': 1.0, 'P8-2': 0.05, 'P8-3': 0.05, 'P8-4S': 1.0, 'P8-4W': 1.0}


def prob(key):
    return np.load(OUT / 'sea' / f'{key}.npz', allow_pickle=False)['prob']


def sk(p, d, alt):
    a = p[:d, :d]
    m = (a + a.T > 0.5) if alt else (np.maximum(a, a.T) > 0.5)
    return m[np.triu_indices(d, 1)]


def f1(s, g):
    t = (g + g.T > 0)[np.triu_indices(g.shape[0], 1)]
    tp, fp, fn = (t & s).sum(), (~t & s).sum(), (t & ~s).sum()
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


def csk(path, d):
    s = np.load(path, allow_pickle=False)['skel'][:d, :d] != 0
    return (s | s.T)[np.triu_indices(d, 1)]


def strat(v, c):
    v, c = np.asarray(v, float), np.asarray(c)
    cs = np.unique(c); w = 1 / len(cs)
    th = sum(w * v[c == k].mean() for k in cs)
    parts = [w * w * (v[c == k].var(ddof=1) if (c == k).sum() > 1 else 0.0) / (c == k).sum() for k in cs]
    se2 = sum(parts)
    if se2 == 0:
        return th, 0.0, None, 1.0, (th, th)
    df = se2 ** 2 / sum(p ** 2 / ((c == k).sum() - 1) for p, k in zip(parts, cs) if (c == k).sum() > 1)
    se = np.sqrt(se2); q = stats.t.ppf(0.975, df)
    return th, se, df, stats.t.sf(th / se, df), (th - q * se, th + q * se)


def paired(v):
    v = np.asarray(v, float); n = len(v); se = v.std(ddof=1) / np.sqrt(n)
    if se == 0:
        return v.mean(), 0.0, n - 1, 1.0, (v.mean(), v.mean())
    q = stats.t.ppf(0.975, n - 1)
    return v.mean(), se, n - 1, stats.t.sf(v.mean() / se, n - 1), (v.mean() - q * se, v.mean() + q * se)


def size(ci, m):
    lo, hi = ci
    return 'SMALL' if (lo > -m and hi < m) else ('LARGE' if (lo > m or hi < -m) else 'UNCLEAR')


res = {}
for alt in (False, True):
    dA, dS, H, BC, cells, lcells = [], [], [], [], [], []
    for ci in range(8):
        dT, e, mech = CELLS[ci]
        for r in range(REPS):
            sysid, i = f'{SET}-c{ci}-r{r}', 15 * ci + r
            g = np.asarray(target(sysid, ci, BASE + 1000 * ci + r)['g'])
            a = 600000 + i + OFF
            K, A, S = (sk(prob(f'{sysid}__{c}__s{a}'), dT, alt) for c in ('k0', 'A20', 'S20'))
            R = [sk(prob(f'{sysid}__k0__s{610000 + 10 * i + m + OFF}'), dT, alt) for m in (1, 2, 3, 4)]
            dA.append(np.mean([(x != A).sum() - (x != K).sum() for x in R]))
            dS.append(np.mean([(x != S).sum() - (x != K).sum() for x in R]))
            H.append(f1(K, g) - f1(A, g)); cells.append(ci)
            if mech == 'lin':
                hc = []
                for alg in ('pc', 'ges'):
                    base = OUT / 'classical' / alg
                    hc.append(f1(csk(base / f'{sysid}__k0.npz', dT), g) - f1(csk(base / f'{sysid}__A20.npz', dT), g))
                BC.append(H[-1] - max(hc)); lcells.append(ci)
    out = {'P8-1': strat(dA, cells), 'P8-1S': strat(dS, cells), 'P8-2': strat(H, cells), 'P8-3': strat(BC, lcells)}
    for (s5, table, j, nd), hyp in zip(TAB, ('P8-4S', 'P8-4W')):
        dl = []
        for r in range(nd):
            a = 620000 + 100 * j + r + OFF
            K = sk(prob(f'{s5}-{table}__k0__r{r:02d}__s{a}'), 11, alt)
            X = sk(prob(f'{s5}-{table}__k20_e0__r{r:02d}__s{a}'), 11, alt)
            R = [sk(prob(f'{s5}-{table}__k0__r{r:02d}__s{630000 + 1000 * j + 10 * r + m + OFF}'), 11, alt) for m in (1, 2, 3, 4)]
            dl.append(np.mean([(x != X).sum() - (x != K).sum() for x in R]))
        out[hyp] = paired(dl)
    res['alt' if alt else 'nat'] = out

nat = res['nat']
order = sorted(nat, key=lambda h: nat[h][3])
holm, stop = {}, False
for k, h in enumerate(order):
    thr = 0.05 / (len(order) - k); rej = (not stop) and nat[h][3] <= thr; stop = stop or not rej
    holm[h] = (k + 1, thr, 'CONFIRMED' if rej else 'NOT_CONFIRMED')
if DEV:
    print(json.dumps(dict(dev_structure_ok=True, hypotheses=sorted(nat), holm_ranks=sorted(v[0] for v in holm.values())), indent=1))
    sys.exit(0)
ref = json.loads((OUT / 'pn8_reading.json').read_text())
worst, mism = 0.0, []
for tag, key in (('nat', 'hypotheses'), ('alt', 'sensitivity_alt_readout')):
    for h, (th, se, df, p, ci) in res[tag].items():
        R_ = ref[key][h]
        for a_, b_ in ((th, R_['theta']), (se, R_['se']), (p, R_['p']), (ci[0], R_['ci95'][0]), (ci[1], R_['ci95'][1])):
            worst = max(worst, abs(a_ - b_))
        if size(ci, MARG[h]) != R_['size']:
            mism.append(f'{tag} {h} size')
        if tag == 'nat' and (holm[h][0] != R_['holm_rank'] or holm[h][2] != R_['label']):
            mism.append(f'{h} Holm')
for h in nat:
    th, se, df, p, ci = nat[h]
    print(f'{h:<6} {th:+.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}] p {p:.3e} {holm[h][2]} {size(ci, MARG[h])}')
print(f'max |difference| vs pn8_reading.json: {worst:.3e}; label/size mismatches: {mism or "none"}')
sys.exit(0 if worst < 1e-9 and not mism else 1)
