# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md
# [MODULE] scripts.register_counter_trend_feeder_tasks
# [DOMAIN] D_INFRA_RUNTIME
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# register_counter_trend_feeder_tasks.ps1 - Register the counter-trend-board feeder tasks
#
# Purpose (2026-09-15, MOD-SIG-080 counter-trend board two-leg repair):
#   1. ZephyrAlpha_IntradayFundFlow - THS industry fund-flow snapshots at 10:05/11:05/
#      13:35/14:35/15:05 (sector_fund_flow, segment-diff needs >=1 snapshot inside the
#      down-segment; single EOD snapshot cannot feed card2 by design).
#   2. ZephyrAlpha_IndexMinuteEOD  - SSE index 1m-K EOD backfill at 15:10
#      (index_quote, feeds the peak/trough down-segment detector; miniQMT channel,
#      re-route to QMT file bridge after 2026-09-18 cutover, playbook #93).
#
# Design mirrors register_process_reaper_task.ps1: pythonw one-shot, stateless,
# Parallel instances, ExecutionTimeLimit 10min, idempotent Set-ScheduledTask update.
# Trading-day filtering: scripts exit 0 with "0 rows" on non-trading days (no noise).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_counter_trend_feeder_tasks.ps1
# Verify: schtasks /query /tn ZephyrAlpha_IntradayFundFlow /v /fo LIST
#         schtasks /query /tn ZephyrAlpha_IndexMinuteEOD  /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

# Log dir (append stdout+stderr for post-mortem; ScheduledTaskAction cannot redirect,
# so wrap with cmd /c)
$LogDir = Join-Path $RepoRoot "logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

function New-FeederTask {
    param(
        [string]$TaskName,
        [string]$ScriptPath,
        [string]$LogName,
        [string[]]$Times
    )
    $argString = "/c cd /d $RepoRoot && `"$PythonW`" `"$ScriptPath`" --once >> `"$LogDir\$LogName`" 2>&1"
    if ($ScriptPath -like "*index_minute*") {
        $argString = "/c cd /d $RepoRoot && `"$PythonW`" `"$ScriptPath`" >> `"$LogDir\$LogName`" 2>&1"
    }
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $argString -WorkingDirectory $RepoRoot

    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

    $principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

    $triggers = @()
    foreach ($t in $Times) {
        $triggers += New-ScheduledTaskTrigger -Daily -At $t
    }

    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers `
            -Settings $settings -Principal $principal | Out-Null
        Write-Host "Updated existing task in place: $TaskName"
    } else {
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers `
            -Settings $settings -Principal $principal -Force | Out-Null
        Write-Host "Registered: $TaskName ($($Times -join ', '))"
    }
}

# 1) THS industry fund-flow snapshots (segment-diff feed for card2)
New-FeederTask -TaskName "ZephyrAlpha_IntradayFundFlow" `
    -ScriptPath "$RepoRoot\scripts\data\collect_sector_fund_flow.py" `
    -LogName "fundflow_collect.log" `
    -Times @("10:05", "11:05", "13:35", "14:35", "15:05")

# 2) SSE index 1m-K EOD backfill (index-leg feed; miniQMT channel until 09-18 cutover)
New-FeederTask -TaskName "ZephyrAlpha_IndexMinuteEOD" `
    -ScriptPath "$RepoRoot\scripts\data\collect_index_minute_eod.py" `
    -LogName "index_minute_eod.log" `
    -Times @("15:10")

Write-Host ""
Write-Host "Done. Verify:"
Write-Host "  schtasks /query /tn ZephyrAlpha_IntradayFundFlow /v /fo LIST"
Write-Host "  schtasks /query /tn ZephyrAlpha_IndexMinuteEOD /v /fo LIST"
Write-Host "Manual run:"
Write-Host "  schtasks /run /tn ZephyrAlpha_IntradayFundFlow"
Write-Host "  schtasks /run /tn ZephyrAlpha_IndexMinuteEOD"
