---
standard_type: ﮒ؟ﮔﺛﮔﮒ
applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨ?
compliance_level: ﮔ­۲ﮒﺙﮔ ﮒ
parent_document: ../CONFIGURATION/SCHEDULED_AUDIT_CONFIGURATION.md
implementation_status: ﮒﺓﺎﮒ؟ﮔ?
owner: ﮔﮔ۰۲ﻝ؟۰ﻝﮒ?
responsibility:
  - 审计报告、合规检查
version: 1.0.0
module_id: SCHEDULED_TASKS_DEPLOYMENT_GUIDE
created_date: 2026-04-02
last_updated: 2026-04-02
---
---

# ﮒ؟ﮔﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻠ۷ﻝﺛﺎﮔﮒ
> **核心职责**: 使用指南和教程
> **职责边界**: 
> - ✅ 本文档负责：使用指南和教程相关内容
> - ❌ 本文档不负责：其他模块内容


**ﮔﮔ۰۲ﻝﮔ؛**: 1.0.0
**ﮔﮒﮔﺑﮔ?*: 2026-04-02
**ﮔﮔ۰۲ﮔﮔﻟ?*: ﮔﮔ۰۲ﻝ؟۰ﻝﮒ?

---

## 1. ﻠ۷ﻝﺛﺎﮔ۵ﻟﺟﺍ

### 1.1 ﻠ۷ﻝﺛﺎﻝ؟ﮔ 

ﮒ۷Windowsﻝﺏﭨﻝﭨﻛﺕﻠ۷ﻝﺛﺎZephyrAlphaﮔﮔ۰۲ﮔﺎﭨﻝﮒ؟ﮔﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﺅﺙﮒ؟ﻝﺍﻟ۹ﮒ۷ﮒﮔﮔ۰۲ﻟﺑ۷ﻠﻝﮔ۶ﻙ?

### 1.2 ﻠ۷ﻝﺛﺎﮒﮒ؟ﺗ

| ﻛﭨﭨﮒ۰ﮒﻝ۶ﺍ | ﻠ۱ﻝ | ﮔ۶ﻟ۰ﮔﭘﻠﺑ | ﮒ؟۰ﻟ؟۰ﮒﮒ؟ﺗ |
|---------|------|----------|----------|
| **ﮒﺟ،ﻠﮒ؟۰ﻟ؟?* | ﮔﺁﮒ۷ﻛﺕ | ﮒﮔ۷2:00 | ﻠﺝﮔ۴ﮔﮔﮔ۶ﻙﮒﮔﺍﮔ؟ﮒ؟ﮔﺑﮔ?|
| **ﮔ ﮒﮒ؟۰ﻟ؟۰** | ﮔﺁﮔ1ﮔ?| ﮒﮔ۷3:00 | ﮔﮔ۰۲ﮒﻝﺎﭨﻙﮒﺛﮒﻟ۶ﻟﻙﻝﺑ۱ﮒﺙﮒ؟ﮔﺑﮔ?|
| **ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰** | ﮔﺁﮒ­۲ﮒﭦ۵ﻠ۵ﮔ?| ﮒﮔ۷3:00 | ﻛﺕﮒﺎﮒ؟۰ﻟ؟۰ﺅﺙL1-L3ﺅﺙﻙﻛﭦﮒ۳۶ﮒﮒﻝ؛۵ﮒﮔ?|

### 1.3 ﻠ۷ﻝﺛﺎﮒﻝﺛ؟ﮔ۰ﻛﭨﭘ

- [x] Windows 10/Windows Server 2016ﮔﮔﺑﻠ،ﻝﮔ?
- [x] Python 3.8ﮔﮔﺑﻠ،ﻝﮔ?
- [x] ﻝ؟۰ﻝﮒﮔﻠ?
- [x] ﻠ۰ﺗﻝ؟ﮒﺓﺎﮒﻠﮒﺍﮔ؛ﮒﺍ

---

## 2. ﻠ۷ﻝﺛﺎﮔ­۴ﻠ۹۳

### 2.1 ﮔ­۴ﻠ۹۳1: ﮒﮒ۳ﻝﺁﮒ۱

