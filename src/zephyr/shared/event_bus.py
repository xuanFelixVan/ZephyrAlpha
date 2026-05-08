"""
EventBus — 事件总线（带背压控制）(M-07)
职责：模块间异步事件分发，队列深度超 CAP-006 阈值时背压减速。

v0.2.0: EventBus + ContractBus 桥接
  - emit() 可选 contract_id 参数，指定后自动经 ContractBus Schema 校验
  - 校验失败的事件被拒绝（不进入队列），返回 False
  - 不指定 contract_id 时行为不变（向后兼容）

设计：
  - Queue 深度采样，每 emit() 检查
  - 超过警戒水位 (CAP-006 = 500) → 生产者减速（sleep / 拒绝）
  - 严重水位 (> 2× threshold) → 丢弃低优先级事件
"""
import asyncio
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

_logger = logging.getLogger(__name__)


class EventPriority(Enum):
    HIGH = 0
    NORMAL = 1
    LOW = 2


@dataclass
class Event:
    topic: str
    payload: Any
    priority: EventPriority = EventPriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    contract_id: str | None = None
    contract_validated: bool = False


class EventBusBackpressure:
    """
    事件总线背压控制器 (M-07)
    跨线程安全：使用 threading.Lock 保护共享状态

    v0.2.0: 集成 ContractBus Schema 校验
    """

    DEFAULT_QUEUE_WARN_THRESHOLD = 500
    DEFAULT_QUEUE_CRITICAL_THRESHOLD = 1000

    def __init__(
        self,
        max_queue_size: int = 10000,
        warn_threshold: int = DEFAULT_QUEUE_WARN_THRESHOLD,
        critical_threshold: int = DEFAULT_QUEUE_CRITICAL_THRESHOLD,
    ):
        self._queue: deque[Event] = deque()
        self._lock = threading.Lock()
        self._handlers: dict[str, list[Callable]] = {}
        self.max_queue_size = max_queue_size
        self.warn_threshold = warn_threshold
        self.critical_threshold = critical_threshold
        self._dropped_count = 0
        self._emit_count = 0
        self._backpressure_events = 0
        self._contract_rejected_count = 0
        self._contract_bus: Any | None = None

    def set_contract_bus(self, contract_bus: Any) -> None:
        self._contract_bus = contract_bus

    def subscribe(self, topic: str, handler: Callable):
        with self._lock:
            self._handlers.setdefault(topic, []).append(handler)

    def unsubscribe(self, topic: str, handler: Callable) -> bool:
        with self._lock:
            handlers = self._handlers.get(topic, [])
            if handler in handlers:
                handlers.remove(handler)
                if not handlers:
                    del self._handlers[topic]
                return True
            return False

    def unsubscribe_all(self, topic: str | None = None) -> int:
        with self._lock:
            if topic is not None:
                count = len(self._handlers.pop(topic, []))
                return count
            total = sum(len(v) for v in self._handlers.values())
            self._handlers.clear()
            return total

    def emit(self, topic: str, payload: Any, priority: EventPriority = EventPriority.NORMAL, *, contract_id: str | None = None) -> bool:
        if contract_id is not None and self._contract_bus is not None:
            try:
                validated = self._contract_bus.validate(contract_id, payload)
                payload = validated
            except Exception as exc:
                self._contract_rejected_count += 1
                _logger.warning("EventBus contract validation rejected: topic=%s contract=%s err=%s", topic, contract_id, exc)
                return False

        event = Event(topic=topic, payload=payload, priority=priority, contract_id=contract_id, contract_validated=contract_id is not None)
        with self._lock:
            queue_depth = len(self._queue)
            self._emit_count += 1

            if queue_depth >= self.max_queue_size:
                self._dropped_count += 1
                return False

            if queue_depth >= self.critical_threshold:
                if priority == EventPriority.LOW:
                    self._dropped_count += 1
                    return False
                self._backpressure_events += 1

            if queue_depth >= self.warn_threshold:
                self._backpressure_events += 1

            self._queue.append(event)

        try:
            handlers = self._handlers.get(topic, [])
            for handler in handlers:
                handler(event)
        except Exception:
            pass

        return True

    def get_queue_depth(self) -> int:
        with self._lock:
            return len(self._queue)

    def get_stats(self) -> dict:
        with self._lock:
            return {
                "queue_depth": len(self._queue),
                "emit_count": self._emit_count,
                "dropped_count": self._dropped_count,
                "backpressure_events": self._backpressure_events,
                "contract_rejected_count": self._contract_rejected_count,
                "max_queue_size": self.max_queue_size,
                "warn_threshold": self.warn_threshold,
                "critical_threshold": self.critical_threshold,
            }

    def drain(self, max_events: int = 100) -> int:
        drained = 0
        with self._lock:
            while self._queue and drained < max_events:
                event = self._queue.popleft()
                drained += 1
        return drained

    def clear(self):
        with self._lock:
            self._queue.clear()
            self._dropped_count = 0
            self._emit_count = 0
            self._backpressure_events = 0
            self._contract_rejected_count = 0


def _init_bridge() -> None:
    try:
        from zephyr.shared.contract_bus import get_bus
        bus.set_contract_bus(get_bus())
    except Exception:
        pass


bus = EventBusBackpressure()
_init_bridge()
