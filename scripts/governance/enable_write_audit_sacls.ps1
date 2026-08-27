# enable_write_audit_sacls.ps1 - WriteAudit SACL exact-attribution one-time enabler (#ARCH-279 B3)
#
# Purpose: enable Windows-native exact attribution for WriteAudit (Security event 4663:
# who / which process / when / which file / what write-delete operation). Two system actions:
#   1. auditpol: enable "File System" audit subcategory (Success)
#   2. Write SACLs on the WriteAudit hot dir set (Everyone, write/delete success, inherited)
#
# Run (REQUIRED): right-click PowerShell "Run as administrator", then:
#   powershell -ExecutionPolicy Bypass -File scripts\governance\enable_write_audit_sacls.ps1
# Verify: script self-checks at the end. Afterwards hot-dir writes/deletes generate 4663
#   events, collected by scripts/governance/collect_write_audit_4663.py into
#   .runtime/audit/write_audit.jsonl (exact_attribution=true).
#
# Rollback: powershell -ExecutionPolicy Bypass -File scripts\governance\enable_write_audit_sacls.ps1 -Undo
# Scope: hot dir set only (registry catalogs / design memos / quarantine). No full-disk audit.

param(
    [switch]$Undo
)

$ErrorActionPreference = "Stop"

# ---- admin self-check ----
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[FAIL] must run as Administrator (right-click -> Run as administrator)" -ForegroundColor Red
    exit 1
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$hotDirs = @(
    (Join-Path $repoRoot "docs\01_policies_and_standards\_registry\catalogs"),
    (Join-Path $repoRoot "docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos"),
    (Join-Path $repoRoot ".runtime\quarantine")
)

if ($Undo) {
    Write-Host "== UNDO: remove hot-dir SACLs and disable File System auditing ==" -ForegroundColor Yellow
    foreach ($dir in $hotDirs) {
        if (Test-Path $dir) {
            $acl = Get-Acl -Path $dir -Audit
            $rules = @($acl.GetAuditRules($true, $false, [Security.Principal.NTAccount]))
            $removed = 0
            foreach ($r in $rules) {
                if ($r.IdentityReference.Value -eq "Everyone" -and $r.AuditFlags -eq "Success") {
                    $acl.RemoveAuditRule($r) | Out-Null
                    $removed++
                }
            }
            Set-Acl -Path $dir -AclObject $acl
            Write-Host ("  [UNDO] {0} (removed {1} audit rules)" -f $dir, $removed)
        }
    }
    auditpol /set /subcategory:"File System" /success:disable | Out-Null
    Write-Host "  [UNDO] auditpol File System success=disable"
    Write-Host "== UNDO complete ==" -ForegroundColor Green
    exit 0
}

Write-Host "== WriteAudit SACL exact-attribution enabler (#ARCH-279 B3) ==" -ForegroundColor Cyan

# 1. enable File System audit subcategory
auditpol /set /subcategory:"File System" /success:enable | Out-Null
Write-Host "  [1/3] auditpol: File System success=enable"

# 2. write SACLs on hot dir set (Everyone write/delete success, child inherit)
$auditRule = New-Object System.Security.AccessControl.FileSystemAuditRule(
    "Everyone",
    [System.Security.AccessControl.FileSystemRights]::Write -bor
        [System.Security.AccessControl.FileSystemRights]::Delete -bor
        [System.Security.AccessControl.FileSystemRights]::DeleteSubdirectoriesAndFiles,
    [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
        [System.Security.AccessControl.InheritanceFlags]::ObjectInherit,
    [System.Security.AccessControl.PropagationFlags]::None,
    [System.Security.AccessControl.AuditFlags]::Success
)
foreach ($dir in $hotDirs) {
    if (-not (Test-Path $dir)) {
        Write-Host "  [2/3] skip (missing): $dir" -ForegroundColor Yellow
        continue
    }
    $acl = Get-Acl -Path $dir -Audit
    $acl.AddAuditRule($auditRule)
    Set-Acl -Path $dir -AclObject $acl
    Write-Host "  [2/3] SACL written: $dir"
}

# 3. readback self-check
$ok = $true
foreach ($dir in $hotDirs) {
    if (-not (Test-Path $dir)) { continue }
    $acl = Get-Acl -Path $dir -Audit
    $rules = @($acl.GetAuditRules($true, $false, [Security.Principal.NTAccount]) |
        Where-Object { $_.IdentityReference.Value -eq "Everyone" -and $_.AuditFlags -eq "Success" })
    if ($rules.Count -eq 0) {
        Write-Host "  [3/3] [FAIL] SACL readback empty: $dir" -ForegroundColor Red
        $ok = $false
    } else {
        Write-Host "  [3/3] SACL readback OK: $dir ($($rules.Count) rules)"
    }
}
$pol = auditpol /get /subcategory:"File System" 2>$null | Out-String
Write-Host "  [3/3] auditpol readback: $($pol -split "`n" | Select-Object -Last 2)"

if ($ok) {
    Write-Host "== DONE: hot-dir writes/deletes now generate Security 4663 events ==" -ForegroundColor Green
    Write-Host "   collect: python scripts/governance/collect_write_audit_4663.py (schedule or ad-hoc)"
} else {
    Write-Host "== PARTIAL FAILURE: see [FAIL] lines above ==" -ForegroundColor Red
    exit 1
}