**ﮔ۲ﮔ۴Pythonﻝﺁﮒ۱**:
```powershell
# ﮔ۲ﮔ۴Pythonﻝﮔ؛
python --version

# ﮒﭦﻟﺁ۴ﮔﺝﻝ۳ﭦ: Python 3.8.x ﮔﮔﺑﻠ،ﻝﮔ?
```

**ﮔ۲ﮔ۴ﻠ۰ﺗﻝ؟ﻝ؟ﮒﺛ?*:
```powershell
# ﻟﺟﮒ۴ﻠ۰ﺗﻝ؟ﻝ؟ﮒﺛ
cd D:\ZephyrAlpha

# ﮔ۲ﮔ۴ﻟﮔ؛ﮔﺁﮒ۵ﮒ­ﮒ?
ls scripts\scheduled_*.py
```

### 2.2 ﮔ­۴ﻠ۹۳2: ﮔﭖﻟﺁﮒ؟۰ﻟ؟۰ﻟﮔ؛

**ﻟﺟﻟ۰ﻠ۷ﻝﺛﺎﻟﮔ؛ﮔﭖﻟﺁ**:
```powershell
# ﻛﭨ۴ﻝ؟۰ﻝﮒﻟﭦ،ﻛﭨﺛﻟﺟﻟ۰PowerShell
# ﮔﭖﻟﺁﻟﮔ؛ﮒﻛﭨﭨﮒ?
.\scripts\deploy_scheduled_tasks.ps1 -Action Test -ProjectRoot "D:\ZephyrAlpha"
```

**ﮔﮒ۷ﮔﭖﻟﺁﻟﮔ؛**:
```powershell
# ﮔﭖﻟﺁﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﻟﮔ?
python scripts\scheduled_quick_audit.py

# ﮔﭖﻟﺁﮔ ﮒﮒ؟۰ﻟ؟۰ﻟﮔ؛
python scripts\scheduled_standard_audit.py

# ﮔﭖﻟﺁﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﻟﮔ؛
python scripts\scheduled_deep_audit.py
```

### 2.3 ﮔ­۴ﻠ۹۳3: ﮒ؟ﻟ۲ﮒ؟ﮔﻛﭨﭨﮒ۰

**ﮒ؟ﻟ۲ﻛﭨﭨﮒ۰**:
```powershell
# ﻛﭨ۴ﻝ؟۰ﻝﮒﻟﭦ،ﻛﭨﺛﻟﺟﻟ۰PowerShell
.\scripts\deploy_scheduled_tasks.ps1 -Action Install -ProjectRoot "D:\ZephyrAlpha"
```

**ﻠ۹ﻟﺁﮒ؟ﻟ۲**:
```powershell
# ﮔ۴ﻝﮒﺓﺎﮒ؟ﻟ۲ﻝﻛﭨﭨﮒ۰
Get-ScheduledTask | Where-Object {$_.TaskName -like "ZephyrAlpha*"}

# ﮔ۴ﻝﻛﭨﭨﮒ۰ﻟﺁ۵ﮔ
Get-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit" | Format-List *
```

### 2.4 ﮔ­۴ﻠ۹۳4: ﻠﻝﺛ؟ﮒ؟۰ﻟ؟۰ﻠﻝ۴ﺅﺙﮒﺁﻠﺅﺙ

**ﻝﺙﻟﺝﻠﻝ۴ﻠﻝﺛ؟**:
```yaml
# ﮔﻛﭨﭘ: config/audit_notification.yaml

email:
  enabled: true
  smtp_server: "smtp.example.com"
  smtp_port: 587
  sender: "audit@example.com"
  recipients:
    - "architect@example.com"
    - "doc-admin@example.com"
```

**ﮔﭖﻟﺁﻠ؟ﻛﭨﭘﻠﻝ۴**:
```powershell
# ﮒﻠﮔﭖﻟﺁﻠ؟ﻛﭨ?
python scripts\test_notification.py
```

---

## 3. ﻛﭨﭨﮒ۰ﻝ؟۰ﻝ

