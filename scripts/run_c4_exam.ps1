# [BLUEPRINT] MOD-SCRIPT-run_c4_exam | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.run_c4_exam
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_c4_exam | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# run_c4_exam.ps1 - One-shot wrapper for the E4 exam (C4 batch screen), two-stage:
#   Stage 1 (IS):  --auto-only      incremental batch over translated/ exam files NOT yet
#                                   in the frozen IS ledger (skips re-testing known files).
#   Stage 2 (OOS): --auto-oos-pending  re-test strategies that ARE in the IS ledger but
#                                   still lack an oos_tested row (S06-G1: keeps the
#                                   bothwin eligible set non-empty so intake can promote).
#   c4_batch_completed is emitted ONLY by Stage 2 (Stage 1 passes --defer-emit), because
#   intake consumes the event and requires BOTH windows landed per strategy.
# Fired by ZephyrAlpha_C4Exam (weekly Sat 14:00) or manually:
#   powershell -Command "Start-ScheduledTask -TaskName ZephyrAlpha_C4Exam"
# Idempotent: ledger key = (batch, strategy_id, verdict, source_file) - reruns append
# rows only for NEW/pending items. Compute-heavy (hours) - weekly window by design.
# Log append-only: .runtime/logs/c4_exam.log

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$logDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "c4_exam.log"

"==== C4 exam fired at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $log -Append -Encoding utf8

# ---- Stage 1: IS incremental batch (auto-only; emit deferred to Stage 2) ----
python scripts\backtest\c4_batch_screen.py --auto-only --defer-emit 2>&1 |
  Out-File -FilePath $log -Append -Encoding utf8
$isExit = $LASTEXITCODE
"==== IS batch exit code $isExit ====" | Out-File -FilePath $log -Append -Encoding utf8
if ($isExit -ne 0) {
  "==== OOS batch SKIPPED (IS batch failed - short circuit) ====" | Out-File -FilePath $log -Append -Encoding utf8
  exit $isExit
}

# ---- Stage 2: auto OOS batch (pending = IS-landed minus oos_tested); emits the event ----
python scripts\backtest\c4_batch_screen.py --auto-oos-pending 2>&1 |
  Out-File -FilePath $log -Append -Encoding utf8
$oosExit = $LASTEXITCODE
"==== OOS batch exit code $oosExit ====" | Out-File -FilePath $log -Append -Encoding utf8
exit $oosExit
