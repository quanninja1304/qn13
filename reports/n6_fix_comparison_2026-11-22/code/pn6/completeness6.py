"""P-N6 completeness check before reading (rules PN6 v1 §7).

usage: completeness6.py [--set PN6|DEV6]
Checks: one terminal record per job, all ok (no error, no budget_stop); every output exists; input hashes match the
regenerated inputs; real-table inputs match the P-N5 input hashes; cached p-values belong to their inputs;
R-L target-pair decisions at every padded input equal those at k0 (exactly); the conditional R-L statement (if the
target-pair decisions are unchanged and no component mixes target and padding variables, the target-component inputs
and the R-L outputs equal R-L at k0 bit for bit); PN6 also the freeze-gate headers at the start and end of the run.
Writes pn6_out/<set>_completeness.json.
"""
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
from common6 import (OUT6, OUT5, INPUTS5, MODELS, R_ARMS, items6, syn_items, base_key, key6, k0_of, assemble6, load_pvals,
                     reject, alphas, sha, SCR)

ap = argparse.ArgumentParser()
ap.add_argument('--set', default='PN6', choices=['PN6', 'DEV6'])
a = ap.parse_args()
bad = []
items = items6(a.set)
sha_in, dT_of = {}, {}
for it in items:
    X, dT, _ = assemble6(it)
    sha_in[base_key(it)], dT_of[base_key(it)] = sha(X), dT

# ---- jobs and terminal records
expected = {('pvals', None): [base_key(it) for it in items]}
for m in MODELS:
    expected[(m, 'plain')] = [key6(it, 'plain') for it in syn_items(a.set)]
    for arm in R_ARMS:
        expected[(m, arm)] = [key6(it, arm) for it in items]
n_jobs = 0
for (task, arm), keys in expected.items():
    logp = OUT6 / task / (f'log_{a.set}.jsonl' if task == 'pvals' else f'log_{a.set}_{arm}.jsonl')
    recs = [json.loads(l) for l in logp.read_text(encoding='utf-8').splitlines() if l.strip()] if logp.exists() else []
    by = {}
    for r in recs:
        by.setdefault(r['key'], []).append(r)
    for k in keys:
        n_jobs += 1
        rs = by.get(k, [])
        if len(rs) != 1:
            bad.append(f'{task} {arm} {k}: {len(rs)} records')
            continue
        r = rs[0]
        if r['status'] != 'ok':
            bad.append(f'{task} {arm} {k}: status {r["status"]}')
        bk = k if task == 'pvals' else k.rsplit('__', 1)[0]
        if r.get('input_sha') != sha_in[bk]:
            bad.append(f'{task} {arm} {k}: input sha differs from the regenerated input')
        f = (OUT6 / 'pvals' / f'{bk}.npz') if task == 'pvals' else (OUT6 / task / f'{k}.npz')
        if not f.exists():
            bad.append(f'missing output {f.name}')
    extra = set(by) - set(keys)
    if extra:
        bad.append(f'{task} {arm}: {len(extra)} records outside the job list')
    for r in recs:
        if r['status'] in ('budget_stop',) or str(r['status']).startswith('error'):
            bad.append(f'{task} {arm} {r["key"]}: {r["status"]}')

# ---- real-table inputs against P-N5, and the P-N5 plain k0 outputs used for phi
if a.set == 'PN6':
    ref5 = json.loads(INPUTS5.read_text())
    for it in items:
        if it['kind'] == 'real' and ref5.get(base_key(it)) != sha_in[base_key(it)]:
            bad.append(f'real input {base_key(it)} differs from P-N5 inputs5.json')
    for m in MODELS:
        for t in ('sachs', 'wine'):
            z = np.load(OUT5 / m / f'{t}__k0.npz', allow_pickle=False)
            if json.loads(str(z['meta'])).get('input_sha') != ref5[f'{t}__k0']:
                bad.append(f'P-N5 plain k0 output {m} {t} has another input')

# ---- cached p-values, R-L decisions and the conditional R-L statement
al = alphas()
stats_rl = dict(padded_inputs=0, decisions_same=0, conditional_inputs=0, conditional_bitwise=0)
for it in items:
    if it['cond'] == 'k0':
        continue
    p, pm = load_pvals(it)
    p0, pm0 = load_pvals(k0_of(it))
    if pm['input_sha'] != sha_in[base_key(it)] or pm0['input_sha'] != sha_in[base_key(k0_of(it))]:
        bad.append(f'cached p-values do not match {base_key(it)}')
        continue
    dT = dT_of[base_key(it)]
    same = bool(np.array_equal(reject(p, 'RL', al['RL'])[:dT, :dT], reject(p0, 'RL', al['RL'])[:dT, :dT]))
    stats_rl['padded_inputs'] += 1
    stats_rl['decisions_same'] += int(same)
    if not same:
        bad.append(f'R-L target-pair decisions differ from k0 at {base_key(it)} (rules §7: report; never relax)')
    for m in MODELS:
        o = np.load(OUT6 / m / f'{key6(it, "RL")}.npz', allow_pickle=False)
        o0 = np.load(OUT6 / m / f'{key6(k0_of(it), "RL")}.npz', allow_pickle=False)
        if not (np.array_equal(o['target_decisions'], reject(p, 'RL', al['RL'])[:dT, :dT].astype(np.uint8))):
            bad.append(f'{m} {base_key(it)}: saved R-L decisions differ from the cached p-values')
        mixed = json.loads(str(o['meta']))['mixed']
        if same and not mixed:
            stats_rl['conditional_inputs'] += 1
            ok = sorted(o['comp_sha'].tolist()) == sorted(o0['comp_sha'].tolist()) and np.array_equal(o['probs_T'], o0['probs_T'])
            if m == 'cdfm':
                thr = dict(zip(o['comp_sha'].tolist(), o['thr_components'].tolist()))
                thr0 = dict(zip(o0['comp_sha'].tolist(), o0['thr_components'].tolist()))
                ok = ok and np.array_equal(o['adj_T'], o0['adj_T']) and thr == thr0
            stats_rl['conditional_bitwise'] += int(ok)
            if not ok:
                bad.append(f'{m} {base_key(it)}: conditional R-L statement fails (implementation error; rules §7)')

# ---- freeze-gate headers
hdr_info = None
if a.set == 'PN6':
    hp = OUT6 / 'pn6_run_header.json'
    H = json.loads(hp.read_text()) if hp.exists() else []
    starts = [h for h in H if h['label'] == 'pn6_start']
    ends = [h for h in H if h['label'] == 'pn6_end']
    if not starts or not ends:
        bad.append('freeze-gate header missing at the start or the end')
    else:
        s, e = starts[0], ends[-1]
        for h, nm in ((s, 'pn6_start'), (e, 'pn6_end')):
            if not h['ok']:
                bad.append(f'{nm} freeze gate not ok: {h["problems"]}')
        for q in ('freeze_commit', 'sha256sums_sha', 'deps_sha'):
            if s.get(q) != e.get(q):
                bad.append(f'{q} differs between pn6_start and pn6_end')
        hdr_info = {nm: dict(ok=h['ok'], freeze_commit=h['freeze_commit'], time_local=h['time_local']) for h, nm in ((s, 'pn6_start'), (e, 'pn6_end'))}

res = dict(set=a.set, n_jobs=n_jobs, rl=stats_rl, freeze_gate=hdr_info, ok=not bad, problems=bad[:200], n_problems=len(bad))
(OUT6 / f'{a.set.lower()}_completeness.json').write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != 'problems'}, indent=1))
if bad:
    print('\n'.join(bad[:30]))
sys.exit(0 if not bad else 1)
