import json
import math
import random
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from zephyr.audit_trail.bridge import write_to_core
from zephyr.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)


class SecurityEventType(str, Enum):
    PROMPT_BLOCKED = "prompt_blocked"
    LEAK_DETECTED = "leak_detected"
    SENSITIVE_REDACTED = "sensitive_redacted"
    HALLUCINATION_DETECTED = "hallucination_detected"
    AGENT_PERMISSION_DENIED = "agent_permission_denied"
    HITL_APPROVAL = "hitl_approval"
    BUDGET_EXCEEDED = "budget_exceeded"
    CIRCUIT_BREAKER_TRIPPED = "circuit_breaker_tripped"
    ANOMALY_DETECTED = "anomaly_detected"
    PROMPTWARE_DETECTED = "promptware_detected"
    SIDE_CHANNEL_DETECTED = "side_channel_detected"


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class SecurityEvent(BaseModel):
    event_type: SecurityEventType
    severity: AlertSeverity = AlertSeverity.INFO
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    module: str = "llm_security"
    message: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)
    request_id: str = ""
    session_id: str = ""


class DashboardMetrics(BaseModel):
    total_prompts_processed: int = 0
    prompts_blocked: int = 0
    prompts_flagged: int = 0
    leaks_detected: int = 0
    hallucinations_detected: int = 0
    agent_permissions_denied: int = 0
    circuit_breaker_trips: int = 0
    budget_exceeded_count: int = 0
    anomaly_events: int = 0
    promptware_detections: int = 0
    side_channel_events: int = 0
    avg_latency_ms: float = 0.0
    peak_events_per_minute: int = 0
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FrequencyAnomalyDetector:
    """EMA基线 + 2σ 阈值频率异常检测."""

    def __init__(self, alpha: float = 0.1, window_size: int = 60):
        self._alpha = alpha
        self._window_size = window_size
        self._lock = threading.Lock()
        self._event_counts: deque = deque(maxlen=window_size)
        self._ema: float = 0.0
        self._var: float = 0.0
        self._initialized: bool = False

    def record(self, count: int) -> Dict[str, Any]:
        with self._lock:
            self._event_counts.append(count)
            if not self._initialized:
                self._ema = float(count)
                self._var = 0.0
                self._initialized = True
                return {"anomaly": False, "ema": self._ema, "sigma": 0.0, "value": count}

            old_ema = self._ema
            diff = count - old_ema
            self._var = (1 - self._alpha) * (self._var + self._alpha * diff * diff)
            sigma = math.sqrt(max(self._var, 1e-9))
            anomaly = abs(diff) > 2.0 * sigma
            self._ema = self._alpha * count + (1 - self._alpha) * old_ema
            return {
                "anomaly": anomaly,
                "ema": round(self._ema, 3),
                "sigma": round(sigma, 3),
                "value": count,
                "threshold": round(2.0 * sigma, 3),
            }

    def reset(self) -> None:
        with self._lock:
            self._event_counts.clear()
            self._ema = 0.0
            self._var = 0.0
            self._initialized = False


class AlertSender:
    """Webhook 告警发送器."""

    def __init__(self, webhook_url: str = ""):
        self._webhook_url = webhook_url
        self._sent_alerts: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def send_alert(
        self,
        severity: AlertSeverity,
        event_type: SecurityEventType,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "severity": severity.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "module": "llm_security",
            "event_type": event_type.value,
            "message": message,
        }
        if details:
            payload["details"] = details

        with self._lock:
            self._sent_alerts.append(payload)
            if len(self._sent_alerts) > 1000:
                self._sent_alerts = self._sent_alerts[-500:]

        return payload

    @property
    def recent_alerts(self) -> List[Dict[str, Any]]:
        return list(self._sent_alerts)


