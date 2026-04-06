---
module_id: PYTHON_CODING_BEST_PRACTICES_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?standard_type: ﻝﺙﻝ ﮔﻛﺛﺏﮒ؟ﻟﺓ?applicable_scope: Pythonﻛﭨ۲ﻝ ﻝﺙﮒ
responsibility:
  - 因子计算
  - 回测系统
  - 数据源
compliance_level: ﮒﺙﭦﮒﭘﮔ۶ﻟ۰
parent_document: ../BEST_PRACTICES_INDEX.md
implementation_status: Active---


# Pythonﻛﭨ۲ﻝ ﻟ۶ﻟﮔﻛﺛﺏﮒ؟ﻟﺓ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

> **ﮔﻛﺛﺏﮒ؟ﻟﺓﭖﻝﺙﮒ?*: BP-001  
> **ﻝﮔ؛**: v1.0  
> **ﻠﻝ۷ﮒﭦﮔﺁ**: ﮔﮔPythonﻛﭨ۲ﻝ ﻝﺙﮒ  
> **ﮒﺙﭦﮒﭘﻝﭦ۶ﮒ،**: ﻭﺑ **ﮒﺙﭦﮒﭘﮔ۶ﻟ۰**

---

## ﻭ **ﻠﻝ۷ﮒﭦﮔﺁ**

### **ﻛﺛﮔﭘﻛﺛﺟﻝ۷**

- ﻗ?ﻝﺙﮒﮔﺍﻝPythonﮔ۷۰ﮒ
- ﻗ?ﻠﮔﻝﺍﮔﻛﭨ۲ﻝ 
- ﻗ?ﻛﭨ۲ﻝ ﮒ؟۰ﮔ۴ﮔﭘﮔ۲ﮔ?- ﻗ?ﮒ۱ﻠﮒﻛﺛﮒﺙﮒ?
### **ﻠﻝ۷ﻟﮒﺑ**

- ﮔﮔﻝﻛﭦ۶ﻝﺁﮒ۱ﻛﭨ۲ﻝ ?- ﮔﮔﮔﭖﻟﺁﻛﭨ۲ﻝ ?- ﮔﮔﻟﮔ؛ﻛﭨ۲ﻝ ?- ﮔﮔﻠﻝﺛ؟ﻛﭨ۲ﻝ ?
---

## ﻭﺁ **ﮒ؟ﮔﺛﮔ­۴ﻠ۹۳**

### **1. ﮒﺛﮒﻟ۶ﻟ**

#### **ﮒﻠﮒﺛﮒ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒﺍﮒ+ﻛﺕﮒﻝﭦ?strategy_factory = StrategyFactory()
event_bus = EventBus()
max_position_size = 0.95

# ﻗ?ﻠﻟﺁﺁ - ﮒ۳۶ﻠ۸ﺙﮒﺏﺍﮔﮒﺍﻠ۸ﺙﮒﺏ?strategyFactory = StrategyFactory()
eventBus = EventBus()
MaxPositionSize = 0.95
```

#### **ﮒﺕﺕﻠﮒﺛﮒ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒ۷ﮒ۳۶ﮒ?ﻛﺕﮒﻝﭦ?MAX_POSITION_SIZE = 0.95
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# ﻗ?ﻠﻟﺁﺁ - ﮒﺍﮒﮔﻠ۸ﺙﮒﺏ?max_position_size = 0.95
defaultTimeout = 30
apiBaseUrl = "https://api.example.com"
```

#### **ﮒﺛﮔﺍﮒﺛﮒ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒﺍﮒ+ﻛﺕﮒﻝﭦﺟﺅﺙﮒ۷ﻟﺁﮒﺙﮒ۳?def create_strategy(strategy_type: str) -> Strategy:
    pass

def calculate_position_size(capital: float) -> float:
    pass

def get_event_bus() -> EventBus:
    pass

