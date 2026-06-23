# [A_module] module_id=MOD-ORC_status_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md

# [MODULE] zephyr.trading.status_dashboard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
StatusDashboard — 实时状态面板
================================
蓝图: ARC-0001 §6.1
TUI + JSON API 双模式。
"""

from datetime import datetime
from typing import Any

from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.circadian_scheduler import CircadianScheduler
from zephyr.trading.health_monitor import HealthMonitor
from zephyr.trading.night_shift_queue import NightShiftQueue
from zephyr.trading.orphan_detector import OrphanDetector
from zephyr.trading.work_orchestrator import WorkOrchestrator


class StatusDashboard:
    """实时状态面板——TUI + JSON API 双模式。"""

    def __init__(
        self,
        registry: CapabilityRegistry,
        health_monitor: HealthMonitor,
        night_shift_queue: NightShiftQueue,
        work_orchestrator: WorkOrchestrator,
        circadian_scheduler: CircadianScheduler,
        orphan_detector: OrphanDetector | None = None,
        uptime_start: str = "",
    ) -> None:
        self._registry = registry
        self._health = health_monitor
        self._nq = night_shift_queue
        self._wo = work_orchestrator
        self._cs = circadian_scheduler
        self._orphan = orphan_detector
        self._uptime_start = uptime_start or datetime.now().isoformat()

    def render_tui(self) -> str:
        phase = self._cs.get_current_phase()
        nq_stats = self._nq.stats()
        pending = self._wo.pending_count()
        running = self._wo.running_count()
        dags = self._wo.list_dags()
        caps = self._registry.list_all()
        pressure = self._health.pressure_level()
        next_task = self._cs.get_next_task()

        orphan_rate = 0.0
        if self._orphan:
            orphan_rate = self._orphan.compute_orphan_rate()

        lines = [
            f"{'=' * 60}",
            "  ZephyrAlpha AutoRuntime Core",
            f"  Phase: {phase.value}  Pressure: {pressure.value}  OrphanRate: {orphan_rate:.1%}",
            f"{'=' * 60}",
            f"  Capabilities: {len(caps)} registered",
            f"  Night Shift: {nq_stats['pending']} pending / {nq_stats['resolved']} resolved",
            f"  Work DAGs: {len(dags)} loaded",
            f"  Pending: L1={pending.get('trae', 0)} L2={pending.get('local', 0)} L3={pending.get('api', 0)}",
            f"  Running: L1={running.get('trae', 0)} L2={running.get('local', 0)} L3={running.get('api', 0)}",
            f"  Next circadian: {next_task.name if next_task else 'none'}",
            f"{'=' * 60}",
        ]
        return "\n".join(lines)

    def render_json(self) -> dict[str, Any]:
        phase = self._cs.get_current_phase()
        nq_stats = self._nq.stats()
        orphan_rate = 0.0
        if self._orphan:
            orphan_rate = self._orphan.compute_orphan_rate()

        return {
            "phase": phase.value,
            "pressure": self._health.pressure_level().value,
            "orphan_rate": orphan_rate,
            "capabilities": len(self._registry.list_all()),
            "night_shift": nq_stats,
            "work_dags": len(self._wo.list_dags()),
            "pending": self._wo.pending_count(),
            "running": self._wo.running_count(),
            "uptime_start": self._uptime_start,
        }
