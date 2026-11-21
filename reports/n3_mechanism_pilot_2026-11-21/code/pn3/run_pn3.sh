#!/usr/bin/env bash
# P-N3 pilot run (rules v1 §6). Stops before any computation if the freeze gate fails; re-checks the gate at the end.
# Completeness is checked again by partB_analyze.py, which refuses to read if any output is missing, failed or stale.
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
export PYTHONWARNINGS=ignore
LOG=../pn3_out/pn3_console.log
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
"$PY" verify_freeze_pn3.py pn3_start >> "$LOG" 2>&1 || { echo "FREEZE GATE FAILED: nothing run" >> "$LOG"; exit 1; }
"$PY" partA_cdfm.py >> "$LOG" 2>&1 || echo "FAILED partA" >> "$LOG"
"$PY" partB_run.py >> "$LOG" 2>&1 || echo "FAILED partB_run" >> "$LOG"
"$PY" verify_freeze_pn3.py pn3_end >> "$LOG" 2>&1 || echo "FREEZE GATE FAILED AT END" >> "$LOG"
echo "=== end $(date -u +%FT%TZ)" >> "$LOG"
