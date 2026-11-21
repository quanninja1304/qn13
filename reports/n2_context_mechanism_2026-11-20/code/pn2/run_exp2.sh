#!/usr/bin/env bash
# P-N2 EXP2 run (rules v1 §0 step 5). Stops before any job if the freeze gate fails; re-checks the gate at the end.
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
export PYTHONWARNINGS=ignore
LOG=../pn2_out/exp2_console.log
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
"$PY" verify_freeze2.py exp2_start >> "$LOG" 2>&1 || { echo "FREEZE GATE FAILED: no EXP2 job run" >> "$LOG"; exit 1; }
for m in avici cdfm; do
  for arm in plain R; do
    "$PY" run2.py "$m" EXP2 "$arm" --threads 2 >> "$LOG" 2>&1 || echo "FAILED $m $arm" >> "$LOG"
  done
done
for alg in pc ges; do
  "$PY" run2_classical.py "$alg" EXP2 >> "$LOG" 2>&1 || echo "FAILED $alg" >> "$LOG"
done
"$PY" screen_variants.py EXP2 >> "$LOG" 2>&1 || echo "FAILED screen_variants" >> "$LOG"
"$PY" verify_freeze2.py exp2_end >> "$LOG" 2>&1 || echo "FREEZE GATE FAILED AT END" >> "$LOG"
echo "=== end $(date -u +%FT%TZ)" >> "$LOG"
