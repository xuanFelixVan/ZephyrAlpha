# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.start_ch_health_probe
# [DOMAIN] D_DATA
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# start_ch_health_probe.ps1 - CH health probe guard process (auto-restart on crash)
#
# Boot chain (watchdog architecture, single entry, mirrors start_scheduler.ps1):
#   Task Scheduler "ZephyrAlpha_CHHealthProbe" (AtLogOn + repeat every 5min, interactive user)
#     -> this script (while-true, single-instance lock = idempotent re-entry)
#       -> python scripts/ops/ch_health_probe.py
#
# Design:
#   - while($true): auto-restart probe on crash, 7x24 CH connectivity monitoring (post-market/weekends/holidays)
#   - Single-instance lock: file lock + PID check (rule: only 1 guard + 1 probe)
#   - Orphan cleanup: always clean orphan probe on start (incl. manually started, ensures guard takeover)
#   - finally-kill: guard exit kills child probe (prevents duplicate probes after revival)
#   - Anti-rapid-restart: runtime <10s treated as startup failure, wait 30s before retry
#   - Logs: probe writes logs/ch_health_probe.log, this guard writes tmp/ch_health_probe_guard.log
#
# Root-cause fix background (2026-08-03 #ARCH-CH-PROBE-GUARD):
#   ch_health_probe had no guard keepalive; started 8/2 20:51 then exited silently, 13h monitoring gap.
#   This guard joins scheduler/tick_subscriber watchdog tier, auto-revived within 5min after death.
#
# DEPLOY (one-time, no admin): powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1
#   register_guard_tasks.ps1 now registers all three tasks (scheduler + tick_subscriber + ch_health_probe).
#
# IMPORTANT for AI sessions: to (re)start service, use `schtasks /run /tn ZephyrAlpha_CHHealthProbe`
#   (Task Scheduler detaches from IDE terminal job objects). NEVER Start-Process this guard from an
#   IDE terminal for production duty - it dies with the terminal.
#
# Manual start (debug only): powershell -ExecutionPolicy Bypass -File scripts\start_ch_health_probe.ps1

$ErrorActionPreference = "Stop"

# ============== Paths ==============
$RepoRoot = "D:\ZephyrAlpha"
$ProbeScript = Join-Path $RepoRoot "scripts\ops\ch_health_probe.py"
$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    # Fallback: absolute known path, then python on PATH (robust under non-interactive contexts)
    $PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }
}
$TmpDir = Join-Path $RepoRoot "tmp"
$LockFile = Join-Path $TmpDir "ch_health_probe_guard.lock"
$GuardLog = Join-Path $TmpDir "ch_health_probe_guard.log"

if (-not (Test-Path $TmpDir)) {
    New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null
}

# ============== Logging ==============
function Write-GuardLog {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts $Message" | Out-File -FilePath $GuardLog -Append -Encoding utf8
}

# ============== Single-instance lock ==============
if (Test-Path $LockFile) {
    $lockPid = (Get-Content $LockFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if ($lockPid -match '^\d+$' -and (Get-Process -Id ([int]$lockPid) -ErrorAction SilentlyContinue)) {
        Write-GuardLog "Guard already running (PID=$lockPid), exit"
        exit 0
    }
    Write-GuardLog "Cleaning stale lock (old PID=$lockPid no longer alive)"
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}

# Always clean orphan probe (incl. manually started or previous guard residual), ensure guard takeover
# Invariant: no guard => no probe. Avoid guard coexisting with existing probe causing dual-write PID file.
Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains("ch_health_probe.py") } |
    ForEach-Object {
        Write-GuardLog "Killing orphaned ch_health_probe (PID=$($_.ProcessId))"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }

"$PID" | Out-File -FilePath $LockFile -Encoding utf8 -NoNewline

try {
    Write-GuardLog "=== Guard started (guard PID=$PID) ==="

    # Env vars: PYTHONPATH for zephyr import; CH_PROBE_INTERVAL/THRESHOLD control probe frequency
    # interval=3s threshold=2: alert after 6s CH disconnect (matches pre-8/2 manual config)
    $env:PYTHONPATH = "src"
    $env:PYTHONIOENCODING = "utf-8"
    $env:CH_PROBE_INTERVAL = "3"
    $env:CH_PROBE_THRESHOLD = "2"

    $restartCount = 0
    while ($true) {
        $startTime = Get-Date
        Write-GuardLog "Starting ch_health_probe (attempt $($restartCount + 1))..."

        $proc = Start-Process -FilePath $PythonExe `
            -ArgumentList $ProbeScript `
            -WorkingDirectory $RepoRoot `
            -WindowStyle Hidden `
            -PassThru

        $probePid = $proc.Id
        Write-GuardLog "ch_health_probe started (PID=$probePid), waiting for exit..."

        $proc.WaitForExit()
        $exitCode = $proc.ExitCode

        $elapsed = (Get-Date) - $startTime
        $elapsedStr = "{0:d2}h{1:d2}m{2:d2}s" -f [int]$elapsed.TotalHours, $elapsed.Minutes, $elapsed.Seconds
        Write-GuardLog "ch_health_probe exited (exit=$exitCode, uptime=$elapsedStr)"

        # Anti-rapid-restart: runtime <10s means startup failure
        if ($elapsed.TotalSeconds -lt 10) {
            Write-GuardLog "Uptime <10s, likely startup failure (dep not ready / config error), wait 30s before retry"
            Start-Sleep -Seconds 30
        } else {
            Start-Sleep -Seconds 5
        }

        $restartCount++
    }
}
finally {
    Write-GuardLog "=== Guard stopping (guard PID=$PID), killing child probe if alive ==="
    # Invariant: no guard => no probe (prevents duplicate probes when watchdog revives guard)
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains("ch_health_probe.py") } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Write-GuardLog "=== Guard stopped (guard PID=$PID) ==="
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}
