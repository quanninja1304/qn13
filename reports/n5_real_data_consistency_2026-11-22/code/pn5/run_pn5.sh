#!/usr/bin/env bash
# P-N5 run (rules PN5 v1 §3, §11 step 4). Stops before any job if the freeze gate fails; re-checks the gate at the end.
# Order: AVICI, CDFM, PC, GES; each runner puts the main inputs first. A main-input timeout (exit 2) or the 3 h budget
# stop (exit 3) stops the remaining algorithms. The script does not judge success: completeness5.py must pass before reading.
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
mkdir -p ../pn5_out
LOG=../pn5_out/pn5_console.log
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
"$PY" -I -W ignore verify_freeze5.py pn5_start >> "$LOG" 2>&1 || { echo "FREEZE GATE FAILED: no P-N5 job run" >> "$LOG"; exit 1; }
for ALG in avici cdfm pc ges; do
  "$PY" -I -W ignore run5.py "$ALG" PN5 >> "$LOG" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ]; then echo "STOP after $ALG (exit $rc)" >> "$LOG"; break; fi
done
"$PY" -I -W ignore verify_freeze5.py pn5_end >> "$LOG" 2>&1 || echo "FREEZE GATE FAILED AT END" >> "$LOG"
echo "=== end $(date -u +%FT%TZ)" >> "$LOG"
