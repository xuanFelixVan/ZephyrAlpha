---
module_id: QMT_ENVIRONMENT_SETUP_SUMMARY
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: QMT_005
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
responsibility:
  - 实施指南、部署文档
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
---
---


# QMTﻝﺁﮒ۱ﻠﻝﺛ؟ﮒ؟ﮔﮔﭨﻝﭨ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


## ﻗ?ﮒﺓﺎﮒ؟ﮔﻝﻛﭨﭨﮒ۰

### 1. Minicondaﮒ؟ﻟ۲ﮒ؟ﮔ
- **ﮒ؟ﻟ۲ﻟﺓﺁﮒﺝ**: `E:\Miniconda`
- **ﻝﭘﮔ?*: ﮒﺓﺎﮒ؟ﻟ۲ﺅﺙﻛﺛPATHﮔ۹ﻟ۹ﮒ۷ﻠﻝﺛ؟ﺅﺙﻠﻟ۵ﮔﮒ۷ﮔﺓﭨﮒﺅﺙ

### 2. Python 3.12ﻝﺁﮒ۱ﮒﮒﭨﭦﮔﮒ
- **ﻝﺁﮒ۱ﮒﻝ۶ﺍ**: `qmt`
- **ﻝﺁﮒ۱ﻟﺓﺁﮒﺝ**: `C:\Users\fanzi\.conda\envs\qmt`
- **Pythonﻝﮔ؛**: 3.12.13 (64ﻛﺛ?
- **ﻝﭘﮔ?*: ﮒ؟ﮒ۷ﻝ؛۵ﮒxtquantﻟ۵ﮔﺎ

### 3. xtquantﮒﭦﮒ؟ﻟ۲ﮔﮒ?- **ﻝﮔ؛**: xtquant_250516.1.1
- **ﮒ؟ﻟ۲ﻛﺛﻝﺛ؟**: QMTﻝﺁﮒ۱ﻝsite-packages
- **APIﻝﭘﮔ?*: ﮒﺁﻝ۷ﺅﺙﮔXtAccountﻝﺎﭨﺅﺙﻛﺛﺟﻝ۷ﻟﺑ۵ﮔﺓﮒﻝ؛۵ﻛﺕﺎﺅﺙ

### 4. ﻠﻝﺛ؟ﮔ۲ﮔ۴ﻠﻟﺟ
- **ﻠﻝﺛ؟ﮔﻛﭨﭘ**: `.env.qmt` ﮒﮒ۷ﻛﺕﻠﻝﺛ؟ﮔ۲ﻝ۰?- **ﻟﺓﺁﮒﺝﻠﻝﺛ؟**: `E:/ﮒﺛﻠQMTﻛﭦ۳ﮔﻝ،ﺁﮔ۷۰ﮔ?userdata_mini` (ﮔ۲ﻝ۰؟)
- **ﮔﻠﮔ۲ﮔ?*: ﮔﻝﻝ۴ﻛﭦ۳ﮔﮔﻠ?(`up_queue_xtquant`ﮔﻛﭨﭘﮒﮒ۷)

### 5. ﮔﺍﮔ؟ﮔ۴ﮒ۲ﮔﭖﻟﺁﮔﮒ
- ﻗ?xtdataﻟﺟﮔ۴ﮔﮒ
- ﻗ?ﻟﺓﮒﮒ?196ﮒ۹ﻟ۰ﻝ۴۷ﮔﺍﮔ?- ﻗ?ﻟ۰ﮔﮔﮒ۰ﮒ۷ﻟﺟﮔ۴ﮔ۲ﮒﺕ?
---

## ﻭ ﮒﺛﮒﻠ؟ﻠ۱

### ﻛﭦ۳ﮔﮔ۴ﮒ۲ﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴ (ﻟﺟﮒﻝ?-1)

**ﮔﭖﻟﺁﻝﭨﮔ**:
```
ﻗ?ﮔﺍﮔ؟ﮔ۴ﮒ۲: ﻟﺟﮔ۴ﮔﮒ
ﻗ?ﻛﭦ۳ﮔﮔ۴ﮒ۲: ﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴ (ﻟﺟﮒﻝ?-1)
```

**ﮒﺁﻟﺛﮒﮒ** (ﮔﮒﺁﻟﺛﮔ۶ﮔﮒﭦ?:

1. **QMTﮒ؟۱ﮔﺓﻝ،ﺁﮔ۹ﻛﭨ۴ﮔﻝ؟ﮔ۷۰ﮒﺙﻝﭨﮒﺛ** (ﮔﮒﺁﻟﺛ)
   - ﻠﻟ۵ﮒﺝﻠﻙﮔﻝ؟ﮔ۷۰ﮒﺙﻙﮔﻙﻝ؛ﻝ،ﻛﭦ۳ﮔﻙ?   - ﻝﭨﮒﺛﻟﺑ۵ﮒﺓ: 8886156677

2. **QMTﮒ؟۱ﮔﺓﻝ،ﺁﮔ۹ﮒﺁﮒ۷**
   - ﻠﻟ۵ﮒﮒﺁﮒ۷QMTﻟﺛﺁﻛﭨﭘ

3. **Sessionﮒﺎﻝ۹**
   - ﮒﺍﻟﺁﻛﺕﮒﻝsession ID

4. **ﻟﺓﺁﮒﺝﮔﻠﻠ؟ﻠ۱**
- ﻛﺛﻟﺁﮔﮔﺝﻝ۳ﭦﮔﮒﮒ۴ﮔﻠ

---

## ﻭ ﻝ،ﮒﺏﮔﻛﺛ

### ﮔ۴ﻠ۹۳1: ﮒﺁﮒ۷ﮒﺗﭘﻝﭨﮒﺛQMTﮒ؟۱ﮔﺓﻝ،?
1. **ﮒﮒﭨﮔﮒﺙ** "ﮒﺛﻠﻟﺁﮒﺕQMTﻛﭦ۳ﮔﻝ،?
2. **ﮒ۷ﻝﭨﮒﺛﻝﻠ?*:
   - ﻟﺑ۵ﮒﺓ: `8886156677`
- ﮒﺁﻝ: `134752`
   - ﻗ?**ﮒﺝﻠﻙﮔﻝ؟ﮔ۷۰ﮒﺙﻙ?* (ﮒﺟﻠ۰ﭨ!)
   - ﻝﺗﮒﭨ"ﻝﭨﮒﺛ"

3. **ﻝ۰؟ﻟ؟۳ﻝﭨﮒﺛﮔﮒ**
- ﻝﮒﺍﻛﺕﭨﻝﻠ?   - ﻝﭘﮔﮔﮔﺝﻝ۳ﭦ"ﮒﺓﺎﻟﺟﮔ?

### ﮔ۴ﻠ۹۳2: ﮔﺟﮔﺑﭨQMTﻝﺁﮒ۱ﮒﺗﭘﮔﭖﻟﺁ?
**ﮔﺗﮔﺏA: ﻛﺛﺟﻝ۷ﮔﺟﮔﺑﭨﻟﮔ?* (ﮔ۷ﻟ)
```powershell
# ﻟﺟﻟ۰ﮔﺟﮔﺑﭨﻟﮔ?.\scripts\activate_qmt_env.ps1

# ﮔﻝ۶ﻟﮔ؛ﮔﻝ۳ﭦﮔﺟﮔﺑﭨﻝﺁﮒ۱?# ﻝﭘﮒﻟﺟﻟ۰ﮔﭖﻟﺁ
python scripts\test_qmt_connection_v6.py
```

**ﮔﺗﮔﺏB: ﻝﺑﮔ۴ﻛﺛﺟﻝ۷ﻝﺁﮒ۱Python**
```powershell
# ﻝﺑﮔ۴ﻛﺛﺟﻝ۷QMTﻝﺁﮒ۱ﻝPython
C:\Users\fanzi\.conda\envs\qmt\python.exe scripts\test_qmt_connection_v6.py
```

**ﮔﺗﮔﺏC: ﮒﮒﭨﭦﮒﺟ،ﮔﺓﮒﺛﻛﭨ۳**
```powershell
# ﻟ؟ﺝﻝﺛ؟ﮒ،ﮒ
Set-Alias qmtpython "C:\Users\fanzi\.conda\envs\qmt\python.exe"

# ﻛﺛﺟﻝ۷ﮒ،ﮒﮔﭖﻟﺁ
qmtpython scripts\test_qmt_connection_v6.py
```

### ﮔ۴ﻠ۹۳3: ﮒ۵ﮔﻛﭨﻝﭘﮒ۳ﺎﻟﺑ۴

ﻟﺟﻟ۰ﮔﺓﺎﮒﭦ۵ﻟﺁﮔ:
```powershell
C:\Users\fanzi\.conda\envs\qmt\python.exe scripts\diagnose_qmt_deep.py
```

ﮔ۲ﮔ۴QMTﻟﺟﻝ۷:
```powershell
# ﮔ۲ﮔ۴QMTﮔﺁﮒ۵ﮒ۷ﻟﺟﻟ۰?Get-Process | Where-Object {$_.ProcessName -like "*qmt*" -or $_.ProcessName -like "*think*"}
```

---

## ﻭ ﻠﻟ۵ﮔﻛﭨﭘﻛﺛﻝﺛ؟

### ﻠﻝﺛ؟ﮔﻛﭨﭘ
- `D:\ZephyrAlpha\.env.qmt` - QMTﻟﺑ۵ﮔﺓﻠﻝﺛ؟
- `D:\ZephyrAlpha\config\qmt_config.yaml` - ﻠﮔﮔﻠﻝﺛ?
### ﻟﮔ؛ﮔﻛﭨﭘ
- `scripts\activate_qmt_env.ps1` - ﻝﺁﮒ۱ﮔﺟﮔﺑﭨﻟﮔ?- `scripts\test_qmt_connection_v6.py` - ﮔﮔﺍﮔﭖﻟﺁﻟﮔ?- `scripts\verify_xtquant_simple.py` - ﻝﺁﮒ۱ﻠ۹ﻟﺁﻟﮔ؛

### ﻝﺁﮒ۱ﮔﻛﭨﭘ
- `E:\Miniconda` - Minicondaﮒ؟ﻟ۲ﻝ؟ﮒﺛ
- `C:\Users\fanzi\.conda\envs\qmt` - Python 3.12ﻝﺁﮒ۱

### QMTﮒ؟۱ﮔﺓﻝ،?- `E:\ﮒﺛﻠQMTﻛﭦ۳ﮔﻝ،ﺁﮔ۷۰ﮔ\` - QMTﮒ؟ﻟ۲ﻝ؟ﮒﺛ
- `E:\ﮒﺛﻠQMTﻛﭦ۳ﮔﻝ،ﺁﮔ۷۰ﮔ\userdata_mini\` - MiniQMTﮔﺍﮔ؟ﻝ؟ﮒﺛ

---

## ﻭﺅﺕ?ﮔﻠﮔﻠ۳

### ﻠ؟ﻠ۱1: condaﮒﺛﻛﭨ۳ﻛﺕﮒﺁﻝ?**ﻟ۶۲ﮒﺏ**: ﮔﮒ۷ﮔﺓﭨﮒPATH
```powershell
$env:Path = "E:\Miniconda;E:\Miniconda\Scripts;E:\Miniconda\Library\bin;$env:Path"
```

### ﻠ؟ﻠ۱2: ﮔﺝﻛﺕﮒﺍqmtﻝﺁﮒ۱
**ﻟ۶۲ﮒﺏ**: ﻠﮔﺍﮒﮒﭨﭦﻝﺁﮒ۱
```powershell
conda create --prefix "C:\Users\fanzi\.conda\envs\qmt" python=3.12 -y
```

### ﻠ؟ﻠ۱3: xtquantﮒﺁﺙﮒ۴ﮒ۳ﺎﻟﺑ۴
**ﻟ۶۲ﮒﺏ**: ﮒ۷qmtﻝﺁﮒ۱ﻛﺕﻠﮔﺍﮒ؟ﻟ۲?```powershell
# ﮔﺟﮔﺑﭨﻝﺁﮒ۱ﮒ
pip install --force-reinstall xtquant
```

### ﻠ؟ﻠ۱4: ﻟﺟﮔ۴ﻟﺟﮒ-1
**ﻟ۶۲ﮒﺏﮔ۲ﮔ۴ﮔﺕﮒ?*:
1. ﻗ?QMTﮒ؟۱ﮔﺓﻝ،ﺁﮒﺓﺎﮒﺁﮒ۷
2. ﻗ?ﻛﭨ۴ﮔﻝ؟ﮔ۷۰ﮒﺙﻝﭨﮒﺛ
3. ﻗ?ﻛﺛﺟﻝ۷ﮔ۲ﻝ۰؟ﻝﻟﺑ۵ﮒ?(8886156677)
4. ﻗ?ﻝﮒﺝQMTﮒ؟ﮒ۷ﮒﺁﮒ۷ (30ﻝ۶?
5. ﻗ?ﮒﺍﻟﺁﻛﺕﮒﻝsession ID

---

## ﻭ ﮔﮔﺁﻝﭘﮔ?
| ﻝﭨﻛﭨﭘ | ﻝﭘﮔ?| ﻝﮔ؛/ﻟﺓﺁﮒﺝ |
|------|------|----------|
| **Miniconda** | ﻗ?ﮒﺓﺎﮒ؟ﻟ۲?| E:\Miniconda |
| **Pythonﻝﺁﮒ۱** | ﻗ?ﮒﺓﺎﮒﮒﭨ?| Python 3.12.13 |
| **xtquantﮒﭦ?* | ﻗ?ﮒﺓﺎﮒ؟ﻟ۲?| xtquant_250516.1.1 |
| **ﮔﺍﮔ؟ﮔ۴ﮒ۲** | ﻗ?ﮔ۲ﮒﺕﺕ | xtdataﻟﺟﮔ۴ﮔﮒ |
| **ﻛﭦ۳ﮔﮔ۴ﮒ۲** | ﻗ?ﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴ | ﻟﺟﮒﻝ?-1 |
| **ﮔﻠ** | ﻗ?ﮔ۲ﮒﺕﺕ | ﮔﻝﻝ۴ﻛﭦ۳ﮔﮔﻠ?|
| **ﻠﻝﺛ؟ﮔﻛﭨﭘ** | ﻗ?ﮔ۲ﮒﺕﺕ | .env.qmt |

---

## ﻭﺁ ﻛﺕﻛﺕﮔ?
### ﮒ۵ﮔﻟﺟﮔ۴ﮔﮒ
1. **ﮒﺙﮒ۶ﮒﺙﮒQMTﮔ۶ﻟ۰ﮒ?*
- ﮒﭦﻛﭦLayer 5ﻝﻝ۴ﮔ۶ﻟ۰ﮒﺎ?   - ﮒ؟ﻝﺍﻟ؟۱ﮒﻝ؟۰ﻝﮒﻟﺛ
   - ﻠﮔﮒﺍZephyrAlphaﻝﺏﭨﻝﭨ

2. **ﮒ؟ﮒﮔﭖﻟﺁﮒ۴ﻛﭨﭘ**
- ﮔﺓﭨﮒﮒﮒﮔﭖﻟﺁ
   - ﮒﮒﭨﭦﮔ۷۰ﮔﻛﭦ۳ﮔﮔﭖﻟﺁ

3. **ﮔﮔ۰۲ﻝﺙﮒ**
   - QMTﮔ۶ﻟ۰ﮒ۷ﻛﺛﺟﻝ۷ﮔﮒ?   - ﮔﻠﮔﻠ۳ﮔﮒ

### ﮒ۵ﮔﻟﺟﮔ۴ﻛﭨﻝﭘﮒ۳ﺎﻟﺑ۴
1. **ﻟﻝﺏﭨﮒﺛﻠﻟﺁﮒﺕﮒ؟۱ﮔ** (95310)
   - ﻝ۰؟ﻟ؟۳ﻟﺑ۵ﮒﺓﮔﻠ
   - ﻟﺓﮒﮔﮔﺁﮔﺁﮔ?
2. **ﮔ۴ﻠﮒ؟ﮔﺗﮔﮔ۰۲**
   - https://dict.thinktrader.net/
   - https://www.xuntou.net/

3. **ﻝ۳ﺝﮒﭦﮔﺎﮒ۸**
   - ﻟﺟﮔﮒ؟ﮔﺗﻟ؟ﭦﮒ
   - ﻠﮒﻛﭦ۳ﮔﻝ۳ﺝﮒﭦ

---

## ﻭ ﮔﺁﮔﻟﭖﮔﭦ

### ﮒ؟ﮔﺗﮔﺁﮔ
- **ﮒﺛﻠﻟﺁﮒﺕﮒ؟۱ﮔ**: 95310
- **ﻟﺟﮔﻝ۴ﻟﺁﮒﭦ?*: https://dict.thinktrader.net/
- **ﮒ؟ﮔﺗﻟ؟ﭦﮒ**: https://www.xuntou.net/

### ﮔ؛ﮒﺍﮔﮔ۰۲
- `docs/05_IMPLEMENTATION/07_OPERATIONS/` - ﮔﻛﺛﮔﮔ۰۲
- `scripts/` - ﮔﭖﻟﺁﮒﻟﺁﮔﻟﮔ?
### ﻟﺁﮔﮒﺓ۴ﮒﺓ
- `diagnose_qmt_permission.py` - ﮔﻠﻟﺁﮔ
- `diagnose_qmt_deep.py` - ﮔﺓﺎﮒﭦ۵ﻟﺁﮔ
- `verify_xtquant_simple.py` - ﻝﺁﮒ۱ﻠ۹ﻟﺁ

---

**ﮔﮒﮔﺑﮔ?*: 2026-04-03  
**ﻝﺁﮒ۱ﻝﮔ؛**: v1.0  
**ﻠ۱ﻟ؟۰ﻟ۶۲ﮒﺏﮔﭘﻠﺑ**: 5-10ﮒﻠ (ﮒﮒﺏﻛﭦQMTﻝﭨﮒﺛﻝﭘﮔ?