# ﻗ?ﻠﻟﺁﺁ - ﮒ۳۶ﻠ۸ﺙﮒﺏﺍﮔﮒﻟﺁﮒﺙﮒ۳?def CreateStrategy(strategy_type: str) -> Strategy:
    pass

def PositionSize(capital: float) -> float:
    pass
```

#### **ﻝﺎﭨﮒﺛﮒ?*

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒ۳۶ﻠ۸ﺙﮒﺏ?class StrategyFactory:
    pass

class EventBus:
    pass

class BacktestAdapter:
    pass

# ﻗ?ﻠﻟﺁﺁ - ﮒﺍﮒ+ﻛﺕﮒﻝﭦ?class strategy_factory:
    pass

class event_bus:
    pass
```

---

### **2. ﻛﭨ۲ﻝ ﮔ ﺙﮒﺙ**

#### **ﮒﺁﺙﮒ۴ﻠ۰ﭦﮒﭦ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮔ ﮒﮒﭦ?ﻗ?ﻝ؛؛ﻛﺕﮔﺗﮒﭦ ﻗ?ﮔ؛ﮒﺍﮔ۷۰ﮒ
import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

import pandas as pd
import numpy as np

from strategy.base import BaseStrategy
from event_bus.event import Event

# ﻗ?ﻠﻟﺁﺁ - ﻠ۰ﭦﮒﭦﮔﺓﺓﻛﺗﺎ
from strategy.base import BaseStrategy
import pandas as pd
import os
from typing import Dict
import numpy as np
```

#### **ﻛﭨ۲ﻝ ﻝﺙ۸ﻟﺟ**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - 4ﻛﺕ۹ﻝ۸ﭦﮔ ﺙﻝﺙ۸ﻟﺟ?def calculate_position_size(
    capital: float,
    risk_pct: float,
    entry_price: float,
    stop_loss: float
) -> float:
    risk_amount = capital * risk_pct
    price_diff = entry_price - stop_loss
    position_size = risk_amount / price_diff
    return position_size

# ﻗ?ﻠﻟﺁﺁ - 2ﻛﺕ۹ﻝ۸ﭦﮔ ﺙﮔTab
def calculate_position_size(capital, risk_pct):
  risk_amount = capital * risk_pct
  return risk_amount
```

#### **ﻟ۰ﻠﺟﮒﭦ۵ﻠﮒ?*

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮔﺁﻟ۰ﻛﺕﻟﭘﻟﺟ?00ﮒ­ﻝ؛۵
result = self.strategy_factory.create_strategy(
    strategy_type="moving_average",
    strategy_id="ma_001",
    config={
        "fast_period": 10,
        "slow_period": 30
    }
)

# ﻗ?ﻠﻟﺁﺁ - ﻟ۰ﻟﺟﻠ?result = self.strategy_factory.create_strategy(strategy_type="moving_average", strategy_id="ma_001", config={"fast_period": 10, "slow_period": 30})
```

---

### **3. ﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲**

#### **ﮒﺛﮔﺍﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲**

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﮒ؟ﮔﺑﻝﻝﺎﭨﮒﮔﺏ۷ﻟ۶?def create_strategy(
    strategy_type: str,
    strategy_id: str,
    config: Optional[Dict[str, Any]] = None
) -> BaseStrategy:
    """ﮒﮒﭨﭦﻝ­ﻝ۴ﮒ؟ﻛﺝ
    
    Args:
        strategy_type: ﻝ­ﻝ۴ﻝﺎﭨﮒ
        strategy_id: ﻝ­ﻝ۴ID
        config: ﻝ­ﻝ۴ﻠﻝﺛ؟ﺅﺙﮒﺁﻠﺅﺙ
    
    Returns:
        ﻝ­ﻝ۴ﮒ؟ﻛﺝ
    
    Raises:
        ValueError: ﮒ۵ﮔﻝ­ﻝ۴ﻝﺎﭨﮒﮔ۹ﮔﺏ۷ﮒ?    """
    pass

# ﻗ?ﻠﻟﺁﺁ - ﻝﺙﭦﮒﺍﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲
def create_strategy(strategy_type, strategy_id, config=None):
    pass
```

