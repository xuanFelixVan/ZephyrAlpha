---
module_id: QMT_EXECUTOR_SPEC_001
version: 1.2.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-03
owner: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 扩展功能、辅助模块
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵
applicable_scope: Layer 5 ﻝ­ﻝ۴ﮔ۶ﻟ۰ﺅﺟ?| ﻛﺕﮒ۰ﮔﭘﮔ: ﻛﺕﻝﭦ۶ﮔﭘﻠﺑﮔ۰ﮔﭘﻟﮒﮔﭘﮔ
compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﺅﺟ?
regulatory_compliance:
  - module: COMPLIANCE_CHECKER_001
    version: 1.0.0
    integration_date: 2026-04-03
---
---


# QMTExecutorﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﮔ۷۰ﮒﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.3 - QMTExecutorﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﮔ۷۰ﮒﻟﺁ۵ﻝﭨﮔﮔﺁﻟ؟ﺝﺅﺟ?
> **ﮔ۷۰ﮒID**: `QMT_EXECUTOR_001`
> **ﻝﮔ؛**: v1.0.0
> **ﻝﭘﺅﺟﺛ?*: ﺅﺟ?ﮔ­۲ﮒﺙ


## 1. ﮔ۵ﻟﺟﺍ

### 1.1 ﻟ؟ﺝﻟ؟۰ﻟﮔﺁﻛﺕﻛﺕﮒ۰ﻝ؟ﺅﺟ?
- **ﻛﺕﮒ۰ﻠﺅﺟ?*: ﻝﺏﭨﻝﭨﻠﻟ۵ﻝﭨﻛﺕﻝﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﻟﺟﻟ۰ﮒ؟ﻝﻛﭦ۳ﮔﮔ۶ﻟ۰
- **ﮔﮔﺁﻝﺅﺟ?*: 
  - ﻛﭦ۳ﮔﮔ۶ﻟ۰ﻛﺕﻝ۷ﺏﮒ؟ﺅﺙﻝﺙﭦﻛﺗﻝﭨﻛﺕﻝﻟ؟۱ﮒﻝ؟۰ﻝﮒﮔ۶ﻟ۰ﮔﭦﮒﭘ
  - ﻟ؟۱ﮒﻝﭘﮔﻝﮔ۶ﮒﺍﻠﺝﺅﺙﻝﺙﭦﻛﺗﮒ؟ﮔﭘﻝﻟ؟۱ﮒﻝﭘﮔﻟﺓﺅﺟ?
  - ﻛﭦ۳ﮔﮒﺙﮒﺕﺕﮒ۳ﻝﻛﺕﻟﭘﺏﺅﺙﻝﺙﭦﻛﺗﮒ؟ﮒﻝﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﺅﺟ?
  - ﻛﭦ۳ﮔﻠ۲ﻠ۸ﮔ۶ﮒﭘﻝﺙﭦﮒ۳ﺎﺅﺙﻝﺙﭦﻛﺗﻛﭦ۳ﮔﮒﻝﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
- **ﻠ۱ﮔﻛﭨﺓﺅﺟﺛ?*: 
  - ﮒﭨﭦﻝ،ﻝﭨﻛﺕﻝﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒﻝ؟۰ﻝﮔﭦﮒﭘ
  - ﮔﻛﺝﮒ؟ﮔﭘﻝﻟ؟۱ﮒﻝﭘﮔﻝﮔ۶ﮒﻟﺓﻟﺕ۹
  - ﮒ؟ﻝﺍﮒ؟ﮒﻝﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘ
  - ﮔﺁﮔﻛﭦ۳ﮔﮒﻝﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒﮔ۶ﮒﭘ

### 1.2 ﮔﮔﺁﮒ؟ﻛﺛﻛﺕﮔﭘﮔﮒﺎﮒﺛﺅﺟ?
- **Layerﮒ؟ﻛﺛ**: Layer 5 - ﻝ­ﻝ۴ﮔ۶ﻟ۰ﺅﺟ?(ﻝ؛۵ﮒARCHITECTURE.mdﮒ؟ﻛﺗ)
- **ﮔ۷۰ﮒﻝﺎﭨﮒ،**: ﮔ ﺕﮒﺟﻛﭦ۳ﮔﮔ۶ﻟ۰ﮔ۷۰ﮒ
- **ﮔﭘﮔﻟ۶ﻟﺎ**: Layer 5ﻝ­ﻝ۴ﮔ۶ﻟ۰ﮔ ﺕﮒﺟﺅﺙﻟﺑﻟﺑ۲ﮒ؟ﻝﻛﭦ۳ﮔﮔ۶ﺅﺟ?

### 1.3 ﻝﮔ؛ﻛﺟ۰ﮔﺁ
| ﻝﮔ؛ | ﮔ۴ﮔ | ﻛﺛﺅﺟﺛ?| ﮒﮔﺑﻟﺁﺑﮔ | ﻝﭘﺅﺟﺛ?|
|------|------|------|----------|------|
| v1.0.0 | 2026-04-02 | ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟ | ﮒﮒ۶ﻝﮔ؛ | Active |
| v1.1.0 | 2026-04-03 | ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?| ﻠﮔﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﮔ۴ﮔ۷۰ﮒﺅﺙCOMPLIANCE_CHECKER_001ﺅﺙ?| Active |
| v1.2.0 | 2026-04-03 | ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?| ﮒ۱ﮒ "ﻠﻛﺟﻝﻟ۶۲"ﻝ، ﻟﺅﺙﮔﮒﮔﮔ۰۲ﮒﺁﻟﺁﭨﮔ?| Active |

### 1.4 ﻠﻛﺟﻝﻟ۶۲

#### 1.4.1 ﻛﺕﮒ۴ﻟﺁﻟ۶۲ﻠ

**QMTExecutor = ﮔ۷ﻝ"ﻛﭦ۳ﮔﮔ۶ﻟ۰ﻝ؟۰ﮒ؟ﭘ"**

ﮒﺍﺎﮒﮔ۷ﮔﻛﺕﻛﺕ۹ﻛﺕﻠ۷ﻝﻝ؟۰ﮒ؟ﭘﮒﺕ؟ﮔ۷ﮒ۳ﻝﮔﮔﻛﭦ۳ﮔﻝﺕﮒﺏﻝﻛﭦﮔﺅﺙﻝ۰؟ﻛﺟﻛﭦ۳ﮔﮒ؟ﮒ۷ﻙﮒﻟ۶ﻙﻠ،ﮔﮒﺍﮔ۶ﻟ۰ﻙ?
#### 1.4.2 ﮒ۷ﻛﭦ۳ﮔﮔﭖﻝ۷ﻛﺕ­ﻝﻛﺛﻝﺛ?
```
ﻛﭦ۳ﮔﮒﺏﻝ­ﮔﭖﻝ۷ﺅﺙ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ?ﻝ­ﻝ۴ﻝﮔﻛﺟ۰ﮒﺓ ﻗ? Layer 3-4
ﻗ?(ﻛﺗﺍﮒ۴/ﮒﮒﭦ)  ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?       ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ?QMTExecutor ﻗ? ﻗ?ﻟﺟﻠﺅﺙﻛﭦ۳ﮔﮔ۶ﻟ۰ﻝ؟۰ﮒ؟?ﻗ? ﮔ۶ﻟ۰ﻛﭦ۳ﮔ    ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?       ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ?QMTﻛﭦ۳ﮔﮔ۴ﮒ۲  ﻗ? ﮒ؟ﻠﻛﺕﮒ
ﻗ?(ﮒﺕﮒﻝﺏﭨﻝﭨ)   ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```

#### 1.4.3 ﮔ ﺕﮒﺟﮒﻟﺛﻝﺎﭨﮔﺁ

**1. ﻟ؟۱ﮒﮔ۶ﻟ۰ = "ﻛﺕﮒﮒ?**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﻠ۳ﮒﻝﮔﮒ۰ﮒﺅﺙﮔﮔ۷ﻝﻟ؟۱ﮒﻠﮒﺍﮒ۷ﮔﺟﺅﺙﮒﺕﮒﻝﺏﭨﻝﭨﺅﺙ

```python
# ﻝ­ﻝ۴ﻟﺁﺑﺅﺙﻛﺗﺍﮒ۴1000ﻟ۰ﮒﺗﺏﮒ؟ﻠﭘﻟ۰?strategy_signal = {
    "symbol": "000001.SZ",
    "action": "buy",
    "quantity": 1000,
    "price": 10.5
}

# QMTExecutorﻟﺑﻟﺑ۲ﺅﺙ?# 1. ﮔ۲ﮔ۴ﻟ؟۱ﮒﮔﺁﮒ۵ﮒﻝ?# 2. ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮒﻟ۶ﺅﺙﮔﺍﮒ۱ﺅﺙﺅﺙ
# 3. ﻟﺛ؛ﮔ۱ﻛﺕﭦQMTﮔ ﺙﮒﺙ
# 4. ﮔﻛﭦ۳ﻝﭨﮒﺕﮒﻝﺏﭨﻝﭨ?qmt_executor.execute_order(strategy_signal)
```

**2. ﻟ؟۱ﮒﻝﮔ۶ = "ﻟ؟۱ﮒﻟﺓﻟﺕ۹ﮒ?**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﮒﺟ،ﻠﻟﺟﺛﻟﺕ۹ﻝﺏﭨﻝﭨﺅﺙﮒ؟ﮔﭘﮔ۴ﻝﻟ؟۱ﮒﻝﭘﮔ?
```python
# ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﻝﭘﮔ?status = qmt_executor.get_order_status("ORDER_001")

# ﮒﺁﻟﺛﻝﻝﭘﮔﺅﺙ
# - pending: ﮒﺝﮔﻛﭦ?# - submitted: ﮒﺓﺎﮔﻛﭦ?# - partial_filled: ﻠ۷ﮒﮔﻛﭦ۳
# - filled: ﮒ؟ﮒ۷ﮔﻛﭦ۳
# - cancelled: ﮒﺓﺎﮔ۳ﻠ
# - rejected: ﮒﺓﺎﮔﻝﭨ?```

**3. ﻠ۲ﻠ۸ﮔ۶ﮒﭘ = "ﮒ؟ﮒ۷ﮔ۲ﮔ۴ﮒ"**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﮔﭦﮒﭦﮒ؟ﮔ۲ﺅﺙﮒ۷ﻝﭨﮔﭦﺅﺙﻛﺕﮒﺅﺙﮒﻟﺟﻟ۰ﮒ؟ﮒ۷ﮔ۲ﮔ?
```python
# ﻛﺕﮒﮒﻟ۹ﮒ۷ﮔ۲ﮔ۴ﺅﺙ
# 1. ﻟﭖﻠﮔﺁﮒ۵ﮒﻟﭘﺏﺅﺙ?# 2. ﮔﻛﭨﮔﺁﮒ۵ﻟﭘﻠﺅﺙ?# 3. ﻛﭨﺓﮔ ﺙﮔﺁﮒ۵ﮒﻝﺅﺙ?# 4. ﮔﺁﮒ۵ﻟ۶۵ﮒﻠ۲ﮔ۶ﻟ۶ﮒﺅﺙ?
if not risk_checker.check_order(order):
    print("ﻟ؟۱ﮒﻟ۱،ﮔﻝﭨﺅﺙﻟﭖﻠﻛﺕﻟﭘﺏ")
```

