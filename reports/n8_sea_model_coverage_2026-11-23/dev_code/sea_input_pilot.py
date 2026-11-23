"""Pilot 1 for SEA (no network is run): coverage of target pairs by SEA's subset sampler and drift of its global
statistic when independent columns are appended. Exploratory; development and exploratory inputs only.

Re-implements, in numpy, the inference path of SEA at commit bfb507b (src/data/samplers.py and dataset.py) with the
FCI configuration (config/aggregator_tf_fci.yaml): fci_batches_inference = 500, fci_vars = 5, fci_batch_size = 500,
use_learned_sampler = False, so 250 batches from RandomSampler, then 250 from CorrelationSampler with the visit
counts carried over; global features = pinv(np.cov(X_batch.T), rcond=1e-10) for fewer than 100 variables, computed on
the last batch of the first sampler. SEA's code is read, not imported.

Inputs: EXP2 (Study 2 exploratory, 40 systems; k0, e0 = Gaussian, e_T = structured, k = 20) and the DEV5 stand-in
table of Study 4 (d = 11; k0, Gaussian padding at k = 20 and 40, two draws). The two real tables are not used.
usage: python -I sea_input_pilot.py <artifacts dir> <out json>
"""
import json
import sys
from pathlib import Path

import numpy as np

ART = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ART / 'n2_runs' / 'pn2'))
sys.path.insert(0, str(ART / 'n1_runs' / 'pn1'))
import common2 as C2  # frozen Study 2 input builder (imports the frozen Study 1 generator)

sys.path.insert(0, str(ART / 'n5_runs' / 'pn5'))
import common5 as C5  # frozen Study 4 input builder

T_INF, K_SUB, B_ROWS = 500, 5, 500
SEEDS = (0, 1, 2, 3, 4)


def features(x):  # SEA compute_features, x: (num_vars, num_samples)
    return np.linalg.pinv(np.cov(x), rcond=1e-10)


def sample_nodes(scores, visit, k):
    joint = scores * 1 / np.sqrt(1 + visit)
    sampled = []
    for _ in range(k):
        if not sampled:
            p = joint.sum(0)
        else:
            sa = np.array(sampled, dtype=int)
            p = joint[sa].copy()
            p[:, sa] = 0
            p = p.sum(0)
        p = p / p.sum()
        sampled.append(int(np.random.choice(len(p), (1,), p=p).item()))
    s = np.array(sampled)
    visit[np.ix_(s, s)] += 1
    return s


def run_sampler(X, seed):
    """Node sets of the 500 inference batches and the global features, following SEA's call order."""
    np.random.seed(seed)
    n, D = X.shape
    visit = np.zeros((D, D))
    rand_scores = np.ones((D, D)) * (1 - np.eye(D))
    batches, feats = [], None
    for _ in range(T_INF // 2):                       # RandomSampler
        idxs = np.random.choice(n, (B_ROWS,), replace=False)
        batches.append(sample_nodes(rand_scores, visit, K_SUB))
    feats = features(X[idxs].T)                       # global features: last batch of the first sampler
    for _ in range(T_INF // 2):                       # CorrelationSampler, visit counts carried over
        np.random.choice(n, (B_ROWS,), replace=False)  # batch rows (consumes the stream as in SEA)
        sidx = np.random.choice(n, (B_ROWS,), replace=False)
        sc = np.abs(features(X[sidx].T) * (1 - np.eye(D)))
        batches.append(sample_nodes(sc, visit, K_SUB))
    return batches, feats


def coverage(batches, dT):
    C = np.zeros((dT, dT))
    target_slots, multi = 0, 0
    for s in batches:
        t = s[s < dT]
        target_slots += len(t)
        multi += len(t) >= 2
        C[np.ix_(t, t)] += 1
    iu = np.triu_indices(dT, 1)
    return C[iu], target_slots / (len(batches) * K_SUB), multi / len(batches)


def pcorr(theta, dT):
    d = np.sqrt(np.diag(theta)[:dT])
    P = -theta[:dT, :dT] / np.outer(d, d)
    return P[np.triu_indices(dT, 1)]


def summarize(X, dT, X0=None):
    out = []
    for seed in SEEDS:
        b, feats = run_sampler(X, seed)
        cov, slots, multi = coverage(b, dT)
        out.append(dict(mean_cov=float(cov.mean()), min_cov=float(cov.min()), share_uncovered=float((cov == 0).mean()),
                        cov_first_half=float(coverage(b[:T_INF // 2], dT)[0].mean()),
                        cov_second_half=float(coverage(b[T_INF // 2:], dT)[0].mean()),
                        target_slot_share=slots, share_batches_2plus_targets=multi, pc=pcorr(feats, dT)))
    agg = {k: float(np.mean([o[k] for o in out])) for k in out[0] if k != 'pc'}
    agg['pc'] = out[0]['pc']                       # the global statistic does not depend on the seed when n = 500
    return agg


res = {'exp2': [], 'standin': []}
for sysid, ci, seed in C2.systems2('EXP2'):
    dT, eT, mech = C2.CELLS[ci]
    row = dict(sys=sysid, dT=dT, eT=eT, mech=mech)
    base = None
    for cond in ('k0', 'e0', C2.rep_cond(ci)):
        X, t, pad = C2.assemble2(sysid, ci, seed, cond)
        s = summarize(np.asarray(X, float), dT)
        if cond == 'k0':
            base = s['pc']
        s['pc_drift_mean_abs'] = float(np.mean(np.abs(s['pc'] - base)))
        s['pc_drift_max_abs'] = float(np.max(np.abs(s['pc'] - base)))
        s['pc_k0_mean_abs'] = float(np.mean(np.abs(base)))
        s.pop('pc')
        row['eT' if cond.startswith('e') and cond != 'e0' else cond] = s
    res['exp2'].append(row)
    print(sysid, {c: round(row[c]['mean_cov'], 1) for c in ('k0', 'e0', 'eT')}, flush=True)

for cond, rr in (('k0', [None]), ('k20_e0', [0, 1]), ('k40_e0', [0, 1]), ('k20_e2', [0, 1]), ('k40_e2', [0, 1])):
    for r in rr:
        X, rb, pad = C5.assemble5('DEV5', 'standin', cond, r)
        s = summarize(np.asarray(X, float), 11)
        if cond == 'k0':
            base_s = s['pc']
        s['pc_drift_mean_abs'] = float(np.mean(np.abs(s['pc'] - base_s)))
        s['pc_drift_max_abs'] = float(np.max(np.abs(s['pc'] - base_s)))
        s.pop('pc')
        res['standin'].append(dict(cond=cond, r=r, **s))
Path(sys.argv[2]).write_text(json.dumps(res, indent=1), encoding='utf-8')
print('written', sys.argv[2])