#### **ﻝﺎﭨﮒﺎﮔ۶ﻝﺎﭨﮒﮔﺏ۷ﻟ۶?*

```python
# ﻗ?ﮔ­۲ﻝ۰؟ - ﻝﺎﭨﮒﺎﮔ۶ﻝﺎﭨﮒﮔﺏ۷ﻟ۶?class StrategyFactory:
    """ﻝ­ﻝ۴ﮒﺓ۴ﮒ"""
    
    def __init__(self):
        self.registry: StrategyRegistry = StrategyRegistry()
        self._instances: Dict[str, BaseStrategy] = {}
        self._lock: Lock = Lock()

# ﻗ?ﻠﻟﺁﺁ - ﻝﺙﭦﮒﺍﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲
class StrategyFactory:
    def __init__(self):
        self.registry = StrategyRegistry()
        self._instances = {}
        self._lock = Lock()
```

---

### **4. ﮔﮔ۰۲ﮒ­ﻝ؛۵ﻛﺕ?*

#### **ﮔ۷۰ﮒﮔﮔ۰۲ﮒ­ﻝ؛۵ﻛﺕ?*

```python
"""
ﻝ­ﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ - ﻝ؟۰ﻝﻝ­ﻝ۴ﻝﮒﮒﭨﭦﮒﻝﮒﺛﮒ۷ﮔ

ﻝﮔ؛: v1.0
ﮒﮒﭨﭦﮔ۴ﮔ: 2026-04-02
ﻛﺛﻟ? ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?
ﻛﺕﭨﻟ۵ﻝﭨﻛﭨﭘ:
- BaseStrategy: ﻝ­ﻝ۴ﮒﭦﻝﺎﭨ
- StrategyFactory: ﻝ­ﻝ۴ﮒﺓ۴ﮒ
- StrategyRegistry: ﻝ­ﻝ۴ﮔﺏ۷ﮒﻟ۰?- StrategyLoader: ﻝ­ﻝ۴ﮒ ﻟﺛﺛﮒ?
ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ:
    >>> factory = StrategyFactory()
    >>> strategy = factory.create_strategy("moving_average", "ma_001")
"""
```

#### **ﻝﺎﭨﮔﮔ۰۲ﮒ­ﻝ؛۵ﻛﺕﺎ**

```python
class StrategyFactory:
    """ﻝ­ﻝ۴ﮒﺓ۴ﮒ - ﮒﮒﭨﭦﮒﻝ؟۰ﻝﻝ­ﻝ۴ﮒ؟ﻛﺝ?    
    ﻝ­ﻝ۴ﮒﺓ۴ﮒﻟﺑﻟﺑ۲ﮒﮒﭨﭦﻝ­ﻝ۴ﮒ؟ﻛﺝﻙﻝ؟۰ﻝﻝ­ﻝ۴ﻝﮒﺛﮒ۷ﮔﻙﻝﺙﮒ­ﻝ­ﻝ۴ﮒ؟ﻛﺝﻙ?    ﻛﺛﺟﻝ۷ﮒﺓ۴ﮒﮔ۷۰ﮒﺙﻝ۰؟ﻛﺟﻝ­ﻝ۴ﮒﮒﭨﭦﻝﻛﺕﻟﺑﮔ۶ﮒﮒﺁﮔ۸ﮒﺎﮔ۶ﻙ?    
    Attributes:
        registry: ﻝ­ﻝ۴ﮔﺏ۷ﮒﻟ۰?        _instances: ﻝ­ﻝ۴ﮒ؟ﻛﺝﻝﺙﮒ­
        _lock: ﻝﭦﺟﻝ۷ﻠ?    
    Example:
        >>> factory = StrategyFactory()
        >>> strategy = factory.create_strategy("moving_average", "ma_001")
        >>> print(strategy.strategy_id)
        'ma_001'
    """
```

