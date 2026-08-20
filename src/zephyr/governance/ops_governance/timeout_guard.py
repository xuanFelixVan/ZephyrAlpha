# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.timeout_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: threading.Timer用于一次性超时/延迟执行，非周期时间触发
from __future__ import annotations

import logging
import threading
from typing import Final

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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def timeouts(self) -> dict[TimeoutLevel, float]:
        """只读：timeouts（Stage 4 公共化）。"""
        return self._timeouts

    @timeouts.setter
    def timeouts(self, value):
        """写入：timeouts（Stage 4 公共化）。"""
        self._timeouts = value

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

        # W2 治本: 同步移除 handler，防 _handlers 只写不删内存泄漏
        self._handlers.pop(key, None)

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
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in timeout_guard", exc_info=True)

    def active_count(self) -> int:
        return len(self._active_scopes)

    def recent_events(self, n: int = 10) -> list[TimeoutEvent]:
        return self._events[-n:]

    def clear(self) -> None:
        for timer in self._timers.values():
            timer.cancel()
        self._timers.clear()
        # W2 治本: clear 时同步清空 handlers，防 _handlers 只写不删内存泄漏
        self._handlers.clear()
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
