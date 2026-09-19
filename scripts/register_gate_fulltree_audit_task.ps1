# [BLUEPRINT] MOD-INF-005 | scripts/register_gate_fulltree_audit_task.ps1 | #
# [MODULE] scripts.register_gate_fulltree_audit_task
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# register_gate_fulltree_audit_task.ps1 - Register the ZephyrAlpha_GateFullTreeAudit task
#
# Purpose (ruling #354, Owner approved 2026-09-19): daily full-tree audit wave for the
# nine staged-only detectors. Night-shift ruling P0-5: these detectors only ever saw the
# staged surface, so historical tracked-tree debt was permanently invisible to them.
# The runner scripts/governance/run_fulltree_gate_audit.py executes all nine detectors
# with --full-tree (staged-mode behavior unchanged; constitution S3.1 own-scope kept)
# and writes tmp/gate_fulltree_audit_report.json.
#
# Audit-scan is NOT a reconciler: constitution S9.3 event-trigger law does not apply
# (ruling #354 explicit). Scheduling carrier decision: ROOR has no existing audit-task
# family; nearest precedent is ZephyrAlpha_ConfigCheck (daily one-shot read-only check,
# pythonw + report-to-tmp), which this script mirrors.
#
# Key design (mirrors register_config_check_task.ps1):
# - pythonw.exe (GUI subsystem, zero console window)
# - Daily 03:30 (off trading hours, before ConfigCheck 08:05)
# - MultipleInstances=Parallel: audit is read-only + idempotent
# - ExecutionTimeLimit=30min: full dedup scan is the long pole; OS reclaim anti-zombie
# - Idempotent non-destructive: Set-ScheduledTask in-place update (NEVER Unregister)
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_gate_fulltree_audit_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_GateFullTreeAudit /v /fo LIST
# Manual: python scripts/governance/run_fulltree_gate_audit.py

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_GateFullTreeAudit"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# pythonw.exe (GUI subsystem, zero window); zephyr resolves via editable install
$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$argString = 'scripts\governance\run_fulltree_gate_audit.py --quiet'
$action = New-ScheduledTaskAction -Execute $PythonW -Argument $argString -WorkingDirectory $RepoRoot

# Settings: Parallel (read-only audit) + ExecutionTimeLimit 30min (OS reclaim anti-zombie)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

# Daily trigger: run once daily at 03:30 (off trading hours)
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At "03:30"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $dailyTrigger `
        -Settings $settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $dailyTrigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "Registered gate full-tree audit task: $TaskName -> pythonw scripts\governance\run_fulltree_gate_audit.py --quiet"
}

# Confirm task registered (sub-second race after registration, retry 3 times)
$task = $null
foreach ($attempt in 1..3) {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $task) { break }
    Start-Sleep -Milliseconds 800
}
if ($null -eq $task) { throw "Task not found after registration: $TaskName" }

Write-Host ""
Write-Host "Done. GateFullTreeAudit: Daily 03:30, one-shot read-only audit of 9 staged-only detectors (ruling #354), ExecutionTimeLimit=30min."
Write-Host "Run now:      schtasks /run /tn $TaskName"
Write-Host "Query status: schtasks /query /tn $TaskName /v /fo LIST"
Write-Host "Manual run:   python scripts\governance\run_fulltree_gate_audit.py"
Write-Host "Report file:  tmp\gate_fulltree_audit_report.json"
