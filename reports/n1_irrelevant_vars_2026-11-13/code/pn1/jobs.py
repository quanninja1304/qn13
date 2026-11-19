"""Job lists per phase (rules v2 §3 + v2.1 §A5, A9, A11 + v2.2 §1-2 for HELD)."""
from common import systems, job_key, perm_for, CELLS, TYPES

# v2.2 §1: nested held-out. Seed formula identical to common.SETS['HELD'] (base 300000 + cell*1000 + r); v2.1 defined
# r in {0,1,2} (24 systems), v2.2 extends to r in 0..9 (80 systems). common.py is left untouched on purpose.
HELD_BASE = 300000
HELD_PER_CELL = {'avici': 10, 'cdfm': 10, 'pc': 10, 'ges': 10, 'foundcause': 3}
HELD_CONDS = {   # (type, k); k = 0 always included
    'avici': [('A', 20), ('B', 20)],
    'cdfm': [('A', 5), ('A', 10), ('A', 20), ('A', 30), ('B', 20), ('C', 20)],
    'foundcause': [('A', 20), ('B', 20)],
    'pc': [('A', 5), ('A', 10), ('A', 20), ('A', 30), ('B', 20), ('C', 20)],   # union of the three models' conditions
}
HELD_CONDS['ges'] = HELD_CONDS['pc']


def held_systems(per_cell):
    return [(f'HELD-c{ci}-r{r}', ci, HELD_BASE + ci * 1000 + r) for ci in range(8) for r in range(per_cell)]

N_EQUIV = 10   # RN0.1: equivariance on 10 DEV systems


def _j(sysid, ci, seed, typ, k, variant='main', **kw):
    return dict(key=job_key(sysid, typ, k, variant), sysid=sysid, ci=ci, seed=seed, typ=typ, k=k, **kw)


def jobs_for(model, phase):
    out = []
    if phase == 'dev':
        for i, (s, ci, seed) in enumerate(systems('DEV')):
            out.append(_j(s, ci, seed, '-', 0))
            if model == 'foundcause':
                out.append(_j(s, ci, seed, '-', 0, 'sched42', sched=42))      # adapter parity (= API repeat)
                out.append(_j(s, ci, seed, '-', 0, 'sched1042', sched=1042))  # tau_sched
            else:
                out.append(_j(s, ci, seed, '-', 0, 'rep'))                    # tau_rep
            if s.endswith('-r0') or s in ('DEV-c0-r1', 'DEV-c7-r1'):   # 10 systems, every cell covered
                out.append(_j(s, ci, seed, '-', 0, 'perm', perm=perm_for(s, CELLS[ci][0])))
        return out
    if phase == 'E1':
        for s, ci, seed in systems('EXP'):
            out.append(_j(s, ci, seed, '-', 0))
            out.append(_j(s, ci, seed, 'A', 20))
        return out
    if phase == 'E2':
        reduced = model == 'foundcause' and FC_REDUCED
        for s, ci, seed in systems('EXP'):
            for typ in TYPES:
                for k in (5, 10, 20, 30):
                    if typ == 'A' and k == 20:
                        continue
                    if reduced and not (typ == 'A' or k == 20):
                        continue
                    out.append(_j(s, ci, seed, typ, k))
        return out
    if phase == 'HELD':
        for s, ci, seed in held_systems(HELD_PER_CELL[model]):
            out.append(_j(s, ci, seed, '-', 0))
            for typ, k in HELD_CONDS[model]:
                out.append(_j(s, ci, seed, typ, k))
        return out
    raise ValueError(phase)


FC_REDUCED = True   # rules v2.1 §2 (user, 14/11): FoundCause E2 = reduced grid, run only if the E1 trigger fires
