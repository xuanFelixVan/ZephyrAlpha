# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | #3
# [MODULE] scripts.register_library_ledger_backup_task
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] scripts.backup.library_ledger_backup
# [CONSUMERS] Task Scheduler ZephyrAlpha_LibraryLedgerBackup / ZephyrAlpha_LibraryLedgerDrill
# [STARTUP] manual
# [MATURITY] production
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] registration failure exits non-zero with schtasks error text
# [TESTS] manual verification via schtasks /query
# [A_module] module_id=MOD-INF-043 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_library_ledger_backup_task.ps1 - Register library ledger backup + drill tasks.
#
# Daily backup at 03:30. Monthly restore drill on day 1 at 04:00 (schtasks MONTHLY /d 1).
# Both are stateless one-shot runs of scripts/backup/library_ledger_backup.py (no resident
# process). Register "library_ledger_backup" in data/runtime/process_reaper_keep.txt so the
# process reaper never kills these runs (AGENTS.md RULE-GUARDIAN).
#
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/register_library_ledger_backup_task.ps1

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
if (-not (Test-Path $python)) { $python = "python.exe" }
$script = Join-Path $repoRoot "scripts\backup\library_ledger_backup.py"
$tr = "`"$python`" `"$script`""

schtasks /create /f /tn "ZephyrAlpha_LibraryLedgerBackup" /tr "$tr backup" /sc DAILY /st 03:30 | Write-Output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

schtasks /create /f /tn "ZephyrAlpha_LibraryLedgerDrill" /tr "$tr drill" /sc MONTHLY /d 1 /st 04:00 | Write-Output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "REGISTERED ZephyrAlpha_LibraryLedgerBackup (DAILY 03:30)"
Write-Output "REGISTERED ZephyrAlpha_LibraryLedgerDrill (MONTHLY day 1 04:00)"
Write-Output "NEXT: add 'library_ledger_backup' line to data/runtime/process_reaper_keep.txt"
