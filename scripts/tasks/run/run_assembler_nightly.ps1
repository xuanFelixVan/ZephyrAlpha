# [BLUEPRINT] MOD-SCRIPT-run_assembler_nightly | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.run_assembler_nightly
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_assembler_nightly | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [COMPLETES_WHEN] n-a (thin wrapper; completion = ibt_runner exit code recorded in the log)
# [ARTIFACTS] scores -> docs/04_research_records/backtest/scores/<YYYY>/ (only-add); ledger -> docs/_working/automation_campaign/p11_assembler/ledger.md; logs -> .runtime/logs/
#
# run_assembler_nightly.ps1 - thin nightly wrapper for the IBT assembler run (21:30 nightly
#   semantics). Task Scheduler registration is OWNED BY the scheduling lane - this file is the
#   job body only, NO scheduled task is registered here (st-ibtclose-20261015 item 2).
#
# Scope discipline (protocol v1.1 / IBT-PROTOCOL-V1):
#   - runs ONLY --window W_POSTD with the pool bridge config\ibt_pool_bridge.yaml
#   - W_HOLDOUT stays untouched by this wrapper (single-burn discipline, protocol section 3;
#     touching it requires an explicit --holdout-guard run which this wrapper must never do)
#   - window/cost parameters stay frozen in ibt_runner.py constants; the pool bridge changes
#     pool membership only
#
# rc discipline: the python segment's exit code is captured and logged; the wrapper exits
#   with that rc so the scheduler's LastTaskResult reflects reality (no fake green).
#
# Pure ASCII file: PowerShell 5.1 decodes no-BOM files as GBK; non-ASCII comments cause
#   fake syntax errors (root constitution section 9.7).

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$logDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "assembler_nightly.log"

function Write-Log([string]$Line) {
    $Line | Out-File -FilePath $log -Append -Encoding utf8
}

$RunId = Get-Date -Format "yyyyMMdd-HHmmss"
Write-Log "==== IBT assembler nightly fired at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') run_id=$RunId ===="

# cmd shell redirection keeps stderr as raw bytes into the log (PS5.1 landmine, see
# run_factory_lane_c.ps1: ErrorActionPreference=Stop turns any stderr line into an ErrorRecord).
cmd.exe /c "python scripts\backtest\ibt\ibt_runner.py --window W_POSTD --pool-file config\ibt_pool_bridge.yaml >> $log 2>&1"
$rc = $LASTEXITCODE
Write-Log "==== ibt_runner exit code $rc ===="

if ($rc -ne 0) {
    Write-Log "==== assembler nightly FAILED rc=$rc (W_POSTD run did not complete clean) ===="
} else {
    Write-Log "==== assembler nightly all green (W_POSTD done; W_HOLDOUT untouched) ===="
}

Write-Log "==== exit code $rc ===="
exit $rc
