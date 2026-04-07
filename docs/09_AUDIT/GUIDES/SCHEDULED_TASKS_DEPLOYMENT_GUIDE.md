---
module_id: SCHEDULED_TASKS_DEPLOYMENT_GUIDE
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - SCHEDULED_TASKS_DEPLOYMENT操作指南
---

﻿---
standard_type: ﮒ؟ﮔﺛﮔﮒ
applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨ?
compliance_level: ﮔ۲ﮒﺙﮔﮒ
parent_document: ../CONFIGURATION/SCHEDULED_AUDIT_CONFIGURATION.md
implementation_status: ﮒﺓﺎﮒ؟ﮔ?
owner: ﮔﮔ۰۲ﻝ؟۰ﻝﮒ?
responsibility:
  - 操作指南编写与使用说明与系统维护管理
version: 1.0.0
module_id: SCHEDULED_TASKS_DEPLOYMENT_GUIDE
created_date: 2026-04-02
last_updated: 2026-04-02
---
---

# ﮒ؟ﮔﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻠ۷ﻝﺛﺎﮔﮒ
> **核心职责**: 使用指南和教程
> **职责边界**: 
> - ✅ 本文档负责：使用指南和教程相关内容
> - ❌ 本文档不负责：其他模块内容


**ﮔﮔ۰۲ﻝﮔ؛**: 1.0.0
**ﮔﮒﮔﺑﮔ?*: 2026-04-02
**ﮔﮔ۰۲ﮔﮔﻟ?*: ﮔﮔ۰۲ﻝ؟۰ﻝﮒ?

---

## 1. ﻠ۷ﻝﺛﺎﮔ۵ﻟﺟﺍ

### 1.1 ﻠ۷ﻝﺛﺎﻝ؟ﮔ

ﮒ۷Windowsﻝﺏﭨﻝﭨﻛﺕﻠ۷ﻝﺛﺎZephyrAlphaﮔﮔ۰۲ﮔﺎﭨﻝﮒ؟ﮔﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﺅﺙﮒ؟ﻝﺍﻟ۹ﮒ۷ﮒﮔﮔ۰۲ﻟﺑ۷ﻠﻝﮔ۶ﻙ?

### 1.2 ﻠ۷ﻝﺛﺎﮒﮒ؟ﺗ

| ﻛﭨﭨﮒ۰ﮒﻝ۶ﺍ | ﻠ۱ﻝ | ﮔ۶ﻟ۰ﮔﭘﻠﺑ | ﮒ؟۰ﻟ؟۰ﮒﮒ؟ﺗ |
|---------|------|----------|----------|
| **ﮒﺟ،ﻠﮒ؟۰ﻟ؟?* | ﮔﺁﮒ۷ﻛﺕ | ﮒﮔ۷2:00 | ﻠﺝﮔ۴ﮔﮔﮔ۶ﻙﮒﮔﺍﮔ؟ﮒ؟ﮔﺑﮔ?|
| **ﮔﮒﮒ؟۰ﻟ؟۰** | ﮔﺁﮔ1ﮔ?| ﮒﮔ۷3:00 | ﮔﮔ۰۲ﮒﻝﺎﭨﻙﮒﺛﮒﻟ۶ﻟﻙﻝﺑ۱ﮒﺙﮒ؟ﮔﺑﮔ?|
| **ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰** | ﮔﺁﮒ۲ﮒﭦ۵ﻠ۵ﮔ?| ﮒﮔ۷3:00 | ﻛﺕﮒﺎﮒ؟۰ﻟ؟۰ﺅﺙL1-L3ﺅﺙﻙﻛﭦﮒ۳۶ﮒﮒﻝ؛۵ﮒﮔ?|

### 1.3 ﻠ۷ﻝﺛﺎﮒﻝﺛ؟ﮔ۰ﻛﭨﭘ

- [x] Windows 10/Windows Server 2016ﮔﮔﺑﻠ،ﻝﮔ?
- [x] Python 3.8ﮔﮔﺑﻠ،ﻝﮔ?
- [x] ﻝ؟۰ﻝﮒﮔﻠ?
- [x] ﻠ۰ﺗﻝ؟ﮒﺓﺎﮒﻠﮒﺍﮔ؛ﮒﺍ

