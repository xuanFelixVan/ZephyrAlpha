# [MODULE] zephyr.frontend.dashboard.components.connection_matrix
# create-guard-not-dup: 全连接矩阵仪表盘组件（图族边面读侧），非 architecture_health_dashboard 第二实现——命中词=共用健康/矩阵面板措辞
# [AI_AUTONOMY] ai_modifiable
# [SAFETY] L
# [STABILITY] stable
# [MODIFY-GUARD] none（纯读侧组件，零判据逻辑）
# [BLUEPRINT] MOD-FE-018 | docs/03_modules/_domain_frontend/blueprint.md
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] panel（可缺）; json; pathlib; zephyr.shared.utils.time_utils（禁 datetime.now，RULE-SCHEMA-TZ）
# [CONSUMERS] zephyr.frontend.dashboard.app_panel.DashboardPanelApp._tab_connection_matrix（build_tabs 唯一入口）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 本组件是**数据源读侧**，零判据逻辑：矩阵四态与差集全部由生成器算出，
#              此处只按 mtime 缓存读产物（改产物即自动失效，无需重启）；产物缺失时
#              显式显示"未生成"，绝不现场重算（第二真源禁令）
# [ERROR_CONTRACT] fetch 不抛异常——产物缺失/JSON 损坏返回 ok=False + reason，面板降级披露
# [TESTS] tests/governance/test_connection_matrix_rulers.py
# [TTL] permanent
# [ARCH-REF] #ARCH-365 (包 13.4)
# [CREATION-TOKEN] pending-registration: wave13-p3-matrix-20260926（总筹合批登记）
"""connection_matrix — 全连接矩阵仪表盘面板（波 13 包 13.4，只当数据源）。

大白话：读生成器落好的矩阵产物，把"该连未连"的头条数和六类边的分母摊给人看。
分母按边类分开列，是因为第一号红线就在两处：把"没人声明"看成"接线断了"，或者反过来。
# [ALGO_FLOW] external: docs/03_modules/_domain_frontend/algo_flow/connection_matrix.yaml
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

try:  # 测试/脚本环境无 panel 时降级为纯 dict payload
    import panel as pn
except Exception:  # noqa: BLE001 — 可选依赖缺失不是错误
    pn = None  # type: ignore[assignment]

__all__: Final = ["ConnectionMatrixData", "fetch_connection_matrix", "render_connection_matrix"]

_REPO_ROOT = Path(__file__).resolve().parents[5]
ARTIFACT_PATH = _REPO_ROOT / "data" / "runtime" / "connection_matrix" / "connection_matrix.json"
CSV_PATH = _REPO_ROOT / "docs" / "_working" / "decision_map_campaign_20260924" / "connection_matrix.csv"

_CACHE: Final[dict[str, Any]] = {"mtime": None, "payload": None}  # mtime 缓存（产物变即重读）
_EDGE_LABELS: dict[str, str] = {  # 边类原文键（不做翻译字典，词表真源在生成器 EDGE_TYPES）
    "data_source__collection_leg": "数据源 → 采集腿",
    "collection_leg__table": "采集腿 → 表",
    "table__factor": "表 → 因子",
    "factor__strategy": "因子 → 策略",
    "strategy__tdm_node": "策略 → 决策地图节点",
    "tdm_node__execution_path": "节点 → 执行路径",
}


@dataclass
class ConnectionMatrixData:
    ok: bool = False
    reason: str = ""
    headline: dict[str, Any] = field(default_factory=dict)
    denominators: dict[str, dict[str, int]] = field(default_factory=dict)
    difference_set: list[dict[str, str]] = field(default_factory=list)
    missing_wiring: list[dict[str, str]] = field(default_factory=list)
    clickhouse: dict[str, Any] = field(default_factory=dict)
    scope_stats: dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""


def fetch_connection_matrix(artifact: Path | None = None) -> ConnectionMatrixData:
    """按 mtime 缓存读矩阵产物（数据源只读，重算属生成器职责）。"""
    p = Path(artifact) if artifact else ARTIFACT_PATH
    if not p.exists():
        return ConnectionMatrixData(
            ok=False,
            reason=f"矩阵产物未生成：先跑 scripts/governance/d5_architecture/generators/"
            f"generate_connection_matrix.py（期望路径 {p}）",
        )
    mtime = p.stat().st_mtime
    if _CACHE["mtime"] == mtime and isinstance(_CACHE["payload"], dict):
        raw = _CACHE["payload"]
    else:
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return ConnectionMatrixData(ok=False, reason=f"产物读取失败: {type(exc).__name__}: {exc}")
        _CACHE["mtime"] = mtime
        _CACHE["payload"] = raw
    return ConnectionMatrixData(
        ok=bool(raw.get("ok")),
        reason=str(raw.get("reason") or ""),
        headline=dict(raw.get("headline") or {}),
        denominators=dict(raw.get("denominators_by_edge_type") or {}),
        difference_set=list(raw.get("difference_set") or []),
        missing_wiring=list(raw.get("missing_wiring") or []),
        clickhouse=dict(raw.get("clickhouse") or {}),
        scope_stats=dict(raw.get("scope_stats") or {}),
        generated_at=str(raw.get("generated_at") or ""),
    )


def _card(label: str, value: str, color: str = "#333") -> Any:
    if pn is None:
        return {"label": label, "value": value, "color": color}
    return pn.pane.Markdown(f"**{label}**\n\n## {value}", styles={"color": color, "text-align": "center"})


def render_connection_matrix(data: ConnectionMatrixData) -> dict[str, Any]:
    """渲染：头条差集数 + 六类边分母表 + 差集/悬空明细（三块缺一不可）。

    分母表把 NO_DECLARED_EDGE 与 MISSING_WIRING 并列成两列——人一眼分得清
    "没人声明过" 与 "声明了但断了"，这是本面板存在的理由。
    """
    payload: dict[str, Any] = {
        "ok": data.ok,
        "reason": data.reason,
        "headline": data.headline,
        "generated_at": data.generated_at,
        "clickhouse": data.clickhouse,
        "table_rows": [],
    }
    for et in _EDGE_LABELS:
        c = data.denominators.get(et) or {}
        payload["table_rows"].append(
            {
                "edge_type": et,
                "edge_label": _EDGE_LABELS[et],
                "wired": c.get("WIRED", 0),
                "difference": c.get("SHOULD_NOT_WIRED_BUT_ISN'T", 0),
                "missing_wiring": c.get("MISSING_WIRING", 0),
                "no_declared_edge": c.get("NO_DECLARED_EDGE", 0),
                "total": c.get("total", 0),
            }
        )

    if pn is None:
        return payload

    if not data.ok:
        return {**payload, "_layout": pn.pane.Alert(f"⚠️ {data.reason}", alert_type="warning")}

    cards = pn.Row(
        _card("该连未连（差集）", str(data.headline.get("difference_set_count", 0)), "#c0392b"),
        _card("指针悬空", str(data.headline.get("missing_wiring_count", 0)), "#e67e22"),
        _card("已连通", str(data.headline.get("wired_count", 0)), "#16a085"),
        _card("声明缺失（不入差集）", str(data.headline.get("no_declared_edge_count", 0)), "#7f8c8d"),
        sizing_mode="stretch_width",
    )
    import pandas as pd

    denom_df = pd.DataFrame(payload["table_rows"])
    ch = data.clickhouse.get("channel", "")
    unreach = data.clickhouse.get("unreachable", 0)
    meta = pn.pane.Markdown(
        f"产物生成时间 `{data.generated_at or '?'}` · 读数通道 `{ch}`"
        f'（CH 不可达降级 {unreach} 次，绝不折算成"表不存在"） · '
        f"扫描口径 §3.4（{data.scope_stats.get('scope_files_scanned', '?')} 文件） · "
        f"明细 CSV：`{CSV_PATH.relative_to(_REPO_ROOT).as_posix()}`"
    )
    diff_df = pd.DataFrame(data.difference_set)
    miss_df = pd.DataFrame(data.missing_wiring)
    layout = pn.Column(
        cards,
        meta,
        pn.pane.Markdown("### 六类边分母（务必分列看：声明缺失 ≠ 接线断了）"),
        pn.pane.DataFrame(denom_df, index=False, sizing_mode="stretch_width"),
        pn.pane.Markdown(f"### 该连未连明细（{len(diff_df)} 条，差集全量）"),
        pn.pane.DataFrame(diff_df, index=False, sizing_mode="stretch_width")
        if not diff_df.empty
        else pn.pane.Markdown("_差集为空——所有在册应连边都已接上_"),
        pn.pane.Markdown(f"### 指针悬空明细（{len(miss_df)} 条）"),
        pn.pane.DataFrame(miss_df, index=False, sizing_mode="stretch_width")
        if not miss_df.empty
        else pn.pane.Markdown("_无悬空指针_"),
        sizing_mode="stretch_width",
    )
    payload["_layout"] = layout
    return payload
