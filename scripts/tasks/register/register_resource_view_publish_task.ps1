# [BLUEPRINT] MOD-RESCHED-VIEW | docs/03_modules/_domain_frontend/resource_week_view/blueprint.md
# [MODULE] scripts.register_resource_view_publish_task
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-RESCHED-VIEW | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_resource_view_publish_task.ps1 - Schedule the week-view render + alert publish (L-2)
#
# Purpose (resource scheduling panorama v2, plan section 4 P0 item 1): the read-only
#   week view (web/features/resourceweek/rw-data.js) and the conflict alert feed both
#   had no production trigger - the view silently rotted (its embedded registry
#   fingerprint drifted away from the registry, C-10) and sched_* findings only reached
#   .runtime/ops_notifications/notifications.jsonl when a human thought to ask. This
#   script puts the "render + broadcast" step on the schedule.
#
#   Task "ZephyrAlpha_ResourceViewPublish"
#     Daily 05:50 (local) -> pythonw generate_resource_week_view.py --publish-alerts
#
# Why DAILY cadence (not hourly): this generator rewrites a git-tracked file (the
#   view data blob). One render per day keeps git noise bounded to a single file that
#   the existing derived-sync housekeeping absorbs - same reasoning as
#   register_resource_sampler_writeback_task.ps1. 05:50 sits AFTER the sampler measured
#   writeback (05:40, because the view renders measured.* values) and BEFORE the 08:30
#   pre_market slot - the quiet window, with no heavy neighbours.
#
# Why the hourly regen-check task does not do this too: separation of cadences - the
#   registry check must be fast and frequent (it is the chain watchdog), the view is a
#   report. They also publish to the alert board under different module_ids so their
#   resolve-hysteresis never erases each other's open alerts.
#
# Key design:
#   - pythonw.exe (GUI subsystem, zero console window; mirrors the sampler tasks).
#   - MultipleInstances=IgnoreNew: two concurrent renders would race the CAS write of
#     the same output blob for nothing.
#   - ExecutionTimeLimit=15min: a normal render (cron expansion + gate findings) runs
#     in well under a minute.
#   - No RestartOnFailure: one-shot semantics, the next daily trigger is the retry.
#   - Idempotent non-destructive: Set-ScheduledTask updates IN PLACE (NEVER
#     Unregister+Register - Unregister kills a running instance).
#   - ONE TASK PER FILE (repo convention): the registry generator parses
#     register_*.ps1 per file and attributes triggers per file; a combined
#     regen-check + view-publish file would mis-attribute one cron to both tasks
#     (verified 2026-09-16 on the sampler pair, hence the split).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_resource_view_publish_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_ResourceViewPublish /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_ResourceViewPublish"

$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$Generator = "$RepoRoot\scripts\governance\generators\generate_resource_week_view.py"
if (-not (Test-Path $Generator)) { throw "week view generator not found: $Generator" }

$Action = New-ScheduledTaskAction -Execute $PythonW `
    -Argument "`"$Generator`" --publish-alerts" `
    -WorkingDirectory $RepoRoot

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -StartWhenAvailable

$Trigger = New-ScheduledTaskTrigger -Daily -At "05:50"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings -Description "Resource week view daily render plus conflict-alert publish to the ops notification board" -Force | Out-Null
    Write-Host "Registered week view publish task: $TaskName -> pythonw generate_resource_week_view.py --publish-alerts"
}
