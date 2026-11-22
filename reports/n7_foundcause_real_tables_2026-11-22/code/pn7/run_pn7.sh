#!/usr/bin/env bash
# P-N7 main runs (rules PN7 v1 §10 step 4): two runs, Sachs then Wine, sequential, nothing in parallel.
# Each run: freeze gate at the start (its time starts the 3 h clock) and at the end. No result is read between runs.
# A failed freeze gate, a budget stop (exit 3), an early stop (exit 4) or any error stops everything. The script does
# not judge success: completeness7.py must pass before reading.
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
mkdir -p ../pn7_out
LOG=../pn7_out/pn7_console.log
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
for T in sachs wine; do
  "$PY" -I -W ignore verify_freeze7.py "pn7_start_$T" >> "$LOG" 2>&1 || { echo "FREEZE GATE FAILED before $T: no job run" >> "$LOG"; exit 1; }
  "$PY" -I -W ignore run7.py PN7 --table "$T" >> "$LOG" 2>&1
  rc=$?
  "$PY" -I -W ignore verify_freeze7.py "pn7_end_$T" >> "$LOG" 2>&1 || { echo "FREEZE GATE FAILED AT END of $T" >> "$LOG"; exit 1; }
  if [ "$rc" -ne 0 ]; then echo "STOP after $T (exit $rc)" >> "$LOG"; exit "$rc"; fi
done
echo "=== end $(date -u +%FT%TZ)" >> "$LOG"
