# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] scripts.start_paper_session_daily
# [DOMAIN] D_EX_CORE
# [A_module] module_id=MOD-SCRIPT-start_paper_session_daily | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# start_paper_session_daily.ps1 - ZephyrAlpha_PaperSession wrapper
# (A6 ; scripts/register_paper_session_task.ps1 , run_post_settlement_daily.ps1 )
#
# (one-shot per fire, while-true PID -- Daily 09:25 +
# LiveStrategyAdapter ):
# 1. is_trading_day (XSHG , zephyr.data.trading_calendar): exit 0
# (run_post_settlement.py --if-trading-day PowerShell ).
# 2. xtMiniQmt.exe : -> + exit 0 ( SKIP, crash-loop).
# QMT (P0-1 ), exit 1; 09:25 .
# 3. QMT -> python scripts/start_paper_session.py --service, stdout/stderr
# .runtime/logs/paper_session.log (run_post_settlement_daily.ps1 ).
#
# Exit codes: 0= ( SKIP / QMT SKIP / --service ),
# 0=python --service exit 1 (//) 2 ()--.
#
# Deploy: scripts/register_paper_session_task.ps1 ( DISABLED, 92 D3 ).
# Manual dry-run: powershell -ExecutionPolicy Bypass -File scripts\start_paper_session_daily.ps1

$ErrorActionPreference = "Stop"
Set-Location D:\ZephyrAlpha

$RepoRoot = "D:\ZephyrAlpha"
$LogDir = Join-Path $RepoRoot ".runtime\logs"
$LogFile = Join-Path $LogDir "paper_session.log"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-PaperLog {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts $Message" | Out-File -FilePath $LogFile -Append -Encoding utf8
}

$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }
}

# 1. is_trading_day (XSHG ; exit 0 )
$isTradingDay = & $PythonExe -c "import sys;sys.path.insert(0,'src');from zephyr.data.trading_calendar import is_trading_day;print(is_trading_day())" 2>&1
if ($LASTEXITCODE -ne 0) {
 # =fail-closed SKIP ()
    Write-PaperLog "SKIP: is_trading_day  (exit=$LASTEXITCODE): $isTradingDay -- "
    exit 0
}
if (($isTradingDay | Out-String).Trim() -ne "True") {
    Write-PaperLog "SKIP:  (is_trading_day=False)"
    exit 0
}

# 2. xtMiniQmt.exe (QMT , = SKIP crash-loop)
$qmt = Get-Process -Name "XtMiniQmt" -ErrorAction SilentlyContinue
if (-not $qmt) {
    Write-PaperLog "SKIP: XtMiniQmt  (57  1 C1=Owner ) -- ,  09:25 "
    exit 0
}
Write-PaperLog "QMT  (PID=$($qmt.Id -join ','))-- --service "

# 3. : LiveStrategyAdapter (biz tmp/live_strategy_biz.heartbeat)
& $PythonExe scripts\start_paper_session.py --service *>> $LogFile
$code = $LASTEXITCODE
Write-PaperLog "start_paper_session --service exited: exit_code=$code (0=, 1=//, 2=)"
exit $code
