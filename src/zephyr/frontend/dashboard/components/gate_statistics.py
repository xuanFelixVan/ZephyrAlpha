# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.gate_statistics
# [DOMAIN] D-FRONTEND
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_gate_statistics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# AI-generated: T-4-07 Gate Statistics Component
"""
GateStatisticsComponent · 门禁统计（通过率/阻断率/趋势）
========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GateStat:
    gate_id: str
    total_runs: int = 0
    passed_runs: int = 0
    failed_runs: int = 0

    @property
    def pass_rate(self) -> float:
        if self.total_runs == 0:
            return 1.0
        return self.passed_runs / self.total_runs

    @property
    def block_rate(self) -> float:
        return 1.0 - self.pass_rate


@dataclass
class GateStatisticsData:
    total_runs: int = 0
    total_passed: int = 0
    total_failed: int = 0
    overall_pass_rate: float = 1.0
    overall_block_rate: float = 0.0
    by_gate: list[GateStat] = field(default_factory=list)


def fetch_gate_statistics(olap_engine: Any = None) -> GateStatisticsData:
    data = GateStatisticsData()
    if olap_engine is None:
        return data
    try:
        summary = olap_engine.get_gate_summary()
        data.total_runs = summary.get("total", 0)
        data.total_passed = summary.get("passed", 0)
        data.total_failed = data.total_runs - data.total_passed
        data.overall_pass_rate = data.total_passed / data.total_runs if data.total_runs > 0 else 1.0
        data.overall_block_rate = 1.0 - data.overall_pass_rate
    except Exception:
        pass
    return data


def render_gate_statistics(data: GateStatisticsData) -> dict[str, Any]:
    return {
        "total_runs": data.total_runs,
        "total_passed": data.total_passed,
        "total_failed": data.total_failed,
        "overall_pass_rate": round(data.overall_pass_rate, 4),
        "overall_block_rate": round(data.overall_block_rate, 4),
        "by_gate": [
            {
                "gate_id": g.gate_id,
                "total_runs": g.total_runs,
                "passed_runs": g.passed_runs,
                "failed_runs": g.failed_runs,
                "pass_rate": round(g.pass_rate, 4),
                "block_rate": round(g.block_rate, 4),
            }
            for g in data.by_gate
        ],
    }
