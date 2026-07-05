# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.anomaly.anomaly_detector
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_anomaly_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import uuid
from dataclasses import dataclass
from typing import Any

from zephyr.trading.feedback_loop.collectors.feedback_collector import FeedbackCollector
from zephyr.trading.feedback_loop.collectors.metrics_collector import MetricsCollector, MetricSnapshot
from zephyr.trading.feedback_loop.protocols import ActionType, FeedbackProtocolAdapter


@dataclass
class AnomalyEvent:
    anomaly_id: str
    severity: int
    evidence: dict[str, Any]
    timestamp: float


@dataclass
class AnomalyDetector:
    metrics_collector: MetricsCollector
    feedback_collector: FeedbackCollector
    protocol_adapter: FeedbackProtocolAdapter | None = None
    z_threshold: float = 2.5
    max_detect_seconds: float = 300.0

    def detect(self, snapshot: MetricSnapshot) -> AnomalyEvent | None:
        result = self.metrics_collector.collect(snapshot)
        if not result["anomaly_triggered"]:
            return None
        triggered_metrics = {k: v for k, v in result["z_scores"].items() if abs(v) > self.z_threshold}
        # 5.106.2 修复: z_threshold 与类常量 Z_THRESHOLD 分叉时 triggered_metrics 可能为空,
        # max() 抛 ValueError。公开方法需空集保护。
        if not triggered_metrics:
            return None
        max_z_metric = max(triggered_metrics, key=lambda k: abs(triggered_metrics[k]))
        severity = min(int(abs(triggered_metrics[max_z_metric]) * 2), 10)
        anomaly_id = str(uuid.uuid4())[:8]
        evidence = {
            "metric_name": max_z_metric,
            "value": getattr(snapshot, max_z_metric),
            "z_score": triggered_metrics[max_z_metric],
            "baseline_ema": getattr(self.metrics_collector.baseline, f"{max_z_metric}_ema", 0.0),
            "repair_failure_rate": self.feedback_collector.repair_failure_rate(),
        }
        event = AnomalyEvent(
            anomaly_id=anomaly_id,
            severity=severity,
            evidence=evidence,
            timestamp=snapshot.timestamp,
        )
        if self.protocol_adapter is not None and severity > 0:
            self.protocol_adapter.dispatch_action(
                ActionType.NOTIFY_OWNER,
                {"anomaly_id": anomaly_id, "severity": severity, "evidence": evidence},
            )
        return event
