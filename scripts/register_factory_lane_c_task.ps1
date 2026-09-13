# [BLUEPRINT] MOD-SCRIPT-register_factory_lane_c | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.register_factory_lane_c_task
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-register_factory_lane_c_task | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_factory_lane_c_task.ps1 - Register the ZephyrAlpha_FactoryLaneC Task Scheduler task.
#
# Purpose: weekly production window for FAC-E1C formula mining (gplearn track, Owner approved
# 2026-09-14: dual-track / REG-IND-001 baseline / pop 1000 x 50 / whitelist governance).
#
# Architecture (mirrors register_pattern_mining_task.ps1 / register_paper_session_task.ps1):
#   Task Scheduler ZephyrAlpha_FactoryLaneC (weekly Sat 10:00)
#   -> powershell -File scripts\run_factory_lane_c.ps1
#   -> lane_c_formula_miner.py mine (E0 gate + whitelist status checked inside, every run)
#
# Key design:
# - Saturday 10:00 = non-trading day window (E0 gate allows heavy all day on holidays);
#   manual fire any trading day after 15:30 works too: schtasks /run /tn ZephyrAlpha_FactoryLaneC
# - The E0 compute gate re-checks trade_calendar at every fire, so the trigger schedule is
#   convenience only and never bypasses discipline.
# - ExecutionTimeLimit=4h: production run est. 30-90min CPU single-thread.
# - Idempotent non-destructive: Set-ScheduledTask in-place update (NEVER Unregister+Register).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_factory_lane_c_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_FactoryLaneC /v /fo LIST
# Manual kick: schtasks /run /tn ZephyrAlpha_FactoryLaneC

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_FactoryLaneC"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File $RepoRoot\scripts\run_factory_lane_c.ps1"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At "10:00"
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 4) `
    -MultipleInstances IgnoreNew -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Output "OK registered $TaskName (weekly Sat 10:00, 4h limit)"
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next Run"
