# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.event_hooks
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;fix_scheduler.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 钩子MUST不阻塞主流程;异常MUST被捕获不传播
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EventHookError
# [TESTS] tests/auto-fix-engine/test_event_hooks.py
# [A_module] module_id=MOD-INF_event_hooks | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
        # 桥接 fix_completed/fix_failed 到主 EventBus (F15→F5/F30)
        if event in (FixEvent.FIX_COMPLETED, FixEvent.FIX_FAILED):
            try:
                from zephyr.shared.events.event_bus import EventBusBackpressure

                EventBusBackpressure().emit(
                    event.value,
                    payload={
                        "timestamp": record["timestamp"],
                        "source_function": "EventHooks.emit",
                        "severity": "info" if event is FixEvent.FIX_COMPLETED else "error",
                        "detail": f"action_id={action.action_id if action else None} target={action.target if action else None}",
                    },
                )
            except Exception as e:
                logger.warning("suppressed error in event_hooks", exc_info=True)
        callbacks = self._hooks.get(event, [])
        for callback in callbacks:
            try:
                callback(event=event, action=action, **kwargs)
            except Exception as exc:
                logger.error("Event hook error for %s: %s", event.value, exc, exc_info=True)

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


# ── EventBusBackpressure 订阅 (DM-2507-F) ──────────────────────────────

_subscribed = False
_engine_instance: Any = None


def subscribe_eventbus() -> None:
    """订阅 EventBusBackpressure 的 drift_detected / validation_result 事件。

    幂等：重复调用安全。Backpressure 总线不可用时静默跳过。
    供 boot_hooks 统一调用。

    事件:
      - drift_detected: 漂移检测→触发自动修复（若 payload 含 target）
      - validation_result: 验证结果→仅日志记录
    """
    global _subscribed
    if _subscribed:
        return
    try:
        from zephyr.shared.events.event_bus import EventBusBackpressure

        bus = EventBusBackpressure()
        bus.subscribe("drift_detected", _on_drift_detected)
        bus.subscribe("validation_result", _on_validation_result)
        _subscribed = True
        logger.info(
            "AutoFixEngine: subscribed to 2 external events "
            "(drift_detected/validation_result)"
        )
    except Exception as e:
        logger.warning("AutoFixEngine: subscribe_eventbus failed: %s", e, exc_info=True)


def _get_engine() -> Any:
    """懒加载 AutoFixEngine 单例。"""
    global _engine_instance
    if _engine_instance is None:
        try:
            from zephyr.infrastructure.auto_fix_engine.engine import AutoFixEngine

            _engine_instance = AutoFixEngine()
        except Exception as e:
            logger.warning("AutoFixEngine: failed to instantiate engine: %s", e, exc_info=True)
            return None
    return _engine_instance


def _on_drift_detected(payload: object) -> None:
    """drift_detected 事件：漂移检测触发自动修复。轻量handler。

    payload 期望字段: {timestamp, source_function, severity, detail}
    若 detail 中含可识别的 target 路径，调用 engine.fix("drift_fix", target)。
    """
    try:
        data = payload if isinstance(payload, dict) else {}
        detail = data.get("detail", str(payload))
        logger.info("AutoFixEngine: drift_detected event received: %s", detail)

        target = data.get("target") or data.get("file_path") or ""
        if not target:
            logger.info("AutoFixEngine: no target in payload, skip auto-fix dispatch")
            return

        engine = _get_engine()
        if engine is None:
            logger.warning("AutoFixEngine: engine unavailable, skip fix for '%s'", target)
            return

        action = engine.fix("drift_fix", target)
        logger.info(
            "AutoFixEngine: fix dispatched (action_id=%s, status=%s) for target=%s",
            getattr(action, "action_id", None),
            getattr(action, "status", None),
            target,
        )
    except Exception as e:
        logger.error("AutoFixEngine: _on_drift_detected failed: %s", e, exc_info=True)


def _on_validation_result(payload: object) -> None:
    """validation_result 事件：验证结果。轻量handler——仅日志记录。

    payload 期望字段: {timestamp, source_function, severity, detail}
    验证结果不触发修复（避免循环），仅记录用于审计。
    """
    try:
        data = payload if isinstance(payload, dict) else {}
        detail = data.get("detail", str(payload))
        source = data.get("source_function", "unknown")
        severity = data.get("severity", "info")
        logger.info(
            "AutoFixEngine: validation_result event (source=%s, severity=%s): %s",
            source,
            severity,
            detail,
        )
    except Exception as e:
        logger.error("AutoFixEngine: _on_validation_result failed: %s", e, exc_info=True)