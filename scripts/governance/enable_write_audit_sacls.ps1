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
# Locale-independent subcategory GUID (Chinese Windows name is localized).
# File System = {0CCE921D-69AE-11D9-BED3-505054503030} (well-known constant).
$fsGuid = "{0CCE921D-69AE-11D9-BED3-505054503030}"

# ---- enable SeSecurityPrivilege (required for SACL write; admin token has it disabled by default) ----
$privCode = @"
using System;
using System.Runtime.InteropServices;
public class TokenPriv {
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool OpenProcessToken(IntPtr h, int acc, out IntPtr tok);
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool LookupPrivilegeValue(string host, string name, out long luid);
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool AdjustTokenPrivileges(IntPtr tok, bool disable, ref TP newState, int len, IntPtr prev, IntPtr relen);
    [StructLayout(LayoutKind.Sequential)]
    public struct TP { public int Count; public long Luid; public int Attr; }
    public static bool Enable(string name) {
        IntPtr tok;
        if (!OpenProcessToken(System.Diagnostics.Process.GetCurrentProcess().Handle, 0x28, out tok)) return false;
        TP tp = new TP();
        tp.Count = 1;
        if (!LookupPrivilegeValue(null, name, out tp.Luid)) return false;
        tp.Attr = 0x2; // SE_PRIVILEGE_ENABLED
        return AdjustTokenPrivileges(tok, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
    }
}
"@
try {
    Add-Type -TypeDefinition $privCode -ErrorAction Stop
    $privOk = [TokenPriv]::Enable("SeSecurityPrivilege")
    Write-Host "  [0/3] SeSecurityPrivilege enabled: $privOk"
} catch {
    Write-Host "  [0/3] [WARN] privilege enable failed: $($_.Exception.Message)" -ForegroundColor Yellow
}
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
    auditpol /set /subcategory:"$fsGuid" /success:disable | Out-Null
    Write-Host "  [UNDO] auditpol File System success=disable (by GUID)"
    Write-Host "== UNDO complete ==" -ForegroundColor Green
    exit 0
}

Write-Host "== WriteAudit SACL exact-attribution enabler (#ARCH-279 B3) ==" -ForegroundColor Cyan

# 1. enable File System audit subcategory (GUID defined above, locale-independent)
auditpol /set /subcategory:"$fsGuid" /success:enable | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [1/3] [FAIL] auditpol /set failed (exit $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}
Write-Host "  [1/3] auditpol: File System success=enable (by GUID)"

# 2. write SACLs on hot dir set (Everyone write/delete success, child inherit)
# NOTE: pre-compute enum unions in variables -- multi-line -bor inside New-Object
# argument list is misparsed as Object[] op_BitwiseOr (PS5.1 parser pitfall).
$rights = [System.Security.AccessControl.FileSystemRights]::Write -bor [System.Security.AccessControl.FileSystemRights]::Delete -bor [System.Security.AccessControl.FileSystemRights]::DeleteSubdirectoriesAndFiles
$inherit = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [System.Security.AccessControl.InheritanceFlags]::ObjectInherit
$auditRule = New-Object System.Security.AccessControl.FileSystemAuditRule(
    "Everyone",
    $rights,
    $inherit,
    [System.Security.AccessControl.PropagationFlags]::None,
    [System.Security.AccessControl.AuditFlags]::Success
)
$saclFails = 0
foreach ($dir in $hotDirs) {
    if (-not (Test-Path $dir)) {
        Write-Host "  [2/3] skip (missing): $dir" -ForegroundColor Yellow
        continue
    }
    try {
        $acl = Get-Acl -Path $dir -Audit
        $acl.AddAuditRule($auditRule)
        Set-Acl -Path $dir -AclObject $acl -ErrorAction Stop
        Write-Host "  [2/3] SACL written: $dir"
    } catch {
        $saclFails++
        Write-Host "  [2/3] [FAIL] SACL write failed: $dir -- $($_.Exception.Message)" -ForegroundColor Red
    }
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
$pol = auditpol /get /subcategory:"$fsGuid" 2>$null | Out-String
Write-Host "  [3/3] auditpol readback: $(($pol -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1) -replace '\s+', ' ')"

if ($ok) {
    Write-Host "== DONE: hot-dir writes/deletes now generate Security 4663 events ==" -ForegroundColor Green
    Write-Host "   collect: python scripts/governance/collect_write_audit_4663.py (schedule or ad-hoc)"
} else {
    Write-Host "== PARTIAL FAILURE: see [FAIL] lines above ==" -ForegroundColor Red
    exit 1
}