---

## 2. ﻠ۷ﻝﺛﺎﮔ۴ﻠ۹۳

### 2.1 ﮔ۴ﻠ۹۳1: ﮒﮒ۳ﻝﺁﮒ۱

**ﮔ۲ﮔ۴Pythonﻝﺁﮒ۱**:
```powershell
# ﮔ۲ﮔ۴Pythonﻝﮔ؛
python --version

# ﮒﭦﻟﺁ۴ﮔﺝﻝ۳ﭦ: Python 3.8.x ﮔﮔﺑﻠ،ﻝﮔ?
```

**ﮔ۲ﮔ۴ﻠ۰ﺗﻝ؟ﻝ؟ﮒﺛ?*:
```powershell
# ﻟﺟﮒ۴ﻠ۰ﺗﻝ؟ﻝ؟ﮒﺛ
cd D:\ZephyrAlpha

# ﮔ۲ﮔ۴ﻟﮔ؛ﮔﺁﮒ۵ﮒﮒ?
ls scripts\scheduled_*.py
```

### 2.2 ﮔ۴ﻠ۹۳2: ﮔﭖﻟﺁﮒ؟۰ﻟ؟۰ﻟﮔ؛

**ﻟﺟﻟ۰ﻠ۷ﻝﺛﺎﻟﮔ؛ﮔﭖﻟﺁ**:
```powershell
# ﻛﭨ۴ﻝ؟۰ﻝﮒﻟﭦ،ﻛﭨﺛﻟﺟﻟ۰PowerShell
# ﮔﭖﻟﺁﻟﮔ؛ﮒﻛﭨﭨﮒ?
.\scripts\deploy_scheduled_tasks.ps1 -Action Test -ProjectRoot "D:\ZephyrAlpha"
```

**ﮔﮒ۷ﮔﭖﻟﺁﻟﮔ؛**:
```powershell
# ﮔﭖﻟﺁﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﻟﮔ?
python scripts\scheduled_quick_audit.py

# ﮔﭖﻟﺁﮔﮒﮒ؟۰ﻟ؟۰ﻟﮔ؛
python scripts\scheduled_standard_audit.py

# ﮔﭖﻟﺁﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﻟﮔ؛
python scripts\scheduled_deep_audit.py
```

### 2.3 ﮔ۴ﻠ۹۳3: ﮒ؟ﻟ۲ﮒ؟ﮔﻛﭨﭨﮒ۰

**ﮒ؟ﻟ۲ﻛﭨﭨﮒ۰**:
```powershell
# ﻛﭨ۴ﻝ؟۰ﻝﮒﻟﭦ،ﻛﭨﺛﻟﺟﻟ۰PowerShell
.\scripts\deploy_scheduled_tasks.ps1 -Action Install -ProjectRoot "D:\ZephyrAlpha"
```

**ﻠ۹ﻟﺁﮒ؟ﻟ۲**:
```powershell
# ﮔ۴ﻝﮒﺓﺎﮒ؟ﻟ۲ﻝﻛﭨﭨﮒ۰
Get-ScheduledTask | Where-Object {$_.TaskName -like "ZephyrAlpha*"}

# ﮔ۴ﻝﻛﭨﭨﮒ۰ﻟﺁ۵ﮔ
Get-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit" | Format-List *
```

### 2.4 ﮔ۴ﻠ۹۳4: ﻠﻝﺛ؟ﮒ؟۰ﻟ؟۰ﻠﻝ۴ﺅﺙﮒﺁﻠﺅﺙ

**ﻝﺙﻟﺝﻠﻝ۴ﻠﻝﺛ؟**:
```yaml
# ﮔﻛﭨﭘ: config/audit_notification.yaml

email:
  enabled: true
  smtp_server: "smtp.example.com"
  smtp_port: 587
  sender: "audit@example.com"
  recipients:
    - "architect@example.com"
    - "doc-admin@example.com"
```

**ﮔﭖﻟﺁﻠ؟ﻛﭨﭘﻠﻝ۴**:
```powershell
# ﮒﻠﮔﭖﻟﺁﻠ؟ﻛﭨ?
python scripts\test_notification.py
```

