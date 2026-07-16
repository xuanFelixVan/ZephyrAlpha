<#
.SYNOPSIS
    手动触发灾备备份（Force模式，跳过8h间隔保护）
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | §3.4
    用法: 右键"用PowerShell运行" 或 终端执行
          powershell -ExecutionPolicy Bypass -File scripts\backup\backup_manual.ps1
    自动触发是主路径（backup_reconciler.py post-commit），此脚本为手动兜底。
#>
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " ZephyrAlpha 灾备备份（手动触发 - Force模式）" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Set-Location "D:\ZephyrAlpha"
& powershell -ExecutionPolicy Bypass -File "scripts\backup\backup.ps1" -Force

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