**4. ﮒﻟ۶ﮔ۲ﮔ?= "ﮒﻟ۶ﮒ؟? ﻭ**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﻛﭦ۳ﻟ­۵ﺅﺙﻝ۰؟ﻛﺟﮔ۷ﻝﻠ۸ﺝﻠ۸ﭘﺅﺙﻛﭦ۳ﮔﺅﺙﻝ؛۵ﮒﻛﭦ۳ﻠﻟ۶ﮒﺅﺙﻝﻝ؟۰ﻟ۵ﮔﺎﺅﺙ?
```python
# ﻛﺕﮒﮒﻟ۹ﮒ۷ﮔ۲ﮔ۴ﺅﺙ
# 1. ﮔﺁﮒ۵ﻟ۶۵ﮒﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﺅﺙ?# 2. ﮔ۳ﮒﻝﮔﺁﮒ۵ﻟﭘﮔ ﺅﺙ
# 3. ﮔﺁﮒ۵ﻟﺟﮒﻝ­ﻝﭦﺟﻛﭦ۳ﮔﻟ۶ﮒﺅﺙ?# 4. ﻟ؟۱ﮒﮒﻝﮔﭘﻠﺑﮔﺁﮒ۵ﻟﭘﺏﮒ۳ﺅﺙ?
compliance_result = compliance_checker.check(order)
if not compliance_result.is_compliant:
    print("ﻟ؟۱ﮒﻟ۱،ﮔﻝﭨﺅﺙﻟﺟﮒﻝﻝ؟۰ﻟ۶ﮒ")
```

**5. ﮒﺙﮒﺕﺕﮒ۳ﻝ = "ﮔﻠﻛﺟ؟ﮒ۳ﮒﺕ?**

ﻝﺎﭨﮔﺁﺅﺙﮒﺍﺎﮒﮒﭨﻠ۱ﻝﮔ۴ﻟﺁﻝ۶ﺅﺙﮒ۳ﻝﮒﻝ۶ﻝ۹ﮒﻝﭘﮒﭖ

```python
# ﮒﺁﻟﺛﻝﮒﺙﮒﺕﺕﮔﮒﭖﺅﺙ
# - ﻝﺛﻝﭨﻛﺕ­ﮔ­
# - ﮒﺕﮒﻝﺏﭨﻝﭨﮔﻠ
# - ﻟ؟۱ﮒﻟ۱،ﮔﻝﭨ?# - ﮔﻛﭦ۳ﻛﭨﺓﮔ ﺙﮒﺙﮒﺕﺕ

# QMTExecutorﻟ۹ﮒ۷ﮒ۳ﻝﺅﺙ?try:
    execute_order(order)
except NetworkError:
    # ﻟ۹ﮒ۷ﻠﻟﺁ
    retry_manager.retry(order)
except BrokerError:
    # ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻠﻝ۴ﻝ۷ﮔﺓ
    logger.error("ﮒﺕﮒﻝﺏﭨﻝﭨﮔﻠ")
```

#### 1.4.4 ﻝﮔﺑﭨﮒﻝﺎﭨﮔﺁﺅﺙﻠ۳ﮒﮒﭦﮔﺁ

| ﻠ۳ﮒﮒﭦﮔﺁ | ﻠﮒﻛﭦ۳ﮔﻝﺏﭨﻝﭨ | QMTExecutorﻝﻛﺛﻝ?|
|---------|------------|-----------------|
| **ﮔ۷ﺅﺙﻠ۰ﺝﮒ؟۱ﺅﺙ?* | ﻝ­ﻝ۴ﻝﺏﭨﻝﭨ | ﮒﺏﮒ؟ﮒﻛﭨﻛﺗﺅﺙﻛﺗﺍﻛﭨﻛﺗﻟ۰ﻝ۴۷ﺅﺙ |
| **ﮔﮒ۰ﮒ?* | **QMTExecutor** | ﮔ۴ﮒﻙﻛﺕﮒﻙﻟﺓﻟﺕ۹ﻙﮒ۳ﻝﻠ؟ﻠ۱?|
| **ﮒ۷ﮔﺟ** | QMTﮒﺕﮒﻝﺏﭨﻝﭨ | ﮒ؟ﻠﮒﻟﺅﺙﮔ۶ﻟ۰ﻛﭦ۳ﮔﺅﺙ |
| **ﻟﮒ** | ﻛﭦ۳ﮔﮔ۴ﮒ۲ | ﮔﻛﺝﮒﺁﻝ۷ﻝﻛﭦ۳ﮔﻠﻠ۰ﺗ |
| **ﻟﺑ۵ﮒ** | ﮔﻛﭦ۳ﮒﮔ۴ | ﮒﻟﺁﮔ۷ﻟﺎﻛﭦﮒ۳ﮒﺍﻠﺎ |

**QMTExecutorﮒﺍﺎﮔﺁﻠ۲ﻛﺕ۹ﻛﺕﻛﺕﻝﮔﮒ۰ﮒ**ﺅﺙﻝ۰؟ﻛﺟﺅﺙ
- ﻗ?ﮔ۷ﻝﻟ؟۱ﮒﮒﻝ۰؟ﮔ ﻟﺁﺁﮒﺍﻛﺙ ﻟﺝﺝﮒﺍﮒ۷ﮔﺟ
- ﻗ?ﮒ؟ﮔﭘﮒﻟﺁﮔ۷ﻟﮒﮒﺍﮒ۹ﻛﺕﮔ­۴ﻛﭦ
- ﻗ?ﮒ۵ﮔﮒ۷ﮔﺟﮒﭦﻠ؟ﻠ۱ﺅﺙﮒﮔﭘﮒ۳ﻝ
- ﻗ?ﻝ۰؟ﻛﺟﮔ۷ﮔﻟﭘﺏﮒ۳ﻝﻠﺎﻛﭨﮔ؛ﺝ
- ﻗ?ﻝ۰؟ﻛﺟﮔ۷ﻝﻝﺗﻟﻝ؛۵ﮒﻠ۳ﮒﻟ۶ﮒ؟

#### 1.4.5 ﻛﺕQMTﻝﮒﺏﻝﺏ?
**QMT = ﻟﺟﮔﻠﮒﻛﭦ۳ﮔﻝﭨﻝ،ﺁ**ﺅﺙﻛﺕﮔ؛ﺝﻠﮒﻛﭦ۳ﮔﻟﺛﺁﻛﭨﭘﺅﺙ

```
QMTﮔﻛﺝﺅﺙ?- ﻛﭦ۳ﮔﮔ۴ﮒ۲ﺅﺙXtQuantTraderﺅﺙ?- ﮔﺍﮔ؟ﮔ۴ﮒ۲
- ﻟ؟۱ﮒﮔ۴ﮒ۲
```

**QMTExecutorﻛﺕQMTﻝﮒﺏﻝﺏ?*ﺅﺙ?
```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ? ﮔ۷ﻝﻝ­ﻝ۴ﻝﺏﭨﻝﭨ    ﻗ?ﻗ? (ﮒﺏﻝ­ﻛﺗﺍﻛﭨﻛﺗ?    ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗﻗﻗ?         ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ? QMTExecutor    ﻗ? ﻗ?ﻛﺕ­ﻠﺑﮒﺎﺅﺙﻝﺟﭨﻟﺁﮒ؟?ﻗ? (ﻟ؟۱ﮒﮒ۳ﻝ)      ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗﻗﻗ?         ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗ? QMTﻛﭦ۳ﮔﮔ۴ﮒ۲     ﻗ? ﻗ?ﮒﭦﮒﺎﮔ۴ﮒ۲
ﻗ? (ﮒﺕﮒﻝﺏﭨﻝﭨ)      ﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```

**QMTExecutorﻝﻛﺛﻝ?*ﺅﺙ?1. **ﻝﺟﭨﻟﺁﮒ؟?*ﺅﺙﮔﮔ۷ﻝﻝ­ﻝ۴ﻛﺟ۰ﮒﺓﻝﺟﭨﻟﺁﮔQMTﻟﺛﻝﻟ۶۲ﻝﮔ ﺙﮒﺙ
2. **ﻛﺟﮔ۳ﻛﺙ?*ﺅﺙﮒ۷ﻟﺍﻝ۷QMTﮔ۴ﮒ۲ﮒﻟﺟﻟ۰ﮒﻝ۶ﮔ۲ﮔ۴ﺅﺙﻠ۲ﻠ۸ﻙﮒﻟ۶ﺅﺙ
3. **ﻝﮔ۶ﮒ?*ﺅﺙﮒ؟ﮔﭘﻝﮔ۶QMTﻟﺟﮒﻝﻟ؟۱ﮒﻝﭘﮔ?4. **ﮔﻠﮒ۳ﻝ**ﺅﺙﮒ۳ﻝQMTﮔ۴ﮒ۲ﮒﺁﻟﺛﮒﭦﻝﺍﻝﮒﻝ۶ﮒﺙﮒﺕ?
#### 1.4.6 ﻛﺕﭦﻛﭨﻛﺗﻠﻟ۵QMTExecutorﺅﺙ?
**ﻠ؟ﻠ۱ﺅﺙﻛﺕﭦﻛﭨﻛﺗﻛﺕﻝﺑﮔ۴ﻟﺍﻝ۷QMTﮔ۴ﮒ۲ﺅﺙ?*

ﻝ­ﮔ۰ﺅﺙﮒﺍﺎﮒﻛﺕﭦﻛﭨﻛﺗﻛﺕﻝﺑﮔ۴ﮒﭨﮒ۷ﮔﺟﻝﺗﻟﺅﺙ

| ﻝﺑﮔ۴ﻟﺍﻝ۷QMT | ﻠﻟﺟQMTExecutor |
|-----------|---------------|
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﮒ۳ﻝﻟ؟۱ﮒﮔ ﺙﮒﺙﻟﺛ؛ﮔ?| ﻗ?ﻟ۹ﮒ۷ﻟﺛ؛ﮔ۱ﮔ ﺙﮒﺙ |
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﻝﮔ۶ﻟ؟۱ﮒﻝﭘﮔ?| ﻗ?ﻟ۹ﮒ۷ﻝﮔ۶ﮒﻠﻝ۴ |
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﮒ۳ﻝﮒﺙﮒﺕ?| ﻗ?ﻟ۹ﮒ۷ﻠﻟﺁﮒﮔ۱ﮒ۳?|
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﮔ۲ﮔ۴ﻠ۲ﻠ?| ﻗ?ﻟ۹ﮒ۷ﻠ۲ﻠ۸ﮔ۲ﮔ?|
| ﻗ?ﻠﻟ۵ﻟ۹ﮒﺓﺎﮔ۲ﮔ۴ﮒﻟ۶?| ﻗ?ﻟ۹ﮒ۷ﮒﻟ۶ﮔ۲ﮔ?|
| ﻗ?ﻛﭨ۲ﻝ ﻠﮒ۳ﺅﺙﻠﺝﻛﭨ۴ﻝﭨﺑﮔ?| ﻗ?ﻝﭨﻛﺕﮔ۴ﮒ۲ﺅﺙﮔﻛﭦﻝﭨﺑﮔ?|

