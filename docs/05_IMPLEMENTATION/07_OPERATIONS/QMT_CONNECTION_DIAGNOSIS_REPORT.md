---
module_id: QMT_CONNECTION_DIAGNOSIS_REPORT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: QMT_002
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
responsibility:
  - 系统审计分析与质量评估报告与改进建议
standard_type: 专业量化机构报告
applicable_scope: 全系统
compliance_level: 专业标准
---
---


# QMTﻟﺟﮔ۴ﻠ؟ﻠ۱ﮒ؟ﮔﺑﻟﺁﮔﮔ۴ﮒ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


**ﻟﺁﮔﮔﭘﻠﺑ**: 2026-04-03 19:35
**ﻟﺁﮔﮒﺁﺗﻟﺎ۰**: ﮒﺛﻠﻟﺁﮒﺕQMTﻛﭦ۳ﮔﻝ،ﺁﻟﺟﮔ۴ﻠ؟ﻠ۱?
**ﻟﺁﮔﻝﭨﮔ**: ﮒﻝﺍﮔﺗﮔ؛ﮒﮒﮒﺗﭘﮒﺓﺎﻠ۷ﮒﻛﺟ؟ﮒ۳

---

## ﻭ ﻟﺁﮔﮔﭨﻝﭨ

### ﻗ?ﮒﺓﺎﻝ۰؟ﻟ؟۳ﮔ۲ﮒﺕﺕﻝﻠ۷ﮒ

| ﮔ۲ﮔ۴ﻠ۰ﺗ | ﻝﭘﮔ?| ﻟﺁﺑﮔ |
|--------|------|------|
| **userdata_miniﮔﻛﭨﭘﮒ۳?* | ﻗ?ﮒﮒ۷ | ﻟﺓﺁﮒﺝﮔ۲ﻝ۰؟ |
| **up_queue_xtquantﮔﻛﭨﭘ** | ﻗ?ﮒﮒ۷ | ﻟﺑ۵ﮒﺓﮔﻝﻝ۴ﻛﭦ۳ﮔﮔﻠ?|
| **down_queueﮔﻛﭨﭘ** | ﻗ?ﮒﮒ۷ | ﻛﭦ۳ﮔﻠﮒﮔ۲ﮒﺕﺕ |
| **ﮒﮒ۴ﮔﻠ** | ﻗ?ﮔ۲ﮒﺕﺕ | ﮒﺁﻛﭨ۴ﮒﮒﭨﭦﮔﻛﭨﭘ |
| **xtdataﮔﺍﮔ؟ﮔ۴ﮒ۲** | ﻗ?ﮔﮒ | ﮒﺁﻛﭨ۴ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟ |
| **xtquantﮒﭦﮒ؟ﻟ۲?* | ﻗ?ﮒﺓﺎﮒ؟ﻟ۲?| ﻝﮔ؛: xtquant_250516 |

### ﻗ?ﮒﻝﺍﻝﻠ؟ﻠ۱?
| ﻠ؟ﻠ۱ | ﻛﺕ۴ﻠﻝ۷ﮒﭦ۵ | ﻝﭘﮔ?| ﮒﺛﺎﮒ |
|------|---------|------|------|
| **Pythonﻝﮔ؛ﻛﺕﮒﺙﮒ؟?* | ﻭﺑ ﻠ،?| ﻗ?ﮔ۹ﻛﺟ؟ﮒ۳?| APIﮒﺁﺙﮒ۴ﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﺟﮔ۴ﻟﺟﮒ?1 |
| **ﻟﺓﺁﮒﺝﮔﺙﮒﺙﻛﺕﮔ۲ﻝ۰?* | ﻭ۰ ﻛﺕ?| ﻗ?ﮒﺓﺎﻛﺟ؟ﮒ۳?| ﮒﺁﻟﺛﮒﺁﺙﻟﺑﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴ |
| **Sessionﮒﺎﻝ۹** | ﻭ۱ ﻛﺛ?| ﻗﺅﺕ  ﻠﮔﺏ۷ﮔ | ﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴ |

