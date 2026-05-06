"""Zero-dependency Observer pattern (subscribe/emit/unsubscribe).

Implements a thread-safe publish-subscribe event bus using only the
Python standard library.  This module is the messaging layer for
DeferredQueue (T-1-09).

Task: T-1-08 | experimental | GLM-5.1
ADR ref: ADR-0037 (pending Opus authoring)
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum, unique
from threading import RLock
from typing import Any


@unique
class EventType(str, Enum):
    FILE_EVENT = "file_event"
    TIME_EVENT = "time_event"
    TASK_EVENT = "task_event"
    MANUAL_EVENT = "manual_event"
    METRIC_EVENT = "metric_event"


EventHandler = Callable[[EventType, dict[str, Any]], None]


class Observer:
    """Thread-safe publish-subscribe event bus.

    Usage::

        bus = Observer()
        bus.subscribe(EventType.FILE_EVENT, my_handler)
        bus.emit(EventType.FILE_EVENT, {"path": "foo.md"})
        bus.unsubscribe(EventType.FILE_EVENT, my_handler)
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._subscribers: dict[EventType, set[EventHandler]] = {et: set() for et in EventType}
        self._once_flags: dict[EventType, set[EventHandler]] = {et: set() for et in EventType}

    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler,
        *,
        once: bool = False,
    ) -> None:
        with self._lock:
            self._subscribers[event_type].add(handler)
            if once:
                self._once_flags[event_type].add(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        with self._lock:
            self._subscribers[event_type].discard(handler)
            self._once_flags[event_type].discard(handler)

    def emit(
        self,
        event_type: EventType,
        payload: dict[str, Any] | None = None,
    ) -> int:
        payload = payload or {}
        with self._lock:
            handlers = list(self._subscribers[event_type])
            once_handlers = set(self._once_flags[event_type])

        called = 0
        for handler in handlers:
            try:
                handler(event_type, payload)
                called += 1
            except Exception:
                pass
            finally:
                if handler in once_handlers:
                    self.unsubscribe(event_type, handler)

        return called

    def subscriber_count(self, event_type: EventType) -> int:
        with self._lock:
            return len(self._subscribers[event_type])

    def clear(self, event_type: EventType | None = None) -> None:
        with self._lock:
            if event_type is None:
                for et in EventType:
                    self._subscribers[et].clear()
                    self._once_flags[et].clear()
            else:
                self._subscribers[event_type].clear()
                self._once_flags[event_type].clear()

    def has_subscriber(self, event_type: EventType, handler: EventHandler) -> bool:
        with self._lock:
            return handler in self._subscribers[event_type]

    def event_types_with_subscribers(self) -> list[EventType]:
        with self._lock:
            return [et for et in EventType if self._subscribers[et]]
