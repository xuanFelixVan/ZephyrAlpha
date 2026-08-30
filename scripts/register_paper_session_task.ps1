# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] scripts.register_paper_session_task
# [DOMAIN] D_EX_CORE
# [A_module] module_id=MOD-SCRIPT-register_paper_session_task | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_paper_session_task.ps1 - Register the ZephyrAlpha_PaperSession Task Scheduler task
# (A6 : 57 GAP-2 , tracker #273)
#
# Background (57 2/7 GAP-2 + 92 D3 ):
# start_paper_session.py --service (LiveStrategyAdapter , biz
# tmp/live_strategy_biz.heartbeat) " 09:25 ".
# Task Scheduler: 09:25 LiveStrategyAdapter
# . 92 D3 (ZephyrAlpha_TradingWatchdog ):
# ** DISABLED**--, enabled Owner
# (=).Disabled , =Owner :
# Enable-ScheduledTask ZephyrAlpha_PaperSession ; schtasks /run /tn ZephyrAlpha_PaperSession
#
# Wrapper semantics (scripts/start_paper_session_daily.ps1, one-shot per fire):
# 1. --if-trading-day : zephyr.data.trading_calendar.is_trading_day (XSHG ,
# /), exit 0 (, run_post_settlement.py --if-trading-day
# --54 ).
# 2. QMT : xtMiniQmt.exe -> + exit 0 ( SKIP).
# : QMT (P0-1 , 57 1 C1=Owner ),
# xtMiniQmt python --service crash-loop ;
# exit 0 + ExecutionTimeLimit=0 + RestartOnFailure = ,
# 09:25 ( crash-loop ).
# 3. QMT -> python scripts/start_paper_session.py --service, stdout/stderr
# .runtime/logs/paper_session.log (run_post_settlement_daily.ps1 ).
# LiveStrategyAdapter ( 3 EXHAUSTED) ;
# biz tmp/live_strategy_biz.heartbeat deadman_switch ().
#
# Key design:
# - python.exe (console subsystem) via wrapper .ps1 with *>> log redirect
# (run_post_settlement_daily.ps1 )-- pythonw.exe
# stdout/stderr ( 09:25-15:05 ), pythonw
# ; action -WindowStyle Hidden .
# - Trigger: Daily 09:25 (NOT AtLogOn)--; wrapper
# is_trading_day (Task Scheduler ).AtLogOn :
# ( 08:00 10:00), 09:25 .
# PT5M = StartWhenAvailable: / 09:25 ,
# (09:30 09:30 , ).
# - ExecutionTimeLimit=0 (unlimited): 09:25-15:05 (~5.7h) 3
# , 3 ----service
# (close_at 15:05 stop), OS .
# - No RestartOnFailure: exit 0 ( SKIP / QMT SKIP) exit 1 (/
# ) -- 09:25 ( #99 :
# ).
# - MultipleInstances=Parallel (#ARCH-BOOT-001 ): Task Scheduler ,
# ; start_paper_session --service LiveStrategyAdapter
# + QMT broker , Daily 09:25 + StartWhenAvailable
# 0 ().
# - Idempotent non-destructive: Set-ScheduledTask
# Enabled/Disabled (92 D3 : Owner ,
# Disabled); Disable (Register Once-free,
# 09:25, Disable ).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_paper_session_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_PaperSession /v /fo LIST
# Dry-run (Owner ): powershell -ExecutionPolicy Bypass -File scripts\start_paper_session_daily.ps1

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_PaperSession"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$WrapperPs1 = Join-Path $RepoRoot "scripts\start_paper_session_daily.ps1"
if (-not (Test-Path $WrapperPs1)) { throw "Wrapper script not found: $WrapperPs1" }

# Wrapper powershell (console subsystem + -WindowStyle Hidden; wrapper *>>)
$argString = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $WrapperPs1 + '"'
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argString -WorkingDirectory $RepoRoot

# Settings: Parallel () + ExecutionTimeLimit 0 ( 09:25-15:05,
# --service close_at ) + StartWhenAvailable (PT5M :
# 09:25 ). RestartOnFailure ( #99: 09:25 )
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances Parallel `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

# Trigger: Daily 09:25 ( wrapper is_trading_day ; exit 0)
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At "09:25"

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
 # : Enabled/Disabled (92 D3: Owner )
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($dailyTrigger) `
        -Settings $settings -Principal $principal | Out-Null
    Write-Host "Updated existing task in place (state preserved): $TaskName"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($dailyTrigger) `
        -Settings $settings -Principal $principal -Force | Out-Null
 # DISABLED (92 D3 ): 09:25, Register Once ,
 # Disable =
    Disable-ScheduledTask -TaskName $TaskName | Out-Null
    Write-Host "Registered paper session task in DISABLED state (92 D3 precedent; enable = Owner window): $TaskName"
}

Write-Host ""
Write-Host "Done. PaperSession: Daily 09:25 + StartWhenAvailable (PT5M ), wrapper=is_trading_day +xtMiniQmt ,  DISABLED."
Write-Host "Enable (Owner window): Enable-ScheduledTask $TaskName ; schtasks /run /tn $TaskName"
Write-Host "Dry-run wrapper now:   powershell -ExecutionPolicy Bypass -File scripts\start_paper_session_daily.ps1"
Write-Host "Query status:          schtasks /query /tn $TaskName /v /fo LIST"
Write-Host "Logs:                  .runtime\logs\paper_session.log"
Write-Host "Biz heartbeat (deadman 4th path): tmp\live_strategy_biz.heartbeat"
