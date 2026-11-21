#!/usr/bin/env bash
# P-N4 run (rules PN4 v1 §0 step 4). Stops before any job if the freeze gate fails; re-checks the gate at the end.
# The script itself does not judge success: completeness4.py must pass before reading (rules PN4 §7).
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
export PYTHONWARNINGS=ignore
mkdir -p ../pn4_out
LOG=../pn4_out/pn4_console.log
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
"$PY" verify_freeze4.py pn4_start >> "$LOG" 2>&1 || { echo "FREEZE GATE FAILED: no P-N4 job run" >> "$LOG"; exit 1; }
"$PY" run4.py PN4 --threads 2 >> "$LOG" 2>&1 || echo "FAILED run4 PN4" >> "$LOG"
"$PY" verify_freeze4.py pn4_end >> "$LOG" 2>&1 || echo "FREEZE GATE FAILED AT END" >> "$LOG"
echo "=== end $(date -u +%FT%TZ)" >> "$LOG"
