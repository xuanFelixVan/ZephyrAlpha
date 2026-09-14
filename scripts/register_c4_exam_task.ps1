# [BLUEPRINT] MOD-SCRIPT-register_c4_exam | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.register_c4_exam_task
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-register_c4_exam | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_c4_exam_task.ps1 - Register the ZephyrAlpha_C4Exam Task Scheduler task.
#
# Purpose: weekly E4 exam window - C4 batch screen over ALL translated/ exam files
# (human-translated + machine-generated c4_fact_*.py). Runs AFTER ZephyrAlpha_FactoryLaneC
# (Sat 10:00) so candidates constructed that morning are included.
#
# Idempotency: ledger key = (batch, strategy_id, verdict, source_file) - reruns are safe.
# Order: Sat 10:00 FactoryLaneC (mine/construct) -> Sat 14:00 C4Exam (test all).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_c4_exam_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_C4Exam /v /fo LIST
# Manual kick: powershell -Command "Start-ScheduledTask -TaskName ZephyrAlpha_C4Exam"

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_C4Exam"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File $RepoRoot\scripts\run_c4_exam.ps1"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At "14:00"
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 8) `
    -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Output "OK registered $TaskName (weekly Sat 14:00, 8h limit)"
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next Run"
