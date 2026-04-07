---
module_id: AI_CONSTRUCTION_QUICK_REFERENCE
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - AIﮔﺛﮒﺓ۴ﮒﺟﻠﮒﻟ文档
---

﻿---
module_id: AI_CONSTRUCTION_QUICK_REFERENCE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?standard_type: AIﮔﺛﮒﺓ۴ﮒﺟ،ﻠﮒﻟ?applicable_scope: AIﮔﭦﻟﺛﻛﺛﮔﺛﮒﺓ۴ﮒﺟﻟﺁ?compliance_level: ﮒﺙﭦﮒﭘﮔ۶ﻟ۰
responsibility:
  - 系统实施与部署管理与优化维护
parent_document: ./CONSTRUCTION_SPECIFICATION.md
implementation_status: ﮒﺙﭦﮒﭘﮔ۶ﻟ۰
---
---


# AIﮔﺛﮒﺓ۴ﮒﺟ،ﻠﮒﻟ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

> **ﻭﺑ ﮒﺙﭦﮒﭘﻠﻟﺁﭨ**: AIﮔﭦﻟﺛﻛﺛﮒ۷ﮒﺙﮒ۶ﻛﭨﭨﻛﺛﮒﺙﮒﮔﮔﮔ۰۲ﮔﮒﭨﭦﻛﭨﭨﮒ۰ﮒﮒﺟﻠ۰ﭨﻠﻟﺁﭨﮔ؛ﮔﮔ۰۲
> **ﮒ؟ﮔﺑﻝ?*: [ﻟﮒﺝﮔﺛﮒﺓ۴ﻟﺁﺑﮔﻛﺗ۵](./CONSTRUCTION_SPECIFICATION.md)
> **ﻝﮔ؛**: v1.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02

---

## ﻗ?**5ﻝ۶ﮒﺟ،ﻠﮔ۲ﮔ?*

```
ﮒﺙﮒ۶ﮔﺛﮒﺓ۴ﮒﺅﺙAIﮒﺟﻠ۰ﭨﮒﻝﻛﭨ۴ﻛﺕﻠ؟ﻠ۱ﺅﺙ?
ﻗ?1. ﮔﻟ۵ﮒﮒﭨﭦﻛﭨﻛﺗﻝﺎﭨﮒﻝﮔﻛﭨﭘﺅﺙ?     - ﻛﭨ۲ﻝﮔﻛﭨﭘ ﻗ?src/
     - ﮔﮔ۰۲ﮔﻛﭨﭘ ﻗ?docs/
     - ﻠﻝﺛ؟ﮔﻛﭨﭘ ﻗ?config/
     - ﮔﭖﻟﺁﮔﻛﭨﭘ ﻗ?tests/

ﻗ?2. ﻝ؟ﮔﮔﻛﭨﭘﮒ۳ﺗﮔﺁﮒ۵ﮒﮒ۷ﺅﺙ
     - ﻛﺛﺟﻝ۷ LS ﮒﺛﻛﭨ۳ﮔ۲ﮔ?
ﻗ?3. ﮔﻛﭨﭘﮒﺛﮒﮔﺁﮒ۵ﮔ۲ﻝ۰؟ﺅﺙ?     - Pythonﮔﻛﭨﭘ: ﮒﺍﮒ+ﻛﺕﮒﻝﭦ?(strategy_factory.py)
     - ﮔﮔ۰۲ﮔﻛﭨﭘ: ﮒ۳۶ﮒ+ﻛﺕﮒﻝﭦ?(STRATEGY_FACTORY_GUIDE.md)
     - ﻠﻝﺛ؟ﮔﻛﭨﭘ: ﮒﺍﮒ+ﻛﺕﮒﻝﭦ?(strategy_config.yaml)

ﻗ?4. ﮔﺁﮒ۵ﻛﺛﺟﻝ۷ﮔﮒﮔ۷۰ﮔﺟﺅﺙ?     - ﮔﮔ۰۲: ﮒﮒ،ﮒﺟﻠﮒﮔﺍﮔ?     - ﻛﭨ۲ﻝ: ﮒﮒ،ﮒﺟﻠﮔﺏ۷ﻠ
```

---