---

## ﻭ ﻟﺁ۵ﻝﭨﻟﺁﮔﻟﺟﻝ۷

### ﻠﭘﮔ؟ﭖ1: ﮒﮒ۶ﻟﺟﮔ۴ﮔﭖﻟﺁ

**ﮔﭖﻟﺁﻟﮔ؛**: `test_qmt_connection_v3.py`

**ﮔﭖﻟﺁﻝﭨﮔ**:
```
ﻗ?ﮔﺍﮔ؟ﮔ۴ﮒ۲ﮔﭖﻟﺁﮔﮒ - ﻟﺓﮒﮒ?5234 ﮒ۹ﻟ۰ﻝ۴?ﻗ?ﻛﭦ۳ﮔﮔ۴ﮒ۲ﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﺟﮒﻝ: -1
```

**ﮒﮔ۴ﻟﺁﮔ**: ﮔﺍﮔ؟ﮔ۴ﮒ۲ﮒﺁﻝ۷ﺅﺙﻛﭦ۳ﮔﮔ۴ﮒ۲ﻛﺕﮒﺁﻝ۷

---

### ﻠﭘﮔ؟ﭖ2: ﮔﻠﻟﺁﮔ

**ﻟﺁﮔﻟﮔ؛**: `diagnose_qmt_permission.py`

**ﮒﺏﻠ؟ﮒﻝﺍ**:
```
ﻗ?ﮔﺝﮒﺍ up_queue_xtquant ﮔﻛﭨﭘ (2 ﻛﺕ?
ﻗ?ﻟﺁﺑﮔﻟﺑ۵ﮒﺓﮔﻝﻝ۴ﻛﭦ۳ﮔﮔﻠ?```

**ﻝﭨﻟ؟ﭦ**: ﮔﻠ۳ﻛﭦﻟﺑ۵ﮒﺓﮔﻠﻠ؟ﻠ۱?
---

### ﻠﭘﮔ؟ﭖ3: ﮔﺓﺎﮒﭦ۵ﻟﺁﮔ

**ﻟﺁﮔﻟﮔ؛**: `diagnose_qmt_deep.py`

**ﮒﺏﻠ؟ﮒﻝﺍ**:

#### 1. ﻟﺓﺁﮒﺝﮔﺙﮒﺙﻠ؟ﻠ۱ ﻗ?ﮒﺓﺎﻛﺟ؟ﮒ۳?
**ﻠ؟ﻠ۱**:
```
ﻗ?ﻠﻟﺁﺁﻟﺓﺁﮒﺝ: E:/ﮒﺛﻠQMTﻛﭦ۳ﮔﻝ،ﺁﮔ۷۰ﮔ?bin.x64
ﻗ?ﮔ۲ﻝ۰؟ﻟﺓﺁﮒﺝ: E:/ﮒﺛﻠQMTﻛﭦ۳ﮔﻝ،ﺁﮔ۷۰ﮔ?userdata_mini
```

**ﮒ؟ﮔﺗﮔﮔ۰۲**:
> miniqmtﺅﺙﻟﺓﺁﮒﺝﮔﮒ؟ﮒﺍﮒ؟ﻟ۲ﻝ؟ﮒﺛﻛﺕ?`\userdata_mini` ﮔﻛﭨﭘﮒ۳?
**ﻛﺟ؟ﮒ۳ﮔﻛﺛ**:
- ﮒﺓﺎﮔﺑﮔ?`.env.qmt` ﮔﻛﭨﭘ
- ﮒﺍﻟﺓﺁﮒﺝﻛﭨ `bin.x64` ﮔﺗﻛﺕﭦ `userdata_mini`

#### 2. Pythonﻝﮔ؛ﻠ؟ﻠ۱ ﻗ?ﮔ۹ﻛﺟ؟ﮒ۳?
**ﻠ؟ﻠ۱**:
```
ﻗ?ﮒﺛﮒﻝﮔ؛: Python 3.13.12
ﻗ?ﮒ؟ﮔﺗﮔﺁﮔ: Python 3.6 - 3.12 (64ﻛﺛ?
```