---

## 3. ﻛﭨﭨﮒ۰ﻝ؟۰ﻝ

### 3.1 ﮔ۴ﻝﻛﭨﭨﮒ۰ﻝﭘﮔ?

**ﻛﺛﺟﻝ۷PowerShellﮔ۴ﻝ**:
```powershell
# ﮔ۴ﻝﮔﮔZephyrAlphaﻛﭨﭨﮒ۰
Get-ScheduledTask | Where-Object {$_.TaskName -like "ZephyrAlpha*"} | 
    Select-Object TaskName, State, NextRunTime, LastRunTime | 
    Format-Table -AutoSize

# ﮔ۴ﻝﻝﺗﮒ؟ﻛﭨﭨﮒ۰
Get-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit" | Format-List *
```

**ﻛﺛﺟﻝ۷ﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦﮔ۴ﻝ**:
1. ﮔﮒﺙ"ﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦ"ﺅﺙTask Schedulerﺅﺙ?
2. ﮒ۷ﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦﮒﭦﻛﺕﮔﺝﮒ?ZephyrAlpha"ﻝﺕﮒﺏﻛﭨﭨﮒ۰
3. ﮔ۴ﻝ"ﻟ۶۵ﮒﮒ?ﻙ?ﮔﻛﺛ"ﻙ?ﮒﮒﺎﻟ؟ﺍﮒﺛ"ﻝﻠﻠ۰ﺗﮒ?

### 3.2 ﮔﮒ۷ﻟﺟﻟ۰ﻛﭨﭨﮒ۰

**ﻛﺛﺟﻝ۷PowerShellﻟﺟﻟ۰**:
```powershell
# ﮔﮒ۷ﻟﺟﻟ۰ﮒﺟ،ﻠﮒ؟۰ﻟ؟?
Start-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit"

# ﮔﮒ۷ﻟﺟﻟ۰ﮔﮒﮒ؟۰ﻟ؟۰
Start-ScheduledTask -TaskName "ZephyrAlpha_Monthly_Audit"

# ﮔﮒ۷ﻟﺟﻟ۰ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰
Start-ScheduledTask -TaskName "ZephyrAlpha_Quarterly_Audit"
```

**ﮔﮒ۷ﻟﺟﻟ۰ﻟﮔ؛**:
```powershell
# ﻟﺟﻟ۰ﮒﺟ،ﻠﮒ؟۰ﻟ؟?
python scripts\scheduled_quick_audit.py

# ﻟﺟﻟ۰ﮔﮒﮒ؟۰ﻟ؟۰
python scripts\scheduled_standard_audit.py

# ﻟﺟﻟ۰ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰
python scripts\scheduled_deep_audit.py
```

### 3.3 ﻝ۵ﻝ۷/ﮒﺁﻝ۷ﻛﭨﭨﮒ۰

**ﻝ۵ﻝ۷ﻛﭨﭨﮒ۰**:
```powershell
Disable-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit"
```

**ﮒﺁﻝ۷ﻛﭨﭨﮒ۰**:
```powershell
Enable-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit"
```

### 3.4 ﮒﺕﻟﺛﺛﻛﭨﭨﮒ۰

**ﮒﺕﻟﺛﺛﮔﮔﻛﭨﭨﮒ?*:
```powershell
# ﻛﭨ۴ﻝ؟۰ﻝﮒﻟﭦ،ﻛﭨﺛﻟﺟﻟ۰
.\scripts\deploy_scheduled_tasks.ps1 -Action Uninstall -ProjectRoot "D:\ZephyrAlpha"
```

**ﮔﮒ۷ﮒﺕﻟﺛﺛﮒﻛﺕ۹ﻛﭨﭨﮒ۰**:
```powershell
Unregister-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit" -Confirm:$false
```

---

## 4. ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﮔ۴ﻝ

### 4.1 ﮔ۴ﮒﻛﺛﻝﺛ؟

ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﻟ۹ﮒ۷ﻛﺟﮒﮒﺍﻛﭨ۴ﻛﺕﻛﺛﻝﺛ؟ﺅﺙ

