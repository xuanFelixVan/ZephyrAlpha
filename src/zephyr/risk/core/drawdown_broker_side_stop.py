# [BLUEPRINT] MOD-RK-011 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md | §3.5.1/§6.11
# [MODULE] zephyr.risk.core.drawdown_broker_side_stop
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 开仓执行链(开仓时同步挂 broker 端 stop) ; RiskOrchestrator(§6.5 接线位) ; drawdown_watchdog(L3 对账数据源)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 每只在持仓位必须有匹配 broker 端保护性止损单(bracket/OCO,不依赖策略连接); 止损价必须为正且低于参考价(保护性卖出方向); 缺 stop_price 即抛错(fail-closed,不可臆造安全价); 对账发现未保护/错配仓位→coverage_ok=False+CRITICAL 日志(fail-closed,不静默兜底); 本模块只产出意图与对账裁决,不直连 broker(miniQMT bracket 支持待实盘验证,§6.11 重评条件)
# [MODIFY-GUARD] tests/risk/test_drawdown_broker_side_stop.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidBrokerSideStopInputError(ZA-RK-0073)
# [TESTS] tests/risk/test_drawdown_broker_side_stop.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: positions {symbol: {qty, stop_price, reference_price?}}(开仓时在持仓位+保护性止损价)
# I2: broker_stop_orders [{symbol, qty, stop_price}](broker 端已确认保护性止损单)
# I3: BrokerSideStopConfig(price_tolerance_ratio 对账容差)
# F1: build_protective_stop_plan(逐仓位产出 ProtectiveStopIntent(symbol/qty/stop_price/SELL); qty≤0/stop_price≤0/stop≥reference 抛错)
# F2: reconcile_broker_side_stops(计划 vs broker 实际: 按 symbol 匹配, qty 覆盖+stop_price 容差内=受保护; 未保护/错配→coverage_ok=False)
# O1: list[ProtectiveStopIntent](开仓时同步挂单侧) + BrokerSideStopReport(coverage_ok/unprotected/mismatched/intents)
# [/ALGO_FLOW]
"""D_RISK — L2 平台层 broker 端硬止损（35 号 memo §6.11 施工，§3.5.1 四层架构 L2 落地）。

痛点（§3.5.1 四层防御表 L2 行）：
  L1 代码层 Kill Switch 平仓链路依赖策略进程存活；策略崩溃/连接中断时，
  持仓失去止损保护（Ghost Position 风险窗口）。L2 平台层把保护性止损单
  （bracket/OCO）挂在 broker 端，不依赖策略连接——开仓时同步挂 stop，
  策略失联时 broker 端止损仍独立生效。

本模块落地（broker 无关纯逻辑，miniQMT bracket 支持验证由执行域承接）：
  - build_protective_stop_plan：开仓时对在持仓位产出 broker 端保护性
    止损意图（symbol/qty/stop_price/SELL）。fail-closed：缺 stop_price
    即抛错——安全价不可由本层臆造，必须由策略/风控侧显式给出。
  - reconcile_broker_side_stops：计划 vs broker 端已确认止损单对账——
    按 symbol 匹配，qty 覆盖持仓且 stop_price 在容差内视为受保护；
    任何未保护/错配仓位 → coverage_ok=False + CRITICAL 日志（fail-closed，
    对齐 §3.5.1 "每层捕获上层遗漏"）。
  - 边界：本模块只产出意图与对账裁决，不直连 broker、不撤单不下单；
    下单通道属执行域（40_execution_broker），消费方 RiskOrchestrator §6.5。

SSoT: 35_drawdown_protocol_impl §3.5.1/§6.11
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Final, Mapping, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "BrokerSideStopConfig",
    "BrokerSideStopReport",
    "InvalidBrokerSideStopInputError",
    "ProtectiveStopIntent",
    "build_protective_stop_plan",
    "reconcile_broker_side_stops",
]

_logger = logging.getLogger(__name__)

#: 保护性止损方向（A 股只多仓，保护性止损恒为卖出）
PROTECTIVE_STOP_SIDE: Final = "SELL"


class InvalidBrokerSideStopInputError(ZephyrBaseError):
    """L2 broker 端止损输入非法（qty/stop_price 非正、止损价不低于参考价、对账阈值越界等）。"""

    error_code = "ZA-RK-0073"


@dataclass(frozen=True)
class BrokerSideStopConfig:
    """L2 对账配置（C 类可调参数）。

    Attributes:
        price_tolerance_ratio: 对账 stop_price 容差比例（默认 0.1%，
            吸收 tick 取整差异；0=精确匹配）
    """

    price_tolerance_ratio: float = 0.001

    def __post_init__(self) -> None:
        if not 0 <= self.price_tolerance_ratio < 1:
            raise InvalidBrokerSideStopInputError(
                f"price_tolerance_ratio 须在 [0,1), got {self.price_tolerance_ratio}"
            )


@dataclass(frozen=True)
class ProtectiveStopIntent:
    """broker 端保护性止损意图（开仓时同步挂单，§3.5.1 L2）。

    Attributes:
        symbol: 标的代码
        qty: 保护数量（= 持仓数量，全量保护）
        stop_price: 止损触发价（必须 < 参考价）
        side: 方向（恒 SELL，A 股只多仓）
    """

    symbol: str
    qty: int
    stop_price: float
    side: str = PROTECTIVE_STOP_SIDE


@dataclass(frozen=True)
class BrokerSideStopReport:
    """L2 对账裁决（计划 vs broker 端已确认止损单）。

    Attributes:
        coverage_ok: 全部在持仓位均受 broker 端止损保护（fail-closed 判据）
        unprotected: 无任何匹配止损单的标的（tuple，保持输入顺序）
        mismatched: 有止损单但 qty 不足/价格越容差的 (symbol, 原因) 对
        intents: 本次对账依据的保护性止损意图（计划侧真源）
    """

    coverage_ok: bool
    unprotected: tuple[str, ...] = field(default_factory=tuple)
    mismatched: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    intents: tuple[ProtectiveStopIntent, ...] = field(default_factory=tuple)


def build_protective_stop_plan(
    positions: Mapping[str, Mapping[str, Any]],
) -> list[ProtectiveStopIntent]:
    """开仓时同步挂 broker 端止损——逐在持仓位产出保护性止损意图（§3.5.1 L2 触发点）。

    Args:
        positions: {symbol: {"qty": int, "stop_price": float, "reference_price": float?}}
            qty>0 才视为在持仓位；stop_price 必填（安全价不可臆造，fail-closed）；
            reference_price 可选（提供时校验 stop_price < reference_price）。

    Returns:
        ProtectiveStopIntent 列表（输入顺序）。

    Raises:
        InvalidBrokerSideStopInputError: qty 非正 / stop_price 缺失或非正 /
            stop_price 不低于参考价（保护性卖出方向被倒挂）。
    """
    intents: list[ProtectiveStopIntent] = []
    for symbol, pos in positions.items():
        if not isinstance(pos, Mapping):
            raise InvalidBrokerSideStopInputError(f"{symbol} 持仓信息须为 Mapping, got {type(pos).__name__}")
        qty = pos.get("qty", 0)
        if qty == 0:
            continue
        if qty < 0:
            raise InvalidBrokerSideStopInputError(f"{symbol} qty 须 >= 0, got {qty}")
        stop_price = pos.get("stop_price")
        if stop_price is None:
            raise InvalidBrokerSideStopInputError(
                f"{symbol} 缺 stop_price——L2 保护性止损价必须由策略/风控显式给出，本层不臆造（fail-closed）"
            )
        if stop_price <= 0:
            raise InvalidBrokerSideStopInputError(f"{symbol} stop_price 须为正, got {stop_price}")
        reference_price = pos.get("reference_price")
        if reference_price is not None:
            if reference_price <= 0:
                raise InvalidBrokerSideStopInputError(f"{symbol} reference_price 须为正, got {reference_price}")
            if stop_price >= reference_price:
                raise InvalidBrokerSideStopInputError(
                    f"{symbol} 保护性卖出止损 stop_price({stop_price}) 须低于参考价({reference_price})——方向倒挂即失去保护语义"
                )
        intents.append(
            ProtectiveStopIntent(symbol=str(symbol), qty=int(qty), stop_price=float(stop_price))
        )
    _logger.info("BROKER_SIDE_STOP_PLAN intents=%d", len(intents))
    return intents


def _index_stop_orders(
    broker_stop_orders: Sequence[Mapping[str, Any]] | None,
) -> dict[str, Mapping[str, Any]]:
    """止损单按 symbol 建索引（同标的多张取 qty 最大者=最覆盖口径；字段非法 fail-closed）。"""
    orders: dict[str, Mapping[str, Any]] = {}
    for order in broker_stop_orders or ():
        if not isinstance(order, Mapping):
            raise InvalidBrokerSideStopInputError(f"止损单须为 Mapping, got {type(order).__name__}")
        sym = order.get("symbol")
        o_qty = order.get("qty", 0)
        o_price = order.get("stop_price", 0)
        if sym is None or o_qty <= 0 or o_price <= 0:
            raise InvalidBrokerSideStopInputError(
                f"止损单字段非法: symbol={sym!r} qty={o_qty} stop_price={o_price}"
            )
        prev = orders.get(str(sym))
        if prev is None or o_qty > prev.get("qty", 0):
            orders[str(sym)] = order
    return orders


def reconcile_broker_side_stops(
    positions: Mapping[str, Mapping[str, Any]],
    broker_stop_orders: Sequence[Mapping[str, Any]] | None,
    *,
    config: BrokerSideStopConfig | None = None,
) -> BrokerSideStopReport:
    """L2 对账：计划在持仓位 vs broker 端已确认保护性止损单（每层捕获上层遗漏）。

    匹配规则（按 symbol）：broker 存在该标的止损单 且 止损单 qty >= 持仓 qty
    且 |broker_stop_price − 计划 stop_price| <= 容差 × 计划 stop_price → 受保护；
    否则记入 mismatched。无任何止损单的标的记入 unprotected。

    Args:
        positions: 同 build_protective_stop_plan（计划侧真源）
        broker_stop_orders: broker 端已确认止损单 [{symbol, qty, stop_price}]；
            None/空 = 全部未保护（fail-closed）
        config: 对账配置（容差）

    Returns:
        BrokerSideStopReport（coverage_ok=False 时调用方须告警 + 补挂/人工介入）
    """
    cfg = config or BrokerSideStopConfig()
    intents = build_protective_stop_plan(positions)
    orders = _index_stop_orders(broker_stop_orders)

    unprotected: list[str] = []
    mismatched: list[tuple[str, str]] = []
    for intent in intents:
        order = orders.get(intent.symbol)
        if order is None:
            unprotected.append(intent.symbol)
            continue
        if order["qty"] < intent.qty:
            mismatched.append(
                (intent.symbol, f"止损单数量 {order['qty']} < 持仓 {intent.qty}（保护不足）")
            )
            continue
        tolerance = cfg.price_tolerance_ratio * intent.stop_price
        if abs(float(order["stop_price"]) - intent.stop_price) > tolerance:
            mismatched.append(
                (
                    intent.symbol,
                    f"止损价 {order['stop_price']} 偏离计划 {intent.stop_price} 超容差 {tolerance:.4f}",
                )
            )

    coverage_ok = not unprotected and not mismatched
    if not coverage_ok:
        _logger.critical(
            "BROKER_SIDE_STOP_UNCOVERED unprotected=%s mismatched=%s",
            unprotected,
            mismatched,
        )
    return BrokerSideStopReport(
        coverage_ok=coverage_ok,
        unprotected=tuple(unprotected),
        mismatched=tuple(mismatched),
        intents=tuple(intents),
    )
