# [BLUEPRINT] MOD-SCRIPT-run_kronos_scoring | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.run_kronos_scoring
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_kronos_scoring | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# run_kronos_scoring.ps1 - Night batch: Kronos forward scoring into c1_market.kronos_prediction_daily.
# Fired by Task Scheduler ZephyrAlpha_KronosScoring (00:30 Sun-Thu) or manually:
#   schtasks /run /tn ZephyrAlpha_KronosScoring
#
# Work order GPU-02 (docs/_working/automation/20260917_wo_gpu02_kronos_batch_scoring.md).
#
# Window arithmetic that this wrapper enforces (and why it is small):
#   The order asks for a 00:30 start AND the shift constitution asks for ZERO batch activity and
#   ZERO ClickHouse queries inside the 01:00-04:00 CH yield window. A 00:30 start therefore has
#   at most 25 minutes of usable runtime (5 min safety margin before 01:00). We pass that cap to
#   the adapter (--max-runtime-min) so the run stops itself and reports yield_window_hit=true
#   instead of silently overrunning into the protected window. Scoring the whole ~5000-symbol
#   universe inside 25 minutes is NOT achievable; the shortfall is reported to coordination
#   (see docs/_working/gpuwo_campaign/) rather than hidden by a green exit.
#
# Consumption discipline: predictions land and are NOT wired to any signal face. Making
# src/zephyr/signal_ashare/ml_forecast/kronos_tsfm_predictor.py consume this table requires B-007
# human approval, which this shift does not grant itself.
#
# rc discipline (mirrors run_factory_lane_c.ps1:15-18): exit code captured and checked; a failure
#   logs "==== <seg> FAILED rc=N ====", raises an Alerter ERROR and exits with that rc.
# PS5.1 landmine: python stderr goes through cmd.exe redirection, never through Out-File.
# Log append-only: .runtime/logs/kronos_scoring.log

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$logDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "kronos_scoring.log"

# Default universe: top 300 by turnover. The full universe is deliberately NOT the default until
# coordination resolves the window arithmetic above; raise it with --top-n here or KRONOS_TOP_N.
$TopN = if ($env:KRONOS_TOP_N) { $env:KRONOS_TOP_N } else { 300 }
$MaxRuntimeMin = if ($env:KRONOS_MAX_RUNTIME_MIN) { $env:KRONOS_MAX_RUNTIME_MIN } else { 25 }
$SampleCount = if ($env:KRONOS_SAMPLE_COUNT) { $env:KRONOS_SAMPLE_COUNT } else { 8 }

# Sharding (coordination ruling R-3, 2026-10-11): one shard per night, four nights per round.
# Scoring the whole universe inside 25 minutes is arithmetically impossible, so the runner takes
# a positional slice instead of pretending a truncated night is a complete one. Index rotates on
# day-of-year modulo shard count, so a 5-night Sun-Thu schedule simply starts the next round again
# - repeating a shard costs nothing (ReplacingMergeTree keyed by date+symbol) and skips none.
$ShardCount = if ($env:KRONOS_SHARD_COUNT) { [int]$env:KRONOS_SHARD_COUNT } else { 4 }
if ($env:KRONOS_SHARD_INDEX -ne $null -and $env:KRONOS_SHARD_INDEX -ne "") {
    $ShardIndex = [int]$env:KRONOS_SHARD_INDEX
} else {
    $ShardIndex = (Get-Date).DayOfYear % $ShardCount
}

"==== Kronos scoring fired at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') (top_n=$TopN shard=$ShardIndex/$ShardCount cap=${MaxRuntimeMin}m) ====" | Out-File -FilePath $log -Append -Encoding utf8

$now = Get-Date
if ($now.Hour -ge 1 -and $now.Hour -lt 4) {
    "==== SKIPPED: inside 01:00-04:00 ClickHouse yield window (no batch, no CH query) ====" | Out-File -FilePath $log -Append -Encoding utf8
    exit 0
}

cmd.exe /c "python scripts\backtest\kronos_adapter.py --score-only --top-n $TopN --sample-count $SampleCount --max-runtime-min $MaxRuntimeMin --shard-count $ShardCount --shard-index $ShardIndex --flush-every 100 >> $log 2>&1"
$scoreExit = $LASTEXITCODE
"==== score-only exit code $scoreExit (shard $ShardIndex of $ShardCount) ====" | Out-File -FilePath $log -Append -Encoding utf8
if ($scoreExit -ne 0) {
    # rc semantics from the adapter: 1=hard failure (empty universe / write failure / zero rows),
    # 3=shard finished but some symbols failed, 4=yield cap cut the shard short (coverage partial).
    # All three leave the table with fewer rows than a round promises, so none may be logged green.
    "==== score-only NOT GREEN rc=$scoreExit ====" | Out-File -FilePath $log -Append -Encoding utf8
    cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('kronos_scoring', 'scoring shard $ShardIndex/$ShardCount NOT green rc=$scoreExit (partial or failed, see log)', 'ERROR')"" >> $log 2>&1"
    exit $scoreExit
}

"==== Kronos scoring shard $ShardIndex/$ShardCount green (rows landed in c1_market.kronos_prediction_daily, still unconsumed) ====" | Out-File -FilePath $log -Append -Encoding utf8
cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('kronos_scoring', 'scoring shard $ShardIndex/$ShardCount green, predictions stored unconsumed', 'INFO')"" >> $log 2>&1"
"==== exit code 0 ====" | Out-File -FilePath $log -Append -Encoding utf8
exit 0

