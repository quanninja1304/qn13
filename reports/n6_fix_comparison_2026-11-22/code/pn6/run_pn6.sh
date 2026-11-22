#!/usr/bin/env bash
# P-N6 run (rules PN6 v1 §3, §10, §11 step 4). Stops before any job if the freeze gate fails; re-checks the gate at the end.
# Order: p-values; plain AVICI, CDFM; R-L AVICI, CDFM; R-H AVICI, CDFM (synthetic inputs first, then the real tables).
# A budget stop (exit 3) or any error stops the remaining steps. The script does not judge success: completeness6.py must
# pass before reading.
set -u
cd "$(dirname "$0")"
PY="../../n1_models_cpu/.venv/Scripts/python.exe"
mkdir -p ../pn6_out
LOG=../pn6_out/pn6_console.log
echo "=== start $(date -u +%FT%TZ)" >> "$LOG"
"$PY" -I -W ignore verify_freeze6.py pn6_start >> "$LOG" 2>&1 || { echo "FREEZE GATE FAILED: no P-N6 job run" >> "$LOG"; exit 1; }
STEPS=("pvals PN6" "avici PN6 plain" "cdfm PN6 plain" "avici PN6 RL" "cdfm PN6 RL" "avici PN6 RH" "cdfm PN6 RH")
for S in "${STEPS[@]}"; do
  "$PY" -I -W ignore run6.py $S >> "$LOG" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ]; then echo "STOP after $S (exit $rc)" >> "$LOG"; break; fi
done
"$PY" -I -W ignore verify_freeze6.py pn6_end >> "$LOG" 2>&1 || echo "FREEZE GATE FAILED AT END" >> "$LOG"
echo "=== end $(date -u +%FT%TZ)" >> "$LOG"
