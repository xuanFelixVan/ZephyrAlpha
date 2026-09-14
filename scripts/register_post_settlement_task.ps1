# [BLUEPRINT] MOD-SCRIPT-run_post_settlement | scripts/run_post_settlement.py
# [MODULE] scripts.register_post_settlement_task
# [DOMAIN] D_TRADING
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-register_post_settlement_task | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_post_settlement_task.ps1 - Register the PostSettlement Task Scheduler task
#
# Background (Owner 2026-09-15 blanket automation directive, opens the B5 Owner window):
#   run_post_settlement.py was designed as a manual CLI (57 GOING-CONCERN doc GAP-3).
#   The Owner mandate "full module automation, zero human participation" authorizes the
#   15:30 weekday wall-clock trigger (construction_backlog.md B5 spec: cron 30 15 * * *).
#
# Architecture (mirrors register_process_reaper_task.ps1 stateless one-shot pattern):
#   Task Scheduler "ZephyrAlpha_PostSettlement" (weekly Mon-Fri 15:30, interactive user)
#     -> python.exe scripts\run_post_settlement.py (one-shot: recon -> audit -> report -> exit)
#   - StartWhenAvailable: if the machine is asleep/off at 15:30, run at next wake.
#   - MultipleInstances=IgnoreNew: settlement must not overlap.
#   - ExecutionTimeLimit=30min: a normal run is minutes; a hung run is killed by OS.
#   - Output appended to data\runtime\post_settlement_last_run.log (rotate-free, CLI is
#     idempotent per trade_date per its INVARIANTS).
#   - Non-trading days: the CLI resolves the previous trading day itself and reports
#     SKIPPED semantics in-band (exit 0) - no holiday calendar needed here.
#   - QMT offline: CLI degrades to system-side-only reconciliation with explicit
#     annotation (no fake broker-side comparison), per its INVARIANTS.
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_post_settlement_task.ps1

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonExe = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
if (-not (Test-Path $pythonExe)) { $pythonExe = "python.exe" }
$logPath = Join-Path $repoRoot "data\runtime\post_settlement_last_run.log"
$cliPath = Join-Path $repoRoot "scripts\run_post_settlement.py"

$action = New-ScheduledTaskAction -Execute $pythonExe `
    -Argument ('-u "' + $cliPath + '" >> "' + $logPath + '" 2>&1') `
    -WorkingDirectory $repoRoot
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "15:30"
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

$existing = Get-ScheduledTask -TaskName "ZephyrAlpha_PostSettlement" -ErrorAction SilentlyContinue
if ($existing) {
    Set-ScheduledTask -TaskName "ZephyrAlpha_PostSettlement" -Action $action -Trigger $trigger -Settings $settings | Out-Null
    Write-Output "UPDATED ZephyrAlpha_PostSettlement (in place, no unregister)"
} else {
    Register-ScheduledTask -TaskName "ZephyrAlpha_PostSettlement" -Action $action -Trigger $trigger -Settings $settings | Out-Null
    Write-Output "REGISTERED ZephyrAlpha_PostSettlement"
}
Get-ScheduledTask -TaskName "ZephyrAlpha_PostSettlement" | Select-Object TaskName, State | Format-Table -AutoSize
