# [BLUEPRINT] MOD-SCRIPT-register_kronos_scoring | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.register_kronos_scoring_task
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-register_kronos_scoring_task | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_kronos_scoring_task.ps1 - Register the ZephyrAlpha_KronosScoring task.
#
# Purpose (work order GPU-02 step 3, Owner order 2026-10-11): nightly forward-scoring batch for
#   Kronos, writing c1_market.kronos_prediction_daily on the gpu_default mutex group.
#
# Architecture (mirrors register_factory_lane_c_task.ps1 / register_pattern_mining_task.ps1):
#   Task Scheduler ZephyrAlpha_KronosScoring (00:30 Sunday-Thursday)
#   -> powershell -File scripts\tasks\run\run_kronos_scoring.ps1
#   -> python scripts\backtest\kronos_adapter.py --score-only ...
#
# Key design:
# - 00:30 Sun-Thu = the schedule the order asked for. Trading days only (Fri/Sat night idle),
#   and the wrapper caps runtime at 25 minutes so nothing overruns into the 01:00-04:00 ClickHouse
#   yield window; ExecutionTimeLimit=35min is the outer OS-level reclaim (25min batch + startup).
# - MultipleInstances=IgnoreNew: a second fire must never stack a second GPU job.
# - Predictions are written but NOT consumed; signal wiring is a B-007 human-gate decision.
# - Idempotent non-destructive: Set-ScheduledTask in-place update (NEVER Unregister+Register).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\tasks\register\register_kronos_scoring_task.ps1
#        (registers DISABLED by default; add -Enable to leave it armed)
# Verify: schtasks /query /tn ZephyrAlpha_KronosScoring /v /fo LIST
# Manual kick: schtasks /run /tn ZephyrAlpha_KronosScoring
# Then regenerate the resource registry FROM THE MAIN ROOT:
#   python scripts\governance\generators\generate_resource_profile_registry.py
#
# Why disabled by default (measured on the live registry face, 2026-10-12 03:1x, see
# docs/_archive/_working_cleared/gpuwo_campaign/11_resource_declaration_and_overlap_precheck.yaml):
# - the generator has no per-schedule channel for GPU classes, so a fresh sch_* entity from this
#   script lands as resource_class=light / pool=default / exclusive_group=[] - i.e. the conflict
#   gate cannot see that this batch wants the gpu_default mutex at all;
# - on the clock face, 00:30 Sun-Thu sits inside sch_f06_grid's Saturday 23:00 + 1440min window.
# Registering the calendar but leaving it disabled keeps "no production behaviour change" literally
# true; arming it is an Owner-visible act (run this script with -Enable, or schtasks /change).

param([switch]$Enable)

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_KronosScoring"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File $RepoRoot\scripts\tasks\run\run_kronos_scoring.ps1"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday,Monday,Tuesday,Wednesday,Thursday -At "00:30"
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 35) `
    -MultipleInstances IgnoreNew -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings -Principal $Principal | Out-Null
    Write-Output "OK updated $TaskName in place (00:30 Sun-Thu, 35min limit)"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings -Principal $Principal -Force | Out-Null
    Write-Output "OK registered $TaskName (00:30 Sun-Thu, 35min limit)"
}
if ($Enable) {
    Enable-ScheduledTask -TaskName $TaskName | Out-Null
    Write-Output "STATE enabled (-Enable passed; armed: this batch will fire at 00:30 Sun-Thu)"
} else {
    Disable-ScheduledTask -TaskName $TaskName | Out-Null
    Write-Output "STATE disabled (default; arm with -Enable or: schtasks /change /tn $TaskName /enable)"
}
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next"

