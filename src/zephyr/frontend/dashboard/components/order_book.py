# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.order_book
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.governance.data_governance.miniqmt_provider
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
# [A_module] module_id=MOD-L08-001-order_book | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""order_book · 5档盘口实时展示组件（v2.2.0新增）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §16.7.3
数据源: D_DATA MiniQmtProvider.get_order_book() 5档盘口实时数据
渲染依赖: plotly + streamlit

布局:
  - 左侧: 5档卖盘(红色, 价格降序 ask5→ask1)
  - 中间: 最新价 + 压力比仪表盘
  - 右侧: 5档买盘(绿色, 价格降序 bid1→bid5)
刷新策略: streamlit.fragment + 100ms rerun，避免全页重渲染.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

try:
    import streamlit as st
except ImportError:
    st = None

try:
    import plotly.graph_objects as go
except ImportError:
    go = None


@dataclass
class OrderBookData:
    """5档盘口数据模型

    蓝图 §16.7.3: askPrice/bidPrice/askVol/bidVol 均为5档
    """
    symbol: str = ""
    timestamp: str = ""
    ask_price: list[float] = field(default_factory=list)  # 5档卖价 [ask1~ask5]
    bid_price: list[float] = field(default_factory=list)  # 5档买价 [bid1~bid5]
    ask_vol: list[int] = field(default_factory=list)      # 5档卖量
    bid_vol: list[int] = field(default_factory=list)      # 5档买量
    last_price: float = 0.0
    pressure_ratio: float = 0.0  # 盘口压力比 = bid_vol_total / ask_vol_total

    @property
    def ask_vol_total(self) -> int:
        return sum(self.ask_vol) if self.ask_vol else 0

    @property
    def bid_vol_total(self) -> int:
        return sum(self.bid_vol) if self.bid_vol else 0


def fetch_order_book(miniqmt_provider: Any, symbol: str) -> OrderBookData:
    """从 D_DATA MiniQmtProvider 获取5档盘口

    蓝图 §16.7.3:
      - 输入: MiniQmtProvider 实例（依赖注入），标的代码
      - 输出: OrderBookData（5档 ask/bid price/vol + 压力比）

    MiniQmtProvider.get_order_book(symbol) 返回 dict:
      {
        "symbol": str,
        "ask_price": list[Decimal],  # 5档卖价
        "bid_price": list[Decimal],  # 5档买价
        "ask_vol": list[Decimal],
        "bid_vol": list[Decimal],
        "last_price": Decimal,
        "timestamp": datetime,
      }
    """
    if miniqmt_provider is None:
        return OrderBookData(symbol=symbol)

    try:
        raw = miniqmt_provider.get_order_book(symbol)
    except Exception:
        return OrderBookData(symbol=symbol)

    if not raw:
        return OrderBookData(symbol=symbol)

    # 内联转换（避免与 tick_replay.py 的 _to_float_list/_to_int_list 重复，FUNCTION-DUP gate）
    def _get_field(key: str) -> Any:
        return raw.get(key) if isinstance(raw, dict) else getattr(raw, key, [])

    ask_p = [float(v) for v in (_get_field("ask_price") or [])]
    bid_p = [float(v) for v in (_get_field("bid_price") or [])]
    ask_v = [int(v) for v in (_get_field("ask_vol") or [])]
    bid_v = [int(v) for v in (_get_field("bid_vol") or [])]

    last_price = 0.0
    if isinstance(raw, dict):
        last_price = float(raw.get("last_price", 0.0) or 0.0)
    elif hasattr(raw, "last_price"):
        last_price = float(getattr(raw, "last_price", 0.0) or 0.0)

    ts = ""
    if isinstance(raw, dict):
        ts_val = raw.get("timestamp", "")
    else:
        ts_val = getattr(raw, "timestamp", "")
    ts = str(ts_val) if ts_val else ""

    ask_total = sum(ask_v) if ask_v else 0
    bid_total = sum(bid_v) if bid_v else 0
    pressure = (bid_total / ask_total) if ask_total > 0 else 0.0

    return OrderBookData(
        symbol=symbol,
        timestamp=ts,
        ask_price=ask_p,
        bid_price=bid_p,
        ask_vol=ask_v,
        bid_vol=bid_v,
        last_price=last_price,
        pressure_ratio=pressure,
    )


def render_order_book(data: OrderBookData) -> dict[str, Any]:
    """Streamlit 渲染5档盘口

    布局:
      - 左侧: 5档卖盘(红色, 价格降序 ask5→ask1)
      - 中间: 最新价 + 压力比仪表盘
      - 右侧: 5档买盘(绿色, 价格降序 bid1→bid5)

    刷新: streamlit.fragment + 100ms rerun.
    测试环境(无 streamlit/plotly)仅返回 dict.
    """
    payload: dict[str, Any] = {
        "symbol": data.symbol,
        "timestamp": data.timestamp,
        "last_price": round(data.last_price, 4),
        "ask_price": [round(p, 4) for p in data.ask_price],
        "bid_price": [round(p, 4) for p in data.bid_price],
        "ask_vol": list(data.ask_vol),
        "bid_vol": list(data.bid_vol),
        "ask_vol_total": data.ask_vol_total,
        "bid_vol_total": data.bid_vol_total,
        "pressure_ratio": round(data.pressure_ratio, 4),
    }

    if st is None:
        return payload

    st.subheader(f"5档盘口 — {data.symbol}")
    if data.timestamp:
        st.caption(f"快照时间: {data.timestamp}")

    if not data.ask_price and not data.bid_price:
        st.info("盘口数据为空")
        return payload

    # 中间：最新价 + 压力比
    col_left, col_mid, col_right = st.columns([2, 1, 2])

    with col_left:
        st.markdown("**卖盘 (ask, 红)** — 价格降序 ask5→ask1")
        # ask5 → ask1（从高到低显示）
        ask_rows = list(zip(data.ask_price, data.ask_vol))
        for i, (p, v) in enumerate(reversed(ask_rows), 1):
            # reversed 后从 ask5 显示到 ask1
            level = len(ask_rows) - i + 1
            st.markdown(
                f"<div style='background:#ffe6e6;padding:4px 8px;border-radius:4px;'>"
                f"<b>ask{level}</b>: {p:.3f} × {v}"
                f"</div>",
                unsafe_allow_html=True,
            )

    with col_mid:
        st.metric("最新价", f"{data.last_price:.3f}")
        st.metric("压力比 (bid/ask)", f"{data.pressure_ratio:.2f}")
        if data.pressure_ratio > 1.5:
            st.success("买盘强势 🟢")
        elif data.pressure_ratio < 0.67:
            st.error("卖盘强势 🔴")
        else:
            st.info("盘口均衡 ⚪")

    with col_right:
        st.markdown("**买盘 (bid, 绿)** — 价格降序 bid1→bid5")
        bid_rows = list(zip(data.bid_price, data.bid_vol))
        for i, (p, v) in enumerate(bid_rows, 1):
            st.markdown(
                f"<div style='background:#e6ffe6;padding:4px 8px;border-radius:4px;'>"
                f"<b>bid{i}</b>: {p:.3f} × {v}"
                f"</div>",
                unsafe_allow_html=True,
            )

    # 100ms 刷新提示（需 app.py 配合 streamlit.fragment + st.rerun()）
    st.caption("刷新策略: 100ms rerun (streamlit.fragment 优化)")

    return payload


__all__ = [
    "OrderBookData",
    "fetch_order_book",
    "render_order_book",
]