**ﮒ؟ﮔﺗﮔﮔ۰۲**:
> XtQuant ﻝ؟ﮒﮔﻛﺝﻝﮒﭦﮒﮔ؛ 64 ﻛﺛ?Python 3.6ﻙ?.7ﻙ?.8ﻙ?.9ﻙ?.10ﻙ?.11ﻙ?.12ﻝﮔ؛

**ﮒﺛﺎﮒ**:
- `XtAccount` ﮒﺁﺙﮒ۴ﮒ۳ﺎﻟﺑ۴
- ﻛﭦ۳ﮔﮔ۴ﮒ۲ﻟﺟﮔ۴ﻟﺟﮒ -1

**ﻠﻟﺁﺁﻛﺟ۰ﮔﺁ**:
```
ﻗ?xtquantﮒﺁﺙﮒ۴ﮒ۳ﺎﻟﺑ۴: cannot import name 'XtAccount' from 'xtquant.xttrader'
```

---

## ﻭ ﻟ۶۲ﮒﺏﮔﺗﮔ۰

### ﻭﺑ ﻝ،ﮒﺏﻛﺟ؟ﮒ۳ﻠ۰ﺗﺅﺙﮒﺟﻠ۰ﭨﺅﺙ?
#### ﮒﮒﭨﭦPython 3.12ﻟﮔﻝﺁﮒ۱

**ﮔﺗﮔ۰1: ﻛﺛﺟﻝ۷condaﺅﺙﮔ۷ﻟﺅﺙ**

```bash
# ﮔ۴ﻠ۹۳1: ﮒﮒﭨﭦﻝﺁﮒ۱
conda create -n qmt python=3.12 -y

# ﮔ۴ﻠ۹۳2: ﮔﺟﮔﺑﭨﻝﺁﮒ۱?conda activate qmt

# ﮔ۴ﻠ۹۳3: ﮒ؟ﻟ۲ﻛﺝﻟﭖ
pip install xtquant pandas numpy

# ﮔ۴ﻠ۹۳4: ﻠ۹ﻟﺁﮒ؟ﻟ۲
python -c "import xtquant; print('ﻗ?xtquantﮒ؟ﻟ۲ﮔﮒ')"
```

**ﮔﺗﮔ۰2: ﻛﺛﺟﻝ۷venv**

```bash
# ﮒﮔﺅﺙﻠﻟ۵ﮒﮒ؟ﻟ۲Python 3.12

# ﮔ۴ﻠ۹۳1: ﻛﺕﻟﺛﺛPython 3.12
# ﻟ؟ﺟﻠ؟: https://www.python.org/downloads/
# ﻛﺕﻟﺛﺛ: Python 3.12.x (64ﻛﺛ?

# ﮔ۴ﻠ۹۳2: ﮒﮒﭨﭦﻟﮔﻝﺁﮒ۱
py -3.12 -m venv qmt_env

# ﮔ۴ﻠ۹۳3: ﮔﺟﮔﺑﭨﻝﺁﮒ۱?qmt_env\Scripts\activate  # Windows

# ﮔ۴ﻠ۹۳4: ﮒ؟ﻟ۲ﻛﺝﻟﭖ
pip install xtquant pandas numpy
```

---

### ﻭ۰ ﻠ۹ﻟﺁﻠﻝﺛ؟ﺅﺙﻠﻟ۵ﺅﺙ

#### 1. ﻠ۹ﻟﺁPythonﻝﮔ؛

```bash
python --version
# ﮒﭦﻟﺁ۴ﮔﺝﻝ۳ﭦ: Python 3.12.x

python -c "import sys; print(f'Python {sys.version}')"
# ﻝ۰؟ﻟ؟۳ﮔ?4ﻛﺛﻝﮔ?```

#### 2. ﻠ۹ﻟﺁxtquantﮒ؟ﻟ۲

