# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.event_bus
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_event_bus_core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
EventBus — 事件总线（带背压控制）(M-07)
职责：模块间异步事件分发，队列深度超 CAP-006 阈值时背压减速。

v0.3.0: SRC-0036 — 合并 core/events/event_bus.py 的 EventType/DomainEvent/EventBus
  - EventType 枚举（任务生命周期 + Gate + Scope Drift）
  - DomainEvent dataclass（领域事件）
  - EventBus 单例（任务事件发布/订阅，兼容 event_reactor/hook_dispatcher）

v0.2.0: EventBus + ContractBus 桥接
  - emit() 可选 contract_id 参数，指定后自动经 ContractBus Schema 校验
  - 校验失败的事件被拒绝（不进入队列），返回 False
  - 不指定 contract_id 时行为不变（向后兼容）

设计：
  - Queue 深度采样，每 emit() 检查
  - 超过警戒水位 (CAP-006 = 500) -> 生产者减速（sleep / 拒绝）
  - 严重水位 (> 2× threshold) -> 丢弃低优先级事件
"""

import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

_logger = logging.getLogger(__name__)


# ── SRC-0036: 从 core/events/event_bus.py 合并的符号 ──────────────────────


# class-name-alias: EventBus truth source (M-07), distinct from observer.py's file-watcher EventType (FILE_EVENT/TIME_EVENT)
class EventType(str, Enum):
    """任务生命周期事件类型（MOD-TASK_SYSTEM §6.13.1）"""

    TASK_CREATED = "task.created"
    TASK_LOCKED = "task.locked"
    TASK_ASSIGNED = "task.assigned"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_ROLLBACK = "task.rollback"
    GATE_PASSED = "gate.passed"
    GATE_FAILED = "gate.failed"
    SCOPE_DRIFT = "scope.drift"
    DEPENDENCY_RESOLVED = "dependency.resolved"


@dataclass
class DomainEvent:
    """领域事件（任务相关）"""

    event_id: str
    event_type: EventType
    task_id: str
    payload: dict[str, Any]
    timestamp_utc: str


EventHandler = Callable[[DomainEvent], None]


class EventBus:
    """
    任务事件发布/订阅总线（单例模式）
    与 EventBusBackpressure 互补：EventBus 面向领域事件，EventBusBackpressure 面向系统事件

    v0.3.0: 从 core/events/event_bus.py 合并（SRC-0036）
    """

    _instance: "EventBus | None" = None

    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[EventHandler]] = {et: [] for et in EventType}
        self._event_log: list[DomainEvent] = []
        self._lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        with self._lock:
            if event_type in self._subscribers:
                self._subscribers[event_type].append(handler)

    def publish(self, event_type: EventType, task_id: str, payload: dict[str, Any] | None = None) -> DomainEvent:
        event = DomainEvent(
            event_id=f"EV-{task_id}-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            event_type=event_type,
            task_id=task_id,
            payload=payload or {},
            timestamp_utc=datetime.now(UTC).isoformat(),
        )

        with self._lock:
            self._event_log.append(event)
            handlers = list(self._subscribers.get(event_type, []))

        for handler in handlers:
            try:
                handler(event)
            except Exception:
                _logger.debug(
                    "EventBus handler error event_type=%s task_id=%s",
                    event_type,
                    task_id,
                    exc_info=True,
                )

        return event

    def get_events_for_task(self, task_id: str) -> list[DomainEvent]:
        with self._lock:
            return [e for e in self._event_log if e.task_id == task_id]

    def get_recent_events(self, limit: int = 50) -> list[DomainEvent]:
        with self._lock:
            return self._event_log[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._event_log.clear()


# ── 原有符号（v0.1.0–v0.2.0）──────────────────────────────────────────


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
        self._handlers: dict[str, list[Callable[[Event], None]]] = {}
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

    def subscribe(self, topic: str, handler: Callable[[Event], None]):
        with self._lock:
            self._handlers.setdefault(topic, []).append(handler)

    def unsubscribe(self, topic: str, handler: Callable[[Event], None]) -> bool:
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

    def emit(
        self,
        topic: str,
        payload: Any,
        priority: EventPriority = EventPriority.NORMAL,
        *,
        contract_id: str | None = None,
    ) -> bool:
        if contract_id is not None and self._contract_bus is not None:
            try:
                validated = self._contract_bus.validate(contract_id, payload)
                payload = validated
            except Exception as exc:
                self._contract_rejected_count += 1
                _logger.warning(
                    "EventBus contract validation rejected: topic=%s contract=%s err=%s", topic, contract_id, exc
                )
                return False

        event = Event(
            topic=topic,
            payload=payload,
            priority=priority,
            contract_id=contract_id,
            contract_validated=contract_id is not None,
        )
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
            _logger.debug(
                "EventBusBackpressure handler error topic=%s",
                topic,
                exc_info=True,
            )

        return True

    def get_queue_depth(self) -> int:
        with self._lock:
            return len(self._queue)

    def get_stats(self) -> dict[str, int]:
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
        _logger.debug("contract_bus bridge init failed", exc_info=True)


bus = EventBusBackpressure()
_init_bridge()
