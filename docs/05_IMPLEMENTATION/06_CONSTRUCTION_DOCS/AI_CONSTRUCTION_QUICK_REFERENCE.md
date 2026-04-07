---
module_id: AI_CONSTRUCTION_QUICK_REFERENCE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?standard_type: AIﮔﺛﮒﺓ۴ﮒﺟ،ﻠﮒﻟ?applicable_scope: AIﮔﭦﻟﺛﻛﺛﮔﺛﮒﺓ۴ﮒﺟﻟﺁ?compliance_level: ﮒﺙﭦﮒﭘﮔ۶ﻟ۰
responsibility:
  - 实施指南、部署文档
parent_document: ./CONSTRUCTION_SPECIFICATION.md
implementation_status: ﮒﺙﭦﮒﭘﮔ۶ﻟ۰
---
---


# AIﮔﺛﮒﺓ۴ﮒﺟ،ﻠﮒﻟ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

> **ﻭﺑ ﮒﺙﭦﮒﭘﻠﻟﺁﭨ**: AIﮔﭦﻟﺛﻛﺛﮒ۷ﮒﺙﮒ۶ﻛﭨﭨﻛﺛﮒﺙﮒﮔﮔﮔ۰۲ﮔﮒﭨﭦﻛﭨﭨﮒ۰ﮒﮒﺟﻠ۰ﭨﻠﻟﺁﭨﮔ؛ﮔﮔ۰۲
> **ﮒ؟ﮔﺑﻝ?*: [ﻟﮒﺝﮔﺛﮒﺓ۴ﻟﺁﺑﮔﻛﺗ۵](./CONSTRUCTION_SPECIFICATION.md)
> **ﻝﮔ؛**: v1.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02

---

## ﻗ?**5ﻝ۶ﮒﺟ،ﻠﮔ۲ﮔ?*

```
ﮒﺙﮒ۶ﮔﺛﮒﺓ۴ﮒﺅﺙAIﮒﺟﻠ۰ﭨﮒﻝ­ﻛﭨ۴ﻛﺕﻠ؟ﻠ۱ﺅﺙ?
ﻗ?1. ﮔﻟ۵ﮒﮒﭨﭦﻛﭨﻛﺗﻝﺎﭨﮒﻝﮔﻛﭨﭘﺅﺙ?     - ﻛﭨ۲ﻝ ﮔﻛﭨﭘ ﻗ?src/
     - ﮔﮔ۰۲ﮔﻛﭨﭘ ﻗ?docs/
     - ﻠﻝﺛ؟ﮔﻛﭨﭘ ﻗ?config/
     - ﮔﭖﻟﺁﮔﻛﭨﭘ ﻗ?tests/

ﻗ?2. ﻝ؟ﮔ ﮔﻛﭨﭘﮒ۳ﺗﮔﺁﮒ۵ﮒ­ﮒ۷ﺅﺙ
     - ﻛﺛﺟﻝ۷ LS ﮒﺛﻛﭨ۳ﮔ۲ﮔ?
ﻗ?3. ﮔﻛﭨﭘﮒﺛﮒﮔﺁﮒ۵ﮔ­۲ﻝ۰؟ﺅﺙ?     - Pythonﮔﻛﭨﭘ: ﮒﺍﮒ+ﻛﺕﮒﻝﭦ?(strategy_factory.py)
     - ﮔﮔ۰۲ﮔﻛﭨﭘ: ﮒ۳۶ﮒ+ﻛﺕﮒﻝﭦ?(STRATEGY_FACTORY_GUIDE.md)
     - ﻠﻝﺛ؟ﮔﻛﭨﭘ: ﮒﺍﮒ+ﻛﺕﮒﻝﭦ?(strategy_config.yaml)

ﻗ?4. ﮔﺁﮒ۵ﻛﺛﺟﻝ۷ﮔ ﮒﮔ۷۰ﮔﺟﺅﺙ?     - ﮔﮔ۰۲: ﮒﮒ،ﮒﺟﻠﮒﮔﺍﮔ?     - ﻛﭨ۲ﻝ : ﮒﮒ،ﮒﺟﻠﮔﺏ۷ﻠ
```

---