### 3.1 ﮔ۴ﻝﻛﭨﭨﮒ۰ﻝﭘﮔ?

**ﻛﺛﺟﻝ۷PowerShellﮔ۴ﻝ**:
```powershell
# ﮔ۴ﻝﮔﮔZephyrAlphaﻛﭨﭨﮒ۰
Get-ScheduledTask | Where-Object {$_.TaskName -like "ZephyrAlpha*"} | 
    Select-Object TaskName, State, NextRunTime, LastRunTime | 
    Format-Table -AutoSize

# ﮔ۴ﻝﻝﺗﮒ؟ﻛﭨﭨﮒ۰
Get-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit" | Format-List *
```

**ﻛﺛﺟﻝ۷ﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦﮔ۴ﻝ**:
1. ﮔﮒﺙ"ﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦ"ﺅﺙTask Schedulerﺅﺙ?
2. ﮒ۷ﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦﮒﭦﻛﺕ­ﮔﺝﮒ?ZephyrAlpha"ﻝﺕﮒﺏﻛﭨﭨﮒ۰
3. ﮔ۴ﻝ"ﻟ۶۵ﮒﮒ?ﻙ?ﮔﻛﺛ"ﻙ?ﮒﮒﺎﻟ؟ﺍﮒﺛ"ﻝ­ﻠﻠ۰ﺗﮒ?

### 3.2 ﮔﮒ۷ﻟﺟﻟ۰ﻛﭨﭨﮒ۰

**ﻛﺛﺟﻝ۷PowerShellﻟﺟﻟ۰**:
```powershell
# ﮔﮒ۷ﻟﺟﻟ۰ﮒﺟ،ﻠﮒ؟۰ﻟ؟?
Start-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit"

# ﮔﮒ۷ﻟﺟﻟ۰ﮔ ﮒﮒ؟۰ﻟ؟۰
Start-ScheduledTask -TaskName "ZephyrAlpha_Monthly_Audit"

# ﮔﮒ۷ﻟﺟﻟ۰ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰
Start-ScheduledTask -TaskName "ZephyrAlpha_Quarterly_Audit"
```

**ﮔﮒ۷ﻟﺟﻟ۰ﻟﮔ؛**:
```powershell
# ﻟﺟﻟ۰ﮒﺟ،ﻠﮒ؟۰ﻟ؟?
python scripts\scheduled_quick_audit.py

# ﻟﺟﻟ۰ﮔ ﮒﮒ؟۰ﻟ؟۰
python scripts\scheduled_standard_audit.py

# ﻟﺟﻟ۰ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰
python scripts\scheduled_deep_audit.py
```

### 3.3 ﻝ۵ﻝ۷/ﮒﺁﻝ۷ﻛﭨﭨﮒ۰

**ﻝ۵ﻝ۷ﻛﭨﭨﮒ۰**:
```powershell
Disable-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit"
```

**ﮒﺁﻝ۷ﻛﭨﭨﮒ۰**:
```powershell
Enable-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit"
```

### 3.4 ﮒﺕﻟﺛﺛﻛﭨﭨﮒ۰

**ﮒﺕﻟﺛﺛﮔﮔﻛﭨﭨﮒ?*:
```powershell
# ﻛﭨ۴ﻝ؟۰ﻝﮒﻟﭦ،ﻛﭨﺛﻟﺟﻟ۰
.\scripts\deploy_scheduled_tasks.ps1 -Action Uninstall -ProjectRoot "D:\ZephyrAlpha"
```

**ﮔﮒ۷ﮒﺕﻟﺛﺛﮒﻛﺕ۹ﻛﭨﭨﮒ۰**:
```powershell
Unregister-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit" -Confirm:$false
```

---

## 4. ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﮔ۴ﻝ

### 4.1 ﮔ۴ﮒﻛﺛﻝﺛ؟

ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﻟ۹ﮒ۷ﻛﺟﮒ­ﮒﺍﻛﭨ۴ﻛﺕﻛﺛﻝﺛ؟ﺅﺙ

