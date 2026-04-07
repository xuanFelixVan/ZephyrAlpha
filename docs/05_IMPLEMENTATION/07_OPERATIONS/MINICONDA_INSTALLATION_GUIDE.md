---
module_id: MINICONDA_INSTALLATION_GUIDE
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: MINICONDA_002
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
responsibility:
  - 操作指南编写与使用说明与系统维护管理
standard_type: 专业量化机构指南
applicable_scope: 全系统
compliance_level: 专业标准
---
---


# Minicondaﮒ؟ﻟ۲ﮔﮒﺅﺙ?ﮒﻠﺅﺙ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

## ﻭ ﮒ؟ﻟ۲ﮔ۴ﻠ۹۳

### ﮔ۴ﻠ۹۳1: ﻛﺕﻟﺛﺛMinicondaﺅﺙ?ﮒﻠﺅﺙ?
1. ﮔﮒﺙﮔﭖﻟ۶ﮒ۷ﺅﺙﻟ؟ﺟﻠ؟ﺅﺙ?   ```
   https://docs.conda.io/en/latest/miniconda.html
   ```

2. ﮒﻛﺕﮔﭨﮒ۷ﮒ?Windows installers"ﻠ۷ﮒ

3. ﻝﺗﮒﭨﻛﺕﻟﺛﺛﺅﺙ?   ```
   Miniconda3 Windows 64-bit
   ```
   ﮔﻛﭨﭘﮒﻝﺎﭨﻛﺙﺙﺅﺙ`Miniconda3-latest-Windows-x86_64.exe`

---

### ﮔ۴ﻠ۹۳2: ﮒ؟ﻟ۲Minicondaﺅﺙ?ﮒﻠﺅﺙ?
1. ﮒﮒﭨﻟﺟﻟ۰ﻛﺕﻟﺛﺛﻝﮒ؟ﻟ۲ﻝ۷ﮒﭦ?
2. ﮔ؛۱ﻟﺟﻝﻠ۱ﺅﺙﻝﺗﮒ?**Next**

3. ﻟ؟ﺕﮒﺁﮒﻟ؟؟ﺅﺙﻝﺗﮒ?**I Agree**

4. ﮒ؟ﻟ۲ﻝﺎﭨﮒﺅﺙﻠﮔ۸ **Just Me (recommended)**ﺅﺙﻝﺗﮒ?**Next**

5. ﮒ؟ﻟ۲ﻟﺓﺁﮒﺝﺅﺙﻛﺛﺟﻝ۷ﻠﭨﻟ؟۳ﻟﺓﺁﮒﺝﺅﺙﻝﺗﮒﭨ **Next**

6. ﻠ،ﻝﭦ۶ﻠﻠ۰ﺗﺅﺙﻠﻟ۵ﺅﺙﺅﺙﺅﺙ
   - ﻗ?**ﮒﺝﻠ?* "Add Miniconda3 to my PATH environment variable"
   - ﻗ?**ﮒﺝﻠ?* "Register Miniconda3 as my default Python"
   - ﻝﺗﮒﭨ **Install**

7. ﻝﮒﺝﮒ؟ﻟ۲ﮒ؟ﮔﺅﺙﻝﺗﮒ?**Next**ﺅﺙﻝﭘﮒﻝﺗﮒ?**Finish**

---

### ﮔ۴ﻠ۹۳3: ﻠﮒﺁﻝﭨﻝ،ﺁﺅﺙ?0ﻝ۶ﺅﺙ

1. **ﮒﺏﻠﮒﺛﮒﮔﮔﻝﭨﻝ،ﺁﻝ۹ﮒ?*

2. **ﻠﮔﺍﮔﮒﺙﻛﺕﻛﺕ۹ﮔﺍﻝPowerShellﻝﭨﻝ،ﺁ**

---

### ﮔ۴ﻠ۹۳4: ﮒﮒﭨﭦPython 3.12ﻝﺁﮒ۱ﺅﺙ?ﮒﻠﺅﺙ?
ﮒ۷ﮔﺍﮔﮒﺙﻝﻝﭨﻝ،ﺁﻛﺕﻟﺟﻟ۰ﺅﺙ?
```powershell
# ﮒﮒﭨﭦﻝﺁﮒ۱
conda create -n qmt python=3.12 -y

# ﮔﺟﮔﺑﭨﻝﺁﮒ۱?conda activate qmt

# ﮒ؟ﻟ۲ﻛﺝﻟﭖ
pip install xtquant pandas numpy

# ﻠ۹ﻟﺁﮒ؟ﻟ۲
python --version
```

**ﻠ۱ﮔﻟﺝﮒﭦ**ﺅﺙ?```
Python 3.12.x
```

---

### ﮔ۴ﻠ۹۳5: ﮔﭖﻟﺁQMTﻟﺟﮔ۴ﺅﺙ?ﮒﻠﺅﺙ?
```powershell
# ﻝ۰؟ﻛﺟﮒ۷qmtﻝﺁﮒ۱ﻛﺕ?conda activate qmt

# ﻟﺟﻟ۰ﻠ۹ﻟﺁﻟﮔ؛
python scripts/verify_qmt_environment.py
```

**ﻠ۱ﮔﻝﭨﮔ**ﺅﺙ?```
ﻗ?Pythonﻝﮔ؛: 3.12.x
ﻗ?xtquantﮒﭦﮒﺁﻝ?ﻗ?XtAccountﻝﺎﭨﮒﺁﻝ?```

---

## ﻗﺅﺕ ﻠﻟ۵ﮔﻝ۳ﭦ

