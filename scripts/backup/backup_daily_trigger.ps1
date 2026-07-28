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
    [switch]$TaskStatus
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

    # Settings: 4h time limit, StartWhenAvailable (catch-up if off at 06:00),
    # allow start on battery, don't stop on idle. StartWhenAvailable lives in
    # Settings (NOT Trigger) on Windows Task Scheduler.
    $settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Hours 4) `
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
exit $exitCode
