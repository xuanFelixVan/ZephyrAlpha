# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md
# [MODULE] scripts.register_process_reaper_task
# [DOMAIN] D_INFRA_RUNTIME
# [A_module] module_id=MOD-RESOURCE_OPTIMIZATION_ENGINE | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_process_reaper_task.ps1 - Register the ProcessReaper Task Scheduler task
#
# Background (2026-08-28 ruling, supersedes ide_health_daemon resident-daemon model):
#   The old ide_health_daemon relied on AI sessions manually starting it at cold-boot
#   (AGENTS.md RULE-GUARDIAN gentlemen's agreement) - empirically broken: daemon died
#   leaving a stale PID file, sessions skipped the cold-start sequence, and a leftover
#   test-sweep loop spawned 60+ python processes overnight (7.7GB memory compression,
#   Trae UI freezing). Root cause: resident guardian processes are themselves residue
#   risks (recursive "who guards the guardian" problem), and creator-registration
#   (track_task_process) can never work because offending processes are exactly the
#   ones that never register.
#
# Architecture (first principles, mirrors deadman_switch.ps1 #ARCH-BOOT-002 E):
#   Task Scheduler "ZephyrAlpha_ProcessReaper" (AtLogOn + PT10M repeat, interactive user)
#     -> pythonw -m zephyr.trading.process_reaper (one-shot: scan -> judge -> kill -> exit)
#   Stateless one-shot = NO resident process, NO heartbeat, NO pid lock. Task Scheduler
#   is the sole lifecycle owner (boot_autostart_architecture.md C3). Fail-safe: if the
#   reaper itself dies, the system degrades to "no cleanup" (pre-reaper state) - never
#   to "wrong kill" (whitelist-first, multi-signal judgement matrix).
#
# Key design:
#   - pythonw.exe (GUI subsystem, zero console window; mirrors register_drift_watchdog_task.ps1)
#   - MultipleInstances=Parallel (#ARCH-BOOT-001 lesson): reaper runs are idempotent
#     (killing an already-dead PID is a no-op), brief overlap is harmless; IgnoreNew
#     would let a hung instance block all future sweeps.
#   - ExecutionTimeLimit=10min: a normal run finishes in <30s; a hung instance is
#     reaped by the OS itself (dogfood: the reaper must not become a zombie).
#   - No RestartOnFailure: one-shot semantics, next PT10M trigger is the retry.
#   - Idempotent non-destructive: Set-ScheduledTask updates IN PLACE (NEVER
#     Unregister+Register - Unregister kills a running instance).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_process_reaper_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_ProcessReaper /v /fo LIST
#         python -m zephyr.trading.process_reaper --status

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_ProcessReaper"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# pythonw.exe (GUI subsystem, zero window); zephyr resolves via editable install
$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

# 2026-08-28 light-import-isolation ruling: direct script execution (NOT -m package path)
# bypasses zephyr/__init__ Timer bootstrap chain. Root cause: the 0.05s daemon Timer in
# zephyr/__init__ imports auto_bootstrap (connects ClickHouse); on CH failure the background
# thread held the import lock and starved the reaper main thread (13:55 hang incident).
# The janitor must be hardier than what it cleans: zero zephyr imports + no package __init__.
$argString = 'src\zephyr\trading\process_reaper.py'
$action = New-ScheduledTaskAction -Execute $PythonW -Argument $argString -WorkingDirectory $RepoRoot

# Settings: Parallel (one-shot idempotent, no single-instance decision by Task Scheduler) +
#   ExecutionTimeLimit 10min (OS reaps hung instances - dogfooding)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

# Two triggers (mirrors drift watchdog tier): AtLogOn + Once(now)
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
$onceTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date)

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($logonTrigger, $onceTrigger) `
        -Settings $settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place: $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($logonTrigger, $onceTrigger) `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "Registered process reaper task: $TaskName -> pythonw -m zephyr.trading.process_reaper"
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

Write-Host ""
Write-Host "Done. ProcessReaper: AtLogOn + every 10min, one-shot (scan->judge->kill->exit), ExecutionTimeLimit=10min."
Write-Host "Run now:      schtasks /run /tn $TaskName"
Write-Host "Query status: python src\zephyr\trading\process_reaper.py --status"
Write-Host "Dry-run:      python src\zephyr\trading\process_reaper.py --dry-run"
Write-Host "Keep list:    data\runtime\process_reaper_keep.txt (per-case preserve, one cmdline substring per line)"
