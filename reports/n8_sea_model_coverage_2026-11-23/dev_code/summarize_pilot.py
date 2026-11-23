"""Step 1 (exploratory): per-cell summary of sea_input_pilot.json, as reported in PN8_pilot1_inputs_vi.md section 3.

The pilot rows store the structured-padding summary under the key 'eT', which overwrote the cell's e_T number, so the cell
is taken from the system id (EXP2-c<ci>-r<r>) and its definition from the frozen Study 2 code (common2.CELLS).
usage (Study 1 model environment): python -I summarize_pilot.py <artifacts dir> <sea_input_pilot.json>
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ART = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ART / 'n2_runs' / 'pn2'))
import common2 as C2

res = json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
by_cell = defaultdict(list)
for row in res['exp2']:
    ci = int(row['sys'].split('-c')[1].split('-')[0])
    by_cell[ci].append(row)

m = lambda rows, c, k: float(np.mean([r[c][k] for r in rows]))
print('ci dT mech eT | cov k0, e0, eT | e0/k0, eT/k0 | target slot share e0; eT | 2nd/1st half e0; eT | rho drift e0; eT | |rho| k0')
for ci in sorted(by_cell):
    rows = by_cell[ci]
    dT, eT, mech = C2.CELLS[ci]
    k0, g, s = m(rows, 'k0', 'mean_cov'), m(rows, 'e0', 'mean_cov'), m(rows, 'eT', 'mean_cov')
    half = lambda c: float(np.mean([r[c]['cov_second_half'] / r[c]['cov_first_half'] for r in rows]))
    print(f"c{ci} {dT} {mech} {eT} | {k0:.1f} {g:.1f} {s:.1f} | {g / k0:.2f} {s / k0:.2f} | "
          f"{m(rows, 'e0', 'target_slot_share'):.2f}; {m(rows, 'eT', 'target_slot_share'):.2f} | {half('e0'):.2f}; {half('eT'):.2f} | "
          f"{m(rows, 'e0', 'pc_drift_mean_abs'):.4f}; {m(rows, 'eT', 'pc_drift_mean_abs'):.4f} | {m(rows, 'k0', 'pc_k0_mean_abs'):.3f}")
allr = res['exp2']
ratio = lambda c: float(np.mean([r[c]['mean_cov'] / r['k0']['mean_cov'] for r in allr]))
print(f"all {len(allr)} systems: coverage ratio e0 {ratio('e0'):.2f}, eT {ratio('eT'):.2f}; "
      f"share uncovered e0 {m(allr, 'e0', 'share_uncovered'):.4f}, eT {m(allr, 'eT', 'share_uncovered'):.4f}; "
      f"rho drift e0 {m(allr, 'e0', 'pc_drift_mean_abs'):.4f}, eT {m(allr, 'eT', 'pc_drift_mean_abs'):.4f}")
print('stand-in table (d = 11):')
for r in res['standin']:
    print(f"  {r['cond']:<7} r={r['r']} cov {r['mean_cov']:.1f} min {r['min_cov']:.1f} uncovered {r['share_uncovered']:.3f} "
          f"target slot share {r['target_slot_share']:.2f} halves {r['cov_first_half']:.1f}; {r['cov_second_half']:.1f} "
          f"rho drift {r['pc_drift_mean_abs']:.4f} (max {r['pc_drift_max_abs']:.3f})")
