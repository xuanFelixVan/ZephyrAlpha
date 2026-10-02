# [BLUEPRINT] MOD-RESCHED-SAMPLER | docs/03_modules/_cross_layer/resource_sampler/blueprint.md
# [MODULE] scripts.register_resource_sampler_scan_task
# [DOMAIN] D_INFRA_RUNTIME
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-RESCHED-SAMPLER | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_resource_sampler_scan_task.ps1 - Register the ResourceSampler 10-min scan task
#
# Purpose (resource scheduling panorama, plan docs/_working/resource_schedule/
#   resource_schedule_panorama_plan_v1.md section 2.2): the sampler had zero
#   production trigger wiring after the overnight build - the measured section of
#   config/resource_profile_registry.yaml stayed empty because nothing invoked
#   scan outside tests. This script wires the production trigger, mirroring the
#   ProcessReaper one-shot sibling pattern (register_process_reaper_task.ps1):
#
#   Task "ZephyrAlpha_ResourceSamplerScan"
#     AtLogOn + PT10M repeat -> pythonw -m ...resource_sampler scan
#     One-shot per trigger: reads the production registry, observes processes by
#     cmdline pattern (zero intrusion - never modifies scripts, never kills),
#     appends samples to .runtime/logs/resource_samples/*.jsonl only.
#
# Key design:
#   - pythonw.exe (GUI subsystem, zero console window; mirrors reaper task).
#   - Uses "-m" package path (unlike reaper's direct-file isolation): the sampler
#     is telemetry, not a firefighter. If zephyr/__init__ bootstrap stalls on a
#     ClickHouse outage, ExecutionTimeLimit=10min lets the OS reap the instance;
#     worst case = one skipped scan cycle (acceptable degradation, next PT10M
#     trigger retries). Reaper must never hang; sampler may skip a beat.
#   - MultipleInstances=Parallel (#ARCH-BOOT-001 lesson): scans are idempotent
#     appends; IgnoreNew would let a hung instance block all future sweeps.
#   - No RestartOnFailure: one-shot semantics, next trigger is the retry.
#   - Idempotent non-destructive: Set-ScheduledTask updates IN PLACE (NEVER
#     Unregister+Register - Unregister kills a running instance).
#   - ONE TASK PER FILE (repo convention): the registry generator parses
#     register_*.ps1 per file; a combined scan+writeback file made it attribute
#     the writeback 05:40 cron to BOTH tasks (verified 2026-09-16, then split).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_resource_sampler_scan_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_ResourceSamplerScan /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_ResourceSamplerScan"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# pythonw.exe (GUI subsystem, zero window); zephyr resolves via editable install
$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$Action = New-ScheduledTaskAction -Execute $PythonW `
    -Argument "-m zephyr.infrastructure.system_telemetry.resource_sampler scan" `
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
        -Settings $Settings -Description "Resource sampler one-shot scan (10-min cadence, zero-intrusion cmdline observation)" -Force | Out-Null
    Write-Host "Registered sampler scan task: $TaskName -> pythonw -m ...resource_sampler scan"
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