#### **ﮒﺛﮔﺍﮔﮔ۰۲ﮒ­ﻝ؛۵ﻛﺕ?*

```python
def create_strategy(
    self,
    strategy_type: str,
    strategy_id: str,
    config: Optional[Dict[str, Any]] = None
) -> BaseStrategy:
    """ﮒﮒﭨﭦﻝ­ﻝ۴ﮒ؟ﻛﺝ
    
    ﮔ ﺗﮔ؟ﻝ­ﻝ۴ﻝﺎﭨﮒﮒﮒﭨﭦﻝ­ﻝ۴ﮒ؟ﻛﺝﺅﺙﮒﺗﭘﮒﺍﮒﭘﻝﺙﮒ­ﮒﺍﮒ؟ﻛﺝﮒ­ﮒﺕﻛﺕ­ﻙ?    ﮒ۵ﮔﻝ­ﻝ۴IDﮒﺓﺎﮒ­ﮒ۷ﺅﺙﮒﺍﻟﺟﮒﻝﺙﮒ­ﻝﮒ؟ﻛﺝﻙ?    
    Args:
        strategy_type: ﻝ­ﻝ۴ﻝﺎﭨﮒﮒﻝ۶ﺍﺅﺙﮒﺟﻠ۰ﭨﮒ۷ﮔﺏ۷ﮒﻟ۰۷ﻛﺕ­ﮔﺏ۷ﮒﺅﺙ?        strategy_id: ﻝ­ﻝ۴ﮒ؟ﻛﺝﻝﮒﺁﻛﺕﮔ ﻟﺁﻝ؛?        config: ﻝ­ﻝ۴ﻠﻝﺛ؟ﮒ­ﮒﺕﺅﺙﮒﺁﻠﺅﺙ
    
    Returns:
        ﮒﮒﭨﭦﻝﻝ­ﻝ۴ﮒ؟ﻛﺝ?    
    Raises:
        ValueError: ﮒ۵ﮔﻝ­ﻝ۴ﻝﺎﭨﮒﮔ۹ﮔﺏ۷ﮒ?        KeyError: ﮒ۵ﮔﻝ­ﻝ۴ﻝﺎﭨﮒﻛﺕﮒ­ﮒ?    
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

## ﻗ ﺅﺕ **ﮔﺏ۷ﮔﻛﭦﻠ۰ﺗ**

### **1. ﻠﺟﮒﻝﻝﺙﻝ ﻠ۲ﮔ ?*

```python
# ﻗ?ﻠﺟﮒﻛﺛﺟﻝ۷ﮒ۷ﮒﺎﮒﻠ
strategy_factory = None

def get_strategy_factory():
    global strategy_factory
    if strategy_factory is None:
        strategy_factory = StrategyFactory()
    return strategy_factory

# ﻗ?ﻛﺛﺟﻝ۷ﮒﻛﺝﮔ۷۰ﮒﺙﮔﻛﺝﻟﭖﮔﺏ۷ﮒ?class StrategyFactory:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### **2. ﻠﺟﮒﻠ­ﮔﺏﮔﺍﮒ­**

```python
# ﻗ?ﻠ­ﮔﺏﮔﺍﮒ­
if position_size > 0.95:
    pass

# ﻗ?ﻛﺛﺟﻝ۷ﮒﺕﺕﻠ
MAX_POSITION_SIZE = 0.95

if position_size > MAX_POSITION_SIZE:
    pass
```

### **3. ﻠﺟﮒﮔﺓﺎﮒﺎﮒﭖﮒ۴**

```python
# ﻗ?ﮔﺓﺎﮒﺎﮒﭖﮒ۴
def process_data(data):
    if data is not None:
        if 'items' in data:
            for item in data['items']:
                if item['type'] == 'stock':
                    # ﮒ۳ﻝﻠﭨﻟﺝ
                    pass

# ﻗ?ﮔﮒﻟﺟﮒ
def process_data(data):
    if data is None:
        return
    
    if 'items' not in data:
        return
    
    for item in data['items']:
        if item['type'] != 'stock':
            continue
        # ﮒ۳ﻝﻠﭨﻟﺝ
```

