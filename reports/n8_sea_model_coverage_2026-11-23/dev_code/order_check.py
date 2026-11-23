import pickle, sys
from pathlib import Path
import numpy as np
W = Path(sys.argv[1])
A = pickle.load(open(W / 'run_A_seed0.pkl', 'rb'))
print('A keys sample:', list(A)[:3])
for solo, key in (('solo_c0k0_seed0.pkl', 'DEV2-c0-r0__k0'), ('one_seed0.pkl', 'standin__k0')):
    S = pickle.load(open(W / solo, 'rb'))
    print(solo, 'keys:', list(S))
    sk = [k for k in S if key in str(k)][0]
    ak = [k for k in A if key in str(k)][0]
    p_s, p_a = np.asarray(S[sk]['pred'][0], float), np.asarray(A[ak]['pred'][0], float)
    print(key, 'solo vs position in run A: bitwise', np.array_equal(p_s, p_a), 'max|dp|', float(np.abs(p_s - p_a).max()))
