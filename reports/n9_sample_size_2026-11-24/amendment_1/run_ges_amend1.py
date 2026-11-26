"""P-N9 amendment 1 (PN9_amendment1_vi.md, 26 Nov 2026): finish GES R1 and run GES R3 under the stop-mark procedure.

Each session: verify_freeze9.py pn9_start_ges_<run> (a new start header, so the run's budget clock starts again), then the
frozen runner run9_classical.py ges <run>, which skips finished jobs whose output matches the input hash. Runner exit 2
(budget stop) opens a new session only while the total GES main-run time is below the cap (amendment item 3); any other
non-zero exit stops. After a finished run: verify_freeze9.py pn9_end_ges_<run>. Sessions are logged to
pn9_out/ges_amend1_sessions.jsonl and the output of every call to pn9_out/ges_amend1_console.log. No metric is computed or
printed. Frozen code is called, never imported or changed.
usage: <Study 1 model environment python> -I run_ges_amend1.py
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PN9 = REPO / 'artifacts' / 'n9_runs' / 'pn9'
OUT = PN9.parent / 'pn9_out'
PY = REPO / 'artifacts' / 'n1_models_cpu' / '.venv' / 'Scripts' / 'python.exe'
CAP_S = 1.8 * 3600                       # item 3: 1.5 x the 1.2 h GES estimate of rules §8
FIRST_KEY, FIRST_S = 'PN9-c2-r14__n4000__k0', 373.3   # first GES R1 session, from its budget_stop record
SESS = OUT / 'ges_amend1_sessions.jsonl'
CON = OUT / 'ges_amend1_console.log'


def say(msg):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(CON, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def call(*args):
    say('=== ' + ' '.join(args))
    with open(CON, 'a', encoding='utf-8') as f:
        rc = subprocess.run([str(PY), '-I', *args], cwd=PN9, stdout=f, stderr=subprocess.STDOUT).returncode
    say(f'exit {rc}')
    return rc


def used_s():
    t = FIRST_S
    if SESS.exists():
        t += sum(json.loads(l)['elapsed_s'] for l in SESS.read_text(encoding='utf-8').splitlines() if l.strip())
    return t


def last_start(run):
    hs = [h for h in json.loads((OUT / 'pn9_run_header.json').read_text()) if h['label'] == f'pn9_start_ges_{run}']
    return hs[-1]


stops = [json.loads(l) for l in (OUT / 'log_ges_R1.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
stops = [r for r in stops if r.get('status') == 'budget_stop']
if not stops or stops[0]['key'] != FIRST_KEY or stops[0]['elapsed_s'] != FIRST_S:
    sys.exit('the first GES R1 budget stop is not the one in the amendment: stop')
say(f'GES amendment-1 runs start; time used so far {used_s():.1f} s of {CAP_S:.0f} s')
for run in ('R1', 'R3'):
    while True:
        if used_s() >= CAP_S:
            say(f'CAP REACHED before a new {run} session ({used_s():.1f} s): stop and report (amendment item 3)')
            sys.exit(4)
        if call('verify_freeze9.py', f'pn9_start_ges_{run}') != 0:
            say(f'STOPPED: start freeze check of ges {run} failed')
            sys.exit(1)
        h = last_start(run)
        if not h['ok']:
            say(f'STOPPED: last start header of ges {run} not ok')
            sys.exit(1)
        rc = call('run9_classical.py', 'ges', run)
        now = time.time()
        rec = dict(run=run, start_header_local=h['time_local'], start_unix=h['time_unix'], exit_unix=now,
                   elapsed_s=round(now - h['time_unix'], 1), rc=rc)
        with open(SESS, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + '\n')
        say(f"ges {run} session: {rec['elapsed_s']} s, runner exit {rc}; total used {used_s():.1f} s")
        if rc == 0:
            break
        if rc != 2:
            say(f'STOPPED: runner exit {rc} (rules §8): report')
            sys.exit(rc)
        say(f'budget stop in ges {run}: add it to allowed_stops9.json and the amendment log (item 6); new session')
    if call('verify_freeze9.py', f'pn9_end_ges_{run}') != 0:
        say(f'STOPPED: end freeze check of ges {run} failed')
        sys.exit(1)
say('GES amendment-1 runs finished')
