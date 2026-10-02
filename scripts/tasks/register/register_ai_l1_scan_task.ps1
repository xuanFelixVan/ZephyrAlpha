# [BLUEPRINT] MOD-SCRIPT-register_ai_l1_scan | docs/03_modules/_domain_governance/registry_governance/blueprint.md
# [MODULE] scripts.register_ai_l1_scan_task
# [DOMAIN] D_GOVERNANCE
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# register_ai_l1_scan_task.ps1 - Register the ZephyrAlpha_AIL1Scan beat host (L1 item 7).
#
# THIS SCRIPT IS DOUBLE-GATED (R1-F2 "two preconditions", fail-closed):
#   P1 resource profile registered: task_id ops_ai_l1_external_scan present in
#      config/resource_profile_registry.yaml (via generator manual seed, GENERATED
#      registry must never be hand-edited).
#   P2 ruling registered: marker L1_EXTERNAL_SCAN_HOST present in
#      docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
#      (ruling number assigned by Owner/governance ONLY; this lane never self-grants
#      one. See docs/_working/ai_layer_vision/P1_full_construction_inventory.md L1 #7
#      and night report item 9: Owner ratification + ruling registration).
# If either gate is unmet the script REFUSES and registers nothing (exit 2).
# Enabling this is a production-scheduling action = Owner gate. Do not run it until
# the Owner approves the window; use -DryRun to preview the exact registration.
#
# Beat: daily calendar slot running scripts/ai_layer/run_ai_l1_scan_tick.py
#   (vein regen + search-order TTL sweep; light local work, no timers in code --
#   constitution 9.3 satisfied because the OS task scheduler provides the beat).
#
# Enable command (run AFTER both gates pass, Owner nod, inside an approved window):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\register_ai_l1_scan_task.ps1
# Preview without touching the task store:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\register_ai_l1_scan_task.ps1 -DryRun
# Verify after enabling:
#   schtasks /query /tn ZephyrAlpha_AIL1Scan /v /fo LIST

param(
    [switch]$DryRun,
    [string]$AtTime = "04:30"   # proposed off-peak slot; final beat value is Owner-rulable
)

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_AIL1Scan"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"
$ProfileReg = Join-Path $RepoRoot "config\resource_profile_registry.yaml"
$RulingReg  = Join-Path $RepoRoot "docs\01_policies_and_standards\_registry\catalogs\ruling_registry.yaml"
$TickScript = Join-Path $RepoRoot "scripts\ai_layer\run_ai_l1_scan_tick.py"

Write-Output "AIL1Scan host gate check (R1-F2 two preconditions)"

if (-not (Test-Path $TickScript)) {
    Write-Output "PRECONDITIONS_UNMET: tick script missing: $TickScript"
    exit 2
}

$gateP1 = $false
$gateP2 = $false
if (Test-Path $ProfileReg) {
    if (Select-String -Path $ProfileReg -Pattern "ops_ai_l1_external_scan" -Quiet) { $gateP1 = $true }
}
if (Test-Path $RulingReg) {
    if (Select-String -Path $RulingReg -Pattern "L1_EXTERNAL_SCAN_HOST" -Quiet) { $gateP2 = $true }
}

Write-Output ("  P1 resource profile registered : " + $(if ($gateP1) { "PASS" } else { "FAIL" }))
Write-Output ("  P2 ruling registered           : " + $(if ($gateP2) { "PASS" } else { "FAIL" }))

if (-not ($gateP1 -and $gateP2)) {
    Write-Output "REFUSED: R1-F2 preconditions unmet - nothing registered."
    Write-Output "  To unblock: (a) total-coordinator adds seed ops_ai_l1_external_scan to"
    Write-Output "      generator manual seeds and regenerates resource_profile_registry;"
    Write-Output "  (b) Owner/governance registers a ruling carrying marker L1_EXTERNAL_SCAN_HOST"
    Write-Output "      in ruling_registry.yaml (number assigned there, never in this script)."
    exit 2
}

if ($DryRun) {
    Write-Output "DRYRUN would register: $TaskName daily at $AtTime"
    Write-Output "  action: powershell.exe -NoProfile -ExecutionPolicy Bypass -Command python $TickScript"
    Write-Output "  settings: 1h limit, IgnoreNew, StartWhenAvailable"
    exit 0
}

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -Command python $TickScript"
$Trigger = New-ScheduledTaskTrigger -Daily -At $AtTime
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Output "OK registered $TaskName (daily $AtTime, 1h limit)"
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next Run"
