# [BLUEPRINT] MOD-L00-004 | scripts/register_guard_tasks.ps1
# [MODULE] scripts.register_guard_tasks
# [DOMAIN] D_DATA
# [TTL] permanent
# register_guard_tasks.ps1 - Register Windows Task Scheduler WATCHDOG tasks for ZephyrAlpha data services
#
# Architecture (watchdog terminates the guard-of-guard chain at OS level):
#   Task Scheduler (OS-hosted, survives user-mode kills)
#     -> guard script (while-true, single-instance lock => idempotent re-entry)
#       -> python business process
#
# Each task: AtLogOn trigger + repeat every 5min indefinitely, interactive user (no admin, no password,
# correct $env:LOCALAPPDATA, same session as QMT/miniQMT terminal). Re-firing while guard is alive is a
# no-op ("Guard already running, exit"); if guard was killed, the next fire revives it (<=5min worst case).
#
# MultipleInstances policy = Parallel (fix #ARCH-BOOT-001 Phase 1, 2026-08-07):
#   Single-instance enforcement has ONE SSoT: the script-level PID lock + heartbeat check in each
#   start_*.ps1 (it can judge health via heartbeat and take over a zombie guard). Task Scheduler is a
#   DUMB periodic launcher here; it must NOT participate in single-instance decisions. IgnoreNew blocks a
#   new guard from launching while a zombie guard (alive but stuck in WaitForExit) holds the slot, which
#   defeats the heartbeat takeover entirely -> this was the exact mechanism of the 08-06/08-07 2-day
#   intraday download outage. Parallel lets the 5min re-fire always launch a new powershell; the new
#   powershell then either exits ("already running, heartbeat fresh") or takes over ("heartbeat stale").
#   register_aux_tasks.ps1 keeps IgnoreNew (one-shot AtLogOn tasks, no while-true guard, no zombie risk).
#
# Idempotent + non-destructive: existing tasks are updated IN PLACE via Set-ScheduledTask.
# NEVER Unregister+Register an existing task - Unregister TERMINATES the running guard instance
# (root cause of silent guard deaths 2026-07-22 23:30-00:48: re-registration killed guards
# 42196/55188 mid-duty; watchdog revived them, but service needlessly bounced).
# INT-03 (2026-08-22, 92 D3 ruling): 5th task ZephyrAlpha_TradingWatchdog is registered in
# DISABLED state - verified no resident trading production process is running today, so an
# enabled watchdog would auto-start a process that is not running (= production behavior
# change). Disabled preserves one-click recovery; enabling is an Owner-window action.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1
# Verify: schtasks /query /tn ZephyrAlpha_DataScheduler & schtasks /query /tn ZephyrAlpha_TickSubscriber

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$services = @(
    @{ TaskName = "ZephyrAlpha_DataScheduler";  Script = "start_scheduler.ps1" },
    @{ TaskName = "ZephyrAlpha_TickSubscriber"; Script = "start_tick_subscriber.ps1" },
    @{ TaskName = "ZephyrAlpha_CHHealthProbe"; Script = "start_ch_health_probe.ps1" },
    # Dead-man switch (#ARCH-BOOT-002 E): one-shot per fire (NOT a while-true guard, no PID lock,
    # no zombie risk). Reads 3 heartbeat files -> alerts if stale >10min. Independent of the 3
    # monitored services. MultipleInstances=Parallel harmless (exits in <1s).
    @{ TaskName = "ZephyrAlpha_DeadmanSwitch"; Script = "deadman_switch.ps1" }
)

# Settings: ExecutionTimeLimit=0 (unlimited; default 3 days would kill the guard every 3 days!)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# Principal: current interactive user (QMT/miniQMT lives in this session; python under user LOCALAPPDATA)
$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

