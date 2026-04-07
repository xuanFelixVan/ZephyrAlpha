---
module_id: QMT_EXECUTOR_TECHNICAL_SPECIFICATION
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - QMT_EXECUTOR_TECHNICAL技术规范
---

﻿---
module_id: QMT_EXECUTOR_SPEC_001
version: 1.2.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-03
owner: ﻠ۵ﮒﺕﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 技术规格定义与实施标准制定与实施标准
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵
applicable_scope: Layer 5 ﻝﻝ۴ﮔ۶ﻟ۰ﺅﺟ?| ﻛﺕﮒ۰ﮔﭘﮔ: ﻛﺕﻝﭦ۶ﮔﭘﻠﺑﮔ۰ﮔﭘﻟﮒﮔﭘﮔ
compliance_level: ﻛﺕﻛﺕﮔﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﺅﺟ?
regulatory_compliance:
  - module: COMPLIANCE_CHECKER_001
    version: 1.0.0
    integration_date: 2026-04-03
---
---


# QMTExecutorﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﮔ۷۰ﮒﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.3 - QMTExecutorﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﮔ۷۰ﮒﻟﺁ۵ﻝﭨﮔﮔﺁﻟ؟ﺝﺅﺟ?
> **ﮔ۷۰ﮒID**: `QMT_EXECUTOR_001`
> **ﻝﮔ؛**: v1.0.0
> **ﻝﭘﺅﺟﺛ?*: ﺅﺟ?ﮔ۲ﮒﺙ


## 1. ﮔ۵ﻟﺟﺍ

### 1.1 ﻟ؟ﺝﻟ؟۰ﻟﮔﺁﻛﺕﻛﺕﮒ۰ﻝ؟ﺅﺟ?
- **ﻛﺕﮒ۰ﻠﺅﺟ?*: ﻝﺏﭨﻝﭨﻠﻟ۵ﻝﭨﻛﺕﻝﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﻟﺟﻟ۰ﮒ؟ﻝﻛﭦ۳ﮔﮔ۶ﻟ۰
- **ﮔﮔﺁﻝﺅﺟ?*: 
  - ﻛﭦ۳ﮔﮔ۶ﻟ۰ﻛﺕﻝ۷ﺏﮒ؟ﺅﺙﻝﺙﭦﻛﺗﻝﭨﻛﺕﻝﻟ؟۱ﮒﻝ؟۰ﻝﮒﮔ۶ﻟ۰ﮔﭦﮒﭘ
  - ﻟ؟۱ﮒﻝﭘﮔﻝﮔ۶ﮒﺍﻠﺝﺅﺙﻝﺙﭦﻛﺗﮒ؟ﮔﭘﻝﻟ؟۱ﮒﻝﭘﮔﻟﺓﺅﺟ?
  - ﻛﭦ۳ﮔﮒﺙﮒﺕﺕﮒ۳ﻝﻛﺕﻟﭘﺏﺅﺙﻝﺙﭦﻛﺗﮒ؟ﮒﻝﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﺅﺟ?
  - ﻛﭦ۳ﮔﻠ۲ﻠ۸ﮔ۶ﮒﭘﻝﺙﭦﮒ۳ﺎﺅﺙﻝﺙﭦﻛﺗﻛﭦ۳ﮔﮒﻝﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
- **ﻠ۱ﮔﻛﭨﺓﺅﺟﺛ?*: 
  - ﮒﭨﭦﻝ،ﻝﭨﻛﺕﻝﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒﻝ؟۰ﻝﮔﭦﮒﭘ
  - ﮔﻛﺝﮒ؟ﮔﭘﻝﻟ؟۱ﮒﻝﭘﮔﻝﮔ۶ﮒﻟﺓﻟﺕ۹
  - ﮒ؟ﻝﺍﮒ؟ﮒﻝﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘ
  - ﮔﺁﮔﻛﭦ۳ﮔﮒﻝﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒﮔ۶ﮒﭘ

### 1.2 ﮔﮔﺁﮒ؟ﻛﺛﻛﺕﮔﭘﮔﮒﺎﮒﺛﺅﺟ?
- **Layerﮒ؟ﻛﺛ**: Layer 5 - ﻝﻝ۴ﮔ۶ﻟ۰ﺅﺟ?(ﻝ؛۵ﮒARCHITECTURE.mdﮒ؟ﻛﺗ)
- **ﮔ۷۰ﮒﻝﺎﭨﮒ،**: ﮔﺕﮒﺟﻛﭦ۳ﮔﮔ۶ﻟ۰ﮔ۷۰ﮒ
- **ﮔﭘﮔﻟ۶ﻟﺎ**: Layer 5ﻝﻝ۴ﮔ۶ﻟ۰ﮔﺕﮒﺟﺅﺙﻟﺑﻟﺑ۲ﮒ؟ﻝﻛﭦ۳ﮔﮔ۶ﺅﺟ?

### 1.3 ﻝﮔ؛ﻛﺟ۰ﮔﺁ
| ﻝﮔ؛ | ﮔ۴ﮔ | ﻛﺛﺅﺟﺛ?| ﮒﮔﺑﻟﺁﺑﮔ | ﻝﭘﺅﺟﺛ?|
|------|------|------|----------|------|
| v1.0.0 | 2026-04-02 | ﻠ۵ﮒﺕﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟ | ﮒﮒ۶ﻝﮔ؛ | Active |
| v1.1.0 | 2026-04-03 | ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?| ﻠﮔﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﮔ۴ﮔ۷۰ﮒﺅﺙCOMPLIANCE_CHECKER_001ﺅﺙ?| Active |
| v1.2.0 | 2026-04-03 | ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?| ﮒ۱ﮒ"ﻠﻛﺟﻝﻟ۶۲"ﻝ،ﻟﺅﺙﮔﮒﮔﮔ۰۲ﮒﺁﻟﺁﭨﮔ?| Active |

### 1.4 ﻠﻛﺟﻝﻟ۶۲

#### 1.4.1 ﻛﺕﮒ۴ﻟﺁﻟ۶۲ﻠ

**QMTExecutor = ﮔ۷ﻝ"ﻛﭦ۳ﮔﮔ۶ﻟ۰ﻝ؟۰ﮒ؟ﭘ"**

ﮒﺍﺎﮒﮔ۷ﮔﻛﺕﻛﺕ۹ﻛﺕﻠ۷ﻝﻝ؟۰ﮒ؟ﭘﮒﺕ؟ﮔ۷ﮒ۳ﻝﮔﮔﻛﭦ۳ﮔﻝﺕﮒﺏﻝﻛﭦﮔﺅﺙﻝ۰؟ﻛﺟﻛﭦ۳ﮔﮒ؟ﮒ۷ﻙﮒﻟ۶ﻙﻠ،ﮔﮒﺍﮔ۶ﻟ۰ﻙ?
#### 1.4.2 ﮒ۷ﻛﭦ۳ﮔﮔﭖﻝ۷ﻛﺕﻝﻛﺛﻝﺛ?
```
ﻛﭦ۳ﮔﮒﺏﻝﮔﭖﻝ۷ﺅﺙ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ?ﻝﻝ۴ﻝﮔﻛﺟ۰ﮒﺓ ﻗ? Layer 3-4
ﻗ?(ﻛﺗﺍﮒ۴/ﮒﮒﭦ)  ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?       ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ?QMTExecutor ﻗ? ﻗ?ﻟﺟﻠﺅﺙﻛﭦ۳ﮔﮔ۶ﻟ۰ﻝ؟۰ﮒ؟?ﻗ? ﮔ۶ﻟ۰ﻛﭦ۳ﮔ    ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?       ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ?QMTﻛﭦ۳ﮔﮔ۴ﮒ۲  ﻗ? ﮒ؟ﻠﻛﺕﮒ
ﻗ?(ﮒﺕﮒﻝﺏﭨﻝﭨ)   ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```

#### 1.4.3 ﮔﺕﮒﺟﮒﻟﺛﻝﺎﭨﮔﺁ

**1. ﻟ؟۱ﮒﮔ۶ﻟ۰ = "ﻛﺕﮒﮒ?**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﻠ۳ﮒﻝﮔﮒ۰ﮒﺅﺙﮔﮔ۷ﻝﻟ؟۱ﮒﻠﮒﺍﮒ۷ﮔﺟﺅﺙﮒﺕﮒﻝﺏﭨﻝﭨﺅﺙ

```python
# ﻝﻝ۴ﻟﺁﺑﺅﺙﻛﺗﺍﮒ۴1000ﻟ۰ﮒﺗﺏﮒ؟ﻠﭘﻟ۰?strategy_signal = {
    "symbol": "000001.SZ",
    "action": "buy",
    "quantity": 1000,
    "price": 10.5
}

# QMTExecutorﻟﺑﻟﺑ۲ﺅﺙ?# 1. ﮔ۲ﮔ۴ﻟ؟۱ﮒﮔﺁﮒ۵ﮒﻝ?# 2. ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮒﻟ۶ﺅﺙﮔﺍﮒ۱ﺅﺙﺅﺙ
# 3. ﻟﺛ؛ﮔ۱ﻛﺕﭦQMTﮔﺙﮒﺙ
# 4. ﮔﻛﭦ۳ﻝﭨﮒﺕﮒﻝﺏﭨﻝﭨ?qmt_executor.execute_order(strategy_signal)
```

**2. ﻟ؟۱ﮒﻝﮔ۶ = "ﻟ؟۱ﮒﻟﺓﻟﺕ۹ﮒ?**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﮒﺟ،ﻠﻟﺟﺛﻟﺕ۹ﻝﺏﭨﻝﭨﺅﺙﮒ؟ﮔﭘﮔ۴ﻝﻟ؟۱ﮒﻝﭘﮔ?
```python
# ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﻝﭘﮔ?status = qmt_executor.get_order_status("ORDER_001")

# ﮒﺁﻟﺛﻝﻝﭘﮔﺅﺙ
# - pending: ﮒﺝﮔﻛﭦ?# - submitted: ﮒﺓﺎﮔﻛﭦ?# - partial_filled: ﻠ۷ﮒﮔﻛﭦ۳
# - filled: ﮒ؟ﮒ۷ﮔﻛﭦ۳
# - cancelled: ﮒﺓﺎﮔ۳ﻠ
# - rejected: ﮒﺓﺎﮔﻝﭨ?```

**3. ﻠ۲ﻠ۸ﮔ۶ﮒﭘ = "ﮒ؟ﮒ۷ﮔ۲ﮔ۴ﮒ"**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﮔﭦﮒﭦﮒ؟ﮔ۲ﺅﺙﮒ۷ﻝﭨﮔﭦﺅﺙﻛﺕﮒﺅﺙﮒﻟﺟﻟ۰ﮒ؟ﮒ۷ﮔ۲ﮔ?
```python
# ﻛﺕﮒﮒﻟ۹ﮒ۷ﮔ۲ﮔ۴ﺅﺙ
# 1. ﻟﭖﻠﮔﺁﮒ۵ﮒﻟﭘﺏﺅﺙ?# 2. ﮔﻛﭨﮔﺁﮒ۵ﻟﭘﻠﺅﺙ?# 3. ﻛﭨﺓﮔﺙﮔﺁﮒ۵ﮒﻝﺅﺙ?# 4. ﮔﺁﮒ۵ﻟ۶۵ﮒﻠ۲ﮔ۶ﻟ۶ﮒﺅﺙ?
if not risk_checker.check_order(order):
    print("ﻟ؟۱ﮒﻟ۱،ﮔﻝﭨﺅﺙﻟﭖﻠﻛﺕﻟﭘﺏ")
```