```
D:\ZephyrAlpha\
ﻗﻗﻗ docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\
ﻗ?  ﻗﻗﻗ weekly_20260402.json          # ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?
ﻗ?  ﻗﻗﻗ monthly_20260402.json         # ﮔ ﮒﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
ﻗ?  ﻗﻗﻗ monthly_summary_20260402.md   # ﮔ ﮒﮒ؟۰ﻟ؟۰ﮔﻟ۵
ﻗ?  ﻗﻗﻗ quarterly_20260402.json       # ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
ﻗ?
ﻗﻗﻗ docs\09_AUDIT\REPORTS\
    ﻗﻗﻗ QUARTERLY_AUDIT_REPORT_20260402.md  # ﮒ­۲ﮒﭦ۵ﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
```

### 4.2 ﮔ۴ﻝﮔﮔﺍﮔ۴ﮒ?

**ﻛﺛﺟﻝ۷PowerShellﮔ۴ﻝ**:
```powershell
# ﮔ۴ﻝﮔﮔﺍﻝﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?
Get-ChildItem docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\weekly_*.json | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1 | 
    Get-Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# ﮔ۴ﻝﮔﮔﺍﻝﮔ ﮒﮒ؟۰ﻟ؟۰ﮔﻟ۵
Get-ChildItem docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\monthly_summary_*.md | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1 | 
    Get-Content
```

### 4.3 ﮔ۴ﮒﮒﮒ؟ﺗﻟﺁﺑﮔ

**ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?*:
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

**ﮔ ﮒﮒ؟۰ﻟ؟۰ﮔﻟ۵**:
```markdown
# ﮔﮒﭦ۵ﮔﮔ۰۲ﮒ؟۰ﻟ؟۰ﮔﻟ۵ﮔ۴ﮒ

**ﮒ؟۰ﻟ؟۰ﮔﭘﻠﺑ**: 2026-04-02T03:00:00

## ﮒ؟۰ﻟ؟۰ﮔ۵ﻟ۵

- ﮔ،ﮔﮔﻛﭨﭘﮔ? 456
- ﻠ؟ﻠ۱ﮔﭨﮔﺍ: 10

## ﻠ؟ﻠ۱ﮒﮒﺕ

- warning: 5ﻛﺕ?
- info: 5ﻛﺕ?

## ﻠ؟ﻠ۱ﻝﺎﭨﮒ

- broken_link: 3ﻛﺕ?
- missing_metadata: 4ﻛﺕ?
- non_standard_category: 3ﻛﺕ?
```

---

## 5. ﮔﻠﮔﮔ۴

### 5.1 ﻛﭨﭨﮒ۰ﮔ۹ﮔ۶ﻟ۰?

**ﮔ۲ﮔ۴ﻛﭨﭨﮒ۰ﻝﭘﮔ?*:
```powershell
Get-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit" | 
    Select-Object TaskName, State, LastRunTime, LastTaskResult
```

**ﮒﺁﻟﺛﮒﮒ ﮒﻟ۶۲ﮒﺏﮔﺗﮔﺏ?*:

| ﻠ؟ﻠ۱ | ﮒﮒ  | ﻟ۶۲ﮒﺏﮔﺗﮔﺏ |
|------|------|---------|
| ﻛﭨﭨﮒ۰ﻝﭘﮔﻛﺕﭦ"ﮒﺓﺎﻝ۵ﻝ? | ﻛﭨﭨﮒ۰ﻟ۱،ﻝ۵ﻝ?| ﮒﺁﻝ۷ﻛﭨﭨﮒ۰ |
| LastTaskResultﻛﺕﻛﺕﭦ0 | ﻟﮔ؛ﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ | ﮔ۴ﻝﮔ۴ﮒﺟﮔﻛﭨﭘ |
| LastRunTimeﻛﺕﭦﻝ۸ﭦ | ﻛﭨﭨﮒ۰ﻛﭨﮔ۹ﻟﺟﻟ۰ | ﮔﮒ۷ﻟﺟﻟ۰ﮔﭖﻟﺁ |
| ﻟ؟۰ﻝ؟ﮔﭦﻛﺙﻝ?| ﻝﭖﮔﭦﻟ؟ﺝﻝﺛ؟ﻠ؟ﻠ۱ | ﻟﺍﮔﺑﻝﭖﮔﭦﻟ؟ﺝﻝﺛ؟ |

