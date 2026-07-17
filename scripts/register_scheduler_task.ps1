# [BLUEPRINT] MOD-L00-004 | scripts/register_scheduler_task.ps1
# [MODULE] scripts.register_scheduler_task
# [DOMAIN] D_DATA
# [TTL] permanent
# Register Windows scheduled task to auto-start ZephyrAlpha DataScheduler at boot
# Usage: Run PowerShell as administrator and execute this script

$ErrorActionPreference = "Stop"

$taskName = "ZephyrAlpha_DataScheduler"
$ps1Path = "d:\ZephyrAlpha\scripts\start_scheduler.ps1"

# Create action (use powershell.exe to launch ps1 script; .bat not in scripts/ directory contract allowlist)
$argString = '-NoProfile -ExecutionPolicy Bypass -File "' + $ps1Path + '"'
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argString -WorkingDirectory "d:\ZephyrAlpha"

# Create trigger (auto-start at boot)
$trigger = New-ScheduledTaskTrigger -AtStartup

# Create settings (retry 3 times on failure, 5-minute interval)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -ExecutionTimeLimit (New-TimeSpan -Days 365)

# Create principal (SYSTEM user, highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register task (overwrite if exists)
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Deleted old task: $taskName"
}

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force

Write-Host "Registered scheduled task: $taskName"
Write-Host "Trigger: Auto-start at boot (AtStartup)"
Write-Host "User: SYSTEM (highest privileges)"
Write-Host "Failure retry: 3 times, 5-minute interval"
Write-Host ""
Write-Host "Manual start:  schtasks /run /tn $taskName"
Write-Host "Manual stop:   schtasks /end /tn $taskName"
Write-Host "Query status:  schtasks /query /tn $taskName"
