# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.correlation.fle_performance_regression_detector
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_fle_performance_regression_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R532: FLEPerformanceRegressionDetector
自修改后基准性能回归检测 — 延迟/吞吐/准确率 vs 基线
"""

import time
from dataclasses import dataclass, field


@dataclass
class PerformanceBaseline:
    latency_ms: float
    throughput_per_sec: float
    accuracy: float
    cycle_count: int
    timestamp: float


@dataclass
class FLEPerformanceRegressionDetector:
    baseline: PerformanceBaseline | None = None
    current_metrics: list[dict] = field(default_factory=list)
    max_history: int = 100
    regression_threshold_latency: float = 0.3
    regression_threshold_throughput: float = 0.2

    def establish_baseline(
        self, latency_ms: float, throughput_per_sec: float, accuracy: float, cycle_count: int
    ) -> None:
        self.baseline = PerformanceBaseline(
            latency_ms=latency_ms,
            throughput_per_sec=throughput_per_sec,
            accuracy=accuracy,
            cycle_count=cycle_count,
            timestamp=time.time(),
        )

    def record_metrics(self, latency_ms: float, throughput_per_sec: float, accuracy: float) -> None:
        self.current_metrics.append(
            {
                "latency_ms": latency_ms,
                "throughput_per_sec": throughput_per_sec,
                "accuracy": accuracy,
                "timestamp": time.time(),
            }
        )
        if len(self.current_metrics) > self.max_history:
            self.current_metrics = self.current_metrics[-self.max_history :]

    def detect_regression(self) -> dict:
        if self.baseline is None or not self.current_metrics:
            return {"status": "no_baseline", "regression_detected": False}

        recent = self.current_metrics[-10:] if len(self.current_metrics) >= 10 else self.current_metrics
        if not recent:
            return {"status": "no_recent_data", "regression_detected": False}

        avg_latency = sum(m["latency_ms"] for m in recent) / len(recent)
        avg_throughput = sum(m["throughput_per_sec"] for m in recent) / len(recent)

        latency_change = (avg_latency - self.baseline.latency_ms) / max(self.baseline.latency_ms, 1e-6)
        throughput_change = (self.baseline.throughput_per_sec - avg_throughput) / max(
            self.baseline.throughput_per_sec, 1e-6
        )

        regressions = []
        if latency_change > self.regression_threshold_latency:
            regressions.append("latency_increased")
        if throughput_change > self.regression_threshold_throughput:
            regressions.append("throughput_decreased")

        severity = "none"
        if len(regressions) == 2:
            severity = "critical"
        elif len(regressions) == 1:
            severity = "warning"

        return {
            "status": severity,
            "regression_detected": len(regressions) > 0,
            "regressions": regressions,
            "baseline_latency_ms": round(self.baseline.latency_ms, 2),
            "current_avg_latency_ms": round(avg_latency, 2),
            "latency_change_pct": round(latency_change * 100, 1),
            "baseline_throughput": round(self.baseline.throughput_per_sec, 2),
            "current_avg_throughput": round(avg_throughput, 2),
            "throughput_change_pct": round(throughput_change * 100, 1),
            "recommendation": "ROLLBACK"
            if severity == "critical"
            else "MONITOR"
            if severity == "warning"
            else "CONTINUE",
        }
