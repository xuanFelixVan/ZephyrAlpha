---
module_id: EVENT_BUS_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?
responsibility:
  - 因子计算
  - 交易执行
  - 机器学习
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ؟ﮔﺛﮔﮒ
applicable_scope: ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮔ۷۰ﮒﮒ؟ﮔﺛ
compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ../README.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮒ؟ﮔﺛﮔﮒ

> **ﻝﮔ؛**: v1.0
> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02
> **ﻟﻟﺑ۲**: ﮔﮒﺁﺙﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮔ۷۰ﮒﻝﮒ؟ﮔﺛﮒﻠ۷ﻝﺛﺎ
> **ﮒ؟ﮔﺛﮒ۷ﮔ**: 2ﮒ۷ﺅﺙWeek 1-2ﺅﺙ?
> **ﻛﺙﮒﻝﭦ?*: P0

---

## ﻭ ﮒ؟ﮔﺛﮔ۵ﻟ۶

### ﻝ؟ﮔ 

ﮒ؟ﻝﺍﻛﺕﻛﺕﮔﭦﮔﻝﭦ۶ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﻝﺏﭨﻝﭨﺅﺙﮔﺁﮔﮒﺙﮔ­۴ﻛﭦﻛﭨﭘﮒﮒﻙﻟ؟۱ﻠﻟﻝ؟۰ﻝﮒﻛﭦﻛﭨﭘﮔﭦﺁﮔﭦﻙ?

### ﮔ ﺕﮒﺟﮒﻟﺛ

- **ﻛﭦﻛﭨﭘﮒﮒﺕﻟ؟۱ﻠ**: ﮔﺁﮔﮒ۳ﮒﺁﺗﮒ۳ﻝﻛﭦﻛﭨﭘﮒﮒﺕﻟ؟۱ﻠﮔ۷۰ﮒﺙ
- **ﮒﺙﮔ­۴ﻛﭦﻛﭨﭘﮒﮒ**: ﻠ،ﮔ۶ﻟﺛﮒﺙﮔ­۴ﻛﭦﻛﭨﭘﮒﮒﮔﭦﮒﭘ
- **ﻛﭦﻛﭨﭘﮔﭦﺁﮔﭦ**: ﮔﺁﮔﻛﭦﻛﭨﭘﮒﮒﺎﻟ؟ﺍﮒﺛﮒﮒﮔ?
- **ﻠﻟﺁﺁﮒ۳ﻝ**: ﮒ؟ﮒﻝﻠﻟﺁﺁﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘ
- **ﮔ۶ﻟﺛﻝﮔ۶**: ﻛﭦﻛﭨﭘﮒ۳ﻝﮔ۶ﻟﺛﻝﮔ۶

### ﮒﻟﻟﮒ?

- [ﻛﺕﻛﺕﻠﮒﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻟﮒﺝ](../01_BLUEPRINTS/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md)

---

## ﻭﺅﺕ?ﮔﭘﮔﻟ؟ﺝﻟ؟۰

### ﮔ۷۰ﮒﻝﭨﮔ

```
src/event_bus/
ﻗﻗﻗ __init__.py                 # ﮔ۷۰ﮒﮒﮒ۶ﮒ?
ﻗﻗﻗ event_bus.py                # EventBusﮔ ﺕﮒﺟﻝﺎ?
ﻗﻗﻗ event.py                    # Eventﮒﭦﻝﺎﭨ
ﻗﻗﻗ handler.py                  # EventHandlerﮒﭦﻝﺎﭨ
ﻗﻗﻗ subscriber.py               # Subscriberﻝ؟۰ﻝ
ﻗﻗﻗ dispatcher.py               # ﻛﭦﻛﭨﭘﮒﮒﮒ?
ﻗﻗﻗ exceptions.py               # ﻟ۹ﮒ؟ﻛﺗﮒﺙﮒﺕ?
ﻗﻗﻗ tests/                      # ﮒﮒﮔﭖﻟﺁ
    ﻗﻗﻗ test_event_bus.py
    ﻗﻗﻗ test_event.py
    ﻗﻗﻗ test_handler.py
    ﻗﻗﻗ test_dispatcher.py
```

### ﻝﺎﭨﻟ؟ﺝﻟ؟?

#### Event - ﻛﭦﻛﭨﭘﮒﭦﻝﺎﭨ

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class EventType(Enum):
    """ﻛﭦﻛﭨﭘﻝﺎﭨﮒﮔﻛﺕﺝ"""
    MARKET_DATA = "market_data"
    ORDER = "order"
    TRADE = "trade"
    POSITION = "position"
    RISK = "risk"
    SYSTEM = "system"

