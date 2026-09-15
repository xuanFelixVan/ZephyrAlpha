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
# PS5.1 landmine fix (2026-09-15, MOD-SCRIPT-run_factory_lane_c): `$ErrorActionPreference
# = "Stop"` + `python ... 2>&1 | Out-File` turns ANY stderr line into an ErrorRecord
# that kills the script (09-15 15:35 first run died after the fired line, LastResult=1).
# cmd shell redirection keeps stderr as raw bytes into the log - no ErrorRecord.
cmd.exe /c "python scripts\backtest\lane_c_formula_miner.py mine --top 10 >> $log 2>&1"

# Full supply chain (Owner 2026-09-15 full-automation mandate): intake all lanes ->
# E2 precheck all four -> E2->E3 auto-construct -> C3 translation (formula subset).
cmd.exe /c "python scripts\backtest\factory_intake_pipeline.py run --with-lane-b --limit-precheck 15 >> $log 2>&1"
cmd.exe /c "python scripts\backtest\factory_intake_pipeline.py construct >> $log 2>&1"
cmd.exe /c "python scripts\backtest\hypothesis_translator.py translate --seeds 5 >> $log 2>&1"

# Worktree application-system weekly audit (policy parallel_session_coordination v1.1.0 s10).
$count = (git log --format=%B --since="7 days ago" | Select-String "non-worktree").Count
"==== worktree audit: non-worktree commits last 7d = $count ====" | Out-File -FilePath $log -Append -Encoding utf8

"==== exit code $LASTEXITCODE ====" | Out-File -FilePath $log -Append -Encoding utf8
exit $LASTEXITCODE
