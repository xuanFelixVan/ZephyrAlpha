---
module_id: EXEC_EVENT_BUS_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
responsibility:
  - 风险预算
  - 因子计算
  - 组合优化
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?---


# EventBus 事件总线

> 基础设施�? 模块间异步通信、事件驱动架�?

---

## 1. 设计概述

EventBus是系统的消息中枢，支持模块间的异步通信和事件驱动架构�?

```
EventBus架构
├── 事件发布 (Publisher)
�?  ├── 同步发布
�?  └── 异步发布
├── 事件订阅 (Subscriber)
�?  ├── 精确匹配
�?  ├── 通配符匹�?
�?  └── 模式匹配
├── 事件路由 (Router)
�?  ├── 直接路由
�?  ├── 主题路由
�?  └── 广播路由
├── 消息队列 (Queue)
�?  ├── 内存队列
�?  ├── 持久化队�?
�?  └── 优先级队�?
└── 事件过滤�?(Filter)
    ├── 类型过滤
    ├── 内容过滤
    └── 时效过滤
```

---

## 2. 核心实现

### 2.1 事件定义

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import threading
import queue
import logging
import json


class EventPriority(Enum):
    """事件优先�?""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Event:
    """事件基类"""
    event_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    priority: EventPriority = EventPriority.NORMAL
    headers: Dict[str, Any] = field(default_factory=dict)
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "priority": self.priority.value,
            "headers": self.headers,
            "payload": self.payload,
            "correlation_id": self.correlation_id
        }


class DataEvent(Event):
    """数据事件"""
    pass


class SignalEvent(Event):
    """信号事件"""
    pass


class OrderEvent(Event):
    """订单事件"""
    pass


class RiskEvent(Event):
    """风险事件"""
    pass


class MarketEvent(Event):
    """市场事件"""
    pass
```

### 2.2 EventBus核心

```python
@dataclass
class Subscription:
    """订阅记录"""
    subscriber_id: str
    event_type: str
    handler: Callable
    filter_func: Optional[Callable] = None
    priority: int = 0


class EventBus:
    """事件总线"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        self.subscriptions: Dict[str, List[Subscription]] = {}
        self.event_queue: queue.PriorityQueue = queue.PriorityQueue(maxsize=10000)
        self.running = False

        self.publisher_lock = threading.Lock()
        self.subscription_lock = threading.Lock()

        self.dispatcher_thread: Optional[threading.Thread] = None
        self.stats = {
            "events_published": 0,
            "events_delivered": 0,
            "events_dropped": 0
        }

    def start(self):
        """启动事件总线"""
        if self.running:
            self.logger.warning("EventBus already running")
            return

        self.running = True
        self.dispatcher_thread = threading.Thread(
            target=self._dispatch_loop,
            daemon=True,
            name="EventBus-Dispatcher"
        )
        self.dispatcher_thread.start()
        self.logger.info("EventBus started")

    def stop(self):
        """停止事件总线"""
        self.running = False

        if self.dispatcher_thread:
            self.dispatcher_thread.join(timeout=5)

        self.logger.info("EventBus stopped")

    def subscribe(
        self,
        subscriber_id: str,
        event_type: str,
        handler: Callable,
        filter_func: Callable = None
    ):
        """订阅事件

        参数:
            subscriber_id: 订阅者ID
            event_type: 事件类型 (支持通配�?'*')
            handler: 事件处理函数
            filter_func: 过滤函数
        """
        with self.subscription_lock:
            if event_type not in self.subscriptions:
                self.subscriptions[event_type] = []

            subscription = Subscription(
                subscriber_id=subscriber_id,
                event_type=event_type,
                handler=handler,
                filter_func=filter_func,
                priority=0
            )

            self.subscriptions[event_type].append(subscription)
            self.subscriptions[event_type].sort(key=lambda x: x.priority, reverse=True)

            self.logger.debug(f"Subscribed {subscriber_id} to {event_type}")

    def unsubscribe(self, subscriber_id: str, event_type: str = None):
        """取消订阅"""
        with self.subscription_lock:
            if event_type:
                if event_type in self.subscriptions:
                    self.subscriptions[event_type] = [
                        s for s in self.subscriptions[event_type]
                        if s.subscriber_id != subscriber_id
                    ]
            else:
                for et in self.subscriptions:
                    self.subscriptions[et] = [
                        s for s in self.subscriptions[et]
                        if s.subscriber_id != subscriber_id
                    ]

    def publish(self, event: Event, async_mode: bool = False):
        """发布事件

        参数:
            event: 事件对象
            async_mode: 是否异步发布
        """
        with self.publisher_lock:
            self.stats["events_published"] += 1

        if async_mode:
            self._publish_async(event)
        else:
            self._dispatch_event(event)

    def _publish_async(self, event: Event):
        """异步发布"""
        try:
            self.event_queue.put_nowait((
                self._get_priority_value(event.priority),
                event
            ))
        except queue.Full:
            self.stats["events_dropped"] += 1
            self.logger.warning(f"Event queue full, dropped event: {event.event_type}")

    def _dispatch_loop(self):
        """分发循环"""
        while self.running:
            try:
                priority, event = self.event_queue.get(timeout=1)

                self._dispatch_event(event)

                self.event_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in dispatch loop: {e}")

    def _dispatch_event(self, event: Event):
        """分发事件到订阅�?""
        matching_types = self._match_event_types(event.event_type)

        delivered = 0

        for event_type in matching_types:
            with self.subscription_lock:
                subs = self.subscriptions.get(event_type, []).copy()

            for sub in subs:
                try:
                    if sub.filter_func and not sub.filter_func(event):
                        continue

                    result = sub.handler(event)

                    delivered += 1

                    if asyncio.iscoroutine(result):
                        asyncio.create_task(result)

                except Exception as e:
                    self.logger.error(
                        f"Error delivering event to {sub.subscriber_id}: {e}"
                    )

        self.stats["events_delivered"] += delivered

    def _match_event_types(self, event_type: str) -> List[str]:
        """匹配事件类型"""
        matches = [event_type]

        with self.subscription_lock:
            for subscribed_type in self.subscriptions.keys():
                if subscribed_type == "*":
                    matches.append(subscribed_type)
                elif "*" in subscribed_type:
                    pattern = subscribed_type.replace("*", "")
                    if event_type.startswith(pattern):
                        matches.append(subscribed_type)

        return matches

    def _get_priority_value(self, priority: EventPriority) -> int:
        """获取优先级数�?""
        return priority.value

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "queue_size": self.event_queue.qsize(),
            "subscription_count": sum(
                len(subs) for subs in self.subscriptions.values()
            )
        }
