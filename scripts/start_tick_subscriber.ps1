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
#     fix #ARCH-BOOT-002 F: root cause = PowerShell redirected output pipe buffer fills -> WaitForExit()
#     never returns -> main thread deadlocks. Polling sidesteps; do NOT "optimize" back to WaitForExit.
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
$BizHeartbeatFile = Join-Path $TmpDir "tick_subscriber_biz.heartbeat"  # biz heartbeat (#ARCH-DATA-017 ruling C, JSON written by subscriber itself)
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
    # fix #ARCH-BOOT-002 D: atomic write -- Out-File truncates+writes non-atomically;
    # a new guard polling in the 5min window could read a half-written heartbeat
    # -> false stale -> kill healthy guard. Write tmp + Move-Item (same-volume atomic).
    "$ts|$PID|$ChildPid" | Out-File -FilePath "$HeartbeatFile.tmp" -Encoding utf8 -NoNewline
    Move-Item -Path "$HeartbeatFile.tmp" -Destination $HeartbeatFile -Force
}

# ============== Business heartbeat staleness (#ARCH-DATA-017 ruling C, 2026-08-15) ==============
# Root-cause fix for amplifier-1 "live process, zero collection" (4 silent days 08-12~14):
# guard-written heartbeat only proves the PROCESS is alive, decoupled from COLLECTION health.
# Biz heartbeat JSON (last_tick_ts/today_rows/is_trading_day) is written by the subscriber
# itself; here we detect "no tick during market hours" and restart the child.
# Triggers only when: weekday + market hours (09:30-15:00) + is_trading_day + last_tick
# stale > $BizStaleMin minutes. last_tick_ts null (never received): anchor =
# max(started_ts, today 09:30) (preopen-start grace). Missing/corrupt file -> no kill
# (deadman_switch reports MISSING/parse error instead).
$BizStaleMin = 10
if ($env:TICK_BIZ_STALE_MIN -match '^\d+$') { $BizStaleMin = [int]$env:TICK_BIZ_STALE_MIN }
function Test-BizHeartbeatStale {
    param([string]$Path)
    $now = Get-Date
    if ($now.DayOfWeek -eq 'Saturday' -or $now.DayOfWeek -eq 'Sunday') { return $false }
    $hm = $now.Hour * 60 + $now.Minute
    if ($hm -lt 9 * 60 + 30 -or $hm -gt 15 * 60) { return $false }
    if (-not (Test-Path $Path)) { return $false }
    try {
        $biz = Get-Content $Path -Raw -Encoding utf8 | ConvertFrom-Json
        if ($null -ne $biz.is_trading_day -and -not [bool]$biz.is_trading_day) { return $false }  # holiday: no kill
        $anchor = $null
        if ($biz.last_tick_ts) {
            $anchor = [datetime]$biz.last_tick_ts
        } else {
            $open = Get-Date -Hour 9 -Minute 30 -Second 0
            $anchor = $open
            if ($biz.started_ts -and ([datetime]$biz.started_ts) -gt $open) { $anchor = [datetime]$biz.started_ts }
        }
        return (($now - $anchor).TotalMinutes -gt $BizStaleMin)
    } catch {
        return $false
    }
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
            # Biz-heartbeat stale restart (#ARCH-DATA-017 ruling C): weekday market hours
            # + is_trading_day + last_tick stale > $BizStaleMin min = live-process-zero-collection.
            # Kill child -> outer while loop restarts it (self-heal before deadman alert).
            # Off-hours/weekend/holiday: Test-BizHeartbeatStale returns false, never kills.
            if (Test-BizHeartbeatStale -Path $BizHeartbeatFile) {
                Write-GuardLog "BIZ-STALE: no tick > ${BizStaleMin}min in market hours (live-process-zero-collection #ARCH-DATA-017), restarting tick_subscriber (PID=$subPid)"
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
            }
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
