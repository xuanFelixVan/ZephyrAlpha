"""
健康聚合器（Health Aggregator）

依据：MOD-MASTER-001 蓝图 §十四
每15s轮询12系统三态探针→生成健康面板快照→年度审计。
"""

from __future__ import annotations

from datetime import datetime, timezone
from math import pi
from typing import Any

from pydantic import BaseModel, Field

from zephyr.telemetry.health_probes import HealthProbeManager, SYSTEMS


class SystemHealthSnapshot(BaseModel):
    system: str
    liveness: str = "alive"
    readiness: str = "ready"
    degraded: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnnualHealthReport(BaseModel):
    year: int
    uptime_ratio: dict[str, float] = Field(default_factory=dict)
    mttr_s: dict[str, float] = Field(default_factory=dict)
    degradation_ratio: dict[str, float] = Field(default_factory=dict)


class HealthAggregator:
    def __init__(self, probe_manager: HealthProbeManager | None = None):
        self._probes = probe_manager or HealthProbeManager()
        self._snapshots: list[SystemHealthSnapshot] = []
        self._poll_interval_s: float = 15.0

    def poll_all(self) -> list[SystemHealthSnapshot]:
        results: list[SystemHealthSnapshot] = []
        for system in SYSTEMS:
            liveness = self._probes.liveness(system)
            readiness = self._probes.readiness(system)
            healthz = self._probes.healthz(system)
            snapshot = SystemHealthSnapshot(
                system=system,
                liveness=liveness["status"],
                readiness=readiness["status"],
                degraded=healthz["status"] == "degraded",
            )
            results.append(snapshot)
        self._snapshots.extend(results)
        return results

    def latest_snapshots(self) -> list[SystemHealthSnapshot]:
        if not self._snapshots:
            return []
        latest_ts = max(s.timestamp for s in self._snapshots)
        return [s for s in self._snapshots if s.timestamp == latest_ts]

    def annual_report(self, year: int, uptimes: dict[str, float],
                      mttr: dict[str, float], degradations: dict[str, float]) -> AnnualHealthReport:
        return AnnualHealthReport(
            year=year,
            uptime_ratio=uptimes,
            mttr_s=mttr,
            degradation_ratio=degradations,
        )
