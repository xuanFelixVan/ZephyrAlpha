# [BLUEPRINT] MOD-BT-222 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.register_sim_bridge_execute_task
# [DOMAIN] D_BACKTEST
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-register_sim_bridge_execute_task | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_sim_bridge_execute_task.ps1 - Register ZephyrAlpha_SimBridgeExecute
# (st-sim-launch-20260923, sim-launch campaign step-2 power-on persistence).
#
# Fires the wrapper scripts\run_sim_bridge_execute_daily.ps1 at 09:35 and 13:05
# daily (wrapper guards: trading-day + XtItClient liveness; bridge-execute is
# idempotent per day, fail-visible on stale quote, R-H5E-1 gate injected).
# env="sim" ONLY -- the real account path stays Owner-gated (ruling #338-5).
#
# Idempotent non-destructive: Set-ScheduledTask when the task already exists
# (enabled state preserved), Register-ScheduledTask otherwise.
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_sim_bridge_execute_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_SimBridgeExecute /v /fo LIST

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_SimBridgeExecute"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$WrapperPs1 = Join-Path $RepoRoot "scripts\run_sim_bridge_execute_daily.ps1"
if (-not (Test-Path $WrapperPs1)) { throw "Wrapper script not found: $WrapperPs1" }

$argString = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $WrapperPs1 + '"'
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argString -WorkingDirectory $RepoRoot

# Settings: short one-shot (runner subprocess self-bounded ~90s + ack wait);
# StartWhenAvailable (missed fire, e.g. host busy at 09:35, runs when free).
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

# Triggers: 09:35 and 13:05 daily (inside the intraday test windows; the
# wrapper's trading-day guard makes weekends a no-op).
$trigger1 = New-ScheduledTaskTrigger -Daily -At "09:35"
$trigger2 = New-ScheduledTaskTrigger -Daily -At "13:05"

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($trigger1, $trigger2) `
        -Settings $settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place (state preserved): $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($trigger1, $trigger2) `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "Registered task: $TaskName (triggers 09:35 + 13:05 daily)"
}
Write-Host "Verify: schtasks /query /tn $TaskName /v /fo LIST"
