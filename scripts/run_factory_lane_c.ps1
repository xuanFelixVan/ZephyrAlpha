# [BLUEPRINT] MOD-SCRIPT-run_factory_lane_c | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.run_factory_lane_c
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_factory_lane_c | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# run_factory_lane_c.ps1 - One-shot wrapper for FAC-E1C formula mining (gplearn track).
# Fired by Task Scheduler ZephyrAlpha_FactoryLaneC (weekly Sat 10:00) or manually via
#   schtasks /run /tn ZephyrAlpha_FactoryLaneC
# Discipline lives INSIDE the job: lane_c_formula_miner consults the E0 compute gate
# (trade_calendar, heavy only after close / non-trading days) and whitelist status.
# Log append-only: .runtime/logs/factory_lane_c.log (map FAC-E0 store_refs convention).

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$logDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "factory_lane_c.log"

"==== FAC-E1C mine fired at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $log -Append -Encoding utf8

# Production defaults live in config/factor_mining_whitelist.yaml (pop 1000 x 50, seed 42).
python scripts\backtest\lane_c_formula_miner.py mine --top 10 2>&1 |
  Out-File -FilePath $log -Append -Encoding utf8
"==== exit code $LASTEXITCODE ====" | Out-File -FilePath $log -Append -Encoding utf8
exit $LASTEXITCODE
