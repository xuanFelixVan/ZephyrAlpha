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
#   - Watchdog heartbeat (fix #ARCH-BOOT-001): guard writes heartbeat every 15s; new guard takes
#     over if lock PID alive but heartbeat stale (>5min) -> kills zombie guard + orphan cleanup.
#     Child monitoring polls HasExited instead of blocking WaitForExit to avoid main-thread deadlock.
#     fix #ARCH-BOOT-002 F: root cause = PowerShell redirected output pipe buffer fills -> WaitForExit()
#     never returns -> main thread deadlocks. Polling sidesteps; do NOT "optimize" back to WaitForExit.
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
# INT-01 fix (2026-08-23): derive repo root from script location instead of hardcoded
# "D:\ZephyrAlpha" -- survives drive/machine/repo relocation. Same pattern as
# audit_data_utilization.ps1; scripts/ is a direct child, so its parent is the repo root.
$RepoRoot = Split-Path -Parent $PSScriptRoot
$BizModule = "zephyr.data.scheduler"
$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    # Fallback: absolute known path, then python on PATH (robust under non-interactive contexts)
    $PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }
}
$TmpDir = Join-Path $RepoRoot "tmp"
$LockFile = Join-Path $TmpDir "scheduler.lock"
$HeartbeatFile = Join-Path $TmpDir "scheduler.heartbeat"
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

# ============== Single-instance lock (with watchdog heartbeat, fix #ARCH-BOOT-001) ==============
# fix #SCHED-DUAL-INSTANCE (2026-08-25): named mutex serializes the check-then-act critical
# section. Root cause of dual schedulers: the task has TWO 5-min triggers (AtLogOn + Once)
# with MultipleInstances=Parallel, so two guards routinely launch within the same second;
# the old Test-Path->write-lock sequence let both pass before either wrote (guard log
# 2026-08-24 14:42:12-13: THREE guards started in 2s) -> dual python schedulers ->
# duplicate task_runs for every task. The mutex is OS-managed: auto-released on process
# death (abandoned => next waiter acquires), no stale state.
$guardMutex = New-Object System.Threading.Mutex($false, 'Local\ZephyrAlphaSchedulerGuardLock')
$mutexHeld = $false
try {
    try { $mutexHeld = $guardMutex.WaitOne(30000) }
    catch [System.Threading.AbandonedMutexException] { $mutexHeld = $true }
    if (-not $mutexHeld) {
        Write-GuardLog "Guard mutex wait timeout (30s), exit"
        exit 1
    }

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
}
finally {
    if ($mutexHeld) { $guardMutex.ReleaseMutex() }
    $guardMutex.Dispose()
}

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
        Write-GuardLog "Scheduler started (PID=$schedulerPid), polling exit (watchdog heartbeat every 15s)..."
        Write-Heartbeat -ChildPid $proc.Id
        # fix: poll HasExited instead of blocking WaitForExit to avoid main-thread deadlock; heartbeat every 15s
        while (-not $proc.HasExited) {
            Start-Sleep -Seconds 15
            Write-Heartbeat -ChildPid $proc.Id
        }
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
    # fix #SCHED-DUAL-INSTANCE (2026-08-25): delete lock/heartbeat ONLY if owned by THIS guard.
    # Root cause of the self-perpetuating dual state: the old unconditional delete let an
    # exiting co-guard wipe the ACTIVE guard's lock; the active guard never rewrites it, so
    # the next watchdog fire saw "no lock" and launched yet another guard (guard log
    # 2026-08-24 20:56->20:57:44 chain; current live state: lock=17680 but guard 15268 alive).
    $ownedPid = (Get-Content $LockFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($ownedPid -and $ownedPid.Trim() -eq "$PID") {
        Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
    }
    $hbLine = (Get-Content $HeartbeatFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($hbLine -and (($hbLine -split '\|')[1]) -eq "$PID") {
        Remove-Item $HeartbeatFile -Force -ErrorAction SilentlyContinue
    }
}
