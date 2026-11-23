#!/usr/bin/env bash
# P-N8 / Study 7 development gate (rules PN8 v1 §6): DEV8 (base 510000) and the DEV5 stand-in only; then gates G1-G5.
# Runs before the freeze, so no freeze gate here. Sequential; nothing heavy in parallel.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HERE/../../n1_models_cpu/.venv/Scripts/python.exe"
cd "$HERE"
"$PY" -I -X utf8 -W ignore run8.py DEV || exit $?
"$PY" -I -X utf8 -W ignore classical8.py pc DEV8 || exit $?
"$PY" -I -X utf8 -W ignore classical8.py ges DEV8 || exit $?
"$PY" -I -X utf8 -W ignore gates8.py "$@"
