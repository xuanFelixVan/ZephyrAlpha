# [BLUEPRINT] MOD-SCRIPT-register_night_mining | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.register_night_mining_task
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-register_night_mining_task | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_night_mining_task.ps1 - Register the ZephyrAlpha_NightMining task.
#
# Purpose (work order GPU-01 step 3, Owner order 2026-10-11): make the local-Ollama hypothesis
#   mining batch a standing night-window producer, on the llm_local mutex group (qwen3 single
#   instance) so it cannot overlap the 22:30 sentiment window or the 20:00 LaneC window.
#
# Architecture (mirrors register_factory_lane_c_task.ps1 / register_pattern_mining_task.ps1):
#   Task Scheduler ZephyrAlpha_NightMining (23:00 Sunday-Thursday)
#   -> powershell -File scripts\tasks\run\run_night_mining.ps1
#   -> lane_b_idea_generator.py generate --model <tier>   (backlog CSV, no auto-enrol)
#   -> mcts_expression_search.py --iterations N           (backlog CSV, zero LLM)
#
# Key design:
# - 23:00 Sun-Thu: starts after the 22:30 sentiment window and finishes well before the
#   01:00-04:00 ClickHouse yield window. Friday/Saturday nights are intentionally excluded
#   (Saturday belongs to the mine_vs_exam serialized window per config/schedule_gate_policy.yaml).
# - ExecutionTimeLimit=2h, MultipleInstances=IgnoreNew (a second fire must not stack a second
#   Ollama instance; the 10-09 LaneC run died at exactly its 4h cap, which is why the cap here
#   is set to a value the legs can actually finish inside).
# - Output goes to the intake backlog only. Enrolment (E2 precheck verdict ledger / exam-file
#   construction) is a separate leg and is NOT triggered here.
# - Model tier comes from $env:NIGHT_MINING_MODEL; the A/B decision (GPU-01 step 1) sets the
#   default. Until that report lands, the wrapper keeps the production tier qwen3:8b.
# - Idempotent non-destructive: Set-ScheduledTask in-place update (NEVER Unregister+Register).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\tasks\register\register_night_mining_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_NightMining /v /fo LIST
# Manual kick: schtasks /run /tn ZephyrAlpha_NightMining
# Then regenerate the resource registry FROM THE MAIN ROOT:
#   python scripts\governance\generators\generate_resource_profile_registry.py
#
# Usage note: registers DISABLED by default; add -Enable to arm it.
#
# Why disabled by default (measured 2026-10-12 03:1x on the live registry face; see
# docs/_working/gpuwo_campaign/11_resource_declaration_and_overlap_precheck.yaml):
# - sch_f06_grid / sch_factory_lane_c arithmetic: LaneC runs Mon-Fri 20:00 with a 240min ceiling,
#   i.e. its tail can reach 00:00, and this window opens at 23:00 on the same five nights. Both
#   batches want the local LLM, so the collision is real even though my run script refuses to
#   auto-enrol anything into intake.
# - the generator has no per-schedule GPU/LLM class channel, so a fresh sch_* entity from this
#   script lands as resource_class=light / pool=default / exclusive_group=[]: the conflict gate
#   would report "zero red" for the wrong reason (it cannot see the mutex at all).
# Arming is therefore an explicit act: run this file with -Enable, or schtasks /change /enable.

param([switch]$Enable)

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_NightMining"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File $RepoRoot\scripts\tasks\run\run_night_mining.ps1"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday,Monday,Tuesday,Wednesday,Thursday -At "23:00"
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances IgnoreNew -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings -Principal $Principal | Out-Null
    Write-Output "OK updated $TaskName in place (23:00 Sun-Thu, 2h limit)"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings -Principal $Principal -Force | Out-Null
    Write-Output "OK registered $TaskName (23:00 Sun-Thu, 2h limit)"
}
if ($Enable) {
    Enable-ScheduledTask -TaskName $TaskName | Out-Null
    Write-Output "STATE enabled (-Enable passed; armed: fires 23:00 Sun-Thu)"
} else {
    Disable-ScheduledTask -TaskName $TaskName | Out-Null
    Write-Output "STATE disabled (default; arm with -Enable or: schtasks /change /tn $TaskName /enable)"
}
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next"