@dataclass
class Event:
    """ﻛﭦﻛﭨﭘﮒﭦﻝﺎﭨ"""
    
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    event_id: Optional[str] = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = f"{self.event_type.value}_{self.timestamp.timestamp()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """ﻟﺛ؛ﮔ۱ﻛﺕﭦﮒ­ﮒ?""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """ﻛﭨﮒ­ﮒﺕﮒﮒﭨﭦﻛﭦﻛﭨ?""
        return cls(
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data["source"],
            data=data["data"],
            metadata=data["metadata"],
            event_id=data["event_id"]
        )
```

#### EventHandler - ﻛﭦﻛﭨﭘﮒ۳ﻝﮒ۷ﮒﭦﻝﺎ?

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from .event import Event

class EventHandler(ABC):
    """ﻛﭦﻛﭨﭘﮒ۳ﻝﮒ۷ﮒﭦﻝﺎ?""
    
    def __init__(self, handler_id: str, event_types: Optional[List[EventType]] = None):
        self.handler_id = handler_id
        self.event_types = event_types or []
    
    @abstractmethod
    async def handle(self, event: Event) -> Optional[Event]:
        """ﮒ۳ﻝﻛﭦﻛﭨﭘ"""
        pass
    
    def can_handle(self, event: Event) -> bool:
        """ﮒ۳ﮔ­ﮔﺁﮒ۵ﻟﺛﮒ۳ﻝﻟﺁ۴ﻛﭦﻛﭨﭘ"""
        if not self.event_types:
            return True
        return event.event_type in self.event_types
    
    def on_error(self, event: Event, error: Exception) -> None:
        """ﻠﻟﺁﺁﮒ۳ﻝ"""
        pass
```

#### EventBus - ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟ

```python
import asyncio
from typing import Dict, List, Optional, Callable
from collections import defaultdict
from .event import Event, EventType
from .handler import EventHandler
from .exceptions import EventBusError

