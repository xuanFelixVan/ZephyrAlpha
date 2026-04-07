﻿---
module_id: PYTHON_CODING_BEST_PRACTICES_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?standard_type: ﻝﺙﻝ ﮔﻛﺛﺏﮒ؟ﻟﺓ?applicable_scope: Pythonﻛﭨ۲ﻝ ﻝﺙﮒ
responsibility:
  - 实施指南、部署文档
compliance_level: ﮒﺙﭦﮒﭘﮔ۶ﻟ۰
parent_document: ../BEST_PRACTICES_INDEX.md
implementation_status: Active
---
---


# Pythonﻛﭨ۲ﻝ ﻟ۶ﻟﮔﻛﺛﺏﮒ؟ﻟﺓ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

> **ﮔﻛﺛﺏﮒ؟ﻟﺓﭖﻝﺙﮒ?*: BP-001  
> **ﻝﮔ؛**: v1.0  
> **ﻠﻝ۷ﮒﭦﮔﺁ**: ﮔﮔPythonﻛﭨ۲ﻝ ﻝﺙﮒ  
> **ﮒﺙﭦﮒﭘﻝﭦ۶ﮒ،**: ﻭﺑ **ﮒﺙﭦﮒﭘﮔ۶ﻟ۰**

---

## ﻭ **ﻠﻝ۷ﮒﭦﮔﺁ**

### **ﻛﺛﮔﭘﻛﺛﺟﻝ۷**

- ﻗ?ﻝﺙﮒﮔﺍﻝPythonﮔ۷۰ﮒ
- ﻗ?ﻠﮔﻝﺍﮔﻛﭨ۲ﻝ 
- ﻗ?ﻛﭨ۲ﻝ ﮒ؟۰ﮔ۴ﮔﭘﮔ۲ﮔ?- ﻗ?ﮒ۱ﻠﮒﻛﺛﮒﺙﮒ?
### **ﻠﻝ۷ﻟﮒﺑ**

- ﮔﮔﻝﻛﭦ۶ﻝﺁﮒ۱ﻛﭨ۲ﻝ ?- ﮔﮔﮔﭖﻟﺁﻛﭨ۲ﻝ ?- ﮔﮔﻟﮔ؛ﻛﭨ۲ﻝ ?- ﮔﮔﻠﻝﺛ؟ﻛﭨ۲ﻝ ?
---

## ﻭﺁ **ﮒ؟ﮔﺛﮔ­۴ﻠ۹۳**

### **1. ﮒﺛﮒﻟ۶ﻟ**

#### **ﮒﻠﮒﺛﮒ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒﺍﮒ+ﻛﺕﮒﻝﭦ?strategy_factory = StrategyFactory()
event_bus = EventBus()
max_position_size = 0.95

# ﻗ?ﻠﻟﺁﺁ - ﮒ۳۶ﻠ۸ﺙﮒﺏﺍﮔﮒﺍﻠ۸ﺙﮒﺏ?strategyFactory = StrategyFactory()
eventBus = EventBus()
MaxPositionSize = 0.95
```

#### **ﮒﺕﺕﻠﮒﺛﮒ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒ۷ﮒ۳۶ﮒ?ﻛﺕﮒﻝﭦ?MAX_POSITION_SIZE = 0.95
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# ﻗ?ﻠﻟﺁﺁ - ﮒﺍﮒﮔﻠ۸ﺙﮒﺏ?max_position_size = 0.95
defaultTimeout = 30
apiBaseUrl = "https://api.example.com"
```

#### **ﮒﺛﮔﺍﮒﺛﮒ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒﺍﮒ+ﻛﺕﮒﻝﭦﺟﺅﺙﮒ۷ﻟﺁﮒﺙﮒ۳?def create_strategy(strategy_type: str) -> Strategy:
    pass

def calculate_position_size(capital: float) -> float:
    pass

def get_event_bus() -> EventBus:
    pass

# ﻗ?ﻠﻟﺁﺁ - ﮒ۳۶ﻠ۸ﺙﮒﺏﺍﮔﮒﻟﺁﮒﺙﮒ۳?def CreateStrategy(strategy_type: str) -> Strategy:
    pass

def PositionSize(capital: float) -> float:
    pass
```

#### **ﻝﺎﭨﮒﺛﮒ?*

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒ۳۶ﻠ۸ﺙﮒﺏ?class StrategyFactory:
    pass

class EventBus:
    pass

class BacktestAdapter:
    pass

# ﻗ?ﻠﻟﺁﺁ - ﮒﺍﮒ+ﻛﺕﮒﻝﭦ?class strategy_factory:
    pass

class event_bus:
    pass
```