## ﻭ **ﮔ ﺕﮒﺟﮔﻛﭨﭘﮒ۳ﺗﻝﭨﮔﺅﺙﻟ؟ﺍﻛﺛﻟﺟﻛﺕ۹ﺅﺙﺅﺙ**

```
ZephyrAlpha/
ﻗﻗﻗ docs/                    # ﮔﮔﮔﮔ۰?ﻗ?  ﻗﻗﻗ 05_IMPLEMENTATION/
ﻗ?      ﻗﻗﻗ 06_CONSTRUCTION_DOCS/  # ﮔﺛﮒﺓ۴ﮔﮔ۰۲ﻛﺕﮒﭦ
ﻗ?ﻗﻗﻗ src/                     # ﮔﮔﮔﭦﻛﭨ۲ﻝ 
ﻗ?  ﻗﻗﻗ strategy/           # ﻝ­ﻝ۴ﮔ۷۰ﮒﺅﺙﻛﺕﮔﺁstrategies/ﺅﺙ?ﻗ?  ﻗﻗﻗ event_bus/          # ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﺅﺙﻛﺕﮔﺁevent/ﮔevents/ﺅﺙ?ﻗ?  ﻗﻗﻗ backtest/           # ﮒﮔﭖﮒﺙﮔﺅﺙﻛﺕﮔﺁbacktesting/ﺅﺙ?ﻗ?  ﻗﻗﻗ risk/               # ﻠ۲ﻠ۸ﻝ؟۰ﻝﺅﺙﻛﺕﮔﺁrisk_management/ﺅﺙ?ﻗ?  ﻗﻗﻗ execution/          # ﮔ۶ﻟ۰ﮒﺙﮔﺅﺙﻛﺕﮔﺁexecution_engine/ﺅﺙ?ﻗ?ﻗﻗﻗ tests/                   # ﮔﮔﮔﭖﻟﺁ?ﻗﻗﻗ config/                  # ﮔﮔﻠﻝﺛ?ﻗﻗﻗ scripts/                 # ﮔﮔﻟﮔ?ﻗﻗﻗ data/                    # ﮔﮔﮔﺍﮔ?ﻗﻗﻗ logs/                    # ﮔﮔﮔ۴ﮒﺟ?```

---

## ﻭ، **ﻝ۵ﮔ­۱ﮒﮒﭨﭦﻝﮔﻛﭨﭘﮒ۳ﺗﺅﺙﻟ؟ﺍﻛﺛﻟﺟﻛﺕ۹ﺅﺙﺅﺙ?*

```
ﻗ?src/strategies/          ﻗ?ﮒﭦﻛﺛﺟﻝ?src/strategy/
ﻗ?src/strategy_factory/    ﻗ?ﮒﭦﻛﺛﺟﻝ?src/strategy/factory.py
ﻗ?src/event/               ﻗ?ﮒﭦﻛﺛﺟﻝ?src/event_bus/
ﻗ?src/events/              ﻗ?ﮒﭦﻛﺛﺟﻝ?src/event_bus/
ﻗ?src/backtesting/         ﻗ?ﮒﭦﻛﺛﺟﻝ?src/backtest/
ﻗ?src/backtest_engine/     ﻗ?ﮒﭦﻛﺛﺟﻝ?src/backtest/
ﻗ?src/risk_management/     ﻗ?ﮒﭦﻛﺛﺟﻝ?src/risk/
ﻗ?src/execution_engine/    ﻗ?ﮒﭦﻛﺛﺟﻝ?src/execution/
ﻗ?docs/documentation/      ﻗ?ﮒﭦﻛﺛﺟﻝ?docs/
ﻗ?docs/docs/               ﻗ?ﮒﭦﻛﺛﺟﻝ?docs/
```

---

## ﻭ **ﮒﺛﮒﻟ۶ﻟﻠﮔ۴ﻟ۰?*

