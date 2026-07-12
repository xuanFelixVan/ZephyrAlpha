# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.fitness_functions
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS] zephyr.frontend.dashboard.app_panel
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
# [TTL] permanent

# AI-generated: T-4-07 Fitness Functions Component
"""fitness_functions · Fitness Functions 仪表盘组件（v3.1.0 Panel 迁移, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §3.1
数据源: FLE FitnessFunctionFramework.run_all() -> FitnessReport
渲染依赖: Panel(布局) — 指标卡片+状态表，无专业图表需求故不调用 ChartFactory

v3.1.0 变更 (#ARCH-047):
  - Streamlit(st.metric/st.write) -> Panel(pn.pane.Markdown 指标卡片 + 状态表)
  - callback仅编排: 布局组装在此, 数据计算在 fetch_fitness_data(纯函数)
  - 测试环境(无 panel)仅返回 dict payload, 便于断言
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

from zephyr.feedback_loop.fitness_functions import (
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
                "status": m.status.value if hasattr(m.status, "value") else str(m.status),
                "message": m.message,
            }
            for m in report.metrics
        ],
        report=report,
    )
    return data


def _status_color(status: str) -> str:
    s = (status or "").upper()
    if s in ("PASS", "OK", "GREEN", "HEALTHY"):
        return "#28a745"
    if s in ("WARN", "WARNING", "YELLOW"):
        return "#ffc107"
    if s in ("FAIL", "ERROR", "RED", "CRITICAL"):
        return "#dc3545"
    return "#6c757d"


def _metric_card(label: str, value: str, color: str = "#333") -> Any:
    """生成单个指标卡片（Panel Card 或 dict）"""
    if pn is None:
        return {"label": label, "value": value, "color": color}
    return pn.pane.Markdown(
        f"**{label}**\n\n## {value}",
        styles={"color": color, "text-align": "center", "padding": "8px",
                "border": "1px solid #e0e0e0", "border-radius": "4px"},
    )


def render_fitness_dashboard(data: FitnessDashboardData) -> dict[str, Any]:
    """Panel 渲染 Fitness Functions 仪表盘（v3.1.0, #ARCH-047）

    布局:
      - 顶部: 总体状态卡片(overall_status)
      - 中部: 各度量指标卡片(metric_name/value/status)
      - 底部: 度量明细表(metric_name/threshold/status/message)

    callback仅编排: 数据计算在 fetch_fitness_data(纯函数).
    测试环境(无 panel)仅返回 dict payload, 便于断言.
    """
    payload: dict[str, Any] = {
        "overall_status": data.overall_status,
        "metrics": data.metrics,
        "metric_count": len(data.metrics),
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    overall_color = _status_color(data.overall_status)
    overall_card = _metric_card("Overall Status", data.overall_status, overall_color)

    layout_items: list[Any] = [
        pn.pane.Markdown("## Fitness Functions 仪表盘"),
        pn.Row(overall_card, sizing_mode="stretch_width"),
        pn.pane.Markdown("### 各度量指标"),
    ]

    if data.metrics:
        metric_cards = [
            _metric_card(
                m.get("metric_name", ""),
                f"{m.get('value', 0)}",
                _status_color(m.get("status", "")),
            )
            for m in data.metrics
        ]
        layout_items.append(pn.Row(*metric_cards, sizing_mode="stretch_width"))

        # 度量明细表
        rows = ["| Metric | Value | Threshold | Status | Message |",
                "|---|---|---|---|---|"]
        for m in data.metrics:
            rows.append(
                f"| {m.get('metric_name', '')} | {m.get('value', 0)} | "
                f"{m.get('threshold', 0)} | {m.get('status', '')} | {m.get('message', '')} |"
            )
        layout_items.append(pn.pane.Markdown("\n".join(rows)))
    else:
        layout_items.append(pn.pane.Alert("无 Fitness 度量数据", alert_type="info"))

    layout = pn.Column(*layout_items, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__ = [
    "FitnessDashboardData",
    "fetch_fitness_data",
    "render_fitness_dashboard",
]
