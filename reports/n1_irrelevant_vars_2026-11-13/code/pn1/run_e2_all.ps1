# P-N1 phase E2 (rules v2.1 §2, A11). Runs every model one after another, never in parallel (RAM).
# Order: AVICI, CDFM, PC, GES (full grid, 1200 jobs each), then FoundCause (reduced grid, 480 jobs; trigger met in E1).
# Resumable: finished jobs are skipped, so re-running this file after an interruption is safe.
# Run:  powershell -ExecutionPolicy Bypass -File .\run_e2_all.ps1
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
$py = '..\..\n1_models_cpu\.venv\Scripts\python.exe'
$env:PYTHONWARNINGS = 'ignore'

Write-Host "=== AVICI E2 (about 2 h) ===";      & $py run_model.py avici E2 --threads 2
Write-Host "=== CDFM E2 (about 4 h) ===";       & $py run_model.py cdfm E2 --threads 2
Write-Host "=== PC E2 (about 1 h) ===";         & $py run_classical.py pc E2
Write-Host "=== GES E2 (a few hours) ===";      & $py run_classical.py ges E2
Write-Host "=== FoundCause E2 reduced (about 50 h) ==="; & $py run_model.py foundcause E2 --threads 4
Write-Host 'P-N1 E2 finished for all models.'
