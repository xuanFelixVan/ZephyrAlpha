# ZephyrAlpha文档治理定期审计任务部署脚本
# 适用于Windows系统

param(
    [string]$Action = "Install",  # Install, Uninstall, Test
    [string]$ProjectRoot = "D:\ZephyrAlpha"
)

$ErrorActionPreference = "Stop"

# 任务定义
$Tasks = @(
    @{
        Name = "ZephyrAlpha_Weekly_Audit"
        Description = "ZephyrAlpha文档治理快速审计 - 每周一凌晨2:00执行"
        Script = "scheduled_quick_audit.py"
        Trigger = "Weekly"
        DayOfWeek = "Monday"
        Hour = 2
        Minute = 0
    },
    @{
        Name = "ZephyrAlpha_Monthly_Audit"
        Description = "ZephyrAlpha文档治理标准审计 - 每月1日凌晨3:00执行"
        Script = "scheduled_standard_audit.py"
        Trigger = "Monthly"
        DayOfMonth = 1
        Hour = 3
        Minute = 0
    },
    @{
        Name = "ZephyrAlpha_Quarterly_Audit"
        Description = "ZephyrAlpha文档治理深度审计 - 每季度首日凌晨3:00执行"
        Script = "scheduled_deep_audit.py"
        Trigger = "Quarterly"
        Months = @("January", "April", "July", "October")
        DayOfMonth = 1
        Hour = 3
        Minute = 0
    }
)

function Install-Tasks {
    Write-Host "开始安装定期审计任务..." -ForegroundColor Green

    foreach ($Task in $Tasks) {
        Write-Host "`n安装任务: $($Task.Name)" -ForegroundColor Cyan

        # 检查任务是否已存在
        $ExistingTask = Get-ScheduledTask -TaskName $Task.Name -ErrorAction SilentlyContinue
        if ($ExistingTask) {
            Write-Host "  任务已存在，跳过安装" -ForegroundColor Yellow
            continue
        }

        # 创建任务触发器
        $Trigger = switch ($Task.Trigger) {
            "Weekly" {
                New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Task.DayOfWeek -At "$($Task.Hour):$($Task.Minute)"
            }
            "Monthly" {
                New-ScheduledTaskTrigger -Once -At (Get-Date -Day $Task.DayOfMonth -Hour $Task.Hour -Minute $Task.Minute -Second 0)
            }
            "Quarterly" {
                # 季度任务需要手动设置多个触发器
                $Triggers = @()
                foreach ($Month in $Task.Months) {
                    $MonthNum = switch ($Month) {
                        "January" { 1 }
                        "April" { 4 }
                        "July" { 7 }
                        "October" { 10 }
                    }
                    $Date = Get-Date -Month $MonthNum -Day $Task.DayOfMonth -Hour $Task.Hour -Minute $Task.Minute -Second 0
                    $Triggers += New-ScheduledTaskTrigger -Once -At $Date
                }
                $Triggers
            }
        }

        # 创建任务动作
        $Action = New-ScheduledTaskAction `
            -Execute "python" `
            -Argument "scripts\$($Task.Script)" `
            -WorkingDirectory $ProjectRoot

        # 创建任务设置
        $Settings = New-ScheduledTaskSettingsSet `
            -StartWhenAvailable `
            -DontStopOnIdleEnd `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries

        # 注册任务
        Register-ScheduledTask `
            -TaskName $Task.Name `
            -Description $Task.Description `
            -Trigger $Trigger `
            -Action $Action `
            -Settings $Settings `
            -RunLevel Highest `
            -Force

        Write-Host "  ✓ 任务安装成功" -ForegroundColor Green
    }

    Write-Host "`n所有任务安装完成！" -ForegroundColor Green
}

function Uninstall-Tasks {
    Write-Host "开始卸载定期审计任务..." -ForegroundColor Yellow

    foreach ($Task in $Tasks) {
        Write-Host "`n卸载任务: $($Task.Name)" -ForegroundColor Cyan

        $ExistingTask = Get-ScheduledTask -TaskName $Task.Name -ErrorAction SilentlyContinue
        if ($ExistingTask) {
            Unregister-ScheduledTask -TaskName $Task.Name -Confirm:$false
            Write-Host "  ✓ 任务已卸载" -ForegroundColor Green
        } else {
            Write-Host "  任务不存在，跳过" -ForegroundColor Yellow
        }
    }

    Write-Host "`n所有任务卸载完成！" -ForegroundColor Green
}

function Test-Tasks {
    Write-Host "测试定期审计任务..." -ForegroundColor Cyan

    foreach ($Task in $Tasks) {
        Write-Host "`n测试任务: $($Task.Name)" -ForegroundColor Cyan

        $ExistingTask = Get-ScheduledTask -TaskName $Task.Name -ErrorAction SilentlyContinue
        if ($ExistingTask) {
            Write-Host "  任务状态: $($ExistingTask.State)" -ForegroundColor Green
            Write-Host "  下次运行时间: $($ExistingTask.NextRunTime)" -ForegroundColor Green
            Write-Host "  上次运行时间: $($ExistingTask.LastRunTime)" -ForegroundColor Green
            Write-Host "  上次运行结果: $($ExistingTask.LastTaskResult)" -ForegroundColor Green
        } else {
            Write-Host "  任务不存在" -ForegroundColor Red
        }
    }

    Write-Host "`n测试完成！" -ForegroundColor Green
}

function Test-Scripts {
    Write-Host "测试审计脚本..." -ForegroundColor Cyan

    $Scripts = @(
        "scheduled_quick_audit.py",
        "scheduled_standard_audit.py",
        "scheduled_deep_audit.py"
    )

    foreach ($Script in $Scripts) {
        Write-Host "`n测试脚本: $Script" -ForegroundColor Cyan

        $ScriptPath = Join-Path $ProjectRoot "scripts\$Script"
        if (Test-Path $ScriptPath) {
            Write-Host "  脚本存在: $ScriptPath" -ForegroundColor Green

            # 检查脚本语法
            $SyntaxCheck = python -m py_compile $ScriptPath 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  语法检查: 通过" -ForegroundColor Green
            } else {
                Write-Host "  语法检查: 失败" -ForegroundColor Red
                Write-Host "  错误信息: $SyntaxCheck" -ForegroundColor Red
            }
        } else {
            Write-Host "  脚本不存在: $ScriptPath" -ForegroundColor Red
        }
    }

    Write-Host "`n脚本测试完成！" -ForegroundColor Green
}

# 主程序
Write-Host @"
========================================
ZephyrAlpha文档治理定期审计任务部署工具
========================================
项目根目录: $ProjectRoot
操作: $Action
========================================
"@ -ForegroundColor Cyan

switch ($Action) {
    "Install" {
        Install-Tasks
    }
    "Uninstall" {
        Uninstall-Tasks
    }
    "Test" {
        Test-Scripts
        Test-Tasks
    }
    default {
        Write-Host "未知操作: $Action" -ForegroundColor Red
        Write-Host "可用操作: Install, Uninstall, Test" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`n操作完成！" -ForegroundColor Green
