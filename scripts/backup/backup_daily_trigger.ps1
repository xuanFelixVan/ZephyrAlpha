<#
.SYNOPSIS
    Daily disaster backup trigger + Windows Scheduled Task registration.
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | Section 4.1
    Two modes:
      (default)           - Run the daily backup (calls backup.ps1 -Mode all -Force)
      -RegisterTask       - Register Windows Scheduled Task "ZephyrAlpha-DailyBackup"
                            (daily 06:00, StartWhenAvailable for catch-up)
      -UnregisterTask     - Remove the scheduled task
      -TaskStatus         - Show scheduled task status

    Scheduled task config:
      - Time:         06:00 daily
      - Run level:    Highest (current user)
      - StartWhenAvailable: $true (catch-up if machine was off at 06:00)
      - ExecutionTimeLimit: PT4H (backup.ps1 has 4h internal timeout)

    Lock file (.runtime/backup.lock) in backup.ps1 prevents concurrent runs
    with post-commit reconciler (backup_reconciler.py).

    WHY a daily task (in addition to post-commit reconciler):
      post-commit only fires on commits. A day with no commits = no backup.
      The daily task is the GUARANTEED floor (1 backup/day minimum).
.PARAMETER RegisterTask
    Register the Windows Scheduled Task (does NOT run backup immediately).
.PARAMETER UnregisterTask
    Remove the Windows Scheduled Task.
.PARAMETER TaskStatus
    Print scheduled task status and last run result.
.EXAMPLE
    .\backup_daily_trigger.ps1 -RegisterTask
    .\backup_daily_trigger.ps1 -TaskStatus
    .\backup_daily_trigger.ps1   # runs the backup (called by the task at 06:00)
#>
param(
    [switch]$RegisterTask,
    [switch]$UnregisterTask,
    [switch]$TaskStatus,
    [switch]$SloCheckOnly,
    [string]$SloStateFile,
    [string]$SloAlertDir
)

$ErrorActionPreference = "Continue"
$ProjectRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha-DailyBackup"
$BackupScript = "$ProjectRoot\scripts\backup\backup.ps1"
$LogFile = "$ProjectRoot\logs\daily_trigger_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Stage($msg) { Write-Host "[DAILY] $msg" -ForegroundColor Cyan }
function Write-OK($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERR] $msg" -ForegroundColor Red }

