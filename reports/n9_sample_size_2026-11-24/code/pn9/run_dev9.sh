#!/bin/sh
# P-N9 DEV gate runs inside the agent session (rules PN9 v1 §6): AVICI, CDFM, SEA, PC, GES. FoundCause: run_dev9_foundcause.ps1
# (user's PowerShell). Sequential; never two models at once. Memory jobs (G3) and reruns (G2) each run in a fresh process.
set -e
cd "$(dirname "$0")"
PY=../../n1_models_cpu/.venv/Scripts/python.exe
$PY -I gates9.py G1
for m in avici cdfm; do
  $PY -I run9.py $m G3
  $PY -I run9.py $m DEV
  $PY -I run9.py $m G2
  $PY -I run9.py $m REPRO
done
$PY -I run9_sea.py G3
$PY -I run9_sea.py DEV
$PY -I run9_sea.py G2
$PY -I run9_sea.py G5
$PY -I run9_classical.py pc DEV
$PY -I run9_classical.py pc G2
$PY -I run9_classical.py pc REPRO
$PY -I run9_classical.py ges G3
$PY -I run9_classical.py ges DEV
$PY -I run9_classical.py ges G2
$PY -I run9_classical.py ges REPRO
echo "DEV runs done (FoundCause: run_dev9_foundcause.ps1)"