#### 1.4.7 ﮔ ﺕﮒﺟﻛﭨﺓﮒ?
| ﻛﭨﺓﮒ?| ﻟﺁﺑﮔ |
|------|------|
| **ﻝﭨﻛﺕﮔ۴ﮒ۲** | ﮔﻛﺝﻝ؟ﮒﮔﻝ۷ﻝﻛﭦ۳ﮔﮔ۴ﮒ۲ |
| **ﻠ۲ﻠ۸ﮔ۶ﮒﭘ** | ﻟ۹ﮒ۷ﮔ۲ﮔ۴ﮒﻝ۶ﻠ۲ﻠ?|
| **ﮒﻟ۶ﮔ۲ﮔ?* | ﻝ۰؟ﻛﺟﻝ؛۵ﮒﻝﻝ؟۰ﻟ۵ﮔﺎ ﻭ |
| **ﮒﺙﮒﺕﺕﮒ۳ﻝ** | ﻟ۹ﮒ۷ﮒ۳ﻝﮒﻝ۶ﮒﺙﮒﺕﺕ |
| **ﻟ؟۱ﮒﻝﮔ۶** | ﮒ؟ﮔﭘﻟﺓﻟﺕ۹ﻟ؟۱ﮒﻝﭘﮔ?|

---

## 2. ﻟﺁ۵ﻝﭨﮔﭘﮔﻟ؟ﺝﻟ؟۰

### 2.1 ﻝﺏﭨﻝﭨﮔﭘﮔﺅﺟ?
```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?
ﺅﺟ?                   Layer 5: ﻝ­ﻝ۴ﮔ۶ﻟ۰ﺅﺟ?                      ﺅﺟ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?
ﺅﺟ?                                                            ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ?       QMTExecutor (ﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﻛﺕﭨﮔ۷۰ﮒ)                  ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﻟ؟۱ﮒﮔ۶ﻟ۰                                            ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﻟ؟۱ﮒﻝﮔ۶                                            ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﮒﺙﮒﺕﺕﮒ۳ﻝ                                            ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﻠ۲ﻠ۸ﮔ۶ﮒﭘ                                            ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - ﮒﻟ۶ﮔ۲ﺅﺟ?ﻭ                                         ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ?                          ﺅﺟ?                                 ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ?         ﮔ ﺕﮒﺟﻝﭨﻛﭨﭘ                                      ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗOrderConverterﺅﺟ?ﻗOrderMonitor ﺅﺟ?ﻗRiskChecker  ﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻟ؟۱ﮒﻟﺛ؛ﮔ۱ﮒ۷     ﺅﺟ? ﻗﻟ؟۱ﮒﻝﮔ۶ﮒ۷   ﺅﺟ? ﻗﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۷   ﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗExceptionHdlrﺅﺟ?ﻗRetryManager ﺅﺟ?ﻗAccountManagerﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﮒﺙﮒﺕﺕﮒ۳ﻝﮒ۷    ﺅﺟ? ﻗﻠﻟﺁﻝ؟۰ﻝﮒ۷   ﺅﺟ? ﻗﻟﺑ۵ﮔﺓﻝ؟۰ﻝﮒ۷   ﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?                                      ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗComplianceChkﺅﺟ?ﻭ ﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷                     ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﺅﺟ?COMPLIANCE_ ﺅﺟ? - ﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔ۲ﺅﺟ?                  ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗCHECKER_001) ﺅﺟ? - ﮔ۳ﮒﻠﮒﭘﮔ۲ﺅﺟ?                      ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﺅﺟ?            ﺅﺟ? - ﻝ­ﻝﭦﺟﻛﭦ۳ﮔﮒﻟ۶ﮔ۲ﺅﺟ?                  ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?                                      ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ?                          ﺅﺟ?                                 ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ?         QMT APIﺅﺟ?                                   ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - XtQuantTrader (ﻛﭦ۳ﮔAPI)                           ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - xtdata (ﮔﺍﮔ؟API)                                  ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﺅﺟ? - xtorder (ﻟ؟۱ﮒAPI)                                 ﺅﺟ? ﺅﺟ?
ﺅﺟ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ? ﺅﺟ?
ﺅﺟ?                                                            ﺅﺟ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?
```

### 2.2 Layerﮒ؟ﻛﺛﻟﺁ۵ﻝﭨﻟﺁﺑﮔ
- **Layerﮒﺛﮒﺎ**: Layer 5 - ﻝ­ﻝ۴ﮔ۶ﻟ۰ﺅﺟ?
- **ﻟﻟﺑ۲ﻟﮒﺑ**: ﻟ؟۱ﮒﮔ۶ﻟ۰ﻙﻟ؟۱ﮒﻝﮔ۶ﻙﮒﺙﮒﺕﺕﮒ۳ﻝﻙﻠ۲ﻠ۸ﮔ۶ﺅﺟ?
- **ﻛﺕﻛﺕﮒﺎﮔ۴ﺅﺟ?*: 
  - ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 5 SignalGenerator (ﮔﻛﺝﻛﭦ۳ﮔﻛﺟ۰ﮒﺓ)
  - ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 6 ﻝﭨﮒﻛﺙﮒﺅﺟ?(ﮔ۴ﮔﭘﮔ۶ﻟ۰ﻝﭨﮔ)

### 2.3 ﮔ۷۰ﮒﻟﻟﺑ۲ﻛﺕﻟﺝﺗﻝﮒ؟ﺅﺟ?
- **ﮔ ﺕﮒﺟﻟﻟﺑ۲**: ﮒ؟ﻝﻛﭦ۳ﮔﮔ۶ﻟ۰ﻙﻟ؟۱ﮒﻝ؟۰ﻝﻙﻠ۲ﻠ۸ﮔ۶ﺅﺟ?
- **ﻟﻟﺑ۲ﻟﺝﺗﻝ**: 
  - ﺅﺟ?ﮔ؛ﮔ۷۰ﮒﻟﺑﺅﺟ? ﻟ؟۱ﮒﮔ۶ﻟ۰ﻙﻟ؟۱ﮒﻝﮔ۶ﻙﮒﺙﮒﺕﺕﮒ۳ﻝﻙﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
  - ﺅﺟ?ﮔ؛ﮔ۷۰ﮒﻛﺕﻟﺑﻟﺑ۲: ﻛﺟ۰ﮒﺓﻝﮔﻙﻝ­ﻝ۴ﮒﺏﻝ­ﻙﮔﺍﮔ؟ﻟﺓﮒﻙﻠ۲ﻠ۸ﮔ۷۰ﺅﺟ?
- **ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵**: ﮔﻛﺝﻝﭨﻛﺕﻝPython APIﮔ۴ﮒ۲

### 2.4 ﻛﺝﻟﭖﮒﺏﻝﺏﭨ
| ﻛﺝﻟﭖﮔ۷۰ﮒ | ﻛﺝﻟﭖﻝﺎﭨﮒ | ﮔ۴ﮒ۲ﮔﺗﮒﺙ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﮒ۳ﮔﺏ۷ |
|----------|----------|----------|----------|------|
| xtquant | ﮒﺙﭦﻛﺝﺅﺟ?| QMT Python API | >=1.0.0 | QMTﮒ؟ﮔﺗAPI |
| threading | ﮒﺙﭦﻛﺝﺅﺟ?| Pythonﮔ ﮒﺅﺟ?| >=3.8 | ﮒ۳ﻝﭦﺟﻝ۷ﮔﺁﺅﺟ?|
| queue | ﮒﺙﭦﻛﺝﺅﺟ?| Pythonﮔ ﮒﺅﺟ?| >=3.8 | ﻠﮒﮔﺁﮔ |

---

## 3. ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 3.1 APIﮔ۴ﮒ۲ﻟ۶ﻟ

#### 3.1.1 ﻛﺕﭨﮔ۴ﮒ۲ﻝﺎﭨ
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
    """ﻟ؟۱ﮒﻝﭘﮔﮔﺅﺟ?""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    ERROR = "error"


class OrderType(Enum):
    """ﻟ؟۱ﮒﻝﺎﭨﮒﮔﻛﺕﺝ"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderDirection(Enum):
    """ﻟ؟۱ﮒﮔﺗﮒﮔﻛﺕﺝ"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class UnifiedOrder:
    """ﻝﭨﻛﺕﻟ؟۱ﮒﮔ ﺙﮒﺙ"""
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
    """QMTﻟ؟۱ﮒﮔ ﺙﮒﺙ"""
    stock_code: str
    order_type: int
    order_volume: int
    price: float
    strategy_name: str
    order_remark: str


@dataclass
class ExecutionResult:
    """ﮔ۶ﻟ۰ﻝﭨﮔ"""
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
    """QMTﻠﻝﺛ؟"""
    account_id: str
    session_id: str
    client_path: str
    max_retry: int = 3
    retry_interval: float = 1.0
    order_timeout: int = 60


class OrderConverter:
    """ﻟ؟۱ﮒﻟﺛ؛ﮔ۱ﺅﺟ?""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def to_qmt_order(self, unified_order: UnifiedOrder) -> QMTOrder:
        """ﮒﺍﻝﭨﻛﺕﻟ؟۱ﮒﻟﺛ؛ﮔ۱ﻛﺕﭦQMTﻟ؟۱ﮒﮔ ﺙﮒﺙ
        
        ﮒﮔﺍ:
            unified_order: ﻝﭨﻛﺕﻟ؟۱ﮒ
            
        ﻟﺟﮒ:
            QMTOrder: QMTﻟ؟۱ﮒ
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
        """ﮔ ﺙﮒﺙﮒﻟ۰ﻝ۴۷ﻛﭨ۲ﺅﺟ?
        
        ﮒﮔﺍ:
            symbol: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            
        ﻟﺟﮒ:
            ﮔ ﺙﮒﺙﮒﮒﻝﻟ۰ﻝ۴۷ﻛﭨ۲ﺅﺟ?
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
        """ﻟﺛ؛ﮔ۱ﻟ؟۱ﮒﻝﺎﭨﮒ
        
        ﮒﮔﺍ:
            order_type: ﻟ؟۱ﮒﻝﺎﭨﮒ
            direction: ﻟ؟۱ﮒﮔﺗﮒ
            
        ﻟﺟﮒ:
            QMTﻟ؟۱ﮒﻝﺎﭨﮒﻛﭨ۲ﻝ 
        """
        type_map = {
            (OrderType.MARKET, OrderDirection.BUY): 23,
            (OrderType.MARKET, OrderDirection.SELL): 24,
            (OrderType.LIMIT, OrderDirection.BUY): 23,
            (OrderType.LIMIT, OrderDirection.SELL): 24,
        }
        
        return type_map.get((order_type, direction), 23)


