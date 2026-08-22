# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.status_dashboard
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
StatusDashboard — 实时状态面板
================================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
TUI + JSON API 双模式。
"""

from datetime import datetime
from typing import Any

from zephyr.shared.utils.time_utils import now_utc
from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.health_monitor import HealthMonitor, PressureLevel
from zephyr.trading.night_shift_queue import NightShiftQueue
from zephyr.trading.orphan_detector import OrphanDetector
from zephyr.trading.work_orchestrator import WorkOrchestrator

# 降级降采样档位（蓝图 §3.3 Lv1 Throttle 动作「StatusDashboard 降采样」的施工裁定，
# 蓝图未给面板采样间隔具体值）：压力升档 → 面板刷新间隔升档。
_SAMPLING_INTERVAL_S: dict[PressureLevel, float] = {
    PressureLevel.NORMAL: 5.0,
    PressureLevel.ELEVATED: 15.0,
    PressureLevel.HIGH: 30.0,
    PressureLevel.CRITICAL: 60.0,
}


def _current_phase() -> str:
    """根据当前时间返回系统节律阶段字符串。

    原 CircadianScheduler.get_current_phase() 的内联实现——CircadianScheduler
    定时调度机制已废除（2026-06-26 裁定），phase 仅用于状态面板展示，
    故下沉为模块级纯函数，不再依赖调度器实例。
    """
    hour = now_utc().hour
    if 6 <= hour < 9:
        return "MORNING"
    if 9 <= hour < 18:
        return "DAY"
    if 18 <= hour < 21:
        return "EVENING"
    return "NIGHT"


class StatusDashboard:
    """实时状态面板——TUI + JSON API 双模式。"""

    def __init__(
        self,
        registry: CapabilityRegistry,
        health_monitor: HealthMonitor,
        night_shift_queue: NightShiftQueue,
        work_orchestrator: WorkOrchestrator,
        orphan_detector: OrphanDetector | None = None,
        uptime_start: str = "",
    ) -> None:
        self._registry = registry
        self._health = health_monitor
        self._nq = night_shift_queue
        self._wo = work_orchestrator
        self._orphan = orphan_detector
        self._uptime_start = uptime_start or now_utc().isoformat()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def orphan(self):
        """只读：orphan（Stage 4 公共化）。"""
        return self._orphan

    @orphan.setter
    def orphan(self, value):
        """写入：orphan（Stage 4 公共化）。"""
        self._orphan = value

    @property
    def registry(self):
        """只读：registry（Stage 4 公共化）。"""
        return self._registry

    @registry.setter
    def registry(self, value):
        """写入：registry（Stage 4 公共化）。"""
        self._registry = value

    @property
    def uptime_start(self):
        """只读：uptime_start（Stage 4 公共化）。"""
        return self._uptime_start

    @uptime_start.setter
    def uptime_start(self, value):
        """写入：uptime_start（Stage 4 公共化）。"""
        self._uptime_start = value

    def render_tui(self) -> str:
        phase = _current_phase()
        nq_stats = self._nq.stats()
        pending = self._wo.pending_count()
        running = self._wo.running_count()
        dags = self._wo.list_dags()
        caps = self._registry.list_all()
        pressure = self._health.pressure_level()

        orphan_rate = 0.0
        if self._orphan:
            orphan_rate = self._orphan.compute_orphan_rate()

        lines = [
            f"{'=' * 60}",
            "  ZephyrAlpha AutoRuntime Core",
            f"  Phase: {phase}  Pressure: {pressure.value}  OrphanRate: {orphan_rate:.1%}",
            f"{'=' * 60}",
            f"  Capabilities: {len(caps)} registered",
            f"  Night Shift: {nq_stats['pending']} pending / {nq_stats['resolved']} resolved",
            f"  Work DAGs: {len(dags)} loaded",
            f"  Pending: L1={pending.get('trae', 0)} L2={pending.get('local', 0)} L3={pending.get('api', 0)}",
            f"  Running: L1={running.get('trae', 0)} L2={running.get('local', 0)} L3={running.get('api', 0)}",
            f"{'=' * 60}",
        ]
        return "\n".join(lines)

    def render_json(self, detail: bool | None = None) -> dict[str, Any]:
        """JSON 状态视图。

        detail=None（默认）：按健康压力自动降级——NORMAL 全量字段（行为与历史一致）；
        ELEVATED/HIGH/CRITICAL（降级链 Lv1+）触发降采样，跳过重计算字段
        （orphan_rate / night_shift 明细 / pending / running 分层计数），
        仅保留心跳级字段（蓝图 §3.3 Lv1 动作「StatusDashboard 降采样」）。
        """
        pressure = self._health.pressure_level()
        if detail is None:
            detail = pressure is PressureLevel.NORMAL

        if not detail:
            return {
                "phase": _current_phase(),
                "pressure": pressure.value,
                "degraded": True,
                "sampling_interval_s": self.sampling_interval_seconds(pressure),
                "capabilities": len(self._registry.list_all()),
                "work_dags": len(self._wo.list_dags()),
                "uptime_start": self._uptime_start,
            }

        nq_stats = self._nq.stats()
        orphan_rate = 0.0
        if self._orphan:
            orphan_rate = self._orphan.compute_orphan_rate()

        return {
            "phase": _current_phase(),
            "pressure": pressure.value,
            "orphan_rate": orphan_rate,
            "capabilities": len(self._registry.list_all()),
            "night_shift": nq_stats,
            "work_dags": len(self._wo.list_dags()),
            "pending": self._wo.pending_count(),
            "running": self._wo.running_count(),
            "uptime_start": self._uptime_start,
        }

    def sampling_interval_seconds(self, pressure: PressureLevel | None = None) -> float:
        """面板采样间隔：随压力升档（降级降采样，蓝图 §3.3 Lv1 配套）。"""
        if pressure is None:
            pressure = self._health.pressure_level()
        return _SAMPLING_INTERVAL_S.get(pressure, 5.0)

    def aggregate_view(self) -> dict[str, Any]:
        """聚合视图 + 下钻（蓝图 §16.3 步骤 1「聚合视图 + 下钻」）。

        summary：跨子系统聚合指标（与 render_json 全量口径一致 + 聚合维度）；
        drilldown：capabilities 按 status/category 分组计数、DAG 逐条概览。
        """
        caps = self._registry.list_all()
        by_status: dict[str, int] = {}
        by_category: dict[str, int] = {}
        for card in caps:
            status = str(getattr(card, "status", "UNKNOWN"))
            category = str(getattr(getattr(card, "category", None), "value", getattr(card, "category", "UNKNOWN")))
            by_status[status] = by_status.get(status, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1

        dag_drilldown: list[dict[str, Any]] = []
        for dag in self._wo.list_dags():
            dag_drilldown.append(
                {
                    "dag_id": str(getattr(dag, "dag_id", getattr(dag, "id", "unknown"))),
                    "status": str(getattr(dag, "status", "unknown")),
                }
            )

        return {
            "summary": self.render_json(detail=True),
            "drilldown": {
                "capabilities_by_status": by_status,
                "capabilities_by_category": by_category,
                "dags": dag_drilldown,
            },
        }
