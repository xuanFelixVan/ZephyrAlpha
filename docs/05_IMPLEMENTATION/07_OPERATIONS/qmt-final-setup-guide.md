---
module_id: QMT_FINAL_SETUP_GUIDE
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - QMT_FINAL_SETUP操作指南
layer: layer_05
standard_type: 专业量化机构指南
applicable_scope: 全系统
compliance_level: 专业标准---
> **核心职责**: 文档内容说明
?**Completed Successfully: **
1. **Miniconda installed** at `E: \Miniconda`
?**Remaining Issue: **
This means:
  - ?Data interface works (xtdata connects)
  - ?Trading interface fails (xttrader returns -1)
2. **On login screen: **
The most common cause for return code -1 is:
  - Account: `8886156677`
  - Password: `134752`
  - Click "Login"
Open PowerShell in `D: "\ZephyrAlpha` and run:"
C: \Users\fanzi\.conda\envs\qmt\python.exe scripts\test_qmt_connection_v6.py
1. **QMT Version: ** Should be 2.0.8.300 (yours is correct)
2. **Installation Paths: **
3. **File Permissions: ** Diagnosis shows write permission is OK
4. **Session Conflict: ** Try different session by waiting 5 minutes or restarting computer
1. **Contact Guojin Securities: ** 95310
2. **Check official documentation: **
If still failing after confirming Minimal Mode login:
  - https://dict.thinktrader.net/
  - https://www.xuntou.net/
- **Path: "** `C:\Users\fanzi\.conda\envs\qmt`"
- **Python: ** 3.12.13 (64-bit)
- **xtquant: ** 250516.1.1
Set-Alias qmtpython "C: \Users\fanzi\.conda\envs\qmt\python.exe"
Set-Alias qmtpip "C: \Users\fanzi\.conda\envs\qmt\Scripts\pip.exe"
1. **Start QMT Executor Development** (Layer 5: Strategy Execution)
All technical preparations are complete:
  - ?Python 3.12 environment ready
  - ?xtquant library installed
  - ?Configuration files correct
  - ?Permissions verified
  - ?Data interface working
---
**Last Updated:** 2026-04-03  

**Status:** Awaiting QMT client configuration  

**Estimated Time to Fix:** 2-5 minutes (login with correct mode)

```

