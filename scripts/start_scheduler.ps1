# [BLUEPRINT] MOD-L00-004 | scripts/start_scheduler.ps1
# [MODULE] scripts.start_scheduler
# [DOMAIN] D_DATA
# [TTL] permanent
# ZephyrAlpha 数据源调度器启动脚本（PowerShell 版）
# 支持崩溃自动重启（10秒后），被 Windows 计划任务调用

$env:PYTHONPATH = "d:\ZephyrAlpha\src"
$env:PYTHONIOENCODING = "utf-8"
Set-Location "d:\ZephyrAlpha"

while ($true) {
    $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$now] 启动 ZephyrAlpha DataScheduler..."
    $proc = Start-Process -FilePath "python" -ArgumentList "-m", "zephyr.data.scheduler" -NoNewWindow -Wait -PassThru
    $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$now] scheduler 退出（exitcode=$($proc.ExitCode)），10秒后重启..."
    Start-Sleep -Seconds 10
}
