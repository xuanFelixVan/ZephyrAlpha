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

# PS5.1 landmine (see run_factory_lane_c.ps1 2026-09-15 note): under ErrorActionPreference=Stop
# a stderr line from a STILL-RUNNING native child becomes a terminating NativeCommandError;
# the pipeline stops, PS kills the child and exits 1 with zero log output. 2026-10-09 W1
# root cause (st-examchief-20261009 trap trace): the `*>>` form here is the SAME landmine
# (pandas FutureWarning at first eval killed every window since 09-19); fix mirrors the
# cmd.exe /c native-redirect pattern proven daily by run_factory_lane_c.ps1 / run_c4_exam.ps1.
# Sequential: batch A census-extend (focus stratify) then batch B subspace enumerate.
cmd.exe /c "python scripts\backtest\factory_grid_executor.py --n-samples 6000 --seed 20260916 --stratify-dims G_universe,A1_factor_normalize,B_top_n >> $log 2>&1"
"batch A exit=$LASTEXITCODE" | Out-File -FilePath $log -Append -Encoding utf8

# batch B JSON: PS single-quoted literal keeps `\"` verbatim through cmd to python argv
# (2026-10-09 quoting probe: doubled-quote form arrives quote-stripped and breaks json.loads).
$batchBJson = '{\"D1_rebalance_freq\":[\"weekly\"],\"E_single_cap\":[\"cap10\"],\"D2_rebalance_trigger\":[\"periodic\"],\"G_universe\":[\"hs300\",\"zz500\"]}'
cmd.exe /c ('python scripts\backtest\factory_grid_executor.py --n-samples 99999 --seed 20260916 --subspace-json ' + $batchBJson + ' >> "' + $log + '" 2>&1')
"batch B exit=$LASTEXITCODE" | Out-File -FilePath $log -Append -Encoding utf8

"==== F06 grid pipeline done at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $log -Append -Encoding utf8
