---
module_id: 05_IMPLEMENTATION_06_CONSTRUCTION_DOCS_02_IMPLEMENTATION_GUIDES_EVENT_BUS_GUIDE
layer: layer_05
version: 1.0.0
status: Active
responsibility:
  - Event Bus Guide相关业务
created_date: 2026-04-02
last_updated: 2026-04-07
owner: ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ؟ﮔﺛﮔﮒ
applicable_scope: ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮔ۷۰ﮒﮒ؟ﮔﺛ
compliance_level: ﻛﺕﻛﺕﮔﮒ
parent_document: ../README.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?
---

## 设计目标



### 主要目标



1. **功能完整性**: 确保文档内容完整，满足使用需求

2. **易用性**: 提高文档可读性，便于快速理解

3. **可维护性**: 文档结构清晰，便于后续维护

4. **一致性**: 确保文档格式和风格统一



### 质量目标



- 文档完整性: 100%

- 格式规范性: 100%

- 内容准确性: 100%





## ﻭ ﮒ؟ﮔﺛﮔ۵ﻟ۶



### ﻝ؟ﮔ



ﮒ؟ﻝﺍﻛﺕﻛﺕﮔﭦﮔﻝﭦ۶ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﻝﺏﭨﻝﭨﺅﺙﮔﺁﮔﮒﺙﮔ۴ﻛﭦﻛﭨﭘﮒﮒﻙﻟ؟۱ﻠﻟﻝ؟۰ﻝﮒﻛﭦﻛﭨﭘﮔﭦﺁﮔﭦﻙ?



### ﮔﺕﮒﺟﮒﻟﺛ



- **ﻛﭦﻛﭨﭘﮒﮒﺕﻟ؟۱ﻠ**: ﮔﺁﮔﮒ۳ﮒﺁﺗﮒ۳ﻝﻛﭦﻛﭨﭘﮒﮒﺕﻟ؟۱ﻠﮔ۷۰ﮒﺙ

- **ﮒﺙﮔ۴ﻛﭦﻛﭨﭘﮒﮒ**: ﻠ،ﮔ۶ﻟﺛﮒﺙﮔ۴ﻛﭦﻛﭨﭘﮒﮒﮔﭦﮒﭘ

- **ﻛﭦﻛﭨﭘﮔﭦﺁﮔﭦ**: ﮔﺁﮔﻛﭦﻛﭨﭘﮒﮒﺎﻟ؟ﺍﮒﺛﮒﮒﮔ?

- **ﻠﻟﺁﺁﮒ۳ﻝ**: ﮒ؟ﮒﻝﻠﻟﺁﺁﮒ۳ﻝﮒﻠﻟﺁﮔﭦﮒﭘ

- **ﮔ۶ﻟﺛﻝﮔ۶**: ﻛﭦﻛﭨﭘﮒ۳ﻝﮔ۶ﻟﺛﻝﮔ۶



### ﮒﻟﻟﮒ?



- ﻛﺕﻛﺕﻠﮒﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻟﮒﺝ



```
```---
```



## ﻭﺅﺕ?ﮔﭘﮔﻟ؟ﺝﻟ؟۰



### ﮔ۷۰ﮒﻝﭨﮔ



```

src/event_bus/

ﻗﻗﻗ __init__.py                 # ﮔ۷۰ﮒﮒﮒ۶ﮒ?

ﻗﻗﻗ event_bus.py                # EventBusﮔﺕﮒﺟﻝﺎ?

ﻗﻗﻗ event.py                    # Eventﮒﭦﻝﺎﭨ

ﻗﻗﻗ handler.py                  # EventHandlerﮒﭦﻝﺎﭨ

ﻗﻗﻗ subscriber.py               # Subscriberﻝ؟۰ﻝ

ﻗﻗﻗ dispatcher.py               # ﻛﭦﻛﭨﭘﮒﮒﮒ?

ﻗﻗﻗ exceptions.py               # ﻟ۹ﮒ؟ﻛﺗﮒﺙﮒﺕ?

ﻗﻗﻗ tests/                      # ﮒﮒﮔﭖﻟﺁ

    ﻗﻗﻗ test_event_bus.py

    ﻗﻗﻗ test_event.py

    ﻗﻗﻗ test_handler.py

    ﻗﻗﻗ test_dispatcher.py

```



### ﻝﺎﭨﻟ؟ﺝﻟ؟?



#### Event - ﻛﭦﻛﭨﭘﮒﭦﻝﺎﭨ



```python

