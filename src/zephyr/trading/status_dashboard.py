# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.status_dashboard
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
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
# [A_module] module_id=MOD-ORC_status_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
StatusDashboard — 实时状态面板
================================
蓝图: ARC-0001 §6.1
TUI + JSON API 双模式。
"""

from datetime import datetime
from typing import Any

from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.health_monitor import HealthMonitor
from zephyr.trading.night_shift_queue import NightShiftQueue
from zephyr.trading.orphan_detector import OrphanDetector
from zephyr.trading.work_orchestrator import WorkOrchestrator
from zephyr.shared.utils.time_utils import now_utc


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

    def render_json(self) -> dict[str, Any]:
        nq_stats = self._nq.stats()
        orphan_rate = 0.0
        if self._orphan:
            orphan_rate = self._orphan.compute_orphan_rate()

        return {
            "phase": _current_phase(),
            "pressure": self._health.pressure_level().value,
            "orphan_rate": orphan_rate,
            "capabilities": len(self._registry.list_all()),
            "night_shift": nq_stats,
            "work_dags": len(self._wo.list_dags()),
            "pending": self._wo.pending_count(),
            "running": self._wo.running_count(),
            "uptime_start": self._uptime_start,
        }
