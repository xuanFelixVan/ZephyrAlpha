# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §6
# [MODULE] zephyr.gov_audit.anomaly
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.pipeline_runner; integrity
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 异常检测基于统计阈值; 误报率低于10%
# [MODIFY-GUARD] 检测算法变更必须同步 self_monitor.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 检测失败返回空结果
# [TESTS] tests/audit-orchestrator/test_anomaly.py
# [A_module] module_id=MOD-GOV_anomaly | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["AnomalyDetector"]


class AnomalyDetector:
    def __init__(self, window_size: int = 50) -> None:
        self._window_size = window_size
        self._values: list[float] = []

    def feed(self, value: float) -> None:
        self._values.append(value)
        if len(self._values) > self._window_size * 2:
            self._values = self._values[-self._window_size :]

    def detect(self, value: float, threshold: float = 2.0) -> dict[str, Any]:
        self.feed(value)

        if len(self._values) < 10:
            return {"is_anomaly": False, "z_score": 0.0, "reason": "insufficient_data"}

        recent = self._values[-self._window_size :]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        std_dev = variance**0.5

        if abs(std_dev) < 1e-9:  # 5.167.3 修复: 浮点==0比较改 < epsilon
            return {"is_anomaly": value != mean, "z_score": 0.0 if value == mean else float("inf")}

        z_score = abs(value - mean) / std_dev
        is_anomaly = z_score > threshold

        return {
            "is_anomaly": is_anomaly,
            "z_score": round(z_score, 4),
            "mean": round(mean, 4),
            "std_dev": round(std_dev, 4),
            "threshold": threshold,
        }

    def scan_series(self, series: list[float], threshold: float = 2.0) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for i, v in enumerate(series):
            result = self.detect(v, threshold)
            if result["is_anomaly"]:
                result["index"] = i
                result["value"] = v
                results.append(result)
        return results


class AnomalyEvent:
    def __init__(self, event_id="", anomaly_type="", severity="medium", description="", timestamp=None, source=""):
        self.event_id = event_id
        self.anomaly_type = anomaly_type
        self.severity = severity
        self.description = description
        self.timestamp = timestamp
        self.source = source


class AnomalyResult:
    def __init__(self, is_anomaly=False, score=0.0, details=None, anomaly_type=""):
        self.is_anomaly = is_anomaly
        self.score = score
        self.details = details or {}
        self.anomaly_type = anomaly_type


class AnomalySignature:
    def __init__(self, signature_id="", pattern="", severity="medium", description=""):
        self.signature_id = signature_id
        self.pattern = pattern
        self.severity = severity
        self.description = description
