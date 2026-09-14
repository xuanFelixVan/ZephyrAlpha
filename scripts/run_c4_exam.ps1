# [BLUEPRINT] MOD-SCRIPT-run_c4_exam | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.run_c4_exam
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_c4_exam | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# run_c4_exam.ps1 - One-shot wrapper for the E4 exam (C4 batch screen over ALL
# translated/ exam files, incl. machine-generated c4_fact_*.py from MOD-BT-159).
# Fired by ZephyrAlpha_C4Exam (weekly Sat 14:00) or manually:
#   powershell -Command "Start-ScheduledTask -TaskName ZephyrAlpha_C4Exam"
# Idempotent: ledger key = (batch, strategy_id, verdict, source_file) - reruns append
# rows only for NEW exam files. Compute-heavy (hours) - weekly window by design.
# Log append-only: .runtime/logs/c4_exam.log

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$logDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "c4_exam.log"

"==== C4 exam fired at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $log -Append -Encoding utf8

python scripts\backtest\c4_batch_screen.py 2>&1 |
  Out-File -FilePath $log -Append -Encoding utf8
"==== exit code $LASTEXITCODE ====" | Out-File -FilePath $log -Append -Encoding utf8
exit $LASTEXITCODE
