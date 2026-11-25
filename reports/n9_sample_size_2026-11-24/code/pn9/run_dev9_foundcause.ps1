# P-N9 DEV gate runs for FoundCause (rules PN9 v1 §6). Run in your own PowerShell window, not in the agent session.
# About 1-1.5 h. Steps, in order, each in a fresh process: G3 (memory job alone), DEV (16 timing jobs at n = 125 and 200),
# G2 (rerun of the first DEV job), REPRO (one Study 1 input; the output must equal Study 1's saved output bitwise).
# Resumable: finished jobs are skipped, so re-running this file after an interruption is safe.
# Run:  powershell -ExecutionPolicy Bypass -File .\run_dev9_foundcause.ps1
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
$py = '..\..\n1_models_cpu\.venv\Scripts\python.exe'
$env:PYTHONWARNINGS = 'ignore'
New-Item -ItemType Directory -Force '..\pn9_out' | Out-Null
$log = '..\pn9_out\dev_foundcause_console.log'

# Turn off QuickEdit for this window only (a click inside the window would otherwise pause the run).
$sig = @'
[DllImport("kernel32.dll")] public static extern System.IntPtr GetStdHandle(int h);
[DllImport("kernel32.dll")] public static extern bool GetConsoleMode(System.IntPtr h, out uint m);
[DllImport("kernel32.dll")] public static extern bool SetConsoleMode(System.IntPtr h, uint m);
'@
try {
    $k = Add-Type -MemberDefinition $sig -Name 'Con' -Namespace 'PN9Dev' -PassThru
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

Run-Step 'FoundCause G3: memory job alone (about 8 min)'      @('run9.py', 'foundcause', 'G3')
Run-Step 'FoundCause DEV: 16 timing jobs (about 45-60 min)'   @('run9.py', 'foundcause', 'DEV')
Run-Step 'FoundCause G2: rerun in a fresh process (3 min)'    @('run9.py', 'foundcause', 'G2')
Run-Step 'FoundCause REPRO: one Study 1 input (3 min)'        @('run9.py', 'foundcause', 'REPRO')
Write-Host 'FoundCause DEV runs finished.'
Add-Content -Path $log -Value "FoundCause DEV runs finished $(Get-Date -Format s)" -Encoding utf8
