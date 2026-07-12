# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | CT-FLE-ORC-001
# [MODULE] zephyr.feedback_loop.alert_dispatcher
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.trading.__init__
# [CONSUMERS] zephyr.orchestrator.alert_handler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] severity 必须是 CRITICAL/HIGH/MEDIUM/LOW; 同一 event_id 不重复 dispatch
# [MODIFY-GUARD] CT-FLE-ORC-001 协议变更必须同步更新 orchestrator/alert_handler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DispatchError 任务创建失败/DB 不可用
# [TESTS] scripts/connect/fle_orc.py --trigger
# [A_module] module_id=MOD-UNK_alert_dispatcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FLE->Orc 告警分派器 — dispatch() 生产者

CT-FLE-ORC-001: FLE 检测异常 -> dispatch AlertEvent -> Orc 创建修复任务。
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, unique
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "AlertCategory",
    "AlertDispatcher",
    "AlertEvent",
    "AlertSeverity",
    "DispatchResult",
    "dispatch",
]


@unique
class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@unique
class AlertCategory(str, Enum):
    METRIC_ANOMALY = "metric_anomaly"
    GATE_FAILURE = "gate_failure"
    SCRIPT_CRITICAL = "script_critical"
    HEALTH_DEGRADED = "health_degraded"
    DLQ_OVERFLOW = "dlq_overflow"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


@dataclass
class AlertEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = "feedback-loop"
    severity: AlertSeverity | str = AlertSeverity.MEDIUM
    category: AlertCategory | str = AlertCategory.METRIC_ANOMALY
    title: str = ""
    detail: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metric_ref: dict[str, Any] | None = None
    affected_systems: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.severity, str):
            self.severity = AlertSeverity(self.severity)
        if isinstance(self.category, str):
            self.category = AlertCategory(self.category)


@dataclass
class DispatchResult:
    dispatched_to: str = "orchestrator"
    task_id: str | None = None
    blocked_tasks: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and self.dispatched_to is not None


class DispatchError(Exception):
    error_code = "ZA-TR-0018"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class AlertDispatcher:
    def dispatch(self, event: AlertEvent) -> DispatchResult:
        try:
            from zephyr.orchestrator.contracts.alert_handler import AlertHandler

            handler = AlertHandler()
            task_card = handler.handle_alert(event)

            blocked: list[str] = []
            if event.severity in (AlertSeverity.CRITICAL,):
                blocked = _block_related_tasks(event)

            task_id = task_card.task_id if task_card else None
            result = DispatchResult(
                dispatched_to="orchestrator",
                task_id=task_id,
                blocked_tasks=blocked,
            )
            logger.info(
                "[FLE-ORC] dispatched %s alert '%s' -> task_id=%s blocked=%d",
                event.severity.value,
                event.title[:60],
                task_id,
                len(blocked),
            )
            return result
        except Exception as exc:
            logger.error("[FLE-ORC] dispatch 失败: %s", exc, exc_info=True)
            return DispatchResult(
                dispatched_to="orchestrator",
                error=str(exc),
            )


def _block_related_tasks(event: AlertEvent) -> list[str]:
    try:
        from zephyr.governance.persistence.sqlite_schema import get_db_connection
    except ImportError:
        return []

    conn = get_db_connection()
    try:
        cat = event.category.value if isinstance(event.category, AlertCategory) else str(event.category)
        cursor = conn.execute(
            "SELECT task_id FROM tasks WHERE tags LIKE ? AND status IN ('PENDING','IN_PROGRESS','READY')",
            (f"%{cat}%",),
        )
        blocked = [r[0] for r in cursor.fetchall()]
        for task_id in blocked:
            conn.execute(
                "UPDATE tasks SET blocked_by = json_insert(COALESCE(blocked_by,'[]'),'$[#]',?) WHERE task_id = ?",
                (event.event_id, task_id),
            )
        conn.commit()
        return blocked
    finally:
        conn.close()


def dispatch(event: AlertEvent) -> DispatchResult:
    return AlertDispatcher().dispatch(event)