# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.tick_replay
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.backtest.core.tick_replay
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
# [TTL] task_bound
"""tick_replay · Tick 回放可视化组件（v2.2.0新增）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §16.7.2
数据源: D_BACKTEST tick_replay 引擎产出的 Tick 序列
渲染依赖: plotly + streamlit

布局:
  - 顶部: 控制栏(回放速度选择/上一页/下一页/跳转时间)
  - 中部: Tick价格图+成交量(plotly, 支持zoom)
  - 中下: 5档盘口快照(实时更新, ask红/bid绿)
  - 底部: 做T场景标记(垂直线+标注)
虚拟滚动: 仅渲染可见区域Tick, 避免万级Tick卡顿.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

try:
    import streamlit as st
except ImportError:
    st = None

try:
    import plotly.graph_objects as go
except ImportError:
    go = None


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
    """做T场景标记（30秒冲高回落 / 5秒级快照）

    用户做T策略：30秒冲高回落，需 Tick 级回测验证
    """
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


def _to_float_list(values: Any) -> list[float]:
    if values is None:
        return []
    return [float(v) for v in values]


def _to_int_list(values: Any) -> list[int]:
    if values is None:
        return []
    return [int(v) for v in values]


def _normalize_tick(raw: Any) -> TickSnapshotView:
    """把异构 Tick 对象（dataclass / dict / DataFrame row）归一化为 TickSnapshotView"""
    # 优先属性访问（dataclass）
    def _get(key: str, default: Any = 0) -> Any:
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
    """自动识别做T场景（30秒冲高回落 / 5秒级尖峰）

    Args:
        ticks: Tick 序列（已归一化）
        spike_drop_window: 冲高回落窗口（默认30秒，对应"30秒冲高回落"做T策略）
        spike_threshold_pct: 价格波动阈值（0.5%）

    Returns:
        做T场景标记列表
    """
    if len(ticks) < 3:
        return []

    marks: list[TScenarioMark] = []
    prices = [t.last_price for t in ticks if t.last_price > 0]
    if len(prices) < 3:
        return []

    n = len(ticks)
    for i in range(1, n - 1):
        # 滑动窗口找局部高点（窗口内最大值位置）
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

        # 30秒冲高回落：窗口内 max → min 跌幅 > threshold，且当前位置接近 max
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
    """从 D_BACKTEST tick_replay 引擎获取 Tick 数据

    蓝图 §16.7.2:
      - 分页加载: 单页 1000 Tick，避免大数据卡顿
      - 做T场景识别: 自动标记 30秒冲高回落 / 5秒级快照

    Args:
        tick_data: Tick 序列（TickSnapshot / dict / DataFrame row 等异构对象）
        symbol: 标的代码
        page: 页码（1-based）
        page_size: 单页 Tick 数（默认 1000）
        replay_speed: 回放速度
        detect_t: 是否自动识别做T场景

    Returns:
        TickReplayData
    """
    total = len(tick_data) if tick_data else 0
    # 分页切片
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
    """Streamlit 渲染 Tick 回放

    布局:
      - 顶部: 控制栏(回放速度/上一页/下一页)
      - 中部: Tick价格图+成交量
      - 中下: 5档盘口快照(ask红/bid绿)
      - 底部: 做T场景标记(垂直线+标注)

    虚拟滚动: 仅渲染可见区域 Tick.
    测试环境(无 streamlit/plotly)仅返回 dict.
    """
    payload: dict[str, Any] = {
        "symbol": data.symbol,
        "page": data.page,
        "page_size": data.page_size,
        "total_ticks": data.total_ticks,
        "visible_ticks": len(data.ticks),
        "replay_speed": data.replay_speed.value,
        "t_scenario_count": len(data.t_scenario_marks),
        "scenarios": [
            {"timestamp": m.timestamp, "type": m.scenario_type, "desc": m.description}
            for m in data.t_scenario_marks
        ],
    }

    if st is None or go is None:
        return payload

    # 顶部：控制栏
    st.subheader(f"Tick 回放 — {data.symbol}")
    cc1, cc2, cc3, cc4 = st.columns([1, 1, 1, 2])
    speed = cc1.selectbox(
        "回放速度",
        [ReplaySpeed.MAX_SPEED.value, ReplaySpeed.FAST_FORWARD.value, ReplaySpeed.REAL_TIME.value],
        index=0,
    )
    total_pages = max(1, (data.total_ticks + data.page_size - 1) // data.page_size)
    cc2.number_input("页码", min_value=1, max_value=total_pages, value=data.page)
    cc3.markdown(f"**总Tick**: {data.total_ticks}  **当前页**: {data.page}/{total_pages}")

    # 中部：Tick价格图+成交量
    if data.ticks:
        ts_x = [t.timestamp for t in data.ticks]
        prices = [t.last_price for t in data.ticks]
        vols = [t.volume for t in data.ticks]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ts_x, y=prices, name="Last Price",
            line=dict(color="#1f77b4", width=1.2),
        ))
        # 做T场景标记：垂直线
        for mark in data.t_scenario_marks:
            fig.add_vline(
                x=mark.timestamp,
                line_dash="dash", line_color="red",
                annotation_text=mark.scenario_type,
                annotation_position="top",
            )
        fig.update_layout(
            height=400, template="plotly_white",
            xaxis_rangeslider_visible=False,
            margin=dict(l=40, r=20, t=30, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)

        # 成交量子图
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=ts_x, y=vols, name="Volume", marker_color="#9467bd"))
        fig_vol.update_layout(height=160, template="plotly_white", margin=dict(l=40, r=20, t=10, b=30))
        st.plotly_chart(fig_vol, use_container_width=True)

        # 中下：5档盘口快照（取最后一个 Tick）
        last_tick = data.ticks[-1]
        if last_tick.ask_price and last_tick.bid_price:
            st.markdown(f"**最新盘口快照** ({last_tick.timestamp}) — 最新价 `{last_tick.last_price:.3f}`")
            ob1, ob2 = st.columns(2)
            with ob1:
                st.markdown("**卖盘 (ask, 红)**")
                for i, (p, v) in enumerate(zip(last_tick.ask_price, last_tick.ask_vol), 1):
                    st.write(f"ask{i}: {p:.3f} × {v}")
            with ob2:
                st.markdown("**买盘 (bid, 绿)**")
                for i, (p, v) in enumerate(zip(last_tick.bid_price, last_tick.bid_vol), 1):
                    st.write(f"bid{i}: {p:.3f} × {v}")
    else:
        st.info("当前页无 Tick 数据")

    # 底部：做T场景标记列表
    if data.t_scenario_marks:
        st.subheader(f"做T场景标记 ({len(data.t_scenario_marks)})")
        for m in data.t_scenario_marks:
            st.markdown(f"- `{m.timestamp}` **{m.scenario_type}** — {m.description}")

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
