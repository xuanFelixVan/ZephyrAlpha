# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.fitness_functions
# [DOMAIN] D-FRONTEND
# [DEPENDENCIES] zephyr.ops.__init__
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
# [A_module] module_id=MOD-UNK_fitness_functions | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# AI-generated: T-4-07 Fitness Functions Component
"""
FitnessFunctionsComponent · Fitness Functions（5 类度量仪表盘）
===============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zephyr.ops.fitness_functions import (
    FitnessFunctionFramework,
    FitnessInputs,
    FitnessReport,
)


@dataclass
class FitnessDashboardData:
    overall_status: str = "PASS"
    metrics: list[dict[str, Any]] = field(default_factory=list)
    report: FitnessReport | None = None


def fetch_fitness_data(
    inputs: FitnessInputs | None = None,
    framework: FitnessFunctionFramework | None = None,
) -> FitnessDashboardData:
    fw = framework or FitnessFunctionFramework()
    if inputs is None:
        inputs = FitnessInputs()
    report = fw.run_all(inputs)
    data = FitnessDashboardData(
        overall_status=report.overall_status.value,
        metrics=[
            {
                "metric_name": m.metric_name,
                "value": m.value,
                "threshold": m.threshold,
                "status": m.status,
                "message": m.message,
            }
            for m in report.metrics
        ],
        report=report,
    )
    return data


def render_fitness_dashboard(data: FitnessDashboardData) -> dict[str, Any]:
    return {
        "overall_status": data.overall_status,
        "metrics": data.metrics,
    }