## ﻭ **ﮔﺕﮒﺟﮔﻛﭨﭘﮒ۳ﺗﻝﭨﮔﺅﺙﻟ؟ﺍﻛﺛﻟﺟﻛﺕ۹ﺅﺙﺅﺙ**

```
ZephyrAlpha/
ﻗﻗﻗ docs/                    # ﮔﮔﮔﮔ۰?ﻗ?  ﻗﻗﻗ 05_IMPLEMENTATION/
ﻗ?      ﻗﻗﻗ 06_CONSTRUCTION_DOCS/  # ﮔﺛﮒﺓ۴ﮔﮔ۰۲ﻛﺕﮒﭦ
ﻗ?ﻗﻗﻗ src/                     # ﮔﮔﮔﭦﻛﭨ۲ﻝ
ﻗ?  ﻗﻗﻗ strategy/           # ﻝﻝ۴ﮔ۷۰ﮒﺅﺙﻛﺕﮔﺁstrategies/ﺅﺙ?ﻗ?  ﻗﻗﻗ event_bus/          # ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﺅﺙﻛﺕﮔﺁevent/ﮔevents/ﺅﺙ?ﻗ?  ﻗﻗﻗ backtest/           # ﮒﮔﭖﮒﺙﮔﺅﺙﻛﺕﮔﺁbacktesting/ﺅﺙ?ﻗ?  ﻗﻗﻗ risk/               # ﻠ۲ﻠ۸ﻝ؟۰ﻝﺅﺙﻛﺕﮔﺁrisk_management/ﺅﺙ?ﻗ?  ﻗﻗﻗ execution/          # ﮔ۶ﻟ۰ﮒﺙﮔﺅﺙﻛﺕﮔﺁexecution_engine/ﺅﺙ?ﻗ?ﻗﻗﻗ tests/                   # ﮔﮔﮔﭖﻟﺁ?ﻗﻗﻗ config/                  # ﮔﮔﻠﻝﺛ?ﻗﻗﻗ scripts/                 # ﮔﮔﻟﮔ?ﻗﻗﻗ data/                    # ﮔﮔﮔﺍﮔ?ﻗﻗﻗ logs/                    # ﮔﮔﮔ۴ﮒﺟ?```

---

## ﻭ، **ﻝ۵ﮔ۱ﮒﮒﭨﭦﻝﮔﻛﭨﭘﮒ۳ﺗﺅﺙﻟ؟ﺍﻛﺛﻟﺟﻛﺕ۹ﺅﺙﺅﺙ?*

```
ﻗ?src/strategies/          ﻗ?ﮒﭦﻛﺛﺟﻝ?src/strategy/
ﻗ?src/strategy_factory/    ﻗ?ﮒﭦﻛﺛﺟﻝ?src/strategy/factory.py
ﻗ?src/event/               ﻗ?ﮒﭦﻛﺛﺟﻝ?src/event_bus/
ﻗ?src/events/              ﻗ?ﮒﭦﻛﺛﺟﻝ?src/event_bus/
ﻗ?src/backtesting/         ﻗ?ﮒﭦﻛﺛﺟﻝ?src/backtest/
ﻗ?src/backtest_engine/     ﻗ?ﮒﭦﻛﺛﺟﻝ?src/backtest/
ﻗ?src/risk_management/     ﻗ?ﮒﭦﻛﺛﺟﻝ?src/risk/
ﻗ?src/execution_engine/    ﻗ?ﮒﭦﻛﺛﺟﻝ?src/execution/
ﻗ?docs/documentation/      ﻗ?ﮒﭦﻛﺛﺟﻝ?docs/
ﻗ?docs/docs/               ﻗ?ﮒﭦﻛﺛﺟﻝ?docs/
```

---

## ﻭ **ﮒﺛﮒﻟ۶ﻟﻠﮔ۴ﻟ۰?*

