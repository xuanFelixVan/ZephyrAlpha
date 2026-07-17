<#
.SYNOPSIS
    Manual disaster recovery backup trigger (Force mode, skips 8h interval protection)
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | Section 3.4
    Usage: right-click 'Run with PowerShell' or execute in terminal
          powershell -ExecutionPolicy Bypass -File scripts\backup\backup_manual.ps1
    Auto-trigger is the primary path (backup_reconciler.py post-commit); this script is a manual fallback.
#>
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " ZephyrAlpha Disaster Backup (Manual - Force Mode)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Set-Location "D:\ZephyrAlpha"
& powershell -ExecutionPolicy Bypass -File "scripts\backup\backup.ps1" -Force

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
