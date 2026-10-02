# [BLUEPRINT] MOD-SCRIPT-register_model_intel_scan | docs/03_modules/_domain_governance/registry_governance/blueprint.md
# [MODULE] scripts.register_model_intel_scan_task
# [DOMAIN] D_GOVERNANCE
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# register_model_intel_scan_task.ps1 - Register the ZephyrAlpha_ModelIntelScan task.
#
# Purpose: OBJ_M M1 weekly deep scan window (all 12 intel sources, DESIGN section 2.2).
# Event-triggered shallow scans stay outside this task; this is the weekly calendar slot.
# Light read-only fetch + intel card JSONL output; no in-code timers (constitution 9.3).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_model_intel_scan_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_ModelIntelScan /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_ModelIntelScan"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -Command python -m zephyr.intelligence.model_intel.scanner --source openrouter --out $RepoRoot\.runtime\model_intel\cards"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At "08:00"
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Output "OK registered $TaskName (weekly Sat 08:00, 2h limit)"
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next Run"
