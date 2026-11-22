#!/usr/bin/env bash
# P-N6 DEV6 (rules PN6 v1 §8, §11 step 3): p-values, alpha choice by J (no model output), model runs, gates G1-G9.
# Sequential (RAM); no model is run on the real tables here.
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
mkdir -p ../pn6_out
LOG=../pn6_out/dev6_console.log
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
"$PY" -I -W ignore run6.py pvals DEV6 >> "$LOG" 2>&1 || { echo "STOP after pvals" >> "$LOG"; exit 1; }
"$PY" -I -W ignore alpha6.py >> "$LOG" 2>&1 || { echo "STOP after alpha6" >> "$LOG"; exit 1; }
for M in avici cdfm; do
  for ARM in plain RL RH fullRL fullRH oracle rep; do
    "$PY" -I -W ignore run6.py "$M" DEV6 "$ARM" >> "$LOG" 2>&1 || { echo "STOP after $M $ARM" >> "$LOG"; exit 1; }
  done
done
"$PY" -I -W ignore gates6.py >> "$LOG" 2>&1
rc=$?
echo "=== end $(date -u +%FT%TZ) gates exit $rc" >> "$LOG"
exit $rc
