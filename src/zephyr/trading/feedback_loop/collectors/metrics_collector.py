# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.metrics_collector
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_metrics_collector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from collections import deque
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class MetricSnapshot:
    timestamp: float
    system_cpu: float
    memory_usage_pct: float
    disk_io_wait: float
    network_errors_count: int
    detection_latency_ms: float


@dataclass
class EMABaseline:
    window: int = 100
    alpha: float = 0.1
    cpu_ema: float = 0.0
    mem_ema: float = 0.0
    disk_ema: float = 0.0
    net_ema: float = 0.0
    latency_ema: float = 0.0
    cpu_var: float = 1.0
    mem_var: float = 1.0
    disk_var: float = 1.0
    net_var: float = 1.0
    latency_var: float = 1.0
    history: deque = field(default_factory=lambda: deque(maxlen=100))

    def update(self, snapshot: MetricSnapshot) -> None:
        self.history.append(snapshot)
        self.cpu_ema = self.alpha * snapshot.system_cpu + (1 - self.alpha) * self.cpu_ema
        self.mem_ema = self.alpha * snapshot.memory_usage_pct + (1 - self.alpha) * self.mem_ema
        self.disk_ema = self.alpha * snapshot.disk_io_wait + (1 - self.alpha) * self.disk_ema
        self.net_ema = self.alpha * snapshot.network_errors_count + (1 - self.alpha) * self.net_ema
        self.latency_ema = self.alpha * snapshot.detection_latency_ms + (1 - self.alpha) * self.latency_ema
        if len(self.history) > 1:
            values = np.array(
                [
                    [s.system_cpu, s.memory_usage_pct, s.disk_io_wait, s.network_errors_count, s.detection_latency_ms]
                    for s in self.history
                ]
            )
            self.cpu_var = max(float(np.var(values[:, 0])), 1e-6)
            self.mem_var = max(float(np.var(values[:, 1])), 1e-6)
            self.disk_var = max(float(np.var(values[:, 2])), 1e-6)
            self.net_var = max(float(np.var(values[:, 3])), 1e-6)
            self.latency_var = max(float(np.var(values[:, 4])), 1e-6)


class MetricsCollector:
    Z_THRESHOLD = 2.5

    def __init__(self):
        self.baseline = EMABaseline()

    def collect(self, snapshot: MetricSnapshot) -> dict[str, Any]:
        self.baseline.update(snapshot)
        z_scores = {
            "system_cpu": abs(snapshot.system_cpu - self.baseline.cpu_ema) / max(self.baseline.cpu_var**0.5, 1e-6),
            "memory_usage_pct": abs(snapshot.memory_usage_pct - self.baseline.mem_ema)
            / max(self.baseline.mem_var**0.5, 1e-6),
            "disk_io_wait": abs(snapshot.disk_io_wait - self.baseline.disk_ema)
            / max(self.baseline.disk_var**0.5, 1e-6),
            "network_errors_count": abs(snapshot.network_errors_count - self.baseline.net_ema)
            / max(self.baseline.net_var**0.5, 1e-6),
            "detection_latency_ms": abs(snapshot.detection_latency_ms - self.baseline.latency_ema)
            / max(self.baseline.latency_var**0.5, 1e-6),
        }
        anomaly_triggered = any(abs(z) > self.Z_THRESHOLD for z in z_scores.values())
        return {
            "snapshot": snapshot,
            "z_scores": z_scores,
            "anomaly_triggered": anomaly_triggered,
        }
