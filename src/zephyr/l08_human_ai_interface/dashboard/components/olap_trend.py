# AI-generated: T-4-07 OLAP Trend Component
"""
OLAPTrendComponent · OLAP 趋势（DuckDB 趋势图）
=================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OLAPTrendData:
    task_progress: list[dict[str, Any]] = field(default_factory=list)
    compliance_rate: list[dict[str, Any]] = field(default_factory=list)
    knowledge_activation: list[dict[str, Any]] = field(default_factory=list)


def fetch_olap_trends(olap_engine: Any = None, period: str = "day", limit: int = 30) -> OLAPTrendData:
    data = OLAPTrendData()
    if olap_engine is None:
        return data
    try:
        data.task_progress = olap_engine.task_progress_trend(period=period, limit=limit)
    except Exception:
        pass
    try:
        data.compliance_rate = olap_engine.compliance_rate_trend(period=period, limit=limit)
    except Exception:
        pass
    try:
        data.knowledge_activation = olap_engine.knowledge_activation_trend(period="month", limit=12)
    except Exception:
        pass
    return data


def render_olap_trends(data: OLAPTrendData) -> dict[str, Any]:
    return {
        "task_progress": data.task_progress,
        "compliance_rate": data.compliance_rate,
        "knowledge_activation": data.knowledge_activation,
    }