```
D:\ZephyrAlpha\
ﻗﻗﻗ docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\
ﻗ?  ﻗﻗﻗ weekly_20260402.json          # ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?
ﻗ?  ﻗﻗﻗ monthly_20260402.json         # ﮔﮒﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
ﻗ?  ﻗﻗﻗ monthly_summary_20260402.md   # ﮔﮒﮒ؟۰ﻟ؟۰ﮔﻟ۵
ﻗ?  ﻗﻗﻗ quarterly_20260402.json       # ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
ﻗ?
ﻗﻗﻗ docs\09_AUDIT\REPORTS\
ﻗﻗﻗ QUARTERLY_AUDIT_REPORT_20260402.md  # ﮒ۲ﮒﭦ۵ﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
```

### 4.2 ﮔ۴ﻝﮔﮔﺍﮔ۴ﮒ?

**ﻛﺛﺟﻝ۷PowerShellﮔ۴ﻝ**:
```powershell
# ﮔ۴ﻝﮔﮔﺍﻝﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?
Get-ChildItem docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\weekly_*.json | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1 | 
    Get-Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# ﮔ۴ﻝﮔﮔﺍﻝﮔﮒﮒ؟۰ﻟ؟۰ﮔﻟ۵
Get-ChildItem docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\monthly_summary_*.md | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1 | 
    Get-Content
```

### 4.3 ﮔ۴ﮒﮒﮒ؟ﺗﻟﺁﺑﮔ

**ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?*:
```json
{
  "summary": {
    "scan_time": "2026-04-02T02:00:00",
    "scanned_files": 456,
    "total_issues": 5,
    "issues_by_severity": {
      "warning": 3,
      "info": 2
    }
  },
  "details": {
    "link_issues": [...],
    "metadata_issues": [...]
  }
}
```

**ﮔﮒﮒ؟۰ﻟ؟۰ﮔﻟ۵**:
```markdown
# ﮔﮒﭦ۵ﮔﮔ۰۲ﮒ؟۰ﻟ؟۰ﮔﻟ۵ﮔ۴ﮒ

**ﮒ؟۰ﻟ؟۰ﮔﭘﻠﺑ**: 2026-04-02T03:00:00

## ﮒ؟۰ﻟ؟۰ﮔ۵ﻟ۵

- ﮔ،ﮔﮔﻛﭨﭘﮔ? 456
- ﻠ؟ﻠ۱ﮔﭨﮔﺍ: 10

## ﻠ؟ﻠ۱ﮒﮒﺕ

- warning: 5ﻛﺕ?
- info: 5ﻛﺕ?

## ﻠ؟ﻠ۱ﻝﺎﭨﮒ

- broken_link: 3ﻛﺕ?
- missing_metadata: 4ﻛﺕ?
- non_standard_category: 3ﻛﺕ?
```

---

## 5. ﮔﻠﮔﮔ۴

### 5.1 ﻛﭨﭨﮒ۰ﮔ۹ﮔ۶ﻟ۰?

**ﮔ۲ﮔ۴ﻛﭨﭨﮒ۰ﻝﭘﮔ?*:
```powershell
Get-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit" | 
    Select-Object TaskName, State, LastRunTime, LastTaskResult
```

**ﮒﺁﻟﺛﮒﮒﮒﻟ۶۲ﮒﺏﮔﺗﮔﺏ?*:

| ﻠ؟ﻠ۱ | ﮒﮒ | ﻟ۶۲ﮒﺏﮔﺗﮔﺏ |
|------|------|---------|
| ﻛﭨﭨﮒ۰ﻝﭘﮔﻛﺕﭦ"ﮒﺓﺎﻝ۵ﻝ? | ﻛﭨﭨﮒ۰ﻟ۱،ﻝ۵ﻝ?| ﮒﺁﻝ۷ﻛﭨﭨﮒ۰ |
| LastTaskResultﻛﺕﻛﺕﭦ0 | ﻟﮔ؛ﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ | ﮔ۴ﻝﮔ۴ﮒﺟﮔﻛﭨﭘ |
| LastRunTimeﻛﺕﭦﻝ۸ﭦ | ﻛﭨﭨﮒ۰ﻛﭨﮔ۹ﻟﺟﻟ۰ | ﮔﮒ۷ﻟﺟﻟ۰ﮔﭖﻟﺁ |
| ﻟ؟۰ﻝ؟ﮔﭦﻛﺙﻝ?| ﻝﭖﮔﭦﻟ؟ﺝﻝﺛ؟ﻠ؟ﻠ۱ | ﻟﺍﮔﺑﻝﭖﮔﭦﻟ؟ﺝﻝﺛ؟ |

