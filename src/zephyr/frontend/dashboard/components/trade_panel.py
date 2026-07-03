# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.trade_panel
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.ex_core.adapters.miniqmt_broker; zephyr.trading.trading_contracts.execution.order
# [CONSUMERS] zephyr.frontend.dashboard.app
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] human_gated(实盘交易需Owner审批); 二次确认; 风控提示; 紧急停止; 1万元100股灰度
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] TradePanelError
# [TESTS]
# [A_module] module_id=MOD-L08-001-trade_panel | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] task_bound
"""trade_panel · 实盘交易面板组件（v2.2.0新增，human_gated）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §16.7.5
数据源: D_EX_CORE ExecutionEngine.execute_order() / MiniQmtBroker.submit_order()
渲染依赖: streamlit

布局:
  - 顶部: 紧急停止按钮(立即停止所有新订单+撤单所有未完成)
  - 上部: 下单表单(代码/方向/数量/价格/算法TWAP/VWAP/MARKET)
  - 中部: 风控提示+二次确认按钮(预估金额/持仓影响/T+1提示)
  - 底部: 订单列表(实时状态更新, 支持撤单按钮)

安全约束（蓝图 §16.7.5 D）:
  - human_gated: 实盘交易面板接入需 Owner 审批
  - 二次确认: 下单前 MUST 弹窗确认（避免误操作）
  - 风控提示: 下单前 MUST 显示预估金额/持仓影响/T+1提示
  - 小资金灰度: 首次部署 MUST 用 1万元做 100股测试
  - 紧急停止: 顶部 MUST 有"紧急停止"按钮，点击后立即停止所有新订单+撤单所有未完成订单

A股约束:
  - t_plus=1 (T+1锁定)
  - min_order_qty=100 (100股整数倍)
  - price_tick=0.01
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, Protocol

try:
    import streamlit as st
except ImportError:
    st = None


class TradePanelError(Exception):
    """交易面板错误"""


# 默认灰度约束（蓝图 §16.7.5 D: 小资金灰度）
DEFAULT_GREY_CAPITAL = 10000.0   # 1万元
DEFAULT_GREY_MAX_QTY = 100       # 100股
DEFAULT_MIN_ORDER_QTY = 100      # A股最小1手
DEFAULT_QTY_STEP = 100           # 100股整数倍


@dataclass
class OrderSubmission:
    """下单表单数据

    蓝图 §16.7.5 B: quantity >= 100 (A股1手起)
    """
    symbol: str = ""
    side: str = "buy"             # "buy" / "sell"
    quantity: int = 100
    price: float = 0.0
    order_type: str = "limit"     # "market" / "limit" / "twap" / "vwap"
    broker_id: str = "miniqmt"
    strategy_id: str = "manual"
    idempotency_key: str = ""

    @property
    def estimated_amount(self) -> float:
        return self.quantity * self.price


@dataclass
class OrderItem:
    """订单列表项（实时状态更新）"""
    order_id: str = ""
    broker_order_id: str = ""
    symbol: str = ""
    side: str = ""
    quantity: int = 0
    price: float = 0.0
    order_type: str = ""
    status: str = "PENDING"  # PENDING/SUBMITTED/ACCEPTED/PARTIALLY_FILLED/FILLED/CANCELLED/REJECTED/EXPIRED
    filled_quantity: int = 0
    avg_fill_price: float = 0.0
    timestamp: str = ""
    error_message: str = ""
    idempotency_key: str = ""


@dataclass
class TradePanelData:
    """实盘交易面板数据模型"""
    orders: list[OrderItem] = field(default_factory=list)
    available_cash: float = 0.0
    total_asset: float = 0.0
    emergency_stopped: bool = False


# ----- 风控校验（纯函数，便于测试） -----

def validate_order_submission(
    sub: OrderSubmission,
    available_cash: float = 0.0,
    grey_capital: float = DEFAULT_GREY_CAPITAL,
    grey_max_qty: int = DEFAULT_GREY_MAX_QTY,
    min_order_qty: int = DEFAULT_MIN_ORDER_QTY,
    qty_step: int = DEFAULT_QTY_STEP,
    enable_grey: bool = True,
) -> tuple[bool, str]:
    """风控校验：返回 (是否通过, 提示消息)

    蓝图 §16.7.5 D:
      - 风控提示: 预估金额 / 持仓影响 / T+1提示
      - 小资金灰度: 1万元 / 100股
    """
    if not sub.symbol:
        return False, "标的代码不能为空"
    if sub.side not in ("buy", "sell"):
        return False, f"方向非法: {sub.side}（仅支持 buy/sell）"
    if sub.quantity < min_order_qty:
        return False, f"数量 < {min_order_qty}（A股最小1手）"
    if sub.quantity % qty_step != 0:
        return False, f"数量必须是 {qty_step} 的整数倍"
    if sub.order_type not in ("market", "limit", "twap", "vwap"):
        return False, f"算法非法: {sub.order_type}"
    if sub.order_type == "limit" and sub.price <= 0:
        return False, "限价单价格必须 > 0"

    # 灰度约束
    if enable_grey:
        if sub.quantity > grey_max_qty:
            return False, f"灰度模式: 单笔数量 > {grey_max_qty}（{grey_max_qty}股灰度上限）"
        if sub.side == "buy":
            est_amount = sub.estimated_amount if sub.order_type == "limit" else sub.quantity * sub.price
            if est_amount > grey_capital:
                return False, f"灰度模式: 预估金额 {est_amount:.2f} > {grey_capital:.2f}（1万元灰度上限）"

    # 资金校验（仅买入）
    if sub.side == "buy" and available_cash > 0:
        est_amount = sub.estimated_amount
        if est_amount > available_cash:
            return False, f"预估金额 {est_amount:.2f} > 可用资金 {available_cash:.2f}"

    return True, "校验通过"


def build_risk_warning(
    sub: OrderSubmission,
    available_cash: float = 0.0,
    is_t_plus_1_relevant: bool = True,
) -> str:
    """构造风控提示文本（蓝图 §16.7.5: 下单前 MUST 显示）"""
    amount = sub.estimated_amount
    cash_after = available_cash - amount if sub.side == "buy" else available_cash + amount
    lines = [
        f"⚠ 风控提示 — 请仔细确认",
        f"  标的: {sub.symbol}",
        f"  方向: {sub.side.upper()}",
        f"  数量: {sub.quantity} 股",
        f"  价格: {sub.price:.3f}" + (f" (限价)" if sub.order_type == "limit" else " (市价参考)"),
        f"  算法: {sub.order_type.upper()}",
        f"  预估金额: {amount:,.2f}",
        f"  资金影响: 可用资金 {available_cash:,.2f} → {cash_after:,.2f}",
    ]
    if is_t_plus_1_relevant and sub.side == "buy":
        lines.append("  T+1 提示: 买入当日不可卖出，次日方可卖出")
    if sub.quantity == DEFAULT_GREY_MAX_QTY and amount <= DEFAULT_GREY_CAPITAL:
        lines.append("  灰度模式: 1万元/100股小资金测试")
    return "\n".join(lines)


# ----- Broker 抽象（依赖注入，支持 MiniQmtBroker 或 mock） -----

class _BrokerLike(Protocol):
    def submit_order(self, order: Any) -> str: ...
    def cancel_order(self, broker_order_id: str) -> bool: ...
    def query_order(self, broker_order_id: str) -> Optional[Any]: ...


# ----- 下单/撤单 -----

def submit_order(
    execution_engine: Any,
    order_submission: OrderSubmission,
    available_cash: float = 0.0,
    grey_capital: float = DEFAULT_GREY_CAPITAL,
    grey_max_qty: int = DEFAULT_GREY_MAX_QTY,
    enable_grey: bool = True,
    confirmed: bool = False,
) -> tuple[bool, str, str]:
    """提交订单到 D_EX_CORE ExecutionEngine / MiniQmtBroker

    蓝图 §16.7.5 C:
      前置校验:
        (1) 显示风控提示(预估金额/持仓影响)
        (2) 二次确认弹窗(streamlit.dialog)
        (3) 调用 ExecutionEngine.execute_order(order, broker_id="miniqmt")

    Returns:
        (success, broker_order_id_or_error, risk_warning_text)
    """
    ok, msg = validate_order_submission(
        order_submission,
        available_cash=available_cash,
        grey_capital=grey_capital,
        grey_max_qty=grey_max_qty,
        enable_grey=enable_grey,
    )
    risk_text = build_risk_warning(order_submission, available_cash=available_cash)

    if not ok:
        return False, msg, risk_text

    if not confirmed:
        return False, "需二次确认", risk_text

    if execution_engine is None:
        return False, "execution_engine 未注入", risk_text

    # 构造 Order 对象（惰性导入，避免循环依赖）
    try:
        from zephyr.trading.trading_contracts.execution.order import (
            Order, OrderSide, OrderType,
        )
    except Exception as e:
        return False, f"导入 Order 失败: {e}", risk_text

    side_enum = OrderSide.BUY if order_submission.side == "buy" else OrderSide.SELL
    type_map = {
        "market": OrderType.MARKET,
        "limit": OrderType.LIMIT,
        "twap": OrderType.LIMIT,      # TWAP/VWAP 算法单基础为限价
        "vwap": OrderType.LIMIT,
    }
    order_type_enum = type_map.get(order_submission.order_type, OrderType.LIMIT)

    idem = order_submission.idempotency_key or f"tp-{order_submission.symbol}-{int(datetime.now().timestamp()*1000)}"

    order = Order(
        idempotency_key=idem,
        order_id=idem,
        order_type=order_type_enum,
        quantity=Decimal(str(order_submission.quantity)),
        side=side_enum,
        strategy_id=order_submission.strategy_id,
        symbol=order_submission.symbol,
        limit_price=Decimal(str(order_submission.price)) if order_submission.price > 0 else None,
        created_at=datetime.now(),
    )

    try:
        # 优先调用 ExecutionEngine.execute_order(order, broker_id=...)
        if hasattr(execution_engine, "execute_order"):
            broker_order_id = execution_engine.execute_order(
                order, broker_id=order_submission.broker_id,
            )
        else:
            # 退化：直接调用 broker.submit_order
            broker_order_id = execution_engine.submit_order(order)
        return True, str(broker_order_id), risk_text
    except Exception as e:
        return False, f"下单异常: {e}", risk_text


def cancel_order(execution_engine: Any, broker_order_id: str) -> tuple[bool, str]:
    """撤单"""
    if execution_engine is None:
        return False, "execution_engine 未注入"
    if not broker_order_id:
        return False, "broker_order_id 为空"
    try:
        if hasattr(execution_engine, "cancel_order"):
            ok = execution_engine.cancel_order(broker_order_id)
        else:
            ok = execution_engine.cancel_order(broker_order_id)
        return bool(ok), "撤单成功" if ok else "撤单失败"
    except Exception as e:
        return False, f"撤单异常: {e}"


def emergency_stop(
    execution_engine: Any,
    orders: list[OrderItem],
) -> tuple[int, list[str]]:
    """紧急停止：立即撤单所有非终态订单

    蓝图 §16.7.5 D: 点击后立即停止所有新订单 + 撤单所有未完成订单
    非终态: PENDING / SUBMITTED / ACCEPTED / PARTIALLY_FILLED
    终态: FILLED / CANCELLED / REJECTED / EXPIRED
    """
    non_terminal = {"PENDING", "SUBMITTED", "ACCEPTED", "PARTIALLY_FILLED"}
    cancelled_count = 0
    errors: list[str] = []
    for o in orders:
        if o.status in non_terminal and o.broker_order_id:
            ok, msg = cancel_order(execution_engine, o.broker_order_id)
            if ok:
                cancelled_count += 1
            else:
                errors.append(f"{o.broker_order_id}: {msg}")
    return cancelled_count, errors


# ----- Streamlit 渲染 -----

def render_trade_panel(
    data: TradePanelData,
    execution_engine: Any = None,
    on_submit: Any = None,
    on_cancel: Any = None,
    on_emergency_stop: Any = None,
    enable_grey: bool = True,
) -> dict[str, Any]:
    """Streamlit 渲染实盘交易面板

    布局:
      - 顶部: 紧急停止按钮
      - 上部: 下单表单
      - 中部: 风控提示+二次确认
      - 底部: 订单列表

    测试环境(无 streamlit)仅返回 dict.
    """
    payload: dict[str, Any] = {
        "orders_count": len(data.orders),
        "available_cash": round(data.available_cash, 2),
        "total_asset": round(data.total_asset, 2),
        "emergency_stopped": data.emergency_stopped,
        "orders": [
            {
                "order_id": o.order_id,
                "broker_order_id": o.broker_order_id,
                "symbol": o.symbol,
                "side": o.side,
                "quantity": o.quantity,
                "price": round(o.price, 3),
                "order_type": o.order_type,
                "status": o.status,
                "filled_quantity": o.filled_quantity,
                "avg_fill_price": round(o.avg_fill_price, 3),
                "timestamp": o.timestamp,
                "error_message": o.error_message,
            }
            for o in data.orders
        ],
    }

    if st is None:
        return payload

    st.subheader("实盘交易面板 🔴 human_gated")
    st.caption("⚠ 实盘交易面板接入需 Owner 审批。首次部署 MUST 用 1万元 / 100股 灰度测试")

    # 顶部：紧急停止按钮
    st.markdown("### 🚨 紧急停止")
    if data.emergency_stopped:
        st.error("⚠ 已紧急停止：禁止所有新订单，未完成订单已撤单")
    if st.button("🚨 紧急停止所有订单", type="primary", help="立即撤单所有非终态订单"):
        if on_emergency_stop is not None:
            cancelled, errs = on_emergency_stop()
            st.warning(f"紧急停止：撤单 {cancelled} 笔；失败 {len(errs)} 笔")
        else:
            st.info("未注入 on_emergency_stop 回调")
        st.rerun()

    st.divider()

    # 上部：下单表单
    st.markdown("### 下单表单")
    with st.form("trade_panel_form", clear_on_submit=False):
        c1, c2, c3, c4 = st.columns(4)
        symbol = c1.text_input("标的代码", value="600000.SH")
        side = c2.selectbox("方向", ["buy", "sell"])
        qty_max = DEFAULT_GREY_MAX_QTY if enable_grey else 10000
        quantity = c3.number_input(
            "数量（股）", min_value=DEFAULT_MIN_ORDER_QTY, max_value=qty_max,
            value=DEFAULT_GREY_MAX_QTY, step=DEFAULT_QTY_STEP,
        )
        price = c4.number_input("价格", min_value=0.01, value=10.00, step=0.01, format="%.2f")

        c5, c6, c7 = st.columns(3)
        order_type = c5.selectbox("算法", ["limit", "market", "twap", "vwap"], index=0)
        broker_id = c6.text_input("Broker ID", value="miniqmt")
        strategy_id = c7.text_input("Strategy ID", value="manual")

        # 中部：风控提示
        sub = OrderSubmission(
            symbol=symbol, side=side, quantity=int(quantity),
            price=float(price), order_type=order_type,
            broker_id=broker_id, strategy_id=strategy_id,
        )
        risk_text = build_risk_warning(sub, available_cash=data.available_cash)
        st.info(risk_text)

        # 二次确认 checkbox
        confirmed = st.checkbox("我已确认上述订单信息，授权提交（二次确认）")
        submitted = st.form_submit_button("提交订单", disabled=not confirmed)

        if submitted and confirmed:
            if on_submit is not None:
                ok, msg, _ = on_submit(sub, confirmed=True)
                if ok:
                    st.success(f"下单成功: {msg}")
                else:
                    st.error(f"下单失败: {msg}")
            else:
                st.info("未注入 on_submit 回调")
            st.rerun()

    st.divider()

    # 底部：订单列表
    st.markdown("### 订单列表")
    if not data.orders:
        st.info("暂无订单")
    else:
        non_terminal = {"PENDING", "SUBMITTED", "ACCEPTED", "PARTIALLY_FILLED"}
        for o in data.orders:
            status_color = {
                "FILLED": "🟢",
                "CANCELLED": "⚪",
                "REJECTED": "🔴",
                "EXPIRED": "⚫",
            }.get(o.status, "🟡")
            st.markdown(
                f"**{status_color} {o.status}** | `{o.broker_order_id or o.order_id}` | "
                f"{o.symbol} {o.side.upper()} {o.quantity}@{o.price:.3f} ({o.order_type}) | "
                f"已成交 {o.filled_quantity}@{o.avg_fill_price:.3f}"
            )
            if o.error_message:
                st.error(f"  错误: {o.error_message}")
            if o.status in non_terminal and o.broker_order_id:
                if st.button(f"撤单 {o.broker_order_id}", key=f"cancel_{o.broker_order_id}"):
                    if on_cancel is not None:
                        ok, msg = on_cancel(o.broker_order_id)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                    st.rerun()

    return payload


__all__ = [
    "TradePanelError",
    "OrderSubmission",
    "OrderItem",
    "TradePanelData",
    "DEFAULT_GREY_CAPITAL",
    "DEFAULT_GREY_MAX_QTY",
    "DEFAULT_MIN_ORDER_QTY",
    "DEFAULT_QTY_STEP",
    "validate_order_submission",
    "build_risk_warning",
    "submit_order",
    "cancel_order",
    "emergency_stop",
    "render_trade_panel",
]
