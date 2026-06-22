# [A_module] module_id=MOD-INF_event_hooks | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto-fix-engine/blueprint.md | §3

# [MODULE] zephyr.infrastructure.auto_fix_engine.event_hooks

# [INVARIANTS] 钩子MUST不阻塞主流程;异常MUST被捕获不传播

# [MODIFY-GUARD] blueprint.md §3

# [CONSUMERS] engine.py;fix_scheduler.py

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] EventHookError

# [TESTS] tests/auto-fix-engine/test_event_hooks.py

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import FixAction, FixStatus

logger = logging.getLogger(__name__)


class FixEvent(str, Enum):
    FIX_STARTED = "fix_started"
    FIX_COMPLETED = "fix_completed"
    FIX_FAILED = "fix_failed"
    FIX_ESCALATED = "fix_escalated"
    FIX_DEAD_LETTERED = "fix_dead_lettered"
    FIX_APPROVAL_PENDING = "fix_approval_pending"
    FIX_CANCELLED = "fix_cancelled"
    FIX_BUDGET_EXCEEDED = "fix_budget_exceeded"
    FIX_CASCADE_TRIGGERED = "fix_cascade_triggered"
    FIX_STORM_DETECTED = "fix_storm_detected"
    FIX_SECRET_LEAK = "fix_secret_leak"
    FIX_VALIDATION_FAILED = "fix_validation_failed"
    FIX_ROLLBACK = "fix_rollback"
    BATCH_STARTED = "batch_started"
    BATCH_COMPLETED = "batch_completed"


class EventHooks:
    def __init__(self) -> None:
        self._hooks: dict[FixEvent, list[Callable[..., None]]] = {}
        self._event_log: list[dict[str, Any]] = []

    def register(self, event: FixEvent, callback: Callable[..., None]) -> None:
        self._hooks.setdefault(event, []).append(callback)

    def unregister(self, event: FixEvent, callback: Callable[..., None]) -> None:
        if event in self._hooks:
            try:
                self._hooks[event].remove(callback)
            except ValueError:
                pass

    def emit(self, event: FixEvent, action: FixAction | None = None, **kwargs: Any) -> None:
        record = {
            "event": event.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "action_id": action.action_id if action else None,
            "target": action.target if action else None,
            "details": kwargs,
        }
        self._event_log.append(record)
        if len(self._event_log) > 1000:
            self._event_log = self._event_log[-500:]
        callbacks = self._hooks.get(event, [])
        for callback in callbacks:
            try:
                callback(event=event, action=action, **kwargs)
            except Exception as exc:
                logger.error("Event hook error for %s: %s", event.value, exc)

    def emit_for_status(self, action: FixAction) -> None:
        status_to_event = {
            FixStatus.COMPLETED: FixEvent.FIX_COMPLETED,
            FixStatus.FAILED: FixEvent.FIX_FAILED,
            FixStatus.DEAD_LETTER: FixEvent.FIX_DEAD_LETTERED,
            FixStatus.APPROVAL_PENDING: FixEvent.FIX_APPROVAL_PENDING,
            FixStatus.CANCELLED: FixEvent.FIX_CANCELLED,
        }
        event = status_to_event.get(action.status)
        if event:
            self.emit(event, action)
        if action.escalated:
            self.emit(FixEvent.FIX_ESCALATED, action)

    def get_event_log(self, limit: int = 50, event_type: str = "") -> list[dict[str, Any]]:
        log = self._event_log
        if event_type:
            log = [r for r in log if r["event"] == event_type]
        return log[-limit:]

    def clear_hooks(self) -> None:
        self._hooks.clear()

    def clear_log(self) -> None:
        self._event_log.clear()
