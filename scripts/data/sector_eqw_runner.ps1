# Sector board minute bars producer runner (internal_eqw convergence producer).
# st-storageswap-20260930 2026-10-01: convergence ruling A (a7 sector_switch
# validation SS6) - this task is the single producer for
# c1_market.kline_sector_intraday after the tdx refusal (09-10) and the J-leg
# dry-run downgrade (sector_synth_eod_runner.ps1). Daily 15:40 slot (after
# kline_1min close ~15:05, before J's 15:50 dry-run slot). Non-trading days
# self-noop (producer exits 0 with no write when kline_1min has no bars).
# Truth protection built in (dates holding data_source='tdx' rows refuse
# without --force). Idempotent: delete_where non-tdx rows of the date, then
# ReplacingMergeTree same-key overwrite.
$ErrorActionPreference = 'Continue'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $python)) { $python = 'python' }
$runner = Join-Path $repoRoot 'scripts\kline_sector_intraday_from_constituents.py'
$logFile = Join-Path $repoRoot 'logs\sector_eqw_intraday.log'
$today = Get-Date -Format 'yyyyMMdd'
Set-Location -LiteralPath $repoRoot
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] START trade-date=$today" | Add-Content -LiteralPath $logFile
& $python -X utf8 $runner --date $today 2>&1 | Tee-Object -Variable out | Add-Content -LiteralPath $logFile
$code = $LASTEXITCODE
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] END exit=$code" | Add-Content -LiteralPath $logFile
exit $code