```bash
python -c "import xtquant; print('ﻗ?xtquantﮒﺁﻝ۷')"
python -c "from xtquant import xtdata; print('ﻗ?xtdataﮒﺁﻝ۷')"
python -c "from xtquant.xttrader import XtQuantTrader; print('ﻗ?xttraderﮒﺁﻝ۷')"
```

#### 3. ﻠ۹ﻟﺁﻟﺓﺁﮒﺝﻠﻝﺛ؟

```bash
# ﮔ۲ﮔ?.env.qmt ﮔﻛﭨﭘ
cat .env.qmt

# ﻝ۰؟ﻟ؟۳ﻟﺓﺁﮒﺝﮔﺙﮒﺙﺅﺙ?# QMT_SIMULATION_CLIENT_PATH=E:/ﮒﺛﻠQMTﻛﭦ۳ﮔﻝ،ﺁﮔ۷۰ﮔ?userdata_mini
# QMT_LIVE_CLIENT_PATH=E:/ﮒﺛﻠQMTﻛﭦ۳ﮔﻝ،ﺁﮒ؟ﻝ?userdata_mini
```

---

### ﻭ۱ ﮔﭖﻟﺁﻟﺟﮔ۴ﺅﺙﮔﮒﮔ۴ﻠ۹۳ﺅﺙ

#### 1. ﮒﺁﮒ۷QMTﮒ؟۱ﮔﺓﻝ،?
```
1. ﮔﮒﺙﮒﺛﻠQMTﻟﺛﺁﻛﭨﭘ
2. ﮒ۷ﻝﭨﮒﺛﻝﻠ۱ﺅﺙﮒﺝﻠﻙﮔﻝ؟ﮔ۷۰ﮒﺙﻙﮔﻙﻝ؛ﻝ،ﻛﭦ۳ﮔﻙ?3. ﻟﺝﮒ۴ﻟﺑ۵ﮒﺓﮒﺁﻝﻝﭨﮒﺛ
4. ﻝ۰؟ﻟ؟۳ﻝﭨﮒﺛﮔﮒ
```

#### 2. ﻟﺟﻟ۰ﮔﭖﻟﺁﻟﮔ؛

```bash
# ﮔﺟﮔﺑﭨqmtﻝﺁﮒ۱
conda activate qmt

# ﻟﺟﻟ۰ﮔﭖﻟﺁ
python scripts/test_qmt_connection_v4.py
```

#### 3. ﻠ۱ﮔﻝﭨﮔ

```
ﻗ?ﮔﺍﮔ؟ﮔ۴ﮒ۲ﮔﭖﻟﺁﮔﮒ
ﻗ?ﻛﭦ۳ﮔﮔ۴ﮒ۲ﻟﺟﮔ۴ﮔﮒ
ﻗ?ﻟﺑ۵ﮔﺓﻟ؟۱ﻠﮔﮒ
ﻗ?ﻟﭖﻛﭦ۶ﮔ۴ﻟﺁ۱ﮔﮒ
```

---

## ﻭﺁ ﮔﺗﮔ؛ﮒﮒﮒﮔ

### ﻠ؟ﻠ۱ﻠﺝﮔ۰

```
Python 3.13 (ﻛﺕﮒﺙﮒ؟?
    ﻗ?xtquant APIﮒﺁﺙﮒ۴ﮒ۳ﺎﻟﺑ۴
ﻗ?XtAccountﻝﺎﭨﻛﺕﮒﮒ۷
    ﻗ?ﻛﭦ۳ﮔﮔ۴ﮒ۲ﻟﺟﮔ۴ﻟﺟﮒ-1
ﻗ?ﮔﮔﺏﻟﺟﻟ۰ﻝ۷ﮒﭦﮒﻛﭦ۳ﮔ?```

### ﻟ۶۲ﮒﺏﻠﺝﮔ۰