**4. ﮒﻟ۶ﮔ۲ﮔ?= "ﮒﻟ۶ﮒ؟? ﻭ**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﻛﭦ۳ﻟ۵ﺅﺙﻝ۰؟ﻛﺟﮔ۷ﻝﻠ۸ﺝﻠ۸ﭘﺅﺙﻛﭦ۳ﮔﺅﺙﻝ؛۵ﮒﻛﭦ۳ﻠﻟ۶ﮒﺅﺙﻝﻝ؟۰ﻟ۵ﮔﺎﺅﺙ?
```python
# ﻛﺕﮒﮒﻟ۹ﮒ۷ﮔ۲ﮔ۴ﺅﺙ
# 1. ﮔﺁﮒ۵ﻟ۶۵ﮒﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﺅﺙ?# 2. ﮔ۳ﮒﻝﮔﺁﮒ۵ﻟﭘﮔﺅﺙ
# 3. ﮔﺁﮒ۵ﻟﺟﮒﻝﻝﭦﺟﻛﭦ۳ﮔﻟ۶ﮒﺅﺙ?# 4. ﻟ؟۱ﮒﮒﻝﮔﭘﻠﺑﮔﺁﮒ۵ﻟﭘﺏﮒ۳ﺅﺙ?
compliance_result = compliance_checker.check(order)
if not compliance_result.is_compliant:
    print("ﻟ؟۱ﮒﻟ۱،ﮔﻝﭨﺅﺙﻟﺟﮒﻝﻝ؟۰ﻟ۶ﮒ")
```

**5. ﮒﺙﮒﺕﺕﮒ۳ﻝ = "ﮔﻠﻛﺟ؟ﮒ۳ﮒﺕ?**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﮒﭨﻠ۱ﻝﮔ۴ﻟﺁﻝ۶ﺅﺙﮒ۳ﻝﮒﻝ۶ﻝ۹ﮒﻝﭘﮒﭖ

```python
# ﮒﺁﻟﺛﻝﮒﺙﮒﺕﺕﮔﮒﭖﺅﺙ
# - ﻝﺛﻝﭨﻛﺕﮔ
# - ﮒﺕﮒﻝﺏﭨﻝﭨﮔﻠ
# - ﻟ؟۱ﮒﻟ۱،ﮔﻝﭨ?# - ﮔﻛﭦ۳ﻛﭨﺓﮔﺙﮒﺙﮒﺕﺕ

# QMTExecutorﻟ۹ﮒ۷ﮒ۳ﻝﺅﺙ?try:
    execute_order(order)
except NetworkError:
    # ﻟ۹ﮒ۷ﻠﻟﺁ
    retry_manager.retry(order)
except BrokerError:
    # ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻠﻝ۴ﻝ۷ﮔﺓ
    logger.error("ﮒﺕﮒﻝﺏﭨﻝﭨﮔﻠ")
```

#### 1.4.4 ﻝﮔﺑﭨﮒﻝﺎﭨﮔﺁﺅﺙﻠ۳ﮒﮒﭦﮔﺁ

| ﻠ۳ﮒﮒﭦﮔﺁ | ﻠﮒﻛﭦ۳ﮔﻝﺏﭨﻝﭨ | QMTExecutorﻝﻛﺛﻝ?|
|---------|------------|-----------------|
| **ﮔ۷ﺅﺙﻠ۰ﺝﮒ؟۱ﺅﺙ?* | ﻝﻝ۴ﻝﺏﭨﻝﭨ | ﮒﺏﮒ؟ﮒﻛﭨﻛﺗﺅﺙﻛﺗﺍﻛﭨﻛﺗﻟ۰ﻝ۴۷ﺅﺙ |
| **ﮔﮒ۰ﮒ?* | **QMTExecutor** | ﮔ۴ﮒﻙﻛﺕﮒﻙﻟﺓﻟﺕ۹ﻙﮒ۳ﻝﻠ؟ﻠ۱?|
| **ﮒ۷ﮔﺟ** | QMTﮒﺕﮒﻝﺏﭨﻝﭨ | ﮒ؟ﻠﮒﻟﺅﺙﮔ۶ﻟ۰ﻛﭦ۳ﮔﺅﺙ |
| **ﻟﮒ** | ﻛﭦ۳ﮔﮔ۴ﮒ۲ | ﮔﻛﺝﮒﺁﻝ۷ﻝﻛﭦ۳ﮔﻠﻠ۰ﺗ |
| **ﻟﺑ۵ﮒ** | ﮔﻛﭦ۳ﮒﮔ۴ | ﮒﻟﺁﮔ۷ﻟﺎﻛﭦﮒ۳ﮒﺍﻠﺎ |

**QMTExecutorﮒﺍﺎﮔﺁﻠ۲ﻛﺕ۹ﻛﺕﻛﺕﻝﮔﮒ۰ﮒ**ﺅﺙﻝ۰؟ﻛﺟﺅﺙ
- ﻗ?ﮔ۷ﻝﻟ؟۱ﮒﮒﻝ۰؟ﮔﻟﺁﺁﮒﺍﻛﺙﻟﺝﺝﮒﺍﮒ۷ﮔﺟ
- ﻗ?ﮒ؟ﮔﭘﮒﻟﺁﮔ۷ﻟﮒﮒﺍﮒ۹ﻛﺕﮔ۴ﻛﭦ
- ﻗ?ﮒ۵ﮔﮒ۷ﮔﺟﮒﭦﻠ؟ﻠ۱ﺅﺙﮒﮔﭘﮒ۳ﻝ
- ﻗ?ﻝ۰؟ﻛﺟﮔ۷ﮔﻟﭘﺏﮒ۳ﻝﻠﺎﻛﭨﮔ؛ﺝ
- ﻗ?ﻝ۰؟ﻛﺟﮔ۷ﻝﻝﺗﻟﻝ؛۵ﮒﻠ۳ﮒﻟ۶ﮒ؟

#### 1.4.5 ﻛﺕQMTﻝﮒﺏﻝﺏ?
**QMT = ﻟﺟﮔﻠﮒﻛﭦ۳ﮔﻝﭨﻝ،ﺁ**ﺅﺙﻛﺕﮔ؛ﺝﻠﮒﻛﭦ۳ﮔﻟﺛﺁﻛﭨﭘﺅﺙ

```
QMTﮔﻛﺝﺅﺙ?- ﻛﭦ۳ﮔﮔ۴ﮒ۲ﺅﺙXtQuantTraderﺅﺙ?- ﮔﺍﮔ؟ﮔ۴ﮒ۲
- ﻟ؟۱ﮒﮔ۴ﮒ۲
```

**QMTExecutorﻛﺕQMTﻝﮒﺏﻝﺏ?*ﺅﺙ?
```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ? ﮔ۷ﻝﻝﻝ۴ﻝﺏﭨﻝﭨ    ﻗ?ﻗ? (ﮒﺏﻝﻛﺗﺍﻛﭨﻛﺗ?    ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗﻗﻗ?         ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ? QMTExecutor    ﻗ? ﻗ?ﻛﺕﻠﺑﮒﺎﺅﺙﻝﺟﭨﻟﺁﮒ؟?ﻗ? (ﻟ؟۱ﮒﮒ۳ﻝ)      ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗﻗﻗ?         ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ? QMTﻛﭦ۳ﮔﮔ۴ﮒ۲     ﻗ? ﻗ?ﮒﭦﮒﺎﮔ۴ﮒ۲
ﻗ? (ﮒﺕﮒﻝﺏﭨﻝﭨ)      ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```

**QMTExecutorﻝﻛﺛﻝ?*ﺅﺙ?1. **ﻝﺟﭨﻟﺁﮒ؟?*ﺅﺙﮔﮔ۷ﻝﻝﻝ۴ﻛﺟ۰ﮒﺓﻝﺟﭨﻟﺁﮔQMTﻟﺛﻝﻟ۶۲ﻝﮔﺙﮒﺙ
2. **ﻛﺟﮔ۳ﻛﺙ?*ﺅﺙﮒ۷ﻟﺍﻝ۷QMTﮔ۴ﮒ۲ﮒﻟﺟﻟ۰ﮒﻝ۶ﮔ۲ﮔ۴ﺅﺙﻠ۲ﻠ۸ﻙﮒﻟ۶ﺅﺙ
3. **ﻝﮔ۶ﮒ?*ﺅﺙﮒ؟ﮔﭘﻝﮔ۶QMTﻟﺟﮒﻝﻟ؟۱ﮒﻝﭘﮔ?4. **ﮔﻠﮒ۳ﻝ**ﺅﺙﮒ۳ﻝQMTﮔ۴ﮒ۲ﮒﺁﻟﺛﮒﭦﻝﺍﻝﮒﻝ۶ﮒﺙﮒﺕ?
#### 1.4.6 ﻛﺕﭦﻛﭨﻛﺗﻠﻟ۵QMTExecutorﺅﺙ?
**ﻠ؟ﻠ۱ﺅﺙﻛﺕﭦﻛﭨﻛﺗﻛﺕﻝﺑﮔ۴ﻟﺍﻝ۷QMTﮔ۴ﮒ۲ﺅﺙ?*

ﻝﮔ۰ﺅﺙﮒﺍﺎﮒﻛﺕﭦﻛﭨﻛﺗﻛﺕﻝﺑﮔ۴ﮒﭨﮒ۷ﮔﺟﻝﺗﻟﺅﺙ

| ﻝﺑﮔ۴ﻟﺍﻝ۷QMT | ﻠﻟﺟQMTExecutor |
|-----------|---------------|
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﮒ۳ﻝﻟ؟۱ﮒﮔﺙﮒﺙﻟﺛ؛ﮔ?| ﻗ?ﻟ۹ﮒ۷ﻟﺛ؛ﮔ۱ﮔﺙﮒﺙ |
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﻝﮔ۶ﻟ؟۱ﮒﻝﭘﮔ?| ﻗ?ﻟ۹ﮒ۷ﻝﮔ۶ﮒﻠﻝ۴ |
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﮒ۳ﻝﮒﺙﮒﺕ?| ﻗ?ﻟ۹ﮒ۷ﻠﻟﺁﮒﮔ۱ﮒ۳?|
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﮔ۲ﮔ۴ﻠ۲ﻠ?| ﻗ?ﻟ۹ﮒ۷ﻠ۲ﻠ۸ﮔ۲ﮔ?|
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﮔ۲ﮔ۴ﮒﻟ۶?| ﻗ?ﻟ۹ﮒ۷ﮒﻟ۶ﮔ۲ﮔ?|
| ﻗ?ﻛﭨ۲ﻝﻠﮒ۳ﺅﺙﻠﺝﻛﭨ۴ﻝﭨﺑﮔ?| ﻗ?ﻝﭨﻛﺕﮔ۴ﮒ۲ﺅﺙﮔﻛﭦﻝﭨﺑﮔ?|

#### 1.4.7 ﮔﺕﮒﺟﻛﭨﺓﮒ?
| ﻛﭨﺓﮒ?| ﻟﺁﺑﮔ |
|------|------|
| **ﻝﭨﻛﺕﮔ۴ﮒ۲** | ﮔﻛﺝﻝ؟ﮒﮔﻝ۷ﻝﻛﭦ۳ﮔﮔ۴ﮒ۲ |
| **ﻠ۲ﻠ۸ﮔ۶ﮒﭘ** | ﻟ۹ﮒ۷ﮔ۲ﮔ۴ﮒﻝ۶ﻠ۲ﻠ?|
| **ﮒﻟ۶ﮔ۲ﮔ?* | ﻝ۰؟ﻛﺟﻝ؛۵ﮒﻝﻝ؟۰ﻟ۵ﮔﺎ ﻭ |
| **ﮒﺙﮒﺕﺕﮒ۳ﻝ** | ﻟ۹ﮒ۷ﮒ۳ﻝﮒﻝ۶ﮒﺙﮒﺕﺕ |
| **ﻟ؟۱ﮒﻝﮔ۶** | ﮒ؟ﮔﭘﻟﺓﻟﺕ۹ﻟ؟۱ﮒﻝﭘﮔ?|

---

## 2. ﻟﺁ۵ﻝﭨﮔﭘﮔﻟ؟ﺝﻟ؟۰

