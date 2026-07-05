# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.gate_statistics
# [DEPENDENCIES] zephyr.frontend.dashboard.components.chart_factory
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
# [A_module] module_id=MOD-UNK_gate_statistics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-4-07 Gate Statistics Component
"""gate_statistics · 门禁统计组件（v3.1.0 Panel 迁移, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §3.1
数据源: OLAPEngine.get_gate_summary() → 通过率/阻断率/各门禁明细
渲染依赖: Panel(布局) + ChartFactory.make_gate_chart(堆叠条形图)

v3.1.0 变更 (#ARCH-047):
  - Streamlit(st.metric) → Panel(pn.pane.Markdown 指标卡片)
  - 图表生成委托 ChartFactory.make_gate_chart (callback仅编排)
  - 测试环境(无 panel)仅返回 dict payload, 便于断言
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

from zephyr.frontend.dashboard.components.chart_factory import (
    ChartFactoryError,
    make_gate_chart,
)


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


def _metric_card(label: str, value: str, color: str = "#333") -> Any:
    if pn is None:
        return {"label": label, "value": value, "color": color}
    return pn.pane.Markdown(
        f"**{label}**\n\n## {value}",
        styles={"color": color, "text-align": "center", "padding": "8px",
                "border": "1px solid #e0e0e0", "border-radius": "4px"},
    )


def render_gate_statistics(data: GateStatisticsData) -> dict[str, Any]:
    """Panel 渲染门禁统计（v3.1.0, #ARCH-047）

    布局:
      - 顶部: 汇总指标卡片(total_runs/pass_rate/block_rate)
      - 中部: 各门禁堆叠条形图(ChartFactory.make_gate_chart, pass绿/block红)
      - 底部: 各门禁明细表

    callback仅编排: 图表生成委托 ChartFactory.make_gate_chart.
    测试环境(无 panel)仅返回 dict payload, 便于断言.
    """
    by_gate_payload = [
        {
            "gate_id": g.gate_id,
            "total_runs": g.total_runs,
            "passed_runs": g.passed_runs,
            "failed_runs": g.failed_runs,
            "pass_rate": round(g.pass_rate, 4),
            "block_rate": round(g.block_rate, 4),
        }
        for g in data.by_gate
    ]

    payload: dict[str, Any] = {
        "total_runs": data.total_runs,
        "total_passed": data.total_passed,
        "total_failed": data.total_failed,
        "overall_pass_rate": round(data.overall_pass_rate, 4),
        "overall_block_rate": round(data.overall_block_rate, 4),
        "by_gate": by_gate_payload,
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    pass_color = "#28a745" if data.overall_pass_rate >= 0.9 else "#ffc107"
    block_color = "#dc3545" if data.overall_block_rate > 0.1 else "#28a745"

    metric_row = pn.Row(
        _metric_card("Total Runs", str(data.total_runs)),
        _metric_card("Pass Rate", f"{data.overall_pass_rate:.1%}", pass_color),
        _metric_card("Block Rate", f"{data.overall_block_rate:.1%}", block_color),
        sizing_mode="stretch_width",
    )

    layout_items: list[Any] = [
        pn.pane.Markdown("## 门禁统计 (Gate Statistics)"),
        metric_row,
    ]

    # 中部：各门禁堆叠条形图（ChartFactory 工厂方法）
    if data.by_gate:
        try:
            gate_fig = make_gate_chart(
                gate_stats=by_gate_payload,
                title="Pass/Block Rate by Gate",
            )
            layout_items.append(pn.pane.Markdown("### 各门禁通过率/阻断率"))
            layout_items.append(gate_fig)
        except ChartFactoryError:
            pass

        # 明细表
        rows = ["| Gate ID | Total | Passed | Failed | Pass Rate | Block Rate |",
                "|---|---|---|---|---|---|"]
        for g in by_gate_payload:
            rows.append(
                f"| {g['gate_id']} | {g['total_runs']} | {g['passed_runs']} | "
                f"{g['failed_runs']} | {g['pass_rate']:.1%} | {g['block_rate']:.1%} |"
            )
        layout_items.append(pn.pane.Markdown("\n".join(rows)))
    else:
        layout_items.append(pn.pane.Alert("无门禁统计数据（OLAPEngine 未配置）", alert_type="info"))

    layout = pn.Column(*layout_items, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__ = [
    "GateStat",
    "GateStatisticsData",
    "fetch_gate_statistics",
    "render_gate_statistics",
]