**ﮔ۴ﻝﮔ۴ﮒﺟ**:
```powershell
# ﮔ۴ﻝﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
Get-Content logs\quick_audit.log -Tail 50

# ﮔ۴ﻝWindowsﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦﮔ۴ﮒﺟ
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" | 
    Where-Object {$_.Message -like "*ZephyrAlpha*"} | 
    Select-Object -First 10
```

### 5.2 ﻟﮔ؛ﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴

**ﮔ۲ﮔ۴Pythonﻝﺁﮒ۱**:
```powershell
# ﮔ۲ﮔ۴Pythonﻝﮔ؛
python --version

# ﮔ۲ﮔ۴ﻛﺝﻟﭖﮒ
pip list | Select-String "pathlib|json|logging"
```

**ﮔ۲ﮔ۴ﻟﮔ؛ﻟﺓﺁﮒﺝ?*:
```powershell
# ﮔ۲ﮔ۴ﻟﮔ؛ﮔﺁﮒ۵ﮒ­ﮒ?
Test-Path scripts\scheduled_quick_audit.py

# ﮔ۲ﮔ۴ﮒﺓ۴ﻛﺛﻝ؟ﮒﺛ?
Get-Location
```

**ﮔﮒ۷ﻟﺟﻟ۰ﮔﭖﻟﺁ**:
```powershell
# ﮒﮔ۱ﮒﺍﻠ۰ﺗﻝ؟ﻝ؟ﮒﺛ?
cd D:\ZephyrAlpha

# ﮔﮒ۷ﻟﺟﻟ۰ﻟﮔ؛
python scripts\scheduled_quick_audit.py
```

### 5.3 ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﮔ۹ﻝﮔ?

**ﮔ۲ﮔ۴ﻟﺝﮒﭦﻝ؟ﮒﺛ?*:
```powershell
# ﮔ۲ﮔ۴ﻝ؟ﮒﺛﮔﺁﮒ۵ﮒ­ﮒ?
Test-Path docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state

# ﮔ۲ﮔ۴ﻝ؟ﮒﺛﮔﻠ?
Get-Acl docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state | Format-List
```

**ﮔ۲ﮔ۴ﻝ۲ﻝﻝ۸ﭦﻠ?*:
```powershell
# ﮔ۲ﮔ۴ﻝ۲ﻝﻝ۸ﭦﻠ?
Get-PSDrive D | Select-Object Used, Free
```

---

## 6. ﻝﭨﺑﮔ۳ﮒﭨﭦﻟ؟؟

### 6.1 ﮒ؟ﮔﮔ۲ﮔ?

**ﮔﺁﮒ۷ﮔ۲ﮔ?*:
- ﮔ۴ﻝﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?
- ﮔ۲ﮔ۴ﻛﭨﭨﮒ۰ﮔ۶ﻟ۰ﻝﭘﮔ?
- ﮒ۳ﻝﮒﻝﺍﻝﻠ؟ﻠ۱?

**ﮔﺁﮔﮔ۲ﮔ?*:
- ﮔ۴ﻝﮔ ﮒﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
- ﮔ۲ﮔ۴ﻝ۲ﻝﻝ۸ﭦﻠ?
- ﮔﺕﻝﻟﺟﮔﮔ۴ﮒ

**ﮔﺁﮒ­۲ﮒﭦ۵ﮔ۲ﮔ?*:
- ﮔ۴ﻝﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﮔ۴ﮒ
- ﻟﺁﻛﺙﺍﮒ؟۰ﻟ؟۰ﮔﮔ
- ﻛﺙﮒﮒ؟۰ﻟ؟۰ﻟ۶ﮒ

### 6.2 ﮔ۴ﮒﮒﺛﮔ۰۲

**ﮔﮒ۷ﮒﺛﮔ۰۲**:
```powershell
# ﮒﮒﭨﭦﮒﺛﮔ۰۲ﻝ؟ﮒﺛ
New-Item -ItemType Directory -Path "docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\archive\2026\Q1" -Force

# ﻝ۶ﭨﮒ۷ﮔ۶ﮔ۴ﮒ?
Move-Item docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\weekly_202601*.json `
    -Destination "docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\archive\2026\Q1\"
