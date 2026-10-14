# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/boot_autostart_architecture.md
# [MODULE] scripts.start_dashboard_api
# [DOMAIN] D_DATA
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# start_dashboard_api.ps1 - Dashboard API guard process (auto-restart on crash)
#
# Boot chain (watchdog architecture, single entry, mirrors start_ch_health_probe.ps1):
#   Task Scheduler "ZephyrAlpha_DashboardAPI" (AtLogOn + repeat every 5min, interactive user)
#     -> this script (while-true, single-instance lock => idempotent re-entry)
#       -> python -m zephyr.frontend.dashboard.api_server (uvicorn 127.0.0.1:8890)
#
# Why (2026-10-14 Owner ruling): the dashboard API was previously spawned only when the desktop
# shell opens (tools/desktop/main.js ensureApi: shell open = up, shell closed = down); after
# boot/wake without the shell the panel was unusable. This guard upgrades it to a boot-auto-start
# resident service (C1 availability); the shell's ensureApi health-probe reuses a running instance
# (main.js:144-146), no double-spawn.
#
# Design (watchdog four-service template, fix #ARCH-BOOT-001/002):
#   - while($true): auto-restart API on crash
#   - Single-instance lock: file lock + PID check (only 1 guard + 1 api_server)
#   - Orphan cleanup: kill any residual api_server python before starting our own child (prevents
#     8890 bind-failure restart churn; includes shell-spawned instances -- after guard takeover the
#     shell's apiProc is dead but the shell no longer re-spawns, it reuses the guard's instance)
#   - finally-kill: guard exit kills child API (no guard => no business process)
#   - Anti-rapid-restart: runtime <10s treated as startup failure, wait 30s before retry
#   - Child monitoring polls HasExited instead of blocking WaitForExit to avoid main-thread deadlock.
#     fix #ARCH-BOOT-002 F: root cause = PowerShell redirected output pipe buffer fills -> WaitForExit()
#     never returns -> main thread deadlocks. Polling sidesteps; do NOT "optimize" back to WaitForExit.
#   - Logs: uvicorn has no file logging (log_level=warning, stdio previously captured by the shell)
#     -- this guard redirects child stdout/stderr per attempt to
#     data/runtime/api_server_guard_attempt{N}.{out,err}.log (per-attempt so a crash traceback is
#     not overwritten by the next restart); the guard itself writes tmp/dashboard_api_guard.log
#   - Two heartbeat files, do not mix: this guard writes tmp/dashboard_api.heartbeat (guard view,
#     takeover criterion, 15s); the API process telemetry writes tmp/dashboard.heartbeat (60s, read
#     by the deadman switch dashboard channel)
#
# Known benign race (no action needed): the shell's ensureApi only has a 20s window in which a
# zombie-port dialog can fire if its own child gets orphan-killed by this guard; the guard's first
# fire is logon+PT4M, far beyond that window, unreachable in practice.
#
# DEPLOY (one-time, no admin): powershell -ExecutionPolicy Bypass -File scripts\tasks\register\register_guard_tasks.ps1
#
# IMPORTANT for AI sessions: to (re)start service, use `schtasks /run /tn ZephyrAlpha_DashboardAPI`
#   (Task Scheduler detaches from IDE terminal job objects). NEVER Start-Process this guard from an
#   IDE terminal for production duty - it dies with the terminal.
#
# Manual start (debug only): powershell -ExecutionPolicy Bypass -File scripts\start_dashboard_api.ps1

$ErrorActionPreference = "Stop"

# ============== Paths ==============
$RepoRoot = "D:\ZephyrAlpha"
$BizModule = "zephyr.frontend.dashboard.api_server"
$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    # Fallback: absolute known path, then python on PATH (robust under non-interactive contexts)
    $PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }
}
$TmpDir = Join-Path $RepoRoot "tmp"
$RuntimeDir = Join-Path $RepoRoot "data\runtime"
$LockFile = Join-Path $TmpDir "dashboard_api_guard.lock"
$HeartbeatFile = Join-Path $TmpDir "dashboard_api.heartbeat"
$GuardLog = Join-Path $TmpDir "dashboard_api_guard.log"

