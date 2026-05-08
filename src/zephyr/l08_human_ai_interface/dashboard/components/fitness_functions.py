# AI-generated: T-4-07 Fitness Functions Component
"""
FitnessFunctionsComponent · Fitness Functions（5 类度量仪表盘）
===============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zephyr.feedback_loop.fitness_functions import (
    FitnessFunctionFramework,
    FitnessInputs,
)


@dataclass
class FitnessDashboardData:
    overall_status: str = "PASS"
    metrics: list[dict[str, Any]] = field(default_factory=list)
    report: Any = None


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
                "detail": m.detail,
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
