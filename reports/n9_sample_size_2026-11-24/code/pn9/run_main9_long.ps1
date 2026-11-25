# P-N9 main runs for FoundCause and SEA (rules PN9 v1 §8). Run in your own PowerShell window, not in the agent session, and
# only after the short runs (run_main9_short.sh) have finished: never two models at once. About 61 h in total.
# Each run is bracketed by the freeze gate; a run stops at its budget mark, at a failed job or at a failed adapter check.
# Resumable: finished jobs are skipped, so re-running this file after an interruption is safe (the start header of an
# interrupted run is written again, which restarts that run's budget clock: tell Claude if this happens).
# Run:  powershell -ExecutionPolicy Bypass -File .\run_main9_long.ps1
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
$py = '..\..\n1_models_cpu\.venv\Scripts\python.exe'
$env:PYTHONWARNINGS = 'ignore'
New-Item -ItemType Directory -Force '..\pn9_out' | Out-Null
$log = '..\pn9_out\main_long_console.log'

$sig = @'
[DllImport("kernel32.dll")] public static extern System.IntPtr GetStdHandle(int h);
[DllImport("kernel32.dll")] public static extern bool GetConsoleMode(System.IntPtr h, out uint m);
[DllImport("kernel32.dll")] public static extern bool SetConsoleMode(System.IntPtr h, uint m);
'@
try {
    $k = Add-Type -MemberDefinition $sig -Name 'Con' -Namespace 'PN9Main' -PassThru
    $hIn = $k::GetStdHandle(-10); $m = [uint32]0
    if ($k::GetConsoleMode($hIn, [ref]$m)) {
        $new = [uint32](($m -band 0xFFFFFFBF) -bor 0x80)
        if ($k::SetConsoleMode($hIn, $new)) { Write-Host 'QuickEdit disabled for this window.' }
    }
} catch { Write-Host 'Could not disable QuickEdit: do not click inside this window.' }

function Run-Step($title, [string[]]$pyArgs) {
    Write-Host "=== $title ==="
    Add-Content -Path $log -Value "=== $title $(Get-Date -Format s) ===" -Encoding utf8
    & $py -I @pyArgs | ForEach-Object { Write-Host $_; Add-Content -Path $log -Value $_ -Encoding utf8 }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "STOPPED: $title exited with code $LASTEXITCODE. Send the output above to Claude."
        Add-Content -Path $log -Value "STOPPED: $title exit $LASTEXITCODE" -Encoding utf8
        exit 1
    }
}

foreach ($r in @('R1', 'R2', 'R3', 'R4')) {
    Run-Step "freeze gate: start foundcause $r" @('verify_freeze9.py', "pn9_start_foundcause_$r")
    Run-Step "FoundCause $r" @('run9.py', 'foundcause', $r)
    Run-Step "freeze gate: end foundcause $r" @('verify_freeze9.py', "pn9_end_foundcause_$r")
}
foreach ($r in @('R1', 'R2', 'R3', 'R4')) {
    Run-Step "freeze gate: start sea $r" @('verify_freeze9.py', "pn9_start_sea_$r")
    Run-Step "SEA $r" @('run9_sea.py', $r)
    Run-Step "freeze gate: end sea $r" @('verify_freeze9.py', "pn9_end_sea_$r")
}
Write-Host 'P-N9 long main runs finished.'
Add-Content -Path $log -Value "P-N9 long main runs finished $(Get-Date -Format s)" -Encoding utf8
