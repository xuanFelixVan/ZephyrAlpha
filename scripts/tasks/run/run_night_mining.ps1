# [ARTIFACTS] outputs per SOP automation_sop/research_production_line_policy.md #8-A (2026-10-15):
# [TTL] permanent
# [COMPLETES_WHEN] n/a - permanent runner; retire only via ruling + deregistration
#   candidates -> data/strategy_intake/lane_b_candidates.csv + lane_c3_candidates.csv (process layer, append-only)
#   run log    -> .runtime/logs/night_mining.log (non-asset)
# [BLUEPRINT] MOD-SCRIPT-run_night_mining | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.run_night_mining
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_night_mining | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# run_night_mining.ps1 - Night-window hypothesis mining batch (lane B ideas + MCTS expressions).
# Fired by Task Scheduler ZephyrAlpha_NightMining (23:00 Sun-Thu) or manually:
#   schtasks /run /tn ZephyrAlpha_NightMining
#
# Work order GPU-01 (docs/_working/automation/20260917_wo_gpu01_night_mining_ollama.md).
#
# Backlog discipline (the order's rule: night output enters the intake backlog, never auto-enrolled):
#   - lane_b_idea_generator.py generate  appends data/strategy_intake/lane_b_candidates.csv (CAS)
#   - mcts_expression_search.py          appends data/strategy_intake/lane_c3_candidates.csv
#   This wrapper deliberately does NOT call factory_intake_pipeline.py run/construct nor
#   hypothesis_translator.py, because those are the enrolment/promotion legs (E2 precheck verdict
#   ledger + exam-file generation). Night output stays in the backlog until a human/next leg picks it.
#
# Pre-flight that the 09-17 order did not have but the 10-08 incident proved necessary:
#   LaneC's night run 2026-10-08 exited 0 and logged "full chain rc all green" while EVERY
#   candidate came back refusal_reason=llm_error:ConnectionError - i.e. Ollama was down and the
#   LLM leg produced nothing, silently. Here the service AND the requested model tag are checked
#   before any work; if either is missing the wrapper raises an Alerter ERROR and exits non-zero.
#   Never trust an all-green banner over a zero-output measurement.
#
# Window discipline: refuses to start inside 01:00-04:00 (ClickHouse yield window; lane_b seeds
#   and mcts inputs are read from CH).
# rc discipline (mirrors run_factory_lane_c.ps1:15-18): each segment rc captured and checked,
#   failure logs "==== <seg> FAILED rc=N ====", alerts, short-circuits, exits with that rc.
# PS5.1 landmine: python stderr via cmd.exe redirection, never Out-File.
# Log append-only: .runtime/logs/night_mining.log
# Model tier: override with $env:NIGHT_MINING_MODEL (default qwen3:8b = current production tier).

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$Model = if ($env:NIGHT_MINING_MODEL) { $env:NIGHT_MINING_MODEL } else { "qwen3:8b" }
$MctsIterations = if ($env:NIGHT_MINING_MCTS_ITER) { $env:NIGHT_MINING_MCTS_ITER } else { 40 }
$NPerTheme = if ($env:NIGHT_MINING_PER_THEME) { $env:NIGHT_MINING_PER_THEME } else { 2 }
$OllamaUrl = if ($env:OLLAMA_BASE_URL) { $env:OLLAMA_BASE_URL } else { "http://localhost:11434" }

$logDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "night_mining.log"

function Write-Log([string]$Line) { $Line | Out-File -FilePath $log -Append -Encoding utf8 }

Write-Log "==== night mining fired at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') model=$Model mcts_iter=$MctsIterations ===="

$now = Get-Date
if ($now.Hour -ge 1 -and $now.Hour -lt 4) {
    Write-Log "==== SKIPPED: inside 01:00-04:00 ClickHouse yield window ===="
    exit 0
}

# Pre-flight 1: service reachable + requested model tag present.
try {
    $tags = Invoke-RestMethod -Uri "$($OllamaUrl.TrimEnd('/'))/api/tags" -TimeoutSec 5
    $names = @($tags.models | ForEach-Object { $_.name })
    if ($names -notcontains $Model) {
        Write-Log "==== PRE-FLIGHT FAILED: model '$Model' not in Ollama roster (seen: $($names -join ',')) ===="
        cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('night_mining', 'model tag missing: $Model', 'ERROR')"" >> $log 2>&1"
        exit 1
    }
    Write-Log "==== preflight ok: Ollama reachable, model '$Model' present ===="
} catch {
    Write-Log "==== PRE-FLIGHT FAILED: Ollama unreachable at $OllamaUrl ($($_.Exception.Message)) - zero mining done ===="
    cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('night_mining', 'Ollama unreachable, batch aborted before any call', 'ERROR')"" >> $log 2>&1"
    exit 1
}

# Segment 1: lane B ideas (writes backlog CSV only; no enrolment).
cmd.exe /c "python scripts\backtest\lane_b_idea_generator.py generate --n-per-theme $NPerTheme --model $Model >> $log 2>&1"
$laneBExit = $LASTEXITCODE
Write-Log "==== lane_b exit code $laneBExit ===="
if ($laneBExit -ne 0) {
    Write-Log "==== lane_b FAILED rc=$laneBExit - mcts SKIPPED (short circuit) ===="
    cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('night_mining', 'lane_b FAILED rc=$laneBExit', 'ERROR')"" >> $log 2>&1"
    exit $laneBExit
}

# Segment 2: MCTS expression search (zero LLM, deterministic-ish breadth leg).
cmd.exe /c "python scripts\backtest\mcts_expression_search.py --iterations $MctsIterations >> $log 2>&1"
$mctsExit = $LASTEXITCODE
Write-Log "==== mcts exit code $mctsExit ===="
if ($mctsExit -ne 0) {
    Write-Log "==== mcts FAILED rc=$mctsExit ===="
    cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('night_mining', 'mcts FAILED rc=$mctsExit', 'ERROR')"" >> $log 2>&1"
    exit $mctsExit
}

Write-Log "==== night mining window green (backlog only, nothing auto-enrolled) ===="
cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('night_mining', 'night mining green into backlog', 'INFO')"" >> $log 2>&1"
Write-Log "==== exit code 0 ===="
exit 0
