# [BLUEPRINT] MOD-SCRIPT-register_model_exam | docs/03_modules/_domain_governance/registry_governance/blueprint.md
# [MODULE] scripts.register_model_exam_task
# [DOMAIN] D_GOVERNANCE
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# register_model_exam_task.ps1 - Register the ZephyrAlpha_ModelExam task.
#
# Purpose: OBJ_M M3 model capability exam window (MCE quick/standard for API models,
# dual-run champion/challenger). Joins the mine_vs_exam serial group: Sat 10:00
# FactoryLaneC -> Sat 14:00 C4Exam -> Sat 18:00 ModelExam (last in serial chain).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_model_exam_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_ModelExam /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_ModelExam"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -Command python -m zephyr.intelligence.model_profiling.cli exam --quick"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At "18:00"
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 4) `
    -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Output "OK registered $TaskName (weekly Sat 18:00, 4h limit, mine_vs_exam serial)"
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next Run"