class EventBus:
    """ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟ - ﻝ؟۰ﻝﻛﭦﻛﭨﭘﻝﮒﮒﺕﮒﻟ؟۱ﻠ"""
    
    _instance = None
    _subscribers: Dict[EventType, List[EventHandler]] = defaultdict(list)
    _event_history: List[Event] = []
    _max_history_size: int = 10000
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def subscribe(
        self, 
        event_type: EventType, 
        handler: EventHandler
    ) -> None:
        """ﻟ؟۱ﻠﻛﭦﻛﭨﭘ"""
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
    
    def unsubscribe(
        self, 
        event_type: EventType, 
        handler: EventHandler
    ) -> None:
        """ﮒﮔﭘﻟ؟۱ﻠ"""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
    
    async def publish(self, event: Event) -> None:
        """ﮒﮒﺕﻛﭦﻛﭨﭘ"""
        self._add_to_history(event)
        
        handlers = self._subscribers.get(event.event_type, [])
        
        tasks = []
        for handler in handlers:
            if handler.can_handle(event):
                tasks.append(self._handle_event(handler, event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _handle_event(
        self, 
        handler: EventHandler, 
        event: Event
    ) -> None:
        """ﮒ۳ﻝﻛﭦﻛﭨﭘ"""
        try:
            result = await handler.handle(event)
            if result:
                await self.publish(result)
        except Exception as e:
            handler.on_error(event, e)
            raise EventBusError(f"Handler {handler.handler_id} failed: {e}")
    
    def _add_to_history(self, event: Event) -> None:
        """ﮔﺓﭨﮒ ﮒﺍﮒﮒﺎﻟ؟ﺍﮒﺛ?""
        self._event_history.append(event)
        
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
    
    def get_history(
        self, 
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """ﻟﺓﮒﮒﮒﺎﻛﭦﻛﭨﭘ"""
        if event_type:
            events = [e for e in self._event_history if e.event_type == event_type]
        else:
            events = self._event_history
        
        return events[-limit:]
    
    def clear_history(self) -> None:
        """ﮔﺕﻝ۸ﭦﮒﮒﺎﻟ؟ﺍﮒﺛ"""
        self._event_history.clear()
```

---

## ﻭ ﮒ؟ﮔﺛﮔ­۴ﻠ۹۳

### Step 1: ﮒﮒﭨﭦﻝ؟ﮒﺛﻝﭨﮔﺅﺙ?0ﮒﻠﺅﺙ?

```bash
# ﮒﮒﭨﭦﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮔ۷۰ﮒﻝ؟ﮒﺛ
mkdir -p src/event_bus/tests

# ﮒﮒﭨﭦﮔﻛﭨﭘ
touch src/event_bus/__init__.py
touch src/event_bus/event_bus.py
touch src/event_bus/event.py
touch src/event_bus/handler.py
touch src/event_bus/subscriber.py
touch src/event_bus/dispatcher.py
touch src/event_bus/exceptions.py
```

### Step 2: ﮒ؟ﻝﺍEventﮒﭦﻝﺎﭨﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻛﺗﻛﭦﻛﭨﭘﻝﺎﭨﮒﮔﻛﺕﺝ
- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﮔﺍﮔ؟ﻝﭨﮔ
- [ ] ﮒ؟ﻝﺍﮒﭦﮒﮒ?ﮒﮒﭦﮒﮒ
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﻛﭦﻛﭨﭘﻝﺎﭨﮒﮒ؟ﻛﺗﮒ؟ﮔﺑ
- ﻗ?ﮔﺍﮔ؟ﻝﭨﮔﮒﻝ
- ﻗ?ﮒﭦﮒﮒﮔ­۲ﻝ۰?
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 3: ﮒ؟ﻝﺍEventHandlerﮒﭦﻝﺎﭨﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻛﺗﮔﺛﻟﺎ۰ﮔﺗﮔﺏ
- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﻟﺟﮔﭨ۳
- [ ] ﮒ؟ﻝﺍﻠﻟﺁﺁﮒ۳ﻝ
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﮔﺛﻟﺎ۰ﮔﺗﮔﺏﮒ؟ﻛﺗﮒ؟ﮔﺑ
- ﻗ?ﻛﭦﻛﭨﭘﻟﺟﮔﭨ۳ﮔ­۲ﻝ۰؟
- ﻗ?ﻠﻟﺁﺁﮒ۳ﻝﮒ؟ﮒ
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 4: ﮒ؟ﻝﺍEventBusﮔ ﺕﮒﺟﻝﺎﭨﺅﺙ2ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﮒﻛﺝﮔ۷۰ﮒﺙ
- [ ] ﮒ؟ﻝﺍﻟ؟۱ﻠ/ﮒﮔﭘﻟ؟۱ﻠ
- [ ] ﮒ؟ﻝﺍﮒﺙﮔ­۴ﻛﭦﻛﭨﭘﮒﮒﺕ
- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﮒﮒﺎﻟ؟ﺍﮒﺛ
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﮒﻛﺝﮔ۷۰ﮒﺙﮔ­۲ﻝ۰؟ﮒ؟ﻝﺍ
- ﻗ?ﻟ؟۱ﻠﮔﭦﮒﭘﮔ­۲ﻝ۰؟
- ﻗ?ﮒﺙﮔ­۴ﮒﮒﺕﮔ­۲ﻝ۰؟
- ﻗ?ﮒﮒﺎﻟ؟ﺍﮒﺛﮒ؟ﮔﺑ
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 5: ﮔ۶ﻟﺛﻛﺙﮒﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﮔﺗﮒ۳ﻝ?
- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﻟﺟﮔﭨ۳ﻛﺙﮒ
- [ ] ﮒ؟ﻝﺍﮒﮒ­ﻛﺙﮒ
- [ ] ﮔ۶ﻟﺛﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﻛﭦﻛﭨﭘﮒ۳ﻝﮒﮒﻠ?> 10000 events/s
- ﻗ?ﮒﮒ­ﮒ ﻝ۷ < 100MB
- ﻗ?ﮒﭨﭘﻟﺟ < 10ms

### Step 6: ﻠﮔﮔﭖﻟﺁﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒﮒﭨﭦﮔﭖﻟﺁﻛﭦﻛﭨﭘﮒ۳ﻝﮒ?
- [ ] ﮔﭖﻟﺁﮒ؟ﮔﺑﮔﭖﻝ۷
- [ ] ﮔ۶ﻟﺛﮔﭖﻟﺁ
- [ ] ﮔﮔ۰۲ﻝﺙﮒ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﮒ؟ﮔﺑﮔﭖﻝ۷ﮒﺁﮔ­۲ﮒﺕﺕﻟﺟﻟ۰?
- ﻗ?ﮔ۶ﻟﺛﮔﮔ ﻟﺝﺝﮔ 
- ﻗ?ﮔﮔ۰۲ﮒ؟ﮔﺑ

---

## ﻗ?ﻠ۹ﮔﭘﮔ ﮒ

### ﮒﻟﺛﻠ۹ﮔﭘ

| ﮒﻟﺛ | ﻠ۹ﮔﭘﮔ ﮒ | ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|---------|---------|
| **ﻛﭦﻛﭨﭘﮒﮒﺕﻟ؟۱ﻠ** | ﻟ؟۱ﻠﻟﮒﺁﮔ­۲ﻝ۰؟ﮔ۴ﮔﭘﻛﭦﻛﭨﭘ | ﮒﮒﮔﭖﻟﺁ |
| **ﮒﺙﮔ­۴ﻛﭦﻛﭨﭘﮒﮒ** | ﮒﮒﮒﭨﭘﻟﺟ < 10ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﻛﭦﻛﭨﭘﮔﭦﺁﮔﭦ** | ﮒﮒﺎﻛﭦﻛﭨﭘﮒﺁﮒﮔ?| ﻠﮔﮔﭖﻟﺁ |
| **ﻠﻟﺁﺁﮒ۳ﻝ** | ﻠﻟﺁﺁﮒﺁﮔ­۲ﻝ۰؟ﮒ۳ﻝ?| ﮒﺙﮒﺕﺕﮔﭖﻟﺁ |
| **ﮔ۶ﻟﺛﻝﮔ۶** | ﻝﮔ۶ﮔﮔ ﮒﺁﻟﺓﮒ?| ﮔ۶ﻟﺛﮔﭖﻟﺁ |

### ﮔ۶ﻟﺛﻠ۹ﮔﭘ

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|--------|---------|
| **ﻛﭦﻛﭨﭘﮒﮒﻠ?* | > 10000 events/s | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﻛﭦﻛﭨﭘﮒﭨﭘﻟﺟ** | < 10ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﮒﮒ­ﮒ ﻝ۷** | < 100MB | ﮒﮒ­ﮒﮔ |
| **CPUﮒ ﻝ۷** | < 30% | ﮔ۶ﻟﺛﻝﮔ۶ |

### ﻟﺑ۷ﻠﻠ۹ﮔﭘ

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|--------|---------|
| **ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?* | > 90% | pytest --cov |
| **ﻛﭨ۲ﻝ ﮒ۳ﮔﮒﭦ?* | < 10 | radon cc |
| **ﻛﭨ۲ﻝ ﻠﮒ۳ﻝ?* | < 5% | pylint |
| **ﮔﮔ۰۲ﮒ؟ﮔﺑﮔ?* | 100% | ﮔﮔ۰۲ﮒ؟۰ﮔ۴ |

---

## ﻭ۶۹ ﮔﭖﻟﺁﻝ­ﻝ۴

### ﮒﮒﮔﭖﻟﺁ

```python
# tests/test_event_bus.py
import pytest
import asyncio
from event_bus.event_bus import EventBus
from event_bus.event import Event, EventType
from event_bus.handler import EventHandler

class TestEventHandler(EventHandler):
    def __init__(self):
        super().__init__("test_handler", [EventType.MARKET_DATA])
        self.received_events = []
    
    async def handle(self, event: Event):
        self.received_events.append(event)

class TestEventBus:
    
    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        bus = EventBus()
        handler = TestEventHandler()
        
        bus.subscribe(EventType.MARKET_DATA, handler)
        
        event = Event(
            event_type=EventType.MARKET_DATA,
            data={"symbol": "AAPL", "price": 150.0}
        )
        
        await bus.publish(event)
        
        assert len(handler.received_events) == 1
        assert handler.received_events[0].data["symbol"] == "AAPL"
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        bus = EventBus()
        handler = TestEventHandler()
        
        bus.subscribe(EventType.MARKET_DATA, handler)
        bus.unsubscribe(EventType.MARKET_DATA, handler)
        
        event = Event(event_type=EventType.MARKET_DATA)
        await bus.publish(event)
        
        assert len(handler.received_events) == 0
```

### ﮔ۶ﻟﺛﮔﭖﻟﺁ

```python
# tests/test_performance.py
import pytest
import asyncio
import time
from event_bus.event_bus import EventBus
from event_bus.event import Event, EventType

class TestEventBusPerformance:
    
    @pytest.mark.asyncio
    async def test_throughput(self):
        bus = EventBus()
        
        start_time = time.time()
        
        tasks = []
        for i in range(10000):
            event = Event(event_type=EventType.MARKET_DATA)
            tasks.append(bus.publish(event))
        
        await asyncio.gather(*tasks)
        
        elapsed_time = time.time() - start_time
        throughput = 10000 / elapsed_time
        
        assert throughput > 10000
```

---

## ﻭ ﮔ۶ﻟﺛﻛﺙﮒ

### ﮒﺙﮔ­۴ﮔﺗﮒ۳ﻝ?

```python
class EventBus:
    
    async def publish_batch(self, events: List[Event]) -> None:
        """ﮔﺗﻠﮒﮒﺕﻛﭦﻛﭨﭘ"""
        tasks = [self.publish(event) for event in events]
        await asyncio.gather(*tasks)
```

### ﻛﭦﻛﭨﭘﻟﺟﮔﭨ۳ﻛﺙﮒ

```python
class EventBus:
    
    def subscribe(
        self, 
        event_type: EventType, 
        handler: EventHandler,
        filter_func: Optional[Callable[[Event], bool]] = None
    ) -> None:
        """ﻟ؟۱ﻠﻛﭦﻛﭨﭘﺅﺙﮒﺕ۵ﻟﺟﮔﭨ۳ﺅﺙ?""
        self._subscribers[event_type].append({
            "handler": handler,
            "filter": filter_func
        })
```

---

## ﻭ۷ ﮒﺕﺕﻟ۶ﻠ؟ﻠ۱

### Q1: ﻛﭦﻛﭨﭘﮒ۳ﻝﻠﭨﮒ۰

**ﻠ؟ﻠ۱**: ﻛﭦﻛﭨﭘﮒ۳ﻝﮒ۷ﮔ۶ﻟ۰ﮔﭘﻠﺑﻟﺟﻠﺟﺅﺙﻠﭨﮒ۰ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟ

**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:
```python
# ﻛﺛﺟﻝ۷ﻟﭘﮔﭘﮔﭦﮒﭘ
async def _handle_event(self, handler: EventHandler, event: Event):
    try:
        await asyncio.wait_for(
            handler.handle(event),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        handler.on_error(event, TimeoutError("Handler timeout"))
```

### Q2: ﮒﮒ­ﮒ ﻝ۷ﻟﺟﻠ،

**ﻠ؟ﻠ۱**: ﻛﭦﻛﭨﭘﮒﮒﺎﻟ؟ﺍﮒﺛﮒ ﻝ۷ﻟﺟﮒ۳ﮒﮒ­

**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:
```python
# ﻠﮒﭘﮒﮒﺎﻟ؟ﺍﮒﺛﮒ۳۶ﮒﺍ
def _add_to_history(self, event: Event):
    self._event_history.append(event)
    
    if len(self._event_history) > self._max_history_size:
        self._event_history.pop(0)
```

### Q3: ﻛﭦﻛﭨﭘﻛﺕ۱ﮒ۳ﺎ

**ﻠ؟ﻠ۱**: ﻠ،ﮒﺗﭘﮒﮒﭦﮔﺁﻛﺕﻛﭦﻛﭨﭘﻛﺕ۱ﮒ۳ﺎ

**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:
```python
# ﻛﺛﺟﻝ۷ﻛﭦﻛﭨﭘﻠﮒ
class EventBus:
    def __init__(self):
        self._event_queue = asyncio.Queue()
        self._running = False
    
    async def start(self):
        self._running = True
        while self._running:
            event = await self._event_queue.get()
            await self._dispatch_event(event)
```

---

## ﻭ ﮒﻟﻟﭖﮔ?

### ﮒﻠ۷ﮔﮔ۰۲

- [ﻛﺕﻛﺕﻠﮒﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻟﮒﺝ](../01_BLUEPRINTS/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md)

### ﮒ۳ﻠ۷ﻟﭖﮔﭦ

- [Python asyncioﮔﮔ۰۲](https://docs.python.org/3/library/asyncio.html)
- [ﻟ؟ﺝﻟ؟۰ﮔ۷۰ﮒﺙﺅﺙﻟ۶ﮒﺁﻟﮔ۷۰ﮒﺙ](https://refactoring.guru/design-patterns/observer)
- [ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮔﭘﮔ](https://martinfowler.com/articles/201701-event-driven.html)

---

## ﻭ ﮔﺑﮔﺍﻟ؟ﺍﮒﺛ

| ﮔ۴ﮔ | ﻝﮔ؛ | ﮔﺑﮔﺍﮒﮒ؟ﺗ | ﮔﺑﮔﺍﻛﭦ?|
|------|------|---------|--------|
| 2026-04-02 | v1.0 | ﮒﮒﭨﭦﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮒ؟ﮔﺛﮔﮒ | ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?|

---

## ﻭ ﻟﻝﺏﭨﮔﺗﮒﺙ

**ﮔﮔ۰۲ﻝﭨﺑﮔ۳ﻟ?*: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ? 
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02  
**ﮔﮒﮔﺑﮔ?*: 2026-04-02  
**ﻝﮔ؛**: v1.0