# ==================== Backup SLO sentinel (#ARCH-BACKUP-SLO-001, 2026-08-13) ====================
# Root cause: CH backup failed 2 days silently (failure only written to log file, no alert channel).
# (E-1, 2026-10-09) Dual-check hardening:
#   - Was: only last_ch_backup_status read -> a failed MAIN backup
#     (last_backup_status, written by backup.ps1 STAGE 4) never alerted, while a
#     LEGAL 24h-cadence CH skip (status="skipped") false-alarmed.
#   - Now: main status + CH status both checked; only failure-grade values alert.
#     CH "skipped" is not failure-grade (last_ch_backup_time only advances on a
#     real ok, so the 36h staleness probe still catches a CH leg gone dark).
# State file / alert dir are parameters so -SloCheckOnly can dry-run against a copy.
function Invoke-BackupSloCheck {
    param(
        [string]$StateFile = "$ProjectRoot\data\databases\backup_state.json",
        [string]$AlertDir  = "$ProjectRoot\logs\alerts"
    )
    $sloMaxHours = 36   # backup SLO: must succeed within 36h (daily 06:00 + tolerance)
    $mainReason = $null
    $chReason = $null
    $chElapsedRound = "n/a"

    if (-not (Test-Path $StateFile)) {
        $mainReason = "backup_state.json missing (backup never ran?)"
    } else {
        try {
            $st = Get-Content $StateFile -Raw | ConvertFrom-Json
            # -- main backup leg (last_backup_status: ok|failed, backup.ps1 STAGE 4) --
            $mainStatus = [string]$st.last_backup_status
            $mainTime = $st.last_backup_time
            if (-not $mainStatus) {
                $mainReason = "last_backup_status missing from state (backup.ps1 too old?)"
            } elseif ($mainStatus -ne "ok") {
                $mainReason = "last_backup_status=${mainStatus}"
            } elseif ($mainTime) {
                $mElapsedH = ((Get-Date) - [datetime]::Parse($mainTime)).TotalHours
                if ($mElapsedH -gt $sloMaxHours) {
                    $mainReason = "main backup stale: last ok attempt {0}h ago (> {1}h SLO)" -f [math]::Round($mElapsedH, 1), $sloMaxHours
                }
            }
            # -- CH leg ("skipped" = legal 24h cadence outcome, NOT failure-grade) --
            $chStatus = [string]$st.last_ch_backup_status
            $chTime = $st.last_ch_backup_time
            $chElapsedH = if ($chTime) { ((Get-Date) - [datetime]::Parse($chTime)).TotalHours } else { [double]::PositiveInfinity }
            $chElapsedRound = [string]([math]::Round($chElapsedH, 1))
            $chFailureGrade = @("failed", "ch_failed", "ch_log_missing")
            if ($chFailureGrade -contains $chStatus) {
                $chErr = [string]$st.last_ch_backup_error
                $chReason = "last_ch_backup_status=${chStatus} (error: ${chErr})"
            } elseif ($chElapsedH -gt $sloMaxHours) {
                $chReason = "CH backup stale: last ok {0}h ago (> {1}h SLO)" -f $chElapsedRound, $sloMaxHours
            }
            if (-not $mainReason -and -not $chReason) {
                Write-OK "SLO check passed: last_backup_status=${mainStatus}, last_ch_backup_status=${chStatus}, CH last ok ${chElapsedRound}h ago"
            }
        } catch {
            $mainReason = "SLO check parse error: $($_.Exception.Message)"
        }
    }

    if (-not $mainReason -and -not $chReason) { return }

    # Write alert files (disk = alert channel; dashboard/AI can scan logs/alerts/)
    # CH alert keeps the legacy backup_slo_<date>.json filename (back-compat).
    New-Item -ItemType Directory -Path $AlertDir -Force | Out-Null
    $today = Get-Date -Format 'yyyyMMdd'
    $pending = @()
    if ($mainReason) { $pending += @{ alert_id = "backup_main_slo"; reason = $mainReason; name = "backup_main_slo_${today}.json" } }
    if ($chReason)   { $pending += @{ alert_id = "backup_ch_slo";   reason = $chReason;   name = "backup_slo_${today}.json" } }
    foreach ($p in $pending) {
        $alertFile = Join-Path $AlertDir $p.name
        $alert = @{
            alert_id   = $p.alert_id
            level      = "ERROR"
            source     = "backup_daily_trigger"
            timestamp  = (Get-Date).ToString("o")
            reason     = $p.reason
            slo_hours  = $sloMaxHours
        }
        [System.IO.File]::WriteAllText($alertFile, ($alert | ConvertTo-Json -Depth 3), (New-Object System.Text.UTF8Encoding($false)))
        Write-Err "SLO ALERT [$($p.alert_id)]: $($p.reason) -> $alertFile"
    }
}

# (E-1) Testable dry-run: evaluate the sentinel against (a copy of) the state
# file WITHOUT running a backup. Also invoked by backup.ps1 end-of-run so the
# sentinel is live on the scheduled-task carrier too (E-1 finding: the 06:00
# task runs backup.ps1 via wscript launch_hidden.vbs and never reaches this
# file's default branch).
if ($SloCheckOnly) {
    $sloArgs = @{}
    if ($SloStateFile) { $sloArgs.StateFile = $SloStateFile }
    if ($SloAlertDir)  { $sloArgs.AlertDir  = $SloAlertDir }
    Invoke-BackupSloCheck @sloArgs
    exit 0
}

# ==================== -TaskStatus ====================
if ($TaskStatus) {
    Write-Stage "Scheduled task status: $TaskName"
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $task) { Write-Warn "Task '$TaskName' not registered. Run: -RegisterTask"; exit 0 }
    $info = $task | Get-ScheduledTaskInfo
    Write-Host "  State:             $($task.State)"
    Write-Host "  LastRunTime:       $($info.LastRunTime)"
    Write-Host "  LastTaskResult:    0x$('{0:X8}' -f $info.LastTaskResult) ($($info.LastTaskResult))"
    Write-Host "  NextRunTime:       $($info.NextRunTime)"
    Write-Host "  NumberOfMissedRuns: $($info.NumberOfMissedRuns)"
    $trig = $task.Triggers[0]
    if ($trig) {
        Write-Host "  Trigger type:      $($trig.CimClass.CimClassName)"
        Write-Host "  StartBoundary:     $($trig.StartBoundary)"
        Write-Host "  StartWhenAvailable: $($trig.StartWhenAvailable)"
    }
    exit 0
}

