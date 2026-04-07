﻿---
module_id: EXEC_EVENT_ENGINE_README_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 说明文档、快速入门
  - 交易执行
  - 系统架构
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?---


# 事件驱动引擎
> **核心职责**: 模块说明和快速入门指南
> **职责边界**: 
> - ✅ 本文档负责：模块说明和快速入门指南相关内容
> - ❌ 本文档不负责：其他模块内容


> 市场事件处理、定时任务、条件触?

**版本**: v1.0
**更新**: 2026-03-29
**Layer**: Layer 4 (执行?
**索引**: 04_EXECUTION/01_EVENT_ENGINE

---

## 1. 事件类型

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


class EventType(Enum):
    """事件类型枚举"""
    MARKET_DATA = "market_data"           # 市场数据事件
    SIGNAL = "signal"                     # 信号事件
    ORDER = "order"                       # 订单事件
    FILL = "fill"                         # 成交事件
    POSITION = "position"                 # 仓位事件
    TIMER = "timer"                       # 定时事件
    RISK = "risk"                         # 风险事件
    CUSTOM = "custom"                     # 自定义事?


@dataclass
class Event:
    """基础事件?""
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
```

---

## 2. 事件处理?

```python
class EventHandler:
    """事件处理器基?""

    def handle(self, event: Event) -> None:
        """处理事件"""
        raise NotImplementedError


class MarketDataHandler(EventHandler):
    """市场数据处理?""

    def handle(self, event: Event) -> None:
        if event.event_type == EventType.MARKET_DATA:
            self._update_market_data(event.data)


class SignalHandler(EventHandler):
    """信号处理?""

    def handle(self, event: Event) -> None:
        if event.event_type == EventType.SIGNAL:
            self._process_signal(event.data)


class OrderHandler(EventHandler):
    """订单处理?""

    def handle(self, event: Event) -> None:
        if event.event_type == EventType.ORDER:
            self._submit_order(event.data)
```

---

## 3. 事件总线

```python
class EventBus:
    """事件总线 - 发布/订阅模式"""

    def __init__(self):
        self.subscribers: Dict[EventType, List[EventHandler]] = {}

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        """发布事件"""
        handlers = self.subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler.handle(event)
            except Exception as e:
                self._log_error(handler, event, e)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """取消订阅"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
```

---

## 4. 定时任务调度?

```python
import schedule
import threading
import time


class TaskScheduler:
    """定时任务调度?""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.running = False
        self.thread = None

    def add_daily_task(self, task_name: str, time_str: str,
                      handler: callable) -> None:
        """添加每日定时任务"""
        schedule.every().day.at(time_str).do(
            lambda: self._execute_task(task_name, handler)
        )

    def add_interval_task(self, task_name: str, interval_seconds: int,
                         handler: callable) -> None:
        """添加间隔任务"""
        schedule.every(interval_seconds).seconds.do(
            lambda: self._execute_task(task_name, handler)
        )

    def start(self) -> None:
        """启动调度?""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.start()

    def stop(self) -> None:
        """停止调度?""
        self.running = False
        schedule.clear()

    def _run_loop(self) -> None:
        """调度循环"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
```

---

## 5. 条件触发机制

```python
class ConditionTrigger:
    """条件触发?""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.conditions: List[Condition] = []

    def add_condition(self, name: str, condition_func: callable,
                     action: callable) -> None:
        """添加触发条件"""
        self.conditions.append(Condition(name, condition_func, action))

    def check_conditions(self, market_data: dict) -> None:
        """检查所有条?""
        for condition in self.conditions:
            if condition.evaluate(market_data):
                condition.execute()


@dataclass
class Condition:
    """触发条件"""
    name: str
    condition_func: callable
    action: callable

    def evaluate(self, data: dict) -> bool:
        """评估条件"""
        return self.condition_func(data)

    def execute(self) -> None:
        """执行动作"""
        self.action()
```

---

## 6. 消息队列管理

```python
import queue
from threading import Lock


class MessageQueue:
    """线程安全消息队列"""

    def __init__(self, maxsize: int = 0):
        self.queue = queue.Queue(maxsize=maxsize)
        self.lock = Lock()

    def put(self, event: Event, block: bool = True) -> None:
        """放入事件"""
        with self.lock:
            self.queue.put(event, block=block)

    def get(self, block: bool = True, timeout: float = None) -> Event:
        """获取事件"""
        return self.queue.get(block=block, timeout=timeout)

    def size(self) -> int:
        """获取队列大小"""
        return self.queue.qsize()


class AsyncEventProcessor:
    """异步事件处理?""

    def __init__(self, event_bus: EventBus, num_workers: int = 4):
        self.event_bus = event_bus
        self.num_workers = num_workers
        self.workers = []

    def start(self) -> None:
        """启动工作线程"""
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self._worker_loop)
            worker.start()
            self.workers.append(worker)

    def _worker_loop(self) -> None:
        """工作线程循环"""
        while True:
            event = self.event_queue.get()
            self.event_bus.publish(event)
```

---

## 7. 层级关系

```
Layer 4 (执行?
    ?上游
Layer 3 (策略? ?策略信号
Layer 5 (监控? ?事件监控
    ?下游
```

---

## 索引

- 父目? [04_EXECUTION/README.md](API_README.md)
- 相关: [04_EXECUTION/03_MONITORING/REAL_TIME_MONITORING.md](04_EXECUTION/03_MONITORING/REAL_TIME_MONITORING.md)
