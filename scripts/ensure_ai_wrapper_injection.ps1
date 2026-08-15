# =============================================================================
# File: scripts/ensure_ai_wrapper_injection.ps1
# Title: AI RunCommand channel wrapper injection (tracker #58, 65 memo section 7.33)
# Owner: ZephyrAlpha-Owner
# Created: 2026-08-15
# Author: AI-GIT-001
# Status: production
# Mechanism: Trae agent-tool-host.exe spawns `powershell -NoProfile -NonInteractive ...`
#   (hardcoded in the Rust binary - no settings.json switch), so all four $PROFILE
#   variants are suppressed for the AI RunCommand channel. But the hardcoded preamble
#   dot-sources a per-toolhost-process snapshot:
#     %USERPROFILE%\.trae-cn\toolhost\native-runcommand-snapshots\process-<pid>-<ts>\powershell-profile-snapshot.ps1
#   Appending one idempotent marker line there restores the full wrapper (L1/L2/L4/L5/L6)
#   for every subsequent RunCommand of that toolhost process.
# Lifetime: a snapshot dir lives as long as its agent-tool-host process; IDE restart
#   spawns a new toolhost -> new snapshot dir -> re-injection needed. A 1-minute
#   scheduled task (ZephyrAlpha-AI-Wrapper-Inject) re-runs this script to close the gap
#   (worst-case unprotected window: one scheduler interval after toolhost start).
# Related-Issues: #ARCH-GIT-CLEAN-GUARD-FIX (tracker #58)
# Creation-Token: ai-channel-wrapper-injection-tracker58-20260815
# Encoding: ASCII-only by gate INJ-007 (PowerShell 5.1 ANSI decoding)
# =============================================================================
# ALGO_FLOW:
#   1. Resolve snapshot roots: TRAE_NATIVE_RUN_COMMAND_SNAPSHOT_DIR env, then
#      .trae-cn / .trae toolhost dirs under USERPROFILE (skip missing silently)
#   2. For every process-*\powershell-profile-snapshot.ps1: skip when marker present,
#      else append one dot-source line (UTF-8 no BOM, PS 5.1 safe)
#   3. Print counters (injected/skipped) - stays silent-safe for scheduled execution
# =============================================================================
[CmdletBinding()]
param(
    # Test hook: point at a fabricated snapshot root instead of the real toolhost dirs
    [string]$SnapshotRoot = '',
    # Uninstall mode: strip injection lines from all snapshots
    [switch]$Remove
)

$ErrorActionPreference = 'Continue'
$MARKER = 'ZEPHYR-AI-WRAPPER-INJECT'
$wrapper = Join-Path $PSScriptRoot 'git_safety_wrapper.ps1'
if (-not (Test-Path $wrapper)) {
    Write-Error "wrapper source not found next to this script: $wrapper"
    exit 1
}
# single-quote the path for the dot-source line; escape embedded quotes defensively
$wrapperLit = $wrapper -replace "'", "''"
$injectLine = ". '$wrapperLit' # $MARKER v1 (tracker #58)"

$roots = @()
if ($SnapshotRoot) {
    $roots += $SnapshotRoot
} else {
    if ($env:TRAE_NATIVE_RUN_COMMAND_SNAPSHOT_DIR) { $roots += $env:TRAE_NATIVE_RUN_COMMAND_SNAPSHOT_DIR }
    $roots += (Join-Path $env:USERPROFILE '.trae-cn\toolhost\native-runcommand-snapshots')
    $roots += (Join-Path $env:USERPROFILE '.trae\toolhost\native-runcommand-snapshots')
}

$injected = 0; $skipped = 0; $removed = 0
foreach ($root in $roots) {
    if (-not $root -or -not (Test-Path $root)) { continue }
    $snaps = Get-ChildItem $root -Directory -Filter 'process-*' -ErrorAction SilentlyContinue |
        ForEach-Object { Join-Path $_.FullName 'powershell-profile-snapshot.ps1' } |
        Where-Object { Test-Path $_ }
    foreach ($snap in $snaps) {
        try {
            $content = [System.IO.File]::ReadAllText($snap)
            if ($Remove) {
                if ($content -match [regex]::Escape($MARKER)) {
                    $kept = [System.IO.File]::ReadAllLines($snap) | Where-Object { $_ -notmatch [regex]::Escape($MARKER) }
                    [System.IO.File]::WriteAllLines($snap, [string[]]$kept, [System.Text.UTF8Encoding]::new($false))
                    $removed++
                    Write-Output "removed: $snap"
                }
                continue
            }
            if ($content -match [regex]::Escape($MARKER)) { $skipped++; continue }
            [System.IO.File]::AppendAllText($snap, "`r`n$injectLine`r`n", [System.Text.UTF8Encoding]::new($false))
            $injected++
            Write-Output "injected: $snap"
        } catch {
            # never fail the scheduled task on a single locked/half-written snapshot
            Write-Output "skip (error): $snap - $_"
        }
    }
}
Write-Output "ensure-ai-wrapper-injection: injected=$injected skipped=$skipped removed=$removed"
exit 0
