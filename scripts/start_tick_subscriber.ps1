# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.start_tick_subscriber
# [DOMAIN] D_DATA
# [TTL] permanent
# start_tick_subscriber.ps1 - TickSubscriber guard process (auto-restart on crash)
#
# Boot chain (watchdog architecture, single entry):
#   Task Scheduler "ZephyrAlpha_TickSubscriber" (AtLogOn + repeat every 5min, interactive user)
#     -> this script (while-true, single-instance lock = idempotent re-entry)
#       -> python -m zephyr.data.tick_subscriber
#
# Design:
#   - while($true): auto-restart tick_subscriber on crash, keep real-time tick stream online
#   - Single-instance lock: file lock + PID check (rule: only 1 tick_subscriber + 1 guard);
#     watchdog re-fires every 5min -> if guard alive, exits immediately ("Guard already running")
#   - Orphan cleanup: on stale lock, kill orphaned business python (invariant: no guard => no subscriber)
#   - finally-kill: guard exit kills child subscriber (prevents duplicates after revival)
#   - Anti-rapid-restart: runtime <10s treated as startup failure, wait 30s before retry
#   - Logs: tick_subscriber writes stdout/stderr, this guard writes tmp/tick_subscriber_guard.log
#   - NOTE: requires interactive user session (miniQMT/QMT terminal lives in user session)
#   - Watchdog heartbeat (fix #ARCH-BOOT-001): guard writes heartbeat every 15s; new guard takes
#     over if lock PID alive but heartbeat stale (>5min) -> kills zombie guard + orphan cleanup.
#     Child monitoring polls HasExited instead of blocking WaitForExit to avoid main-thread deadlock.
#
# DEPLOY (one-time, no admin): powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1
#
# IMPORTANT for AI sessions: to (re)start service, use `schtasks /run /tn ZephyrAlpha_TickSubscriber`
#   (Task Scheduler detaches from IDE terminal job objects). NEVER Start-Process this guard from an
#   IDE terminal for production duty - it dies with the terminal.
#
# Manual start (debug only): powershell -ExecutionPolicy Bypass -File scripts\start_tick_subscriber.ps1

$ErrorActionPreference = "Stop"

# ============== Paths ==============
$RepoRoot = "D:\ZephyrAlpha"
$BizModule = "zephyr.data.tick_subscriber"
$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    # Fallback: absolute known path, then python on PATH (robust under non-interactive contexts)
    $PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }
}
$TmpDir = Join-Path $RepoRoot "tmp"
$LockFile = Join-Path $TmpDir "tick_subscriber.lock"
$HeartbeatFile = Join-Path $TmpDir "tick_subscriber.heartbeat"
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

# ============== Watchdog heartbeat (fix #ARCH-BOOT-001) ==============
# guard writes heartbeat every 15s; new guard takeover if lock PID alive but heartbeat stale (>5min).
# heartbeat format: <ISO8601>|<guard_pid>|<child_pid>
function Write-Heartbeat {
    param([int]$ChildPid)
    $ts = (Get-Date).ToString("o")  # ISO 8601, with timezone
    "$ts|$PID|$ChildPid" | Out-File -FilePath $HeartbeatFile -Encoding utf8 -NoNewline
}

# ============== Single-instance lock (with watchdog heartbeat, fix #ARCH-BOOT-001) ==============
if (Test-Path $LockFile) {
    $lockPid = (Get-Content $LockFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if ($lockPid -match '^\d+$' -and (Get-Process -Id ([int]$lockPid) -ErrorAction SilentlyContinue)) {
        # fix: PID alive but heartbeat stale (>5min) => zombie guard, force takeover
        $stale = $true
        if (Test-Path $HeartbeatFile) {
            try {
                $hb = (Get-Content $HeartbeatFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
                $hbTs = ($hb -split '\|')[0]
                if (((Get-Date) - ([datetime]$hbTs)).TotalMinutes -lt 5) { $stale = $false }
            } catch { }
        }
        if ($stale) {
            Write-GuardLog "Guard PID=$lockPid alive but heartbeat stale (>5min), force takeover (kill zombie guard)"
            Stop-Process -Id ([int]$lockPid) -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            Remove-Item $LockFile, $HeartbeatFile -Force -ErrorAction SilentlyContinue
        } else {
            Write-GuardLog "Guard already running (PID=$lockPid, heartbeat fresh), exit"
            exit 0
        }
    } else {
        Write-GuardLog "Cleaning stale lock (old PID=$lockPid no longer alive)"
        Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
    }
    # Invariant: no guard => no business process. Kill orphaned business python from the dead/zombie guard.
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains("-m $BizModule") } |
        ForEach-Object {
            Write-GuardLog "Killing orphaned $BizModule (PID=$($_.ProcessId))"
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
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
            -ArgumentList "-m", $BizModule `
            -WorkingDirectory $RepoRoot `
            -WindowStyle Hidden `
            -PassThru

        $subPid = $proc.Id
        Write-GuardLog "tick_subscriber started (PID=$subPid), polling exit (watchdog heartbeat every 15s)..."
        Write-Heartbeat -ChildPid $proc.Id
        # fix: poll HasExited instead of blocking WaitForExit to avoid main-thread deadlock; heartbeat every 15s
        while (-not $proc.HasExited) {
            Start-Sleep -Seconds 15
            Write-Heartbeat -ChildPid $proc.Id
        }
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
    Write-GuardLog "=== TickSubscriber guard stopping (guard PID=$PID), killing child subscriber if alive ==="
    # Invariant: no guard => no business process (prevents duplicates when watchdog revives guard)
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains("-m $BizModule") } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Write-GuardLog "=== TickSubscriber guard stopped (guard PID=$PID) ==="
    Remove-Item $LockFile, $HeartbeatFile -Force -ErrorAction SilentlyContinue
}
