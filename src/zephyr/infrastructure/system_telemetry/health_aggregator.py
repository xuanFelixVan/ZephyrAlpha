# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.health_aggregator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.shared.health_discovery; zephyr.shared.contracts.core.timestamp
# [CONSUMERS] zephyr.security.access_control; zephyr.infrastructure.budget_enforcement
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 12-system probe contract; 15s poll interval; liveness/readiness/degraded triple-state
# [MODIFY-GUARD] health_probes.py; watchdog.py; health.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError; RuntimeError
# [TESTS] tests/system-telemetry/test_health_aggregator.py
# [A_module] module_id=MOD-INF_health_aggregator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
健康聚合器（Health Aggregator）

依据：MOD-MASTER-002 蓝图 §十四
每15s轮询12系统三态探针→生成健康面板快照→年度审计。
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from zephyr.infrastructure.system_telemetry.health_probes import SYSTEMS, HealthProbeManager


class SystemHealthSnapshot(BaseModel):
    system: str
    liveness: str = "alive"
    readiness: str = "ready"
    degraded: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AnnualHealthReport(BaseModel):
    year: int
    uptime_ratio: dict[str, float] = Field(default_factory=dict)
    mttr_s: dict[str, float] = Field(default_factory=dict)
    degradation_ratio: dict[str, float] = Field(default_factory=dict)


class HealthAggregator:
    _MAX_SNAPSHOTS = 1440

    def __init__(self, probe_manager: HealthProbeManager | None = None):
        self._probes = probe_manager or HealthProbeManager()
        self._snapshots: list[SystemHealthSnapshot] = []

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
        if len(self._snapshots) > self._MAX_SNAPSHOTS:
            self._snapshots = self._snapshots[-self._MAX_SNAPSHOTS :]
        return results

    def latest_snapshots(self) -> list[SystemHealthSnapshot]:
        if not self._snapshots:
            return []
        latest_ts = max(s.timestamp for s in self._snapshots)
        return [s for s in self._snapshots if s.timestamp == latest_ts]

    def annual_report(
        self, year: int, uptimes: dict[str, float], mttr: dict[str, float], degradations: dict[str, float]
    ) -> AnnualHealthReport:
        return AnnualHealthReport(
            year=year,
            uptime_ratio=uptimes,
            mttr_s=mttr,
            degradation_ratio=degradations,
        )