**ﮔ۴ﻝﮔ۴ﮒﺟ**:
```powershell
# ﮔ۴ﻝﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
Get-Content logs\quick_audit.log -Tail 50

# ﮔ۴ﻝWindowsﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦﮔ۴ﮒﺟ
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" | 
    Where-Object {$_.Message -like "*ZephyrAlpha*"} | 
    Select-Object -First 10
```

### 5.2 ﻟﮔ؛ﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴

**ﮔ۲ﮔ۴Pythonﻝﺁﮒ۱**:
```powershell
# ﮔ۲ﮔ۴Pythonﻝﮔ؛
python --version

# ﮔ۲ﮔ۴ﻛﺝﻟﭖﮒ
pip list | Select-String "pathlib|json|logging"
```

**ﮔ۲ﮔ۴ﻟﮔ؛ﻟﺓﺁﮒﺝ?*:
```powershell
# ﮔ۲ﮔ۴ﻟﮔ؛ﮔﺁﮒ۵ﮒﮒ?
Test-Path scripts\scheduled_quick_audit.py

# ﮔ۲ﮔ۴ﮒﺓ۴ﻛﺛﻝ؟ﮒﺛ?
Get-Location
```

**ﮔﮒ۷ﻟﺟﻟ۰ﮔﭖﻟﺁ**:
```powershell
# ﮒﮔ۱ﮒﺍﻠ۰ﺗﻝ؟ﻝ؟ﮒﺛ?
cd D:\ZephyrAlpha

# ﮔﮒ۷ﻟﺟﻟ۰ﻟﮔ؛
python scripts\scheduled_quick_audit.py
```

### 5.3 ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﮔ۹ﻝﮔ?

**ﮔ۲ﮔ۴ﻟﺝﮒﭦﻝ؟ﮒﺛ?*:
```powershell
# ﮔ۲ﮔ۴ﻝ؟ﮒﺛﮔﺁﮒ۵ﮒﮒ?
Test-Path docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state

# ﮔ۲ﮔ۴ﻝ؟ﮒﺛﮔﻠ?
Get-Acl docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state | Format-List
```

**ﮔ۲ﮔ۴ﻝ۲ﻝﻝ۸ﭦﻠ?*:
```powershell
# ﮔ۲ﮔ۴ﻝ۲ﻝﻝ۸ﭦﻠ?
Get-PSDrive D | Select-Object Used, Free
```

---

## 6. ﻝﭨﺑﮔ۳ﮒﭨﭦﻟ؟؟

### 6.1 ﮒ؟ﮔﮔ۲ﮔ?

**ﮔﺁﮒ۷ﮔ۲ﮔ?*:
- ﮔ۴ﻝﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?
- ﮔ۲ﮔ۴ﻛﭨﭨﮒ۰ﮔ۶ﻟ۰ﻝﭘﮔ?
- ﮒ۳ﻝﮒﻝﺍﻝﻠ؟ﻠ۱?

**ﮔﺁﮔﮔ۲ﮔ?*:
- ﮔ۴ﻝﮔﮒﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
- ﮔ۲ﮔ۴ﻝ۲ﻝﻝ۸ﭦﻠ?
- ﮔﺕﻝﻟﺟﮔﮔ۴ﮒ

**ﮔﺁﮒ۲ﮒﭦ۵ﮔ۲ﮔ?*:
- ﮔ۴ﻝﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
- ﻟﺁﻛﺙﺍﮒ؟۰ﻟ؟۰ﮔﮔ
- ﻛﺙﮒﮒ؟۰ﻟ؟۰ﻟ۶ﮒ

