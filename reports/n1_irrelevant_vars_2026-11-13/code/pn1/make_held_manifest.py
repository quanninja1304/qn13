"""v2.2 freeze: seed and input manifest for the held-out set. Generates targets and padded inputs only; calls no model.

usage: make_held_manifest.py  -> pn1_out/held_manifest.json
Records per system: base seed, seed actually used (zero-edge rejection rule), rejected seeds, true edge count, target sha;
per job (union over all algorithms): input sha, d, padding note. Also checks seed collisions with DEV/EXP/ORACLE.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from common import OUT, CELLS, assemble, sha, systems, target, pad_seed
from jobs import jobs_for, held_systems, HELD_PER_CELL, HELD_CONDS

used = {}
for st in ('DEV', 'EXP', 'ORACLE'):
    for s, ci, seed in systems(st):
        used[seed] = s
sysrec, problems = {}, []
for s, ci, seed in held_systems(10):
    t = target(s, ci, seed)
    for sd in [seed] + t['rejected'] + [t['seed_used']]:
        if sd in used and used[sd] != s:
            problems.append(f'seed {sd} of {s} also used by {used[sd]}')
    used[t['seed_used']] = s
    sysrec[s] = dict(cell=list(CELLS[ci]), base_seed=seed, seed_used=int(t['seed_used']), rejected=[int(x) for x in t['rejected']],
                     n_true_edges=int(t['g'].sum()), target_sha=sha(t['x']), in_foundcause_24=s.split('-r')[1] in ('0', '1', '2'))
jobs = {}
for m in ('avici', 'cdfm', 'foundcause', 'pc'):
    for j in jobs_for(m, 'HELD'):
        if j['key'] in jobs:
            continue
        x, t, gp, note = assemble(j['sysid'], j['ci'], j['seed'], j['typ'], j['k'])
        jobs[j['key']] = dict(input_sha=sha(x), d=int(x.shape[1]), note=note,
                              pad_seed=(pad_seed(j['seed'], j['typ'], j['k']) if j['k'] else None))
pads = [v['pad_seed'] for v in jobs.values() if v['pad_seed'] is not None]
if len(pads) != len(set(pads)):
    problems.append('duplicate padding seeds')
res = dict(phase='HELD', rules='v2.2', per_cell=HELD_PER_CELL, conditions={k: [list(c) for c in v] for k, v in HELD_CONDS.items()},
           n_systems=len(sysrec), n_jobs_union=len(jobs),
           jobs_per_alg={m: len(jobs_for(m, 'HELD')) for m in ('avici', 'cdfm', 'foundcause', 'pc', 'ges')},
           problems=problems, systems=sysrec, jobs=jobs)
(OUT / 'held_manifest.json').write_text(json.dumps(res, indent=1, sort_keys=True))
print(json.dumps({k: v for k, v in res.items() if k not in ('systems', 'jobs')}, indent=1))
print('rejected-seed systems:', {s: r['rejected'] for s, r in sysrec.items() if r['rejected']})
print('mean true edges by cell:', {str(c): float(np.mean([r['n_true_edges'] for r in sysrec.values() if r['cell'] == list(c)])) for c in CELLS})
