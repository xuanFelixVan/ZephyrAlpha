# [MODULE] scripts.register_decision_chain_sentinel_task
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# register_decision_chain_sentinel_task.ps1 - Register the decision chain sentinel daily task
#
# Purpose (TRD-A01 / L09-C04, docs/_working/decision_map_campaign_20260924/
#   links/L09_review/SKEL.md): alert when the decision chain starves - N or more
#   consecutive trading days without a new c1_backtest.decision_daily row.
#   Runs 09:40 on trading days BEFORE the market opens, so a broken overnight
#   dloop leg is surfaced while the human is still pre-market.
#
#   Task "ZephyrAlpha_DecisionChainSentinel"
#     Daily 09:40 -> pythonw scripts\governance\decision_chain_sentinel.py
#     Read-only CH probe (DatabaseService reader); on starvation appends one
#     alert line to .runtime\logs\decision_chain_alert.jsonl and exits 4;
#     healthy = exit 0; DB failure = fail-soft error record + exit 8.
#
# Key design (mirrors register_resource_sampler_scan_task.ps1 / reaper sibling):
#   - pythonw.exe (GUI subsystem, zero console window).
#   - Direct file path (scripts/ is not an importable -m package); the script
#     bootstraps repo root onto sys.path itself.
#   - MultipleInstances=IgnoreNew: daily one-shot, no overlap risk; a hung
#     instance cannot stack.
#   - ExecutionTimeLimit=15min: the probe is two count/max queries; anything
#     longer means CH is wedged and the OS should reap the instance.
#   - No RestartOnFailure: one-shot semantics, next day 09:40 is the retry.
#   - Idempotent non-destructive: Set-ScheduledTask updates IN PLACE (NEVER
#     Unregister+Register - Unregister kills a running instance).
#   - ONE TASK PER FILE (repo convention).
#   - Companion keep-alive entry "decision_chain_sentinel" must exist in
#     data\runtime\process_reaper_keep.txt (appended by the session that
#     registered this task; reaper matches cmdline substrings).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_decision_chain_sentinel_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_DecisionChainSentinel /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_DecisionChainSentinel"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# pythonw.exe (GUI subsystem, zero window); zephyr resolves via editable install
$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$ScriptPath = Join-Path $RepoRoot "scripts\governance\decision_chain_sentinel.py"
if (-not (Test-Path $ScriptPath)) { throw "sentinel script missing: $ScriptPath" }

$Action = New-ScheduledTaskAction -Execute $PythonW `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory $RepoRoot

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -StartWhenAvailable

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited
# Daily 09:40 pre-market slot (TRD-A01): decision row for today was due at
# 16:45 yesterday; 09:40 leaves margin before the 09:25/09:35 trading tasks.
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At "09:40"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $dailyTrigger `
        -Settings $Settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $dailyTrigger `
        -Settings $Settings -Principal $principal `
        -Description "Decision chain sentinel (TRD-A01/L09-C04): daily 09:40 read-only probe of c1_backtest.decision_daily; alert jsonl + exit 4 on N-day starvation, exit 8 fail-soft on DB error" -Force | Out-Null
    Write-Host "Registered decision chain sentinel task: $TaskName -> pythonw scripts\governance\decision_chain_sentinel.py"
}

# Registration->query has a sub-second race (sibling lesson) - retry x3 then verify
$task = $null
foreach ($attempt in 1..3) {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $task) { break }
    Start-Sleep -Milliseconds 800
}
if ($null -eq $task) { throw "Task not found after registration: $TaskName" }
Write-Host ("Verified: {0} state={1} next_run={2}" -f $TaskName, $task.State, ($task.Triggers[0].StartBoundary))