```

**ﻟ۹ﮒ۷ﮒﺛﮔ۰۲**:
```powershell
# ﻟﺟﻟ۰ﮔﺕﻝﻟﮔ؛
python scripts\cleanup_audit_reports.py
```

### 6.3 ﮔ۶ﻟﺛﻛﺙﮒ

**ﻛﺙﮒﮒ؟۰ﻟ؟۰ﻠﮒﭦ۵**:
- ﮒﮒﺍﮔ،ﮔﮔﻛﭨﭘﮔﺍﻠﺅﺙﮔﻠ۳ﻛﺕﮒﺟﻟ۵ﻝﻝ؟ﮒﺛﺅﺙ
- ﻟﺍﮔﺑﮒ؟۰ﻟ؟۰ﻟ۶ﮒﺅﺙﮒ۹ﮔ۲ﮔ۴ﮒﺏﻠ؟ﻠ؟ﻠ۱ﺅﺙ
- ﻛﺛﺟﻝ۷ﮒﺗﭘﻟ۰ﮒ۳ﻝﺅﺙﮒ۵ﮔﮔﺁﮔﺅﺙ

**ﻛﺙﮒﻝ۲ﻝﻛﺛﺟﻝ۷**:
- ﮒ؟ﮔﮔﺕﻝﻟﺟﮔﮔ۴ﮒ
- ﮒﻝﺙ۸ﮒﺛﮔ۰۲ﮔ۴ﮒ
- ﻝﮔ۶ﻝ۲ﻝﻝ۸ﭦﻠﺑ

---

## 7. ﮒﻟﮔﮔ۰?

- [ﮒ؟ﮔﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻠﻝﺛ؟](09_AUDIT/CONFIGURATION/SCHEDULED_AUDIT_CONFIGURATION.md)
- [ﮔﮔ۰۲ﮔﺎﭨﻝﮔﭖﻝ۷ﮔ ﮒ](09_AUDIT/STANDARDS/DOCUMENT_GOVERNANCE_PROCESS_STANDARD.md)
<!-- ﻠﺝﮔ۴ﻝ؟ﮔ ﻛﺕﮒ­ﮒ۷ﮒﺓﺎﮔﺏ۷ﻠ: - [ﮔﮔ۰۲ﮒ؟۰ﻟ؟۰ﮒﺓ۴ﮒﺓﻛﺛﺟﻝ۷ﮔﮒ](../../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/DOCUMENT_AUDITOR_SPECIFICATION.md) -->


---

## 8. ﮒﺟ،ﻠﮒﻟ?

### ﮒﺕﺕﻝ۷ﮒﺛﻛﭨ۳

```powershell
# ﮒ؟ﻟ۲ﻛﭨﭨﮒ۰
.\scripts\deploy_scheduled_tasks.ps1 -Action Install

# ﮔﭖﻟﺁﻛﭨﭨﮒ۰
.\scripts\deploy_scheduled_tasks.ps1 -Action Test

# ﮒﺕﻟﺛﺛﻛﭨﭨﮒ۰
.\scripts\deploy_scheduled_tasks.ps1 -Action Uninstall

# ﮔ۴ﻝﻛﭨﭨﮒ۰ﻝﭘﮔ?
Get-ScheduledTask | Where-Object {$_.TaskName -like "ZephyrAlpha*"}

# ﮔﮒ۷ﻟﺟﻟ۰ﻛﭨﭨﮒ۰
Start-ScheduledTask -TaskName "ZephyrAlpha_Weekly_Audit"

# ﮔ۴ﻝﮔﮔﺍﮔ۴ﮒ?
Get-ChildItem docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\*.json | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1
```

---

**ﮔﮔ۰۲ﻝﭘﮔ?*: ﮔ­۲ﮒﺙﮔ ﮒ
**ﻛﺕﮔ؛۰ﮒ؟۰ﮔ۴**: 2026-07-02
