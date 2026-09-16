# [BLUEPRINT] MOD-SCRIPT-register_f06_grid_task | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.register_f06_grid_task
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-register_f06_grid_task | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_f06_grid_task.ps1 - Register ZephyrAlpha_F06Grid Task Scheduler task.
#
# Architecture (mirrors register_factory_lane_c_task.ps1):
#   Task Scheduler ZephyrAlpha_F06Grid (weekly Sat 14:00 - after LaneC 10:00, non-trading day)
#   -> powershell -File scripts\run_f06_grid.ps1
#   -> factory_grid_executor.py (E0 discipline inside data availability checks;
#      N ledger MOD-BT-200 auto-registration at summary)
#
# - ExecutionTimeLimit=24h: batch A ~11h + batch B ~11h sequential worst case.
# - Idempotent non-destructive: Set-ScheduledTask in-place update (NEVER Unregister+Register).

$ErrorActionPreference = "Stop"
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File D:\ZephyrAlpha\scripts\run_f06_grid.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At 14:00
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 24) `
    -StartWhenAvailable -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName "ZephyrAlpha_F06Grid" `
    -Action $action -Trigger $trigger -Settings $settings -Principal $principal `
    -Description "F-06 grid factory weekly window: batch A census-extend + batch B subspace enumerate (MOD-BT-196, N ledger auto-registration)" `
    -Force | Out-Null
Write-Output "Registered ZephyrAlpha_F06Grid (weekly Sat 14:00, ExecutionTimeLimit=24h)"
Get-ScheduledTask -TaskName "ZephyrAlpha_F06Grid" | Format-List TaskName, State