from dataclasses import dataclass, field

from datetime import datetime

from typing import Dict, Any, Optional

from enum import Enum



class EventType(Enum):

    """ﻛﭦﻛﭨﭘﻝﺎﭨﮒﮔﻛﺕﺝ"""

    MARKET_DATA = "market_data"

    ORDER = "order"

    TRADE = "trade"

    POSITION = "position"

    RISK = "risk"

    SYSTEM = "system"



@dataclass

class Event:

    """ﻛﭦﻛﭨﭘﮒﭦﻝﺎﭨ"""



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

"""ﻟﺛ؛ﮔ۱ﻛﺕﭦﮒﮒ?""

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

"""ﻛﭨﮒﮒﺕﮒﮒﭨﭦﻛﭦﻛﭨ?""

        return cls(

            event_type=EventType(data["event_type"]),

            timestamp=datetime.fromisoformat(data["timestamp"]),

            source=data["source"],

            data=data["data"],

            metadata=data["metadata"],

            event_id=data["event_id"]

        )

```



#### EventHandler - ﻛﭦﻛﭨﭘﮒ۳ﻝﮒ۷ﮒﭦﻝﺎ?



```python

from abc import ABC, abstractmethod

from typing import Optional, List

from .event import Event



class EventHandler(ABC):

    """ﻛﭦﻛﭨﭘﮒ۳ﻝﮒ۷ﮒﭦﻝﺎ?""



    def __init__(self, handler_id: str, event_types: Optional[List[EventType]] = None):

        self.handler_id = handler_id

        self.event_types = event_types or []



    @abstractmethod

    async def handle(self, event: Event) -> Optional[Event]:

        """ﮒ۳ﻝﻛﭦﻛﭨﭘ"""

        pass



    def can_handle(self, event: Event) -> bool:

"""ﮒ۳ﮔﮔﺁﮒ۵ﻟﺛﮒ۳ﻝﻟﺁ۴ﻛﭦﻛﭨﭘ"""

        if not self.event_types:

            return True

        return event.event_type in self.event_types



    def on_error(self, event: Event, error: Exception) -> None:

        """ﻠﻟﺁﺁﮒ۳ﻝ"""

        pass

```



#### EventBus - ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟ



```python

import asyncio

from typing import Dict, List, Optional, Callable

from collections import defaultdict

from .event import Event, EventType

from .handler import EventHandler

from .exceptions import EventBusError



class EventBus:

    """ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟ - ﻝ؟۰ﻝﻛﭦﻛﭨﭘﻝﮒﮒﺕﮒﻟ؟۱ﻠ"""



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

        """ﻟ؟۱ﻠﻛﭦﻛﭨﭘ"""

        if handler not in self._subscribers[event_type]:

            self._subscribers[event_type].append(handler)



    def unsubscribe(

        self,

        event_type: EventType,

        handler: EventHandler

    ) -> None:

        """ﮒﮔﭘﻟ؟۱ﻠ"""

        if handler in self._subscribers[event_type]:

            self._subscribers[event_type].remove(handler)



    async def publish(self, event: Event) -> None:

        """ﮒﮒﺕﻛﭦﻛﭨﭘ"""

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

        """ﮒ۳ﻝﻛﭦﻛﭨﭘ"""

        try:

            result = await handler.handle(event)

            if result:

                await self.publish(result)

        except Exception as e:

            handler.on_error(event, e)

            raise EventBusError(f"Handler {handler.handler_id} failed: {e}")



    def _add_to_history(self, event: Event) -> None:

"""ﮔﺓﭨﮒﮒﺍﮒﮒﺎﻟ؟ﺍﮒﺛ?""

        self._event_history.append(event)



        if len(self._event_history) > self._max_history_size:

            self._event_history.pop(0)



    def get_history(

        self,

        event_type: Optional[EventType] = None,

        limit: int = 100

    ) -> List[Event]:

        """ﻟﺓﮒﮒﮒﺎﻛﭦﻛﭨﭘ"""

        if event_type:

            events = [e for e in self._event_history if e.event_type == event_type]

        else:

            events = self._event_history



        return events[-limit:]



    def clear_history(self) -> None:

        """ﮔﺕﻝ۸ﭦﮒﮒﺎﻟ؟ﺍﮒﺛ"""

        self._event_history.clear()

```



```
```---
```



## ﻭ ﮒ؟ﮔﺛﮔ۴ﻠ۹۳



