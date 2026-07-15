# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.start_scheduler
# [DOMAIN] D_DATA
# [TTL] permanent
# start_scheduler.ps1 - IntegratorScheduler guard process (auto-restart on crash)
#
# Boot chain (two options, see DEPLOY below):
#   Option A (boot folder, no admin): Startup folder .bat/.lnk -> this script (while-true) -> python -m zephyr.data.scheduler
#   Option B (Task Scheduler, admin): register_scheduler_task.ps1 -> this script (while-true) -> python -m zephyr.data.scheduler
#
# Design:
#   - while($true): auto-restart scheduler on crash, keep 9:15-9:25 auction window online
#   - Single-instance lock: file lock + PID check (rule: only 1 scheduler + 1 guard)
#   - Anti-rapid-restart: runtime <10s treated as startup failure, wait 30s before retry
#   - Logs: scheduler writes tmp/scheduler_run.log, this guard writes tmp/scheduler_guard.log
#
# DEPLOY (Option A - boot folder, no admin required):
#   Create a .bat in Startup folder (Win+R -> shell:startup) with this content:
#     @echo off
#     cd /d D:\ZephyrAlpha
#     powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\ZephyrAlpha\scripts\start_scheduler.ps1"
#   NOTE: .bat is NOT committed to repo (directory_contract.yaml forbids .bat in scripts/).
#
# DEPLOY (Option B - Task Scheduler, admin required):
#   Run as admin: powershell -ExecutionPolicy Bypass -File scripts\register_scheduler_task.ps1
#
# Manual start: powershell -ExecutionPolicy Bypass -File scripts\start_scheduler.ps1

$ErrorActionPreference = "Stop"

# ============== Paths ==============
$RepoRoot = "D:\ZephyrAlpha"
$PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python311\python.exe"
$TmpDir = Join-Path $RepoRoot "tmp"
$LockFile = Join-Path $TmpDir "scheduler.lock"
$GuardLog = Join-Path $TmpDir "scheduler_guard.log"

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
    Write-GuardLog "=== Guard started (guard PID=$PID) ==="

    $env:PYTHONPATH = "src"
    $env:PYTHONIOENCODING = "utf-8"

    $restartCount = 0
    while ($true) {
        $startTime = Get-Date
        Write-GuardLog "Starting scheduler (attempt $($restartCount + 1))..."

        $proc = Start-Process -FilePath $PythonExe `
            -ArgumentList "-m", "zephyr.data.scheduler" `
            -WorkingDirectory $RepoRoot `
            -WindowStyle Hidden `
            -PassThru

        $schedulerPid = $proc.Id
        Write-GuardLog "Scheduler started (PID=$schedulerPid), waiting for exit..."

        $proc.WaitForExit()
        $exitCode = $proc.ExitCode

        $elapsed = (Get-Date) - $startTime
        $elapsedStr = "{0:d2}h{1:d2}m{2:d2}s" -f [int]$elapsed.TotalHours, $elapsed.Minutes, $elapsed.Seconds
        Write-GuardLog "Scheduler exited (exit=$exitCode, uptime=$elapsedStr)"

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
    Write-GuardLog "=== Guard stopped (guard PID=$PID) ==="
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}