### ﮒ؟ﻟ۲ﮔﭘﮒﺟﻠ۰ﭨﮒﺝﻠPATHﻠﻠ۰ﺗﺅﺙ?
```
ﮒ؟ﻟ۲ﻝﻠ۱ﻝ۳ﭦﻛﺝﺅﺙ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ?Advanced Options                    ﻗ?ﻗ?                                    ﻗ?ﻗ?ﻗﺅﺕ Add Miniconda3 to my PATH        ﻗ?ﻗ?ﮒﺟﻠ۰ﭨﮒﺝﻠﺅﺙ
ﻗ?   environment variable             ﻗ?ﻗ?                                    ﻗ?ﻗ?ﻗﺅﺕ Register Miniconda3 as my        ﻗ?ﻗ?ﮒﭨﭦﻟ؟؟ﮒﺝﻠ?ﻗ?   default Python                   ﻗ?ﻗ?                                    ﻗ?ﻗ?[Install]  [Cancel]                 ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```

### ﮒ۵ﮔﮒﺟﻟ؟ﺍﮒﺝﻠPATHﻠﻠ۰ﺗ

ﻠﻟ۵ﮔﮒ۷ﮔﺓﭨﮒﮒﺍPATHﺅﺙ?1. ﮒﺏﻠ؟"ﮔ۳ﻝﭖﻟ? ﻗ?ﮒﺎﮔ?ﻗ?ﻠ،ﻝﭦ۶ﻝﺏﭨﻝﭨﻟ؟ﺝﻝﺛ؟
2. ﻝﺁﮒ۱ﮒﻠ ﻗ?ﻝﺏﭨﻝﭨﮒﻠ ﻗ?Path ﻗ?ﻝﺙﻟﺝ
3. ﮔﺓﭨﮒﻛﭨ۴ﻛﺕﻟﺓﺁﮒﺝﺅﺙ?   ```
C: （待补充）
C: （待补充）
C: （待补充）
   ```

---

## ﻭﺁ ﻠ۹ﻟﺁﮒ؟ﻟ۲ﮔﮒ

ﻟﺟﻟ۰ﻛﭨ۴ﻛﺕﮒﺛﻛﭨ۳ﺅﺙ?
```powershell
# ﮔ۲ﮔ۴condaﻝﮔ؛
conda --version
# ﮒﭦﮔﺝﻝ۳? conda 24.x.x

# ﮔ۲ﮔ۴Pythonﻝﮔ؛
python --version
# ﮒﭦﮔﺝﻝ۳? Python 3.12.x

# ﮔ۲ﮔ۴ﻝﺁﮒ۱ﮒﻟ۰?conda env list
# ﮒﭦﮔﺝﻝ۳? qmt ﻝﺁﮒ۱
```

---

## ﻭ ﻠﮒﺍﻠ؟ﻠ۱ﺅﺙ?
### ﻠ؟ﻠ۱1: condaﮒﺛﻛﭨ۳ﮔﺝﻛﺕﮒ?
**ﮒﮒ**ﺅﺙﮔ۹ﮒﺝﻠPATHﻠﻠ۰ﺗﮔﮔ۹ﻠﮒﺁﻝﭨﻝ،ﺁ

**ﻟ۶۲ﮒﺏ**ﺅﺙ?1. ﻠﮒﺁﻝﭨﻝ،ﺁ
2. ﮒ۵ﮔﻟﺟﻛﺕﻟ۰ﺅﺙﻠﮔﺍﮒ؟ﻟ۲ﮒﺗﭘﮒﺝﻠPATHﻠﻠ۰ﺗ

### ﻠ؟ﻠ۱2: Pythonﻝﮔ؛ﻛﭨﻝﭘﮔ?.13

**ﮒﮒ**ﺅﺙﮔ۹ﮔﺟﮔﺑﭨqmtﻝﺁﮒ۱

**ﻟ۶۲ﮒﺏ**ﺅﺙ?```powershell
conda activate qmt
python --version
```

### ﻠ؟ﻠ۱3: pipﮒ؟ﻟ۲ﮒ۳ﺎﻟﺑ۴

**ﮒﮒ**ﺅﺙﻝﺛﻝﭨﻠ؟ﻠ۱?
**ﻟ۶۲ﮒﺏ**ﺅﺙﻛﺛﺟﻝ۷ﮒﺛﮒﻠﮒ?```powershell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple xtquant pandas numpy
```

---

## ﻭ ﮒ؟ﻟ۲ﮒ؟ﮔﮒ?
1. **ﮒﺁﮒ۷QMTﮒ؟۱ﮔﺓﻝ،?*
   - ﮔﮒﺙﮒﺛﻠQMTﻟﺛﺁﻛﭨﭘ
   - ﻝﭨﮒﺛﮔﭘﮒﺝﻠﻙﮔﻝ؟ﮔ۷۰ﮒﺙﻙﮔﻙﻝ؛ﻝ،ﻛﭦ۳ﮔﻙ?
2. **ﮔﺟﮔﺑﭨqmtﻝﺁﮒ۱**
   ```powershell
   conda activate qmt
   ```

3. **ﻟﺟﻟ۰ﮔﭖﻟﺁﻟﮔ؛**
   ```powershell
   python scripts/test_qmt_connection_v4.py
   ```

4. **ﻠ۱ﮔﻝﭨﮔ**
   ```
   ﻗ?ﮔﺍﮔ؟ﮔ۴ﮒ۲ﻟﺟﮔ۴ﮔﮒ
   ﻗ?ﻛﭦ۳ﮔﮔ۴ﮒ۲ﻟﺟﮔ۴ﮔﮒ
   ﻗ?ﻟﺑ۵ﮔﺓﻟ؟۱ﻠﮔﮒ
   ```

---

**ﻠ۱ﻟ؟۰ﮔﭨﮔﭘﻠ?*: 5-7ﮒﻠ