# ==================== -UnregisterTask ====================
if ($UnregisterTask) {
    Write-Stage "Unregistering task: $TaskName"
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-OK "Task '$TaskName' removed"
    } else {
        Write-Warn "Task '$TaskName' not found (nothing to remove)"
    }
    exit 0
}

# ==================== -RegisterTask ====================
if ($RegisterTask) {
    Write-Stage "Registering scheduled task: $TaskName"

    if (-not (Test-Path $BackupScript)) { Write-Err "backup.ps1 not found: $BackupScript"; exit 1 }

    # Action: run backup.ps1 -Mode all -Force
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$BackupScript`" -Mode all -Force" `
        -WorkingDirectory $ProjectRoot

    # Trigger: daily at 06:00
    $trigger = New-ScheduledTaskTrigger -Daily -At 6:00am

    # Settings: 12h time limit, StartWhenAvailable (catch-up if off at 06:00),
    # allow start on battery, don't stop on idle. StartWhenAvailable lives in
    # Settings (NOT Trigger) on Windows Task Scheduler.
    # Time limit raised 4h -> 12h (2026-10-12 chief order 8 item 3). Why: the task
    # action chain is wscript.exe -> launch_hidden.vbs -> backup.ps1, and the vbs
    # waits for the child (sh.Run cmd, 0, True), so the whole backup tree runs INSIDE
    # this limit. A dated-snapshot rotation delete measured 6h42m44s on 2026-10-12
    # (total run 27844.9s = 7h44m), i.e. longer than the old 4h ceiling. All runs that
    # survived did so because they were ignited by the reconciler, outside the task.
    # Under the old limit a long 06:00 run gets hard-terminated mid-flight (default
    # AllowHardTerminate=true), which leaves .runtime/backup.lock held by a dead PID
    # and a truncated backup -- the exact silent-outage shape this chain is built to
    # avoid. 12h = 3x the worst measured run, still a backstop, not unlimited.
    $settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Hours 12) `
        -StartWhenAvailable `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -DontStopOnIdleEnd `
        -RestartCount 1 `
        -RestartInterval (New-TimeSpan -Minutes 30)

    # Principal: current user. Daily backup.ps1 (robocopy/pg_dump/curl/SSH) does
    # NOT need elevation -- only backup_ch_vm.ps1 (Hyper-V Stop/Start-VM) does.
    # RunLevel Limited avoids the admin requirement to register the task.
    $principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -LogonType Interactive

    # Register (overwrite if exists)
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null
        Write-OK "Task '$TaskName' updated"
    } else {
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "ZephyrAlpha daily disaster backup (06:00, robocopy + CH incremental)" | Out-Null
        Write-OK "Task '$TaskName' registered"
    }

    # Verify
    $task = Get-ScheduledTask -TaskName $TaskName
    $info = $task | Get-ScheduledTaskInfo
    Write-Host "  State:         $($task.State)" -ForegroundColor White
    Write-Host "  NextRunTime:   $($info.NextRunTime)" -ForegroundColor White
    Write-Host "  Trigger:       Daily 06:00 (StartWhenAvailable=$($trigger.StartWhenAvailable))" -ForegroundColor White
    exit 0
}

# ==================== Default: run the backup ====================
# This branch is invoked by the scheduled task at 06:00.
Write-Stage "Daily backup trigger starting at $(Get-Date -Format 'o')"

if (-not (Test-Path $BackupScript)) { Write-Err "backup.ps1 not found: $BackupScript"; exit 1 }

New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null

# Invoke backup.ps1 with -Force (skip 24h CH cadence gate -- daily task is authoritative)
# Mode=all runs PG dump + SQLite + CH incremental + code robocopy + config sync.
# Lock file (.runtime/backup.lock) prevents overlap with a concurrent post-commit run.
$exitCode = 0
try {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $BackupScript -Mode all -Force 2>&1 |
        Tee-Object -FilePath $LogFile
    $exitCode = $LASTEXITCODE
} catch {
    Write-Err "Daily trigger exception: $($_.Exception.Message)"
    $exitCode = 1
}

Write-Stage "Daily trigger finished at $(Get-Date -Format 'o'), backup.ps1 exit=$exitCode, log=$LogFile"

# SLO sentinel: independently check CH backup health regardless of backup.ps1 exit code
Invoke-BackupSloCheck

exit $exitCode
