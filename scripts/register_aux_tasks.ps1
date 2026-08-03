# [BLUEPRINT] MOD-L00-004 | scripts.register_aux_tasks
# [MODULE] scripts.register_aux_tasks
# [DOMAIN] D_DATA
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_aux_tasks.ps1 - Register Windows Task Scheduler tasks for RSSHub + Trae cache cleanup
#
# Replaces legacy Startup folder .bat entries (which flash console windows on login) with silent
# Task Scheduler tasks. Idempotent: Set-ScheduledTask updates in place (NEVER Unregister, which
# would terminate a running instance - same discipline as register_guard_tasks.ps1).
#
# Tasks:
#   ZephyrAlpha_RSSHub           - AtLogOn, hidden `pm2 resurrect` (restores RSSHub process tree)
#   ZephyrAlpha_TraeCacheCleanup - AtLogOn + 30s delay, hidden clean_trae_cache.ps1
#
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\register_aux_tasks.ps1
# Verify: schtasks /query /tn ZephyrAlpha_RSSHub /v /fo LIST
#         schtasks /query /tn ZephyrAlpha_TraeCacheCleanup /v /fo LIST
#
# See docs/03_modules/_domain_data/boot_autostart_architecture.md for full architecture.

$ErrorActionPreference = "Stop"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# Settings: ExecutionTimeLimit=0 (pm2 resurrect / cache cleanup may run long on first boot)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

function Register-AuxTask {
    param(
        [string]$Name,
        [string]$Argument,
        [string]$WorkDir,
        [string]$Delay
    )
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $Argument -WorkingDirectory $WorkDir
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser

    if (Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue) {
        # Non-destructive update: preserves any running instance (Unregister would kill it)
        Set-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger `
            -Settings $settings -Principal $principal | Out-Null
        Write-Host "Updated existing task in place: $Name"
    } else {
        Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger `
            -Settings $settings -Principal $principal -Force | Out-Null
        Write-Host "Registered task: $Name"
    }

    # Apply startup delay post-creation (PS5.1 New-ScheduledTaskTrigger has no -Delay param)
    if ($Delay) {
        $task = Get-ScheduledTask -TaskName $Name
        $task.Triggers[0].Delay = $Delay
        $task | Set-ScheduledTask | Out-Null
        Write-Host "  (startup delay: $Delay)"
    }
}

# Task 1: RSSHub - pm2 resurrect restores the previously saved process tree (dump.pm2)
Register-AuxTask -Name "ZephyrAlpha_RSSHub" `
    -Argument '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "cd D:\RSSHub; pm2 resurrect"' `
    -WorkDir "D:\RSSHub" -Delay $null

# Task 2: Trae cache cleanup - 30s delay to avoid boot contention (matches old bat `timeout /t 30`)
Register-AuxTask -Name "ZephyrAlpha_TraeCacheCleanup" `
    -Argument '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\Users\fanzi\scripts\clean_trae_cache.ps1"' `
    -WorkDir "C:\Users\fanzi" -Delay "PT30S"

Write-Host ""
Write-Host "Done. AtLogOn, user=$CurrentUser, hidden, unlimited execution time."
Write-Host "Start now:  schtasks /run /tn ZephyrAlpha_RSSHub ; schtasks /run /tn ZephyrAlpha_TraeCacheCleanup"
Write-Host "Unregister: Unregister-ScheduledTask -TaskName <Name> -Confirm:`$false"
