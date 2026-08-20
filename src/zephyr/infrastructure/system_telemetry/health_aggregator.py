# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.health_aggregator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.health_probes; zephyr.shared.event_bus
# [CONSUMERS] zephyr.security.access_control; zephyr.infrastructure.budget_enforcement
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 11-system probe contract（knowledge_base 随 KB 退役 d5b6f5dde1 移除，真源 health_probes.SYSTEMS）; 15s poll interval; liveness/readiness/degraded triple-state
# [MODIFY-GUARD] health_probes.py; watchdog.py; health.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError; RuntimeError
# [TESTS] tests/system-telemetry/test_health_aggregator.py
# [A_module] module_id=MOD-INF-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
健康聚合器（Health Aggregator）

依据：MOD-MASTER-002 蓝图 §十四
每15s轮询11系统三态探针->生成健康面板快照->年度审计。
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from zephyr.infrastructure.system_telemetry.health_probes import SYSTEMS, HealthProbeManager

logger = logging.getLogger(__name__)


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


# class-name-alias: system_telemetry 健康聚合器（poll_all 三态探针快照+事件驱动触发），区别于 health_monitor/health_aggregator.py 的 check_all 并行检查
class HealthAggregator:
    _MAX_SNAPSHOTS = 1440

    def __init__(self, probe_manager: HealthProbeManager | None = None):
        self._probes = probe_manager or HealthProbeManager()
        self._snapshots: list[SystemHealthSnapshot] = []

    @property
    def snapshots(self) -> list[SystemHealthSnapshot]:
        """只读：snapshots（Stage 4 公共化）。"""
        return self._snapshots

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
        # 契约：返回每个 system 的最新一条快照（一轮 poll 全集）。
        # 旧实现按"最大时间戳精确相等"过滤——Windows 时钟分辨率 ~15.6ms，
        # 一轮 poll 跨 tick 时只剩部分 system，结果随机（0 生产消费者，潜在缺陷）。
        latest_by_system: dict[str, SystemHealthSnapshot] = {}
        for s in self._snapshots:
            cur = latest_by_system.get(s.system)
            if cur is None or s.timestamp >= cur.timestamp:
                latest_by_system[s.system] = s
        return list(latest_by_system.values())

    def annual_report(
        self, year: int, uptimes: dict[str, float], mttr: dict[str, float], degradations: dict[str, float]
    ) -> AnnualHealthReport:
        return AnnualHealthReport(
            year=year,
            uptime_ratio=uptimes,
            mttr_s=mttr,
            degradation_ratio=degradations,
        )

    _subscribed: bool = False

    def subscribe_eventbus(self) -> None:
        """事件驱动订阅——kill_switch_triggered/pipeline_failed 时立即采集健康快照（永久系统四要素：自动触发）。"""
        if self._subscribed:
            return
        from zephyr.shared.event_bus import bus

        aggregator = self

        def _on_critical_event(payload: object) -> None:
            try:
                snapshots = aggregator.poll_all()
                degraded = [s for s in snapshots if s.degraded]
                if degraded:
                    from datetime import UTC, datetime

                    ts = datetime.now(UTC).isoformat()
                    logger.warning("[HEALTH] %s: %d degraded systems after critical event", ts, len(degraded))
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                pass

        bus.subscribe("kill_switch_triggered", _on_critical_event)
        bus.subscribe("pipeline_failed", _on_critical_event)
        self._subscribed = True
