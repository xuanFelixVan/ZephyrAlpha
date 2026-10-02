# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] scripts.register_health_monitor_probe_task
# [DOMAIN] D_INFRA_RUNTIME
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-035 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_health_monitor_probe_task.ps1 - Register the HealthMonitor one-shot probe task
#
# Purpose (I-06/F81 runtime-carrier gap, wave st-ffchief-20261001): the HealthMonitor
# module (zephyr/trading/health_monitor.py) had zero production trigger wiring outside
# the AutoRuntime boot chain (lifecycle_manager step 07, event-driven, in-process only).
# The EventBus is an in-process bus, so no cross-process event can reach a standalone
# monitor; the module's own tick() docstring designates external batch invocation as the
# designed fallback entry ("CI batch bottom-line call"). This script wires that carrier,
# mirroring the ProcessReaper / ResourceSamplerScan one-shot sibling pattern:
#
#   Task "ZephyrAlpha_HealthMonitorProbe"
#     AtLogOn + PT10M repeat -> pythonw -m zephyr.trading.health_monitor
#     One-shot per trigger: register shared probes -> reconcile (tiered auto-restart)
#     -> overwrite data/runtime/health_monitor/health_latest.json (bounded snapshot)
#     -> alert on inactive probes via pipeline_events (fail-open) -> process exits.
#
# Key design:
#   - pythonw.exe (GUI subsystem, zero console window; mirrors reaper/sampler tasks).
#   - One-shot semantics: NO resident process, NO sleep-loop (constitution S9.3);
#     Task Scheduler is the sole lifecycle owner.
#   - MultipleInstances=Parallel (#ARCH-BOOT-001 lesson): runs are idempotent
#     (snapshot overwrite + repeatable reconcile); IgnoreNew would let a hung
#     instance block all future probes.
#   - ExecutionTimeLimit=10min: a normal run finishes well under a minute; a hung
#     instance is reaped by the OS itself.
#   - No RestartOnFailure: one-shot semantics, next PT10M trigger is the retry.
#   - Idempotent non-destructive: Set-ScheduledTask updates IN PLACE (NEVER
#     Unregister+Register - Unregister kills a running instance).
#   - ONE TASK PER FILE (repo convention): the registry generator parses
#     register_*.ps1 per file.
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_health_monitor_probe_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_HealthMonitorProbe /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_HealthMonitorProbe"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# pythonw.exe (GUI subsystem, zero window); zephyr resolves via editable install
$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$Action = New-ScheduledTaskAction -Execute $PythonW `
    -Argument "-m zephyr.trading.health_monitor" `
    -WorkingDirectory $RepoRoot

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -StartWhenAvailable

$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
$onceTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date)

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger @($logonTrigger, $onceTrigger) `
        -Settings $Settings | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger @($logonTrigger, $onceTrigger) `
        -Settings $Settings -Description "HealthMonitor one-shot probe (10-min cadence, bounded snapshot, exit after run)" -Force | Out-Null
    Write-Host "Registered health probe task: $TaskName -> pythonw -m zephyr.trading.health_monitor"
}

# 10min periodic repeat (PS5.1 New-ScheduledTaskTrigger has no -Repetition param, patch post-registration)
# Registration->query has a sub-second race (Get right after Register sporadically returns null) - retry x3
$task = $null
foreach ($attempt in 1..3) {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $task) { break }
    Start-Sleep -Milliseconds 800
}
if ($null -eq $task) { throw "Task not found after registration: $TaskName" }
foreach ($t in $task.Triggers) { $t.Repetition.Interval = "PT10M" }
$task | Set-ScheduledTask | Out-Null
Write-Host "PT10M repetition patched: $TaskName"
