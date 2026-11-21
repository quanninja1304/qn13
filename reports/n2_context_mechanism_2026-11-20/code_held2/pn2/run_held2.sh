#!/usr/bin/env bash
# P-N2 HELD2 run (rules held2 v1 §0 step 4). Stops before any job if the freeze gate fails; re-checks the gate at the end.
# The script itself does not judge success: held2_completeness.py must pass before reading (rules held2 §6).
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
export PYTHONWARNINGS=ignore
LOG=../pn2_out/held2_console.log
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
"$PY" verify_freeze_held2.py held2_start >> "$LOG" 2>&1 || { echo "FREEZE GATE FAILED: no HELD2 job run" >> "$LOG"; exit 1; }
for m in avici cdfm; do
  for arm in plain R; do
    "$PY" run2_held2.py "$m" HELD2 "$arm" --threads 2 >> "$LOG" 2>&1 || echo "FAILED $m $arm" >> "$LOG"
  done
done
"$PY" verify_freeze_held2.py held2_end >> "$LOG" 2>&1 || echo "FREEZE GATE FAILED AT END" >> "$LOG"
echo "=== end $(date -u +%FT%TZ)" >> "$LOG"
