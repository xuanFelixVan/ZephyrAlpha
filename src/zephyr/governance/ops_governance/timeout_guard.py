# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.timeout_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_timeout_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: threading.Timer用于一次性超时/延迟执行，非周期时间触发
from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum


class TimeoutLevel(Enum):
    REQUEST = "request"
    TURN = "turn"
    TASK = "task"
    SESSION = "session"


DEFAULT_TIMEOUTS: Final[dict[TimeoutLevel, float]] = {
    TimeoutLevel.REQUEST: 120.0,
    TimeoutLevel.TURN: 300.0,
    TimeoutLevel.TASK: 3600.0,
    TimeoutLevel.SESSION: 28800.0,
}


@dataclass
class TimeoutEvent:
    level: TimeoutLevel
    scope_id: str
    elapsed: float
    limit: float
    aborted: bool = False
    timestamp: float = field(default_factory=time.time)


class TimeoutGuard:
    def __init__(self, custom_timeouts: dict[TimeoutLevel, float] | None = None):
        self._timeouts: dict[TimeoutLevel, float] = {**DEFAULT_TIMEOUTS}
        if custom_timeouts:
            self._timeouts.update(custom_timeouts)
        self._timers: dict[tuple[TimeoutLevel, str], threading.Timer] = {}
        self._handlers: dict[tuple[TimeoutLevel, str], Callable[[TimeoutEvent], None]] = {}
        self._active_scopes: dict[tuple[TimeoutLevel, str], float] = {}
        self._events: list[TimeoutEvent] = []

    def watch(
        self,
        level: TimeoutLevel,
        scope_id: str,
        on_timeout: Callable[[TimeoutEvent], None] | None = None,
    ) -> None:
        limit = self._timeouts.get(level, 300.0)
        key = (level, scope_id)
        self._active_scopes[key] = time.time()
        if on_timeout:
            self._handlers[key] = on_timeout

        timer = threading.Timer(limit, self._on_timeout, args=[level, scope_id])
        timer.daemon = True
        self._timers[key] = timer
        timer.start()

    def unwatch(self, level: TimeoutLevel, scope_id: str) -> TimeoutEvent | None:
        key = (level, scope_id)
        timer = self._timers.pop(key, None)
        if timer:
            timer.cancel()

        started = self._active_scopes.pop(key, None)
        elapsed = time.time() - started if started else 0.0
        limit = self._timeouts.get(level, 300.0)

        event = TimeoutEvent(
            level=level,
            scope_id=scope_id,
            elapsed=elapsed,
            limit=limit,
            aborted=elapsed >= limit,
        )
        self._events.append(event)
        return event

    def check(self, level: TimeoutLevel, scope_id: str) -> float:
        key = (level, scope_id)
        started = self._active_scopes.get(key)
        if started is None:
            return 0.0
        elapsed = time.time() - started
        limit = self._timeouts.get(level, 300.0)
        return elapsed / limit

    def is_timeout(self, level: TimeoutLevel, scope_id: str) -> bool:
        return self.check(level, scope_id) >= 1.0

    def remaining(self, level: TimeoutLevel, scope_id: str) -> float:
        key = (level, scope_id)
        started = self._active_scopes.get(key)
        if started is None:
            return self._timeouts.get(level, 300.0)
        limit = self._timeouts.get(level, 300.0)
        return max(limit - (time.time() - started), 0.0)

    def _on_timeout(self, level: TimeoutLevel, scope_id: str) -> None:
        key = (level, scope_id)
        started = self._active_scopes.get(key)
        if started is None:
            return
        elapsed = time.time() - started
        limit = self._timeouts.get(level, 300.0)
        event = TimeoutEvent(
            level=level,
            scope_id=scope_id,
            elapsed=elapsed,
            limit=limit,
            aborted=True,
        )
        self._events.append(event)

        handler = self._handlers.get(key)
        if handler:
            try:
                handler(event)
            except Exception as e:
                logger.warning("suppressed error in timeout_guard", exc_info=True)

    def active_count(self) -> int:
        return len(self._active_scopes)

    def recent_events(self, n: int = 10) -> list[TimeoutEvent]:
        return self._events[-n:]

    def clear(self) -> None:
        for timer in self._timers.values():
            timer.cancel()
        self._timers.clear()
        self._active_scopes.clear()
        self._events.clear()

    @staticmethod
    def sleep_or_abort(seconds: float, guard: TimeoutGuard, level: TimeoutLevel, scope_id: str) -> bool:
        deadline = time.time() + seconds
        while time.time() < deadline:
            if guard.is_timeout(level, scope_id):
                return False
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            time.sleep(min(remaining, 0.1))
        return True