class OrderMonitor:
    """ﻟ؟۱ﮒﻝﮔ۶ﺅﺟ?""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        self._order_status: Dict[str, OrderStatus] = {}
        self._order_results: Dict[str, ExecutionResult] = {}
        self._monitor_thread = None
        self._running = False
        self.logger = logging.getLogger(__name__)
    
    def start(self) -> None:
        """ﮒﺁﮒ۷ﻟ؟۱ﮒﻝﮔ۶"""
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        self.logger.info("OrderMonitor started")
    
    def stop(self) -> None:
        """ﮒﮔ­۱ﻟ؟۱ﮒﻝﮔ۶"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        self.logger.info("OrderMonitor stopped")
    
    def register_order(self, order_id: str) -> None:
        """ﮔﺏ۷ﮒﻟ؟۱ﮒ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
        """
        self._order_status[order_id] = OrderStatus.PENDING
        self.logger.info(f"Registered order: {order_id}")
    
    def update_status(
        self,
        order_id: str,
        status: OrderStatus,
        result: Optional[ExecutionResult] = None
    ) -> None:
        """ﮔﺑﮔﺍﻟ؟۱ﮒﻝﭘﺅﺟﺛ?
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            status: ﻟ؟۱ﮒﻝﭘﺅﺟﺛ?
            result: ﮔ۶ﻟ۰ﻝﭨﮔ
        """
        self._order_status[order_id] = status
        
        if result:
            self._order_results[order_id] = result
        
        self.logger.info(f"Order {order_id} status updated to {status}")
    
    def get_status(self, order_id: str) -> OrderStatus:
        """ﻟﺓﮒﻟ؟۱ﮒﻝﭘﺅﺟﺛ?
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            
        ﻟﺟﮒ:
            ﻟ؟۱ﮒﻝﭘﺅﺟﺛ?
        """
        return self._order_status.get(order_id, OrderStatus.PENDING)
    
    def get_result(self, order_id: str) -> Optional[ExecutionResult]:
        """ﻟﺓﮒﮔ۶ﻟ۰ﻝﭨﮔ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            
        ﻟﺟﮒ:
            ﮔ۶ﻟ۰ﻝﭨﮔ
        """
        return self._order_results.get(order_id)
    
    def _monitor_loop(self) -> None:
        """ﻝﮔ۶ﮒﺝ۹ﻝﺁ"""
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
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﻝﭘﺅﺟ?
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
        """
        pass


class RiskChecker:
    """ﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۷"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def check_order(self, order: UnifiedOrder) -> bool:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﻠ۲ﺅﺟ?
        
        ﮒﮔﺍ:
            order: ﻝﭨﻛﺕﻟ؟۱ﮒ
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
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
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﮔﺍﺅﺟ?
        
        ﮒﮔﺍ:
            volume: ﻟ؟۱ﮒﮔﺍﻠ
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟﮔ۲ﺅﺟ?
        """
        max_volume = self.config.get('max_volume', 1000000)
        min_volume = self.config.get('min_volume', 100)
        
        return min_volume <= volume <= max_volume
    
    def _check_price(self, price: Optional[float]) -> bool:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﻛﭨﺓﺅﺟ?
        
        ﮒﮔﺍ:
            price: ﻟ؟۱ﮒﻛﭨﺓﮔ ﺙ
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟﮔ۲ﺅﺟ?
        """
        if price is None:
            return True
        
        max_price = self.config.get('max_price', 1000.0)
        min_price = self.config.get('min_price', 0.1)
        
        return min_price <= price <= max_price
    
    def _check_frequency(self, symbol: str) -> bool:
        """ﮔ۲ﮔ۴ﻛﭦ۳ﮔﻠ۱ﺅﺟ?
        
        ﮒﮔﺍ:
            symbol: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟﮔ۲ﺅﺟ?
        """
        return True


class ExceptionHandler:
    """ﮒﺙﮒﺕﺕﮒ۳ﻝﺅﺟ?""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def handle_execution_error(
        self,
        order: UnifiedOrder,
        error: Exception
    ) -> Optional[ExecutionResult]:
        """ﮒ۳ﻝﮔ۶ﻟ۰ﻠﻟﺁﺁ
        
        ﮒﮔﺍ:
            order: ﻝﭨﻛﺕﻟ؟۱ﮒ
            error: ﮒﺙﮒﺕﺕ
            
        ﻟﺟﮒ:
            ﮔ۶ﻟ۰ﻝﭨﮔ
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
    """ﻠﻟﺁﻝ؟۰ﻝﺅﺟ?""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        self._retry_count: Dict[str, int] = {}
        self.logger = logging.getLogger(__name__)
    
    def should_retry(self, order_id: str) -> bool:
        """ﮒ۳ﮔ­ﮔﺁﮒ۵ﮒﭦﻟﺁ۴ﻠﻟﺁ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﮒﭦﻟﺁ۴ﻠﻟﺁ
        """
        count = self._retry_count.get(order_id, 0)
        
        if count < self.config.max_retry:
            self._retry_count[order_id] = count + 1
            self.logger.info(f"Retry {count + 1}/{self.config.max_retry} for order {order_id}")
            return True
        
        self.logger.warning(f"Max retry reached for order {order_id}")
        return False
    
    def reset_retry(self, order_id: str) -> None:
        """ﻠﻝﺛ؟ﻠﻟﺁﻟ؟۰ﮔﺍ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
        """
        if order_id in self._retry_count:
            del self._retry_count[order_id]
    
    def wait_before_retry(self) -> None:
        """ﻠﻟﺁﮒﻝ­ﺅﺟ?""
        time.sleep(self.config.retry_interval)


class AccountManager:
    """ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﺅﺟ?""
    
    def __init__(self, trader):
        self.trader = trader
        self.logger = logging.getLogger(__name__)
    
    def get_account_info(self, account_id: str) -> Dict[str, Any]:
        """ﻟﺓﮒﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            
        ﻟﺟﮒ:
            ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
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
        """ﻟﺓﮒﮔﻛﭨﻛﺟ۰ﮔﺁ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            
        ﻟﺟﮒ:
            ﮔﻛﭨﮒﻟ۰۷
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
    """QMTﻛﭦ۳ﮔﮔ۶ﻟ۰ﺅﺟ?""
    
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
        """ﮔ۶ﻟ۰ﻟ؟۱ﮒ
        
        ﮒﮔﺍ:
            unified_order: ﻝﭨﻛﺕﻟ؟۱ﮒ
            
        ﻟﺟﮒ:
            ﮔ۶ﻟ۰ﻝﭨﮔ
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
        """ﮔ۳ﻠﻟ؟۱ﮒ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﮔﮒ
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
        """ﻝ­ﮒﺝﻟ؟۱ﮒﮒ؟ﮔ
        
        ﮒﮔﺍ:
            order_id: ﻟ؟۱ﮒID
            timeout: ﻟﭘﮔﭘﮔﭘﻠﺑ
            
        ﻟﺟﮒ:
            ﮔ۶ﻟ۰ﻝﭨﮔ
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
        """ﻟﺓﮒﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
        
        ﻟﺟﮒ:
            ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
        """
        return self.account_manager.get_account_info(self.config.account_id)
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """ﻟﺓﮒﮔﻛﭨﻛﺟ۰ﮔﺁ
        
        ﻟﺟﮒ:
            ﮔﻛﭨﮒﻟ۰۷
        """
        return self.account_manager.get_positions(self.config.account_id)
    
    def start(self) -> None:
        """ﮒﺁﮒ۷ﮔ۶ﻟ۰ﺅﺟ?""
        self.monitor.start()
        self.logger.info("QMTExecutor started")
    
    def stop(self) -> None:
        """ﮒﮔ­۱ﮔ۶ﻟ۰ﺅﺟ?""
        self.monitor.stop()
        self.logger.info("QMTExecutor stopped")
```

### 3.2 ﮔ۶ﻟﺛﮔﮔ ﻟ۵ﮔﺎ
| ﮔ۶ﻟﺛﮔﮔ  | ﻝ؟ﮔ ﺅﺟ?| ﮔﭖﻠﮔﺗﮔﺏ |
|----------|--------|----------|
| ﻟ؟۱ﮒﮔ۶ﻟ۰ﮔﭘﻠﺑ | < 500ms | ﮒﮔ؛۰ﮔ۶ﻟ۰ |
| ﻟ؟۱ﮒﻝﮔ۶ﮒﭨﭘﻟﺟ | < 1ﺅﺟ?| ﮒﮔ؛۰ﻝﮔ۶ |
| ﮒﺗﭘﮒﻟ؟۱ﮒﺅﺟ?| ﺅﺟ?10ﺅﺟ?| ﮒﺗﭘﮒﮔﭖﻟﺁ |
| ﻟ؟۱ﮒﮔﮒﺅﺟ?| ﺅﺟ?95% | ﻝﭨﻟ؟۰ﮒﮔ |

### 3.3 ﮒ؟ﮒ۷ﮔﭦﮒﭘ
- **ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?*: ﻛﭦ۳ﮔﮒﻟﺟﻟ۰ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
- **ﮒﺙﮒﺕﺕﮒ۳ﻝ**: ﮒ؟ﮒﻝﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘ
- **ﻟ؟۱ﮒﻝﮔ۶**: ﮒ؟ﮔﭘﻝﮔ۶ﻟ؟۱ﮒﻝﭘﺅﺟﺛ?

---

## 4. ﮔﺍﮔ؟ﮔ۷۰ﮒﻛﺕﮒ­ﺅﺟ?

### 4.1 ﮔ ﺕﮒﺟﮔﺍﮔ؟ﻝﭨﮔ

#### 4.1.1 ﻝﭨﻛﺕﻟ؟۱ﮒﮔ۷۰ﮒ
```python
@dataclass
class UnifiedOrderData:
    """ﻝﭨﻛﺕﻟ؟۱ﮒﮔﺍﮔ؟ﮔ۷۰ﮒ"""
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

#### 4.1.2 ﮔ۶ﻟ۰ﻝﭨﮔﮔ۷۰ﮒ
```python
@dataclass
class ExecutionResultData:
    """ﮔ۶ﻟ۰ﻝﭨﮔﮔﺍﮔ؟ﮔ۷۰ﮒ"""
    order_id: str
    status: OrderStatus
    filled_volume: int
    filled_amount: float
    avg_price: float
    commission: float
    timestamp: datetime
    error_message: Optional[str]
```

### 4.2 ﻝﺙﮒ­ﻝ­ﻝ۴
| ﻝﺙﮒ­ﻝﺎﭨﮒ | TTL | ﮔﺓﮔﺎﺍﻝ­ﻝ۴ | ﮔﮒ۳۶ﮒ؟ﺗﺅﺟ?|
|----------|-----|----------|----------|
| ﻟ؟۱ﮒﻝﭘﮔﻝﺙﺅﺟ?| 1ﺅﺟ?| LRU | 1000ﻛﺕ۹ﻟ؟۱ﺅﺟ?|
| ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁﻝﺙﮒ­ | 1ﮒﻠ | LRU | 1ﻛﺕ۹ﻟﺑ۵ﺅﺟ?|
| ﮔﻛﭨﻛﺟ۰ﮔﺁﻝﺙﮒ­ | 1ﮒﻠ | LRU | 100ﮒ۹ﻟ۰ﺅﺟ?|

### 4.3 ﮔﺍﮔ؟ﮔﻛﺗﺅﺟ?
- **ﮔﻛﺗﮒﻠﺅﺟ?*: ﻟ؟۱ﮒﮒﮒﺎﻙﮔ۶ﻟ۰ﻝﭨﮔﻠﻟ۵ﮔﻛﺗﮒﮒ­ﮒ۷
- **ﮒ­ﮒ۷ﮔ ﺙﮒﺙ**: SQLiteﮔﺍﮔ؟ﺅﺟ?

---

## 5. ﻝ؟ﮔﺏﮒ؟ﻝﺍﻟﺁﺑﮔ

### 5.1 ﮔ ﺕﮒﺟﻝ؟ﮔﺏ

#### 5.1.1 ﻟ؟۱ﮒﮔ۶ﻟ۰ﻝ؟ﮔﺏ
```python
def execute_order(self, unified_order: UnifiedOrder) -> ExecutionResult:
    """
    ﻟ؟۱ﮒﮔ۶ﻟ۰ﻝ؟ﮔﺏ
    
    ﻝ؟ﮔﺏﮒﻝ:
    1. ﻟﺟﻟ۰ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?
    2. ﮔﺏ۷ﮒﻟ؟۱ﮒﮒﺍﻝﮔ۶ﮒ۷
    3. ﻟﺛ؛ﮔ۱ﻟ؟۱ﮒﮔ ﺙﮒﺙ
    4. ﮒﻠﻟ؟۱ﮒﮒﺍQMT
    5. ﻝ­ﮒﺝﻟ؟۱ﮒﮒ؟ﮔ
    6. ﻟﺟﮒﮔ۶ﻟ۰ﻝﭨﮔ
    
    ﮒ۳ﮔﺅﺟ? O(1)
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

