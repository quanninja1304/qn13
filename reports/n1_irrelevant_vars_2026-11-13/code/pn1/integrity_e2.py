"""P-N1 E2 integrity check (step 1). Reads raw outputs and logs only; computes no metric.

Checks per algorithm (avici, cdfm, foundcause, pc, ges):
  I1 every expected E2 job has exactly one loadable .npz; no unexpected E2 .npz
  I2 required arrays present, shapes match d = dT + k, values finite, probs in [0, 1]
  I3 input_sha stored in each .npz equals the sha of a fresh `assemble` of that job (regenerates every input)
  I4 input_sha identical across all algorithms that ran the job
  I5 target_sha (models) constant within a system and equal to the E1 k = 0 target_sha
  I6 log_E2.jsonl: errors, duplicates, runtimes (outliers listed, not judged)
Also explains the per-algorithm file counts (DEV + E1 + E2).
usage: integrity_e2.py  -> pn1_out/integrity_e2.json
"""
import os, sys, json
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from common import OUT, assemble, sha, systems
from jobs import jobs_for

ALGS = ['avici', 'cdfm', 'foundcause', 'pc', 'ges']
REQ = {'avici': ['probs'], 'cdfm': ['probs', 'logits', 'adj_native'],
       'foundcause': ['probs', 'adj_native', 'agreement'], 'pc': ['skel'], 'ges': ['skel']}


def expected(alg, phase):
    jl = jobs_for('pc' if alg in ('pc', 'ges') else alg, phase)
    if alg in ('pc', 'ges'):
        jl = [j for j in jl if j['key'].endswith('__main') or j['key'].endswith('__rep')]
    return jl


rep = {}
fresh_sha = {}
all_e2 = {}
for alg in ALGS:
    all_e2[alg] = {j['key']: j for j in expected(alg, 'E2')}
union = {}
for alg in ALGS:
    union.update(all_e2[alg])
print(f'regenerating {len(union)} distinct E2 inputs ...', flush=True)
for i, (key, j) in enumerate(sorted(union.items())):
    x, t, gp, note = assemble(j['sysid'], j['ci'], j['seed'], j['typ'], j['k'])
    fresh_sha[key] = (sha(x), x.shape[1], t['x'].shape[1], note)
    if (i + 1) % 200 == 0:
        print(f'  {i + 1}/{len(union)}', flush=True)