| ﮔﻛﭨﭘﻝﺎﭨﮒ | ﮔ۲ﻝ۰؟ﻝ۳ﭦﻛﺝ | ﻠﻟﺁﺁﻝ۳ﭦﻛﺝ |
|---------|---------|---------|
| **Pythonﮔﻛﭨﭘ** | `strategy_factory.py` | `StrategyFactory.py` |
| **ﮔﮔ۰۲ﮔﻛﭨﭘ** | `STRATEGY_FACTORY_GUIDE.md` | `strategy_factory_guide.md` |
| **ﻠﻝﺛ؟ﮔﻛﭨﭘ** | `strategy_config.yaml` | `StrategyConfig.yaml` |
| **ﻝ؟ﮒﺛ** | `src/strategy/` | `src/Strategy/` |
| **ﮒﻠ** | `strategy_factory` | `strategyFactory` |
| **ﮒﺛﮔﺍ** | `create_strategy()` | `createStrategy()` |
| **ﻝﺎ?* | `StrategyFactory` | `strategy_factory` |
| **ﮒﺕﺕﻠ** | `MAX_POSITION` | `maxPosition` |

---

## ﻭ **ﮔﮒﮔﺛﮒﺓ۴ﮔﭖﻝ۷**

```
Step 1: ﮔ۲ﮔ۴ﻝﺍﮔﻝﭨﮔ?   ﻗ?LS d:\ZephyrAlpha\src\
   ﻗ?LS d:\ZephyrAlpha\docs\

Step 2: ﻝ۰؟ﻟ؟۳ﻝ؟ﮔﻛﺛﻝﺛ؟
ﻗ?ﮔ۴ﻝﮔ؛ﮒﺟ،ﻠﮒﻟﻝﮔﻛﭨﭘﮒ۳ﺗﻝﭨﮔ?   ﻗ?ﻝ۰؟ﻟ؟۳ﮔ۲ﻝ۰؟ﻟﺓﺁﮒﺝ

Step 3: ﻛﺛﺟﻝ۷ﮔﮒﮔ۷۰ﮔﺟ
ﻗ?ﮔﮔ۰۲: ﮒﮒ،ﮒﺟﻠﮒﮔﺍﮔ?   ﻗ?ﻛﭨ۲ﻝ: ﮒﮒ،ﮒﺟﻠﮔﺏ۷ﻠ

Step 4: ﮒﮒﭨﭦﮔﻛﭨﭘ
ﻗ?ﻛﺛﺟﻝ۷ﮔ۲ﻝ۰؟ﻟﺓﺁﮒﺝ
ﻗ?ﻛﺛﺟﻝ۷ﮔ۲ﻝ۰؟ﮒﺛﮒ
ﻗ?ﮔﺓﭨﮒﮔﮒﮒﮒ؟ﺗ

Step 5: ﻠ۹ﻟﺁ
   ﻗ?LS ﮔ۲ﮔ۴ﮔﻛﭨﭘﻛﺛﻝﺛ?   ﻗ?ﮔ۲ﮔ۴ﮒﺛﮒﻟ۶ﻟ?   ﻗ?ﻟﺟﻟ۰ﻟﺑ۷ﻠﻠ۷ﻝ۵
```

---

## ﻭ **ﮔﮔ۰۲ﮒﺟﻠﮒﮔﺍﮔ?*

```markdown
---
module_id: [MODULE_ID]_001
version: 1.0.0
status: Active
created_date: YYYY-MM-DD
last_updated: YYYY-MM-DD
owner: [ﻟﺑﻟﺑ۲ﻛﭦﭦ]
standard_type: [ﮔﮔ۰۲ﻝﺎﭨﮒ]
applicable_scope: [ﻠﻝ۷ﻟﮒﺑ]
compliance_level: [ﮒﻟ۶ﻝﭦ۶ﮒ،]
parent_document: [ﻝﭘﮔﮔ۰۲ﻟﺓﺁﮒﺝ]
implementation_status: [ﮒ؟ﮔﺛﻝﭘﮔ]
---
```

---

## ﻭﭨ **ﻛﭨ۲ﻝﮒﺟﻠﮔﺏ۷ﻠ**