#### 5.1.2 ﻠﻟﺁﻝ؟ﮔﺏ
```python
def should_retry(self, order_id: str) -> bool:
    """
    ﻠﻟﺁﮒ۳ﮔ­ﻝ؟ﮔﺏ
    
    ﻝ؟ﮔﺏﮒﻝ:
    1. ﻟﺓﮒﮒﺛﮒﻠﻟﺁﮔ؛۰ﮔﺍ
    2. ﮒ۳ﮔ­ﮔﺁﮒ۵ﻟﭘﻟﺟﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﺅﺟ?
    3. ﮔﺑﮔﺍﻠﻟﺁﻟ؟۰ﮔﺍ
    
    ﮒ۳ﮔﺅﺟ? O(1)
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

## 6. ﮒ؟ﮔﺛﮔﮔﺁﮔ 

### 6.1 ﻟﺁ­ﻟ۷ﻛﺕﮔ۰ﺅﺟ?
| ﮔﮔﺁﻠﮒ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﻝ۷ﺅﺟﺛ?| ﻠﮔ۸ﻝﻝﺎ |
|----------|----------|------|----------|
| Python | >=3.8 | ﻛﺕﭨﻟ۵ﮒﺙﮒﻟﺁ­ﻟ۷ | ﻠﮒﻝﺏﭨﻝﭨﮔ ﮒﻟﺁ­ﻟ۷ |
| xtquant | >=1.0.0 | QMT Python API | QMTﮒ؟ﮔﺗAPI |
| threading | ﮔ ﮒﺅﺟ?| ﮒ۳ﻝﭦﺟﻝ۷ﮔﺁﺅﺟ?| Pythonﮒﻝﺛ؟ﺅﺙﻝ۷ﺏﮒ؟ﮒﺁﺅﺟ?|

### 6.2 ﻝ؛؛ﻛﺕﮔﺗﻛﺝﺅﺟ?
```yaml
requirements:
  - xtquant>=1.0.0
```

---

## 7. ﮔﭖﻟﺁﻝ­ﻝ۴

### 7.1 ﮒﮒﮔﭖﻟﺁ
| ﮔﭖﻟﺁﺅﺟ?| ﮔﭖﻟﺁﮒﮒ؟ﺗ | ﻟ۵ﻝﻝﻝ؟ﺅﺟ?|
|--------|----------|------------|
| ﻟ؟۱ﮒﻟﺛ؛ﮔ۱ | ﻟﺛ؛ﮔ۱ﮔ­۲ﻝ۰؟ﺅﺟ?| 100% |
| ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?| ﮔ۲ﮔ۴ﮔ­۲ﻝ۰؟ﺅﺟﺛ?| 100% |
| ﻟ؟۱ﮒﮔ۶ﻟ۰ | ﮔ۶ﻟ۰ﮔ­۲ﻝ۰؟ﺅﺟ?| 100% |
| ﮒﺙﮒﺕﺕﮒ۳ﻝ | ﮒ۳ﻝﮔ­۲ﻝ۰؟ﺅﺟ?| 100% |

### 7.2 ﻠﮔﮔﭖﻟﺁ
```python
def test_qmt_executor_integration():
    """ﻠﮔﮔﭖﻟﺁﻝ۳ﭦﻛﺝ"""
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

## 8. ﻠ۲ﻠ۸ﻛﺕﻝﭦ۵ﺅﺟ?

### 8.1 ﮔﮔﺁﻠ۲ﺅﺟ?
| ﻠ۲ﻠ۸ID | ﻠ۲ﻠ۸ﮔﻟﺟﺍ | ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |
|--------|----------|----------|----------|
| R001 | QMT APIﻛﺕﻝ۷ﺏﺅﺟ?| P0 | ﮒ؟ﻝﺍﮒﺙﮒﺕﺕﮒ۳ﻝﮒﻠﻟﺁﮔﭦﺅﺟ?|
| R002 | ﻟ؟۱ﮒﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ | P1 | ﮒ؟ﻝﺍﻟ؟۱ﮒﻝﮔ۶ﮒﮒﺅﺟ?|
| R003 | ﻝﺛﻝﭨﻟﺟﮔ۴ﻛﺕ­ﮔ­ | P1 | ﮒ؟ﻝﺍﻟﺟﮔ۴ﻠﻟﺟﮔﭦﮒﭘ |
| R004 | ﻛﭦ۳ﮔﮔﻠﻛﺕﻟﭘﺏ | P2 | ﮒ؟ﻝﺍﮔﻠﮔ۲ﮔ۴ﮔﭦﺅﺟ?|

### 8.2 ﻝﭦ۵ﮔﮔ۰ﻛﭨﭘ
- **ﮔﮔﺁﻝﭦ۵ﺅﺟ?*: ﻛﺝﻟﭖQMTﮒ؟۱ﮔﺓﻝ،ﺁﮒAPI
- **ﻟﭖﮔﭦﻝﭦ۵ﮔ**: ﮒﮒ­ﻛﺛﺟﻝ۷<500MBﺅﺙCPUﻛﺛﺟﻝ۷<20%
- **ﮔﭘﻠﺑﻝﭦ۵ﮔ**: ﻠ۱ﻟ؟۰ﮒﺙﮒﮔﭘﺅﺟ?0ﮒﺍﮔﭘ
- **ﻟﺑ۷ﻠﻝﭦ۵ﮔ**: ﮔﭖﻟﺁﻟ۵ﻝﻝﻗ۴90%

---

## 9. ﻠ۹ﮔﭘﮔ ﮒ

### 9.1 ﮒﻟﺛﻠ۹ﮔﭘﮔ ﮒ
| ﮒﻟﺛﺅﺟ?| ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|--------|----------|----------|
| ﻟ؟۱ﮒﮔ۶ﻟ۰ | ﮔ۶ﻟ۰ﮔ­۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| ﻟ؟۱ﮒﻝﮔ۶ | ﻝﮔ۶ﮔ­۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| ﮒﺙﮒﺕﺕﮒ۳ﻝ | ﮒ۳ﻝﮔ­۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| ﻠ۲ﻠ۸ﮔ۲ﺅﺟ?| ﮔ۲ﮔ۴ﮔ­۲ﺅﺟ?| ﮒﮒﮔﭖﻟﺁ |

### 9.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘﮔ ﮒ
| ﮔ۶ﻟﺛﮔﮔ  | ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|----------|----------|----------|
| ﻟ؟۱ﮒﮔ۶ﻟ۰ﮔﭘﻠﺑ | < 500ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| ﻟ؟۱ﮒﻝﮔ۶ﮒﭨﭘﻟﺟ | < 1ﺅﺟ?| ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| ﻟ؟۱ﮒﮔﮒﺅﺟ?| ﺅﺟ?95% | ﻝﭨﻟ؟۰ﮒﮔ |

### 9.3 ﻟﺑ۷ﻠﻠ۹ﮔﭘﮔ ﮒ
| ﻟﺑ۷ﻠﮔﮔ  | ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|----------|----------|----------|
| ﮔﭖﻟﺁﻟ۵ﻝﺅﺟ?| ﺅﺟ?90% | pytest-cov |
| ﻛﭨ۲ﻝ ﻟﺑ۷ﻠ | ﮔ ﻛﺕ۴ﻠﻠ؟ﺅﺟ?| pylint |

---

## 10. ﮒ؟ﮔﺛﻟﺓﺁﻝﭦﺟﺅﺟ?

### 10.1 Phase 1: ﮔ ﺕﮒﺟﮒﻟﺛﮒﺙﺅﺟ?(3ﺅﺟ?
- **Day 1**: ﻟ؟۱ﮒﻟﺛ؛ﮔ۱ﮒ۷ﻙﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۷
- **Day 2**: ﻟ؟۱ﮒﻝﮔ۶ﮒ۷ﻙﮒﺙﮒﺕﺕﮒ۳ﻝﮒ۷
- **Day 3**: ﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﻙﻠﮔﮔﭖﺅﺟ?

---

## ﻠﮒﺛ

### A. ﻠﻝﺛ؟ﻝ۳ﭦﻛﺝ
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

### B. ﻠﻟﺁﺁﻝ ﮒ؟ﺅﺟ?
| ﻠﻟﺁﺁﺅﺟ?| ﻠﻟﺁﺁﻝﺎﭨﮒ | ﻠﻟﺁﺁﮔﻟﺟﺍ | ﮒ۳ﻝﮔﺗﮒﺙ |
|--------|----------|----------|----------|
| ERR_EXEC_001 | ExecuteError | ﻟ؟۱ﮒﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﺅﺟ?|
| ERR_EXEC_002 | CancelError | ﻟ؟۱ﮒﮔ۳ﻠﮒ۳ﺎﻟﺑ۴ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﺅﺟ?|
| ERR_EXEC_003 | RiskCheckError | ﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۳ﺎﺅﺟ?| ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﺅﺟ?|
| ERR_EXEC_004 | TimeoutError | ﻟ؟۱ﮒﻟﭘﮔﭘ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﺅﺟ?|

### C. ﮒﻟﮔﺅﺟ?
- [ﮔﭘﮔﮒ؟ﻛﺗ](../../01_FRAMEWORK/ARCHITECTURE.md)
- [ﮔ۷۰ﮒﻟﻟﺑ۲ﻟﺝﺗﻝ](../../01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md)
- [QMTﮔﺍﮔ؟ﮔ۴ﮒ۲ﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵](./QMT_DATA_INTERFACE_TECHNICAL_SPECIFICATION.md)


