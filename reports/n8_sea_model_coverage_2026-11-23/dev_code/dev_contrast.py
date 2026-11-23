"""Descriptive only (development inputs): seed-only disagreement at k0 vs disagreement after padding, using runs A (seed 0)
and C (seed 1) as two independent schedule draws per input (order-dependent streams), plus F1 at both seeds."""
import json, pickle, sys
from pathlib import Path
import numpy as np
W = Path(sys.argv[1])
inputs = {i['key']: i for i in json.loads((W / 'inputs.json').read_text(encoding='utf-8'))}
R = {r: pickle.load(open(W / f'run_{r}.pkl', 'rb')) for r in ('A_seed0', 'C_seed1')}
def prob(res, key):
    D = inputs[key]['d']; P = D * (D - 1) // 2; p = np.asarray(res[key]['pred'][0], float)
    iu = np.triu_indices(D, 1); F, B = np.zeros((D, D)), np.zeros((D, D)); F[iu], B[iu] = p[:P], p[P:]
    return F + B.T
def skel(pr, dT):
    return (np.maximum(pr, pr.T)[:dT, :dT] > 0.5)[np.triu_indices(dT, 1)]
def f1(s, key, dT):
    G = np.load(W / 'inputs' / key / 'DAG.npy'); g = ((G + G.T) > 0)[:dT, :dT][np.triu_indices(dT, 1)]
    tp, fp, fn = int((g & s).sum()), int((~g & s).sum()), int((g & ~s).sum())
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)
for root, dT in (('standin', 11), ('DEV2-c0-r0', 10), ('DEV2-c7-r1', 20)):
    k0 = f'{root}__k0'
    kA, kC = skel(prob(R['A_seed0'], k0), dT), skel(prob(R['C_seed1'], k0), dT)
    print(f'{root}: pairs={dT*(dT-1)//2} seed-only flips(k0@A,k0@C)={int((kA!=kC).sum())} F1 k0: A={f1(kA,k0,dT):.3f} C={f1(kC,k0,dT):.3f}')
    for key in inputs:
        if not key.startswith(root + '__') or key == k0: continue
        pA, pC = skel(prob(R['A_seed0'], key), dT), skel(prob(R['C_seed1'], key), dT)
        sym1 = int((kC != pA).sum()) - int((kC != kA).sum())
        sym2 = int((kA != pC).sum()) - int((kA != kC).sum())
        print(f'   {key:<24} same-run flips: A={int((kA!=pA).sum())} C={int((kC!=pC).sum())} | cross-seed: (k0@C,pad@A)={int((kC!=pA).sum())} (k0@A,pad@C)={int((kA!=pC).sum())} | symmetric contrast: {sym1:+d} {sym2:+d} | F1 pad: A={f1(pA,key,dT):.3f} C={f1(pC,key,dT):.3f}')