```python
"""
[ﮔ۷۰ﮒﮒﻝ۶ﺍ] - [ﮔ۷۰ﮒﻟﻟﺑ۲]

ﻝﮔ؛: v1.0
ﮒﮒﭨﭦﮔ۴ﮔ: YYYY-MM-DD
ﻛﺛﻟ? [ﻛﺛﻟ]
"""

def function_name(param1: str, param2: Optional[Dict] = None) -> Dict[str, Any]:
    """ﮒﺛﮔﺍﻟﺁﺑﮔ
    
    Args:
        param1: ﮒﮔﺍ1ﻟﺁﺑﮔ
        param2: ﮒﮔﺍ2ﻟﺁﺑﮔﺅﺙﮒﺁﻠﺅﺙ
    
    Returns:
        ﻟﺟﮒﮒﺙﻟﺁﺑﮔ?    
    Raises:
        ValueError: ﮒﺙﮒﺕﺕﻟﺁﺑﮔ
    
    Example:
        >>> result = function_name("test")
        >>> print(result)
    """
    pass
```

---

## ﻭ۷ **ﮒﺕﺕﻟ۶ﻠﻟﺁﺁﻝ۳ﭦﻛﺝ**

### **ﻠﻟﺁﺁ1: ﮔﻛﭨﭘﮒ۳ﺗﮒﺛﮒﻠﻟﺁ?*

```bash
# ﻗ?ﻠﻟﺁﺁ
src/strategies/factory.py

# ﻗ?ﮔ۲ﻝ۰؟
src/strategy/factory.py
```

### **ﻠﻟﺁﺁ2: ﮔﻛﭨﭘﮒﺛﮒﻠﻟﺁﺁ**

```python
# ﻗ?ﻠﻟﺁﺁ
StrategyFactory.py

# ﻗ?ﮔ۲ﻝ۰؟
strategy_factory.py
```

### **ﻠﻟﺁﺁ3: ﮒﻛﺕﮔ۷۰ﮒﮒ۳ﻛﺕ۹ﻛﺛﻝﺛ؟**

```bash
# ﻗ?ﻠﻟﺁﺁ
src/strategy/factory.py
src/strategies/factory.py
src/core/strategy_factory.py

# ﻗ?ﮔ۲ﻝ۰؟ﺅﺙﮒ۹ﻛﺟﻝﻛﺕﻛﺕ۹ﺅﺙ
src/strategy/factory.py
```

---

## ﻭ **ﻠﮒﺍﻠ؟ﻠ۱ﺅﺙ?*

1. **ﮔ۴ﻝﮒ؟ﮔﺑﻝ?*: [ﻟﮒﺝﮔﺛﮒﺓ۴ﻟﺁﺑﮔﻛﺗ۵](./CONSTRUCTION_SPECIFICATION.md)
2. **ﮔ۲ﮔ۴ﻝﺍﮔﻝﭨﮔ?*: ﻛﺛﺟﻝ۷ LS ﮒﺛﻛﭨ۳
3. **ﮒﻟﮒﺓﺎﮔﮔﻛﭨ?*: ﮔ۴ﻝﻝﺎﭨﻛﺙﺙﮔﻛﭨﭘﻝﻝﭨﮔ?4. **ﻟﺁ۱ﻠ؟ﻝ۷ﮔﺓ**: ﮒ۵ﮔﻛﺕﻝ۰؟ﮒ؟ﺅﺙﮒﻟﺁ۱ﻠ؟ﻝ۷ﮔ?
---

## ﻭﺁ **ﻟ؟ﺍﻛﺛﻟﺟﮒ۴ﻟﺁ?*

> **"ﮒ۷ﮒﮒﭨﭦﻛﭨﭨﻛﺛﮔﻛﭨﭘﮒﺅﺙﮒﻝ۷LSﮔ۲ﮔ۴ﻝﺍﮔﻝﭨﮔﺅﺙﻝ۰؟ﻟ؟۳ﮔ۲ﻝ۰؟ﻟﺓﺁﮒﺝﮒﮒﺛﮒﺅﺙﻛﺛﺟﻝ۷ﮔﮒﮔ۷۰ﮔﺟﺅﺙﻠﭖﮒﺝ۹ﮔﺛﮒﺓ۴ﻟ۶ﻟﻙ?**

---

**ﮔﮔ۰۲ﻝﭨﺑﮔ۳ﻟ?*: ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?
**ﻝﮔ؛**: v1.0  
**ﮔﮒﮔﺑﮔ?*: 2026-04-02
