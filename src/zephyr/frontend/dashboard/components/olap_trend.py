# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.olap_trend
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
# [A_module] module_id=MOD-UNK_olap_trend | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-4-07 OLAP Trend Component
"""olap_trend · OLAP 趋势组件（v3.1.0 Panel 迁移, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §3.1
数据源: OLAPEngine.task_progress_trend/compliance_rate_trend/knowledge_activation_trend
渲染依赖: Panel(布局) + ChartFactory.make_trend_line(趋势折线图)

v3.1.0 变更 (#ARCH-047):
  - Streamlit(st.dataframe) → Panel(pn.pane.Markdown 表格 + ChartFactory.make_trend_line)
  - 图表生成委托 ChartFactory.make_trend_line (callback仅编排)
  - 测试环境(无 panel)仅返回 dict payload, 便于断言
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass, field
from typing import Any, Optional

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

from zephyr.frontend.dashboard.components.chart_factory import (
    ChartFactoryError,
    make_trend_line,
)

# 常见的时间/周期键名（用于从 list[dict] 提取 X 轴）
_TIME_KEYS = ("period", "date", "time", "timestamp", "day", "month", "dt", "x")


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
    except Exception as e:
        logger.warning("suppressed error in olap_trend", exc_info=True)
    try:
        data.compliance_rate = olap_engine.compliance_rate_trend(period=period, limit=limit)
    except Exception as e:
        logger.warning("suppressed error in olap_trend", exc_info=True)
    try:
        data.knowledge_activation = olap_engine.knowledge_activation_trend(period="month", limit=12)
    except Exception as e:
        logger.warning("suppressed error in olap_trend", exc_info=True)
    return data


def _extract_xy(rows: list[dict[str, Any]]) -> tuple[list[str], list[float], Optional[str]]:
    """从 list[dict] 启发式提取 X(时间)/Y(数值) 序列及 Y 轴字段名。

    策略: X 取第一个匹配 _TIME_KEYS 的字段；Y 取第一个数值型非时间字段。
    返回: (x_labels, y_values, y_field_name) — 提取失败时 y_values 为空
    """
    if not rows or not isinstance(rows[0], dict):
        return [], [], None

    keys = list(rows[0].keys())
    x_field: Optional[str] = None
    for k in keys:
        if k.lower() in _TIME_KEYS:
            x_field = k
            break
    if x_field is None and keys:
        x_field = keys[0]

    y_field: Optional[str] = None
    for k in keys:
        if k == x_field:
            continue
        try:
            float(rows[0].get(k, 0))
            y_field = k
            break
        except (TypeError, ValueError):
            continue

    if y_field is None:
        return [], [], None

    x_labels = [str(r.get(x_field, "")) for r in rows]
    y_values: list[float] = []
    for r in rows:
        try:
            y_values.append(float(r.get(y_field, 0)))
        except (TypeError, ValueError):
            y_values.append(0.0)
    return x_labels, y_values, y_field


def _trend_section(title: str, rows: list[dict[str, Any]], color: str) -> list[Any]:
    """构建单个趋势区块（折线图 + 数据表），返回 Panel 组件列表"""
    items: list[Any] = [pn.pane.Markdown(f"### {title}")]
    x_labels, y_values, y_field = _extract_xy(rows)
    if y_values:
        try:
            fig = make_trend_line(
                y_values=y_values,
                x_labels=x_labels,
                title=title,
                color=color,
                y_title=y_field or "Value",
            )
            items.append(fig)
        except ChartFactoryError:
            pass

    # 数据表
    if rows:
        keys = list(rows[0].keys())
        header = "| " + " | ".join(keys) + " |"
        sep = "| " + " | ".join("---" for _ in keys) + " |"
        lines = [header, sep]
        for r in rows[:50]:  # 仅展示前50行
            lines.append("| " + " | ".join(str(r.get(k, "")) for k in keys) + " |")
        items.append(pn.pane.Markdown("\n".join(lines)))
    return items


def render_olap_trends(data: OLAPTrendData) -> dict[str, Any]:
    """Panel 渲染 OLAP 趋势（v3.1.0, #ARCH-047）

    布局:
      - 任务进度趋势(ChartFactory.make_trend_line, 蓝色)
      - 合规率趋势(ChartFactory.make_trend_line, 绿色)
      - 知识激活趋势(ChartFactory.make_trend_line, 橙色)

    callback仅编排: 图表生成委托 ChartFactory.make_trend_line.
    测试环境(无 panel)仅返回 dict payload, 便于断言.
    """
    payload: dict[str, Any] = {
        "task_progress": data.task_progress,
        "compliance_rate": data.compliance_rate,
        "knowledge_activation": data.knowledge_activation,
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    layout_items: list[Any] = [pn.pane.Markdown("## OLAP 趋势 (OLAP Trends)")]

    has_data = False
    layout_items += _trend_section("任务进度趋势", data.task_progress, "#1f77b4")
    layout_items += _trend_section("合规率趋势", data.compliance_rate, "#28a745")
    layout_items += _trend_section("知识激活趋势", data.knowledge_activation, "#fd7e14")

    if data.task_progress:
        has_data = True
    if data.compliance_rate:
        has_data = True
    if data.knowledge_activation:
        has_data = True

    if not has_data:
        layout_items.append(pn.pane.Alert("无 OLAP 趋势数据（OLAPEngine 未配置）", alert_type="info"))

    layout = pn.Column(*layout_items, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__ = [
    "OLAPTrendData",
    "fetch_olap_trends",
    "render_olap_trends",
]