### 2.1 ﻝﺏﭨﻝﭨﮔﭘﮔﺅﺟ?
```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?
ﺅﺟ?                   Layer 5: ﻝﻝ۴ﮔ۶ﻟ۰ﺅﺟ?                      ﺅﺟ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?
ﺅﺟ?                                                            ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ?       QMTExecutor (ﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﻛﺕﭨﮔ۷۰ﮒ)                  ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﻟ؟۱ﮒﮔ۶ﻟ۰                                            ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﻟ؟۱ﮒﻝﮔ۶                                            ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﮒﺙﮒﺕﺕﮒ۳ﻝ                                            ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﻠ۲ﻠ۸ﮔ۶ﮒﭘ                                            ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﮒﻟ۶ﮔ۲ﺅﺟ?ﻭ                                         ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ?                          ﺅﺟ?                                 ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ?         ﮔﺕﮒﺟﻝﭨﻛﭨﭘ                                      ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗOrderConverterﺅﺟ?ﻗOrderMonitor ﺅﺟ?ﻗRiskChecker  ﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻟ؟۱ﮒﻟﺛ؛ﮔ۱ﮒ۷     ﺅﺟ? ﻗﻟ؟۱ﮒﻝﮔ۶ﮒ۷   ﺅﺟ? ﻗﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۷   ﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗExceptionHdlrﺅﺟ?ﻗRetryManager ﺅﺟ?ﻗAccountManagerﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﮒﺙﮒﺕﺕﮒ۳ﻝﮒ۷    ﺅﺟ? ﻗﻠﻟﺁﻝ؟۰ﻝﮒ۷   ﺅﺟ? ﻗﻟﺑ۵ﮔﺓﻝ؟۰ﻝﮒ۷   ﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?                                      ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗComplianceChkﺅﺟ?ﻭ ﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷                     ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﺅﺟ?COMPLIANCE_ ﺅﺟ? - ﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔ۲ﺅﺟ?                  ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗCHECKER_001) ﺅﺟ? - ﮔ۳ﮒﻠﮒﭘﮔ۲ﺅﺟ?                      ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﺅﺟ?            ﺅﺟ? - ﻝﻝﭦﺟﻛﭦ۳ﮔﮒﻟ۶ﮔ۲ﺅﺟ?                  ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?                                      ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ?                          ﺅﺟ?                                 ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ?         QMT APIﺅﺟ?                                   ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - XtQuantTrader (ﻛﭦ۳ﮔAPI)                           ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - xtdata (ﮔﺍﮔ؟API)                                  ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - xtorder (ﻟ؟۱ﮒAPI)                                 ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ?                                                            ﺅﺟ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?
```

### 2.2 Layerﮒ؟ﻛﺛﻟﺁ۵ﻝﭨﻟﺁﺑﮔ
- **Layerﮒﺛﮒﺎ**: Layer 5 - ﻝﻝ۴ﮔ۶ﻟ۰ﺅﺟ?
- **ﻟﻟﺑ۲ﻟﮒﺑ**: ﻟ؟۱ﮒﮔ۶ﻟ۰ﻙﻟ؟۱ﮒﻝﮔ۶ﻙﮒﺙﮒﺕﺕﮒ۳ﻝﻙﻠ۲ﻠ۸ﮔ۶ﺅﺟ?
- **ﻛﺕﻛﺕﮒﺎﮔ۴ﺅﺟ?*: 
  - ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 5 SignalGenerator (ﮔﻛﺝﻛﭦ۳ﮔﻛﺟ۰ﮒﺓ)
  - ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 6 ﻝﭨﮒﻛﺙﮒﺅﺟ?(ﮔ۴ﮔﭘﮔ۶ﻟ۰ﻝﭨﮔ)

### 2.3 ﮔ۷۰ﮒﻟﻟﺑ۲ﻛﺕﻟﺝﺗﻝﮒ؟ﺅﺟ?
- **ﮔﺕﮒﺟﻟﻟﺑ۲**: ﮒ؟ﻝﻛﭦ۳ﮔﮔ۶ﻟ۰ﻙﻟ؟۱ﮒﻝ؟۰ﻝﻙﻠ۲ﻠ۸ﮔ۶ﺅﺟ?
- **ﻟﻟﺑ۲ﻟﺝﺗﻝ**: 
  - ﺅﺟ?ﮔ؛ﮔ۷۰ﮒﻟﺑﺅﺟ? ﻟ؟۱ﮒﮔ۶ﻟ۰ﻙﻟ؟۱ﮒﻝﮔ۶ﻙﮒﺙﮒﺕﺕﮒ۳ﻝﻙﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
- ﺅﺟ?ﮔ؛ﮔ۷۰ﮒﻛﺕﻟﺑﻟﺑ۲: ﻛﺟ۰ﮒﺓﻝﮔﻙﻝﻝ۴ﮒﺏﻝﻙﮔﺍﮔ؟ﻟﺓﮒﻙﻠ۲ﻠ۸ﮔ۷۰ﺅﺟ?
- **ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵**: ﮔﻛﺝﻝﭨﻛﺕﻝPython APIﮔ۴ﮒ۲

### 2.4 ﻛﺝﻟﭖﮒﺏﻝﺏﭨ
| ﻛﺝﻟﭖﮔ۷۰ﮒ | ﻛﺝﻟﭖﻝﺎﭨﮒ | ﮔ۴ﮒ۲ﮔﺗﮒﺙ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﮒ۳ﮔﺏ۷ |
|----------|----------|----------|----------|------|
| xtquant | ﮒﺙﭦﻛﺝﺅﺟ?| QMT Python API | >=1.0.0 | QMTﮒ؟ﮔﺗAPI |
| threading | ﮒﺙﭦﻛﺝﺅﺟ?| Pythonﮔﮒﺅﺟ?| >=3.8 | ﮒ۳ﻝﭦﺟﻝ۷ﮔﺁﺅﺟ?|
| queue | ﮒﺙﭦﻛﺝﺅﺟ?| Pythonﮔﮒﺅﺟ?| >=3.8 | ﻠﮒﮔﺁﮔ |

---

## 3. ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 3.1 APIﮔ۴ﮒ۲ﻟ۶ﻟ

