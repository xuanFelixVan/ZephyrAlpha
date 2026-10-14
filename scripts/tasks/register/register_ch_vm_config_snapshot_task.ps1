# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | sect ch_vm_config_snapshot_task
# [MODULE] scripts.register_ch_vm_config_snapshot_task
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] scripts.backup.ch_vm_config_snapshot
# [CONSUMERS] Task Scheduler ZephyrAlpha-CHVMConfigSnapshot (monthly, one-shot)
# [STARTUP] manual
# [MATURITY] production
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] precondition missing -> refuse registration with exit 1; schtasks failure returns its exit code
# [TESTS] manual verification via schtasks /query
# [A_module] module_id=MOD-INF-043 | layer=script | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_ch_vm_config_snapshot_task.ps1 - monthly config-surface snapshot of the zephyr-ch VM.
#
# Owner 2026-10-13 (evening shift order) ruled "monthly snapshot" for the VM; this is the
# trigger leg. Cadence = MONTHLY day 5 at 10:00, deliberately NOT the 1st: the PG restore
# drill (ZEPHYR-RESTORE-DRILL) owns day 1 04:30, and the main backup chain owns 06:00.
# One-shot run: the executor exits when done (no resident process, no in-process Timer).
#
# Two in-register preconditions, refused when unmet (design behaviour, not a convenience):
#   P2 ruling gate  - the ruling id must exist in ruling_registry.yaml (a ruling whose
#                     affected_files names the executor) and for revising the 2026-10-04 image retirement).
#   P1 resource gate- the task must be seeded in the resource profile registry, else the
#                     system-side task is sched_task_orphan for everyone else's bags.
#
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/register_ch_vm_config_snapshot_task.ps1
#        add -ForceRegister to skip nothing (flag kept for symmetry with sibling scripts)

param([switch]$ForceRegister, [switch]$Unregister, [switch]$Status)

$ErrorActionPreference = "Stop"
# [FIX 2026-10-14 st-chiefcap3-20261014] repoRoot must go up THREE levels from
# scripts/tasks/register/. The original two-level Split-Path resolved to <root>\scripts,
# so $registry/$profile both missed and the P2 gate answered a false
# "ruling_registry.yaml not found". Aligned with register_post_settlement_task.ps1 /
# register_sector_eqw_task.ps1 ("..\..\.."). ASCII-only per root constitution rule 9.7.
$_cap3_up1 = Split-Path -Parent $PSScriptRoot
$_cap3_up2 = Split-Path -Parent $_cap3_up1
$repoRoot = Split-Path -Parent $_cap3_up2
$taskName = "ZephyrAlpha-CHVMConfigSnapshot"
$python = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
if (-not (Test-Path $python)) { $python = "python.exe" }
$script = Join-Path $repoRoot "scripts\backup\ch_vm_config_snapshot.py"

if ($Unregister) {
    schtasks /delete /tn $taskName /f | Write-Output
    exit $LASTEXITCODE
}
if ($Status) {
    schtasks /query /tn $taskName /fo LIST | Write-Output
    exit $LASTEXITCODE
}

# --- precondition P2: ruling must be on record -------------------------------
$registry = Join-Path $repoRoot "docs\01_policies_and_standards\_registry\catalogs\ruling_registry.yaml"
if (-not (Test-Path $registry)) {
    Write-Output "REFUSE: ruling_registry.yaml not found (cannot prove authority for a new scheduled task)"
    exit 1
}
# Marker is the executor path itself (ASCII only: .ps1 must stay pure ASCII per the root constitution
# (rule 9.7), so the numeric ruling id cannot be inlined here). A ruling whose affected_files
# names this executor is the proof that the cadence is on record.
$rulingHit = Select-String -Path $registry -Pattern 'scripts/backup/ch_vm_config_snapshot.py' -SimpleMatch |
    Select-Object -First 1
if (-not $rulingHit) {
    Write-Output "REFUSE: no ruling cites scripts/backup/ch_vm_config_snapshot.py (P2 gate, by design)"
    exit 1
}

# --- precondition P1: resource profile seed must exist -----------------------
$profile = Join-Path $repoRoot "config\resource_profile_registry.yaml"
if (-not (Test-Path $profile)) {
    Write-Output "REFUSE: resource profile registry not found"
    exit 1
}
# [FIX 2026-10-14 st-chiefcap3-20261014] the generator emits the seed UNQUOTED
# (`task_id: ops_ch_vm_config_snapshot`); the original pattern only matched the quoted
# form, so P1 refused even when the seed was present (false negative). Quotes are now
# optional: the gate still refuses when the seed is genuinely absent.
$seedHit = Select-String -Path $profile -Pattern 'task_id:\s+"?ops_ch_vm_config_snapshot"?' |
    Select-Object -First 1
if (-not $seedHit) {
    Write-Output "REFUSE: task_id ops_ch_vm_config_snapshot not seeded in resource_profile_registry (P1 gate)"
    exit 1
}

if (-not (Test-Path $script)) {
    Write-Output "REFUSE: executor missing $script"
    exit 1
}

$tr = "`"$python`" `"$script`""
schtasks /create /f /tn $taskName /tr $tr /sc MONTHLY /d 5 /st 10:00 | Write-Output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "REGISTERED $taskName (MONTHLY day 5 10:00, one-shot executor)"
Write-Output "NEXT: keep one line 'ch_vm_config_snapshot' in data/runtime/process_reaper_keep.txt"
