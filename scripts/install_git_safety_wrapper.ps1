# =============================================================================
# File: scripts/install_git_safety_wrapper.ps1
# Title: Git safety wrapper installer/uninstaller (65 memo section 7.7, P0 most critical gap)
# Owner: ZephyrAlpha-Owner
# Created: 2026-08-14
# Author: AI-GIT-001
# Status: production
# True-Source: wrapper function source = scripts/git_safety_wrapper.ps1 (this script only writes a dot-source line into $PROFILE - single source, no drift)
# Design-Spec: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/65_git_safety_governance.md section 7.7
# Creation-Token: auto-git-safety-wrapper-installer-20260814
# Encoding: ASCII-only by gate INJ-007 (PowerShell 5.1 ANSI decoding)
# Usage: powershell -File scripts/install_git_safety_wrapper.ps1            # install (idempotent)
#        powershell -File scripts/install_git_safety_wrapper.ps1 -Uninstall # uninstall
#        powershell -File scripts/install_git_safety_wrapper.ps1 -ProfilePath <tmp>  # test with temp profile
# =============================================================================
# ALGO_FLOW:
#   1. resolve -ProfilePath (default $PROFILE.CurrentUserCurrentHost); create if absent (append, never overwrite)
#   2. idempotency: marker '# >>> git-safety-wrapper >>>' present -> skip (-Force = uninstall then reinstall)
#   3. install: append marker block (dot-source absolute path of git_safety_wrapper.ps1; Session ID lives inside wrapper 7.32)
#   4. -Uninstall: delete marker block only, keep all other profile content
#   5. self-check: marker present + wrapper source reachable; print acceptance hints
# =============================================================================
#requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$Uninstall,
    [switch]$Force,
    [string]$ProfilePath = $PROFILE.CurrentUserCurrentHost
)

$ErrorActionPreference = 'Stop'
$_markerBegin = '# >>> git-safety-wrapper >>> (ZephyrAlpha #ARCH-GIT-CLEAN-GUARD-FIX)'
$_markerEnd   = '# <<< git-safety-wrapper <<<'
$_wrapperPath = Join-Path $PSScriptRoot 'git_safety_wrapper.ps1'

function _WriteBlock([string]$WrapperPath) {
    return @"

$_markerBegin
# wrapper function single source: git()/Remove-Item/rd/del/rm interception + CRITICAL hard block + audit + Session ID
. '$WrapperPath'
$_markerEnd
"@
}

# --- precondition ---
if (-not (Test-Path $_wrapperPath)) {
    Write-Host "[INSTALL] FAILED: wrapper source not found: $_wrapperPath" -ForegroundColor Red
    exit 1
}

# --- profile dir/file preparation ---
$_profileDir = Split-Path $ProfilePath -Parent
if ($_profileDir -and -not (Test-Path $_profileDir)) {
    New-Item -ItemType Directory -Path $_profileDir -Force | Out-Null
}
if (-not (Test-Path $ProfilePath)) {
    New-Item -ItemType File -Path $ProfilePath -Force | Out-Null
    Write-Host "[INSTALL] profile absent, created: $ProfilePath" -ForegroundColor Cyan
}

$_content = Get-Content $ProfilePath -Raw -ErrorAction SilentlyContinue
if ($null -eq $_content) { $_content = '' }
$_installed = $_content.Contains($_markerBegin)

if ($Uninstall) {
    if (-not $_installed) {
        Write-Host "[UNINSTALL] not installed (marker absent), nothing to do: $ProfilePath" -ForegroundColor Yellow
        exit 0
    }
    $_pattern = "(?ms)\r?\n?$([regex]::Escape($_markerBegin)).*?$([regex]::Escape($_markerEnd))\r?\n?"
    $_newContent = [regex]::Replace($_content, $_pattern, "`n")
    Set-Content -Path $ProfilePath -Value $_newContent -Encoding UTF8 -NoNewline
    Write-Host "[UNINSTALL] removed marker block: $ProfilePath" -ForegroundColor Green
    exit 0
}

if ($_installed -and -not $Force) {
    Write-Host "[INSTALL] already installed (marker present), idempotent skip. Use -Force to reinstall: $ProfilePath" -ForegroundColor Yellow
    exit 0
}
if ($_installed -and $Force) {
    $_pattern = "(?ms)\r?\n?$([regex]::Escape($_markerBegin)).*?$([regex]::Escape($_markerEnd))\r?\n?"
    $_content = [regex]::Replace($_content, $_pattern, "`n")
    Write-Host "[INSTALL] -Force: old block removed, reinstalling" -ForegroundColor Cyan
}

# --- append install (never overwrite existing profile content) ---
$_block = _WriteBlock -WrapperPath $_wrapperPath
$_newContent = $_content.TrimEnd() + "`n" + $_block
Set-Content -Path $ProfilePath -Value $_newContent -Encoding UTF8 -NoNewline

# --- self-check ---
$_verify = Get-Content $ProfilePath -Raw
if ($_verify.Contains($_markerBegin) -and $_verify.Contains($_markerEnd)) {
    Write-Host "[INSTALL] OK: wrapper installed into $ProfilePath" -ForegroundColor Green
    Write-Host "[INSTALL] wrapper source: $_wrapperPath" -ForegroundColor Green
    Write-Host "[INSTALL] acceptance: new PowerShell -> (Get-Command git) shows Function; git clean -fd -> BLOCKED; audit under `$env:USERPROFILE\.zephyr_audit\" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "[INSTALL] FAILED: marker self-check failed after write" -ForegroundColor Red
    exit 1
}
