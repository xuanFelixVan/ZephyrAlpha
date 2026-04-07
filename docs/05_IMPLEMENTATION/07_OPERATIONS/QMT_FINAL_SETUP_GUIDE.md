---
module_id: QMT_FINAL_SETUP_GUIDE
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: QMT_FINAL_SETUP_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
responsibility:
  - 实施指南、部署文档
  - 交易执行
  - 文档治理
standard_type: 专业量化机构指南
applicable_scope: 全系统
compliance_level: 专业标准---


# QMT Final Setup Guide
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


## Current Status

?**Completed Successfully:**

1. **Miniconda installed** at `E:\Miniconda`
2. **Python 3.12 environment** created as `qmt`
3. **xtquant library** installed and working
4. **Data interface** connected successfully (gets 5196 stocks)
5. **Permissions verified** (strategy trading permission exists)
6. **Configuration updated** with correct paths

?**Remaining Issue:**

**QMT trading interface connection returns -1**

This means:
- ?Data interface works (xtdata connects)
- ?Trading interface fails (xttrader returns -1)

## Root Cause Analysis

The most common cause for return code -1 is:


When you login to QMT, you must check the "Minimal Mode" or "Independent Trading" checkbox.

## Immediate Action Required

### Step 1: Logout of QMT (if currently logged in)

1. Close QMT client completely
2. Make sure no QMT processes are running

### Step 2: Login with Minimal Mode

2. **On login screen:**
   - Account: `8886156677`
   - Password: `134752`
   - Click "Login"
3. **Wait 30 seconds** for full initialization

### Step 3: Test Connection

Open PowerShell in `D:\ZephyrAlpha` and run:

```powershell
# Option 1: Use activation script
.\scripts\activate_qmt_simple.ps1

# Then run test (if you created the alias)
qmtpython scripts\test_qmt_connection_v6.py

# OR directly
C:\Users\fanzi\.conda\envs\qmt\python.exe scripts\test_qmt_connection_v6.py
```

### Step 4: Expected Results

If successful:
```

If still failing (returns -1):
```
```

## If Still Failing

### Double-check these items:

1. **QMT Version:** Should be 2.0.8.300 (yours is correct)
2. **Installation Paths:**
3. **File Permissions:** Diagnosis shows write permission is OK
4. **Session Conflict:** Try different session by waiting 5 minutes or restarting computer

### Advanced Troubleshooting

Run these diagnostic scripts:

```powershell
# Run in QMT Python environment
C:\Users\fanzi\.conda\envs\qmt\python.exe scripts\diagnose_qmt_permission.py
C:\Users\fanzi\.conda\envs\qmt\python.exe scripts\diagnose_qmt_deep.py
```

### Contact Support

If still failing after confirming Minimal Mode login:

1. **Contact Guojin Securities:** 95310
2. **Check official documentation:**
   - https://dict.thinktrader.net/
   - https://www.xuntou.net/

## Configuration Files

### `.env.qmt` (sensitive - DO NOT SHARE)
```
QMT_SIMULATION_ACCOUNT=8886156677
QMT_SIMULATION_PASSWORD=134752

QMT_LIVE_ACCOUNT=8887871993
QMT_LIVE_PASSWORD=198910
```

### Python Environment
- **Path:** `C:\Users\fanzi\.conda\envs\qmt`
- **Python:** 3.12.13 (64-bit)
- **xtquant:** 250516.1.1

## Quick Test Commands

```powershell
# 1. Check Python version
C:\Users\fanzi\.conda\envs\qmt\python.exe --version

# 2. Test xtquant import
C:\Users\fanzi\.conda\envs\qmt\python.exe -c "import xtquant; print('OK')"

# 3. Run quick connection test
C:\Users\fanzi\.conda\envs\qmt\python.exe scripts\test_qmt_connection_v6.py

# 4. Create aliases (for convenience)
Set-Alias qmtpython "C:\Users\fanzi\.conda\envs\qmt\python.exe"
Set-Alias qmtpip "C:\Users\fanzi\.conda\envs\qmt\Scripts\pip.exe"
```

## Next Steps After Successful Connection

Once connection succeeds:

1. **Start QMT Executor Development** (Layer 5: Strategy Execution)
2. **Implement order management functions**
3. **Integrate with ZephyrAlpha system**
4. **Create comprehensive test suite**

## Summary

**The only remaining issue is QMT client login mode.**

All technical preparations are complete:
- ?Python 3.12 environment ready
- ?xtquant library installed
- ?Configuration files correct
- ?Permissions verified
- ?Data interface working

**You just need to ensure QMT is logged in with "Minimal Mode" checked.**

---

**Last Updated:** 2026-04-03  
**Status:** Awaiting QMT client configuration  
**Estimated Time to Fix:** 2-5 minutes (login with correct mode)
