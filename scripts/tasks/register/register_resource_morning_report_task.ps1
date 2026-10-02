# [BLUEPRINT] MOD-RESCHED-MORNING | docs/_working/resource_schedule/resource_schedule_v2_construction_plan.md | 2.2 L-9 / 4-P5
# [MODULE] scripts.register_resource_morning_report_task
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-RESCHED-MORNING | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_resource_morning_report_task.ps1 - Register ZephyrAlpha_ResourceMorningReport scheduled task
#
# Purpose (schedule v2 P5, L-9): daily 06:31 render the resource morning report
# (registry + incubation ledger + sample stream + notification board -> one markdown,
# zero new data sources) into docs/_working/resource_schedule/morning_report/latest.md.
# Placed after sampler writeback (05:40) and week-view publish (05:50) so the report
# reads same-day fresh data; 06:31 avoids every declared same-second co-start.
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_resource_morning_report_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_ResourceMorningReport /v /fo LIST
# Manual: python scripts\governance\generators\generate_resource_morning_report.py --print-md

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_ResourceMorningReport"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# pythonw.exe (GUI subsystem, zero console window; mirrors register_pattern_mining_task.ps1)
$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$argString = 'scripts/governance/generators/generate_resource_morning_report.py'
$action = New-ScheduledTaskAction -Execute $PythonW -Argument $argString -WorkingDirectory $RepoRoot

# Settings: Parallel harmless (report render is idempotent full rewrite via CAS) +
# ExecutionTimeLimit 5min anti-zombie (normal run < 2s)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

# Daily trigger at 06:31 (after 05:40 writeback / 05:50 view publish, before market open)
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At "06:31"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $dailyTrigger `
        -Settings $settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $dailyTrigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "Registered morning report task: $TaskName -> generate_resource_morning_report.py"
}

$task = $null
foreach ($attempt in 1..3) {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $task) { break }
    Start-Sleep -Milliseconds 800
}
if ($null -eq $task) { throw "Task not found after registration: $TaskName" }

Write-Host ""
Write-Host "Done. ResourceMorningReport: daily 06:31 one-shot render, ExecutionTimeLimit=5min."
Write-Host "Query status: schtasks /query /tn $TaskName /v /fo LIST"
