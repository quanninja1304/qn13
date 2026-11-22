#!/usr/bin/env bash
# P-N7 DEV7 (rules PN7 v1 §7, §10 step 3): FoundCause on the DEV5 stand-in table and on the P-N1 DEV input (G2), then
# gates G1-G8. Sequential; nothing else runs in parallel.
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
mkdir -p ../pn7_out
LOG=../pn7_out/dev7_console.log
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
"$PY" -I -W ignore run7.py DEV7 >> "$LOG" 2>&1
rc=$?
echo "run7 DEV7 exit $rc" >> "$LOG"
if [ "$rc" -eq 0 ]; then
  "$PY" -I -W ignore gates7.py >> "$LOG" 2>&1
  echo "gates7 exit $?" >> "$LOG"
fi
echo "=== end $(date -u +%FT%TZ)" >> "$LOG"