#### 3.1.1 ﻛﺕﭨﮔ۴ﮒ۲ﻝﺎﭨ
```python
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import time
import logging


class OrderStatus(Enum):
    """ﻟ؟۱ﮒﻝﭘﮔﮔﺅﺟ?""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    ERROR = "error"


class OrderType(Enum):
    """ﻟ؟۱ﮒﻝﺎﭨﮒﮔﻛﺕﺝ"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderDirection(Enum):
    """ﻟ؟۱ﮒﮔﺗﮒﮔﻛﺕﺝ"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class UnifiedOrder:
"""ﻝﭨﻛﺕﻟ؟۱ﮒﮔﺙﮒﺙ"""
    order_id: str
    symbol: str
    direction: OrderDirection
    order_type: OrderType
    volume: int
    price: Optional[float]
    strategy_id: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class QMTOrder:
"""QMTﻟ؟۱ﮒﮔﺙﮒﺙ"""
    stock_code: str
    order_type: int
    order_volume: int
    price: float
    strategy_name: str
    order_remark: str


@dataclass
class ExecutionResult:
    """ﮔ۶ﻟ۰ﻝﭨﮔ"""
    order_id: str
    status: OrderStatus
    filled_volume: int
    filled_amount: float
    avg_price: float
    commission: float
    timestamp: datetime
    error_message: Optional[str]


@dataclass
class QMTConfig:
    """QMTﻠﻝﺛ؟"""
    account_id: str
    session_id: str
    client_path: str
    max_retry: int = 3
    retry_interval: float = 1.0
    order_timeout: int = 60


class OrderConverter:
    """ﻟ؟۱ﮒﻟﺛ؛ﮔ۱ﺅﺟ?""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def to_qmt_order(self, unified_order: UnifiedOrder) -> QMTOrder:
"""ﮒﺍﻝﭨﻛﺕﻟ؟۱ﮒﻟﺛ؛ﮔ۱ﻛﺕﭦQMTﻟ؟۱ﮒﮔﺙﮒﺙ
        
        ﮒﮔﺍ:
            unified_order: ﻝﭨﻛﺕﻟ؟۱ﮒ
            
        ﻟﺟﮒ:
            QMTOrder: QMTﻟ؟۱ﮒ
        """
        stock_code = self._format_symbol(unified_order.symbol)
        
        order_type = self._convert_order_type(
            unified_order.order_type,
            unified_order.direction
        )
        
        price = unified_order.price or 0.0
        
        return QMTOrder(
            stock_code=stock_code,
            order_type=order_type,
            order_volume=unified_order.volume,
            price=price,
            strategy_name=unified_order.strategy_id,
            order_remark=unified_order.order_id
        )
    
    def _format_symbol(self, symbol: str) -> str:
"""ﮔﺙﮒﺙﮒﻟ۰ﻝ۴۷ﻛﭨ۲ﺅﺟ?
        
        ﮒﮔﺍ:
symbol: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ
            
        ﻟﺟﮒ:
ﮔﺙﮒﺙﮒﮒﻝﻟ۰ﻝ۴۷ﻛﭨ۲ﺅﺟ?
        """
        if symbol.endswith('.SH'):
            return symbol.replace('.SH', '.XSHG')
        elif symbol.endswith('.SZ'):
            return symbol.replace('.SZ', '.XSHE')
        else:
            if symbol.startswith('6'):
                return f"{symbol}.XSHG"
            else:
                return f"{symbol}.XSHE"
    
    def _convert_order_type(
        self,
        order_type: OrderType,
        direction: OrderDirection
    ) -> int:
        """ﻟﺛ؛ﮔ۱ﻟ؟۱ﮒﻝﺎﭨﮒ
        
        ﮒﮔﺍ:
            order_type: ﻟ؟۱ﮒﻝﺎﭨﮒ
            direction: ﻟ؟۱ﮒﮔﺗﮒ
            
        ﻟﺟﮒ:
QMTﻟ؟۱ﮒﻝﺎﭨﮒﻛﭨ۲ﻝ
        """
        type_map = {
            (OrderType.MARKET, OrderDirection.BUY): 23,
            (OrderType.MARKET, OrderDirection.SELL): 24,
            (OrderType.LIMIT, OrderDirection.BUY): 23,
            (OrderType.LIMIT, OrderDirection.SELL): 24,
        }
        
        return type_map.get((order_type, direction), 23)


class OrderMonitor:
    """ﻟ؟۱ﮒﻝﮔ۶ﺅﺟ?""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        self._order_status: Dict[str, OrderStatus] = {}
        self._order_results: Dict[str, ExecutionResult] = {}
        self._monitor_thread = None
        self._running = False
        self.logger = logging.getLogger(__name__)
    
    def start(self) -> None:
        """ﮒﺁﮒ۷ﻟ؟۱ﮒﻝﮔ۶"""
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        self.logger.info("OrderMonitor started")
    
    def stop(self) -> None:
"""ﮒﮔ۱ﻟ؟۱ﮒﻝﮔ۶"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        self.logger.info("OrderMonitor stopped")
    
    def register_order(self, order_id: str) -> None:
        """ﮔﺏ۷ﮒﻟ؟۱ﮒ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
        """
        self._order_status[order_id] = OrderStatus.PENDING
        self.logger.info(f"Registered order: {order_id}")
    
    def update_status(
        self,
        order_id: str,
        status: OrderStatus,
        result: Optional[ExecutionResult] = None
    ) -> None:
        """ﮔﺑﮔﺍﻟ؟۱ﮒﻝﭘﺅﺟﺛ?
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            status: ﻟ؟۱ﮒﻝﭘﺅﺟﺛ?
            result: ﮔ۶ﻟ۰ﻝﭨﮔ
        """
        self._order_status[order_id] = status
        
        if result:
            self._order_results[order_id] = result
        
        self.logger.info(f"Order {order_id} status updated to {status}")
    
    def get_status(self, order_id: str) -> OrderStatus:
        """ﻟﺓﮒﻟ؟۱ﮒﻝﭘﺅﺟﺛ?
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            
        ﻟﺟﮒ:
            ﻟ؟۱ﮒﻝﭘﺅﺟﺛ?
        """
        return self._order_status.get(order_id, OrderStatus.PENDING)
    
    def get_result(self, order_id: str) -> Optional[ExecutionResult]:
        """ﻟﺓﮒﮔ۶ﻟ۰ﻝﭨﮔ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            
        ﻟﺟﮒ:
            ﮔ۶ﻟ۰ﻝﭨﮔ
        """
        return self._order_results.get(order_id)
    
    def _monitor_loop(self) -> None:
        """ﻝﮔ۶ﮒﺝ۹ﻝﺁ"""
        while self._running:
            try:
                for order_id in list(self._order_status.keys()):
                    status = self._order_status[order_id]
                    
                    if status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                        continue
                    
                    self._check_order_status(order_id)
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
    
    def _check_order_status(self, order_id: str) -> None:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﻝﭘﺅﺟ?
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
        """
        pass


class RiskChecker:
    """ﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۷"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def check_order(self, order: UnifiedOrder) -> bool:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﻠ۲ﺅﺟ?
        
        ﮒﮔﺍ:
            order: ﻝﭨﻛﺕﻟ؟۱ﮒ
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
        """
        if not self._check_volume(order.volume):
            self.logger.warning(f"Order volume check failed: {order.order_id}")
            return False
        
        if not self._check_price(order.price):
            self.logger.warning(f"Order price check failed: {order.order_id}")
            return False
        
        if not self._check_frequency(order.symbol):
            self.logger.warning(f"Order frequency check failed: {order.order_id}")
            return False
        
        return True
    
    def _check_volume(self, volume: int) -> bool:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﮔﺍﺅﺟ?
        
        ﮒﮔﺍ:
            volume: ﻟ؟۱ﮒﮔﺍﻠ
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟﮔ۲ﺅﺟ?
        """
        max_volume = self.config.get('max_volume', 1000000)
        min_volume = self.config.get('min_volume', 100)
        
        return min_volume <= volume <= max_volume
    
    def _check_price(self, price: Optional[float]) -> bool:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﻛﭨﺓﺅﺟ?
        
        ﮒﮔﺍ:
price: ﻟ؟۱ﮒﻛﭨﺓﮔﺙ
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟﮔ۲ﺅﺟ?
        """
        if price is None:
            return True
        
        max_price = self.config.get('max_price', 1000.0)
        min_price = self.config.get('min_price', 0.1)
        
        return min_price <= price <= max_price
    
    def _check_frequency(self, symbol: str) -> bool:
        """ﮔ۲ﮔ۴ﻛﭦ۳ﮔﻠ۱ﺅﺟ?
        
        ﮒﮔﺍ:
symbol: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟﮔ۲ﺅﺟ?
        """
        return True


class ExceptionHandler:
    """ﮒﺙﮒﺕﺕﮒ۳ﻝﺅﺟ?""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def handle_execution_error(
        self,
        order: UnifiedOrder,
        error: Exception
    ) -> Optional[ExecutionResult]:
        """ﮒ۳ﻝﮔ۶ﻟ۰ﻠﻟﺁﺁ
        
        ﮒﮔﺍ:
            order: ﻝﭨﻛﺕﻟ؟۱ﮒ
            error: ﮒﺙﮒﺕﺕ
            
        ﻟﺟﮒ:
            ﮔ۶ﻟ۰ﻝﭨﮔ
        """
        self.logger.error(f"Execution error for order {order.order_id}: {error}")
        
        return ExecutionResult(
            order_id=order.order_id,
            status=OrderStatus.ERROR,
            filled_volume=0,
            filled_amount=0.0,
            avg_price=0.0,
            commission=0.0,
            timestamp=datetime.now(),
            error_message=str(error)
        )


class RetryManager:
    """ﻠﻟﺁﻝ؟۰ﻝﺅﺟ?""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        self._retry_count: Dict[str, int] = {}
        self.logger = logging.getLogger(__name__)
    
    def should_retry(self, order_id: str) -> bool:
"""ﮒ۳ﮔﮔﺁﮒ۵ﮒﭦﻟﺁ۴ﻠﻟﺁ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﮒﭦﻟﺁ۴ﻠﻟﺁ
        """
        count = self._retry_count.get(order_id, 0)
        
        if count < self.config.max_retry:
            self._retry_count[order_id] = count + 1
            self.logger.info(f"Retry {count + 1}/{self.config.max_retry} for order {order_id}")
            return True
        
        self.logger.warning(f"Max retry reached for order {order_id}")
        return False
    
    def reset_retry(self, order_id: str) -> None:
        """ﻠﻝﺛ؟ﻠﻟﺁﻟ؟۰ﮔﺍ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
        """
        if order_id in self._retry_count:
            del self._retry_count[order_id]
    
    def wait_before_retry(self) -> None:
"""ﻠﻟﺁﮒﻝﺅﺟ?""
        time.sleep(self.config.retry_interval)


class AccountManager:
    """ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﺅﺟ?""
    
    def __init__(self, trader):
        self.trader = trader
        self.logger = logging.getLogger(__name__)
    
    def get_account_info(self, account_id: str) -> Dict[str, Any]:
        """ﻟﺓﮒﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            
        ﻟﺟﮒ:
            ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
        """
        try:
            account = self.trader.query_account(account_id)
            
            return {
                'total_asset': account.total_asset,
                'available_cash': account.available_cash,
                'market_value': account.market_value,
                'frozen_cash': account.frozen_cash
            }
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            return {}
    
    def get_positions(self, account_id: str) -> List[Dict[str, Any]]:
        """ﻟﺓﮒﮔﻛﭨﻛﺟ۰ﮔﺁ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            
        ﻟﺟﮒ:
            ﮔﻛﭨﮒﻟ۰۷
        """
        try:
            positions = self.trader.query_stock_positions(account_id)
            
            return [
                {
                    'stock_code': pos.stock_code,
                    'volume': pos.volume,
                    'available_volume': pos.can_use_volume,
                    'market_value': pos.market_value,
                    'avg_price': pos.open_price
                }
                for pos in positions
            ]
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []


class QMTExecutor:
    """QMTﻛﭦ۳ﮔﮔ۶ﻟ۰ﺅﺟ?""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        
        from xtquant.xttrader import XtQuantTrader
        
        self.trader = XtQuantTrader(
            config.account_id,
            config.session_id,
            config.client_path
        )
        
        self.trader.start()
        self.trader.subscribe_account(config.account_id)
        
        self.converter = OrderConverter()
        self.monitor = OrderMonitor(config)
        self.risk_checker = RiskChecker({})
        self.exception_handler = ExceptionHandler(config)
        self.retry_manager = RetryManager(config)
        self.account_manager = AccountManager(self.trader)
        
        self.logger = logging.getLogger(__name__)
    
    def execute_order(self, unified_order: UnifiedOrder) -> ExecutionResult:
        """ﮔ۶ﻟ۰ﻟ؟۱ﮒ
        
        ﮒﮔﺍ:
            unified_order: ﻝﭨﻛﺕﻟ؟۱ﮒ
            
        ﻟﺟﮒ:
            ﮔ۶ﻟ۰ﻝﭨﮔ
        """
        if not self.risk_checker.check_order(unified_order):
            return ExecutionResult(
                order_id=unified_order.order_id,
                status=OrderStatus.REJECTED,
                filled_volume=0,
                filled_amount=0.0,
                avg_price=0.0,
                commission=0.0,
                timestamp=datetime.now(),
                error_message="Risk check failed"
            )
        
        self.monitor.register_order(unified_order.order_id)
        
        qmt_order = self.converter.to_qmt_order(unified_order)
        
        try:
            order_id = self.trader.order_stock(
                qmt_order.stock_code,
                qmt_order.order_type,
                qmt_order.order_volume,
                qmt_order.price,
                qmt_order.strategy_name,
                qmt_order.order_remark
            )
            
            self.monitor.update_status(
                unified_order.order_id,
                OrderStatus.SUBMITTED
            )
            
            result = self._wait_for_completion(unified_order.order_id)
            
            return result
            
        except Exception as e:
            if self.retry_manager.should_retry(unified_order.order_id):
                self.retry_manager.wait_before_retry()
                return self.execute_order(unified_order)
            else:
                return self.exception_handler.handle_execution_error(
                    unified_order,
                    e
                )
    
    def cancel_order(self, order_id: str) -> bool:
        """ﮔ۳ﻠﻟ؟۱ﮒ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﮔﮒ
        """
        try:
            result = self.trader.cancel_order(
                self.config.account_id,
                order_id
            )
            
            if result:
                self.monitor.update_status(order_id, OrderStatus.CANCELLED)
                self.logger.info(f"Order {order_id} cancelled")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def _wait_for_completion(
        self,
        order_id: str,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
"""ﻝﮒﺝﻟ؟۱ﮒﮒ؟ﮔ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            timeout: ﻟﭘﮔﭘﮔﭘﻠﺑ
            
        ﻟﺟﮒ:
            ﮔ۶ﻟ۰ﻝﭨﮔ
        """
        timeout = timeout or self.config.order_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.monitor.get_status(order_id)
            
            if status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                result = self.monitor.get_result(order_id)
                if result:
                    return result
            
            time.sleep(0.5)
        
        return ExecutionResult(
            order_id=order_id,
            status=OrderStatus.ERROR,
            filled_volume=0,
            filled_amount=0.0,
            avg_price=0.0,
            commission=0.0,
            timestamp=datetime.now(),
            error_message="Order timeout"
        )
    
    def get_account_info(self) -> Dict[str, Any]:
        """ﻟﺓﮒﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
        
        ﻟﺟﮒ:
            ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
        """
        return self.account_manager.get_account_info(self.config.account_id)
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """ﻟﺓﮒﮔﻛﭨﻛﺟ۰ﮔﺁ
        
        ﻟﺟﮒ:
            ﮔﻛﭨﮒﻟ۰۷
        """
        return self.account_manager.get_positions(self.config.account_id)
    
    def start(self) -> None:
        """ﮒﺁﮒ۷ﮔ۶ﻟ۰ﺅﺟ?""
        self.monitor.start()
        self.logger.info("QMTExecutor started")
    
    def stop(self) -> None:
"""ﮒﮔ۱ﮔ۶ﻟ۰ﺅﺟ?""
        self.monitor.stop()
        self.logger.info("QMTExecutor stopped")
```

### 3.2 ﮔ۶ﻟﺛﮔﮔﻟ۵ﮔﺎ
| ﮔ۶ﻟﺛﮔﮔ | ﻝ؟ﮔﺅﺟ?| ﮔﭖﻠﮔﺗﮔﺏ |
|----------|--------|----------|
| ﻟ؟۱ﮒﮔ۶ﻟ۰ﮔﭘﻠﺑ | < 500ms | ﮒﮔ؛۰ﮔ۶ﻟ۰ |
| ﻟ؟۱ﮒﻝﮔ۶ﮒﭨﭘﻟﺟ | < 1ﺅﺟ?| ﮒﮔ؛۰ﻝﮔ۶ |
| ﮒﺗﭘﮒﻟ؟۱ﮒﺅﺟ?| ﺅﺟ?10ﺅﺟ?| ﮒﺗﭘﮒﮔﭖﻟﺁ |
| ﻟ؟۱ﮒﮔﮒﺅﺟ?| ﺅﺟ?95% | ﻝﭨﻟ؟۰ﮒﮔ |

### 3.3 ﮒ؟ﮒ۷ﮔﭦﮒﭘ
- **ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?*: ﻛﭦ۳ﮔﮒﻟﺟﻟ۰ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
- **ﮒﺙﮒﺕﺕﮒ۳ﻝ**: ﮒ؟ﮒﻝﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘ
- **ﻟ؟۱ﮒﻝﮔ۶**: ﮒ؟ﮔﭘﻝﮔ۶ﻟ؟۱ﮒﻝﭘﺅﺟﺛ?

---

## 4. ﮔﺍﮔ؟ﮔ۷۰ﮒﻛﺕﮒﺅﺟ?

### 4.1 ﮔﺕﮒﺟﮔﺍﮔ؟ﻝﭨﮔ

#### 4.1.1 ﻝﭨﻛﺕﻟ؟۱ﮒﮔ۷۰ﮒ
```python
@dataclass
class UnifiedOrderData:
    """ﻝﭨﻛﺕﻟ؟۱ﮒﮔﺍﮔ؟ﮔ۷۰ﮒ"""
    order_id: str
    symbol: str
    direction: OrderDirection
    order_type: OrderType
    volume: int
    price: Optional[float]
    strategy_id: str
    timestamp: datetime
    metadata: Dict[str, Any]
```

#### 4.1.2 ﮔ۶ﻟ۰ﻝﭨﮔﮔ۷۰ﮒ
```python
@dataclass
class ExecutionResultData:
    """ﮔ۶ﻟ۰ﻝﭨﮔﮔﺍﮔ؟ﮔ۷۰ﮒ"""
    order_id: str
    status: OrderStatus
    filled_volume: int
    filled_amount: float
    avg_price: float
    commission: float
    timestamp: datetime
    error_message: Optional[str]
```

