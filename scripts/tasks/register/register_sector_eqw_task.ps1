# Idempotent (re)registration for scheduled task ZephyrAlpha_SectorEqwIntraday.
# st-fig13-followup-20261006 2026-10-08: renamed from 'sector_eqw_intraday' to
# the ZephyrAlpha_ prefix convention (ops naming lane; map D13-48 tn/query faces
# synced in the same batch). One-shot rename migration: Register new name first,
# verify it is live, then Unregister the old name - S12 "never Unregister a live
# instance" is honored because the successor is confirmed live before teardown.
# st-storageswap-20260930 2026-10-01: convergence ruling A (a7 sector_switch
# validation SS6) - registers the internal_eqw producer (converged single
# producer for c1_market.kline_sector_intraday after tdx refusal 09-10 and the
# J-leg dry-run downgrade). Daily 15:40 (after kline_1min close ~15:05, before
# J's 15:50 dry-run observation slot). Non-trading days self-noop inside the
# producer. Mirrors register_sector_synth_task.ps1 semantics (tilib mirror):
# InteractiveToken, IgnoreNew. Re-runs use in-place Register -Force per house
# rule S12. Pure ASCII (PowerShell 5.1 GBK decoding).
$ErrorActionPreference = 'Stop'
$taskName = 'ZephyrAlpha_SectorEqwIntraday'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$runner = Join-Path $repoRoot 'scripts\data\sector_eqw_runner.ps1'
if (-not (Test-Path -LiteralPath $runner)) { throw ('runner missing: ' + $runner) }
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $runner + '"') -WorkingDirectory $repoRoot
$trigger = New-ScheduledTaskTrigger -Daily -At '15:40'
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Output ('REGISTERED ' + $taskName + ' -> ' + $runner + ' @ daily 15:40')
