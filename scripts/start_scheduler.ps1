# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.start_scheduler
# [DOMAIN] D_DATA
# [TTL] permanent
# start_scheduler.ps1 - IntegratorScheduler guard process (auto-restart on crash)
#
# Boot chain (watchdog architecture, single entry):
#   Task Scheduler "ZephyrAlpha_DataScheduler" (AtLogOn + repeat every 5min, interactive user)
#     -> this script (while-true, single-instance lock = idempotent re-entry)
#       -> python -m zephyr.data.scheduler
#
# Design:
#   - while($true): auto-restart scheduler on crash, keep 9:15-9:25 auction window online
#   - Single-instance lock: file lock + PID check (rule: only 1 scheduler + 1 guard);
#     watchdog re-fires every 5min -> if guard alive, exits immediately ("Guard already running")
#   - Orphan cleanup: on stale lock, kill orphaned business python (invariant: no guard => no scheduler)
#   - finally-kill: guard exit kills child scheduler (prevents duplicate schedulers after revival)
#   - Anti-rapid-restart: runtime <10s treated as startup failure, wait 30s before retry
#   - Logs: scheduler writes tmp/scheduler_run.log, this guard writes tmp/scheduler_guard.log
#
# DEPLOY (one-time, no admin): powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1
#   Registers BOTH watchdog tasks (scheduler + tick_subscriber).
#   Task Scheduler watchdog is the SOLE entry (legacy Startup .lnk/.bat removed 2026-07-27:
#   redundant with this watchdog + flashed console windows). Single-instance lock = defense-in-depth.
#   See docs/03_modules/_domain_data/boot_autostart_architecture.md.
#
# IMPORTANT for AI sessions: to (re)start service, use `schtasks /run /tn ZephyrAlpha_DataScheduler`
#   (Task Scheduler detaches from IDE terminal job objects). NEVER Start-Process this guard from an
#   IDE terminal for production duty - it dies with the terminal.
#
# Manual start (debug only): powershell -ExecutionPolicy Bypass -File scripts\start_scheduler.ps1

$ErrorActionPreference = "Stop"

# ============== Paths ==============
$RepoRoot = "D:\ZephyrAlpha"
$BizModule = "zephyr.data.scheduler"
$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    # Fallback: absolute known path, then python on PATH (robust under non-interactive contexts)
    $PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }
}
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
    # Invariant: no guard => no business process. Kill orphaned business python from the dead guard.
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains("-m $BizModule") } |
        ForEach-Object {
            Write-GuardLog "Killing orphaned $BizModule (PID=$($_.ProcessId))"
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
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
            -ArgumentList "-m", $BizModule `
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
    Write-GuardLog "=== Guard stopping (guard PID=$PID), killing child scheduler if alive ==="
    # Invariant: no guard => no business process (prevents duplicate schedulers when watchdog revives guard)
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains("-m $BizModule") } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Write-GuardLog "=== Guard stopped (guard PID=$PID) ==="
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}
