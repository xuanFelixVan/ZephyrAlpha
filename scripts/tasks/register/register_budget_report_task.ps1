# [BLUEPRINT] MOD-SCRIPT-register_budget_report | docs/03_modules/_domain_governance/registry_governance/blueprint.md
# [MODULE] scripts.register_budget_report_task
# [DOMAIN] D_GOVERNANCE
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# register_budget_report_task.ps1 - Register the ZephyrAlpha_BudgetReport task.
#
# Purpose: OBJ_M M5 budget analyzer daily report (usage_records read-only aggregation,
# four-tier alert advisory, recharge suggestion text only - payment action NEVER automated).
# Runs 07:30 daily (before pre_open window 08:00).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_budget_report_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_BudgetReport /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_BudgetReport"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -Command python -m zephyr.intelligence.budget_analyzer --report"
$Trigger = New-ScheduledTaskTrigger -Daily -At "07:30"
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Output "OK registered $TaskName (daily 07:30, 1h limit)"
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next Run"