### 4.2 ﻝﺙﮒﻝﻝ۴
| ﻝﺙﮒﻝﺎﭨﮒ | TTL | ﮔﺓﮔﺎﺍﻝﻝ۴ | ﮔﮒ۳۶ﮒ؟ﺗﺅﺟ?|
|----------|-----|----------|----------|
| ﻟ؟۱ﮒﻝﭘﮔﻝﺙﺅﺟ?| 1ﺅﺟ?| LRU | 1000ﻛﺕ۹ﻟ؟۱ﺅﺟ?|
| ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁﻝﺙﮒ | 1ﮒﻠ | LRU | 1ﻛﺕ۹ﻟﺑ۵ﺅﺟ?|
| ﮔﻛﭨﻛﺟ۰ﮔﺁﻝﺙﮒ | 1ﮒﻠ | LRU | 100ﮒ۹ﻟ۰ﺅﺟ?|

### 4.3 ﮔﺍﮔ؟ﮔﻛﺗﺅﺟ?
- **ﮔﻛﺗﮒﻠﺅﺟ?*: ﻟ؟۱ﮒﮒﮒﺎﻙﮔ۶ﻟ۰ﻝﭨﮔﻠﻟ۵ﮔﻛﺗﮒﮒﮒ۷
- **ﮒﮒ۷ﮔﺙﮒﺙ**: SQLiteﮔﺍﮔ؟ﺅﺟ?

---

## 5. ﻝ؟ﮔﺏﮒ؟ﻝﺍﻟﺁﺑﮔ

### 5.1 ﮔﺕﮒﺟﻝ؟ﮔﺏ

#### 5.1.1 ﻟ؟۱ﮒﮔ۶ﻟ۰ﻝ؟ﮔﺏ
```python
def execute_order(self, unified_order: UnifiedOrder) -> ExecutionResult:
    """
    ﻟ؟۱ﮒﮔ۶ﻟ۰ﻝ؟ﮔﺏ
    
    ﻝ؟ﮔﺏﮒﻝ:
    1. ﻟﺟﻟ۰ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
    2. ﮔﺏ۷ﮒﻟ؟۱ﮒﮒﺍﻝﮔ۶ﮒ۷
3. ﻟﺛ؛ﮔ۱ﻟ؟۱ﮒﮔﺙﮒﺙ
    4. ﮒﻠﻟ؟۱ﮒﮒﺍQMT
5. ﻝﮒﺝﻟ؟۱ﮒﮒ؟ﮔ
    6. ﻟﺟﮒﮔ۶ﻟ۰ﻝﭨﮔ
    
    ﮒ۳ﮔﺅﺟ? O(1)
    """
    if not self.risk_checker.check_order(unified_order):
        return ExecutionResult(
            order_id=unified_order.order_id,
            status=OrderStatus.REJECTED,
            filled_volume=0,
            filled_amount=0.0,
            avg_price=0.0,
            commission=0.0,
            timestamp=datetime.now(),
            error_message="Risk check failed"
        )
    
    self.monitor.register_order(unified_order.order_id)
    
    qmt_order = self.converter.to_qmt_order(unified_order)
    
    try:
        order_id = self.trader.order_stock(
            qmt_order.stock_code,
            qmt_order.order_type,
            qmt_order.order_volume,
            qmt_order.price,
            qmt_order.strategy_name,
            qmt_order.order_remark
        )
        
        self.monitor.update_status(
            unified_order.order_id,
            OrderStatus.SUBMITTED
        )
        
        result = self._wait_for_completion(unified_order.order_id)
        
        return result
        
    except Exception as e:
        if self.retry_manager.should_retry(unified_order.order_id):
            self.retry_manager.wait_before_retry()
            return self.execute_order(unified_order)
        else:
            return self.exception_handler.handle_execution_error(
                unified_order,
                e
            )
```

#### 5.1.2 ﻠﻟﺁﻝ؟ﮔﺏ
```python
def should_retry(self, order_id: str) -> bool:
    """
ﻠﻟﺁﮒ۳ﮔﻝ؟ﮔﺏ
    
    ﻝ؟ﮔﺏﮒﻝ:
    1. ﻟﺓﮒﮒﺛﮒﻠﻟﺁﮔ؛۰ﮔﺍ
2. ﮒ۳ﮔﮔﺁﮒ۵ﻟﭘﻟﺟﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﺅﺟ?
    3. ﮔﺑﮔﺍﻠﻟﺁﻟ؟۰ﮔﺍ
    
    ﮒ۳ﮔﺅﺟ? O(1)
    """
    count = self._retry_count.get(order_id, 0)
    
    if count < self.config.max_retry:
        self._retry_count[order_id] = count + 1
        self.logger.info(f"Retry {count + 1}/{self.config.max_retry} for order {order_id}")
        return True
    
    self.logger.warning(f"Max retry reached for order {order_id}")
    return False
```

---

## 6. ﮒ؟ﮔﺛﮔﮔﺁﮔ

### 6.1 ﻟﺁﻟ۷ﻛﺕﮔ۰ﺅﺟ?
| ﮔﮔﺁﻠﮒ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﻝ۷ﺅﺟﺛ?| ﻠﮔ۸ﻝﻝﺎ |
|----------|----------|------|----------|
| Python | >=3.8 | ﻛﺕﭨﻟ۵ﮒﺙﮒﻟﺁﻟ۷ | ﻠﮒﻝﺏﭨﻝﭨﮔﮒﻟﺁﻟ۷ |
| xtquant | >=1.0.0 | QMT Python API | QMTﮒ؟ﮔﺗAPI |
| threading | ﮔﮒﺅﺟ?| ﮒ۳ﻝﭦﺟﻝ۷ﮔﺁﺅﺟ?| Pythonﮒﻝﺛ؟ﺅﺙﻝ۷ﺏﮒ؟ﮒﺁﺅﺟ?|

### 6.2 ﻝ؛؛ﻛﺕﮔﺗﻛﺝﺅﺟ?
```yaml
requirements:
  - xtquant>=1.0.0
```

---

## 7. ﮔﭖﻟﺁﻝﻝ۴

### 7.1 ﮒﮒﮔﭖﻟﺁ
| ﮔﭖﻟﺁﺅﺟ?| ﮔﭖﻟﺁﮒﮒ؟ﺗ | ﻟ۵ﻝﻝﻝ؟ﺅﺟ?|
|--------|----------|------------|
| ﻟ؟۱ﮒﻟﺛ؛ﮔ۱ | ﻟﺛ؛ﮔ۱ﮔ۲ﻝ۰؟ﺅﺟ?| 100% |
| ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?| ﮔ۲ﮔ۴ﮔ۲ﻝ۰؟ﺅﺟﺛ?| 100% |
| ﻟ؟۱ﮒﮔ۶ﻟ۰ | ﮔ۶ﻟ۰ﮔ۲ﻝ۰؟ﺅﺟ?| 100% |
| ﮒﺙﮒﺕﺕﮒ۳ﻝ | ﮒ۳ﻝﮔ۲ﻝ۰؟ﺅﺟ?| 100% |

### 7.2 ﻠﮔﮔﭖﻟﺁ
```python
def test_qmt_executor_integration():
    """ﻠﮔﮔﭖﻟﺁﻝ۳ﭦﻛﺝ"""
    config = QMTConfig(
        account_id="test_account",
        session_id="test_session",
        client_path="test_path"
    )
    
    executor = QMTExecutor(config)
    
    order = UnifiedOrder(
        order_id="test_order_001",
        symbol="600000.SH",
        direction=OrderDirection.BUY,
        order_type=OrderType.LIMIT,
        volume=100,
        price=10.0,
        strategy_id="test_strategy",
        timestamp=datetime.now(),
        metadata={}
    )
    
    result = executor.execute_order(order)
    
    assert result.order_id == "test_order_001"
```

---

## 8. ﻠ۲ﻠ۸ﻛﺕﻝﭦ۵ﺅﺟ?

### 8.1 ﮔﮔﺁﻠ۲ﺅﺟ?
| ﻠ۲ﻠ۸ID | ﻠ۲ﻠ۸ﮔﻟﺟﺍ | ﻠ۲ﻠ۸ﻝﻝﭦ۶ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |
|--------|----------|----------|----------|
| R001 | QMT APIﻛﺕﻝ۷ﺏﺅﺟ?| P0 | ﮒ؟ﻝﺍﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﺅﺟ?|
| R002 | ﻟ؟۱ﮒﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ | P1 | ﮒ؟ﻝﺍﻟ؟۱ﮒﻝﮔ۶ﮒﮒﺅﺟ?|
| R003 | ﻝﺛﻝﭨﻟﺟﮔ۴ﻛﺕﮔ | P1 | ﮒ؟ﻝﺍﻟﺟﮔ۴ﻠﻟﺟﮔﭦﮒﭘ |
| R004 | ﻛﭦ۳ﮔﮔﻠﻛﺕﻟﭘﺏ | P2 | ﮒ؟ﻝﺍﮔﻠﮔ۲ﮔ۴ﮔﭦﺅﺟ?|

### 8.2 ﻝﭦ۵ﮔﮔ۰ﻛﭨﭘ
- **ﮔﮔﺁﻝﭦ۵ﺅﺟ?*: ﻛﺝﻟﭖQMTﮒ؟۱ﮔﺓﻝ،ﺁﮒAPI
- **ﻟﭖﮔﭦﻝﭦ۵ﮔ**: ﮒﮒﻛﺛﺟﻝ۷<500MBﺅﺙCPUﻛﺛﺟﻝ۷<20%
- **ﮔﭘﻠﺑﻝﭦ۵ﮔ**: ﻠ۱ﻟ؟۰ﮒﺙﮒﮔﭘﺅﺟ?0ﮒﺍﮔﭘ
- **ﻟﺑ۷ﻠﻝﭦ۵ﮔ**: ﮔﭖﻟﺁﻟ۵ﻝﻝﻗ۴90%

---

## 9. ﻠ۹ﮔﭘﮔﮒ

### 9.1 ﮒﻟﺛﻠ۹ﮔﭘﮔﮒ
| ﮒﻟﺛﺅﺟ?| ﻠ۹ﮔﭘﮔﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|--------|----------|----------|
| ﻟ؟۱ﮒﮔ۶ﻟ۰ | ﮔ۶ﻟ۰ﮔ۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| ﻟ؟۱ﮒﻝﮔ۶ | ﻝﮔ۶ﮔ۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| ﮒﺙﮒﺕﺕﮒ۳ﻝ | ﮒ۳ﻝﮔ۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?| ﮔ۲ﮔ۴ﮔ۲ﺅﺟ?| ﮒﮒﮔﭖﻟﺁ |

### 9.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘﮔﮒ
| ﮔ۶ﻟﺛﮔﮔ | ﻠ۹ﮔﭘﮔﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|----------|----------|----------|
| ﻟ؟۱ﮒﮔ۶ﻟ۰ﮔﭘﻠﺑ | < 500ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| ﻟ؟۱ﮒﻝﮔ۶ﮒﭨﭘﻟﺟ | < 1ﺅﺟ?| ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| ﻟ؟۱ﮒﮔﮒﺅﺟ?| ﺅﺟ?95% | ﻝﭨﻟ؟۰ﮒﮔ |

### 9.3 ﻟﺑ۷ﻠﻠ۹ﮔﭘﮔﮒ
| ﻟﺑ۷ﻠﮔﮔ | ﻠ۹ﮔﭘﮔﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|----------|----------|----------|
| ﮔﭖﻟﺁﻟ۵ﻝﺅﺟ?| ﺅﺟ?90% | pytest-cov |
| ﻛﭨ۲ﻝﻟﺑ۷ﻠ | ﮔﻛﺕ۴ﻠﻠ؟ﺅﺟ?| pylint |

---

## 10. ﮒ؟ﮔﺛﻟﺓﺁﻝﭦﺟﺅﺟ?

### 10.1 Phase 1: ﮔﺕﮒﺟﮒﻟﺛﮒﺙﺅﺟ?(3ﺅﺟ?
- **Day 1**: ﻟ؟۱ﮒﻟﺛ؛ﮔ۱ﮒ۷ﻙﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۷
- **Day 2**: ﻟ؟۱ﮒﻝﮔ۶ﮒ۷ﻙﮒﺙﮒﺕﺕﮒ۳ﻝﮒ۷
- **Day 3**: ﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﻙﻠﮔﮔﭖﺅﺟ?

---

## ﻠﮒﺛ

### A. ﻠﻝﺛ؟ﻝ۳ﭦﻛﺝ
```yaml
qmt_executor:
  account_id: "your_account_id"
  session_id: "your_session_id"
  client_path: "C:\\QMT"
  
  max_retry: 3
  retry_interval: 1.0
  order_timeout: 60
  
  risk_check:
    max_volume: 1000000
    min_volume: 100
    max_price: 1000.0
    min_price: 0.1
```

