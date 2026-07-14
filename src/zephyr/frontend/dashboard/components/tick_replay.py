# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.tick_replay
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.dashboard.components.chart_factory; zephyr.backtest.core.tick_replay
# [CONSUMERS] zephyr.frontend.dashboard.app
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L08-001-tick_replay | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""tick_replay · Tick 回放可视化组件（v3.0.0 Panel+HoloViz 重构, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §16.7.2
数据源: D_BACKTEST tick_replay 引擎产出的 Tick 序列
渲染依赖: Panel(布局) + ChartFactory.make_tick(图表)

v3.0.0 变更 (#ARCH-047):
  - Streamlit -> Panel (布局)
  - plotly 直接调用 -> ChartFactory.make_tick (callback仅编排)
  - Datashader阈值触发(>50万点)由ChartFactory内置处理

布局:
  - 顶部: 控制栏(回放速度选择/页码/总Tick)
  - 中部: Tick价格图(ChartFactory.make_tick)+成交量
  - 中下: 5档盘口快照(ask红/bid绿)
  - 底部: 做T场景标记(垂直线+标注)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

from zephyr.frontend.dashboard.components.chart_factory import (
    ChartFactoryError,
    make_tick,
)


class ReplaySpeed(str, Enum):
    """回放速度"""
    REAL_TIME = "real_time"        # 实时(1x)
    FAST_FORWARD = "fast_forward"  # 快进(10x)
    MAX_SPEED = "max_speed"        # 最大(无延迟)


@dataclass
class TickSnapshotView:
    """前端展示用的 Tick 快照（剥离 Decimal 依赖，纯 float）"""
    timestamp: str = ""
    last_price: float = 0.0
    ask_price: list[float] = field(default_factory=list)  # 5档卖价
    bid_price: list[float] = field(default_factory=list)  # 5档买价
    ask_vol: list[int] = field(default_factory=list)      # 5档卖量
    bid_vol: list[int] = field(default_factory=list)      # 5档买量
    volume: int = 0
    amount: float = 0.0


@dataclass
class TScenarioMark:
    """做T场景标记（30秒冲高回落 / 5秒级快照）"""
    timestamp: str = ""
    scenario_type: str = ""  # "30s_spike_drop" / "5s_spike"
    description: str = ""


@dataclass
class TickReplayData:
    """Tick 回放可视化数据模型"""
    symbol: str = ""
    ticks: list[TickSnapshotView] = field(default_factory=list)
    replay_speed: ReplaySpeed = ReplaySpeed.MAX_SPEED
    t_scenario_marks: list[TScenarioMark] = field(default_factory=list)
    page: int = 1
    page_size: int = 1000
    total_ticks: int = 0


def _to_float_list(values: object) -> list[float]:
    if values is None:
        return []
    return [float(v) for v in values]


def _to_int_list(values: object) -> list[int]:
    if values is None:
        return []
    return [int(v) for v in values]


def _normalize_tick(raw: object) -> TickSnapshotView:
    """把异构 Tick 对象（dataclass / dict / DataFrame row）归一化为 TickSnapshotView"""
    def _get(key: str, default: object = 0) -> object:
        if hasattr(raw, key):
            return getattr(raw, key)
        if isinstance(raw, dict):
            return raw.get(key, default)
        return default

    ts = _get("timestamp", "")
    if ts and not isinstance(ts, str):
        ts = str(ts)

    return TickSnapshotView(
        timestamp=ts,
        last_price=float(_get("last_price", _get("lastPrice", 0.0)) or 0.0),
        ask_price=_to_float_list(_get("ask_price", _get("askPrice", []))),
        bid_price=_to_float_list(_get("bid_price", _get("bidPrice", []))),
        ask_vol=_to_int_list(_get("ask_vol", _get("askVol", []))),
        bid_vol=_to_int_list(_get("bid_vol", _get("bidVol", []))),
        volume=int(_get("volume", 0) or 0),
        amount=float(_get("amount", 0.0) or 0.0),
    )


def detect_t_scenarios(
    ticks: list[TickSnapshotView],
    spike_drop_window: int = 30,
    spike_threshold_pct: float = 0.005,
) -> list[TScenarioMark]:
    """自动识别做T场景（30秒冲高回落 / 5秒级尖峰）"""
    if len(ticks) < 3:
        return []

    marks: list[TScenarioMark] = []
    prices = [t.last_price for t in ticks if t.last_price > 0]
    if len(prices) < 3:
        return []

    n = len(ticks)
    for i in range(1, n - 1):
        window_start = max(0, i - spike_drop_window // 2)
        window_end = min(n, i + spike_drop_window // 2)
        window_prices = [ticks[j].last_price for j in range(window_start, window_end) if ticks[j].last_price > 0]
        if not window_prices:
            continue

        local_max = max(window_prices)
        local_min = min(window_prices)
        cur = ticks[i].last_price
        if cur <= 0 or local_max <= 0:
            continue

        drop_pct = (local_max - local_min) / local_max
        if drop_pct >= spike_threshold_pct and cur >= local_max * 0.999:
            marks.append(TScenarioMark(
                timestamp=ticks[i].timestamp,
                scenario_type="30s_spike_drop",
                description=f"冲高回落 高={local_max:.3f} 低={local_min:.3f} 跌幅={drop_pct:.2%}",
            ))

    return marks


def fetch_tick_replay(
    tick_data: list[Any],
    symbol: str,
    page: int = 1,
    page_size: int = 1000,
    replay_speed: ReplaySpeed = ReplaySpeed.MAX_SPEED,
    detect_t: bool = True,
) -> TickReplayData:
    """从 D_BACKTEST tick_replay 引擎获取 Tick 数据（纯函数，无副作用）

    蓝图 §16.7.2:
      - 分页加载: 单页 1000 Tick，避免大数据卡顿
      - 做T场景识别: 自动标记 30秒冲高回落 / 5秒级快照
    """
    total = len(tick_data) if tick_data else 0
    start_idx = max(0, (page - 1) * page_size)
    end_idx = min(total, start_idx + page_size)
    page_slice = list(tick_data[start_idx:end_idx]) if total > 0 else []

    ticks = [_normalize_tick(t) for t in page_slice]

    marks: list[TScenarioMark] = []
    if detect_t and ticks:
        marks = detect_t_scenarios(ticks)

    return TickReplayData(
        symbol=symbol,
        ticks=ticks,
        replay_speed=replay_speed,
        t_scenario_marks=marks,
        page=page,
        page_size=page_size,
        total_ticks=total,
    )


def render_tick_replay(data: TickReplayData) -> dict[str, Any]:
    """Panel+HoloViz 渲染 Tick 回放（v3.0.0, #ARCH-047）

    布局:
      - 顶部: 控制栏(回放速度/页码/总Tick)
      - 中部: Tick价格图(ChartFactory.make_tick)+成交量
      - 中下: 5档盘口快照(ask红/bid绿)
      - 底部: 做T场景标记

    callback仅编排: 图表生成委托 ChartFactory.make_tick.
    测试环境(无 panel)仅返回 dict payload.
    """
    total_pages = max(1, (data.total_ticks + data.page_size - 1) // data.page_size)

    payload: dict[str, Any] = {
        "symbol": data.symbol,
        "page": data.page,
        "page_size": data.page_size,
        "total_pages": total_pages,
        "total_ticks": data.total_ticks,
        "visible_ticks": len(data.ticks),
        "replay_speed": data.replay_speed.value,
        "t_scenario_count": len(data.t_scenario_marks),
        "scenarios": [
            {"timestamp": m.timestamp, "type": m.scenario_type, "desc": m.description}
            for m in data.t_scenario_marks
        ],
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    # ===== 顶部：控制栏 =====
    speed_select = pn.widgets.Select(
        name="回放速度",
        options=[s.value for s in ReplaySpeed],
        value=data.replay_speed.value,
        width=150,
    )
    page_input = pn.widgets.IntInput(
        name="页码",
        start=1,
        end=total_pages,
        value=data.page,
        width=100,
    )
    info_pane = pn.pane.Markdown(
        f"**总Tick**: {data.total_ticks}  **当前页**: {data.page}/{total_pages}",
        width=200,
    )
    control_row = pn.Row(speed_select, page_input, info_pane, sizing_mode="stretch_width")

    layout_items: list[Any] = [
        pn.pane.Markdown(f"## Tick 回放 — {data.symbol}"),
        control_row,
    ]

    # ===== 中部：Tick价格图 + 成交量 =====
    if data.ticks:
        ts_x = [t.timestamp for t in data.ticks]
        prices = [t.last_price for t in data.ticks]

        try:
            tick_fig = make_tick(
                tick_data=prices,
                timestamps=ts_x,
                title=f"Tick Price — {data.symbol}",
                height=400,
            )
            layout_items.append(tick_fig)
        except ChartFactoryError:
            pass

        # 成交量简表（用 Markdown 表格替代 plotly.Bar，避免直接 plotly 调用）
        vol_lines = []
        for i, t in enumerate(data.ticks[:20]):  # 仅展示前20条避免过长
            vol_lines.append(f"| {t.timestamp} | {t.volume} | {t.amount:.0f} |")
        if vol_lines:
            vol_md = (
                "### 成交量(前20条)\n\n"
                "| Timestamp | Volume | Amount |\n|---|---|---|\n"
                + "\n".join(vol_lines)
            )
            layout_items.append(pn.pane.Markdown(vol_md))

        # ===== 中下：5档盘口快照（取最后一个 Tick）=====
        last_tick = data.ticks[-1]
        if last_tick.ask_price and last_tick.bid_price:
            ask_md = "**卖盘 (ask, 红)**\n\n"
            for i, (p, v) in enumerate(zip(last_tick.ask_price, last_tick.ask_vol), 1):
                ask_md += f"- ask{i}: {p:.3f} × {v}\n"
            bid_md = "**买盘 (bid, 绿)**\n\n"
            for i, (p, v) in enumerate(zip(last_tick.bid_price, last_tick.bid_vol), 1):
                bid_md += f"- bid{i}: {p:.3f} × {v}\n"
            ob_row = pn.Row(
                pn.pane.Markdown(ask_md, styles={"color": "#dc3545", "flex": "1"}),
                pn.pane.Markdown(
                    f"**最新价**\n\n## {last_tick.last_price:.3f}",
                    styles={"text-align": "center", "flex": "1"},
                ),
                pn.pane.Markdown(bid_md, styles={"color": "#28a745", "flex": "1"}),
                sizing_mode="stretch_width",
            )
            layout_items.append(pn.pane.Markdown(f"### 最新盘口快照 ({last_tick.timestamp})"))
            layout_items.append(ob_row)
    else:
        layout_items.append(pn.pane.Alert("当前页无 Tick 数据", alert_type="info"))

    # ===== 底部：做T场景标记 =====
    if data.t_scenario_marks:
        marks_md = f"### 做T场景标记 ({len(data.t_scenario_marks)})\n\n"
        for m in data.t_scenario_marks:
            marks_md += f"- `{m.timestamp}` **{m.scenario_type}** — {m.description}\n"
        layout_items.append(pn.pane.Markdown(marks_md))

    layout = pn.Column(*layout_items, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__ = [
    "ReplaySpeed",
    "TickSnapshotView",
    "TScenarioMark",
    "TickReplayData",
    "fetch_tick_replay",
    "render_tick_replay",
    "detect_t_scenarios",
]