```

---

## 3. 预定义事件类�?

```python
class EventTypes:
    """预定义事件类�?""

    DATA = "data"
    DATA_UPDATE = "data.update"
    DATA_OHLCV = "data.ohlcv"

    SIGNAL = "signal"
    SIGNAL_GENERATED = "signal.generated"
    SIGNAL_UPDATED = "signal.updated"

    ORDER = "order"
    ORDER_SUBMITTED = "order.submitted"
    ORDER_FILLED = "order.filled"
    ORDER_CANCELLED = "order.cancelled"
    ORDER_REJECTED = "order.rejected"

    RISK = "risk"
    RISK_ALERT = "risk.alert"
    RISK_BREACH = "risk.breach"
    RISK_CHECK_PASSED = "risk.check.passed"

    MARKET = "market"
    MARKET_OPEN = "market.open"
    MARKET_CLOSE = "market.close"
    MARKET_HALT = "market.halt"

    PORTFOLIO = "portfolio"
    PORTFOLIO_UPDATE = "portfolio.update"
    PORTFOLIO_REBALANCE = "portfolio.rebalance"

    STRATEGY = "strategy"
    STRATEGY_START = "strategy.start"
    STRATEGY_STOP = "strategy.stop"
    STRATEGY_ERROR = "strategy.error"

    SYSTEM = "system"
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    SYSTEM_ERROR = "system.error"
```

---

## 4. 使用示例

```python
def example_eventbus():
    """EventBus使用示例"""

    bus = EventBus()
    bus.start()

    def on_data_update(event: DataEvent):
        print(f"Data update received: {event.payload}")

    def on_risk_alert(event: RiskEvent):
        print(f"Risk alert: {event.payload}")

    bus.subscribe("strategy_001", EventTypes.DATA_UPDATE, on_data_update)
    bus.subscribe("risk_monitor", EventTypes.RISK_ALERT, on_risk_alert)

    data_event = DataEvent(
        event_type=EventTypes.DATA_UPDATE,
        source="datahub",
        payload={"symbol": "000001.SZ", "close": 10.5}
    )

    bus.publish(data_event)

    risk_event = RiskEvent(
        event_type=EventTypes.RISK_ALERT,
        source="risk_manager",
        priority=EventPriority.HIGH,
        payload={"alert_type": "drawdown", "value": 0.08}
    )

    bus.publish(risk_event, async_mode=True)

    print(bus.get_stats())

    bus.stop()
```

---

## 5. 与现有系统的集成

```python
class EventBusIntegration:
    """EventBus与现有模块集�?""

    def __init__(self, event_bus: EventBus):
        self.bus = event_bus

    def integrate_datahub(self, datahub: DataHub):
        """集成DataHub"""
        original_get_ohlcv = datahub.get_ohlcv

        def wrapped_get_ohlcv(*args, **kwargs):
            result = original_get_ohlcv(*args, **kwargs)

            self.bus.publish(DataEvent(
                event_type=EventTypes.DATA_OHLCV,
                source="datahub",
                payload={"args": args, "kwargs": kwargs, "result": result}
            ))

            return result

        datahub.get_ohlcv = wrapped_get_ohlcv

    def integrate_strategy_engine(self, strategy_engine: StrategyEngine):
        """集成策略引擎"""
        def on_signal(event: SignalEvent):
            print(f"Signal received: {event.payload}")

        self.bus.subscribe(
            "trade_executor",
            EventTypes.SIGNAL_GENERATED,
            on_signal
        )

    def integrate_risk_manager(self, risk_manager: RiskManager):
        """集成风险管理"""
        original_check = risk_manager.check_order

        def wrapped_check(*args, **kwargs):
            result = original_check(*args, **kwargs)

            if not result.allowed:
                self.bus.publish(RiskEvent(
                    event_type=EventTypes.RISK_BREACH,
                    source="risk_manager",
                    priority=EventPriority.HIGH,
                    payload={"order": args, "violations": result.violations}
                ))

            return result

        risk_manager.check_order = wrapped_check
```

---

**版本**: 1.0
**更新**: 2026-03-28
**Layer**: 基础设施�?(横切关注�?
**索引**: BLUEPRINTS.md �?基础设施蓝图
**上游接口**: 所有模�?
**下游接口**: 所有模�?
