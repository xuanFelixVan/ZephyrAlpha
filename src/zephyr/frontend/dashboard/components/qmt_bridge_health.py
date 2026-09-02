# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint_qmt_bridge_health.md
# [MODULE] zephyr.frontend.dashboard.components.qmt_bridge_health
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.shared.utils.time_utils
# [CONSUMERS] zephyr.frontend.dashboard.app_panel
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] fail-closed(assembly未注入/异常→空态); 阈值不前端化(只读level+detail)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/frontend/dashboard/components/test_qmt_bridge_health.py
# [A_module] module_id=MOD-L28-QMTBH | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""qmt_bridge_health · QMT 文件桥健康监控面板组件（蓝图 v0.1.0）

蓝图规格: docs/03_modules/_domain_frontend/blueprint_qmt_bridge_health.md
数据源: QmtFileBridgeAssembly.health_check()（ex_core，commit b907bfbe）
渲染依赖: Panel（可选导入，测试环境零依赖仅返回 dict payload）

设计要点:
  - 三级状态映射: ok(绿●)/degraded(黄▲)/down(红■)
  - 总状态横幅 + 每组件卡片（broker/queue/quote）
  - fail-closed: assembly 未注入或异常 → 空态"未装配"，不炸面板
  - 健康判定阈值全在后端 API，本组件只读 level+detail（防第二真源）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

from zephyr.shared.utils.time_utils import now_utc

# level → (alert_type, 图标, 中文语义)
_LEVEL_VISUAL: Final[dict[str, tuple[str, str, str]]] = {
    "ok": ("success", "●", "正常"),
    "degraded": ("warning", "▲", "降级"),
    "down": ("danger", "■", "中断"),
}


@dataclass
class ComponentHealth:
    """单组件健康视图"""

    name: str  # broker_sim / queue_qmt_sim / quote_real ...
    type: str  # broker / order_queue / quote_provider
    level: str  # ok / degraded / down
    detail: str = ""  # 排障提示（空=正常）
    metrics: dict = field(default_factory=dict)  # 关键指标透传


@dataclass
class QmtBridgeHealthData:
    """面板数据（fetch 输出）"""

    assembled: bool  # assembly 是否注入
    overall_level: str  # 聚合等级
    components: list[ComponentHealth] = field(default_factory=list)
    checked_at: str = ""  # 检查时刻（展示用）


def _component_metrics(comp_type: str, raw: dict) -> dict:
    """按组件类型提取关键指标（原样透传，不做阈值判定）"""
    if comp_type == "broker":
        counter = raw.get("counter", {})
        return {
            "导出延迟(s)": raw.get("export_age_seconds", {}),
            "在途挂单": counter.get("pending_orders", 0),
            "持仓数": counter.get("positions", 0),
            "可用资金": counter.get("available_cash", "0"),
        }
    if comp_type == "quote_provider":
        return {
            "文件延迟(s)": raw.get("file_age_seconds", "-"),
            "新鲜": raw.get("fresh", False),
        }
    if comp_type == "order_queue":
        return {
            "待发": raw.get("pending", 0),
            "已发": raw.get("sent", 0),
            "失败": raw.get("failed", 0),
        }
    return {}


def fetch_qmt_bridge_health(assembly: object) -> QmtBridgeHealthData:
    """从 Assembly 聚合健康端点取数（纯函数，fail-closed）

    蓝图 §4.2: assembly None/异常 → QmtBridgeHealthData(assembled=False)
    """
    checked_at = now_utc().astimezone().strftime("%H:%M:%S")
    empty = QmtBridgeHealthData(
        assembled=False,
        overall_level="down",
        checked_at=checked_at,
    )
    if assembly is None:
        return empty

    try:
        raw = assembly.health_check()
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return empty

    if not isinstance(raw, dict):
        return empty

    components: list[ComponentHealth] = []
    for name, comp in (raw.get("components") or {}).items():
        comp_type = comp.get("type", "")
        components.append(
            ComponentHealth(
                name=name,
                type=comp_type,
                level=comp.get("level", "down"),
                detail=comp.get("detail", ""),
                metrics=_component_metrics(comp_type, comp),
            )
        )

    return QmtBridgeHealthData(
        assembled=True,
        overall_level=raw.get("level", "down"),
        components=components,
        checked_at=checked_at,
    )


def _level_visual(level: str) -> tuple[str, str, str]:
    return _LEVEL_VISUAL.get(level, _LEVEL_VISUAL["down"])


def _format_metrics(metrics: dict) -> str:
    """指标 dict → Markdown 文本（导出延迟嵌套 dict 特殊展开）"""
    lines: list[str] = []
    for key, value in metrics.items():
        if isinstance(value, dict):
            inner = " ".join(f"{k}={v}" for k, v in value.items() if v is not None)
            lines.append(f"- {key}: {inner}" if inner else f"- {key}: -")
        else:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def render_qmt_bridge_health(data: QmtBridgeHealthData) -> dict[str, Any]:
    """渲染健康面板（payload + '_layout' 挂 Panel 布局）

    布局: 总状态横幅(Alert) + 组件卡片网格(pn.Card)。
    测试环境(无 panel)仅返回 dict payload。
    """
    alert_type, icon, level_text = _level_visual(data.overall_level)
    payload: dict[str, Any] = {
        "assembled": data.assembled,
        "overall_level": data.overall_level,
        "checked_at": data.checked_at,
        "components": [
            {
                "name": c.name,
                "type": c.type,
                "level": c.level,
                "detail": c.detail,
                "metrics": c.metrics,
            }
            for c in data.components
        ],
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    layout_items: list[Any] = [pn.pane.Markdown("## QMT 文件桥健康监控")]

    if not data.assembled:
        layout_items.append(pn.pane.Alert("QMT 文件桥未装配（qmt_assembly 未注入）", alert_type="info"))
        layout = pn.Column(*layout_items, sizing_mode="stretch_width")
        payload["_layout"] = layout
        return payload

    # 总状态横幅
    layout_items.append(
        pn.pane.Alert(
            f"{icon} 文件桥整体: {level_text}（{data.overall_level}） — 检查于 {data.checked_at}",
            alert_type=alert_type,
        )
    )

    # 组件卡片
    cards: list[Any] = []
    for comp in data.components:
        c_alert, c_icon, c_text = _level_visual(comp.level)
        body_parts = [f"**状态**: {c_icon} {c_text}（{comp.level}）"]
        if comp.detail:
            body_parts.append(f"**原因**: {comp.detail}")
        metrics_text = _format_metrics(comp.metrics)
        if metrics_text:
            body_parts.append(metrics_text)
        cards.append(
            pn.Card(
                pn.pane.Markdown("\n\n".join(body_parts)),
                title=f"{c_icon} {comp.name}",
                sizing_mode="stretch_width",
            )
        )
    if cards:
        layout_items.append(pn.GridBox(*cards, ncols=2, sizing_mode="stretch_width"))

    layout = pn.Column(*layout_items, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__: Final = [
    "ComponentHealth",
    "QmtBridgeHealthData",
    "fetch_qmt_bridge_health",
    "render_qmt_bridge_health",
]