### B. ﻠﻟﺁﺁﻝﮒ؟ﺅﺟ?
| ﻠﻟﺁﺁﺅﺟ?| ﻠﻟﺁﺁﻝﺎﭨﮒ | ﻠﻟﺁﺁﮔﻟﺟﺍ | ﮒ۳ﻝﮔﺗﮒﺙ |
|--------|----------|----------|----------|
| ERR_EXEC_001 | ExecuteError | ﻟ؟۱ﮒﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﺅﺟ?|
| ERR_EXEC_002 | CancelError | ﻟ؟۱ﮒﮔ۳ﻠﮒ۳ﺎﻟﺑ۴ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﺅﺟ?|
| ERR_EXEC_003 | RiskCheckError | ﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۳ﺎﺅﺟ?| ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﺅﺟ?|
| ERR_EXEC_004 | TimeoutError | ﻟ؟۱ﮒﻟﭘﮔﭘ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﺅﺟ?|

### C. ﮒﻟﮔﺅﺟ?
- [ﮔﭘﮔﮒ؟ﻛﺗ](../../01_FRAMEWORK/ARCHITECTURE.md)
- [ﮔ۷۰ﮒﻟﻟﺑ۲ﻟﺝﺗﻝ](../../01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md)
- [QMTﮔﺍﮔ؟ﮔ۴ﮒ۲ﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵](./QMT_DATA_INTERFACE_TECHNICAL_SPECIFICATION.md)


**ﮔﮔ۰۲ﻝﮔ؛**: v1.2.0 | **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02 | **ﻝﭨﺑﮔ۳ﻟ?*: ﻝﻝ۴ﮔ۶ﻟ۰ﮒﺎﻟﺑﻟﺑ۲ﻛﭦﭦ

---

## 11. ﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﮔ۴ﻠﮔﮔﺗﺅﺟ?ﻭ

### 11.1 ﻠﮔﻟﮔﺁ

**ﻝﻝ؟۰ﻟ۵ﮔﺎ**ﺅﺟ?- **2026ﺅﺟ?ﺅﺟ?ﺅﺟ?*ﺅﺙﻟﺁﻝﻛﺙﻙﮒﺏﻛﭦﻝﻝﭦﺟﻛﭦ۳ﮔﻝﻝ؟۰ﻝﻟ۴ﮒﺗﺎﻟ۶ﮒ؟ﻙﮔ۲ﮒﺙﮔﺛﺅﺟ?- **2025ﺅﺟ?ﺅﺟ?ﺅﺟ?*ﺅﺙﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﻙﮔ۲ﮒﺙﮔﺛﺅﺟ?- **ﻝﻝ؟۰ﮒﺁﺙﮒ**ﺅﺙﻠﻠﻙﻝ۸ﺟﻠﻙﮒﺗﺏﮔﺅﺙAﻟ۰ﻛﭦ۳ﮔﻝﮔﻟﺟﮔ۴ﮔﺗﮔ؛ﮔ۶ﻠﺅﺟ?
**ﻠﮔﻝ؟ﮔ**ﺅﺟ?- ﺅﺟ?ﻝ۰؟ﻛﺟﮔﮔﻛﭦ۳ﮔﻟ۰ﻛﺕﭦﻝ؛۵ﮒﮔﮔﺍﻝﻝ؟۰ﻟ۵ﺅﺟ?- ﺅﺟ?ﮒ؟ﮔﭘﻠ۱ﻟ۵ﮒﻟ۶ﻠ۲ﻠ۸ﺅﺙﻠﺟﮒﻟﺟﻟ۶ﮒ۳ﺅﺟ?- ﺅﺟ?ﻠﻛﺛﮒﻟ۶ﮔﮔ؛ﺅﺙﻟ۹ﮒ۷ﮒﮒﻟ۶ﮔ۲ﮔ۴ﮔﭖﺅﺟ?- ﺅﺟ?ﮔﮒﻝﺏﭨﻝﭨﻛﺕﻛﺕﮔ۶ﺅﺙﻝ؛۵ﮒﮔﭦﮔﻝﭦ۶ﮔﺅﺟ?
### 11.2 ﮒﻟ۶ﮔ۷۰ﮒﻠﮔ

#### 11.2.1 ﮔ۷۰ﮒﻛﺝﻟﭖ

**ﻛﺝﻟﭖﮔ۷۰ﮒ**: `COMPLIANCE_CHECKER_001` (v1.0.0)

**ﮔ۷۰ﮒﻛﺛﻝﺛ؟**: `src/modules/compliance_checker.py`

**ﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵**: [COMPLIANCE_CHECKER_TECHNICAL_SPECIFICATION.md](./COMPLIANCE_CHECKER_TECHNICAL_SPECIFICATION.md)

#### 11.2.2 ﮔﺕﮒﺟﮒﻟﺛ

| ﮒﻟﺛﮔ۷۰ﮒ | ﮒﻟﺛﻟﺁﺑﮔ | ﻝﻝ؟۰ﻛﺝﮔ؟ |
|---------|---------|---------|
| **ﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔ۲ﺅﺟ?* | ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟ۶۵ﮒﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔﮒﺅﺙﮔﺁﻝ۶ﺅﺟ?00ﻝ؛ﮔﮒﮔ۴ﺅﺟ?0000ﻝ؛ﺅﺙ | ﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﻙﻝ؛؛ﻛﺕﮒﻛﺕﮔ۰ |
| **ﮔ۳ﮒﻠﮒﭘﮔ۲ﺅﺟ?* | ﮔ۲ﮔ۴ﮔ۳ﮒﻠ۱ﻝﮒﮔ۳ﮒﻝﮔﺁﮒ۵ﻝ؛۵ﮒﻠﮒﭘﺅﺙﮔﺁﻝ۶ﺅﺟ?5ﻝ؛ﺅﺙﮔ۳ﮒﻝﻗ۳15%ﺅﺟ?| ﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﺅﺟ?|
| **ﻟ؟۱ﮒﮒﻝﮔﭘﻠﺑﮔ۲ﺅﺟ?* | ﮔ۲ﮔ۴ﻟ؟۱ﮒﮔﺁﮒ۵ﮔﭨ۰ﻟﭘﺏﮔﮒﺍﮒﻝﮔﭘﻠﺑﻟ۵ﮔﺎﺅﺙﺅﺟ?0ﮒﺝ؟ﻝ۶ﺅﺟ?| ﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﺅﺟ?|
| **ﻝﻝﭦﺟﻛﭦ۳ﮔﮒﻟ۶ﮔ۲ﺅﺟ?* | ﮔ۲ﮔ۴ﮒ۳۶ﻟ۰ﻛﺕﻝﻝﭦﺟﻛﭦ۳ﮔﻠﻛﭨﮔﺅﺙ6ﻛﺕ۹ﮔﺅﺟ?| ﻟﺁﻝﻛﺙﻙﮒﺏﻛﭦﻝﻝﭦﺟﻛﭦ۳ﮔﻝﻝ؟۰ﻝﻟ۴ﮒﺗﺎﻟ۶ﮒ؟ﺅﺟ?|
| **ﮒﺙﮒﺕﺕﻛﭦ۳ﮔﻟ۰ﻛﺕﭦﻝﮔ۶** | ﻝﮔ۶ﮒﻝﺎﭨﮒﺙﮒﺕﺕﻛﭦ۳ﮔﻟ۰ﻛﺕﭦ | ﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﺅﺟ?|

### 11.3 ﻠﮔﮒ؟ﻝﺍﮔﺗﮔ۰

#### 11.3.1 ﮒﮒ۶ﮒﻠﺅﺟ?
```python
from src.modules.compliance_checker import (
    create_compliance_checker,
    OrderRecord,
    ComplianceLevel
)

class QMTExecutor:
    """QMTﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﺅﺙﻠﮔﮒﻟ۶ﮔ۲ﮔ۴ﺅﺙ"""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        
        # ﮒﮒ۶ﮒQMTﻛﭦ۳ﮔﮔ۴ﮒ۲
        from xtquant.xttrader import XtQuantTrader
        self.trader = XtQuantTrader(
            config.account_id,
            config.session_id,
            config.client_path
        )
        self.trader.start()
        self.trader.subscribe_account(config.account_id)
        
# ﮒﮒ۶ﮒﮔﺕﮒﺟﻝﭨﺅﺟ?        self.converter = OrderConverter()
        self.monitor = OrderMonitor(config)
        self.risk_checker = RiskChecker({})
        self.exception_handler = ExceptionHandler(config)
        self.retry_manager = RetryManager(config)
        self.account_manager = AccountManager(self.trader)
        
        # ﻭ ﮒﮒ۶ﮒﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷
        self.compliance_checker = create_compliance_checker()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("QMTExecutor initialized with compliance checker")
```

#### 11.3.2 ﻟ؟۱ﮒﮔﻛﭦ۳ﮒﮒﻟ۶ﮔ۲ﺅﺟ?
```python
def execute_order(self, unified_order: UnifiedOrder) -> ExecutionResult:
    """ﮔ۶ﻟ۰ﻟ؟۱ﮒﺅﺙﻠﮔﮒﻟ۶ﮔ۲ﮔ۴ﺅﺙ
    
    ﮔ۶ﻟ۰ﮔﭖﻝ۷:
1. ﻛﺙﻝﭨﻠ۲ﻠ۸ﮔ۲ﺅﺟ?    2. ﻭ ﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﺅﺟ?    3. ﻟ؟۱ﮒﻟﺛ؛ﮔ۱
    4. ﻟ؟۱ﮒﮔﻛﭦ۳
    5. ﻟ؟۱ﮒﻝﮔ۶
    
    ﮒﮔﺍ:
        unified_order: ﻝﭨﻛﺕﻟ؟۱ﮒ
        
    ﻟﺟﮒ:
        ﮔ۶ﻟ۰ﻝﭨﮔ
    """
# 1. ﻛﺙﻝﭨﻠ۲ﻠ۸ﮔ۲ﺅﺟ?    if not self.risk_checker.check_order(unified_order):
        return ExecutionResult(
            order_id=unified_order.order_id,
            status=OrderStatus.REJECTED,
            filled_volume=0,
            filled_amount=0.0,
            avg_price=0.0,
            commission=0.0,
            timestamp=datetime.now(),
            error_message="Risk check failed"
        )
    
    # 2. ﻭ ﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﺅﺟ?    compliance_result = self._check_compliance(unified_order)
    
    if not compliance_result.is_compliant:
        self.logger.error(
            f"Order {unified_order.order_id} rejected by compliance check: "
            f"{compliance_result.violations}"
        )
        return ExecutionResult(
            order_id=unified_order.order_id,
            status=OrderStatus.REJECTED,
            filled_volume=0,
            filled_amount=0.0,
            avg_price=0.0,
            commission=0.0,
            timestamp=datetime.now(),
            error_message=f"Compliance check failed: {compliance_result.violations}"
        )
    
# ﻟ؟ﺍﮒﺛﮒﻟ۶ﻟ۵ﮒ
    if compliance_result.warnings:
        self.logger.warning(
            f"Order {unified_order.order_id} compliance warnings: "
            f"{compliance_result.warnings}"
        )
    
    # 3. ﻟ؟۱ﮒﻟﺛ؛ﮔ۱
    qmt_order = self.converter.to_qmt_order(unified_order)
    
    # 4. ﻟ؟۱ﮒﮔﻛﭦ۳
    try:
        order_id = self.trader.order_stock(
            self.config.account_id,
            qmt_order.order_type,
            qmt_order.stock_code,
            qmt_order.order_volume,
            qmt_order.price,
            qmt_order.strategy_name,
            qmt_order.order_remark
        )
        
        # 5. ﮔﺏ۷ﮒﻟ؟۱ﮒﻝﮔ۶
        self.monitor.register_order(order_id)
        
        self.logger.info(
            f"Order submitted successfully: {unified_order.order_id} -> {order_id}"
        )
        
        return ExecutionResult(
            order_id=unified_order.order_id,
            status=OrderStatus.SUBMITTED,
            filled_volume=0,
            filled_amount=0.0,
            avg_price=0.0,
            commission=0.0,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return self.exception_handler.handle_execution_error(unified_order, e)


def _check_compliance(self, unified_order: UnifiedOrder) -> 'ComplianceCheckResult':
    """ﮔ۶ﻟ۰ﮒﻟ۶ﮔ۲ﺅﺟ?    
    ﮒﮔﺍ:
        unified_order: ﻝﭨﻛﺕﻟ؟۱ﮒ
        
    ﻟﺟﮒ:
        ﮒﻟ۶ﮔ۲ﮔ۴ﻝﭨﺅﺟ?    """
    # ﮒﮒﭨﭦﮒﻟ۶ﮔ۲ﮔ۴ﻟ؟۱ﮒﻟ؟ﺍﺅﺟ?    compliance_order = OrderRecord(
        order_id=unified_order.order_id,
        symbol=unified_order.symbol,
        direction='buy' if unified_order.direction == OrderDirection.BUY else 'sell',
        quantity=unified_order.volume,
        price=unified_order.price or 0.0,
        order_type=unified_order.order_type.value,
        timestamp=unified_order.timestamp,
        status='submitted'
    )
    
# ﻟﺓﮒﮔﻛﭨﻛﺟ۰ﮔﺁﺅﺙﻝ۷ﻛﭦﻝﻝﭦﺟﻛﭦ۳ﮔﮔ۲ﮔ۴ﺅﺙ
    position_pct = self._get_position_pct(unified_order.symbol)
    last_trade_date = self._get_last_trade_date(unified_order.symbol)
    
    # ﮔ۶ﻟ۰ﮒﻟ۶ﮔ۲ﺅﺟ?    result = self.compliance_checker.check_order_before_submission(
        order=compliance_order,
        position_pct=position_pct,
        last_trade_date=last_trade_date
    )
    
    return result


def _get_position_pct(self, symbol: str) -> float:
    """ﻟﺓﮒﮔﻛﭨﮔﺁﻛﺝ
    
    ﮒﮔﺍ:
symbol: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ
        
    ﻟﺟﮒ:
        ﮔﻛﭨﮔﺁﻛﺝ
    """
    account_info = self.account_manager.get_account_info(self.config.account_id)
    positions = self.account_manager.get_positions(self.config.account_id)
    
    total_asset = account_info.get('total_asset', 0)
    if total_asset == 0:
        return 0.0
    
    for pos in positions:
        if pos['stock_code'] == symbol:
            return pos['market_value'] / total_asset
    
    return 0.0


def _get_last_trade_date(self, symbol: str) -> Optional[datetime]:
    """ﻟﺓﮒﻛﺕﮔ؛۰ﻛﭦ۳ﮔﮔ۴ﮔ
    
    ﮒﮔﺍ:
symbol: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ
        
    ﻟﺟﮒ:
        ﻛﺕﮔ؛۰ﻛﭦ۳ﮔﮔ۴ﮔ
    """
# TODO: ﻛﭨﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﺕﻟﺓﮒﻛﺕﮔ؛۰ﻛﭦ۳ﮔﮔ۴ﮔ
# ﻟﺟﻠﻠﻟ۵ﻛﭨﮔﺍﮔ؟ﮒﭦﮔﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﺕﮔ۴ﺅﺟ?    return None
```

