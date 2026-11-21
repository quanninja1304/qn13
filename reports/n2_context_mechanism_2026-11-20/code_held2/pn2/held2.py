"""P-N2 HELD2 (rules PN2_rules_held2 v1, locked 2026-11-21 at commit 7bc8ba0): systems and inputs.

Imports the frozen P-N2 modules (common2.py, fddfadd) unchanged. No metric is computed here.
"""
from common2 import *

HELD2_BASE, HELD2_REPS = 430000, 15


def systems_held2():
    return [(f'HELD2-c{ci}-r{r}', ci, HELD2_BASE + ci * 1000 + r) for ci in range(8) for r in range(HELD2_REPS)]


def systems_by_set(set_name):
    """HELD2 for the confirmation run; EXP2 only for validating the reading code (rules held2 §7)."""
    return systems_held2() if set_name == 'HELD2' else systems2(set_name)


def conds_held2(ci):
    """k0, e = 0, e = e_T of the cell (rules held2 §1)."""
    return ['k0', 'e0', rep_cond(ci)]