class ReportGenerator:
    """日报/周报自动生成器."""

    def __init__(self):
        self._daily_events: Dict[str, List[SecurityEvent]] = defaultdict(list)
        self._lock = threading.Lock()

    def record_event(self, event: SecurityEvent) -> None:
        day_key = event.timestamp[:10]
        with self._lock:
            self._daily_events[day_key].append(event)

    def generate_daily_report(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        date_str = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        events = self._daily_events.get(date_str, [])
        type_counts: Dict[str, int] = defaultdict(int)
        severity_counts: Dict[str, int] = defaultdict(int)
        for ev in events:
            type_counts[ev.event_type.value] += 1
            severity_counts[ev.severity.value] += 1

        prev_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        prev_count = len(self._daily_events.get(prev_date, []))

        trend = "up" if len(events) > prev_count else ("down" if len(events) < prev_count else "stable")
        top_alert = max(type_counts, key=type_counts.get) if type_counts else "none"

        return {
            "report_type": "daily",
            "date": date_str,
            "total_events": len(events),
            "event_breakdown": dict(type_counts),
            "severity_breakdown": dict(severity_counts),
            "top_alert_type": top_alert,
            "trend_vs_previous_day": trend,
            "day_over_day_change": len(events) - prev_count,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def generate_weekly_report(self, end_date: Optional[str] = None) -> Dict[str, Any]:
        end_date = end_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        start_dt = end_dt - timedelta(days=6)

        weekly_events: List[SecurityEvent] = []
        daily_totals: Dict[str, int] = {}
        for i in range(7):
            day = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
            evs = self._daily_events.get(day, [])
            weekly_events.extend(evs)
            daily_totals[day] = len(evs)

        type_counts: Dict[str, int] = defaultdict(int)
        for ev in weekly_events:
            type_counts[ev.event_type.value] += 1

        top_alerts = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "report_type": "weekly",
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_date,
            "total_events": len(weekly_events),
            "daily_totals": daily_totals,
            "event_breakdown": dict(type_counts),
            "top_3_alerts": top_alerts,
            "avg_daily_events": round(len(weekly_events) / 7, 1),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


class PromptwareKillChainTracker:
    """Promptware Kill Chain 7阶段轨迹追踪 (Stage 0-7)."""

    STAGES: List[str] = [
        "Stage_0_Reconnaissance",
        "Stage_1_Weaponization",
        "Stage_2_Delivery",
        "Stage_3_Exploitation",
        "Stage_4_Installation",
        "Stage_5_CommandAndControl",
        "Stage_6_ActionsOnObjectives",
        "Stage_7_Exfiltration",
    ]

    def __init__(self):
        self._trajectory_store: List[Dict[str, Any]] = []
        self._deep_search_samples: List[str] = []
        self._lock = threading.Lock()

    def record_stage(
        self,
        stage_index: int,
        prompt_snippet: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "stage": self.STAGES[min(stage_index, 7)],
            "stage_index": stage_index,
            "prompt_snippet": prompt_snippet[:500],
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self._trajectory_store.append(record)
            if len(self._trajectory_store) > 10000:
                self._trajectory_store = self._trajectory_store[-5000:]
        return record

    def deep_search_prompts(self, query: str) -> List[str]:
        query_lower = query.lower()
        results: List[str] = []
        with self._lock:
            for sample in self._deep_search_samples:
                if query_lower in sample.lower():
                    results.append(sample)
            for record in self._trajectory_store:
                snippet = record.get("prompt_snippet", "")
                if query_lower in snippet.lower():
                    results.append(snippet)
        return results[:20]

    def add_sample(self, prompt: str) -> None:
        with self._lock:
            self._deep_search_samples.append(prompt)
            if len(self._deep_search_samples) > 500:
                self._deep_search_samples = self._deep_search_samples[-250:]

    @property
    def trajectory(self) -> List[Dict[str, Any]]:
        return list(self._trajectory_store)


class SideChannelDefender:
    """侧信道防御 — 流量填充 + 时序噪声 + 审计."""

    def __init__(
        self,
        padding_rate: float = 0.1,
        noise_max_ms: float = 50.0,
    ):
        self._padding_rate = padding_rate
        self._noise_max_ms = noise_max_ms
        self._audit_log: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def traffic_padding(self, content_size: int) -> int:
        if random.random() < self._padding_rate:
            pad = random.randint(1, max(1, content_size // 10))
            return content_size + pad
        return content_size

    def timing_noise(self) -> float:
        return random.uniform(0, self._noise_max_ms) / 1000.0

    def side_channel_audit(
        self, operation: str, timing_ms: float, size_bytes: int
    ) -> Dict[str, Any]:
        audit = {
            "operation": operation,
            "timing_ms": round(timing_ms, 3),
            "size_bytes": size_bytes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "flagged": timing_ms > 100.0,
        }
        with self._lock:
            self._audit_log.append(audit)
            if len(self._audit_log) > 1000:
                self._audit_log = self._audit_log[-500:]
        write_to_core("llm_side_channel_audit", audit)
        return audit

    @property
    def audit_log(self) -> List[Dict[str, Any]]:
        return list(self._audit_log)


class ObservabilityLayer(LLMSecurityProtocol):
    """L6 可观测性层 —— 事件日志+异常检测+告警+仪表板+报告+Promptware+侧信道."""

    def __init__(self, webhook_url: str = ""):
        self._events: List[SecurityEvent] = []
        self._lock = threading.Lock()
        self._anomaly_detector = FrequencyAnomalyDetector()
        self._alert_sender = AlertSender(webhook_url=webhook_url)
        self._report_generator = ReportGenerator()
        self._kill_chain_tracker = PromptwareKillChainTracker()
        self._side_channel_defender = SideChannelDefender()
        self._metrics = DashboardMetrics()

    def layer_name(self) -> str:
        return "l6_observability"

    def layer_index(self) -> int:
        return 6

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        self.log_security_event(
            event_type=SecurityEventType.PROMPT_BLOCKED,
            message=f"LSG pipeline evaluation: request_id={ctx.request_id}, layer={ctx.layer_name}",
            severity=AlertSeverity.INFO,
            details={
                "request_id": ctx.request_id,
                "source": ctx.metadata.get("source", "unknown"),
                "input_length": len(ctx.raw_input),
            },
            request_id=ctx.request_id,
            session_id=ctx.metadata.get("session_id", ""),
        )
        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="L6 observability pass-through",
            layer_name=self.layer_name(),
            score=1.0,
        )

    def log_security_event(
        self,
        event_type: SecurityEventType,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        details: Optional[Dict[str, Any]] = None,
        request_id: str = "",
        session_id: str = "",
    ) -> SecurityEvent:
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            message=message,
            details=details or {},
            request_id=request_id,
            session_id=session_id,
        )
        with self._lock:
            self._events.append(event)
            if len(self._events) > 10000:
                self._events = self._events[-5000:]
        self._report_generator.record_event(event)
        self._update_metrics(event)
        return event

    def _update_metrics(self, event: SecurityEvent) -> None:
        m = self._metrics
        m.total_prompts_processed += 1
        et = event.event_type
        if et == SecurityEventType.PROMPT_BLOCKED:
            m.prompts_blocked += 1
        elif et == SecurityEventType.LEAK_DETECTED:
            m.leaks_detected += 1
        elif et == SecurityEventType.HALLUCINATION_DETECTED:
            m.hallucinations_detected += 1
        elif et == SecurityEventType.AGENT_PERMISSION_DENIED:
            m.agent_permissions_denied += 1
        elif et == SecurityEventType.CIRCUIT_BREAKER_TRIPPED:
            m.circuit_breaker_trips += 1
        elif et == SecurityEventType.BUDGET_EXCEEDED:
            m.budget_exceeded_count += 1
        elif et == SecurityEventType.ANOMALY_DETECTED:
            m.anomaly_events += 1
        elif et == SecurityEventType.PROMPTWARE_DETECTED:
            m.promptware_detections += 1
        elif et == SecurityEventType.SIDE_CHANNEL_DETECTED:
            m.side_channel_events += 1
        m.last_updated = datetime.now(timezone.utc).isoformat()

    def detect_frequency_anomaly(self, count: int) -> Dict[str, Any]:
        result = self._anomaly_detector.record(count)
        if result["anomaly"]:
            self.log_security_event(
                event_type=SecurityEventType.ANOMALY_DETECTED,
                message=f"Frequency anomaly: {count} events, EMA={result['ema']}, threshold={result['threshold']}",
                severity=AlertSeverity.WARNING,
                details=result,
            )
        return result

    def send_alert(
        self,
        severity: AlertSeverity,
        event_type: SecurityEventType,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self._alert_sender.send_alert(
            severity=severity, event_type=event_type, message=message, details=details
        )

    def collect_metrics(self) -> DashboardMetrics:
        return self._metrics

    def generate_daily_report(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        return self._report_generator.generate_daily_report(date_str)

    def generate_weekly_report(self, end_date: Optional[str] = None) -> Dict[str, Any]:
        return self._report_generator.generate_weekly_report(end_date)

    @property
    def events(self) -> List[SecurityEvent]:
        with self._lock:
            return list(self._events)

    @property
    def kill_chain_tracker(self) -> PromptwareKillChainTracker:
        return self._kill_chain_tracker

    @property
    def side_channel_defender(self) -> SideChannelDefender:
        return self._side_channel_defender

    @property
    def anomaly_detector(self) -> FrequencyAnomalyDetector:
        return self._anomaly_detector

    @property
    def alert_sender(self) -> AlertSender:
        return self._alert_sender