### Step 1: ﮒﮒﭨﭦﻝ؟ﮒﺛﻝﭨﮔﺅﺙ?0ﮒﻠﺅﺙ?



```bash

# ﮒﮒﭨﭦﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮔ۷۰ﮒﻝ؟ﮒﺛ

mkdir -p src/event_bus/tests



# ﮒﮒﭨﭦﮔﻛﭨﭘ

touch src/event_bus/__init__.py

touch src/event_bus/event_bus.py

touch src/event_bus/event.py

touch src/event_bus/handler.py

touch src/event_bus/subscriber.py

touch src/event_bus/dispatcher.py

touch src/event_bus/exceptions.py

```



### Step 2: ﮒ؟ﻝﺍEventﮒﭦﻝﺎﭨﺅﺙ?ﮒﺍﮔﭘﺅﺙ?



**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:

- [ ] ﮒ؟ﻛﺗﻛﭦﻛﭨﭘﻝﺎﭨﮒﮔﻛﺕﺝ

- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﮔﺍﮔ؟ﻝﭨﮔ

- [ ] ﮒ؟ﻝﺍﮒﭦﮒﮒ?ﮒﮒﭦﮒﮒ

- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ



**ﻠ۹ﮔﭘﮔﮒ**:

- ﻗ?ﻛﭦﻛﭨﭘﻝﺎﭨﮒﮒ؟ﻛﺗﮒ؟ﮔﺑ

- ﻗ?ﮔﺍﮔ؟ﻝﭨﮔﮒﻝ

- ﻗ?ﮒﭦﮒﮒﮔ۲ﻝ۰?

- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%



### Step 3: ﮒ؟ﻝﺍEventHandlerﮒﭦﻝﺎﭨﺅﺙ?ﮒﺍﮔﭘﺅﺙ?



**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:

- [ ] ﮒ؟ﻛﺗﮔﺛﻟﺎ۰ﮔﺗﮔﺏ

- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﻟﺟﮔﭨ۳

- [ ] ﮒ؟ﻝﺍﻠﻟﺁﺁﮒ۳ﻝ

- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ



**ﻠ۹ﮔﭘﮔﮒ**:

- ﻗ?ﮔﺛﻟﺎ۰ﮔﺗﮔﺏﮒ؟ﻛﺗﮒ؟ﮔﺑ

- ﻗ?ﻛﭦﻛﭨﭘﻟﺟﮔﭨ۳ﮔ۲ﻝ۰؟

- ﻗ?ﻠﻟﺁﺁﮒ۳ﻝﮒ؟ﮒ

- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%



### Step 4: ﮒ؟ﻝﺍEventBusﮔﺕﮒﺟﻝﺎﭨﺅﺙ2ﮒﺍﮔﭘﺅﺙ?



**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:

- [ ] ﮒ؟ﻝﺍﮒﻛﺝﮔ۷۰ﮒﺙ

- [ ] ﮒ؟ﻝﺍﻟ؟۱ﻠ/ﮒﮔﭘﻟ؟۱ﻠ

- [ ] ﮒ؟ﻝﺍﮒﺙﮔ۴ﻛﭦﻛﭨﭘﮒﮒﺕ

- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﮒﮒﺎﻟ؟ﺍﮒﺛ

- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ



**ﻠ۹ﮔﭘﮔﮒ**:

- ﻗ?ﮒﻛﺝﮔ۷۰ﮒﺙﮔ۲ﻝ۰؟ﮒ؟ﻝﺍ

- ﻗ?ﻟ؟۱ﻠﮔﭦﮒﭘﮔ۲ﻝ۰؟

- ﻗ?ﮒﺙﮔ۴ﮒﮒﺕﮔ۲ﻝ۰؟

- ﻗ?ﮒﮒﺎﻟ؟ﺍﮒﺛﮒ؟ﮔﺑ

- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%



### Step 5: ﮔ۶ﻟﺛﻛﺙﮒﺅﺙ?ﮒﺍﮔﭘﺅﺙ?



**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:

- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﮔﺗﮒ۳ﻝ?

- [ ] ﮒ؟ﻝﺍﻛﭦﻛﭨﭘﻟﺟﮔﭨ۳ﻛﺙﮒ

- [ ] ﮒ؟ﻝﺍﮒﮒﻛﺙﮒ

- [ ] ﮔ۶ﻟﺛﮔﭖﻟﺁ



**ﻠ۹ﮔﭘﮔﮒ**:

