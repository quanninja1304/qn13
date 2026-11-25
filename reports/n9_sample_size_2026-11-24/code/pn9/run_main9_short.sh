#!/bin/sh
# P-N9 main runs that are short enough for the agent session (rules PN9 v1 §8): AVICI and CDFM (R1-R4), PC and GES (R1, R3:
# linear cells only). About 14 h. Sequential. Each run is bracketed by the freeze gate (start header starts the budget clock;
# the end header is required by the completeness check). Resumable: finished jobs are skipped.
set -e
cd "$(dirname "$0")"
PY=../../n1_models_cpu/.venv/Scripts/python.exe
for m in avici cdfm; do
  for r in R1 R2 R3 R4; do
    $PY -I verify_freeze9.py pn9_start_${m}_${r}
    $PY -I run9.py $m $r
    $PY -I verify_freeze9.py pn9_end_${m}_${r}
  done
done
for m in pc ges; do
  for r in R1 R3; do
    $PY -I verify_freeze9.py pn9_start_${m}_${r}
    $PY -I run9_classical.py $m $r
    $PY -I verify_freeze9.py pn9_end_${m}_${r}
  done
done
echo "short main runs done"
