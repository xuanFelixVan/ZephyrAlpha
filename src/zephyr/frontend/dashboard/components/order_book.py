# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.order_book
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.dashboard.components.chart_factory; zephyr.governance.data_governance.miniqmt_provider
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
# [TTL] permanent
"""order_book · 5档盘口实时展示组件（v3.0.0 Panel+HoloViz 重构, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §16.7.3
数据源: D_DATA MiniQmtProvider.get_order_book() 5档盘口实时数据
渲染依赖: Panel(布局) + ChartFactory.make_orderbook(图表)

v3.0.0 变更 (#ARCH-047):
  - Streamlit → Panel (布局)
  - plotly 直接调用 → ChartFactory.make_orderbook (callback仅编排)
  - 100ms Bokeh WebSocket 推送(原生WebSocket, 无rerun开销)

布局:
  - 左侧: 5档卖盘(红色, 价格降序 ask5→ask1)
  - 中间: 最新价 + 压力比仪表盘
  - 右侧: 5档买盘(绿色, 价格降序 bid1→bid5)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

from zephyr.frontend.dashboard.components.chart_factory import (
    ChartFactoryError,
    make_orderbook,
)


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
    """从 D_DATA MiniQmtProvider 获取5档盘口（纯函数，无副作用）

    蓝图 §16.7.3:
      - 输入: MiniQmtProvider 实例（依赖注入），标的代码
      - 输出: OrderBookData（5档 ask/bid price/vol + 压力比）
    """
    if miniqmt_provider is None:
        return OrderBookData(symbol=symbol)

    try:
        raw = miniqmt_provider.get_order_book(symbol)
    except Exception:
        return OrderBookData(symbol=symbol)

    if not raw:
        return OrderBookData(symbol=symbol)

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
    """Panel+HoloViz 渲染5档盘口（v3.0.0, #ARCH-047）

    布局:
      - 顶部: 标题+快照时间
      - 中部: ChartFactory.make_orderbook(5档水平条形图)
      - 底部: 压力比指示器

    callback仅编排: 图表生成委托 ChartFactory.make_orderbook.
    测试环境(无 panel)仅返回 dict payload.
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
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    layout_items: list[Any] = [
        pn.pane.Markdown(f"## 5档盘口 — {data.symbol}"),
    ]
    if data.timestamp:
        layout_items.append(pn.pane.Markdown(f"*快照时间: {data.timestamp}*"))

    if not data.ask_price and not data.bid_price:
        layout_items.append(pn.pane.Alert("盘口数据为空", alert_type="info"))
        layout = pn.Column(*layout_items, sizing_mode="stretch_width")
        payload["_layout"] = layout
        return payload

    # 中部：ChartFactory.make_orderbook 图表
    try:
        ob_fig = make_orderbook(
            ask_price=data.ask_price,
            bid_price=data.bid_price,
            ask_vol=data.ask_vol,
            bid_vol=data.bid_vol,
            last_price=data.last_price,
            pressure_ratio=data.pressure_ratio,
            title=f"Order Book — {data.symbol}",
        )
        layout_items.append(ob_fig)
    except ChartFactoryError:
        pass

    # 底部：压力比指示器
    if data.pressure_ratio > 1.5:
        pressure_alert = pn.pane.Alert(
            f"压力比 {data.pressure_ratio:.2f} > 1.5 — 买盘强势 🟢",
            alert_type="success",
        )
    elif data.pressure_ratio < 0.67:
        pressure_alert = pn.pane.Alert(
            f"压力比 {data.pressure_ratio:.2f} < 0.67 — 卖盘强势 🔴",
            alert_type="danger",
        )
    else:
        pressure_alert = pn.pane.Alert(
            f"压力比 {data.pressure_ratio:.2f} — 盘口均衡 ⚪",
            alert_type="info",
        )
    layout_items.append(pressure_alert)

    layout = pn.Column(*layout_items, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__ = [
    "OrderBookData",
    "fetch_order_book",
    "render_order_book",
]