- ﻗ?ﻛﭦﻛﭨﭘﮒ۳ﻝﮒﮒﻠ?> 10000 events/s

- ﻗ?ﮒﮒﮒﻝ۷ < 100MB

- ﻗ?ﮒﭨﭘﻟﺟ < 10ms



### Step 6: ﻠﮔﮔﭖﻟﺁﺅﺙ?ﮒﺍﮔﭘﺅﺙ?



**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:

- [ ] ﮒﮒﭨﭦﮔﭖﻟﺁﻛﭦﻛﭨﭘﮒ۳ﻝﮒ?

- [ ] ﮔﭖﻟﺁﮒ؟ﮔﺑﮔﭖﻝ۷

- [ ] ﮔ۶ﻟﺛﮔﭖﻟﺁ

- [ ] ﮔﮔ۰۲ﻝﺙﮒ



**ﻠ۹ﮔﭘﮔﮒ**:

- ﻗ?ﮒ؟ﮔﺑﮔﭖﻝ۷ﮒﺁﮔ۲ﮒﺕﺕﻟﺟﻟ۰?

- ﻗ?ﮔ۶ﻟﺛﮔﮔﻟﺝﺝﮔ

- ﻗ?ﮔﮔ۰۲ﮒ؟ﮔﺑ



```
```---
```



## ﻗ?ﻠ۹ﮔﭘﮔﮒ



### ﮒﻟﺛﻠ۹ﮔﭘ



| ﮒﻟﺛ | ﻠ۹ﮔﭘﮔﮒ | ﮔﭖﻟﺁﮔﺗﮔﺏ |

|------|---------|---------|

| **ﻛﭦﻛﭨﭘﮒﮒﺕﻟ؟۱ﻠ** | ﻟ؟۱ﻠﻟﮒﺁﮔ۲ﻝ۰؟ﮔ۴ﮔﭘﻛﭦﻛﭨﭘ | ﮒﮒﮔﭖﻟﺁ |

| **ﮒﺙﮔ۴ﻛﭦﻛﭨﭘﮒﮒ** | ﮒﮒﮒﭨﭘﻟﺟ < 10ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |

| **ﻛﭦﻛﭨﭘﮔﭦﺁﮔﭦ** | ﮒﮒﺎﻛﭦﻛﭨﭘﮒﺁﮒﮔ?| ﻠﮔﮔﭖﻟﺁ |

| **ﻠﻟﺁﺁﮒ۳ﻝ** | ﻠﻟﺁﺁﮒﺁﮔ۲ﻝ۰؟ﮒ۳ﻝ?| ﮒﺙﮒﺕﺕﮔﭖﻟﺁ |

| **ﮔ۶ﻟﺛﻝﮔ۶** | ﻝﮔ۶ﮔﮔﮒﺁﻟﺓﮒ?| ﮔ۶ﻟﺛﮔﭖﻟﺁ |



### ﮔ۶ﻟﺛﻠ۹ﮔﭘ



| ﮔﮔ | ﻝ؟ﮔﮒ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |

|------|--------|---------|

| **ﻛﭦﻛﭨﭘﮒﮒﻠ?* | > 10000 events/s | ﮔ۶ﻟﺛﮔﭖﻟﺁ |

| **ﻛﭦﻛﭨﭘﮒﭨﭘﻟﺟ** | < 10ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |

| **ﮒﮒﮒﻝ۷** | < 100MB | ﮒﮒﮒﮔ |

| **CPUﮒﻝ۷** | < 30% | ﮔ۶ﻟﺛﻝﮔ۶ |



### ﻟﺑ۷ﻠﻠ۹ﮔﭘ



| ﮔﮔ | ﻝ؟ﮔﮒ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |

|------|--------|---------|

| **ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?* | > 90% | pytest --cov |

| **ﻛﭨ۲ﻝﮒ۳ﮔﮒﭦ?* | < 10 | radon cc |

| **ﻛﭨ۲ﻝﻠﮒ۳ﻝ?* | < 5% | pylint |

| **ﮔﮔ۰۲ﮒ؟ﮔﺑﮔ?* | 100% | ﮔﮔ۰۲ﮒ؟۰ﮔ۴ |



```
```---
```



## ﻭ۶۹ ﮔﭖﻟﺁﻝﻝ۴



### ﮒﮒﮔﭖﻟﺁ



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



### ﮔ۶ﻟﺛﮔﭖﻟﺁ



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



```
```---
```



## ﻭ ﮔ۶ﻟﺛﻛﺙﮒ



### ﮒﺙﮔ۴ﮔﺗﮒ۳ﻝ?



```python

