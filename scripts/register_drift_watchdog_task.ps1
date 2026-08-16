# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | scripts/register_drift_watchdog_task.ps1 | #99-2
# [MODULE] scripts.register_drift_watchdog_task
# [DOMAIN] D_GOV_ENFORCEMENT
# [TTL] permanent
# register_drift_watchdog_task.ps1 - Register the worktree_drift_watchdog Task Scheduler task
# (#99-2 root fix: RestartOnFailure backoff)
#
# Background (#99 memory-exhaustion incident, 2026-08-16 evening, 800705AF pagefile):
#   An ad-hoc registered drift_watchdog task had RestartOnFailure with NO backoff -
#   scan timeouts/crashes were chain-relaunched, piling up 50 instances and exhausting
#   commit memory. Stopgap = kill pileup + unregister ad-hoc task; root fix #1 (single-
#   instance lock) landed in 0b87986a1a (msvcrt non-blocking byte lock, second instance
#   exits immediately). This script = root fix #2: declarative idempotent registration
#   (mirrors register_guard_tasks.ps1; memo 64 section 10.12 "declarative idempotent >
#   manual schtasks"), baking the backoff into the task definition so any re-registration
#   can never again be "manual without backoff".
#
# Backoff semantics (RestartOnFailure): daemon crash (non-zero exit) -> wait 10 minutes
#   before relaunch, at most 3 consecutive restarts - instance creation rate is capped
#   at 6/hour, and every surplus instance is gated out by the app-level lock in ~0.1s,
#   so pileup is mathematically impossible (incident chain: zero backoff = seconds-level
#   chain relaunch). Normal daemon exits (idle self-exit / lock-gate exit = exit 0) do
#   NOT trigger RestartOnFailure; revival falls to the 5min periodic trigger (same as
#   the guard-tier services).
#
# Key design:
#   - Action invokes pythonw.exe directly (GUI subsystem = zero console window; avoids
#     the powershell window flash - the incident's "python window popup storm" came from
#     the ad-hoc task using console-subsystem python.exe). The zephyr package resolves
#     to the main-repo src via editable install, so no PYTHONPATH/activation is needed.
#   - MultipleInstances=Parallel (#ARCH-BOOT-001 lesson): Task Scheduler must NOT make
#     single-instance decisions; the single-instance SSoT is the daemon's byte lock.
#     IgnoreNew would block zombie takeover.
#   - ExecutionTimeLimit=0 (unlimited; the daemon self-exits after 1800s idle).
#   - Idempotent non-destructive: if the task exists, update IN PLACE via
#     Set-ScheduledTask (NEVER Unregister+Register - Unregister kills the running
#     instance; root cause of the silent guard deaths 2026-07-22 23:30-00:48).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_drift_watchdog_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_WorktreeDriftWatchdog /xml | findstr /i "Restart"

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_WorktreeDriftWatchdog"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

# pythonw.exe (GUI subsystem, zero window); zephyr resolves via editable install
$PythonW = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if (-not (Test-Path $PythonW)) { throw "pythonw.exe not found in known locations" }
}

$argString = '-m zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog "' + $RepoRoot + '" --daemon'
$action = New-ScheduledTaskAction -Execute $PythonW -Argument $argString -WorkingDirectory $RepoRoot

# Settings: backoff trio = RestartCount 3 + RestartInterval 10min (#99-2 core) +
#   MultipleInstances Parallel (app-level lock is the single-instance SSoT) +
#   ExecutionTimeLimit 0 (unlimited)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 10)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

# Two triggers (same as guard tier): AtLogOn (no CH dependency => no Delay) + Once(now)
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
$onceTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date)

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($logonTrigger, $onceTrigger) `
        -Settings $settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place (running daemon preserved): $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($logonTrigger, $onceTrigger) `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "Registered drift watchdog task: $TaskName -> pythonw -m worktree_drift_watchdog --daemon"
}

# 5min periodic repeat (PS5.1 New-ScheduledTaskTrigger has no -Repetition param, patch post-registration)
# Registration->query has a sub-second race (Get right after Register sporadically returns null) - retry x3
$task = $null
foreach ($attempt in 1..3) {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $task) { break }
    Start-Sleep -Milliseconds 800
}
if ($null -eq $task) { throw "Task not found after registration: $TaskName" }
foreach ($t in $task.Triggers) { $t.Repetition.Interval = "PT5M" }
$task | Set-ScheduledTask | Out-Null

Write-Host ""
Write-Host "Done. Drift watchdog: AtLogOn + every 5min, RestartCount=3 / RestartInterval=10min (#99 backoff)."
Write-Host "Start now:    schtasks /run /tn $TaskName"
Write-Host "Query status: schtasks /query /tn $TaskName /v /fo LIST"
