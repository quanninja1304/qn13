"""P-N3 Part B configurations (rules v1 §2), shared by partB_run.py and partB_analyze.py."""
CONFIGS = [('PLAIN', 'PLAIN', ()), ('V0-all', 'V0', tuple(range(1, 9))), ('KO-all', 'KO', tuple(range(1, 9)))] + \
          [(f'V0-{l}', 'V0', (l,)) for l in range(1, 9)] + [(f'KO-{l}', 'KO', (l,)) for l in range(1, 9)]
