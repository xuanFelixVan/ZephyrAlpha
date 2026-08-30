# [BLUEPRINT] MOD-INF-055 | docs/03_modules/MOD-INF-055/
# [MODULE] scripts.register_pattern_mining_task
# [DOMAIN] D_SECURITY
# [A_module] module_id=MOD-INF-055 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_pattern_mining_task.ps1 - Register the ZephyrAlpha_PatternMining Task Scheduler task
#
# Purpose (16-doc section 4.4 P2-1): Periodically run fix_pattern_miner.run_once() to mine fix patterns
# and produce hit-rate statistics. Task Scheduler triggers daily (AtLogOn + daily repeat), no resident process.
#
# Architecture:
# Task Scheduler "ZephyrAlpha_PatternMining" (Daily, interactive user)
# -> pythonw -m zephyr.security.ops.fix_pattern_miner run_once
# Each run = single mining round (read pattern_index.yaml -> cluster stats -> produce suggestions -> write report -> exit).
# Report append-only to .runtime/security_ops/pattern_mining_reports.jsonl.
#
# Key design:
# - pythonw.exe (GUI subsystem, zero console window; mirrors register_process_reaper_task.ps1)
# - Daily trigger: Run once daily, suitable for low-frequency mining (fix patterns not real-time needed)
# - MultipleInstances=Parallel: Mining is idempotent (read YAML -> produce suggestions), brief overlap harmless
# - ExecutionTimeLimit=5min: Normal run <10s, timeout reclaimed by OS (anti-zombie)
# - Idempotent non-destructive: Set-ScheduledTask in-place update (NEVER Unregister+Register)
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_pattern_mining_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_PatternMining /v /fo LIST
# python -m zephyr.security.ops.fix_pattern_miner run_once

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_PatternMining"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# pythonw.exe (GUI subsystem, zero window); zephyr resolves via editable install
$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

# 2026-08-28 light-import-isolation ruling: Direct script execution bypasses zephyr/__init__ Timer bootstrap
# but fix_pattern_miner is a module entry, uses -m path. Task Scheduler runs with WorkingDirectory=RepoRoot.
$argString = '-m zephyr.security.ops.fix_pattern_miner run_once'
$action = New-ScheduledTaskAction -Execute $PythonW -Argument $argString -WorkingDirectory $RepoRoot

# Settings: Parallel (idempotent mining, brief overlap harmless) + ExecutionTimeLimit 5min (OS reclaim anti-zombie)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

# Daily trigger: Run once daily (default 09:00, adjust as needed)
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At "09:00"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $dailyTrigger `
        -Settings $settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $dailyTrigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "Registered pattern mining task: $TaskName -> pythonw -m zephyr.security.ops.fix_pattern_miner run_once"
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
Write-Host "Done. PatternMining: Daily 09:00, one-shot (mine->suggest->report->exit), ExecutionTimeLimit=5min."
Write-Host "Run now:      schtasks /run /tn $TaskName"
Write-Host "Query status: schtasks /query /tn $TaskName /v /fo LIST"
Write-Host "Manual run:   python -m zephyr.security.ops.fix_pattern_miner run_once"
Write-Host "Report file:  .runtime\security_ops\pattern_mining_reports.jsonl"
