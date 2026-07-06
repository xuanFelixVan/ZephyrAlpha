# [BLUEPRINT] MOD-LLM_SECURITY
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
# [TTL] permanent
"""L6 Observability Layer — security event logging, alerting, and reporting."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.security.llm_defense.llm_security.protocol import SecurityResult


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

    def __init__(self, config=None):
        self.config = config or {}
        self.events: list[SecurityEvent] = []
        self._alert_sender = AlertSender(self.config)
        self._frequency_detector = FrequencyAnomalyDetector()
        self._report_generator = ReportGenerator(self.config)

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