| ﮔﻛﭨﭘﻝﺎﭨﮒ | ﮔ­۲ﻝ۰؟ﻝ۳ﭦﻛﺝ | ﻠﻟﺁﺁﻝ۳ﭦﻛﺝ |
|---------|---------|---------|
| **Pythonﮔﻛﭨﭘ** | `strategy_factory.py` | `StrategyFactory.py` |
| **ﮔﮔ۰۲ﮔﻛﭨﭘ** | `STRATEGY_FACTORY_GUIDE.md` | `strategy_factory_guide.md` |
| **ﻠﻝﺛ؟ﮔﻛﭨﭘ** | `strategy_config.yaml` | `StrategyConfig.yaml` |
| **ﻝ؟ﮒﺛ** | `src/strategy/` | `src/Strategy/` |
| **ﮒﻠ** | `strategy_factory` | `strategyFactory` |
| **ﮒﺛﮔﺍ** | `create_strategy()` | `createStrategy()` |
| **ﻝﺎ?* | `StrategyFactory` | `strategy_factory` |
| **ﮒﺕﺕﻠ** | `MAX_POSITION` | `maxPosition` |

---

## ﻭ **ﮔ ﮒﮔﺛﮒﺓ۴ﮔﭖﻝ۷**

```
Step 1: ﮔ۲ﮔ۴ﻝﺍﮔﻝﭨﮔ?   ﻗ?LS d:\ZephyrAlpha\src\
   ﻗ?LS d:\ZephyrAlpha\docs\

Step 2: ﻝ۰؟ﻟ؟۳ﻝ؟ﮔ ﻛﺛﻝﺛ؟
   ﻗ?ﮔ۴ﻝﮔ؛ﮒﺟ،ﻠﮒﻟﻝﮔﻛﭨﭘﮒ۳ﺗﻝﭨﮔ?   ﻗ?ﻝ۰؟ﻟ؟۳ﮔ­۲ﻝ۰؟ﻟﺓﺁﮒﺝ

Step 3: ﻛﺛﺟﻝ۷ﮔ ﮒﮔ۷۰ﮔﺟ
   ﻗ?ﮔﮔ۰۲: ﮒﮒ،ﮒﺟﻠﮒﮔﺍﮔ?   ﻗ?ﻛﭨ۲ﻝ : ﮒﮒ،ﮒﺟﻠﮔﺏ۷ﻠ

Step 4: ﮒﮒﭨﭦﮔﻛﭨﭘ
   ﻗ?ﻛﺛﺟﻝ۷ﮔ­۲ﻝ۰؟ﻟﺓﺁﮒﺝ
   ﻗ?ﻛﺛﺟﻝ۷ﮔ­۲ﻝ۰؟ﮒﺛﮒ
   ﻗ?ﮔﺓﭨﮒ ﮔ ﮒﮒﮒ؟ﺗ

Step 5: ﻠ۹ﻟﺁ
   ﻗ?LS ﮔ۲ﮔ۴ﮔﻛﭨﭘﻛﺛﻝﺛ?   ﻗ?ﮔ۲ﮔ۴ﮒﺛﮒﻟ۶ﻟ?   ﻗ?ﻟﺟﻟ۰ﻟﺑ۷ﻠﻠ۷ﻝ۵
```

---

## ﻭ **ﮔﮔ۰۲ﮒﺟﻠﮒﮔﺍﮔ?*

```markdown
---
module_id: [MODULE_ID]_001
version: 1.0.0
status: Active
created_date: YYYY-MM-DD
last_updated: YYYY-MM-DD
owner: [ﻟﺑﻟﺑ۲ﻛﭦﭦ]
standard_type: [ﮔﮔ۰۲ﻝﺎﭨﮒ]
applicable_scope: [ﻠﻝ۷ﻟﮒﺑ]
compliance_level: [ﮒﻟ۶ﻝﭦ۶ﮒ،]
parent_document: [ﻝﭘﮔﮔ۰۲ﻟﺓﺁﮒﺝ]
implementation_status: [ﮒ؟ﮔﺛﻝﭘﮔ]
---
```

---

## ﻭﭨ **ﻛﭨ۲ﻝ ﮒﺟﻠﮔﺏ۷ﻠ**