**ﮔﮔ۰۲ﻝﮔ؛**: v1.2.0 | **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02 | **ﻝﭨﺑﮔ۳ﻟ?*: ﻝ­ﻝ۴ﮔ۶ﻟ۰ﮒﺎﻟﺑﻟﺑ۲ﻛﭦﭦ

---

## 11. ﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﮔ۴ﻠﮔﮔﺗﺅﺟ?ﻭ

### 11.1 ﻠﮔﻟﮔﺁ

**ﻝﻝ؟۰ﻟ۵ﮔﺎ**ﺅﺟ?- **2026ﺅﺟ?ﺅﺟ?ﺅﺟ?*ﺅﺙﻟﺁﻝﻛﺙﻙﮒﺏﻛﭦﻝ­ﻝﭦﺟﻛﭦ۳ﮔﻝﻝ؟۰ﻝﻟ۴ﮒﺗﺎﻟ۶ﮒ؟ﻙﮔ­۲ﮒﺙﮔﺛﺅﺟ?- **2025ﺅﺟ?ﺅﺟ?ﺅﺟ?*ﺅﺙﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﻙﮔ­۲ﮒﺙﮔﺛﺅﺟ?- **ﻝﻝ؟۰ﮒﺁﺙﮒ**ﺅﺙﻠﻠﻙﻝ۸ﺟﻠﻙﮒﺗﺏﮔﺅﺙAﻟ۰ﻛﭦ۳ﮔﻝﮔﻟﺟﮔ۴ﮔ ﺗﮔ؛ﮔ۶ﻠﺅﺟ?
**ﻠﮔﻝ؟ﮔ **ﺅﺟ?- ﺅﺟ?ﻝ۰؟ﻛﺟﮔﮔﻛﭦ۳ﮔﻟ۰ﻛﺕﭦﻝ؛۵ﮒﮔﮔﺍﻝﻝ؟۰ﻟ۵ﺅﺟ?- ﺅﺟ?ﮒ؟ﮔﭘﻠ۱ﻟ­۵ﮒﻟ۶ﻠ۲ﻠ۸ﺅﺙﻠﺟﮒﻟﺟﻟ۶ﮒ۳ﺅﺟ?- ﺅﺟ?ﻠﻛﺛﮒﻟ۶ﮔﮔ؛ﺅﺙﻟ۹ﮒ۷ﮒﮒﻟ۶ﮔ۲ﮔ۴ﮔﭖﺅﺟ?- ﺅﺟ?ﮔﮒﻝﺏﭨﻝﭨﻛﺕﻛﺕﮔ۶ﺅﺙﻝ؛۵ﮒﮔﭦﮔﻝﭦ۶ﮔ ﺅﺟ?
### 11.2 ﮒﻟ۶ﮔ۷۰ﮒﻠﮔ

#### 11.2.1 ﮔ۷۰ﮒﻛﺝﻟﭖ

**ﻛﺝﻟﭖﮔ۷۰ﮒ**: `COMPLIANCE_CHECKER_001` (v1.0.0)

**ﮔ۷۰ﮒﻛﺛﻝﺛ؟**: `src/modules/compliance_checker.py`

**ﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵**: [COMPLIANCE_CHECKER_TECHNICAL_SPECIFICATION.md](./COMPLIANCE_CHECKER_TECHNICAL_SPECIFICATION.md)

#### 11.2.2 ﮔ ﺕﮒﺟﮒﻟﺛ

| ﮒﻟﺛﮔ۷۰ﮒ | ﮒﻟﺛﻟﺁﺑﮔ | ﻝﻝ؟۰ﻛﺝﮔ؟ |
|---------|---------|---------|
| **ﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔ۲ﺅﺟ?* | ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟ۶۵ﮒﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔ ﮒﺅﺙﮔﺁﻝ۶ﺅﺟ?00ﻝ؛ﮔﮒﮔ۴ﺅﺟ?0000ﻝ؛ﺅﺙ | ﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﻙﻝ؛؛ﻛﺕﮒﻛﺕﮔ۰ |
| **ﮔ۳ﮒﻠﮒﭘﮔ۲ﺅﺟ?* | ﮔ۲ﮔ۴ﮔ۳ﮒﻠ۱ﻝﮒﮔ۳ﮒﻝﮔﺁﮒ۵ﻝ؛۵ﮒﻠﮒﭘﺅﺙﮔﺁﻝ۶ﺅﺟ?5ﻝ؛ﺅﺙﮔ۳ﮒﻝﻗ۳15%ﺅﺟ?| ﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﺅﺟ?|
| **ﻟ؟۱ﮒﮒﻝﮔﭘﻠﺑﮔ۲ﺅﺟ?* | ﮔ۲ﮔ۴ﻟ؟۱ﮒﮔﺁﮒ۵ﮔﭨ۰ﻟﭘﺏﮔﮒﺍﮒﻝﮔﭘﻠﺑﻟ۵ﮔﺎﺅﺙﺅﺟ?0ﮒﺝ؟ﻝ۶ﺅﺟ?| ﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﺅﺟ?|
| **ﻝ­ﻝﭦﺟﻛﭦ۳ﮔﮒﻟ۶ﮔ۲ﺅﺟ?* | ﮔ۲ﮔ۴ﮒ۳۶ﻟ۰ﻛﺕﻝ­ﻝﭦﺟﻛﭦ۳ﮔﻠﻛﭨﮔﺅﺙ6ﻛﺕ۹ﮔﺅﺟ?| ﻟﺁﻝﻛﺙﻙﮒﺏﻛﭦﻝ­ﻝﭦﺟﻛﭦ۳ﮔﻝﻝ؟۰ﻝﻟ۴ﮒﺗﺎﻟ۶ﮒ؟ﺅﺟ?|
| **ﮒﺙﮒﺕﺕﻛﭦ۳ﮔﻟ۰ﻛﺕﭦﻝﮔ۶** | ﻝﮔ۶ﮒﻝﺎﭨﮒﺙﮒﺕﺕﻛﭦ۳ﮔﻟ۰ﻛﺕﭦ | ﮔﺎ۹ﮔﺓﺎﮒﻛﭦ۳ﮔﮔﻙﻝ۷ﮒﭦﮒﻛﭦ۳ﮔﻝ؟۰ﻝﮒ؟ﮔﺛﻝﭨﮒﺅﺟ?|

### 11.3 ﻠﮔﮒ؟ﻝﺍﮔﺗﮔ۰

#### 11.3.1 ﮒﮒ۶ﮒﻠﺅﺟ?
```python
from src.modules.compliance_checker import (
    create_compliance_checker,
    OrderRecord,
    ComplianceLevel
)

class QMTExecutor:
    """QMTﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒ۷ﺅﺙﻠﮔﮒﻟ۶ﮔ۲ﮔ۴ﺅﺙ"""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        
        # ﮒﮒ۶ﮒQMTﻛﭦ۳ﮔﮔ۴ﮒ۲
        from xtquant.xttrader import XtQuantTrader
        self.trader = XtQuantTrader(
            config.account_id,
            config.session_id,
            config.client_path
        )
        self.trader.start()
        self.trader.subscribe_account(config.account_id)
        
        # ﮒﮒ۶ﮒﮔ ﺕﮒﺟﻝﭨﺅﺟ?        self.converter = OrderConverter()
        self.monitor = OrderMonitor(config)
        self.risk_checker = RiskChecker({})
        self.exception_handler = ExceptionHandler(config)
        self.retry_manager = RetryManager(config)
        self.account_manager = AccountManager(self.trader)
        
        # ﻭ ﮒﮒ۶ﮒﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷
        self.compliance_checker = create_compliance_checker()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("QMTExecutor initialized with compliance checker")
```

#### 11.3.2 ﻟ؟۱ﮒﮔﻛﭦ۳ﮒﮒﻟ۶ﮔ۲ﺅﺟ?
```python
def execute_order(self, unified_order: UnifiedOrder) -> ExecutionResult:
    """ﮔ۶ﻟ۰ﻟ؟۱ﮒﺅﺙﻠﮔﮒﻟ۶ﮔ۲ﮔ۴ﺅﺙ
    
    ﮔ۶ﻟ۰ﮔﭖﻝ۷:
    1. ﻛﺙ ﻝﭨﻠ۲ﻠ۸ﮔ۲ﺅﺟ?    2. ﻭ ﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﺅﺟ?    3. ﻟ؟۱ﮒﻟﺛ؛ﮔ۱
    4. ﻟ؟۱ﮒﮔﻛﭦ۳
    5. ﻟ؟۱ﮒﻝﮔ۶
    
    ﮒﮔﺍ:
        unified_order: ﻝﭨﻛﺕﻟ؟۱ﮒ
        
    ﻟﺟﮒ:
        ﮔ۶ﻟ۰ﻝﭨﮔ
    """
    # 1. ﻛﺙ ﻝﭨﻠ۲ﻠ۸ﮔ۲ﺅﺟ?    if not self.risk_checker.check_order(unified_order):
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
    
    # 2. ﻭ ﻝﻝ؟۰ﮒﻟ۶ﮔ۲ﺅﺟ?    compliance_result = self._check_compliance(unified_order)
    
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
    
    # ﻟ؟ﺍﮒﺛﮒﻟ۶ﻟ­۵ﮒ
    if compliance_result.warnings:
        self.logger.warning(
            f"Order {unified_order.order_id} compliance warnings: "
            f"{compliance_result.warnings}"
        )
    
    # 3. ﻟ؟۱ﮒﻟﺛ؛ﮔ۱
    qmt_order = self.converter.to_qmt_order(unified_order)
    
    # 4. ﻟ؟۱ﮒﮔﻛﭦ۳
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
        
        # 5. ﮔﺏ۷ﮒﻟ؟۱ﮒﻝﮔ۶
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
    """ﮔ۶ﻟ۰ﮒﻟ۶ﮔ۲ﺅﺟ?    
    ﮒﮔﺍ:
        unified_order: ﻝﭨﻛﺕﻟ؟۱ﮒ
        
    ﻟﺟﮒ:
        ﮒﻟ۶ﮔ۲ﮔ۴ﻝﭨﺅﺟ?    """
    # ﮒﮒﭨﭦﮒﻟ۶ﮔ۲ﮔ۴ﻟ؟۱ﮒﻟ؟ﺍﺅﺟ?    compliance_order = OrderRecord(
        order_id=unified_order.order_id,
        symbol=unified_order.symbol,
        direction='buy' if unified_order.direction == OrderDirection.BUY else 'sell',
        quantity=unified_order.volume,
        price=unified_order.price or 0.0,
        order_type=unified_order.order_type.value,
        timestamp=unified_order.timestamp,
        status='submitted'
    )
    
    # ﻟﺓﮒﮔﻛﭨﻛﺟ۰ﮔﺁﺅﺙﻝ۷ﻛﭦﻝ­ﻝﭦﺟﻛﭦ۳ﮔﮔ۲ﮔ۴ﺅﺙ
    position_pct = self._get_position_pct(unified_order.symbol)
    last_trade_date = self._get_last_trade_date(unified_order.symbol)
    
    # ﮔ۶ﻟ۰ﮒﻟ۶ﮔ۲ﺅﺟ?    result = self.compliance_checker.check_order_before_submission(
        order=compliance_order,
        position_pct=position_pct,
        last_trade_date=last_trade_date
    )
    
    return result


def _get_position_pct(self, symbol: str) -> float:
    """ﻟﺓﮒﮔﻛﭨﮔﺁﻛﺝ
    
    ﮒﮔﺍ:
        symbol: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
        
    ﻟﺟﮒ:
        ﮔﻛﭨﮔﺁﻛﺝ
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
    """ﻟﺓﮒﻛﺕﮔ؛۰ﻛﭦ۳ﮔﮔ۴ﮔ
    
    ﮒﮔﺍ:
        symbol: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
        
    ﻟﺟﮒ:
        ﻛﺕﮔ؛۰ﻛﭦ۳ﮔﮔ۴ﮔ
    """
    # TODO: ﻛﭨﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﺕ­ﻟﺓﮒﻛﺕﮔ؛۰ﻛﭦ۳ﮔﮔ۴ﮔ
    # ﻟﺟﻠﻠﻟ۵ﻛﭨﮔﺍﮔ؟ﮒﭦﮔﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﺕ­ﮔ۴ﺅﺟ?    return None
```

