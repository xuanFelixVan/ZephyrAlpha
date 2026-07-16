<#
.SYNOPSIS
    ZephyrAlpha 灾备备份——手动一键触发（Force模式，跳过间隔保护）
.DESCRIPTION
    [BLUEPRINT] MOD-INF-027 | §3.4
    双击或右键"用PowerShell运行"即可触发完整备份流水线。
    也可终端执行: powershell -ExecutionPolicy Bypass -File scripts\backup\一键备份.ps1
#>
$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " ZephyrAlpha 灾备备份（手动触发 - Force模式）" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Set-Location "D:\ZephyrAlpha"
& powershell -ExecutionPolicy Bypass -File scripts\backup\backup.ps1 -Force

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
