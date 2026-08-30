# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | CT-FLE-ORC-001
# [MODULE] zephyr.feedback_loop.alert_dispatcher
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.trading.__init__
# [CONSUMERS] zephyr.orchestrator.alert_handler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] severity 必须是 CRITICAL/HIGH/MEDIUM/LOW; 同一 event_id 不重复 dispatch
# [MODIFY-GUARD] CT-FLE-ORC-001 协议变更必须同步更新 orchestrator/alert_handler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] dispatch 失败不抛异常——捕获后返回 DispatchResult.error（RULE-THREE 裁定：原 DispatchError 全库无 raise，死异常类已删除）
# [TESTS] scripts/connect/fle_orc.py --trigger
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
FLE->Orc 告警分派器 — dispatch() 生产者

CT-FLE-ORC-001: FLE 检测异常 -> dispatch AlertEvent -> Orc 创建修复任务。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: event 参数
#   fields: 参数 event，类型注解 AlertEvent
#   code: alert_dispatcher.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DispatchResult
#   name_en: DispatchResult
#   intro: class DispatchResult 源码 L138-L146
#   desc: 公共方法（定义序）: success；源码 L138-L146
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② AlertDispatcher
#   name_en: AlertDispatcher
#   intro: class AlertDispatcher 源码 L149-L180
#   desc: 公共方法（定义序）: dispatch；源码 L149-L180
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ dispatch
#   name_en: dispatch
#   intro: dispatch(event) 源码 L208-L209
#   desc: 源码 L208-L209
#   inputs: event
#   outputs: DispatchResult
# - id: A4
#   name_zh: ④ route_alert
#   name_en: route_alert
#   intro: Route an AlertEvent to appropriate channels based on severi…
#   desc: Route an AlertEvent to appropriate channels based on severity. Thin wrapper around ``zeph…；源码 L212-L228
#   inputs: event
#   outputs: dict
#   （注：A4 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: DispatchResult
#   name_en: DispatchResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.orchestrator.alert_handler
# - id: O2
#   name_zh: dict
#   name_en: dict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.orchestrator.alert_handler
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
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
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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


def route_alert(event: AlertEvent) -> dict:
    """Route an AlertEvent to appropriate channels based on severity.

    Thin wrapper around ``zephyr.feedback_loop.actors.alert_router.route``
    that adapts the AlertEvent to the router's expected interface.

    Returns:
        Dict with ``channels`` (list[str]), ``routed`` (bool), ``reason`` (str).
    """
    from zephyr.feedback_loop.actors.alert_router import route as _route

    decision = _route(event)
    return {
        "channels": list(decision.channels),
        "routed": decision.routed,
        "reason": decision.reason,
    }