sha_by_key = defaultdict(dict)
for alg in ALGS:
    d = OUT / alg
    r = dict()
    exp = all_e2[alg]
    counts = {ph: len(expected(alg, ph)) for ph in ('dev', 'E1', 'E2')}
    r['expected_counts'] = counts
    r['npz_total_on_disk'] = len(list(d.glob('*.npz')))
    r['npz_total_expected'] = sum(counts.values())
    all_keys = {j['key'] for ph in ('dev', 'E1', 'E2') for j in expected(alg, ph)}
    on_disk = {f.stem for f in d.glob('*.npz')}
    r['unexpected_npz'] = sorted(on_disk - all_keys)
    r['missing_E2'] = sorted(set(exp) - on_disk)
    bad = []
    for key, j in exp.items():
        f = d / f'{key}.npz'
        if not f.exists():
            continue
        try:
            z = np.load(f, allow_pickle=False)
            meta = json.loads(str(z['meta']))
            fs, dd, dT, note = fresh_sha[key]
            for a in REQ[alg]:
                if a not in z.files:
                    bad.append((key, f'missing array {a}')); continue
                v = z[a]
                if v.shape != (dd, dd):
                    bad.append((key, f'{a} shape {v.shape} != {(dd, dd)}'))
                if not np.all(np.isfinite(v)):
                    bad.append((key, f'{a} non-finite'))
            if 'probs' in z.files and (z['probs'].min() < 0 or z['probs'].max() > 1):
                bad.append((key, 'probs outside [0,1]'))
            if meta['input_sha'] != fs:
                bad.append((key, 'I3 stored input_sha != fresh assemble'))
            if meta.get('status') != 'ok':
                bad.append((key, 'status ' + str(meta.get('status'))))
            if meta.get('d') != dd or meta.get('dT') != dT:
                bad.append((key, 'd/dT mismatch'))
            sha_by_key[key][alg] = meta['input_sha']
            if 'target_sha' in meta:
                sha_by_key[(j['sysid'], 'target')].setdefault(alg, set()).add(meta['target_sha'])
            if alg == 'foundcause' and meta.get('threads') != 4:
                bad.append((key, f"threads {meta.get('threads')} != 4"))
        except Exception as e:
            bad.append((key, 'load error ' + repr(e)))
    r['bad'] = bad
    # log
    lf = d / 'log_E2.jsonl'
    recs = [json.loads(l) for l in lf.read_text(encoding='utf-8').splitlines() if l.strip()] if lf.exists() else []
    st = Counter(x['key'] for x in recs if x['status'] == 'ok')
    r['log_lines'] = len(recs)
    r['log_errors'] = [(x['key'], x['status']) for x in recs if x['status'] != 'ok']
    r['log_keys_ok_more_than_once'] = sorted(k for k, c in st.items() if c > 1)
    r['log_ok_missing_npz'] = sorted(k for k in st if k not in on_disk)
    rt = np.array([x['runtime_s'] for x in recs if x['status'] == 'ok'], float)
    if rt.size:
        by_d = defaultdict(list)
        for x in recs:
            if x['status'] == 'ok':
                by_d[x['d']].append(x['runtime_s'])
        r['runtime_by_d_median_s'] = {int(k): float(np.median(v)) for k, v in sorted(by_d.items())}
        r['runtime_total_h'] = float(rt.sum() / 3600)
        out = []
        for x in recs:
            if x['status'] == 'ok':
                med = np.median(by_d[x['d']])
                if x['runtime_s'] > 3 * med and x['runtime_s'] > 60:
                    out.append((x['key'], x['runtime_s'], float(med)))
        r['runtime_outliers_gt3x_median'] = out
    r['notes'] = dict(Counter(fresh_sha[k][3] for k in exp if fresh_sha[k][3]))
    rep[alg] = r

# I4 cross-algorithm input identity
mism = [k for k, v in sha_by_key.items() if not isinstance(k, tuple) and len(set(v.values())) > 1]
coverage = Counter(len(v) for k, v in sha_by_key.items() if not isinstance(k, tuple))
# I5 target identity within system and vs E1 k = 0
tgt_bad = []
for s, ci, seed in systems('EXP'):
    for alg in ('avici', 'cdfm', 'foundcause'):
        vals = sha_by_key.get((s, 'target'), {}).get(alg, set())
        f0 = OUT / alg / f'{s}__-__k0__main.npz'
        m0 = json.loads(str(np.load(f0)['meta']))['target_sha']
        if vals != {m0}:
            tgt_bad.append((s, alg, sorted(vals), m0))
res = dict(per_alg=rep, I4_input_sha_mismatch_across_algs=mism, I4_n_algs_per_key=dict(coverage),
           I5_target_bad=tgt_bad)
(OUT / 'integrity_e2.json').write_text(json.dumps(res, indent=1, default=str))
for alg in ALGS:
    r = rep[alg]
    print(f"{alg:10s} disk {r['npz_total_on_disk']}/{r['npz_total_expected']} {r['expected_counts']} "
          f"missingE2 {len(r['missing_E2'])} unexpected {len(r['unexpected_npz'])} bad {len(r['bad'])} "
          f"logerr {len(r['log_errors'])} dupok {len(r['log_keys_ok_more_than_once'])} "
          f"rt {r.get('runtime_total_h', 0):.1f}h outliers {len(r.get('runtime_outliers_gt3x_median', []))} notes {r['notes']}")
    for b in r['bad'][:5]:
        print('   BAD', b)
    for o in r.get('runtime_outliers_gt3x_median', [])[:5]:
        print('   SLOW', o)
    print('   runtime median by d:', r.get('runtime_by_d_median_s'))
print('I4 mismatches:', len(mism), ' algs per key:', dict(coverage))
print('I5 target problems:', len(tgt_bad), tgt_bad[:3])