### 6.2 ﮔ۴ﮒﮒﺛﮔ۰۲

**ﮔﮒ۷ﮒﺛﮔ۰۲**:
```powershell
# ﮒﮒﭨﭦﮒﺛﮔ۰۲ﻝ؟ﮒﺛ
New-Item -ItemType Directory -Path "docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\archive\2026\Q1" -Force

# ﻝ۶ﭨﮒ۷ﮔ۶ﮔ۴ﮒ?
Move-Item docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\weekly_202601*.json `
    -Destination "docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\archive\2026\Q1\"
```

**ﻟ۹ﮒ۷ﮒﺛﮔ۰۲**:
```powershell
# ﻟﺟﻟ۰ﮔﺕﻝﻟﮔ؛
python scripts\cleanup_audit_reports.py
```

### 6.3 ﮔ۶ﻟﺛﻛﺙﮒ

**ﻛﺙﮒﮒ؟۰ﻟ؟۰ﻠﮒﭦ۵**:
- ﮒﮒﺍﮔ،ﮔﮔﻛﭨﭘﮔﺍﻠﺅﺙﮔﻠ۳ﻛﺕﮒﺟﻟ۵ﻝﻝ؟ﮒﺛﺅﺙ
- ﻟﺍﮔﺑﮒ؟۰ﻟ؟۰ﻟ۶ﮒﺅﺙﮒ۹ﮔ۲ﮔ۴ﮒﺏﻠ؟ﻠ؟ﻠ۱ﺅﺙ
- ﻛﺛﺟﻝ۷ﮒﺗﭘﻟ۰ﮒ۳ﻝﺅﺙﮒ۵ﮔﮔﺁﮔﺅﺙ

**ﻛﺙﮒﻝ۲ﻝﻛﺛﺟﻝ۷**:
- ﮒ؟ﮔﮔﺕﻝﻟﺟﮔﮔ۴ﮒ
- ﮒﻝﺙ۸ﮒﺛﮔ۰۲ﮔ۴ﮒ
- ﻝﮔ۶ﻝ۲ﻝﻝ۸ﭦﻠﺑ

---

## 7. ﮒﻟﮔﮔ۰?

- ﮒ؟ﮔﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻠﻝﺛ؟
- ﮔﮔ۰۲ﮔﺎﭨﻝﮔﭖﻝ۷ﮔﮒ
<!-- ﻠﺝﮔ۴ﻝ؟ﮔﻛﺕﮒﮒ۷ﮒﺓﺎﮔﺏ۷ﻠ: - [ﮔﮔ۰۲ﮒ؟۰ﻟ؟۰ﮒﺓ۴ﮒﺓﻛﺛﺟﻝ۷ﮔﮒ](../../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/DOCUMENT_AUDITOR_SPECIFICATION.md) -->


---

## 8. ﮒﺟ،ﻠﮒﻟ?

### ﮒﺕﺕﻝ۷ﮒﺛﻛﭨ۳

```powershell
# ﮒ؟ﻟ۲ﻛﭨﭨﮒ۰
.\scripts\deploy_scheduled_tasks.ps1 -Action Install

# ﮔﭖﻟﺁﻛﭨﭨﮒ۰
.\scripts\deploy_scheduled_tasks.ps1 -Action Test

# ﮒﺕﻟﺛﺛﻛﭨﭨﮒ۰
.\scripts\deploy_scheduled_tasks.ps1 -Action Uninstall

# ﮔ۴ﻝﻛﭨﭨﮒ۰ﻝﭘﮔ?
Get-ScheduledTask | Where-Object {$_.TaskName -like "ZephyrAlpha*"}

# ﮔﮒ۷ﻟﺟﻟ۰ﻛﭨﭨﮒ۰
Start-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit"

# ﮔ۴ﻝﮔﮔﺍﮔ۴ﮒ?
Get-ChildItem docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\*.json | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1
```

---

**ﮔﮔ۰۲ﻝﭘﮔ?*: ﮔ۲ﮒﺙﮔﮒ
**ﻛﺕﮔ؛۰ﮒ؟۰ﮔ۴**: 2026-07-02
