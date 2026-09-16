# [BLUEPRINT] MOD-RESCHED-SAMPLER | docs/03_modules/_cross_layer/resource_sampler/blueprint.md
# [MODULE] scripts.register_resource_sampler_writeback_task
# [DOMAIN] D_INFRA_RUNTIME
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-RESCHED-SAMPLER | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_resource_sampler_writeback_task.ps1 - Register the ResourceSampler daily writeback task
#
# Purpose (resource scheduling panorama, plan section 2.2): aggregates sampler
# sample streams into config/resource_profile_registry.yaml measured.* keys
# (memory = observed max +15% margin; duration = P90) via safe_write_text CAS
# with file-header preservation. The registry generator re-merges and preserves
# measured on regeneration (sampler owns exactly those four keys, nothing else).
#
#   Task "ZephyrAlpha_ResourceSamplerWriteback"
#     Daily 05:40 (local) -> pythonw -m ...resource_sampler writeback
#
# Why DAILY cadence (not 10-min): writeback edits a git-tracked file (the
# registry); a 10-min cadence would keep the workspace permanently dirty.
# Daily keeps git noise bounded to one file which the existing derived-sync
# housekeeping absorbs. 05:40 chosen to slot AFTER catchup_guard (05:30) and
# BEFORE pre_market (08:30) - quiet window, no heavy neighbours.
#
# Key design:
#   - pythonw.exe (GUI subsystem, zero console window; mirrors reaper task).
#   - MultipleInstances=IgnoreNew: writeback rewrites the registry file; two
#     concurrent writebacks would race the CAS check for nothing (idempotent
#     values, but why allow the race).
#   - ExecutionTimeLimit=15min: a normal run finishes in seconds.
#   - No RestartOnFailure: one-shot semantics, next daily trigger is the retry.
#   - Idempotent non-destructive: Set-ScheduledTask updates IN PLACE.
#   - ONE TASK PER FILE (repo convention): see register_resource_sampler_scan_task.ps1.
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_resource_sampler_writeback_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_ResourceSamplerWriteback /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_ResourceSamplerWriteback"

$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$Action = New-ScheduledTaskAction -Execute $PythonW `
    -Argument "-m zephyr.infrastructure.system_telemetry.resource_sampler writeback" `
    -WorkingDirectory $RepoRoot

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -StartWhenAvailable

$Trigger = New-ScheduledTaskTrigger -Daily -At "05:40"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings -Description "Resource sampler daily measured writeback (max+15% margin mem / P90 duration, CAS-safe)" -Force | Out-Null
    Write-Host "Registered sampler writeback task: $TaskName -> pythonw -m ...resource_sampler writeback"
}