---

### **2. ﻛﭨ۲ﻝ ﮔ ﺙﮒﺙ**

#### **ﮒﺁﺙﮒ۴ﻠ۰ﭦﮒﭦ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮔ ﮒﮒﭦ?ﻗ?ﻝ؛؛ﻛﺕﮔﺗﮒﭦ ﻗ?ﮔ؛ﮒﺍﮔ۷۰ﮒ
import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

import pandas as pd
import numpy as np

from strategy.base import BaseStrategy
from event_bus.event import Event

# ﻗ?ﻠﻟﺁﺁ - ﻠ۰ﭦﮒﭦﮔﺓﺓﻛﺗﺎ
from strategy.base import BaseStrategy
import pandas as pd
import os
from typing import Dict
import numpy as np
```

#### **ﻛﭨ۲ﻝ ﻝﺙ۸ﻟﺟ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - 4ﻛﺕ۹ﻝ۸ﭦﮔ ﺙﻝﺙ۸ﻟﺟ?def calculate_position_size(
    capital: float,
    risk_pct: float,
    entry_price: float,
    stop_loss: float
) -> float:
    risk_amount = capital * risk_pct
    price_diff = entry_price - stop_loss
    position_size = risk_amount / price_diff
    return position_size

# ﻗ?ﻠﻟﺁﺁ - 2ﻛﺕ۹ﻝ۸ﭦﮔ ﺙﮔTab
def calculate_position_size(capital, risk_pct):
  risk_amount = capital * risk_pct
  return risk_amount
```

#### **ﻟ۰ﻠﺟﮒﭦ۵ﻠﮒ?*

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮔﺁﻟ۰ﻛﺕﻟﭘﻟﺟ?00ﮒ­ﻝ؛۵
result = self.strategy_factory.create_strategy(
    strategy_type="moving_average",
    strategy_id="ma_001",
    config={
        "fast_period": 10,
        "slow_period": 30
    }
)

# ﻗ?ﻠﻟﺁﺁ - ﻟ۰ﻟﺟﻠ?result = self.strategy_factory.create_strategy(strategy_type="moving_average", strategy_id="ma_001", config={"fast_period": 10, "slow_period": 30})
```

---

### **3. ﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲**

#### **ﮒﺛﮔﺍﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒ؟ﮔﺑﻝﻝﺎﭨﮒﮔﺏ۷ﻟ۶?def create_strategy(
    strategy_type: str,
    strategy_id: str,
    config: Optional[Dict[str, Any]] = None
) -> BaseStrategy:
    """ﮒﮒﭨﭦﻝ­ﻝ۴ﮒ؟ﻛﺝ
    
    Args:
        strategy_type: ﻝ­ﻝ۴ﻝﺎﭨﮒ
        strategy_id: ﻝ­ﻝ۴ID
        config: ﻝ­ﻝ۴ﻠﻝﺛ؟ﺅﺙﮒﺁﻠﺅﺙ
    
    Returns:
        ﻝ­ﻝ۴ﮒ؟ﻛﺝ
    
    Raises:
        ValueError: ﮒ۵ﮔﻝ­ﻝ۴ﻝﺎﭨﮒﮔ۹ﮔﺏ۷ﮒ?    """
    pass

# ﻗ?ﻠﻟﺁﺁ - ﻝﺙﭦﮒﺍﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲
def create_strategy(strategy_type, strategy_id, config=None):
    pass
```

#### **ﻝﺎﭨﮒﺎﮔ۶ﻝﺎﭨﮒﮔﺏ۷ﻟ۶?*

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﻝﺎﭨﮒﺎﮔ۶ﻝﺎﭨﮒﮔﺏ۷ﻟ۶?class StrategyFactory:
    """ﻝ­ﻝ۴ﮒﺓ۴ﮒ"""
    
    def __init__(self):
        self.registry: StrategyRegistry = StrategyRegistry()
        self._instances: Dict[str, BaseStrategy] = {}
        self._lock: Lock = Lock()

# ﻗ?ﻠﻟﺁﺁ - ﻝﺙﭦﮒﺍﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲
class StrategyFactory:
    def __init__(self):
        self.registry = StrategyRegistry()
        self._instances = {}
        self._lock = Lock()
