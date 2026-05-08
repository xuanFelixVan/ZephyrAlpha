"""
Event Bus — 任务卡事件发布/订阅总线。

依据：
    蓝图 MOD-INF-006 §6.13.1 + v0.6.0
    任务卡 TASK-INF-0122
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class EventType(str, Enum):
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
    event_id: str
    event_type: EventType
    task_id: str
    payload: dict[str, Any]
    timestamp_utc: str


EventHandler = Callable[[DomainEvent], None]


class EventBus:

    _instance: "EventBus | None" = None

    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[EventHandler]] = {
            et: [] for et in EventType
        }
        self._event_log: list[DomainEvent] = []

    @classmethod
    def get_instance(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        if event_type in self._subscribers:
            self._subscribers[event_type].append(handler)

    def publish(self, event_type: EventType, task_id: str,
                payload: dict[str, Any] | None = None) -> DomainEvent:
        event = DomainEvent(
            event_id=f"EV-{task_id}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            event_type=event_type,
            task_id=task_id,
            payload=payload or {},
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )

        self._event_log.append(event)

        for handler in self._subscribers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                pass

        return event

    def get_events_for_task(self, task_id: str) -> list[DomainEvent]:
        return [e for e in self._event_log if e.task_id == task_id]

    def get_recent_events(self, limit: int = 50) -> list[DomainEvent]:
        return self._event_log[-limit:]

    def clear(self) -> None:
        self._event_log.clear()
