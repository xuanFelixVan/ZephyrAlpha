# [MODULE] scripts.register_config_check_task
# [DOMAIN] D_INFRA_OPS
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-092 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_config_check_task.ps1 - Register the ZephyrAlpha_ConfigCheck Task Scheduler task
#
# Purpose (WORK-ORDER-3, 2026-09-18): Daily config effect check. Compares on-disk
# schedule.yaml/tasks.yaml against the scheduler process loaded-state fingerprint
# snapshot (tmp/scheduler_loaded_state.json). Mismatch -> data/failures/*.json alert.
# This is a SMOKE ALARM ONLY -- no hot reload (hot-reload was ruled out, 2026-09-17).
#
# Architecture:
# Task Scheduler "ZephyrAlpha_ConfigCheck" (Daily 08:05, interactive user)
# -> pythonw -m zephyr.infra_ops.config_effect_checker
# Each run = single check (read snapshot -> hash disk files -> diff parsed structures
# -> write tmp/config_effect_check_report.json -> alert on mismatch -> exit).
#
# Key design:
# - pythonw.exe (GUI subsystem, zero console window; mirrors register_pattern_mining_task.ps1)
# - Daily 08:05: before pre_market (08:34), catches overnight config edits before the trading day
# - MultipleInstances=Parallel: check is read-only + idempotent, brief overlap harmless
# - ExecutionTimeLimit=10min: normal run <5s, timeout reclaimed by OS (anti-zombie)
# - Idempotent non-destructive: Set-ScheduledTask in-place update (NEVER Unregister+Register)
# - Exit codes: 0=ok / 1=mismatch / 2=unknown (fail-closed, snapshot missing is NOT green)
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_config_check_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_ConfigCheck /v /fo LIST
# Manual: python -m zephyr.infra_ops.config_effect_checker

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_ConfigCheck"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# pythonw.exe (GUI subsystem, zero window); zephyr resolves via editable install
$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

# Module entry uses -m path. Task Scheduler runs with WorkingDirectory=RepoRoot.
$argString = '-m zephyr.infra_ops.config_effect_checker'
$action = New-ScheduledTaskAction -Execute $PythonW -Argument $argString -WorkingDirectory $RepoRoot

# Settings: Parallel (idempotent read-only check) + ExecutionTimeLimit 10min (OS reclaim anti-zombie)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

# Daily trigger: run once daily at 08:05 (before pre_market 08:34)
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At "08:05"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $dailyTrigger `
        -Settings $settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $dailyTrigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "Registered config check task: $TaskName -> pythonw -m zephyr.infra_ops.config_effect_checker"
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
Write-Host "Done. ConfigCheck: Daily 08:05, one-shot (read snapshot -> hash disk -> diff -> alert -> exit), ExecutionTimeLimit=10min."
Write-Host "Run now:      schtasks /run /tn $TaskName"
Write-Host "Query status: schtasks /query /tn $TaskName /v /fo LIST"
Write-Host "Manual run:   python -m zephyr.infra_ops.config_effect_checker"
Write-Host "Report file:  tmp\config_effect_check_report.json"
Write-Host "Alerts land:  data\failures\*_config_effect_check.json (ERROR level only)"
