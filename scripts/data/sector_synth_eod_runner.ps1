# EOD sector board minute synthesizer runner (kline_sector_intraday supply leg).
# st-c9-secktide 2026-09-29: tdx truth channel dead since 2026-09-10 (server-side
# K-line family refusal, forensics in known_data_gaps kline_sector_intraday_tdx_dead);
# the synth leg (scripts/data/synth_board_minute.py, calibrated 2026-09-15) had no
# schedule and stopped after 09-22. This runner gives it a daily 15:50 slot
# (task sector_board_synth_eod). Non-trading days self-noop (script exits 0 with
# zero rows when kline_1min has no bars for the date). Idempotent: the synthesizer
# delete-then-writes only synth_* rows of the target date, tdx truth rows untouched.
# CONVERGENCE 2026-10-01 (st-storageswap-20260930, ruling A in a7 sector_switch
# validation SS6): the converged producer for this table is now
# kline_sector_intraday_from_constituents (internal_eqw, 5 periods, 727 boards).
# This runner switches to --dry-run observation mode (S12: task stays registered,
# writes nothing; stats still logged). Task retirement goes to the Owner gate
# batch together with the 5 tdx tasks and the resample task.
$ErrorActionPreference = 'Continue'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $python)) { $python = 'python' }
$runner = Join-Path $repoRoot 'scripts\data\synth_board_minute.py'
$logFile = Join-Path $repoRoot 'logs\sector_synth_eod.log'
$today = Get-Date -Format 'yyyy-MM-dd'
Set-Location -LiteralPath $repoRoot
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] START trade-date=$today mode=DRY-RUN (convergence ruling A, a7 SS6)" | Add-Content -LiteralPath $logFile
& $python -X utf8 $runner --trade-date $today --dry-run 2>&1 | Tee-Object -Variable out | Add-Content -LiteralPath $logFile
$code = $LASTEXITCODE
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] END exit=$code" | Add-Content -LiteralPath $logFile
exit $code
