# Idempotent (re)registration for scheduled task sector_board_synth_eod.
# st-c9-secktide 2026-09-29: restores the daily supply leg of
# c1_market.kline_sector_intraday after the tdx truth channel died (server-side
# K-line refusal, forensics in known_data_gaps kline_sector_intraday_tdx_dead)
# and the manual synth runs stopped after 2026-09-22. Daily 15:50 (after the
# intraday_minute layer closes kline_1min ~15:05, before daily_kline 16:30);
# non-trading days self-noop inside the runner. Mirrors tilib task semantics:
# InteractiveToken, IgnoreNew, battery guards by PS 5.1 defaults. In-place
# Register -Force per house rule S12 (never Unregister a live instance).
# Pure ASCII (PowerShell 5.1 GBK decoding).
$ErrorActionPreference = 'Stop'
$taskName = 'sector_board_synth_eod'
$repoRoot = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $repoRoot 'scripts\data\sector_synth_eod_runner.ps1'
if (-not (Test-Path -LiteralPath $runner)) { throw ('runner missing: ' + $runner) }
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $runner + '"') -WorkingDirectory $repoRoot
$trigger = New-ScheduledTaskTrigger -Daily -At '15:50'
# PS 5.1 has no DisallowStartIfOnBatteries / StopIfGoingOnBatteries switches; battery-stop
# is the cmdlet default, so omitting both preserves the battery-guard behavior.
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Output ('REGISTERED ' + $taskName + ' -> ' + $runner + ' @ daily 15:50')