#### 11.3.3 ﮔ۳ﮒﮒﻟ۶ﮔ۲ﺅﺟ?
```python
def cancel_order(self, order_id: str) -> bool:
    """ﮔ۳ﮒﺅﺙﻠﮔﮒﻟ۶ﮔ۲ﮔ۴ﺅﺙ
    
    ﮒﮔﺍ:
        order_id: ﻟ؟۱ﮒID
        
    ﻟﺟﮒ:
        ﮔﺁﮒ۵ﮔﮒ
    """
    # ﻟﺓﮒﻟ؟۱ﮒﻛﺟ۰ﮔﺁ
    order_status = self.monitor.get_status(order_id)
    
    if order_status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
        self.logger.warning(f"Cannot cancel order {order_id}: status is {order_status}")
        return False
    
    # ﻭ ﮔ۲ﮔ۴ﮔ۳ﮒﻠﺅﺟ?    cancel_check = self.compliance_checker.check_cancel_limits()
    
    if not cancel_check.is_compliant:
        self.logger.error(
            f"Cannot cancel order {order_id}: cancel limit exceeded - "
            f"{cancel_check.violations}"
        )
        return False
    
    # ﻟ؟ﺍﮒﺛﮔ۳ﮒﻟ­۵ﮒ
    if cancel_check.warnings:
        self.logger.warning(f"Cancel warnings: {cancel_check.warnings}")
    
    # ﮔ۶ﻟ۰ﮔ۳ﮒ
    try:
        self.trader.cancel_order(self.config.account_id, order_id)
        
        # ﻭ ﻟ؟ﺍﮒﺛﮔ۳ﮒﮔﭘﻠﺑﺅﺙﻝ۷ﻛﭦﻟ؟۱ﮒﮒﻝﮔﭘﻠﺑﮔ۲ﮔ۴ﺅﺙ
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

### 11.4 ﮒ؟ﮔﭘﻝﮔ۶ﻛﭨﭨﮒ۰

#### 11.4.1 ﮒ؟ﮔﭘﮒﻟ۶ﻝﮔ۶

```python
def start_compliance_monitoring(self):
    """ﮒﺁﮒ۷ﮒﻟ۶ﻝﮔ۶"""
    import threading
    import time
    
    def monitoring_loop():
        while True:
            try:
                # ﮔ۲ﮔ۴ﮒﺙﮒﺕﺕﻛﭦ۳ﮔﻟ۰ﺅﺟ?                result = self.compliance_checker.check_abnormal_trading()
                
                if result.compliance_level == ComplianceLevel.WARNING:
                    self.logger.warning(
                        f"Compliance warning: {result.warnings}"
                    )
                    # TODO: ﮒﻠﮒﻟ­۵ﻠﻝ۴
                
                elif result.compliance_level == ComplianceLevel.VIOLATION:
                    self.logger.error(
                        f"Compliance violation: {result.violations}"
                    )
                    # TODO: ﻟ۶۵ﮒﻠ۲ﮔ۶ﮔ۹ﮔﺛ
                
                # ﮔﺁﮒﻠﮔ۲ﮔ۴ﻛﺕﺅﺟ?                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in compliance monitoring: {e}")
                time.sleep(60)
    
    monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitor_thread.start()
    self.logger.info("Compliance monitoring started")
```

#### 11.4.2 ﮔﺁﮔ۴ﻠﻝﺛ؟ﻛﭨﭨﮒ۰

```python
def daily_reset(self):
    """ﮔﺁﮔ۴ﻠﻝﺛ؟ﺅﺙﮒﺙﻝﮒﻟﺍﻝ۷ﺅﺟ?""
    # ﻠﻝﺛ؟ﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷
    self.compliance_checker.reset_daily()
    self.logger.info("Compliance checker reset for new trading day")
```

### 11.5 ﮒﻟ۶ﮔ۴ﮒﻝﮔ

```python
def generate_compliance_report(self) -> Dict:
    """ﻝﮔﮒﻟ۶ﮔ۴ﮒ
    
    ﻟﺟﮒ:
        ﮒﻟ۶ﮔ۴ﮒﮒ­ﮒﺕ
    """
    report = self.compliance_checker.generate_compliance_report()
    
    self.logger.info(
        f"Compliance report generated: "
        f"compliance_rate={report['compliance_summary']['compliance_rate']:.2%}"
    )
    
    return report
```

### 11.6 ﻠﻝﺛ؟ﻝ؟۰ﻝ

#### 11.6.1 ﮒﻟ۶ﻠﻝﺛ؟ﮔﻛﭨﭘ

**ﻠﻝﺛ؟ﮔﻛﭨﭘﻛﺛﻝﺛ؟**: `config/compliance_config.yaml`

```yaml
compliance:
  # ﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔ ﮒ
  high_frequency_criteria:
    per_second_threshold: 300      # ﮔﺁﻝ۶ﻝﺏﮔ۴+ﮔ۳ﮒﺅﺟ?00ﺅﺟ?    per_day_threshold: 20000       # ﮒﮔ۴ﻝﺏﮔ۴+ﮔ۳ﮒﺅﺟ?0000ﺅﺟ?    stricter_standard:
      per_second: 15                # ﮔﺑﻛﺕ۴ﮔ ﺙﮔ ﮒﺅﺙﮔﺁﻝ۶15ﺅﺟ?      cancel_rate_per_day: 0.15     # ﮒﮔ۴ﮔ۳ﮒﻝﻗ۳15%
  
  # ﮔ۳ﮒﻠﮒﭘ
  cancel_order_limits:
    max_cancel_per_second: 15       # ﮔﺁﻝ۶ﮔ۳ﮒﺅﺟ?5ﺅﺟ?    max_cancel_rate_per_day: 0.15   # ﮒﮔ۴ﮔ۳ﮒﻝﻗ۳15%
    min_order_duration_microseconds: 50  # ﻟ؟۱ﮒﮒﻝﺅﺟ?0ﮒﺝ؟ﻝ۶
  
  # ﻝ­ﻝﭦﺟﻛﭦ۳ﮔﻟ۶ﮒ
  short_term_trading_rules:
    lock_period_months: 6              # 6ﻛﺕ۹ﮔﻠﻛﭨﺅﺟ?    major_shareholder_threshold: 0.05  # 5%ﮒ۳۶ﻟ۰ﻛﺕﻟ؟۳ﺅﺟ?    penetration_enabled: true          # ﻝ۸ﺟﻠﻝﻝ؟۰ﮒﺁﺅﺟ?  
  # ﻝﮔ۶ﻠﻝﺛ؟
  monitoring:
    enabled: true                      # ﮒﺁﻝ۷ﻝﮔ۶
    check_interval_seconds: 60         # ﮔ۲ﮔ۴ﻠﺑﻠﺅﺙﻝ۶ﺅﺙ
    alert_enabled: true                # ﮒﺁﻝ۷ﮒﻟ­۵
```

#### 11.6.2 ﮒ ﻟﺛﺛﻠﻝﺛ؟

```python
import yaml

def load_compliance_config(self, config_path: str = 'config/compliance_config.yaml'):
    """ﮒ ﻟﺛﺛﮒﻟ۶ﻠﻝﺛ؟
    
    ﮒﮔﺍ:
        config_path: ﻠﻝﺛ؟ﮔﻛﭨﭘﻟﺓﺁﮒﺝ
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # ﻠﮔﺍﮒﮒﭨﭦﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷ﺅﺙﮒﭦﻝ۷ﮔﺍﻠﻝﺛ؟ﺅﺟ?        self.compliance_checker = create_compliance_checker(
            config.get('compliance', {})
        )
        
        self.logger.info(f"Compliance config loaded from {config_path}")
        
    except Exception as e:
        self.logger.error(f"Failed to load compliance config: {e}")
        # ﻛﺛﺟﻝ۷ﻠﭨﻟ؟۳ﻠﻝﺛ؟
        self.compliance_checker = create_compliance_checker()
```

### 11.7 ﮔﭖﻟﺁﻠ۹ﻟﺁ

#### 11.7.1 ﮒﮒﮔﭖﻟﺁ

```python
import unittest
from datetime import datetime, timedelta

class TestQMTExecutorCompliance(unittest.TestCase):
    """QMTExecutorﮒﻟ۶ﮔ۲ﮔ۴ﮔﭖﺅﺟ?""
    
    def setUp(self):
        """ﮔﭖﻟﺁﮒﮒ۶ﺅﺟ?""
        self.config = QMTConfig(
            account_id='test_account',
            session_id='test_session',
            client_path='/path/to/qmt'
        )
        self.executor = QMTExecutor(self.config)
    
    def test_compliance_check_pass(self):
        """ﮔﭖﻟﺁﮒﻟ۶ﮔ۲ﮔ۴ﻠﻟﺟ"""
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
        """ﮔﭖﻟﺁﻠ،ﻠ۱ﻛﭦ۳ﮔﮔ۲ﺅﺟ?""
        # ﮔ۷۰ﮔﻠ،ﻠ۱ﻛﭦ۳ﮔﮒﭦﮔﺁ
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
        
        # ﮔ۲ﮔ۴ﻠ،ﻠ۱ﻛﭦ۳ﮔﮔ۲ﺅﺟ?        result = self.executor.compliance_checker.check_high_frequency_trading()
        self.assertEqual(result.compliance_level, ComplianceLevel.WARNING)
    
    def test_cancel_limit_check(self):
        """ﮔﭖﻟﺁﮔ۳ﮒﻠﮒﭘﮔ۲ﺅﺟ?""
        # ﮔ۷۰ﮔﮔ۳ﮒﮒﭦﮔﺁ
        for i in range(20):
            self.executor.compliance_checker.order_tracker.record_cancel(
                f'ORDER_{i:03d}',
                datetime.now()
            )
        
        # ﮔ۲ﮔ۴ﮔ۳ﮒﻠﺅﺟ?        result = self.executor.compliance_checker.check_cancel_limits()
        self.assertFalse(result.is_compliant)