---

## ﻭ **ﮔﮔﻟﺁﻛﺙﺍ**

### **ﻛﭨ۲ﻝ ﻟﺑ۷ﻠﮔﮔ **

| ﮔﮔ  | ﻝ؟ﮔ  | ﮒ؟ﻠ | ﻝﭘﮔ?|
|------|------|------|------|
| ﻛﭨ۲ﻝ ﮒﺁﻟﺁﭨﮔ?| ﻗ?0ﮒ?| 95ﮒ?| ﻗ?|
| ﻛﭨ۲ﻝ ﮒ۳ﮔﮒﭦ?| ﻗ?0 | 8 | ﻗ?|
| ﮔﮔ۰۲ﻟ۵ﻝﻝ?| ﻗ?0% | 90% | ﻗ?|
| ﻝﺎﭨﮒﮔﺏ۷ﻟ۶۲ﻟ۵ﻝﻝ?| ﻗ?0% | 95% | ﻗ?|

### **ﮒﺙﮒﮔﻝﮔﮔ ?*

| ﮔﮔ  | ﮔﺗﻟﺟﮒ?| ﮔﺗﻟﺟﮒ?| ﮔﮒ |
|------|--------|--------|------|
| ﻛﭨ۲ﻝ ﮒ؟۰ﮔ۴ﮔﭘﻠﺑ | 2ﮒﺍﮔﭘ | 1ﮒﺍﮔﭘ | 50% |
| Bugﻛﺟ؟ﮒ۳ﮔﭘﻠﺑ | 4ﮒﺍﮔﭘ | 2ﮒﺍﮔﭘ | 50% |
| ﮔﺍﻛﭦﭦﻛﺕﮔﮔﭘﻠﺑ | 2ﮒ?| 1ﮒ?| 50% |

---

## ﻭ **ﻝﺕﮒﺏﮔ۰ﻛﺝ**

- [ﻝ­ﻝ۴ﮒﺓ۴ﮒﮒ؟ﮔﺛﮔ۰ﻛﺝ](../case_studies/STRATEGY_FACTORY_IMPLEMENTATION_CASE_STUDY.md)
- [ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﻠﮔﮔ۰ﻛﺝ](../case_studies/EVENT_BUS_INTEGRATION_CASE_STUDY.md)

---

## ﻭ **ﮒﻟﻟﭖﮔ?*

### **ﮒﻠ۷ﮔﮔ۰۲**

- [ﻟﮒﺝﮔﺛﮒﺓ۴ﻟﺁﺑﮔﻛﺗ۵](../../../06_CONSTRUCTION_DOCS/CONSTRUCTION_SPECIFICATION.md)
- [ﻛﭨ۲ﻝ ﻟﺑ۷ﻠﮔ ﮒ](../../../02_DEVELOPMENT/CODE_QUALITY.md)

### **ﮒ۳ﻠ۷ﻟﭖﮔﭦ**

- [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [The Clean Code Blog](https://blog.cleancoder.com/)

---

## ﻭ **ﮔﺑﮔﺍﻟ؟ﺍﮒﺛ**

| ﮔ۴ﮔ | ﻝﮔ؛ | ﮔﺑﮔﺍﮒﮒ؟ﺗ | ﮔﺑﮔﺍﻛﭦ?|
|------|------|---------|--------|
| 2026-04-02 | v1.0 | ﮒﮒﭨﭦPythonﻛﭨ۲ﻝ ﻟ۶ﻟﮔﻛﺛﺏﮒ؟ﻟﺓ?| ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?|

---

## ﻭ **ﻟﻝﺏﭨﮔﺗﮒﺙ**

**ﮔﮔ۰۲ﻝﭨﺑﮔ۳ﻟ?*: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ? 
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02  
**ﮔﮒﮔﺑﮔ?*: 2026-04-02  
**ﻝﮔ؛**: v1.0
