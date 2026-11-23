#!/usr/bin/env bash
# P-N8 / Study 7 main runs (rules PN8 v1 §8): A1, A2, A3, A4, B in order, each between a start and an end freeze gate;
# the budget clock of a run starts at its start header. Stops at the first failure. Then the classical controls, and
# the interleaved branch IL only if gate G3 labelled SEA POSITION_SENSITIVE. No reading of results between runs.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HERE/../../n1_models_cpu/.venv/Scripts/python.exe"
cd "$HERE"
RUNS="A1 A2 A3 A4 B"
if grep -q '"label": "POSITION_SENSITIVE"' ../pn8_out/gates8.json; then RUNS="$RUNS IL"; fi
for run in $RUNS; do
  "$PY" -I -X utf8 verify_freeze8.py "pn8_start_$run" > /dev/null || { echo "freeze gate failed before $run"; exit 1; }
  "$PY" -I -X utf8 -W ignore run8.py "$run" || { echo "run $run stopped"; exit 1; }
  "$PY" -I -X utf8 verify_freeze8.py "pn8_end_$run" > /dev/null || { echo "freeze gate failed after $run"; exit 1; }
done
"$PY" -I -X utf8 -W ignore classical8.py pc PN8 || exit 1
"$PY" -I -X utf8 -W ignore classical8.py ges PN8 || exit 1
echo "all main runs done"