class EventBus:



    async def publish_batch(self, events: List[Event]) -> None:

        """ﮔﺗﻠﮒﮒﺕﻛﭦﻛﭨﭘ"""

        tasks = [self.publish(event) for event in events]

        await asyncio.gather(*tasks)

```



### ﻛﭦﻛﭨﭘﻟﺟﮔﭨ۳ﻛﺙﮒ



```python

class EventBus:



    def subscribe(

        self,

        event_type: EventType,

        handler: EventHandler,

        filter_func: Optional[Callable[[Event], bool]] = None

    ) -> None:

        """ﻟ؟۱ﻠﻛﭦﻛﭨﭘﺅﺙﮒﺕ۵ﻟﺟﮔﭨ۳ﺅﺙ?""

        self._subscribers[event_type].append({

            "handler": handler,

            "filter": filter_func

        })

```



```
```---
```



## ﻭ۷ ﮒﺕﺕﻟ۶ﻠ؟ﻠ۱



### Q1: ﻛﭦﻛﭨﭘﮒ۳ﻝﻠﭨﮒ۰



**ﻠ؟ﻠ۱**: ﻛﭦﻛﭨﭘﮒ۳ﻝﮒ۷ﮔ۶ﻟ۰ﮔﭘﻠﺑﻟﺟﻠﺟﺅﺙﻠﭨﮒ۰ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟ



**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:

```python

# ﻛﺛﺟﻝ۷ﻟﭘﮔﭘﮔﭦﮒﭘ

async def _handle_event(self, handler: EventHandler, event: Event):

    try:

        await asyncio.wait_for(

            handler.handle(event),

            timeout=5.0

        )

    except asyncio.TimeoutError:

        handler.on_error(event, TimeoutError("Handler timeout"))

```



### Q2: ﮒﮒﮒﻝ۷ﻟﺟﻠ،



**ﻠ؟ﻠ۱**: ﻛﭦﻛﭨﭘﮒﮒﺎﻟ؟ﺍﮒﺛﮒﻝ۷ﻟﺟﮒ۳ﮒﮒ



**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:

```python

# ﻠﮒﭘﮒﮒﺎﻟ؟ﺍﮒﺛﮒ۳۶ﮒﺍ

def _add_to_history(self, event: Event):

    self._event_history.append(event)



    if len(self._event_history) > self._max_history_size:

        self._event_history.pop(0)

```



### Q3: ﻛﭦﻛﭨﭘﻛﺕ۱ﮒ۳ﺎ



**ﻠ؟ﻠ۱**: ﻠ،ﮒﺗﭘﮒﮒﭦﮔﺁﻛﺕﻛﭦﻛﭨﭘﻛﺕ۱ﮒ۳ﺎ



**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:

```python

# ﻛﺛﺟﻝ۷ﻛﭦﻛﭨﭘﻠﮒ

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



```
```---
```



## ﻭ ﮒﻟﻟﭖﮔ?



### ﮒﻠ۷ﮔﮔ۰۲



- ﻛﺕﻛﺕﻠﮒﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻟﮒﺝ



### ﮒ۳ﻠ۷ﻟﭖﮔﭦ



- [Python asyncioﮔﮔ۰۲](https://docs.python.org/3/library/asyncio.html)

- [ﻟ؟ﺝﻟ؟۰ﮔ۷۰ﮒﺙﺅﺙﻟ۶ﮒﺁﻟﮔ۷۰ﮒﺙ](https://refactoring.guru/design-patterns/observer)

- [ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮔﭘﮔ](https://martinfowler.com/articles/201701-event-driven.html)



```
```---
```



## ﻭ ﮔﺑﮔﺍﻟ؟ﺍﮒﺛ



| ﮔ۴ﮔ | ﻝﮔ؛ | ﮔﺑﮔﺍﮒﮒ؟ﺗ | ﮔﺑﮔﺍﻛﭦ?|

|------|------|---------|--------|

| 2026-04-02 | v1.0 | ﮒﮒﭨﭦﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮒ؟ﮔﺛﮔﮒ | ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?|



```
```---
```



## ﻭ ﻟﻝﺏﭨﮔﺗﮒﺙ



**ﮔﮔ۰۲ﻝﭨﺑﮔ۳ﻟ?*: ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?

**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02

**ﮔﮒﮔﺑﮔ?*: 2026-04-02

**ﻝﮔ؛**: v1.0
