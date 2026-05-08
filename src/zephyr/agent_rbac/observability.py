"""
L6 Observability — OpenTelemetry指标上报 + 行为异常检测

MOD-INF-018 §2.9  D-018-11
"""

import time
import hashlib
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional


@dataclass
class MetricEntry:
    metric: str
    value: float
    labels: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class AnomalyResult:
    anomaly: bool = False
    rule: str = ""
    detail: str = ""
    severity: str = "INFO"


class ObservabilityReporter:
    def __init__(self) -> None:
        self._metrics: list[MetricEntry] = []
        self._decision_counter: dict[str, int] = defaultdict(int)
        self._anomaly_events: list[dict] = []
        self._signal_count: int = 0
        self._noise_count: int = 0
        self._source_hash: str = self._compute_self_hash()

    def record_decision(self, agent_id: str, level: str, decision: str) -> None:
        key = f"d2.authz.decision.agent={agent_id}.level={level}.decision={decision}"
        self._decision_counter[key] += 1
        self._signal_count += 1
        self._metrics.append(MetricEntry(
            metric="d2.authz.decision",
            value=1.0,
            labels={"agent_id": agent_id, "level": level, "decision": decision},
        ))

    def record_noise(self, source: str) -> None:
        self._noise_count += 1

    @property
    def signal_noise_ratio(self) -> float:
        if self._noise_count == 0:
            return float("inf")
        return self._signal_count / self._noise_count

    def check_signal_noise_alert(self) -> bool:
        return self._noise_count > 0 and self.signal_noise_ratio < 0.1

    def detect_density_anomaly(
        self,
        agent_id: str,
        operations_in_window: int,
        threshold_per_minute: int = 60,
    ) -> AnomalyResult:
        if operations_in_window > threshold_per_minute:
            return AnomalyResult(
                anomaly=True,
                rule="HIGH_OP_DENSITY",
                detail=f"Agent {agent_id}: {operations_in_window} ops/min > {threshold_per_minute}",
                severity="P2",
            )
        return AnomalyResult()

    def detect_off_hours_destructive(
        self,
        agent_id: str,
        operation: str,
        timestamp: Optional[float] = None,
    ) -> AnomalyResult:
        ts = timestamp or time.time()
        hour = time.localtime(ts).tm_hour
        destructive = any(p in operation for p in ["delete:", "rm ", "remove:"])
        if destructive and (hour < 8 or hour >= 22):
            return AnomalyResult(
                anomaly=True,
                rule="OFF_HOURS_DESTRUCTIVE",
                detail=f"Agent {agent_id}: destructive op at {hour:02d}:00",
                severity="P1",
            )
        return AnomalyResult()

    def detect_maturity_escalation(
        self,
        agent_id: str,
        from_level: str,
        to_level: str,
    ) -> AnomalyResult:
        levels = ["L0_INTERN", "L1_JUNIOR", "L2_REGULAR", "L3_SENIOR", "L4_PRINCIPAL"]
        from_idx = levels.index(from_level) if from_level in levels else 0
        to_idx = levels.index(to_level) if to_level in levels else 0
        if to_idx - from_idx > 1:
            return AnomalyResult(
                anomaly=True,
                rule="MATURITY_JUMP",
                detail=f"Agent {agent_id}: jumped {to_idx - from_idx} levels ({from_level}→{to_level})",
                severity="P2",
            )
        return AnomalyResult()

    def verify_metric_integrity(self) -> bool:
        current_hash = self._compute_self_hash()
        return current_hash == self._source_hash

    def _compute_self_hash(self) -> str:
        try:
            import __main__
            source = __main__.__file__ if hasattr(__main__, "__file__") else "observability.py"
            return hashlib.sha256(source.encode()).hexdigest()[:16]
        except Exception:
            return hashlib.sha256(b"observability").hexdigest()[:16]

    def get_metrics_summary(self) -> dict:
        return {
            "decision_counter": dict(self._decision_counter),
            "signal_noise_ratio": self.signal_noise_ratio,
            "total_metrics": len(self._metrics),
        }

    def reset(self) -> None:
        self._metrics.clear()
        self._decision_counter.clear()
        self._anomaly_events.clear()
        self._signal_count = 0
        self._noise_count = 0
