# [BLUEPRINT] MOD-SCRIPT-register_commit_perf_report | scripts/governance/commit_perf_report.py
# [MODULE] scripts.register_commit_perf_report_task
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# register_commit_perf_report_task.ps1 - Register the ZephyrAlpha_CommitPerfReport task.
#
# Purpose: mount the in-service commit performance / concurrency health report
# (scripts/governance/commit_perf_report.py, 11-family death-cause spectrum) into the
# Windows Task Scheduler daily roster. Registered by st-tclose-gateops-20261004
# (2026-10-04): the script had zero consumers (no tasks.yaml entry, no schedule,
# no scheduled task) despite being production-in-service.
#
# Schedule: daily 07:00 (before the 07:30 BudgetReport slot; StartWhenAvailable so a
# powered-off morning catches up on wake). Output appends to
# .runtime/logs/commit_perf_report.log (same convention as io_check_task.bat /
# zcode_workspace_patrol.ps1 patrol logs - never the .runtime root).
#
# Read-only: the report only reads git log + .runtime/audit/*.jsonl and prints to
# stdout; no repo mutation, no DB writes, no task-control verbs beyond self-registration.
#
# Idempotent: Register-ScheduledTask -Force updates in place (same pattern as
# register_budget_report_task.ps1); rerun is safe.
#
# Roster coverage: placed at scripts/ root (NOT scripts/tasks/register/) so
# scripts/governance/scheduled_task_reconcile.py export_expected_tasks glob
# ("register_*.ps1", non-recursive) picks it up as a declared daily task.
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_commit_perf_report_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_CommitPerfReport /v /fo LIST
#         python scripts/governance/scheduled_task_reconcile.py

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_CommitPerfReport"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $PythonExe)) { throw "python.exe not found in known locations" }
}

$LogDir = "$RepoRoot\.runtime\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -Command & '$PythonExe' '$RepoRoot\scripts\governance\commit_perf_report.py' --hours 24 >> '$LogDir\commit_perf_report.log' 2>&1"
$Trigger = New-ScheduledTaskTrigger -Daily -At "07:00"
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Output "OK registered $TaskName (daily 07:00, 30min limit, log append)"
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next Run"
