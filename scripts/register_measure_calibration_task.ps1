# [BLUEPRINT] MOD-RESCHED-CALIB | docs/_working/resource_schedule/resource_schedule_v2_construction_plan.md | 4-P5
# [MODULE] scripts.register_measure_calibration_task
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-RESCHED-CALIB-REG | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_measure_calibration_task.ps1 - Register ZephyrAlpha_MeasureCalibration scheduled task
#
# Purpose (schedule v2 P5): weekly Saturday 06:17 run the p90 measured-vs-declared
# calibrator (read-only arm: sample stream + registry, never writes measured.*) to
# docs/_working/resource_schedule/calibration_report.yaml. Saturday morning sits in
# the mine_vs_exam quiet band (factory_lane_c starts 10:00, c4_exam 14:00); 06:17 is
# distinct from every declared window (06:13 scan cadence excluded by dow anyway).
# Deviations over tolerance are flagged as PROPOSALS for a human/AI correction batch
# (constitution: declared values change only through the gated apply path).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_measure_calibration_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_MeasureCalibration /v /fo LIST
# Manual: python -m zephyr.infrastructure.system_telemetry.measure_calibration --print

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_MeasureCalibration"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$argString = '-m zephyr.infrastructure.system_telemetry.measure_calibration'
$action = New-ScheduledTaskAction -Execute $PythonW -Argument $argString -WorkingDirectory $RepoRoot

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

# Weekly Saturday 06:17 trigger
$weeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At "06:17"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $weeklyTrigger `
        -Settings $settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $weeklyTrigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "Registered calibration task: $TaskName -> measure_calibration"
}

$task = $null
foreach ($attempt in 1..3) {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $task) { break }
    Start-Sleep -Milliseconds 800
}
if ($null -eq $task) { throw "Task not found after registration: $TaskName" }

Write-Host ""
Write-Host "Done. MeasureCalibration: weekly Sat 06:17 one-shot, ExecutionTimeLimit=15min."
Write-Host "Query status: schtasks /query /tn $TaskName /v /fo LIST"
