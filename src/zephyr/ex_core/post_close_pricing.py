# [BLUEPRINT] MOD-L06-002 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.post_close_pricing
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.order; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] OpenOrderResolver/TradingSession 尾盘清退可选通道(40号§2.12, Phase 1.5 装配批次接线)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 时间窗 15:05-15:30 硬校验(窗外拒绝); 买入限价≥收盘价/卖出限价≤收盘价(交易所规则); 15:05后不可撤单(cancellable=False); 未成交 15:30 自动作废; 北交所不适用(4/8/920 前缀拒绝); 函数级 MVP 不接真实申报通道
# [MODIFY-GUARD] 40_execution_broker.md §2.12/§6.1 gap 16
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PostClosePricingError(ZA-EX-0016)
# [TESTS] tests/ex_core/test_post_close_pricing.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: order(未成交委托单) + close_price(当日收盘价) + at_time(当前时刻)
# F1: is_in_post_close_window(t)——15:05≤t≤15:30 窗口判定
# F2: is_post_close_eligible(symbol)——北交所(4/8/920 前缀)不适用拒绝
# F3: validate_post_close_price(side, limit, close)——买入≥收盘/卖出≤收盘
# F4: convert_to_post_close_order(order, close_price, at_time)——生成盘后固定价格申报规格(不可撤单+15:30 自动作废)
# O1: PostCloseOrderSpec -> 调用方(申报通道装配层)
# [/ALGO_FLOW]
"""



D_EX_CORE — 盘后固定价格交易通道（40 号 §6.1 gap 16，函数级 MVP）。

40 号 §2.12：尾盘清退时可选择将未成交订单转入盘后固定价格交易
（2026-07-06 新规扩容至全部 A 股/ETF，15:05-15:30 以收盘价按时间优先
逐笔撮合，15:05 后不可撤单，未成交 15:30 自动作废；买入限价≥收盘价、
卖出限价≤收盘价；沪深 A 股+ETF 适用，北交所暂未开通）。

工程裁定：函数级 MVP——申报规格生成 + 规则校验，不接真实申报通道
（miniQMT 盘后定价申报接口归 Phase 1.5 装配批次）。MVP 参与口径维持
40 号决策"暂不参与"——本模块仅供有以收盘价建仓/减仓需求时（指数调仓/
ETF 套利）显式调用。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: at_time 参数
#   fields: 参数 at_time，类型注解 time
#   code: post_close_pricing.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: symbol 参数
#   fields: 参数 symbol，类型注解 str
#   code: post_close_pricing.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: side 参数
#   fields: 参数 side，类型注解 OrderSide
#   code: post_close_pricing.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: limit_price 参数
#   fields: 参数 limit_price，类型注解 Decimal
#   code: post_close_pricing.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① is_in_post_close_window
#   name_en: is_in_post_close_window
#   intro: 盘后固定价格窗口判定（15:05 ≤ t ≤ 15:30，含端点）。
#   desc: 盘后固定价格窗口判定（15:05 ≤ t ≤ 15:30，含端点）。；源码 L149-L151
#   inputs: at_time
#   outputs: bool
# - id: A2
#   name_zh: ② is_post_close_eligible
#   name_en: is_post_close_eligible
#   intro: 标的是否适用盘后固定价格交易（沪深 A 股+ETF；北交所暂未开通）。
#   desc: 标的是否适用盘后固定价格交易（沪深 A 股+ETF；北交所暂未开通）。 北交所代码前缀：4xxxxx / 8xxxxx / 920xxx。；源码 L154-L161
#   inputs: symbol
#   outputs: bool
# - id: A3
#   name_zh: ③ validate_post_close_price
#   name_en: validate_post_close_price
#   intro: 价格规则校验：买入限价≥收盘价、卖出限价≤收盘价（违规拒绝）。
#   desc: 价格规则校验：买入限价≥收盘价、卖出限价≤收盘价（违规拒绝）。；源码 L164-L185
#   inputs: side limit_price close_price
#   outputs: 返回值
# - id: A4
#   name_zh: ④ convert_to_post_close_order
#   name_en: convert_to_post_close_order
#   intro: 未成交订单 → 盘后固定价格申报规格（40 号 §2.12 可选通道）。
#   desc: 未成交订单 → 盘后固定价格申报规格（40 号 §2.12 可选通道）。 Args: order: 尾盘清退的未成交委托单。 close_price: 当日收盘价（盘后定价撮合基…；源码 L188-L238
#   inputs: order close_price at_time
#   outputs: PostCloseOrderSpec
#   （注：A4 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: OpenOrderResolver/TradingSession 尾盘清退可选通道(40号§2.12, Phase 1.5 装配批次接线)
# - id: O2
#   name_zh: PostCloseOrderSpec
#   name_en: PostCloseOrderSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: OpenOrderResolver/TradingSession 尾盘清退可选通道(40号§2.12, Phase 1.5 装配批次接线)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from decimal import Decimal
from typing import Final

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError

#: 盘后固定价格交易窗口（沪深交易所 2026 修订规则 §3.7/§3.6）
POST_CLOSE_WINDOW_START: Final[time] = time(15, 5)
POST_CLOSE_WINDOW_END: Final[time] = time(15, 30)


class PostClosePricingError(ZephyrBaseError):
    """盘后固定价格交易规则违例——窗外/价格越界/不适用标的等。"""

    error_code = "ZA-EX-0016"


@dataclass(frozen=True)
class PostCloseOrderSpec:
    """盘后固定价格申报规格（不可变）。"""

    order_id: str
    symbol: str
    side: str  # BUY / SELL
    quantity: Decimal
    limit_price: Decimal
    close_price: Decimal
    channel: str  # 恒 "post_close_fixed_price"
    cancellable: bool  # 恒 False（15:05 后不可撤单）
    auto_expire_at: time  # 恒 15:30（未成交自动作废）
    schema_version: str = "1.0"


def is_in_post_close_window(at_time: time) -> bool:
    """盘后固定价格窗口判定（15:05 ≤ t ≤ 15:30，含端点）。"""
    return POST_CLOSE_WINDOW_START <= at_time <= POST_CLOSE_WINDOW_END


def is_post_close_eligible(symbol: str) -> bool:
    """标的是否适用盘后固定价格交易（沪深 A 股+ETF；北交所暂未开通）。

    北交所代码前缀：4xxxxx / 8xxxxx / 920xxx。
    """
    if not symbol:
        return False
    return not (symbol.startswith("4") or symbol.startswith("8") or symbol.startswith("920"))


def validate_post_close_price(side: OrderSide, limit_price: Decimal, close_price: Decimal) -> None:
    """价格规则校验：买入限价≥收盘价、卖出限价≤收盘价（违规拒绝）。"""
    if close_price <= 0:
        raise PostClosePricingError(
            "收盘价必须为正",
            details={"close_price": str(close_price)},
        )
    if limit_price <= 0:
        raise PostClosePricingError(
            "限价必须为正",
            details={"limit_price": str(limit_price)},
        )
    if side is OrderSide.BUY and limit_price < close_price:
        raise PostClosePricingError(
            "盘后定价买入限价必须 ≥ 收盘价",
            details={"limit_price": str(limit_price), "close_price": str(close_price)},
        )
    if side is OrderSide.SELL and limit_price > close_price:
        raise PostClosePricingError(
            "盘后定价卖出限价必须 ≤ 收盘价",
            details={"limit_price": str(limit_price), "close_price": str(close_price)},
        )


def convert_to_post_close_order(
    order: Order,
    close_price: Decimal,
    at_time: time,
) -> PostCloseOrderSpec:
    """未成交订单 → 盘后固定价格申报规格（40 号 §2.12 可选通道）。

    Args:
        order: 尾盘清退的未成交委托单。
        close_price: 当日收盘价（盘后定价撮合基准）。
        at_time: 当前时刻（必须在 15:05-15:30 窗口内）。

    Returns:
        PostCloseOrderSpec：cancellable=False + auto_expire_at=15:30；
        限价默认取收盘价（order.limit_price 显式给出时须过价格规则）。

    Raises:
        PostClosePricingError: 窗外 / 北交所标的 / 价格规则违例 / 数量非正。
    """
    if order is None or not getattr(order, "order_id", None):
        raise PostClosePricingError("order 缺失或 order_id 为空", details={})
    if not is_in_post_close_window(at_time):
        raise PostClosePricingError(
            "盘后固定价格窗口外（须 15:05-15:30）",
            details={"at_time": at_time.isoformat()},
        )
    if not is_post_close_eligible(order.symbol):
        raise PostClosePricingError(
            "北交所标的不适用盘后固定价格交易",
            details={"symbol": order.symbol},
        )
    if order.quantity <= 0:
        raise PostClosePricingError(
            "委托数量必须为正",
            details={"quantity": str(order.quantity)},
        )
    side = order.side if isinstance(order.side, OrderSide) else OrderSide(str(order.side))
    limit_price = order.limit_price if order.limit_price is not None else close_price
    validate_post_close_price(side, limit_price, close_price)

    return PostCloseOrderSpec(
        order_id=order.order_id,
        symbol=order.symbol,
        side=side.value,
        quantity=order.quantity,
        limit_price=limit_price,
        close_price=close_price,
        channel="post_close_fixed_price",
        cancellable=False,
        auto_expire_at=POST_CLOSE_WINDOW_END,
    )


__all__ = [
    "POST_CLOSE_WINDOW_END",
    "POST_CLOSE_WINDOW_START",
    "PostCloseOrderSpec",
    "PostClosePricingError",
    "convert_to_post_close_order",
    "is_in_post_close_window",
    "is_post_close_eligible",
    "validate_post_close_price",
]
