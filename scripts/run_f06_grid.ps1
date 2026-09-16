# [BLUEPRINT] MOD-SCRIPT-run_f06_grid | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.run_f06_grid
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_f06_grid | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# run_f06_grid.ps1 - One-shot wrapper for F-06 grid batch pipeline (weekly window).
# Fired by Task Scheduler ZephyrAlpha_F06Grid (weekly Sat 14:00, after LaneC 10:00) or
#   manually via: schtasks /run /tn ZephyrAlpha_F06Grid
# Discipline lives INSIDE the pipeline: factory_grid_executor consults data availability
# per batch; N ledger auto-registration happens at summary time (MOD-BT-200).
# Log append-only: .runtime/logs/f06_grid.log

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$logDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "f06_grid.log"

"==== F06 grid pipeline fired at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $log -Append -Encoding utf8

# PS5.1 landmine (see run_factory_lane_c.ps1 2026-09-15 note): do NOT pipe python stderr
# through Out-File under ErrorActionPreference=Stop (any stderr line becomes ErrorRecord).
# Sequential: batch A census-extend (focus stratify) then batch B subspace enumerate.
$py = "python"
& $py scripts\backtest\factory_grid_executor.py --n-samples 6000 --seed 20260916 --stratify-dims G_universe,A1_factor_normalize,B_top_n *>> $log
"batch A exit=$LASTEXITCODE" | Out-File -FilePath $log -Append -Encoding utf8

& $py scripts\backtest\factory_grid_executor.py --n-samples 99999 --seed 20260916 --subspace-json "{\"D1_rebalance_freq\":[\"weekly\"],\"E_single_cap\":[\"cap10\"],\"D2_rebalance_trigger\":[\"periodic\"],\"G_universe\":[\"hs300\",\"zz500\"]}" *>> $log
"batch B exit=$LASTEXITCODE" | Out-File -FilePath $log -Append -Encoding utf8

"==== F06 grid pipeline done at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $log -Append -Encoding utf8