```

---

### **4. ﮔﮔ۰۲ﮒ­ﻝ؛۵ﻛﺕ?*

#### **ﮔ۷۰ﮒﮔﮔ۰۲ﮒ­ﻝ؛۵ﻛﺕ?*

```python
"""
ﻝ­ﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ - ﻝ؟۰ﻝﻝ­ﻝ۴ﻝﮒﮒﭨﭦﮒﻝﮒﺛﮒ۷ﮔ

ﻝﮔ؛: v1.0
ﮒﮒﭨﭦﮔ۴ﮔ: 2026-04-02
ﻛﺛﻟ? ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?
ﻛﺕﭨﻟ۵ﻝﭨﻛﭨﭘ:
- BaseStrategy: ﻝ­ﻝ۴ﮒﭦﻝﺎﭨ
- StrategyFactory: ﻝ­ﻝ۴ﮒﺓ۴ﮒ
- StrategyRegistry: ﻝ­ﻝ۴ﮔﺏ۷ﮒﻟ۰?- StrategyLoader: ﻝ­ﻝ۴ﮒ ﻟﺛﺛﮒ?
ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ:
    >>> factory = StrategyFactory()
    >>> strategy = factory.create_strategy("moving_average", "ma_001")
"""
```

#### **ﻝﺎﭨﮔﮔ۰۲ﮒ­ﻝ؛۵ﻛﺕﺎ**

```python
class StrategyFactory:
    """ﻝ­ﻝ۴ﮒﺓ۴ﮒ - ﮒﮒﭨﭦﮒﻝ؟۰ﻝﻝ­ﻝ۴ﮒ؟ﻛﺝ?    
    Attributes:
        registry: ﻝ­ﻝ۴ﮔﺏ۷ﮒﻟ۰?        _instances: ﻝ­ﻝ۴ﮒ؟ﻛﺝﻝﺙﮒ­
        _lock: ﻝﭦﺟﻝ۷ﻠ?    
    Example:
        >>> factory = StrategyFactory()
        >>> strategy = factory.create_strategy("moving_average", "ma_001")
        >>> print(strategy.strategy_id)
        'ma_001'
    """
```

#### **ﮒﺛﮔﺍﮔﮔ۰۲ﮒ­ﻝ؛۵ﻛﺕ?*

```python
def create_strategy(
    self,
    strategy_type: str,
    strategy_id: str,
    config: Optional[Dict[str, Any]] = None
) -> BaseStrategy:
    """ﮒﮒﭨﭦﻝ­ﻝ۴ﮒ؟ﻛﺝ
    
    Args:
    
    Returns:
        ﮒﮒﭨﭦﻝﻝ­ﻝ۴ﮒ؟ﻛﺝ?    
    Raises:
        ValueError: ﮒ۵ﮔﻝ­ﻝ۴ﻝﺎﭨﮒﮔ۹ﮔﺏ۷ﮒ?        KeyError: ﮒ۵ﮔﻝ­ﻝ۴ﻝﺎﭨﮒﻛﺕﮒ­ﮒ?    
    Example:
        >>> factory = StrategyFactory()
        >>> config = {"fast_period": 10, "slow_period": 30}
        >>> strategy = factory.create_strategy("moving_average", "ma_001", config)
        >>> print(strategy.strategy_id)
        'ma_001'
    """
    pass
```

---

## ﻗ ﺅﺕ **ﮔﺏ۷ﮔﻛﭦﻠ۰ﺗ**

### **1. ﻠﺟﮒﻝﻝﺙﻝ ﻠ۲ﮔ ?*

```python
# ﻗ?ﻠﺟﮒﻛﺛﺟﻝ۷ﮒ۷ﮒﺎﮒﻠ
strategy_factory = None

def get_strategy_factory():
    global strategy_factory
    if strategy_factory is None:
        strategy_factory = StrategyFactory()
    return strategy_factory

# ﻗ?ﻛﺛﺟﻝ۷ﮒﻛﺝﮔ۷۰ﮒﺙﮔﻛﺝﻟﭖﮔﺏ۷ﮒ?class StrategyFactory:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### **2. ﻠﺟﮒﻠ­ﮔﺏﮔﺍﮒ­**

```python
# ﻗ?ﻠ­ﮔﺏﮔﺍﮒ­
if position_size > 0.95:
    pass

# ﻗ?ﻛﺛﺟﻝ۷ﮒﺕﺕﻠ
MAX_POSITION_SIZE = 0.95

if position_size > MAX_POSITION_SIZE:
    pass
```