```
ﮒﮒﭨﭦPython 3.12ﻝﺁﮒ۱
ﻗ?ﮔ۲ﻝ۰؟ﮒ؟ﻟ۲xtquantﮒﭦ?    ﻗ?APIﮒﺁﺙﮒ۴ﮔﮒ
    ﻗ?ﻛﭦ۳ﮔﮔ۴ﮒ۲ﻟﺟﮔ۴ﮔﮒ
    ﻗ?ﮒﺁﻛﭨ۴ﻝ۷ﮒﭦﮒﻛﭦ۳ﮔ?```

---

## ﻭ ﮒﻟﮔﮔ۰?
### ﮒ؟ﮔﺗﮔﮔ۰۲

1. **ﻟﺟﮔﻝ۴ﻟﺁﮒﭦ?*: https://dict.thinktrader.net/
2. **Native APIﮔﮔ۰۲**: https://dict.thinktrader.net/nativeApi/start_now.html
3. **Inner APIﮔﮔ۰۲**: https://dict.thinktrader.net/innerApi/start_now.html

### ﻝ۳ﺝﮒﭦﻟﭖﮔﭦ

1. **ﻟﺟﮔﮒ؟ﮔﺗﻟ؟ﭦﮒ**: https://www.xuntou.net/
2. **ﮒﺛﻠMiniQMTﻟﺟﮔ۴ﻠ؟ﻠ۱**: https://www.xuntou.net/forum.php?mod=viewthread&tid=1705

### ﮔ؛ﮒﺍﮔﮔ۰۲

1. **PDFﻟﺁﺑﮔﮔﮔ۰۲**: `D:\ZephyrAlpha\ﻟﺟﮔQMTﮔﻠﻝﻝ۴ﻛﭦ۳ﮔﻝﺏﭨﻝﭨﻟﺁﺑﮔﮔﮔ۰?pdf`
2. **ﻟﺟﮔ۴ﮔﻠﮔﮔ۴**: `docs/05_IMPLEMENTATION/07_OPERATIONS/QMT_CONNECTION_TROUBLESHOOTING.md`
3. **MiniQMTﻝﭨﮒﺛﮔﮒ**: `docs/05_IMPLEMENTATION/07_OPERATIONS/QMT_MINIQMT_LOGIN_GUIDE.md`

---

## ﻗﺅﺕ  ﻠﻟ۵ﮔﻝ۳ﭦ

### Pythonﻝﮔ؛ﻟ۵ﮔﺎ