foreach ($svc in $services) {
    $ps1Path = Join-Path $RepoRoot ("scripts\" + $svc.Script)
    if (-not (Test-Path $ps1Path)) { throw "Guard script not found: $ps1Path" }

    $argString = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $ps1Path + '"'
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argString -WorkingDirectory $RepoRoot

    # Two triggers (repetition added post-registration; PS5.1 doesn't expose Repetition
    # on trigger objects from New-ScheduledTaskTrigger):
    #   1) AtLogOn + repeat 5min: delayed start (PT4M) at logon so the ClickHouse VM
    #      (AutomaticStartupDelay=180s) + CH init (~1min) finish first; avoids CH-connect
    #      retry churn in the first ~3min after boot. Heartbeat still anchored to logon event.
    #   2) Once(now) + repeat 5min: heartbeat anchored IMMEDIATELY at registration and persists
    #      across sessions (without this, repetition only activates after the next logon -
    #      verified: LogonTrigger-only registration shows NextRunTime=null until re-logon)
    $logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
    $logonTrigger.Delay = 'PT4M'
    $onceTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date)

    if (Get-ScheduledTask -TaskName $svc.TaskName -ErrorAction SilentlyContinue) {
        # Non-destructive update: Set-ScheduledTask replaces the definition in place and
        # does NOT terminate the running guard instance (Unregister would kill it).
        Set-ScheduledTask -TaskName $svc.TaskName -Action $action -Trigger @($logonTrigger, $onceTrigger) `
            -Settings $settings -Principal $principal | Out-Null
        Write-Host "Updated existing task in place (running guard preserved): $($svc.TaskName)"
    } else {
        Register-ScheduledTask -TaskName $svc.TaskName -Action $action -Trigger @($logonTrigger, $onceTrigger) `
            -Settings $settings -Principal $principal -Force | Out-Null
        Write-Host "Registered watchdog task: $($svc.TaskName) -> $($svc.Script)"
    }

    # Add watchdog heartbeat: repeat every 5min, no Duration => repeats indefinitely
    $task = Get-ScheduledTask -TaskName $svc.TaskName
    foreach ($t in $task.Triggers) { $t.Repetition.Interval = "PT5M" }
    $task | Set-ScheduledTask | Out-Null
}

# --- INT-03 trading watchdog (92 D3 ruling): register in DISABLED state ---
# Same action/triggers/settings as the data-domain guards, so once enabled the 5min re-fire
# + heartbeat-takeover semantics apply unchanged. Idempotent = create-if-absent ONLY: an
# existing task is left completely untouched (never Unregister, never Set) so whatever state
# the Owner has since chosen (including Enabled) is preserved.
$tradingSvc = @{ TaskName = "ZephyrAlpha_TradingWatchdog"; Script = "start_trading.ps1" }
$tradingPs1 = Join-Path $RepoRoot ("scripts\" + $tradingSvc.Script)
if (-not (Test-Path $tradingPs1)) { throw "Guard script not found: $tradingPs1" }

if (Get-ScheduledTask -TaskName $tradingSvc.TaskName -ErrorAction SilentlyContinue) {
    Write-Host "Task already exists, left untouched (idempotent; state preserved): $($tradingSvc.TaskName)"
} else {
    $tradingArg = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $tradingPs1 + '"'
    $tradingAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $tradingArg -WorkingDirectory $RepoRoot
    $tradingLogonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
    $tradingLogonTrigger.Delay = 'PT4M'
    $tradingOnceTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date)
    Register-ScheduledTask -TaskName $tradingSvc.TaskName -Action $tradingAction `
        -Trigger @($tradingLogonTrigger, $tradingOnceTrigger) `
        -Settings $settings -Principal $principal -Force | Out-Null
    # Disable IMMEDIATELY after registration (92 D3): minimizes the enabled window so the
    # Once-trigger can never fire the guard into starting a trading process.
    Disable-ScheduledTask -TaskName $tradingSvc.TaskName | Out-Null
    # Watchdog heartbeat repetition (same as other guards: every 5min, indefinitely).
    # Get-after-Disable => the object carries Enabled=$false; Set preserves the Disabled state.
    $tradingTask = Get-ScheduledTask -TaskName $tradingSvc.TaskName
    foreach ($t in $tradingTask.Triggers) { $t.Repetition.Interval = "PT5M" }
    $tradingTask | Set-ScheduledTask | Out-Null
    Write-Host "Registered watchdog task in DISABLED state (92 D3; enable = Owner window): $($tradingSvc.TaskName) -> $($tradingSvc.Script)"
}

Write-Host ""
Write-Host "Done. Watchdog: AtLogOn + every 5min, user=$CurrentUser, unlimited execution time."
Write-Host "Start now:    schtasks /run /tn ZephyrAlpha_DataScheduler ; schtasks /run /tn ZephyrAlpha_TickSubscriber ; schtasks /run /tn ZephyrAlpha_CHHealthProbe"
Write-Host "Dead-man:     schtasks /run /tn ZephyrAlpha_DeadmanSwitch (auto-fires every 5min, alerts if any heartbeat stale >10min)"
Write-Host "Trading:      REGISTERED DISABLED (92 D3). Enable = Owner window: Enable-ScheduledTask ZephyrAlpha_TradingWatchdog ; schtasks /run /tn ZephyrAlpha_TradingWatchdog"
Write-Host "Query status: schtasks /query /tn <TaskName> /v /fo LIST"
Write-Host "Unregister:   Unregister-ScheduledTask -TaskName <TaskName> -Confirm:`$false"
