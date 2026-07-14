# [BLUEPRINT] MOD-L00-004 | scripts/register_scheduler_task.ps1
# [MODULE] scripts.register_scheduler_task
# [DOMAIN] D_DATA
# [TTL] permanent
# 注册 Windows 计划任务，开机自启 ZephyrAlpha DataScheduler
# 用法：以管理员身份运行 PowerShell，执行此脚本

$ErrorActionPreference = "Stop"

$taskName = "ZephyrAlpha_DataScheduler"
$ps1Path = "d:\ZephyrAlpha\scripts\start_scheduler.ps1"

# 创建动作（用 powershell.exe 启动 ps1 脚本，避免 .bat 不在 scripts/ 目录契约允许清单）
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ps1Path`"" -WorkingDirectory "d:\ZephyrAlpha"

# 创建触发器（开机自启）
$trigger = New-ScheduledTaskTrigger -AtStartup

# 创建设置（失败重试3次，间隔5分钟）
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -ExecutionTimeLimit (New-TimeSpan -Days 365)

# 创建主体（SYSTEM 用户，最高权限）
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# 注册任务（如果已存在则覆盖）
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "已删除旧任务: $taskName"
}

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force

Write-Host "已注册计划任务: $taskName"
Write-Host "触发器: 开机自启 (AtStartup)"
Write-Host "用户: SYSTEM (最高权限)"
Write-Host "失败重试: 3次，间隔5分钟"
Write-Host ""
Write-Host "手动启动: schtasks /run /tn $taskName"
Write-Host "手动停止: schtasks /end /tn $taskName"
Write-Host "查询状态: schtasks /query /tn $taskName"