#### 11.3.3 ﮔ۳ﮒﮒﻟ۶ﮔ۲ﺅﺟ?
```python
def cancel_order(self, order_id: str) -> bool:
    """ﮔ۳ﮒﺅﺙﻠﮔﮒﻟ۶ﮔ۲ﮔ۴ﺅﺙ
    
    ﮒﮔﺍ:
        order_id: ﻟ؟۱ﮒID
        
    ﻟﺟﮒ:
        ﮔﺁﮒ۵ﮔﮒ
    """
    # ﻟﺓﮒﻟ؟۱ﮒﻛﺟ۰ﮔﺁ
    order_status = self.monitor.get_status(order_id)
    
    if order_status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
        self.logger.warning(f"Cannot cancel order {order_id}: status is {order_status}")
        return False
    
    # ﻭ ﮔ۲ﮔ۴ﮔ۳ﮒﻠﺅﺟ?    cancel_check = self.compliance_checker.check_cancel_limits()
    
    if not cancel_check.is_compliant:
        self.logger.error(
            f"Cannot cancel order {order_id}: cancel limit exceeded - "
            f"{cancel_check.violations}"
        )
        return False
    
# ﻟ؟ﺍﮒﺛﮔ۳ﮒﻟ۵ﮒ
    if cancel_check.warnings:
        self.logger.warning(f"Cancel warnings: {cancel_check.warnings}")
    
    # ﮔ۶ﻟ۰ﮔ۳ﮒ
    try:
        self.trader.cancel_order(self.config.account_id, order_id)
        
        # ﻭ ﻟ؟ﺍﮒﺛﮔ۳ﮒﮔﭘﻠﺑﺅﺙﻝ۷ﻛﭦﻟ؟۱ﮒﮒﻝﮔﭘﻠﺑﮔ۲ﮔ۴ﺅﺙ
        self.compliance_checker.order_tracker.record_cancel(
            order_id, 
            datetime.now()
        )
        
        self.logger.info(f"Order cancelled successfully: {order_id}")
        return True
        
    except Exception as e:
        self.logger.error(f"Failed to cancel order {order_id}: {e}")
        return False
```

### 11.4 ﮒ؟ﮔﭘﻝﮔ۶ﻛﭨﭨﮒ۰

#### 11.4.1 ﮒ؟ﮔﭘﮒﻟ۶ﻝﮔ۶

```python
def start_compliance_monitoring(self):
    """ﮒﺁﮒ۷ﮒﻟ۶ﻝﮔ۶"""
    import threading
    import time
    
    def monitoring_loop():
        while True:
            try:
                # ﮔ۲ﮔ۴ﮒﺙﮒﺕﺕﻛﭦ۳ﮔﻟ۰ﺅﺟ?                result = self.compliance_checker.check_abnormal_trading()
                
                if result.compliance_level == ComplianceLevel.WARNING:
                    self.logger.warning(
                        f"Compliance warning: {result.warnings}"
                    )
# TODO: ﮒﻠﮒﻟ۵ﻠﻝ۴
                
                elif result.compliance_level == ComplianceLevel.VIOLATION:
                    self.logger.error(
                        f"Compliance violation: {result.violations}"
                    )
                    # TODO: ﻟ۶۵ﮒﻠ۲ﮔ۶ﮔ۹ﮔﺛ
                
                # ﮔﺁﮒﻠﮔ۲ﮔ۴ﻛﺕﺅﺟ?                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in compliance monitoring: {e}")
                time.sleep(60)
    
    monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitor_thread.start()
    self.logger.info("Compliance monitoring started")
```

#### 11.4.2 ﮔﺁﮔ۴ﻠﻝﺛ؟ﻛﭨﭨﮒ۰

```python
def daily_reset(self):
    """ﮔﺁﮔ۴ﻠﻝﺛ؟ﺅﺙﮒﺙﻝﮒﻟﺍﻝ۷ﺅﺟ?""
    # ﻠﻝﺛ؟ﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷
    self.compliance_checker.reset_daily()
    self.logger.info("Compliance checker reset for new trading day")
```

### 11.5 ﮒﻟ۶ﮔ۴ﮒﻝﮔ

```python
def generate_compliance_report(self) -> Dict:
    """ﻝﮔﮒﻟ۶ﮔ۴ﮒ
    
    ﻟﺟﮒ:
ﮒﻟ۶ﮔ۴ﮒﮒﮒﺕ
    """
    report = self.compliance_checker.generate_compliance_report()
    
    self.logger.info(
        f"Compliance report generated: "
        f"compliance_rate={report['compliance_summary']['compliance_rate']:.2%}"
    )
    
    return report
```

### 11.6 ﻠﻝﺛ؟ﻝ؟۰ﻝ

#### 11.6.1 ﮒﻟ۶ﻠﻝﺛ؟ﮔﻛﭨﭘ

**ﻠﻝﺛ؟ﮔﻛﭨﭘﻛﺛﻝﺛ؟**: `config/compliance_config.yaml`

```yaml
compliance:
# ﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔﮒ
  high_frequency_criteria:
    per_second_threshold: 300      # ﮔﺁﻝ۶ﻝﺏﮔ۴+ﮔ۳ﮒﺅﺟ?00ﺅﺟ?    per_day_threshold: 20000       # ﮒﮔ۴ﻝﺏﮔ۴+ﮔ۳ﮒﺅﺟ?0000ﺅﺟ?    stricter_standard:
per_second: 15                # ﮔﺑﻛﺕ۴ﮔﺙﮔﮒﺅﺙﮔﺁﻝ۶15ﺅﺟ?      cancel_rate_per_day: 0.15     # ﮒﮔ۴ﮔ۳ﮒﻝﻗ۳15%
  
  # ﮔ۳ﮒﻠﮒﭘ
  cancel_order_limits:
    max_cancel_per_second: 15       # ﮔﺁﻝ۶ﮔ۳ﮒﺅﺟ?5ﺅﺟ?    max_cancel_rate_per_day: 0.15   # ﮒﮔ۴ﮔ۳ﮒﻝﻗ۳15%
    min_order_duration_microseconds: 50  # ﻟ؟۱ﮒﮒﻝﺅﺟ?0ﮒﺝ؟ﻝ۶
  
# ﻝﻝﭦﺟﻛﭦ۳ﮔﻟ۶ﮒ
  short_term_trading_rules:
    lock_period_months: 6              # 6ﻛﺕ۹ﮔﻠﻛﭨﺅﺟ?    major_shareholder_threshold: 0.05  # 5%ﮒ۳۶ﻟ۰ﻛﺕﻟ؟۳ﺅﺟ?    penetration_enabled: true          # ﻝ۸ﺟﻠﻝﻝ؟۰ﮒﺁﺅﺟ?  
  # ﻝﮔ۶ﻠﻝﺛ؟
  monitoring:
    enabled: true                      # ﮒﺁﻝ۷ﻝﮔ۶
    check_interval_seconds: 60         # ﮔ۲ﮔ۴ﻠﺑﻠﺅﺙﻝ۶ﺅﺙ
alert_enabled: true                # ﮒﺁﻝ۷ﮒﻟ۵
```

#### 11.6.2 ﮒﻟﺛﺛﻠﻝﺛ؟

```python
import yaml

def load_compliance_config(self, config_path: str = 'config/compliance_config.yaml'):
"""ﮒﻟﺛﺛﮒﻟ۶ﻠﻝﺛ؟
    
    ﮒﮔﺍ:
        config_path: ﻠﻝﺛ؟ﮔﻛﭨﭘﻟﺓﺁﮒﺝ
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # ﻠﮔﺍﮒﮒﭨﭦﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷ﺅﺙﮒﭦﻝ۷ﮔﺍﻠﻝﺛ؟ﺅﺟ?        self.compliance_checker = create_compliance_checker(
            config.get('compliance', {})
        )
        
        self.logger.info(f"Compliance config loaded from {config_path}")
        
    except Exception as e:
        self.logger.error(f"Failed to load compliance config: {e}")
        # ﻛﺛﺟﻝ۷ﻠﭨﻟ؟۳ﻠﻝﺛ؟
        self.compliance_checker = create_compliance_checker()
```

### 11.7 ﮔﭖﻟﺁﻠ۹ﻟﺁ

#### 11.7.1 ﮒﮒﮔﭖﻟﺁ

