# P-N1 held-out (rules v2.2). Sequential, never in parallel (RAM). About 8 h in total, FoundCause about 6.5 h of it.
# Order: freeze gate, AVICI (240 jobs), CDFM (560), PC (560), GES (560), FoundCause (72, 4 threads).
# Resumable: finished jobs are skipped, so re-running this file after an interruption is safe.
# Run:  powershell -ExecutionPolicy Bypass -File .\run_heldout.ps1
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
$py = '..\..\n1_models_cpu\.venv\Scripts\python.exe'
$env:PYTHONWARNINGS = 'ignore'
$log = '..\pn1_out\held_console.log'

# Turn off QuickEdit for this window only (a click inside the window would otherwise pause the run).
$sig = @'
[DllImport("kernel32.dll")] public static extern System.IntPtr GetStdHandle(int h);
[DllImport("kernel32.dll")] public static extern bool GetConsoleMode(System.IntPtr h, out uint m);
[DllImport("kernel32.dll")] public static extern bool SetConsoleMode(System.IntPtr h, uint m);
'@
try {
    $k = Add-Type -MemberDefinition $sig -Name 'Con' -Namespace 'PN1Held' -PassThru
    $hIn = $k::GetStdHandle(-10); $m = [uint32]0
    if ($k::GetConsoleMode($hIn, [ref]$m)) {
        $new = [uint32](($m -band 0xFFFFFFBF) -bor 0x80)
        if ($k::SetConsoleMode($hIn, $new)) { Write-Host 'QuickEdit disabled for this window.' }
    }
} catch { Write-Host 'Could not disable QuickEdit: do not click inside this window.' }

function Run-Step($title, [string[]]$pyArgs) {
    Write-Host "=== $title ==="
    Add-Content -Path $log -Value "=== $title $(Get-Date -Format s) ===" -Encoding utf8
    & $py @pyArgs | ForEach-Object { Write-Host $_; Add-Content -Path $log -Value $_ -Encoding utf8 }
}

& $py verify_freeze.py held_start
if ($LASTEXITCODE -ne 0) { Write-Host 'FREEZE CHECK FAILED: nothing was run. Send the output above to Claude.'; exit 1 }

Run-Step 'AVICI HELD (about 15 min)'        @('run_model.py', 'avici', 'HELD', '--threads', '2')
Run-Step 'CDFM HELD (about 1 h)'            @('run_model.py', 'cdfm', 'HELD', '--threads', '2')
Run-Step 'PC HELD (a few minutes)'          @('run_classical.py', 'pc', 'HELD')
Run-Step 'GES HELD (about 30-60 min)'       @('run_classical.py', 'ges', 'HELD')
Run-Step 'FoundCause HELD (about 6.5 h)'    @('run_model.py', 'foundcause', 'HELD', '--threads', '4')
& $py verify_freeze.py held_end
Write-Host 'P-N1 held-out finished for all algorithms.'
Add-Content -Path $log -Value "P-N1 held-out finished $(Get-Date -Format s)" -Encoding utf8
