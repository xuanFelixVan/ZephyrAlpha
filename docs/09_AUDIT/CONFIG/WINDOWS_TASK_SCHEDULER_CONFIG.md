---
module_id: WINDOWS_TASK_SCHEDULER_CONFIG
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - Windows任务计划配置指南文档
---

# Windows任务计划配置指南

## 📋 任务计划概述

**配置目的**: 在Windows系统上设置定期审计任务
**适用系统**: Windows 10/11/Server
**配置方法**: 使用Windows任务计划程序

---

## 🕐 任务计划配置

### 快速审计任务（每日）

**任务名称**: ZephyrAlpha_Quick_Audit
**执行频率**: 每天凌晨2:00
**执行程序**: `python.exe`
**参数**: `D:\ZephyrAlpha\scripts\periodic_audit_executor.py quick`
**工作目录**: `D:\ZephyrAlpha`

**配置步骤**:
1. 打开"任务计划程序"（Task Scheduler）
2. 创建基本任务
3. 设置触发器：每天凌晨2:00
4. 设置操作：启动程序
   - 程序或脚本：`C:\Python39\python.exe`（根据实际Python路径调整）
   - 添加参数：`scripts\periodic_audit_executor.py quick`
   - 起始于：`D:\ZephyrAlpha`
5. 设置条件：
   - 只有在计算机使用交流电源时才启动此任务：取消勾选
   - 如果计算机开始使用电池，则停止：取消勾选
6. 设置设置：
   - 如果任务失败，按以下频率重新启动：每5分钟
   - 尝试重新启动最多：3次

---

### 标准审计任务（每周）

**任务名称**: ZephyrAlpha_Standard_Audit
**执行频率**: 每周一凌晨3:00
**执行程序**: `python.exe`
**参数**: `D:\ZephyrAlpha\scripts\periodic_audit_executor.py standard`
**工作目录**: `D:\ZephyrAlpha`

**配置步骤**: 同快速审计任务

---

### 深度审计任务（每月）

**任务名称**: ZephyrAlpha_Deep_Audit
**执行频率**: 每月1日凌晨4:00
**执行程序**: `python.exe`
**参数**: `D:\ZephyrAlpha\scripts\periodic_audit_executor.py deep`
**工作目录**: `D:\ZephyrAlpha`

**配置步骤**: 同快速审计任务

---

## 📝 PowerShell脚本配置

### 创建任务的PowerShell脚本

```powershell
# 快速审计任务
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "scripts\periodic_audit_executor.py quick" -WorkingDirectory "D:\ZephyrAlpha"
$Trigger = New-ScheduledTaskTrigger -Daily -At 2am
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "ZephyrAlpha_Quick_Audit" -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Highest

# 标准审计任务
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "scripts\periodic_audit_executor.py standard" -WorkingDirectory "D:\ZephyrAlpha"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 3am
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "ZephyrAlpha_Standard_Audit" -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Highest

# 深度审计任务
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "scripts\periodic_audit_executor.py deep" -WorkingDirectory "D:\ZephyrAlpha"
$Trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 4am
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "ZephyrAlpha_Deep_Audit" -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Highest
```

---

## 🔔 告警配置

### 邮件告警配置

**SMTP服务器**: smtp.example.com
**端口**: 587
**发件人**: audit@zephyralpha.com
**收件人**: admin@zephyralpha.com

**配置文件**: `docs/09_AUDIT/CONFIG/email_config.json`

```json
{
  "smtp_server": "smtp.example.com",
  "smtp_port": 587,
  "sender_email": "audit@zephyralpha.com",
  "sender_password": "your_password",
  "recipient_email": "admin@zephyralpha.com",
  "enable_ssl": true
}
```

---

## 📊 监控与日志

### 日志文件位置

| 日志类型 | 文件路径 |
|---------|---------|
| **审计日志** | `logs/audit/` |
| **错误日志** | `logs/error/` |
| **系统日志** | `logs/system/` |

### 日志轮转配置

**保留期限**: 90天
**压缩策略**: 超过7天的日志自动压缩
**归档策略**: 超过90天的日志自动归档

---

## ✅ 验证任务配置

### 手动测试任务

```powershell
# 测试快速审计
python scripts\periodic_audit_executor.py quick

# 测试标准审计
python scripts\periodic_audit_executor.py standard

# 测试深度审计
python scripts\periodic_audit_executor.py deep
```

### 查看任务状态

```powershell
# 查看所有任务
Get-ScheduledTask | Where-Object {$_.TaskName -like "ZephyrAlpha*"}

# 查看任务详情
Get-ScheduledTask -TaskName "ZephyrAlpha_Quick_Audit" | Format-List *

# 查看任务历史
Get-ScheduledTaskInfo -TaskName "ZephyrAlpha_Quick_Audit"
```

---

## 🔧 故障排除

### 常见问题

1. **任务未执行**
   - 检查任务是否启用
   - 检查触发器配置
   - 检查用户权限

2. **任务执行失败**
   - 检查Python路径
   - 检查脚本路径
   - 检查工作目录

3. **任务超时**
   - 调整任务超时设置
   - 优化审计脚本性能

---

## 📝 维护记录

| 日期 | 操作 | 操作人 | 备注 |
|------|------|--------|------|
| 2026-04-07 | 创建配置指南 | Audit Sentinel | 初始创建 |

---

**配置状态**: ✅ 已创建
**下次更新**: 根据实际使用情况调整