```python
"""
[ﮔ۷۰ﮒﮒﻝ۶ﺍ] - [ﮔ۷۰ﮒﻟﻟﺑ۲]

ﻝﮔ؛: v1.0
ﮒﮒﭨﭦﮔ۴ﮔ: YYYY-MM-DD
ﻛﺛﻟ? [ﻛﺛﻟ]
"""

def function_name(param1: str, param2: Optional[Dict] = None) -> Dict[str, Any]:
    """ﮒﺛﮔﺍﻟﺁﺑﮔ
    
    Args:
        param1: ﮒﮔﺍ1ﻟﺁﺑﮔ
        param2: ﮒﮔﺍ2ﻟﺁﺑﮔﺅﺙﮒﺁﻠﺅﺙ
    
    Returns:
        ﻟﺟﮒﮒﺙﻟﺁﺑﮔ?    
    Raises:
        ValueError: ﮒﺙﮒﺕﺕﻟﺁﺑﮔ
    
    Example:
        >>> result = function_name("test")
        >>> print(result)
    """
    pass
```

---

## ﻭ۷ **ﮒﺕﺕﻟ۶ﻠﻟﺁﺁﻝ۳ﭦﻛﺝ**

### **ﻠﻟﺁﺁ1: ﮔﻛﭨﭘﮒ۳ﺗﮒﺛﮒﻠﻟﺁ?*

```bash
# ﻗ?ﻠﻟﺁﺁ
src/strategies/factory.py

# ﻗ?ﮔ­۲ﻝ۰؟
src/strategy/factory.py
```

### **ﻠﻟﺁﺁ2: ﮔﻛﭨﭘﮒﺛﮒﻠﻟﺁﺁ**

```python
# ﻗ?ﻠﻟﺁﺁ
StrategyFactory.py

# ﻗ?ﮔ­۲ﻝ۰؟
strategy_factory.py
```

### **ﻠﻟﺁﺁ3: ﮒﻛﺕﮔ۷۰ﮒﮒ۳ﻛﺕ۹ﻛﺛﻝﺛ؟**

```bash
# ﻗ?ﻠﻟﺁﺁ
src/strategy/factory.py
src/strategies/factory.py
src/core/strategy_factory.py

# ﻗ?ﮔ­۲ﻝ۰؟ﺅﺙﮒ۹ﻛﺟﻝﻛﺕﻛﺕ۹ﺅﺙ
src/strategy/factory.py
```

---

## ﻭ **ﻠﮒﺍﻠ؟ﻠ۱ﺅﺙ?*

1. **ﮔ۴ﻝﮒ؟ﮔﺑﻝ?*: [ﻟﮒﺝﮔﺛﮒﺓ۴ﻟﺁﺑﮔﻛﺗ۵](./CONSTRUCTION_SPECIFICATION.md)
2. **ﮔ۲ﮔ۴ﻝﺍﮔﻝﭨﮔ?*: ﻛﺛﺟﻝ۷ LS ﮒﺛﻛﭨ۳
3. **ﮒﻟﮒﺓﺎﮔﮔﻛﭨ?*: ﮔ۴ﻝﻝﺎﭨﻛﺙﺙﮔﻛﭨﭘﻝﻝﭨﮔ?4. **ﻟﺁ۱ﻠ؟ﻝ۷ﮔﺓ**: ﮒ۵ﮔﻛﺕﻝ۰؟ﮒ؟ﺅﺙﮒﻟﺁ۱ﻠ؟ﻝ۷ﮔ?
---

## ﻭﺁ **ﻟ؟ﺍﻛﺛﻟﺟﮒ۴ﻟﺁ?*

> **"ﮒ۷ﮒﮒﭨﭦﻛﭨﭨﻛﺛﮔﻛﭨﭘﮒﺅﺙﮒﻝ۷LSﮔ۲ﮔ۴ﻝﺍﮔﻝﭨﮔﺅﺙﻝ۰؟ﻟ؟۳ﮔ­۲ﻝ۰؟ﻟﺓﺁﮒﺝﮒﮒﺛﮒﺅﺙﻛﺛﺟﻝ۷ﮔ ﮒﮔ۷۰ﮔﺟﺅﺙﻠﭖﮒﺝ۹ﮔﺛﮒﺓ۴ﻟ۶ﻟﻙ?**

---

**ﮔﮔ۰۲ﻝﭨﺑﮔ۳ﻟ?*: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ? 
**ﻝﮔ؛**: v1.0  
**ﮔﮒﮔﺑﮔ?*: 2026-04-02