- ﻗ?**ﮒﺟﻠ۰ﭨﻛﺛﺟﻝ۷**: Python 3.6 - 3.12 (64ﻛﺛ?
- ﻗ?**ﻛﺕﮔﺁﮔ?*: Python 3.13+ ﮔ?32ﻛﺛﻝﮔ?
### QMTﮒ؟۱ﮔﺓﻝ،ﺁﻟ۵ﮔﺎ?
- ﻗ?**ﮒﺟﻠ۰ﭨﮒﺁﮒ۷**: QMTﮒ؟۱ﮔﺓﻝ،ﺁﮒﺟﻠ۰ﭨﮒﮒﺁﮒ۷
- ﻗ?**ﮒﺟﻠ۰ﭨﻝﭨﮒﺛ**: ﻛﭨ۴ﮔﻝ؟ﮔ۷۰ﮒﺙﮔﻝ؛ﻝ،ﻛﭦ۳ﮔﮔ۷۰ﮒﺙﻝﭨﮒﺛ?- ﻗ?**ﻟﺓﺁﮒﺝﮔ۲ﻝ۰؟**: ﻠﻝﺛ؟ﮔﻛﭨﭘﮔﮒ `userdata_mini` ﮔﻛﭨﭘﮒ۳?
### ﻟﺑ۵ﮒﺓﮔﻠﻟ۵ﮔﺎ

- ﻗ?**ﮒﺓﺎﻝ۰؟ﻟ؟?*: ﮔ۷ﻝﻟﺑ۵ﮒﺓﮔﻝﻝ۴ﻛﭦ۳ﮔﮔﻠ?- ﻗ?**ﮒﺓﺎﻝ۰؟ﻟ؟?*: up_queue_xtquantﮔﻛﭨﭘﮒﮒ۷

---

## ﻭ ﻛﺕﻛﺕﮔ۴ﻟ۰ﮒ?
### ﻝ،ﮒﺏﮔ۶ﻟ۰ﺅﺙﻛﭨﮒ۳۸ﺅﺙ

1. ﻗ?**ﮒﮒﭨﭦPython 3.12ﻝﺁﮒ۱**
   ```bash
   conda create -n qmt python=3.12 -y
   conda activate qmt
   pip install xtquant pandas numpy
   ```

2. ﻗ?**ﻠ۹ﻟﺁﻝﺁﮒ۱ﻠﻝﺛ؟**
   ```bash
   python --version
   python -c "import xtquant; print('ﻗ?ﮔﮒ')"
   ```

3. ﻗ?**ﻠﮔﺍﮔﭖﻟﺁﻟﺟﮔ۴**
   ```bash
   python scripts/test_qmt_connection_v4.py
   ```

### ﮒﻝﭨﻛﭨﭨﮒ۰ﺅﺙﮔ؛ﮒ۷ﺅﺙ

1. ﻭ **ﮔﺑﮔﺍﻠ۰ﺗﻝ؟ﮔﮔ۰۲**
   - ﻟ؟ﺍﮒﺛPythonﻝﮔ؛ﻟ۵ﮔﺎ
   - ﮔﺑﮔﺍﻝﺁﮒ۱ﻠﻝﺛ؟ﮔﮒ

2. ﻭ۶۹ **ﮒ؟ﮒﮔﭖﻟﺁﻟﮔ؛**
- ﮔﺓﭨﮒﮔﺑﮒ۳ﻠﻟﺁﺁﮒ۳ﻝ
- ﮒ۱ﮒﻟ۹ﮒ۷ﮒﻟﺁﮔ?
3. ﻭ **ﮒ؟ﻝﺍQMTﮔ۶ﻟ۰ﮒ?*
- ﮒﭦﻛﭦﮔﮒﻝﻟﺟﮔ۴ﮔﭖﻟﺁ?   - ﻠﮔﮒﺍLayer 5ﻝﻝ۴ﮔ۶ﻟ۰ﮒﺎ?
---

## ﻭ ﮔﮔﺁﮔﺁﮔ?
### ﮒ۵ﻠﻠ؟ﻠ۱

1. **ﮔ۲ﮔ۴Pythonﻝﮔ؛**: `python --version`
2. **ﮔ۲ﮔ۴xtquantﮒ؟ﻟ۲**: `pip show xtquant`
3. **ﮔ۲ﮔ۴QMTﮒ؟۱ﮔﺓﻝ،?*: ﻝ۰؟ﻟ؟۳ﮒﺓﺎﮒﺁﮒ۷ﮒﺗﭘﻝﭨﮒﺛ
4. **ﮔ۴ﻝﮔ۴ﮒﺟ**: ﻟﺟﻟ۰ﻟﺁﮔﻟﮔ؛ﮔ۴ﻝﻟﺁ۵ﻝﭨﻛﺟ۰ﮔﺁ

### ﻟﻝﺏﭨﮔﺗﮒﺙ

- **ﮒﺛﻠﻟﺁﮒﺕﮒ؟۱ﮔ**: 95310
- **ﻟﺟﮔﮒ؟ﮔﺗﻟ؟ﭦﮒ**: https://www.xuntou.net/

---

**ﮔ۴ﮒﻝﮔﮔﭘﻠﺑ**: 2026-04-03 19:35  
**ﻟﺁﮔﮒﺓ۴ﮒﺓﻝﮔ؛**: v4.0
**ﻛﺕﮔ؛۰ﮒ؟۰ﻟ؟۰ﮒﭨﭦﻟ؟؟**: ﻝﺁﮒ۱ﻠﻝﺛ؟ﮒ؟ﮔﮒﻠﮔﺍﮔﭖﻟﺁ?