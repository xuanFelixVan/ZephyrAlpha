# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.knowledge_overview
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_knowledge_overview | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-4-07 Knowledge Overview Component
"""knowledge_overview · 知识库概览组件（v3.1.0 Panel 迁移, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §3.1
数据源: KbRepo（当前 fetch 返回空 dataclass, 待上游施工后填充）
渲染依赖: Panel(布局) — 指标卡片+分布表，无专业图表需求故不调用 ChartFactory

v3.1.0 变更 (#ARCH-047):
  - Streamlit(st.metric) -> Panel(pn.pane.Markdown 指标卡片 + 分布表)
  - callback仅编排: 数据计算在 fetch_knowledge_overview(纯函数)
  - 测试环境(无 panel)仅返回 dict payload, 便于断言
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None


@dataclass
class KnowledgeStatusDistribution:
    status: str
    count: int = 0


@dataclass
class KnowledgeOverviewData:
    total_entries: int = 0
    activated_entries: int = 0
    activation_rate: float = 0.0
    status_distribution: list[KnowledgeStatusDistribution] = field(default_factory=list)
    category_distribution: dict[str, int] = field(default_factory=dict)


def fetch_knowledge_overview() -> KnowledgeOverviewData:
    return KnowledgeOverviewData()


def _metric_card(label: str, value: str, color: str = "#333") -> Any:
    if pn is None:
        return {"label": label, "value": value, "color": color}
    return pn.pane.Markdown(
        f"**{label}**\n\n## {value}",
        styles={"color": color, "text-align": "center", "padding": "8px",
                "border": "1px solid #e0e0e0", "border-radius": "4px"},
    )


def render_knowledge_overview(data: KnowledgeOverviewData) -> dict[str, Any]:
    """Panel 渲染知识库概览（v3.1.0, #ARCH-047）

    布局:
      - 顶部: 汇总指标卡片(total_entries/activated_entries/activation_rate)
      - 中部: 状态分布表
      - 底部: 分类分布表

    callback仅编排: 数据计算在 fetch_knowledge_overview(纯函数).
    测试环境(无 panel)仅返回 dict payload, 便于断言.
    """
    payload: dict[str, Any] = {
        "total_entries": data.total_entries,
        "activated_entries": data.activated_entries,
        "activation_rate": round(data.activation_rate, 4),
        "status_distribution": [{"status": d.status, "count": d.count} for d in data.status_distribution],
        "category_distribution": data.category_distribution,
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    rate_color = "#28a745" if data.activation_rate >= 0.5 else "#ffc107"

    metric_row = pn.Row(
        _metric_card("Total Entries", str(data.total_entries)),
        _metric_card("Activated", str(data.activated_entries)),
        _metric_card("Activation Rate", f"{data.activation_rate:.1%}", rate_color),
        sizing_mode="stretch_width",
    )

    layout_items: list[Any] = [
        pn.pane.Markdown("## 知识库概览 (Knowledge Overview)"),
        metric_row,
    ]

    if data.status_distribution:
        rows = ["| Status | Count |", "|---|---|"]
        for d in data.status_distribution:
            rows.append(f"| {d.status} | {d.count} |")
        layout_items.append(pn.pane.Markdown("### 状态分布\n\n" + "\n".join(rows)))

    if data.category_distribution:
        rows = ["| Category | Count |", "|---|---|"]
        for cat, cnt in data.category_distribution.items():
            rows.append(f"| {cat} | {cnt} |")
        layout_items.append(pn.pane.Markdown("### 分类分布\n\n" + "\n".join(rows)))

    if not data.status_distribution and not data.category_distribution:
        layout_items.append(pn.pane.Alert("无知识库数据（KbRepo 未配置）", alert_type="info"))

    layout = pn.Column(*layout_items, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__ = [
    "KnowledgeStatusDistribution",
    "KnowledgeOverviewData",
    "fetch_knowledge_overview",
    "render_knowledge_overview",
]