if (-not (Test-Path $TmpDir)) {
    New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null
}
if (-not (Test-Path $RuntimeDir)) {
    New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null
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
    # atomic write -- Out-File truncates+writes non-atomically; a new guard polling in the 5min
    # window could read a half-written heartbeat -> false stale -> kill healthy guard.
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
    # Invariant: no guard => no business process. Kill orphaned api_server from the dead/zombie guard.
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains($BizModule) } |
        ForEach-Object {
            Write-GuardLog "Killing orphaned $BizModule (PID=$($_.ProcessId))"
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
}

# Always clean orphan api_server (incl. shell-spawned / manually started), ensure guard takeover
# Invariant: no guard => no business process. Avoid dual api_server causing 8890 bind failure.
Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains($BizModule) } |
    ForEach-Object {
        Write-GuardLog "Killing orphaned $BizModule (PID=$($_.ProcessId))"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }

"$PID" | Out-File -FilePath $LockFile -Encoding utf8 -NoNewline

try {
    Write-GuardLog "=== DashboardAPI guard started (guard PID=$PID) ==="

    # Env vars: PYTHONPATH for zephyr import (src layout); utf-8 IO for Windows console-less spawn
    $env:PYTHONPATH = "src"
    $env:PYTHONIOENCODING = "utf-8"

    $restartCount = 0
    while ($true) {
        $startTime = Get-Date
        Write-GuardLog "Starting dashboard api_server (attempt $($restartCount + 1))..."

        # per-attempt log redirect: uvicorn has no file handler (log_level=warning); overwrite only
        # collides within the same attempt number, crash evidence survives until next attempt.
        $outLog = Join-Path $RuntimeDir "api_server_guard_attempt$restartCount.out.log"
        $errLog = Join-Path $RuntimeDir "api_server_guard_attempt$restartCount.err.log"

        $proc = Start-Process -FilePath $PythonExe `
            -ArgumentList @("-m", $BizModule) `
            -WorkingDirectory $RepoRoot `
            -WindowStyle Hidden `
            -RedirectStandardOutput $outLog `
            -RedirectStandardError $errLog `
            -PassThru

        $apiPid = $proc.Id
        Write-GuardLog "api_server started (PID=$apiPid), polling exit (watchdog heartbeat every 15s)..."
        Write-Heartbeat -ChildPid $proc.Id
        # fix: poll HasExited instead of blocking WaitForExit to avoid main-thread deadlock; heartbeat every 15s
        while (-not $proc.HasExited) {
            Start-Sleep -Seconds 15
            Write-Heartbeat -ChildPid $proc.Id
        }
        $exitCode = $proc.ExitCode

        $elapsed = (Get-Date) - $startTime
        $elapsedStr = "{0:d2}h{1:d2}m{2:d2}s" -f [int]$elapsed.TotalHours, $elapsed.Minutes, $elapsed.Seconds
        Write-GuardLog "api_server exited (exit=$exitCode, uptime=$elapsedStr, err=$errLog)"

        # Anti-rapid-restart: runtime <10s means startup failure (port taken / dep error)
        if ($elapsed.TotalSeconds -lt 10) {
            Write-GuardLog "Uptime <10s, likely startup failure (port 8890 taken / dep error), wait 30s before retry"
            Start-Sleep -Seconds 30
        } else {
            Start-Sleep -Seconds 5
        }

        $restartCount++
    }
}
finally {
    Write-GuardLog "=== DashboardAPI guard stopping (guard PID=$PID), killing child api_server if alive ==="
    # Invariant: no guard => no business process (prevents duplicate api_server when watchdog revives guard)
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains($BizModule) } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Write-GuardLog "=== DashboardAPI guard stopped (guard PID=$PID) ==="
    Remove-Item $LockFile, $HeartbeatFile -Force -ErrorAction SilentlyContinue
}
