# [BLUEPRINT] MOD-L00-004 | scripts/register_guard_tasks.ps1
# [MODULE] scripts.register_guard_tasks
# [DOMAIN] D_DATA
# [TTL] permanent
# register_guard_tasks.ps1 - Register Windows Task Scheduler WATCHDOG tasks for ZephyrAlpha data services
#
# Architecture (watchdog terminates the guard-of-guard chain at OS level):
#   Task Scheduler (OS-hosted, survives user-mode kills)
#     -> guard script (while-true, single-instance lock => idempotent re-entry)
#       -> python business process
#
# Each task: AtLogOn trigger + repeat every 5min indefinitely, interactive user (no admin, no password,
# correct $env:LOCALAPPDATA, same session as QMT/miniQMT terminal). Re-firing while guard is alive is a
# no-op ("Guard already running, exit"); if guard was killed, the next fire revives it (<=5min worst case).
#
# Idempotent: safe to re-run; unregisters existing tasks first.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1
# Verify: schtasks /query /tn ZephyrAlpha_DataScheduler & schtasks /query /tn ZephyrAlpha_TickSubscriber

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$services = @(
    @{ TaskName = "ZephyrAlpha_DataScheduler";  Script = "start_scheduler.ps1" },
    @{ TaskName = "ZephyrAlpha_TickSubscriber"; Script = "start_tick_subscriber.ps1" }
)

# Settings: ExecutionTimeLimit=0 (unlimited; default 3 days would kill the guard every 3 days!)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# Principal: current interactive user (QMT/miniQMT lives in this session; python under user LOCALAPPDATA)
$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

foreach ($svc in $services) {
    $ps1Path = Join-Path $RepoRoot ("scripts\" + $svc.Script)
    if (-not (Test-Path $ps1Path)) { throw "Guard script not found: $ps1Path" }

    $argString = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $ps1Path + '"'
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argString -WorkingDirectory $RepoRoot

    # Trigger: AtLogOn; repetition added post-registration (New-ScheduledTaskTrigger
    # doesn't expose Repetition for AtLogOn triggers in PS5.1)
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser

    if (Get-ScheduledTask -TaskName $svc.TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $svc.TaskName -Confirm:$false
        Write-Host "Replaced existing task: $($svc.TaskName)"
    }

    Register-ScheduledTask -TaskName $svc.TaskName -Action $action -Trigger $trigger `
        -Settings $settings -Principal $principal -Force | Out-Null

    # Add watchdog heartbeat: repeat every 5min, no Duration => repeats indefinitely
    $task = Get-ScheduledTask -TaskName $svc.TaskName
    $task.Triggers[0].Repetition.Interval = "PT5M"
    $task | Set-ScheduledTask | Out-Null

    Write-Host "Registered watchdog task: $($svc.TaskName) -> $($svc.Script)"
}

Write-Host ""
Write-Host "Done. Watchdog: AtLogOn + every 5min, user=$CurrentUser, unlimited execution time."
Write-Host "Start now:    schtasks /run /tn ZephyrAlpha_DataScheduler ; schtasks /run /tn ZephyrAlpha_TickSubscriber"
Write-Host "Query status: schtasks /query /tn <TaskName> /v /fo LIST"
Write-Host "Unregister:   Unregister-ScheduledTask -TaskName <TaskName> -Confirm:`$false"