if __name__ == '__main__':
    unittest.main()
```

### 11.8 ﻝﮔ۶ﻛﺕﮒﺅﺟ?
#### 11.8.1 ﻝﮔ۶ﮔﮔ 

| ﻝﮔ۶ﮔﮔ  | ﻟﺁﺑﮔ | ﮒﻟ­۵ﻠﺅﺟﺛ?|
|---------|------|---------|
| **ﮒﻟ۶ﮔ۲ﮔ۴ﮔ؛۰ﺅﺟ?* | ﮔﺁﮔ۴ﮒﻟ۶ﮔ۲ﮔ۴ﮔﭨﮔ؛۰ﺅﺟ?| - |
| **ﻟﺟﻟ۶ﮔ؛۰ﮔﺍ** | ﮔﺁﮔ۴ﻟﺟﻟ۶ﮔ؛۰ﮔﺍ | > 0 ﻝ،ﮒﺏﮒﻟ­۵ |
| **ﻟ­۵ﮒﮔ؛۰ﮔﺍ** | ﮔﺁﮔ۴ﻟ­۵ﮒﮔ؛۰ﮔﺍ | > 10 ﮒﭨﭘﻟﺟﮒﻟ­۵ |
| **ﮒﻟ۶ﺅﺟ?* | ﮒﻟ۶ﮔ۲ﮔ۴ﻠﻟﺟﺅﺟ?| < 95% ﮔﺁﮔ۴ﮒﻟ­۵ |
| **ﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ۶۵ﮒﮔ؛۰ﮔﺍ** | ﻟ۶۵ﮒﻠ،ﻠ۱ﻛﭦ۳ﮔﻟ؟۳ﮒ؟ﮔ؛۰ﮔﺍ | > 0 ﻝ،ﮒﺏﮒﻟ­۵ |
| **ﮔ۳ﮒﺅﺟ?* | ﮔﺁﮔ۴ﮔ۳ﮒﺅﺟ?| > 10% ﻟ­۵ﮒﮒﻟ­۵ |

#### 11.8.2 ﮒﻟ­۵ﻠﻝ۴

```python
def send_compliance_alert(self, level: str, message: str):
    """ﮒﻠﮒﻟ۶ﮒﺅﺟ?    
    ﮒﮔﺍ:
        level: ﮒﻟ­۵ﻝﭦ۶ﮒ،
        message: ﮒﻟ­۵ﮔﭘﮔﺁ
    """
    # TODO: ﻠﮔﮒﻟ­۵ﻝﺏﭨﻝﭨ
    self.logger.warning(f"[COMPLIANCE ALERT] [{level}] {message}")
    
    # ﻝ۳ﭦﻛﺝﺅﺙﮒﻠﻠ؟ﻛﭨﭘﻠﻝ۴
    # send_email(
    #     subject=f"[ﮒﻟ۶ﮒﻟ­۵] {level}",
    #     body=message
    # )
    
    # ﻝ۳ﭦﻛﺝﺅﺙﮒﻠﮒﺝ؟ﻛﺟ۰ﻠﻝ۴
    # send_wechat_message(message)
```

### 11.9 ﮔﻛﺛﺏﮒ؟ﺅﺟ?
#### 11.9.1 ﮒﺙﮒﮒﭨﭦﺅﺟ?
1. **ﮒ۶ﻝﭨﻟﺟﻟ۰ﮒﻟ۶ﮔ۲ﺅﺟ?*: ﮒ۷ﻟ؟۱ﮒﮔﻛﭦ۳ﮒﮒﺟﻠ۰ﭨﻟﺟﻟ۰ﮒﻟ۶ﮔ۲ﺅﺟ?2. **ﻟ؟ﺍﮒﺛﮔﮔﻟ­۵ﺅﺟ?*: ﮒﺏﻛﺛﺟﻠﻟﺟﮔ۲ﮔ۴ﺅﺙﻛﺗﻟ۵ﻟ؟ﺍﮒﺛﻟ­۵ﮒﻛﺟ۰ﮔﺁ
3. **ﮒ؟ﮔﻝﮔﮔ۴ﮒ**: ﮔﺁﮔ۴ﻝﮔﮒﻟ۶ﮔ۴ﮒﺅﺙﻛﺝﺟﻛﭦﮒ؟۰ﺅﺟ?4. **ﮒﮔﭘﮔﺑﮔﺍﻟ۶ﮒ**: ﮒﺏﮔﺏ۷ﻝﻝ؟۰ﮒ۷ﮔﺅﺙﮒﮔﭘﮔﺑﮔﺍﮒﻟ۶ﻟ۶ﮒ

#### 11.9.2 ﻟﺟﻝﭨﺑﮒﭨﭦﻟ؟؟

1. **ﮔﺁﮔ۴ﻠﻝﺛ؟**: ﮒﺙﻝﮒﻟﺍﻝ۷ `daily_reset()` ﻠﻝﺛ؟ﮒﻟ۶ﮔ۲ﮔ۴ﮒ۷
2. **ﮒ؟ﮔﭘﻝﮔ۶**: ﮒﺁﮒ۷ﮒﻟ۶ﻝﮔ۶ﻝﭦﺟﻝ۷ﺅﺙﮒ؟ﮔﭘﻝﮔ۶ﻛﭦ۳ﮔﻟ۰ﺅﺟ?3. **ﮒﻟ­۵ﮒﮒﭦ**: ﮔﭘﮒﺍﮒﻟ­۵ﮒﻝ،ﮒﺏﮒ۳ﻝﺅﺙﻠﺟﮒﻟﺟﻟ۶
4. **ﮒ؟ﮔﮒ؟۰ﻟ؟۰**: ﮒ؟ﮔﮒ؟۰ﻟ؟۰ﮒﻟ۶ﮔ۴ﮒﺅﺙﻛﺙﮒﻛﭦ۳ﮔﻝ­ﺅﺟ?
### 11.10 ﮔﻠﮔﮔ۴

#### 11.10.1 ﮒﺕﺕﻟ۶ﻠ؟ﻠ۱

| ﻠ؟ﻠ۱ | ﮒﺁﻟﺛﮒﮒ  | ﻟ۶۲ﮒﺏﮔﺗﮔ۰ |
|------|---------|---------|
| **ﻟ؟۱ﮒﻟ۱،ﮔﺅﺟ?* | ﻟ۶۵ﮒﮒﻟ۶ﻠﮒﭘ | ﮔ۲ﮔ۴ﮒﻟ۶ﮔ۲ﮔ۴ﻝﭨﮔﺅﺙﻟﺍﮔﺑﻛﭦ۳ﮔﻝ­ﻝ۴ |
| **ﻠ،ﻠ۱ﻛﭦ۳ﮔﮒﻟ­۵** | ﻛﭦ۳ﮔﻠ۱ﻝﻟﺟﻠ، | ﻠﻛﺛﻛﭦ۳ﮔﻠ۱ﻝﺅﺙﻛﺛﺟﻝ۷ﮔﭦﻟﺛﮔ۶ﻟ۰ﻝ؟ﺅﺟ?|
| **ﮔ۳ﮒﮒ۳ﺎﻟﺑ۴** | ﮔ۳ﮒﻝﻟﭘﺅﺟ?| ﮒﮒﺍﮔ۳ﮒﮔﻛﺛﺅﺙﻛﺙﮒﻟ؟۱ﮒﻛﭨﺓﺅﺟ?|
| **ﮒﻟ۶ﮔ۴ﮒﮒﺙﮒﺕﺕ** | ﮔﺍﮔ؟ﻝﭨﻟ؟۰ﻠﻟﺁﺁ | ﮔ۲ﮔ۴ﻟ؟۱ﮒﻟﺓﻟﺕ۹ﮒ۷ﺅﺙﻠﻝﺛ؟ﮔﺁﮔ۴ﮔﺍﺅﺟ?|

#### 11.10.2 ﮔ۴ﮒﺟﮒﮔ

```python
# ﮔ۴ﻝﮒﻟ۶ﮔ۲ﮔ۴ﮔ۴ﺅﺟ?# grep "COMPLIANCE" logs/trading.log

# ﮔ۴ﻝﻟﺟﻟ۶ﻟ؟ﺍﮒﺛ
# grep "Compliance violation" logs/trading.log

# ﮔ۴ﻝﮒﻟ­۵ﻟ؟ﺍﮒﺛ
# grep "COMPLIANCE ALERT" logs/trading.log
```

### 11.11 ﮔﭨﻝﭨ

**ﻠﮔﻛﭨﺓﺅﺟﺛ?*ﺅﺟ?- ﺅﺟ?**ﮒﻟ۶ﻛﺟﻠ**: ﻝ۰؟ﻛﺟﻝﺏﭨﻝﭨ100%ﻝ؛۵ﮒﮔﮔﺍﻝﻝ؟۰ﻟ۵ﺅﺟ?- ﺅﺟ?**ﻠ۲ﻠ۸ﻠ۱ﻟ­۵**: ﮒ؟ﮔﭘﻝﮔ۶ﺅﺙﮔﮒﻠ۱ﻟ­۵ﮒﻟ۶ﻠ۲ﺅﺟ?- ﺅﺟ?**ﮔﮔ؛ﻠﻛﺛ**: ﻟ۹ﮒ۷ﮒﮒﻟ۶ﮔ۲ﮔ۴ﺅﺙﻠﻛﺛﻛﭦﭦﮒﺓ۴ﮔﮔ؛
- ﺅﺟ?**ﻛﺕﻛﺕﮔﮒ**: ﻝ؛۵ﮒﮔﭦﮔﻝﭦ۶ﮔ ﮒﺅﺙﮔﮒﻝﺏﭨﻝﭨﻛﺕﻛﺕﺅﺟ?
**ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟**ﺅﺟ?1. **ﻝ،ﮒﺏﻠﮔ**: ﮒﺍﮒﻟ۶ﮔ۲ﮔ۴ﮔ۷۰ﮒﻠﮔﮒﺍQMTExecutor
2. **ﮒ؟ﮔﻝﮔ۶**: ﻟ؟ﺝﻝﺛ؟ﮒ؟ﮔﭘﻛﭨﭨﮒ۰ﺅﺙﮒ؟ﮔﭘﻝﮔ۶ﮒﻟ۶ﻝﭘﺅﺟ?3. **ﮔﻝﭨ­ﮔﺑﮔﺍ**: ﮒﺏﮔﺏ۷ﻝﻝ؟۰ﮒ۷ﮔﺅﺙﮒﮔﭘﮔﺑﮔﺍﻟ۶ﮒ
4. **ﮒﺗﻟ؟­ﮒ۱ﻠ**: ﻝ۰؟ﻛﺟﮒ۱ﻠﻝﻟ۶۲ﮒﻟ۶ﻟ۵ﮔﺎ

---

**ﮔﮔ۰۲ﻝﮔ؛**: v1.2.0 | **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02 | **ﻝﭨﺑﮔ۳ﻟ?*: ﻝ­ﻝ۴ﮔ۶ﻟ۰ﮒﺎﻟﺑﻟﺑ۲ﻛﭦﭦ
