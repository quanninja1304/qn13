"""P-N5 preparation (rules PN5 v1 §1): compute X_R of every table of a set once and save it; no model is called.

The runner and the completeness check compare each input's real block with this saved copy; gate G1 checks it against
a fresh computation, the manifest and the locked idx hashes.
usage: prep5.py <PN5|DEV5>  ->  pn5_out/inputs/<table>_XR.npy and pn5_out/inputs/prep_<set>.json (no data values)
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common5 import OUT5, SETS5, real_block, xr_file, sha

set_name = sys.argv[1]
assert set_name in SETS5
(OUT5 / 'inputs').mkdir(parents=True, exist_ok=True)
rec = {}
for t in SETS5[set_name]['tables']:
    rb = real_block(t)
    np.save(xr_file(t), rb['XR'])
    assert sha(np.load(xr_file(t))) == rb['XR_sha']
    rec[t] = dict(XR_sha=rb['XR_sha'], idx_sha=rb['idx_sha'], n_total=rb['n_total'], shape=list(rb['XR'].shape),
                  n_excess_duplicates_in_selection=rb['n_excess_duplicates'], names=rb['names'])
(OUT5 / 'inputs' / f'prep_{set_name}.json').write_text(json.dumps(rec, indent=1))
print(json.dumps({t: dict(XR_sha=v['XR_sha'][:16], idx_sha=v['idx_sha'][:16], dup=v['n_excess_duplicates_in_selection'])
                  for t, v in rec.items()}))
