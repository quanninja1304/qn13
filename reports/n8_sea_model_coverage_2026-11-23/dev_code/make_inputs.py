"""Feasibility check for SEA (step 2): write development inputs in SEA's format. Runs no model.

Each input goes to <work>/inputs/<key>/data.npy (rows x variables, float32) and DAG.npy (true graph of the whole table,
int64; zeros where no ground truth is defined), and a CSV lists them with SEA's columns (fp_data, fp_graph, fp_regime,
split=test). Inputs come from the frozen builders: the DEV5 stand-in table of Study 4 (d = 11) and two DEV2 systems of
Study 2. No real table and no held-out set is used.
usage (Study 1 model environment): python -I make_inputs.py <artifacts dir> <work dir>
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ART, WORK = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
for sub in ('n1_runs/pn1', 'n2_runs/pn2', 'n5_runs/pn5'):
    sys.path.insert(0, str(ART / sub))
import common2 as C2
import common5 as C5
from avici import simulate_data

inputs = []


def put(key, X, G):
    d = WORK / 'inputs' / key
    d.mkdir(parents=True, exist_ok=True)
    X = np.ascontiguousarray(X, dtype=np.float32)
    np.save(d / 'data.npy', X)
    np.save(d / 'DAG.npy', np.asarray(G, dtype=np.int64))
    inputs.append(dict(key=key, d=int(X.shape[1]), sha=hashlib.sha256(X.tobytes()).hexdigest()))


# stand-in table: its true graph, regenerated with the same frozen call as common5.real_block
g_si, _, _ = simulate_data(d=11, n=500, seed=999000, path=str(C5.cfg_path(2, 'rff')))
for cond, r in (('k0', None), ('k20_e0', 0), ('k20_e0', 1), ('k20_e2', 0), ('k40_e0', 0)):
    X, rb, pad = C5.assemble5('DEV5', 'standin', cond, r)
    D = X.shape[1]
    G = np.zeros((D, D), dtype=np.int64)
    G[:11, :11] = g_si
    if pad is not None:
        G[11:, 11:] = pad['g']
    put(C5.key5('standin', cond, r), X, G)

for sysid, ci, seed in C2.systems2('DEV2'):
    if sysid not in ('DEV2-c0-r0', 'DEV2-c7-r1'):
        continue
    for cond in ('k0', 'e0', C2.rep_cond(ci)):
        X, t, pad = C2.assemble2(sysid, ci, seed, cond)
        D, dT = X.shape[1], t['g'].shape[0]
        G = np.zeros((D, D), dtype=np.int64)
        G[:dT, :dT] = t['g']
        if pad is not None:
            G[dT:, dT:] = pad['g']
        put(f'{sysid}__{cond}', X, G)

with open(WORK / 'inputs.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['fp_data', 'fp_graph', 'fp_regime', 'split'])
    for it in inputs:
        d = (WORK / 'inputs' / it['key']).as_posix()
        w.writerow([f'{d}/data.npy', f'{d}/DAG.npy', '', 'test'])
(WORK / 'inputs.json').write_text(json.dumps(inputs, indent=1), encoding='utf-8')
print(len(inputs), 'inputs:', [(i['key'], i['d']) for i in inputs])