```python
import unittest
from datetime import datetime, timedelta

class TestQMTExecutorCompliance(unittest.TestCase):
    """QMTExecutorﮒﻟ۶ﮔ۲ﮔ۴ﮔﭖﺅﺟ?""
    
    def setUp(self):
        """ﮔﭖﻟﺁﮒﮒ۶ﺅﺟ?""
        self.config = QMTConfig(
            account_id='test_account',
            session_id='test_session',
            client_path='/path/to/qmt'
        )
        self.executor = QMTExecutor(self.config)
    
    def test_compliance_check_pass(self):
        """ﮔﭖﻟﺁﮒﻟ۶ﮔ۲ﮔ۴ﻠﻟﺟ"""
        order = UnifiedOrder(
            order_id='TEST_001',
            symbol='000001.SZ',
            direction=OrderDirection.BUY,
            order_type=OrderType.LIMIT,
            volume=1000,
            price=10.5,
            strategy_id='test_strategy',
            timestamp=datetime.now()
        )
        
        result = self.executor._check_compliance(order)
        self.assertTrue(result.is_compliant)
    
    def test_high_frequency_detection(self):
        """ﮔﭖﻟﺁﻠ،ﻠ۱ﻛﭦ۳ﮔﮔ۲ﺅﺟ?""
        # ﮔ۷۰ﮔﻠ،ﻠ۱ﻛﭦ۳ﮔﮒﭦﮔﺁ
        for i in range(20):
            order = UnifiedOrder(
                order_id=f'HF_{i:03d}',
                symbol='000001.SZ',
                direction=OrderDirection.BUY,
                order_type=OrderType.LIMIT,
                volume=100,
                price=10.5,
                strategy_id='test_strategy',
                timestamp=datetime.now()
            )
            self.executor._check_compliance(order)
        
        # ﮔ۲ﮔ۴ﻠ،ﻠ۱ﻛﭦ۳ﮔﮔ۲ﺅﺟ?        result = self.executor.compliance_checker.check_high_frequency_trading()
        self.assertEqual(result.compliance_level, ComplianceLevel.WARNING)
    
    def test_cancel_limit_check(self):
        """ﮔﭖﻟﺁﮔ۳ﮒﻠﮒﭘﮔ۲ﺅﺟ?""
        # ﮔ۷۰ﮔﮔ۳ﮒﮒﭦﮔﺁ
        for i in range(20):
            self.executor.compliance_checker.order_tracker.record_cancel(
                f'ORDER_{i:03d}',
                datetime.now()
            )
        
        # ﮔ۲ﮔ۴ﮔ۳ﮒﻠﺅﺟ?        result = self.executor.compliance_checker.check_cancel_limits()
        self.assertFalse(result.is_compliant)


if __name__ == '__main__':
    unittest.main()
```

### 11.8 ﻝﮔ۶ﻛﺕﮒﺅﺟ?
#### 11.8.1 ﻝﮔ۶ﮔﮔ

| ﻝﮔ۶ﮔﮔ | ﻟﺁﺑﮔ | ﮒﻟ۵ﻠﺅﺟﺛ?|
|---------|------|---------|
| **ﮒﻟ۶ﮔ۲ﮔ۴ﮔ؛۰ﺅﺟ?* | ﮔﺁﮔ۴ﮒﻟ۶ﮔ۲ﮔ۴ﮔﭨﮔ؛۰ﺅﺟ?| - |
| **ﻟﺟﻟ۶ﮔ؛۰ﮔﺍ** | ﮔﺁﮔ۴ﻟﺟﻟ۶ﮔ؛۰ﮔﺍ | > 0 ﻝ،ﮒﺏﮒﻟ۵ |
| **ﻟ۵ﮒﮔ؛۰ﮔﺍ** | ﮔﺁﮔ۴ﻟ۵ﮒﮔ؛۰ﮔﺍ | > 10 ﮒﭨﭘﻟﺟﮒﻟ۵ |
| **ﮒﻟ۶ﺅﺟ?* | ﮒﻟ۶ﮔ۲ﮔ۴ﻠﻟﺟﺅﺟ?| < 95% ﮔﺁﮔ۴ﮒﻟ۵ |
| **ﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ۶۵ﮒﮔ؛۰ﮔﺍ** | ﻟ۶۵ﮒﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔ؛۰ﮔﺍ | > 0 ﻝ،ﮒﺏﮒﻟ۵ |
| **ﮔ۳ﮒﺅﺟ?* | ﮔﺁﮔ۴ﮔ۳ﮒﺅﺟ?| > 10% ﻟ۵ﮒﮒﻟ۵ |

#### 11.8.2 ﮒﻟ۵ﻠﻝ۴

```python
def send_compliance_alert(self, level: str, message: str):
    """ﮒﻠﮒﻟ۶ﮒﺅﺟ?    
    ﮒﮔﺍ:
level: ﮒﻟ۵ﻝﭦ۶ﮒ،
message: ﮒﻟ۵ﮔﭘﮔﺁ
    """
# TODO: ﻠﮔﮒﻟ۵ﻝﺏﭨﻝﭨ
    self.logger.warning(f"[COMPLIANCE ALERT] [{level}] {message}")
    
    # ﻝ۳ﭦﻛﺝﺅﺙﮒﻠﻠ؟ﻛﭨﭘﻠﻝ۴
    # send_email(
#     subject=f"[ﮒﻟ۶ﮒﻟ۵] {level}",
    #     body=message
    # )
    
    # ﻝ۳ﭦﻛﺝﺅﺙﮒﻠﮒﺝ؟ﻛﺟ۰ﻠﻝ۴
    # send_wechat_message(message)
```

### 11.9 ﮔﻛﺛﺏﮒ؟ﺅﺟ?
#### 11.9.1 ﮒﺙﮒﮒﭨﭦﺅﺟ?
1. **ﮒ۶ﻝﭨﻟﺟﻟ۰ﮒﻟ۶ﮔ۲ﺅﺟ?*: ﮒ۷ﻟ؟۱ﮒﮔﻛﭦ۳ﮒﮒﺟﻠ۰ﭨﻟﺟﻟ۰ﮒﻟ۶ﮔ۲ﺅﺟ?2. **ﻟ؟ﺍﮒﺛﮔﮔﻟ۵ﺅﺟ?*: ﮒﺏﻛﺛﺟﻠﻟﺟﮔ۲ﮔ۴ﺅﺙﻛﺗﻟ۵ﻟ؟ﺍﮒﺛﻟ۵ﮒﻛﺟ۰ﮔﺁ
3. **ﮒ؟ﮔﻝﮔﮔ۴ﮒ**: ﮔﺁﮔ۴ﻝﮔﮒﻟ۶ﮔ۴ﮒﺅﺙﻛﺝﺟﻛﭦﮒ؟۰ﺅﺟ?4. **ﮒﮔﭘﮔﺑﮔﺍﻟ۶ﮒ**: ﮒﺏﮔﺏ۷ﻝﻝ؟۰ﮒ۷ﮔﺅﺙﮒﮔﭘﮔﺑﮔﺍﮒﻟ۶ﻟ۶ﮒ

#### 11.9.2 ﻟﺟﻝﭨﺑﮒﭨﭦﻟ؟؟

1. **ﮔﺁﮔ۴ﻠﻝﺛ؟**: ﮒﺙﻝﮒﻟﺍﻝ۷ `daily_reset()` ﻠﻝﺛ؟ﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷
2. **ﮒ؟ﮔﭘﻝﮔ۶**: ﮒﺁﮒ۷ﮒﻟ۶ﻝﮔ۶ﻝﭦﺟﻝ۷ﺅﺙﮒ؟ﮔﭘﻝﮔ۶ﻛﭦ۳ﮔﻟ۰ﺅﺟ?3. **ﮒﻟ۵ﮒﮒﭦ**: ﮔﭘﮒﺍﮒﻟ۵ﮒﻝ،ﮒﺏﮒ۳ﻝﺅﺙﻠﺟﮒﻟﺟﻟ۶
4. **ﮒ؟ﮔﮒ؟۰ﻟ؟۰**: ﮒ؟ﮔﮒ؟۰ﻟ؟۰ﮒﻟ۶ﮔ۴ﮒﺅﺙﻛﺙﮒﻛﭦ۳ﮔﻝﺅﺟ?
### 11.10 ﮔﻠﮔﮔ۴

#### 11.10.1 ﮒﺕﺕﻟ۶ﻠ؟ﻠ۱

| ﻠ؟ﻠ۱ | ﮒﺁﻟﺛﮒﮒ | ﻟ۶۲ﮒﺏﮔﺗﮔ۰ |
|------|---------|---------|
| **ﻟ؟۱ﮒﻟ۱،ﮔﺅﺟ?* | ﻟ۶۵ﮒﮒﻟ۶ﻠﮒﭘ | ﮔ۲ﮔ۴ﮒﻟ۶ﮔ۲ﮔ۴ﻝﭨﮔﺅﺙﻟﺍﮔﺑﻛﭦ۳ﮔﻝﻝ۴ |
| **ﻠ،ﻠ۱ﻛﭦ۳ﮔﮒﻟ۵** | ﻛﭦ۳ﮔﻠ۱ﻝﻟﺟﻠ، | ﻠﻛﺛﻛﭦ۳ﮔﻠ۱ﻝﺅﺙﻛﺛﺟﻝ۷ﮔﭦﻟﺛﮔ۶ﻟ۰ﻝ؟ﺅﺟ?|
| **ﮔ۳ﮒﮒ۳ﺎﻟﺑ۴** | ﮔ۳ﮒﻝﻟﭘﺅﺟ?| ﮒﮒﺍﮔ۳ﮒﮔﻛﺛﺅﺙﻛﺙﮒﻟ؟۱ﮒﻛﭨﺓﺅﺟ?|
| **ﮒﻟ۶ﮔ۴ﮒﮒﺙﮒﺕﺕ** | ﮔﺍﮔ؟ﻝﭨﻟ؟۰ﻠﻟﺁﺁ | ﮔ۲ﮔ۴ﻟ؟۱ﮒﻟﺓﻟﺕ۹ﮒ۷ﺅﺙﻠﻝﺛ؟ﮔﺁﮔ۴ﮔﺍﺅﺟ?|

#### 11.10.2 ﮔ۴ﮒﺟﮒﮔ

```python
# ﮔ۴ﻝﮒﻟ۶ﮔ۲ﮔ۴ﮔ۴ﺅﺟ?# grep "COMPLIANCE" logs/trading.log

# ﮔ۴ﻝﻟﺟﻟ۶ﻟ؟ﺍﮒﺛ
# grep "Compliance violation" logs/trading.log

# ﮔ۴ﻝﮒﻟ۵ﻟ؟ﺍﮒﺛ
# grep "COMPLIANCE ALERT" logs/trading.log
```

### 11.11 ﮔﭨﻝﭨ

**ﻠﮔﻛﭨﺓﺅﺟﺛ?*ﺅﺟ?- ﺅﺟ?**ﮒﻟ۶ﻛﺟﻠ**: ﻝ۰؟ﻛﺟﻝﺏﭨﻝﭨ100%ﻝ؛۵ﮒﮔﮔﺍﻝﻝ؟۰ﻟ۵ﺅﺟ?- ﺅﺟ?**ﻠ۲ﻠ۸ﻠ۱ﻟ۵**: ﮒ؟ﮔﭘﻝﮔ۶ﺅﺙﮔﮒﻠ۱ﻟ۵ﮒﻟ۶ﻠ۲ﺅﺟ?- ﺅﺟ?**ﮔﮔ؛ﻠﻛﺛ**: ﻟ۹ﮒ۷ﮒﮒﻟ۶ﮔ۲ﮔ۴ﺅﺙﻠﻛﺛﻛﭦﭦﮒﺓ۴ﮔﮔ؛
- ﺅﺟ?**ﻛﺕﻛﺕﮔﮒ**: ﻝ؛۵ﮒﮔﭦﮔﻝﭦ۶ﮔﮒﺅﺙﮔﮒﻝﺏﭨﻝﭨﻛﺕﻛﺕﺅﺟ?
**ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟**ﺅﺟ?1. **ﻝ،ﮒﺏﻠﮔ**: ﮒﺍﮒﻟ۶ﮔ۲ﮔ۴ﮔ۷۰ﮒﻠﮔﮒﺍQMTExecutor
2. **ﮒ؟ﮔﻝﮔ۶**: ﻟ؟ﺝﻝﺛ؟ﮒ؟ﮔﭘﻛﭨﭨﮒ۰ﺅﺙﮒ؟ﮔﭘﻝﮔ۶ﮒﻟ۶ﻝﭘﺅﺟ?3. **ﮔﻝﭨﮔﺑﮔﺍ**: ﮒﺏﮔﺏ۷ﻝﻝ؟۰ﮒ۷ﮔﺅﺙﮒﮔﭘﮔﺑﮔﺍﻟ۶ﮒ
4. **ﮒﺗﻟ؟ﮒ۱ﻠ**: ﻝ۰؟ﻛﺟﮒ۱ﻠﻝﻟ۶۲ﮒﻟ۶ﻟ۵ﮔﺎ

---

**ﮔﮔ۰۲ﻝﮔ؛**: v1.2.0 | **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02 | **ﻝﭨﺑﮔ۳ﻟ?*: ﻝﻝ۴ﮔ۶ﻟ۰ﮒﺎﻟﺑﻟﺑ۲ﻛﭦﭦ
