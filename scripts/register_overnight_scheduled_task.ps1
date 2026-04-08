# 注册 Windows 计划任务：每 8 小时运行一次 overnight_audit_runner.py（当前用户，无需管理员）
# 用法（在 PowerShell 中）：
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force   # 若未允许脚本
#   cd D:\ZephyrAlpha
#   powershell -ExecutionPolicy Bypass -File .\scripts\register_overnight_scheduled_task.ps1
#
# 卸载任务：
#   Unregister-ScheduledTask -TaskName "ZephyrAlpha-OvernightAudit" -Confirm:$false

$Repo = "D:\ZephyrAlpha"
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) {
    Write-Error "未找到 python，请先安装 Python 并加入 PATH。"
    exit 1
}

$TaskName = "ZephyrAlpha-OvernightAudit"
$Script = Join-Path $Repo "scripts\overnight_audit_runner.py"

if (-not (Test-Path $Script)) {
    Write-Error "找不到: $Script"
    exit 1
}

# 若已存在则先删
Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false

$Action = New-ScheduledTaskAction -Execute $Python -Argument "`"$Script`"" -WorkingDirectory $Repo
# 每 8 小时重复（从下一分钟起算）
$Start = (Get-Date).AddMinutes(1)
$Trigger = New-ScheduledTaskTrigger -Once -At $Start -RepetitionInterval (New-TimeSpan -Hours 8) -RepetitionDuration ([TimeSpan]::MaxValue)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "ZephyrAlpha: 生成 overnight_runs 审计报告包"

Write-Host "已注册计划任务: $TaskName（每 8 小时运行一次）"
Write-Host "查看: Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "手动跑一次: Start-ScheduledTask -TaskName '$TaskName'"
