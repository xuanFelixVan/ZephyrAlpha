# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l6_observability
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.alert_manager
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l6_observability
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-LLM_SECURITY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
L6 Observability Layer — security event logging, alerting, and reporting.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: alpha 参数
#   fields: 参数 alpha（无注解）
#   code: l6_observability.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: threshold 参数
#   fields: 参数 threshold（无注解）
#   code: l6_observability.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FrequencyAnomalyDetector
#   name_en: FrequencyAnomalyDetector
#   intro: Detects frequency-based anomalies using EWMA.
#   desc: Detects frequency-based anomalies using EWMA.；公共方法（定义序）: record, get_baseline；源码 L169-L193
#   inputs: alpha threshold
#   outputs: 返回值
# - id: A2
#   name_zh: ② AlertSender
#   name_en: AlertSender
#   intro: Sends security alerts through configured channels.
#   desc: Sends security alerts through configured channels.；公共方法（定义序）: send_alert, send_critical；源码 L196-L223
#   inputs: config
#   outputs: 返回值
# - id: A3
#   name_zh: ③ ReportGenerator
#   name_en: ReportGenerator
#   intro: Generates security reports.
#   desc: Generates security reports.；公共方法（定义序）: record_event, generate_daily_report, generate_weekly_report, generate,…
#   inputs: config
#   outputs: 返回值
# - id: A4
#   name_zh: ④ PromptwareKillChainTracker
#   name_en: PromptwareKillChainTracker
#   intro: Tracks promptware kill chain progression.
#   desc: Tracks promptware kill chain progression.；公共方法（定义序）: record_stage, track_stage, get_chain_progress；源码 L277-L3…
#   inputs: config
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ SideChannelDefender
#   name_en: SideChannelDefender
#   intro: Defends against side-channel attacks via traffic padding an…
#   desc: Defends against side-channel attacks via traffic padding and audit.；公共方法（定义序）: traffic_padding, side_channel_…
#   inputs: padding_rate config
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ ObservabilityLayer
#   name_en: ObservabilityLayer
#   intro: L6 Observability Layer — aggregates logging, alerting, metr…
#   desc: L6 Observability Layer — aggregates logging, alerting, metrics, reporting.；公共方法（定义序）: log_security_event, det…
#   inputs: config feishu_alerter
#   outputs: 返回值
#   （注：A6 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（10 定义）
#   name_en: public defs
#   intro: FrequencyAnomalyDetector, AlertSender, ReportGenerator, PromptwareKillChainTrac…
#   downstream: zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l6_ob…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.security.llm_defense.llm_security.layers.l6_feishu_alert import LsgFeishuAlerter
    from zephyr.security.llm_defense.llm_security.protocol import SecurityResult

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Severity levels for security alerts."""

    DEBUG = "debug"
    INFO = "info"
    LOW = "low"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(Enum):
    """Types of security events."""

    PROMPT_BLOCKED = "prompt_blocked"
    LEAK_DETECTED = "leak_detected"
    HALLUCINATION_DETECTED = "hallucination_detected"
    INJECTION = "injection"
    DATA_LEAK = "data_leak"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ANOMALY = "anomaly"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM = "system"


class SecurityEvent:
    """Represents a security event."""

    def __init__(
        self,
        event_type: SecurityEventType | str = "",
        severity: AlertSeverity | str = AlertSeverity.LOW,
        message: str = "",
        source: str = "",
        description: str = "",
        timestamp: str | None = None,
    ):
        self.event_type = event_type
        self.severity = severity
        self.message = message
        self.source = source
        self.description = description
        self.timestamp = timestamp or datetime.now(UTC).isoformat()


from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    """Metrics for security dashboard display."""

    total_events: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    total_prompts_processed: int = 0
    prompts_blocked: int = 0


class FrequencyAnomalyDetector:
    """Detects frequency-based anomalies using EWMA."""

    def __init__(self, alpha: float = 0.1, threshold: float = 3.0):
        self.alpha = alpha
        self.threshold = threshold
        self._baseline: float = 0.0
        self._variance: float = 0.0
        self._count: int = 0

    def record(self, value: float) -> dict[str, Any]:
        self._count += 1
        if self._count == 1:
            self._baseline = value
            self._variance = 0.0
            return {"anomaly": False, "baseline": self._baseline, "value": value}
        delta = value - self._baseline
        old_std = (self._variance**0.5) if self._variance > 0 else 1.0
        anomaly = bool(abs(delta) > self.threshold * old_std) and self._count > 5
        self._baseline += self.alpha * delta
        self._variance = (1 - self.alpha) * (self._variance + self.alpha * delta * delta)
        return {"anomaly": anomaly, "baseline": self._baseline, "value": value}

    def get_baseline(self, event_type: str = "") -> float:
        return self._baseline


class AlertSender:
    """Sends security alerts through configured channels."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.recent_alerts: list[dict[str, Any]] = []

    def send_alert(
        self,
        severity: AlertSeverity | str = AlertSeverity.LOW,
        event_type: SecurityEventType | str = "",
        message: str = "",
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        sev_str = severity.value if isinstance(severity, AlertSeverity) else str(severity)
        et_str = event_type.value if isinstance(event_type, SecurityEventType) else str(event_type)
        payload = {
            "severity": sev_str,
            "event_type": et_str,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.recent_alerts.append(payload)
        return payload

    def send_critical(self, message: str) -> dict[str, Any]:
        return self.send_alert(severity=AlertSeverity.CRITICAL, message=message)


class ReportGenerator:
    """Generates security reports."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._events: list[SecurityEvent] = []

    def record_event(self, event: SecurityEvent) -> None:
        self._events.append(event)

    def generate_daily_report(self, date_str: str | None = None) -> dict[str, Any]:
        target = date_str or datetime.now(UTC).strftime("%Y-%m-%d")
        day_events = [e for e in self._events if (e.timestamp or "").startswith(target)]
        breakdown: dict[str, int] = defaultdict(int)
        for ev in day_events:
            et = ev.event_type.value if isinstance(ev.event_type, SecurityEventType) else str(ev.event_type)
            breakdown[et] += 1
        return {"date": target, "total_events": len(day_events), "event_breakdown": dict(breakdown)}

    def generate_weekly_report(self, date_str: str | None = None) -> dict[str, Any]:
        target = date_str or datetime.now(UTC).strftime("%Y-%m-%d")
        try:
            end = datetime.strptime(target, "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            end = datetime.now(UTC)
        start = end - timedelta(days=7)
        week_events = [
            e for e in self._events if start.isoformat() <= (e.timestamp or "") <= (end + timedelta(days=1)).isoformat()
        ]
        daily_totals: dict[str, int] = defaultdict(int)
        for ev in week_events:
            day = (ev.timestamp or "")[:10]
            daily_totals[day] += 1
        breakdown: dict[str, int] = defaultdict(int)
        for ev in week_events:
            et = ev.event_type.value if isinstance(ev.event_type, SecurityEventType) else str(ev.event_type)
            breakdown[et] += 1
        return {
            "week_ending": target,
            "total_events": len(week_events),
            "daily_totals": dict(daily_totals),
            "event_breakdown": dict(breakdown),
        }

    def generate(self, time_range: str = "24h", include_details: bool = True) -> dict[str, Any]:
        return {"report": "generated", "time_range": time_range}

    def generate_summary(self) -> str:
        return f"Security report summary: {len(self._events)} events"


class PromptwareKillChainTracker:
    """Tracks promptware kill chain progression."""

    STAGE_NAMES = {
        0: "Stage_0_Reconnaissance",
        1: "Stage_1_Weaponization",
        2: "Stage_2_Delivery",
        3: "Stage_3_Exploitation",
        4: "Stage_4_Installation",
        5: "Stage_5_CommandAndControl",
        6: "Stage_6_ActionsOnObjectives",
    }

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.trajectory: list[dict[str, Any]] = []

    def record_stage(self, stage: int, description: str = "", details: dict[str, Any] | None = None) -> bool:
        stage_name = self.STAGE_NAMES.get(stage, f"Stage_{stage}_Unknown")
        entry = {
            "stage": stage_name,
            "stage_num": stage,
            "description": description,
            "details": details or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.trajectory.append(entry)
        return True

    def track_stage(self, stage: str, details: dict[str, Any] | None = None) -> bool:
        try:
            num = int(stage)
        except (ValueError, TypeError):
            num = 0
        return self.record_stage(num, str(stage), details)

    def get_chain_progress(self) -> list[dict[str, Any]]:
        return list(self.trajectory)


class SideChannelDefender:
    """Defends against side-channel attacks via traffic padding and audit."""

    def __init__(self, padding_rate: float = 0.1, config: dict[str, Any] | None = None):
        self.padding_rate = padding_rate
        self.config = config or {}
        self.audit_log: list[dict[str, Any]] = []

    def traffic_padding(self, base_value: int) -> int:
        import random

        padding = int(base_value * self.padding_rate) + random.randint(1, max(1, int(base_value * 0.1) + 1))
        return base_value + padding

    def side_channel_audit(self, operation: str, value: float, size: int) -> dict[str, Any]:
        flagged = bool(value > 100.0 or size > 4096)
        entry = {
            "operation": operation,
            "value": value,
            "size": size,
            "flagged": flagged,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.audit_log.append(entry)
        return entry

    def detect_side_channel(self, timing_data: dict[str, Any]) -> bool:
        return False

    def add_noise(self, value: float) -> float:
        return value


class ObservabilityLayer:
    """L6 Observability Layer — aggregates logging, alerting, metrics, reporting."""

    def __init__(self, config=None, feishu_alerter: LsgFeishuAlerter | None = None):
        self.config = config or {}
        self.events: list[SecurityEvent] = []
        self._alert_sender = AlertSender(self.config)
        self._frequency_detector = FrequencyAnomalyDetector()
        self._report_generator = ReportGenerator(self.config)
        # 蓝图 §9 / 09 号文 §4.3 P1-1：高危事件实时推送 Owner（飞书 Webhook）。
        # 默认 None（不接线）；显式注入或 config["feishu_alert_enabled"]=True 时启用。
        # 降级语义由 LsgFeishuAlerter 保证：webhook 不可达/未配置 → 本地持久化不丢事件。
        if feishu_alerter is None and isinstance(self.config, dict) and self.config.get("feishu_alert_enabled"):
            from zephyr.security.llm_defense.llm_security.layers.l6_feishu_alert import LsgFeishuAlerter

            feishu_alerter = LsgFeishuAlerter()
        self._feishu_alerter = feishu_alerter

    def _push_feishu_alert(self, event: SecurityEvent, severity: AlertSeverity | str) -> None:
        """高危事件推飞书告警链路；任何异常不得阻断 L6 主链路。"""
        alerter = self._feishu_alerter
        if alerter is None:
            return
        try:
            et_str = (
                event.event_type.value if isinstance(event.event_type, SecurityEventType) else str(event.event_type)
            )
            sev_str = severity.value if isinstance(severity, AlertSeverity) else str(severity)
            alerter.send_high_risk_alert(
                layer=event.source or "l6_observability",
                rule=et_str,
                result=event.message,
                severity=sev_str,
            )
        except Exception:  # noqa: BLE001 — 告警链路异常不得阻断主链路
            logger.warning("飞书告警推送异常，事件已由告警通道本地兜底", exc_info=True)

    def log_security_event(
        self,
        event_type: SecurityEventType | str = SecurityEventType.SYSTEM,
        message: str = "",
        severity: AlertSeverity | str = AlertSeverity.LOW,
    ) -> SecurityEvent:
        ev = SecurityEvent(event_type=event_type, severity=severity, message=message)
        self.events.append(ev)
        self._report_generator.record_event(ev)
        if severity in (AlertSeverity.CRITICAL, AlertSeverity.HIGH):
            self._alert_sender.send_alert(severity=severity, event_type=event_type, message=message)
            self._push_feishu_alert(ev, severity)
        return ev

    def detect_frequency_anomaly(self, value: float) -> dict[str, Any]:
        return self._frequency_detector.record(value)

    def collect_metrics(self) -> DashboardMetrics:
        total = len(self.events)
        critical = sum(1 for e in self.events if e.severity is AlertSeverity.CRITICAL)
        high = sum(1 for e in self.events if e.severity is AlertSeverity.HIGH)
        medium = sum(1 for e in self.events if e.severity is AlertSeverity.WARNING)
        low = sum(1 for e in self.events if e.severity in (AlertSeverity.LOW, AlertSeverity.INFO, AlertSeverity.DEBUG))
        blocked = sum(
            1
            for e in self.events
            if (
                e.event_type is SecurityEventType.PROMPT_BLOCKED
                if isinstance(e.event_type, SecurityEventType)
                else False
            )
        )
        return DashboardMetrics(
            total_events=total,
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            total_prompts_processed=total,
            prompts_blocked=blocked,
        )

    def generate_daily_report(self, date_str: str | None = None) -> dict[str, Any]:
        return self._report_generator.generate_daily_report(date_str)

    def generate_weekly_report(self, date_str: str | None = None) -> dict[str, Any]:
        return self._report_generator.generate_weekly_report(date_str)

    def validate(self, observability_data: dict[str, Any]) -> bool:
        return True

    def log_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        self.log_security_event(event_type=event_type, message=str(data or {}))

    def check_monitoring(self, component_id: str) -> bool:
        return True

    async def evaluate(self, ctx: dict[str, Any]) -> SecurityResult:
        """Pass-through evaluation for A2A protocol integration."""
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        self.log_security_event(
            event_type=getattr(ctx, "layer_name", "system"),
            message=f"evaluate ctx={getattr(ctx, 'request_id', '')}",
            severity=AlertSeverity.DEBUG,
        )
        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="pass-through",
            layer_name="l6_observability",
            score=1.0,
        )
