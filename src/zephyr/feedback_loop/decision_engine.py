# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.decision_engine
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Feedback Loop Decision Engine
================================

CT-FLE-ORC-001 桥接模块：FLE 异常检测 -> Orchestrator 调度调整

职责
----
1. 接收 FLE 异常检测结果，生成 ScheduleAdjustment 指令
2. 提供 reflect_on_blueprint() 供 trigger_router 蓝图反思回调
3. 通过 FeedbackProtocolAdapter 协议与 Orchestrator 通信（防循环依赖）

架构决策
----
FLE 单向依赖原则（ 不直接 import Orchestrator，
通过 Protocol 适配器 fire-and-forget，防止循环依赖。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from zephyr.feedback_loop.protocols import ActionType, FeedbackProtocolAdapter

__all__ = [
    "AnomalyReport",
    "AnomalySeverity",
    "DecisionEngine",
    "ScheduleAdjustment",
    "reflect_on_blueprint",
]

_logger = logging.getLogger(__name__)


class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class AnomalyReport:
    anomaly_type: str
    severity: AnomalySeverity
    metric_name: str
    current_value: float
    baseline_value: float
    deviation_pct: float
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduleAdjustment:
    action_type: ActionType
    target_task_id: str = ""
    priority_override: str = ""
    throttle_pct: float = 0.0
    reason: str = ""
    anomaly_report: AnomalyReport | None = None


_ANOMALY_TO_ACTION: dict[AnomalySeverity, ActionType] = {
    AnomalySeverity.LOW: ActionType.REPAIR,
    AnomalySeverity.MEDIUM: ActionType.REPAIR,
    AnomalySeverity.HIGH: ActionType.NOTIFY_OWNER,
    AnomalySeverity.CRITICAL: ActionType.NOTIFY_OWNER,
}

_DEVIATION_THRESHOLDS: dict[AnomalySeverity, float] = {
    AnomalySeverity.LOW: 50.0,
    AnomalySeverity.MEDIUM: 100.0,
    AnomalySeverity.HIGH: 200.0,
    AnomalySeverity.CRITICAL: 300.0,
}


class DecisionEngine:
    def __init__(self, adapter: FeedbackProtocolAdapter | None = None) -> None:
        self._adapter = adapter
        self._pending: list[ScheduleAdjustment] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def adapter(self):
        """只读：adapter（Stage 4 公共化）。"""
        return self._adapter

    @adapter.setter
    def adapter(self, value):
        """写入：adapter（Stage 4 公共化）。"""
        self._adapter = value

    @property
    def pending(self) -> list[ScheduleAdjustment]:
        """只读：pending（Stage 4 公共化）。"""
        return self._pending

    @pending.setter
    def pending(self, value):
        """写入：pending（Stage 4 公共化）。"""
        self._pending = value

    def evaluate_anomaly(self, report: AnomalyReport) -> ScheduleAdjustment:
        action_type = _ANOMALY_TO_ACTION.get(report.severity, ActionType.REPAIR)
        throttle = 0.0
        if report.severity in (AnomalySeverity.HIGH, AnomalySeverity.CRITICAL):
            throttle = min(50.0, report.deviation_pct / 10.0)

        adjustment = ScheduleAdjustment(
            action_type=action_type,
            throttle_pct=throttle,
            reason=f"Anomaly detected: {report.anomaly_type} "
            f"deviation={report.deviation_pct:.1f}% "
            f"metric={report.metric_name}",
            anomaly_report=report,
        )

        if self._adapter is not None:
            try:
                self._adapter.dispatch_action(
                    action_type=action_type,
                    payload={
                        "anomaly_type": report.anomaly_type,
                        "severity": report.severity.value,
                        "metric_name": report.metric_name,
                        "deviation_pct": report.deviation_pct,
                        "throttle_pct": throttle,
                        "reason": adjustment.reason,
                    },
                )
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                _logger.warning("FLE->Orc dispatch failed, queuing: %s", exc, exc_info=True)
                self._pending.append(adjustment)
        else:
            self._pending.append(adjustment)

        return adjustment

    def flush_pending(self) -> list[ScheduleAdjustment]:
        if self._adapter is None:
            items = list(self._pending)
            self._pending.clear()
            return items

        flushed: list[ScheduleAdjustment] = []
        remaining: list[ScheduleAdjustment] = []
        for adj in self._pending:
            try:
                self._adapter.dispatch_action(
                    action_type=adj.action_type,
                    payload={"reason": adj.reason},
                )
                flushed.append(adj)
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                remaining.append(adj)
        self._pending = remaining
        return flushed

    @property
    def pending_count(self) -> int:
        return len(self._pending)


def reflect_on_blueprint(payload: dict[str, Any]) -> dict[str, Any]:
    engine = DecisionEngine(adapter=None)
    deviation = payload.get("deviation_pct", 0.0)
    severity = AnomalySeverity.LOW
    for sev in (AnomalySeverity.CRITICAL, AnomalySeverity.HIGH, AnomalySeverity.MEDIUM, AnomalySeverity.LOW):
        if deviation >= _DEVIATION_THRESHOLDS[sev]:
            severity = sev
            break

    report = AnomalyReport(
        anomaly_type=payload.get("anomaly_type", "blueprint_drift"),
        severity=severity,
        metric_name=payload.get("metric_name", "blueprint_health"),
        current_value=payload.get("current_value", 0.0),
        baseline_value=payload.get("baseline_value", 1.0),
        deviation_pct=deviation,
        context=payload,
    )
    adjustment = engine.evaluate_anomaly(report)
    return {
        "status": "reflected",
        "anomaly_severity": report.severity.value,
        "action_type": adjustment.action_type.value,
        "reason": adjustment.reason,
        "throttle_pct": adjustment.throttle_pct,
    }
