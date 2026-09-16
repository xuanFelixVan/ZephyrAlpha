# [BLUEPRINT] MOD-RESCHED-PROFILE | docs/03_modules/_cross_layer/resource_profile_registry/blueprint.md
# [MODULE] scripts.register_resource_regen_check_task
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-RESCHED-PROFILE | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_resource_regen_check_task.ps1 - Schedule the resource-registry regen check (L-2)
#
# Purpose (resource scheduling panorama v2, plan section 4 P0 item 1 "eat our own
#   dogfood"): config/resource_profile_registry.yaml is a GENERATED file whose three
#   truth sources (register_*.ps1 / schedule.yaml / plan-doc seeds) are edited by
#   humans and AI all the time, but nothing used to re-run the generator on a
#   schedule. Drift therefore stayed invisible until a commit happened to hit the
#   RESOURCE-SCHEDULE gate. This script puts "regeneration" itself on the schedule.
#
#   Task "ZephyrAlpha_ResourceRegenCheck"
#     Hourly one-shot -> pythonw generate_resource_profile_registry.py
#                        --check --publish-alerts --auto-regen
#
# What one run does (all logic lives in the generator, none in this file):
#   1. compares the three truth sources against the registry on disk;
#   2. probes scheduling-chain health: C-5 (is the E0 calendar / the conflict gate /
#      its registration actually resolvable - previously the alert chain went silent
#      exactly when the guard was missing) and C-10 (does the week view's embedded
#      registry fingerprint still match the registry);
#   3. --auto-regen: if the registry drifted, rewrite it from truth sources
#      (merge-preserve keeps human-reviewed and measured fields);
#   4. --publish-alerts: pushes the resulting sched_* findings to the single
#      notification board .runtime/ops_notifications/notifications.jsonl via
#      OpsAlertFeed (publisher identity resource-schedule-regen).
#
# Key design:
#   - pythonw.exe (GUI subsystem, zero console window; mirrors the sampler tasks).
#   - MultipleInstances=IgnoreNew: --auto-regen does a CAS write on the registry, so
#     two concurrent runs would only race the compare-and-swap for nothing.
#   - ExecutionTimeLimit=10min: a normal check is a few seconds; the limit only
#     matters if the truth-source glob ever hangs.
#   - No RestartOnFailure: one-shot semantics, the next hourly trigger is the retry.
#   - Hourly cadence is patched post-registration (PS5.1 New-ScheduledTaskTrigger
#     has no -Repetition parameter), same as register_resource_sampler_scan_task.ps1.
#     Consequence for the registry: no cron is extractable from this file's static
#     text, so the entity materializes as window_type=event - deliberate, because
#     "time values never move" forbids hand-writing window_expr.
#   - Exit code 2 (drift survived regen) / 3 (health codes only) is intentionally
#     not turned into a task failure: the alert board is the signalling channel.
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_resource_regen_check_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_ResourceRegenCheck /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_ResourceRegenCheck"

$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$Generator = "$RepoRoot\scripts\governance\generators\generate_resource_profile_registry.py"
if (-not (Test-Path $Generator)) { throw "registry generator not found: $Generator" }

$Action = New-ScheduledTaskAction -Execute $PythonW `
    -Argument "`"$Generator`" --check --publish-alerts --auto-regen" `
    -WorkingDirectory $RepoRoot

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -StartWhenAvailable

$OnceTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date)

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $OnceTrigger `
        -Settings $Settings | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $OnceTrigger `
        -Settings $Settings -Description "Resource registry hourly self-check: truth-source drift regen (L-2) + gate-absence (C-5) + view-staleness (C-10) alerts" -Force | Out-Null
    Write-Host "Registered regen check task: $TaskName -> pythonw generate_resource_profile_registry.py --check --publish-alerts --auto-regen"
}

# PT1H repetition patched post-registration; Register->Query has a sub-second race
# (Get right after Register sporadically returns null) - retry x3
$task = $null
foreach ($attempt in 1..3) {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $task) { break }
    Start-Sleep -Milliseconds 800
}
if ($null -eq $task) { throw "Task not found after registration: $TaskName" }
foreach ($t in $task.Triggers) { $t.Repetition.Interval = "PT1H" }
$task | Set-ScheduledTask | Out-Null
Write-Host "PT1H repetition patched: $TaskName"
