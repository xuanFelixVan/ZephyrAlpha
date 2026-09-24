# [BLUEPRINT] MOD-BT-222 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.run_sim_bridge_execute_daily
# [DOMAIN] D_BACKTEST
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_sim_bridge_execute_daily | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# run_sim_bridge_execute_daily.ps1 - wrapper for the ZephyrAlpha_SimBridgeExecute
# scheduled task (st-sim-launch-20260923).
#
# One-shot per fire (09:35 / 13:05 Mon-Fri, inside the intraday test windows):
#   1. is_trading_day (XSHG calendar, zephyr.data.trading_calendar): non-trading
#      day or calendar failure -> exit 0 SKIP (fail-closed skip, no order).
#   2. XtItClient liveness: terminal not running -> exit 0 SKIP. Writing order
#      instruction files into a dead bridge would leave them unprocessed (the
#      ruling #339 gap-2 overnight-drop surface); skip is the mitigation.
#   3. python scripts/backtest/sim_daily_runner.py bridge-execute --day <today>.
#      PS 5.1 stderr trap (FIX-3 v2 lesson, 2026-09-22): route through cmd /c
#      with cmd-native redirection so PowerShell never sees the stderr stream.
#
# Idempotency/safety is enforced inside bridge-execute itself: plan posture
# mapping per Owner-ruled decision card, limit price from the live bridge quote
# (stale quote -> no order), signal_batch=plan-bridge-<day> + orders_sim.csv
# idem-key pre-check (same-day rerun cannot double-order), R-H5E-1 pre-trade
# gate injected (ruling #338-5), env="sim" ONLY (real account = Owner gate).
#
# Exit codes: 0 = ok or SKIP; 1 = runner/bridge failure (logged).
#
# Deploy: powershell -ExecutionPolicy Bypass -File scripts\register_sim_bridge_execute_task.ps1
# Manual dry-run: powershell -ExecutionPolicy Bypass -File scripts\run_sim_bridge_execute_daily.ps1

$ErrorActionPreference = "Stop"
Set-Location D:\ZephyrAlpha

$RepoRoot = "D:\ZephyrAlpha"
$LogDir = Join-Path $RepoRoot ".runtime\logs"
$LogFile = Join-Path $LogDir "sim_bridge_execute.log"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-SimLog {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts $Message" | Out-File -FilePath $LogFile -Append -Encoding utf8
}

$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }
}

# 1. is_trading_day (XSHG calendar; failure = fail-closed SKIP)
$isTradingDay = & $PythonExe -c "import sys;sys.path.append('src');from zephyr.data.trading_calendar import is_trading_day;print(is_trading_day())" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-SimLog "SKIP: is_trading_day check failed (exit=$LASTEXITCODE): $isTradingDay"
    exit 0
}
if (($isTradingDay | Out-String).Trim() -ne "True") {
    Write-SimLog "SKIP: non-trading day (is_trading_day=False)"
    exit 0
}

# 2. XtItClient liveness (dead bridge -> instruction files would sit unprocessed)
$qmt = Get-Process -Name "XtItClient" -ErrorAction SilentlyContinue
if (-not $qmt) {
    Write-SimLog "SKIP: XtItClient not running -- bridge terminal offline, no order file written"
    exit 0
}

# 3. bridge-execute via cmd /c native redirection (PS 5.1 stderr trap, FIX-3 v2)
$today = Get-Date -Format "yyyy-MM-dd"
$ErrorActionPreference = "Continue"
cmd /c "`"$PythonExe`" scripts\backtest\sim_daily_runner.py bridge-execute --day $today >> `"$LogFile`" 2>&1"
$code = $LASTEXITCODE
$ErrorActionPreference = "Stop"
Write-SimLog "bridge-execute day=$today exited: exit_code=$code (0=ok or honest no-order row)"
exit $code
