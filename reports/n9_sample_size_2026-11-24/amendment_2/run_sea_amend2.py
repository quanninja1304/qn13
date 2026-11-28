"""P-N9 amendment 2 (PN9_amendment2_vi.md, 28 Nov 2026): SEA R3 in a new session, then SEA R4.

For each run: verify_freeze9.py pn9_start_sea_<run> (a new start header, so the run's budget clock starts again), then the
frozen runner run9_sea.py <run>, which skips finished jobs whose output matches the input hash and runs the others, then
verify_freeze9.py pn9_end_sea_<run>. Any non-zero exit stops (rules §8; the amendment opens no other session). Sessions are
logged to pn9_out/sea_amend2_sessions.jsonl and every call's output to pn9_out/sea_amend2_console.log and to the console.
No metric is computed or printed. Frozen code is called, never imported or changed.
Run it in your own PowerShell window (not in the agent session), with nothing else running:
  & "<repo>\\artifacts\\n1_models_cpu\\.venv\\Scripts\\python.exe" -I "<repo>\\reports\\n9_sample_size_2026-11-24\\amendment_2\\run_sea_amend2.py"
"""
import ctypes
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PN9 = REPO / 'artifacts' / 'n9_runs' / 'pn9'
OUT = PN9.parent / 'pn9_out'
PY = REPO / 'artifacts' / 'n1_models_cpu' / '.venv' / 'Scripts' / 'python.exe'
SESS = OUT / 'sea_amend2_sessions.jsonl'
CON = OUT / 'sea_amend2_console.log'
ERR_KEY = 'PN9-c6-r8__n5000__A20__s740983'

if os.name == 'nt':
    k32 = ctypes.windll.kernel32
    k32.SetThreadExecutionState(0x80000000 | 0x00000001)       # no idle sleep while this runs (not a requested sleep)
    h, m = k32.GetStdHandle(-10), ctypes.c_uint32()
    if k32.GetConsoleMode(h, ctypes.byref(m)):                  # QuickEdit off: a click in the window cannot pause the run
        k32.SetConsoleMode(h, (m.value & ~0x40) | 0x80)


def say(msg):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(CON, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def call(*args):
    say('=== ' + ' '.join(args))
    p = subprocess.Popen([str(PY), '-I', *args], cwd=PN9, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         errors='replace', bufsize=1)
    with open(CON, 'a', encoding='utf-8') as f:
        for line in p.stdout:
            print(line, end='', flush=True)
            f.write(line)
            f.flush()
    rc = p.wait()
    say(f'exit {rc}')
    return rc


def headers(label):
    return [h for h in json.loads((OUT / 'pn9_run_header.json').read_text()) if h['label'] == label]


log3 = [json.loads(l) for l in (OUT / 'log_sea_R3.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
bad = [(r['key'], r.get('status')) for r in log3 if r.get('status') != 'ok']
if bad != [(ERR_KEY, 'error: exit timeout')]:
    sys.exit(f'the non-ok records of SEA R3 are not the one in the amendment: {bad}')
if headers('pn9_start_sea_R4') or (OUT / 'log_sea_R4.jsonl').exists():
    sys.exit('SEA R4 has already been started: stop and report')
say('SEA amendment-2 runs start')
for run in ('R3', 'R4'):
    if call('verify_freeze9.py', f'pn9_start_sea_{run}') != 0 or not headers(f'pn9_start_sea_{run}')[-1]['ok']:
        say(f'STOPPED: start freeze check of sea {run} failed. Send this window to Claude.')
        sys.exit(1)
    t0 = headers(f'pn9_start_sea_{run}')[-1]['time_unix']
    rc = call('run9_sea.py', run)
    now = time.time()
    with open(SESS, 'a', encoding='utf-8') as f:
        f.write(json.dumps(dict(run=run, start_unix=t0, exit_unix=now, elapsed_s=round(now - t0, 1), rc=rc)) + '\n')
    say(f'sea {run} session: {now - t0:.0f} s, runner exit {rc}')
    if rc != 0:
        say(f'STOPPED: SEA {run} exited with code {rc} (rules §8). Send this window to Claude; do not restart.')
        sys.exit(rc)
    if call('verify_freeze9.py', f'pn9_end_sea_{run}') != 0:
        say(f'STOPPED: end freeze check of sea {run} failed. Send this window to Claude.')
        sys.exit(1)
say('P-N9 SEA amendment-2 runs finished. Tell Claude.')
