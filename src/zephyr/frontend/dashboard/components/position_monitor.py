# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.position_monitor
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.ex_core.adapters.miniqmt_broker
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
# [A_module] module_id=MOD-L08-001-position_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""position_monitor · 实盘持仓监控组件（v2.2.0新增）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §16.7.4
数据源: D_EX_CORE MiniQmtBroker.get_positions() 实盘持仓快照
渲染依赖: streamlit（持仓表格）

布局:
  - 顶部: 账户资金卡片(总资产/可用资金/当日盈亏)
  - 中部: 持仓表格(symbol/名称/持仓/可用/冻结/成本/最新价/盈亏/盈亏%/T+1标记)
  - T+1锁定行: 红色背景标记，鼠标悬停提示"当日买入, 次日可卖"
刷新策略: 1s rerun
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

try:
    import streamlit as st
except ImportError:
    st = None


@dataclass
class PositionItem:
    """单标的持仓项

    蓝图 §16.7.4: 含 T+1 标记（today_bought > 0 → is_t_plus_1_locked=True）
    """
    symbol: str = ""
    name: str = ""
    quantity: int = 0                # 总持仓
    available_quantity: int = 0      # 可用数量（扣除冻结）
    frozen_quantity: int = 0         # 冻结数量
    today_bought: int = 0            # 当日买入（T+1锁定）
    cost_price: float = 0.0
    last_price: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    is_t_plus_1_locked: bool = False

    @property
    def market_value(self) -> float:
        return self.quantity * self.last_price


@dataclass
class PositionMonitorData:
    """实盘持仓监控数据模型"""
    account_id: str = ""
    total_asset: float = 0.0          # 总资产 = cash + 持仓市值
    available_cash: float = 0.0       # 可用资金
    market_value_total: float = 0.0   # 持仓总市值
    today_pnl: float = 0.0            # 当日盈亏（占位，需 D_EX_CORE 提供）
    positions: list[PositionItem] = field(default_factory=list)
    timestamp: str = ""


def _to_float(v: Any, default: float = 0.0) -> float:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _to_int(v: Any, default: int = 0) -> int:
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def fetch_position_monitor(
    miniqmt_broker: Any,
    today_bought_map: Optional[dict[str, int]] = None,
    last_prices: Optional[dict[str, float]] = None,
    cost_prices: Optional[dict[str, float]] = None,
    symbol_names: Optional[dict[str, str]] = None,
) -> PositionMonitorData:
    """从 D_EX_CORE MiniQmtBroker 获取持仓

    蓝图 §16.7.4:
      - 输入: MiniQmtBroker 实例（依赖注入）
      - 输出: PositionMonitorData（持仓+盈亏+T+1标记）
      - T+1标记: today_bought > 0 → is_t_plus_1_locked=True

    MiniQmtBroker.get_positions() 返回 PositionSnapshot:
      cash / holdings(dict[symbol, Decimal]) / market_values(dict[symbol, Decimal])
      / total_market_value / as_of_timestamp / portfolio_id

    Backtest 兼容: 也支持 Portfolio 对象（cash/holdings/total_nav）。
    """
    if miniqmt_broker is None:
        return PositionMonitorData()

    try:
        snapshot = miniqmt_broker.get_positions()
    except Exception:
        return PositionMonitorData()

    if snapshot is None:
        return PositionMonitorData()

    # 兼容 PositionSnapshot 和 Portfolio
    cash = _to_float(getattr(snapshot, "cash", 0.0))
    holdings = getattr(snapshot, "holdings", {}) or {}
    market_values = getattr(snapshot, "market_values", {}) or {}
    total_mv = _to_float(getattr(snapshot, "total_market_value", 0.0))
    if total_mv == 0.0 and hasattr(snapshot, "total_nav"):
        total_mv = _to_float(getattr(snapshot, "total_nav", 0.0))
    portfolio_id = getattr(snapshot, "portfolio_id", "") or getattr(snapshot, "idempotency_key", "")
    as_of = getattr(snapshot, "as_of_timestamp", None) or getattr(snapshot, "current_date", None)

    today_bought_map = today_bought_map or {}
    last_prices = last_prices or {}
    cost_prices = cost_prices or {}
    symbol_names = symbol_names or {}

    positions: list[PositionItem] = []
    for symbol, qty_raw in holdings.items():
        qty = _to_int(qty_raw)
        if qty <= 0:
            continue

        mv = _to_float(market_values.get(symbol, 0.0))
        last_price = _to_float(last_prices.get(symbol), mv / qty if qty > 0 else 0.0)
        cost_price = _to_float(cost_prices.get(symbol), last_price)
        today_bought = _to_int(today_bought_map.get(symbol, 0))

        # 可用 = 总持仓 - 今日买入（T+1锁定）- 冻结
        available = max(0, qty - today_bought)
        frozen = qty - available

        unrealized_pnl = (last_price - cost_price) * qty
        pnl_pct = ((last_price - cost_price) / cost_price) if cost_price > 0 else 0.0

        positions.append(PositionItem(
            symbol=symbol,
            name=symbol_names.get(symbol, symbol),
            quantity=qty,
            available_quantity=available,
            frozen_quantity=frozen,
            today_bought=today_bought,
            cost_price=cost_price,
            last_price=last_price,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=pnl_pct,
            is_t_plus_1_locked=(today_bought > 0),
        ))

    ts_str = str(as_of) if as_of else ""

    return PositionMonitorData(
        account_id=str(portfolio_id),
        total_asset=cash + total_mv,
        available_cash=cash,
        market_value_total=total_mv,
        today_pnl=sum(p.unrealized_pnl for p in positions),
        positions=positions,
        timestamp=ts_str,
    )


