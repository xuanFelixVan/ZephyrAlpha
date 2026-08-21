# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] scripts.start_trading
# [DOMAIN] D_INFRA_RUNTIME
# [TTL] permanent
# start_trading.ps1 - AutoRuntime Core (trading main process) guard (auto-restart on crash)
#
# Work order: INT-03 (92_phase2_business_construction_order.md section 5.4, D3 ruling).
#
# Boot chain (watchdog architecture, single entry):
#   Task Scheduler "ZephyrAlpha_TradingWatchdog" (registered DISABLED per D3; enable = Owner window)
#     -> this script (while-true, single-instance lock = idempotent re-entry)
#       -> python -m zephyr.trading
#
# D3 ruling (why DISABLED): verified 2026-08-22 - NO resident trading production process is
#   running today (57_daily_cycle_sop.md section 2 / GAP-2: intraday paper session is pulled
#   up manually by an AI session before 09:25 via scripts/start_paper_session.py, transitional
#   form; register_aux_tasks.ps1 registers only RSSHub/TraeCacheCleanup). An enabled watchdog
#   would auto-start a process that is not running today = production behavior change.
#   Disabled preserves one-click recovery:
#     Enable-ScheduledTask ZephyrAlpha_TradingWatchdog   (Owner window)
#     schtasks /run /tn ZephyrAlpha_TradingWatchdog
#
# Design (isomorphic to start_scheduler.ps1, the data-domain guard SSoT):
#   - while($true): auto-restart trading main process on crash
#   - Single-instance lock: file lock + PID check (rule: only 1 trading + 1 guard);
#     watchdog re-fires every 5min -> if guard alive, exits immediately ("Guard already running")
#   - Orphan cleanup: on stale lock, kill orphaned business python (invariant: no guard => no trading)
#   - finally-kill: guard exit kills child trading (prevents duplicate trading after revival)
#   - Anti-rapid-restart: runtime <10s treated as startup failure, wait 30s before retry
#   - Logs: this guard writes tmp/trading_guard.log
#   - Watchdog heartbeat (fix #ARCH-BOOT-001): guard writes heartbeat every 15s; new guard takes
#     over if lock PID alive but heartbeat stale (>5min) -> kills zombie guard + orphan cleanup.
#     Child monitoring polls HasExited instead of blocking WaitForExit to avoid main-thread deadlock.
#     fix #ARCH-BOOT-002 F: root cause = PowerShell redirected output pipe buffer fills -> WaitForExit()
#     never returns -> main thread deadlocks. Polling sidesteps; do NOT "optimize" back to WaitForExit.
#   - Heartbeat file tmp/trading.heartbeat uses the deadman_switch.ps1-compatible format
#     (<ISO8601>|<guard_pid>|<child_pid>) but is intentionally NOT in the deadman_switch
#     monitored list (3 channels): while this task stays Disabled the missing heartbeat file
#     would false-alert as MISSING. Add it as the 4th channel in the same Owner window that
#     enables the task.
#
# DEPLOY (Owner/coordinator window, no admin):
#   powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1
#   Registers the task in DISABLED state (idempotent create-if-absent; an existing task is
#   left completely untouched).
#
# IMPORTANT for AI sessions: to (re)start service after enabling, use
#   `schtasks /run /tn ZephyrAlpha_TradingWatchdog` (Task Scheduler detaches from IDE terminal
#   job objects). NEVER Start-Process this guard from an IDE terminal for production duty -
#   it dies with the terminal.
#
# Manual start (debug only): powershell -ExecutionPolicy Bypass -File scripts\start_trading.ps1

$ErrorActionPreference = "Stop"

# ============== Paths ==============
$RepoRoot = "D:\ZephyrAlpha"
$BizModule = "zephyr.trading"
$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    # Fallback: absolute known path, then python on PATH (robust under non-interactive contexts)
    $PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }
}
$TmpDir = Join-Path $RepoRoot "tmp"
$LockFile = Join-Path $TmpDir "trading.lock"
$HeartbeatFile = Join-Path $TmpDir "trading.heartbeat"
$GuardLog = Join-Path $TmpDir "trading_guard.log"

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
# heartbeat format: <ISO8601>|<guard_pid>|<child_pid>  (deadman_switch.ps1 compatible)
function Write-Heartbeat {
    param([int]$ChildPid)
    $ts = (Get-Date).ToString("o")  # ISO 8601, with timezone
    # fix #ARCH-BOOT-002 D: atomic write -- Out-File truncates+writes non-atomically;
    # a new guard polling in the 5min window could read a half-written heartbeat
    # -> false stale -> kill healthy guard. Write tmp + Move-Item (same-volume atomic).
    "$ts|$PID|$ChildPid" | Out-File -FilePath "$HeartbeatFile.tmp" -Encoding utf8 -NoNewline
    Move-Item -Path "$HeartbeatFile.tmp" -Destination $HeartbeatFile -Force
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
    Write-GuardLog "=== Guard started (guard PID=$PID) ==="

    $env:PYTHONPATH = "src"
    $env:PYTHONIOENCODING = "utf-8"

    $restartCount = 0
    while ($true) {
        $startTime = Get-Date
        Write-GuardLog "Starting trading main process (attempt $($restartCount + 1))..."

        $proc = Start-Process -FilePath $PythonExe `
            -ArgumentList "-m", $BizModule `
            -WorkingDirectory $RepoRoot `
            -WindowStyle Hidden `
            -PassThru

        $tradingPid = $proc.Id
        Write-GuardLog "Trading main process started (PID=$tradingPid), polling exit (watchdog heartbeat every 15s)..."
        Write-Heartbeat -ChildPid $proc.Id
        # fix: poll HasExited instead of blocking WaitForExit to avoid main-thread deadlock; heartbeat every 15s
        while (-not $proc.HasExited) {
            Start-Sleep -Seconds 15
            Write-Heartbeat -ChildPid $proc.Id
        }
        $exitCode = $proc.ExitCode

        $elapsed = (Get-Date) - $startTime
        $elapsedStr = "{0:d2}h{1:d2}m{2:d2}s" -f [int]$elapsed.TotalHours, $elapsed.Minutes, $elapsed.Seconds
        Write-GuardLog "Trading main process exited (exit=$exitCode, uptime=$elapsedStr)"

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
    Write-GuardLog "=== Guard stopping (guard PID=$PID), killing child trading if alive ==="
    # Invariant: no guard => no business process (prevents duplicate trading when watchdog revives guard)
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains("-m $BizModule") } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Write-GuardLog "=== Guard stopped (guard PID=$PID) ==="
    Remove-Item $LockFile, $HeartbeatFile -Force -ErrorAction SilentlyContinue
}
