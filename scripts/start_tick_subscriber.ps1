# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.start_tick_subscriber
# [DOMAIN] D_DATA
# [TTL] permanent
# start_tick_subscriber.ps1 - TickSubscriber guard process (auto-restart on crash)
#
# Boot chain (Option A, no admin):
#   Startup folder .bat -> this script (while-true) -> python -m zephyr.data.tick_subscriber
#
# Design:
#   - while($true): auto-restart tick_subscriber on crash, keep real-time tick stream online
#   - Single-instance lock: file lock + PID check (rule: only 1 tick_subscriber + 1 guard)
#   - Anti-rapid-restart: runtime <10s treated as startup failure, wait 30s before retry
#   - Logs: tick_subscriber writes stdout/stderr, this guard writes tmp/tick_subscriber_guard.log
#
# DEPLOY: launched by Startup folder start_zephyr_scheduler.bat (alongside start_scheduler.ps1)
# Manual start: powershell -ExecutionPolicy Bypass -File scripts\start_tick_subscriber.ps1

$ErrorActionPreference = "Stop"

# ============== Paths ==============
$RepoRoot = "D:\ZephyrAlpha"
$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$TmpDir = Join-Path $RepoRoot "tmp"
$LockFile = Join-Path $TmpDir "tick_subscriber.lock"
$GuardLog = Join-Path $TmpDir "tick_subscriber_guard.log"

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

"$PID" | Out-File -FilePath $LockFile -Encoding utf8 -NoNewline

try {
    Write-GuardLog "=== TickSubscriber guard started (guard PID=$PID) ==="

    $env:PYTHONPATH = "src"
    $env:PYTHONIOENCODING = "utf-8"

    $restartCount = 0
    while ($true) {
        $startTime = Get-Date
        Write-GuardLog "Starting tick_subscriber (attempt $($restartCount + 1))..."

        $proc = Start-Process -FilePath $PythonExe `
            -ArgumentList "-m", "zephyr.data.tick_subscriber" `
            -WorkingDirectory $RepoRoot `
            -WindowStyle Hidden `
            -PassThru

        $subPid = $proc.Id
        Write-GuardLog "tick_subscriber started (PID=$subPid), waiting for exit..."

        $proc.WaitForExit()
        $exitCode = $proc.ExitCode

        $elapsed = (Get-Date) - $startTime
        $elapsedStr = "{0:d2}h{1:d2}m{2:d2}s" -f [int]$elapsed.TotalHours, $elapsed.Minutes, $elapsed.Seconds
        Write-GuardLog "tick_subscriber exited (exit=$exitCode, uptime=$elapsedStr)"

        # Anti-rapid-restart: runtime <10s means startup failure (miniQMT not ready / config error)
        if ($elapsed.TotalSeconds -lt 10) {
            Write-GuardLog "Uptime <10s, likely startup failure (miniQMT not ready / dep error), wait 30s before retry"
            Start-Sleep -Seconds 30
        } else {
            Start-Sleep -Seconds 5
        }

        $restartCount++
    }
}
finally {
    Write-GuardLog "=== TickSubscriber guard stopped (guard PID=$PID) ==="
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}
