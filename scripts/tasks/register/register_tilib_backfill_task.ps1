# Idempotent (re)registration for scheduled task tilib_indicator_backfill_nightly.
# S2 root fix 2026-09-27 (st-ec3-water): re-points the task action from the contract-violating
# legacy backfill_night.bat (.bat not in scripts/ directory_contract allowed list) to
# scripts\data\backfill_night.ps1. Mirrors legacy task semantics: daily 02:30,
# InteractiveToken, IgnoreNew, battery guards. In-place Register -Force per house rule
# S12 (never Unregister a live instance). Pure ASCII (PowerShell 5.1 GBK decoding).
$ErrorActionPreference = 'Stop'
$taskName = 'tilib_indicator_backfill_nightly'
$repoRoot = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $repoRoot 'scripts\data\backfill_night.ps1'
if (-not (Test-Path -LiteralPath $runner)) { throw ('runner missing: ' + $runner) }
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $runner + '"') -WorkingDirectory $repoRoot
$trigger = New-ScheduledTaskTrigger -Daily -At '02:30'
# PS 5.1 has no DisallowStartIfOnBatteries / StopIfGoingOnBatteries switches; battery-stop
# is the cmdlet default, so omitting both preserves legacy battery-guard behavior.
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Output ('REGISTERED ' + $taskName + ' -> ' + $runner)
