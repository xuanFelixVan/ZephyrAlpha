"""Self Health Monitor — v0.4.0 R29

Blindspot: FLE monitors everything except its own internal health.
Risk: R29 — FLE degradation goes undetected, false negatives spike.
"""
from dataclasses import dataclass, field


@dataclass
class HealthStatus:
    cpu_ok: bool = True
    memory_ok: bool = True
    disk_ok: bool = True
    anomaly_rate_normal: bool = True

    @property
    def healthy(self) -> bool:
        return all([self.cpu_ok, self.memory_ok, self.disk_ok, self.anomaly_rate_normal])


@dataclass
class SelfHealthMonitor:
    status: HealthStatus = field(default_factory=HealthStatus)

    def check(self) -> HealthStatus:
        return self.status
