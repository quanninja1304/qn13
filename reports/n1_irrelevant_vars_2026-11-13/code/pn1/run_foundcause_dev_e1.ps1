# P-N1: FoundCause DEV -> RN0 gate -> E1 (rules v2.1 §2, 4 threads). Resumable: finished jobs are skipped.
# Run from any PowerShell window:  powershell -ExecutionPolicy Bypass -File run_foundcause_dev_e1.ps1
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
$py = '..\..\n1_models_cpu\.venv\Scripts\python.exe'
$env:PYTHONWARNINGS = 'ignore'

& $py run_model.py foundcause dev --threads 4
& $py rn0.py foundcause | Out-File -Encoding utf8 ..\pn1_out\rn0_foundcause_stdout.txt
$r = Get-Content ..\pn1_out\rn0_foundcause.json -Raw | ConvertFrom-Json
$ok = $r.A5_adapter_parity.PASS -and $r.'RN0.3_determinism'.PASS
Write-Host "RN0 gate (adapter parity + determinism): $ok"
if (-not $ok) { Write-Host 'Gate FAILED: E1 not started. Report to Claude.'; exit 1 }
& $py run_model.py foundcause E1 --threads 4
Write-Host 'FoundCause DEV + E1 finished.'