### **3. ﻠﺟﮒﮔﺓﺎﮒﺎﮒﭖﮒ۴**

```python
# ﻗ?ﮔﺓﺎﮒﺎﮒﭖﮒ۴
def process_data(data):
    if data is not None:
        if 'items' in data:
            for item in data['items']:
                if item['type'] == 'stock':
                    # ﮒ۳ﻝﻠﭨﻟﺝ
                    pass

# ﻗ?ﮔﮒﻟﺟﮒ
def process_data(data):
    if data is None:
        return
    
    if 'items' not in data:
        return
    
    for item in data['items']:
        if item['type'] != 'stock':
            continue
        # ﮒ۳ﻝﻠﭨﻟﺝ
```

---

## ﻭ **ﮔﮔﻟﺁﻛﺙﺍ**

### **ﻛﭨ۲ﻝ ﻟﺑ۷ﻠﮔﮔ **

| ﮔﮔ  | ﻝ؟ﮔ  | ﮒ؟ﻠ | ﻝﭘﮔ?|
|------|------|------|------|
| ﻛﭨ۲ﻝ ﮒﺁﻟﺁﭨﮔ?| ﻗ?0ﮒ?| 95ﮒ?| ﻗ?|
| ﻛﭨ۲ﻝ ﮒ۳ﮔﮒﭦ?| ﻗ?0 | 8 | ﻗ?|
| ﮔﮔ۰۲ﻟ۵ﻝﻝ?| ﻗ?0% | 90% | ﻗ?|
| ﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲ﻟ۵ﻝﻝ?| ﻗ?0% | 95% | ﻗ?|

### **ﮒﺙﮒﮔﻝﮔﮔ ?*

| ﮔﮔ  | ﮔﺗﻟﺟﮒ?| ﮔﺗﻟﺟﮒ?| ﮔﮒ |
|------|--------|--------|------|
| ﻛﭨ۲ﻝ ﮒ؟۰ﮔ۴ﮔﭘﻠﺑ | 2ﮒﺍﮔﭘ | 1ﮒﺍﮔﭘ | 50% |
| Bugﻛﺟ؟ﮒ۳ﮔﭘﻠﺑ | 4ﮒﺍﮔﭘ | 2ﮒﺍﮔﭘ | 50% |
| ﮔﺍﻛﭦﭦﻛﺕﮔﮔﭘﻠﺑ | 2ﮒ?| 1ﮒ?| 50% |

---

## ﻭ **ﻝﺕﮒﺏﮔ۰ﻛﺝ**

- [ﻝ­ﻝ۴ﮒﺓ۴ﮒﮒ؟ﮔﺛﮔ۰ﻛﺝ](05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/case_studies/STRATEGY_FACTORY_IMPLEMENTATION_CASE_STUDY.md)
- [ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﻠﮔﮔ۰ﻛﺝ](05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/case_studies/EVENT_BUS_INTEGRATION_CASE_STUDY.md)

---

## ﻭ **ﮒﻟﻟﭖﮔ?*

### **ﮒﻠ۷ﮔﮔ۰۲**

- [ﻟﮒﺝﮔﺛﮒﺓ۴ﻟﺁﺑﮔﻛﺗ۵](05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/CONSTRUCTION_SPECIFICATION.md)
- [ﻛﭨ۲ﻝ ﻟﺑ۷ﻠﮔ ﮒ](05_IMPLEMENTATION/02_DEVELOPMENT/CODE_QUALITY.md)

### **ﮒ۳ﻠ۷ﻟﭖﮔﭦ**

- [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [The Clean Code Blog](https://blog.cleancoder.com/)

---

## ﻭ **ﮔﺑﮔﺍﻟ؟ﺍﮒﺛ**

| ﮔ۴ﮔ | ﻝﮔ؛ | ﮔﺑﮔﺍﮒﮒ؟ﺗ | ﮔﺑﮔﺍﻛﭦ?|
|------|------|---------|--------|
| 2026-04-02 | v1.0 | ﮒﮒﭨﭦPythonﻛﭨ۲ﻝ ﻟ۶ﻟﮔﻛﺛﺏﮒ؟ﻟﺓ?| ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?|

---

## ﻭ **ﻟﻝﺏﭨﮔﺗﮒﺙ**

**ﮔﮔ۰۲ﻝﭨﺑﮔ۳ﻟ?*: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ? 
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02  
**ﮔﮒﮔﺑﮔ?*: 2026-04-02  
**ﻝﮔ؛**: v1.0
