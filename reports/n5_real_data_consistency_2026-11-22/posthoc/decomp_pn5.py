"""EXPLORATORY: decomposition of the CDFM NATIVE real-block skeleton change, structured (e = 2) minus Gaussian (e = 0)
padding, on the saved P-N5 outputs. Not in the locked P-N5 rules; computed after the P-N5 results were seen, at the
user's request (22/11/2026). No model is run.

m(A, tau): the P-N4 rule (rules PN4 §2, selector4.count_target): unordered real-block pairs (55) with
max(A_ij, A_ji) > tau (strict), diagonal excluded. The script first checks that this rule reproduces the saved NATIVE
adjacency of every P-N5 CDFM output, so T + S equals the change of the NATIVE skeleton count.

Per padding draw r (both padding types share the draw's randomness), with g = Gaussian, s = structured:
  anchor e = 0 (as P-N4):  S  = m(P_s, tau_g) - m(P_g, tau_g)   T  = m(P_s, tau_s) - m(P_s, tau_g)
  reversed anchor (e = 2): S' = m(P_s, tau_s) - m(P_g, tau_s)   T' = m(P_g, tau_s) - m(P_g, tau_g)
T + S = T' + S' = m(P_s, tau_s) - m(P_g, tau_g). Means over the 20 draws with t CI 95% (df 19), conditional on the
fixed table. This is anchor-dependent accounting, not two separately identified causes.
usage: python -I decomp_pn5.py <pn5_out dir> <output json>
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats

OUT, DEST = Path(sys.argv[1]), Path(sys.argv[2])
DT, R = 11, 20
IU = np.triu_indices(DT, 1)


def m(A, tau):
    a = (A > tau).astype(np.int8)
    np.fill_diagonal(a, 0)
    return int(((a + a.T) > 0)[IU].sum())


def load(key):
    z = np.load(OUT / 'cdfm' / f'{key}.npz', allow_pickle=False)
    return z['probs'].astype(float), float(z['threshold']), z['adj_native'].astype(np.int8)


def summ(v):
    v = np.asarray(v, float)
    mean, se = float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v)))
    q = float(stats.t.ppf(0.975, len(v) - 1))
    return dict(mean=mean, ci95=[mean - q * se, mean + q * se], n_pos=int((v > 0).sum()), n_zero=int((v == 0).sum()),
                n_neg=int((v < 0).sum()))


# (1) the rule m(A, tau) against the saved NATIVE adjacency, on every P-N5 CDFM output
keys = sorted(p.stem for p in (OUT / 'cdfm').glob('*.npz') if not p.stem.startswith('standin'))
bad_full, bad_block = [], []
for key in keys:
    P, tau, A = load(key)
    off = ~np.eye(P.shape[0], dtype=bool)
    if not np.array_equal((P > tau)[off], (A != 0)[off]):
        bad_full.append(key)
    a = (P[:DT, :DT] > tau).astype(np.int8)
    np.fill_diagonal(a, 0)
    if not np.array_equal(((a + a.T) > 0)[IU], ((A[:DT, :DT] + A[:DT, :DT].T) > 0)[IU]):
        bad_block.append(key)
check = dict(n_outputs=len(keys), full_matrix_mismatch=bad_full, real_block_skeleton_mismatch=bad_block)

# (2) decomposition per table and k
res = {}
for t in ('sachs', 'wine'):
    for k in (20, 40):
        rows = []
        for r in range(R):
            Pg, tg, Ag = load(f'{t}__k{k}_e0__r{r:02d}')
            Ps, ts, As = load(f'{t}__k{k}_e2__r{r:02d}')
            Pg, Ps = Pg[:DT, :DT], Ps[:DT, :DT]
            mgg, msg, mss, mgs = m(Pg, tg), m(Ps, tg), m(Ps, ts), m(Pg, ts)
            nat = int(((As[:DT, :DT] + As[:DT, :DT].T) > 0)[IU].sum()) - int(((Ag[:DT, :DT] + Ag[:DT, :DT].T) > 0)[IU].sum())
            S, T, S2, T2 = msg - mgg, mss - msg, mss - mgs, mgs - mgg
            rows.append(dict(r=r, m_gauss=mgg, m_struct=mss, S=S, T=T, TpS=T + S, TmS=T - S, S_alt=S2, T_alt=T2,
                             native_dm=nat, dthr=ts - tg))
        assert all(x['TpS'] == x['native_dm'] for x in rows)
        out = {c: summ([x[c] for x in rows]) for c in ('T', 'S', 'TpS', 'TmS', 'T_alt', 'S_alt', 'dthr')}
        out['frac_T_below_minus_absS'] = float(np.mean([x['T'] < -abs(x['S']) for x in rows]))
        out['c5_pattern'] = dict(T_ci_below_minus_1_5=out['T']['ci95'][1] < -1.5, TpS_ci_below_0=out['TpS']['ci95'][1] < 0,
                                 TmS_ci_below_0=out['TmS']['ci95'][1] < 0)
        out['rows'] = rows
        res[f'{t}_k{k}'] = out

DEST.write_text(json.dumps(dict(label='EXPLORATORY (after P-N5 results were seen; not in the locked rules)',
                                rule='m(A, tau) of PN4 §2 on the 55 real-block pairs', check=check, results=res), indent=1))
print('check:', {k: (v if not isinstance(v, list) else len(v)) for k, v in check.items()})
f = lambda s: f"{s['mean']:+.2f} [{s['ci95'][0]:+.2f}, {s['ci95'][1]:+.2f}]"
for key, o in res.items():
    print(f"{key}: T {f(o['T'])}  S {f(o['S'])}  T+S {f(o['TpS'])}  T-S {f(o['TmS'])}  | reversed anchor T' {f(o['T_alt'])}"
          f"  S' {f(o['S_alt'])}  | share T<-|S| {o['frac_T_below_minus_absS']:.2f}  | C5 pattern {o['c5_pattern']}")
