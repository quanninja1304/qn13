#!/usr/bin/env bash
# P-N2 DEV2 model jobs (rules v1 §4, §9). Sequential on purpose so that G11 timings are not distorted.
# Requires pn2_out/alpha.json from dev2_data_gates.py (R arm).
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
export PYTHONWARNINGS=ignore
LOG=../pn2_out/dev2_models_console.log
test -f ../pn2_out/alpha.json || { echo "alpha.json missing: run dev2_data_gates.py first" | tee -a "$LOG"; exit 1; }
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
for m in avici cdfm; do
  for arm in plain R rep oracle; do
    "$PY" run2.py "$m" DEV2 "$arm" --threads 2 >> "$LOG" 2>&1 || echo "FAILED $m $arm" >> "$LOG"
  done
done
for alg in pc ges; do
  "$PY" run2_classical.py "$alg" DEV2 >> "$LOG" 2>&1 || echo "FAILED $alg" >> "$LOG"
done
"$PY" dev2_model_gates.py >> "$LOG" 2>&1 || echo "FAILED gates" >> "$LOG"
echo "=== end $(date -u +%FT%TZ)" >> "$LOG"