def render_position_monitor(data: PositionMonitorData) -> dict[str, Any]:
    """Streamlit 渲染持仓监控

    布局:
      - 顶部: 账户资金卡片(总资产/可用资金/当日盈亏)
      - 中部: 持仓表格(symbol/名称/持仓/可用/冻结/成本/最新价/盈亏/盈亏%/T+1标记)
      - T+1锁定行: 红色背景标记

    刷新: 1s rerun
    测试环境(无 streamlit)仅返回 dict.
    """
    payload: dict[str, Any] = {
        "account_id": data.account_id,
        "total_asset": round(data.total_asset, 2),
        "available_cash": round(data.available_cash, 2),
        "market_value_total": round(data.market_value_total, 2),
        "today_pnl": round(data.today_pnl, 2),
        "timestamp": data.timestamp,
        "positions_count": len(data.positions),
        "positions": [
            {
                "symbol": p.symbol,
                "name": p.name,
                "quantity": p.quantity,
                "available": p.available_quantity,
                "frozen": p.frozen_quantity,
                "today_bought": p.today_bought,
                "cost_price": round(p.cost_price, 3),
                "last_price": round(p.last_price, 3),
                "unrealized_pnl": round(p.unrealized_pnl, 2),
                "unrealized_pnl_pct": round(p.unrealized_pnl_pct, 4),
                "is_t_plus_1_locked": p.is_t_plus_1_locked,
            }
            for p in data.positions
        ],
    }

    if st is None:
        return payload

    st.subheader("实盘持仓监控")
    if data.timestamp:
        st.caption(f"快照时间: {data.timestamp}")

    # 顶部：账户资金卡片
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总资产", f"{data.total_asset:,.2f}")
    col2.metric("可用资金", f"{data.available_cash:,.2f}")
    col3.metric("持仓市值", f"{data.market_value_total:,.2f}")
    pnl_color_prefix = "+" if data.today_pnl >= 0 else ""
    col4.metric("当日盈亏", f"{pnl_color_prefix}{data.today_pnl:,.2f}")

    # 中部：持仓表格
    if not data.positions:
        st.info("当前无持仓")
        return payload

    st.markdown("### 持仓明细")
    header = "| Symbol | 名称 | 持仓 | 可用 | 冻结 | 当日买入 | 成本价 | 最新价 | 盈亏 | 盈亏% | T+1 |\n"
    header += "|--------|------|------|------|------|---------|--------|--------|------|-------|-----|\n"
    rows = ""
    for p in data.positions:
        pnl_str = f"{p.unrealized_pnl:+.2f}"
        pnl_pct_str = f"{p.unrealized_pnl_pct:+.2%}"
        t1_str = "🔴锁定" if p.is_t_plus_1_locked else "—"
        rows += f"| {p.symbol} | {p.name} | {p.quantity} | {p.available_quantity} | {p.frozen_quantity} | {p.today_bought} | {p.cost_price:.3f} | {p.last_price:.3f} | {pnl_str} | {pnl_pct_str} | {t1_str} |\n"
    st.markdown(header + rows)

    # T+1 锁定行额外提示
    locked_positions = [p for p in data.positions if p.is_t_plus_1_locked]
    if locked_positions:
        st.warning(
            f"⚠ **T+1 锁定**：以下 {len(locked_positions)} 个标的存在当日买入，次日才能卖出 — "
            + ", ".join(p.symbol for p in locked_positions)
        )

    st.caption("刷新策略: 1s rerun")

    return payload


__all__ = [
    "PositionItem",
    "PositionMonitorData",
    "fetch_position_monitor",
    "render_position_monitor",
]
