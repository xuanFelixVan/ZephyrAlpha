# [BLUEPRINT] MOD-TRADING-002 | docs/03_modules/_domain_trading/pnl_calculator/blueprint.md
# [MODULE] zephyr.trading.pnl_calculator
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.fill; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.reporting; zephyr.ex_core; zephyr.position
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Decimal-only金额计算; FeeConfig/FeeBreakdown/RealizedPnl/UnrealizedPnl/PortfolioPnl frozen不可变; 已实现盈亏仅卖出计毛盈亏(买入毛盈亏=0); 净盈亏=毛盈亏-总费用恒成立
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPnlInputError(ZA-TR-0001)
# [TESTS] tests/trading/test_pnl_calculator.py
# [A_module] module_id=MOD-TRADING-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_TRADING — PnL Calculator (盈亏计算器)

交易后盈亏核算基础设施。从成交回报(Fill)和持仓均价计算已实现盈亏,
从持仓+当前市价计算未实现盈亏, 含A股交易成本(佣金/印花税/过户费)核算。

产出 CTR-TRD-01 费率/PnL数据 → D-REPORTING(C-010 盈亏分析)。

设计真源: D:/临时工作区/依赖图/18-D-TRADING-交易运营域.md §3.2 CTR-TRD-01
蓝图: docs/03_modules/_domain_trading/pnl_calculator/blueprint.md

核心职责（阶段1）:
  - 已实现盈亏: 卖出成交 (fill_price - avg_cost) × qty - 费用
  - 未实现盈亏: (current_price - avg_cost) × qty
  - A股费率: 佣金(0.025%最低¥5) + 印花税(0.05%仅卖出) + 过户费(0.001%双向)
  - 组合盈亏: 汇总已实现+未实现

属 A 类基础设施（确定性数学计算），费率为 C 类可调参数(FeeConfig)。
纯基础设施: 不决定"买什么/何时买"，只负责"算这笔交易赚了多少/花了多少成本"。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 成交回报 Fill（CTR-005 契约）
#   fields: fill_price + filled_quantity + symbol（Decimal，不可变）
#   code: zephyr.shared.contracts.fill.Fill
# - id: I2
#   name: 持仓均价 avg_cost（Decimal）
#   fields: 卖出前持仓均价，来自 PositionTracker
#   code: calculate_realized(avg_cost) L230
# - id: I3
#   name: 持仓与市价 positions
#   fields: (symbol, quantity, avg_cost, current_price) 列表；quantity>0多头 <0空头
#   code: calculate_portfolio(positions) L368
# - id: I4
#   name: A股费率配置 FeeConfig（C类可调参数）
#   fields: 佣金0.025%最低¥5 / 印花税0.05%仅卖出 / 过户费0.001%双向
#   code: FeeConfig L60
# 层: 算法
# - id: A1
#   name_zh: ① 输入校验
#   name_en: PnlCalculator 校验段
#   intro: 检查成交价/数量为正、均价市价非负，非法抛错
#   desc: fill_price<=0 / qty<=0 / avg_cost<0 / current_price<0 → InvalidPnlInputError(ZA-TR-0001)
#   inputs: I1 I2 I3
#   outputs: 校验通过或异常
# - id: A2
#   name_zh: ② A股费用核算
#   name_en: AShareFeeCalculator.calculate
#   intro: 按成交额算佣金/印花税/过户费三件套
#   desc: commission=max(turnover×rate, min¥5)；stamp_duty=turnover×0.0005 仅SELL；transfer_fee=turnover×0.00001 双向
#   inputs: A1 I1 I4
#   outputs: FeeBreakdown（total=三项之和）
# - id: A3
#   name_zh: ③ 已实现盈亏
#   name_en: calculate_realized
#   intro: 卖出才算赚亏：价差乘数量减费用；买入只计费用不计毛盈亏
#   desc: turnover=price×qty；SELL gross=(fill_price-avg_cost)×qty，BUY gross=0；net_pnl=gross-fees.total
#   inputs: A1 A2 I1 I2
#   outputs: RealizedPnl
#   invariant: 净盈亏=毛盈亏-总费用恒成立；买入毛盈亏=0
# - id: A4
#   name_zh: ④ 未实现盈亏
#   name_en: calculate_unrealized
#   intro: 按当前市价给持仓估浮盈浮亏，多空方向相反
#   desc: 多头 gross=(current_price-avg_cost)×qty；空头 gross=(avg_cost-current_price)×|qty|；零持仓=0
#   inputs: A1 I3
#   outputs: UnrealizedPnl
# - id: A5
#   name_zh: ⑤ 组合盈亏汇总
#   name_en: calculate_portfolio
#   intro: 批量算全部成交的已实现和全部持仓的未实现，加总成组合盈亏
#   desc: total_pnl=Σnet_realized+Σgross_unrealized；total_fees=Σfees.total
#   inputs: A3 A4
#   outputs: PortfolioPnl
# 层: 输出
# - id: O1
#   name_zh: 单笔已实现盈亏 RealizedPnl
#   name_en: RealizedPnl
#   intro: 毛盈亏+费用分解+净盈亏，frozen 不可变
#   invariant: net_pnl = gross_pnl - fees.total
#   downstream: calculate_portfolio 聚合（A5）
# - id: O2
#   name_zh: 组合盈亏 PortfolioPnl（CTR-TRD-01 费率/PnL数据）
#   name_en: PortfolioPnl
#   intro: 已实现净额+未实现毛额+费用合计，供报表域做盈亏分析
#   downstream: zephyr.reporting（C-010 盈亏分析）；zephyr.ex_core；zephyr.position
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# I1 --> A2
# I4 --> A2
# A1 --> A3
# A2 --> A3
# I1 --> A3
# I2 --> A3
# A1 --> A4
# I3 --> A4
# A3 --> A5
# A4 --> A5
# A3 --> O1
# A5 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, runtime_checkable

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class InvalidPnlInputError(ZephyrBaseError):
    """PnL 计算输入非法——负均价/负数量/负市价等。"""

    error_code = "ZA-TR-0001"


# ── 数据模型（全部 frozen 不可变）──


@dataclass(frozen=True)
class FeeConfig:
    """A股交易费率配置（C 类可调参数）。

    默认值反映 2023 年印花税减半后的 A 股标准费率:
      - 佣金: 0.025%，最低 ¥5/笔（买入+卖出）
      - 印花税: 0.05%（仅卖出，2023 减半）
      - 过户费: 0.001%（买入+卖出，2022 沪深统一）
    """

    commission_rate: Decimal = Decimal("0.00025")  # 0.025%
    commission_min: Decimal = Decimal("5")  # 最低 ¥5/笔
    stamp_duty_rate: Decimal = Decimal("0.0005")  # 0.05% (卖出)
    transfer_fee_rate: Decimal = Decimal("0.00001")  # 0.001%


@dataclass(frozen=True)
class FeeBreakdown:
    """费用分解——佣金/印花税/过户费。不可变。"""

    commission: Decimal
    stamp_duty: Decimal
    transfer_fee: Decimal

    @property
    def total(self) -> Decimal:
        """总费用 = 佣金 + 印花税 + 过户费。"""
        return self.commission + self.stamp_duty + self.transfer_fee


@dataclass(frozen=True)
class RealizedPnl:
    """已实现盈亏——单笔卖出成交的盈亏核算结果。不可变。

    对 BUY 方向：gross_pnl=0（买入不计已实现盈亏，仅更新持仓成本），
    但费用仍计入（佣金+过户费，无印花税），net_pnl=-fees.total。
    """

    symbol: str
    side: OrderSide
    quantity: Decimal
    fill_price: Decimal
    avg_cost: Decimal
    turnover: Decimal
    gross_pnl: Decimal
    fees: FeeBreakdown

    @property
    def net_pnl(self) -> Decimal:
        """净盈亏 = 毛盈亏 - 总费用。"""
        return self.gross_pnl - self.fees.total


@dataclass(frozen=True)
class UnrealizedPnl:
    """未实现盈亏——持仓浮盈浮亏。不可变。

    多头(quantity>0): (current_price - avg_cost) × quantity
    空头(quantity<0): (avg_cost - current_price) × |quantity|  (反向)
    """

    symbol: str
    quantity: Decimal
    avg_cost: Decimal
    current_price: Decimal
    gross_pnl: Decimal


@dataclass(frozen=True)
class PortfolioPnl:
    """组合盈亏汇总——已实现+未实现。不可变。"""

    realized: list[RealizedPnl]
    unrealized: list[UnrealizedPnl]

    @property
    def total_realized(self) -> Decimal:
        """已实现盈亏合计（净额）。"""
        return sum((r.net_pnl for r in self.realized), Decimal("0"))

    @property
    def total_unrealized(self) -> Decimal:
        """未实现盈亏合计（毛额）。"""
        return sum((u.gross_pnl for u in self.unrealized), Decimal("0"))

    @property
    def total_pnl(self) -> Decimal:
        """组合总盈亏 = 已实现净额 + 未实现毛额。"""
        return self.total_realized + self.total_unrealized

    @property
    def total_fees(self) -> Decimal:
        """总费用合计。"""
        return sum((r.fees.total for r in self.realized), Decimal("0"))


# ── 费用计算 port + 默认实现 ──


@runtime_checkable
class FeeCalculator(Protocol):
    """费用计算器接口（port）。

    未来 MOD-TRADING-004(公司行为处理器)可注入更复杂的费率逻辑，
    如分级佣金、免5优惠、ETF费率等。
    """

    def calculate(self, turnover: Decimal, side: OrderSide) -> FeeBreakdown:
        """根据成交额和方向计算费用分解。"""
        ...


class AShareFeeCalculator:
    """A股标准费用计算器——使用 FeeConfig 计算佣金/印花税/过户费。

    规则（设计真源 §3.3）:
      - 佣金: turnover × commission_rate，最低 commission_min/笔（买入+卖出）
      - 印花税: turnover × stamp_duty_rate（仅卖出）
      - 过户费: turnover × transfer_fee_rate（买入+卖出）
    """

    def __init__(self, config: FeeConfig | None = None) -> None:
        self._config = config if config is not None else FeeConfig()

    def calculate(self, turnover: Decimal, side: OrderSide) -> FeeBreakdown:
        cfg = self._config
        # 佣金：按费率计算，不低于最低收费
        commission = max(turnover * cfg.commission_rate, cfg.commission_min)
        # 印花税：仅卖出
        stamp_duty = turnover * cfg.stamp_duty_rate if side == OrderSide.SELL else Decimal("0")
        # 过户费：双向
        transfer_fee = turnover * cfg.transfer_fee_rate
        return FeeBreakdown(
            commission=commission,
            stamp_duty=stamp_duty,
            transfer_fee=transfer_fee,
        )


# ── PnL 计算器主类 ──


class PnlCalculator:
    """盈亏计算器——已实现/未实现/组合盈亏 + A股费率核算。

    纯计算基础设施，无状态（除 fee_calculator 注入外），线程安全。

    Usage:
        calc = PnlCalculator()  # 默认 A股费率

        # 已实现盈亏（卖出）
        realized = calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("10.00"))
        print(realized.net_pnl)

        # 未实现盈亏
        unrealized = calc.calculate_unrealized("600000", Decimal("100"), Decimal("10"), Decimal("11"))

        # 组合汇总
        portfolio = calc.calculate_portfolio(fills, positions)
        print(portfolio.total_pnl)
    """

    def __init__(self, fee_calculator: FeeCalculator | None = None) -> None:
        self._fee_calculator: FeeCalculator = fee_calculator if fee_calculator is not None else AShareFeeCalculator()

    def calculate_realized(self, fill: Fill, side: OrderSide, avg_cost: Decimal) -> RealizedPnl:
        """计算单笔成交的已实现盈亏。

        Args:
            fill: 成交回报（CTR-005，不可变）。使用 fill_price/filled_quantity/symbol。
            side: 买卖方向（Fill 契约无 side 字段，需调用方从 Order 传入）。
            avg_cost: 卖出前的持仓均价（来自 PositionTracker）。

        Returns:
            RealizedPnl: 含毛盈亏、费用分解、净盈亏。

        Note:
            - SELL: gross_pnl = (fill_price - avg_cost) × qty
            - BUY:  gross_pnl = 0（买入不计已实现盈亏，仅更新持仓成本）
            - 费用始终计算（SELL 含印花税，BUY 不含）
            - fill.commission（券商回报佣金）不参与计算，由 FeeCalculator 统一核算；
              阶段2可增加对账逻辑比对两者差异。
        """
        fill_price = fill.fill_price
        qty = fill.filled_quantity
        symbol = fill.symbol

        # 输入校验
        if fill_price <= 0:
            raise InvalidPnlInputError(
                f"fill_price 必须为正, 实际={fill_price}",
                details={"symbol": symbol, "fill_price": str(fill_price)},
            )
        if qty <= 0:
            raise InvalidPnlInputError(
                f"filled_quantity 必须为正, 实际={qty}",
                details={"symbol": symbol, "filled_quantity": str(qty)},
            )
        if avg_cost < 0:
            raise InvalidPnlInputError(
                f"avg_cost 不能为负, 实际={avg_cost}",
                details={"symbol": symbol, "avg_cost": str(avg_cost)},
            )

        turnover = fill_price * qty

        # 毛盈亏：仅卖出计算（买入只更新成本，毛盈亏=0）
        if side == OrderSide.SELL:
            gross_pnl = (fill_price - avg_cost) * qty
        else:
            gross_pnl = Decimal("0")

        fees = self._fee_calculator.calculate(turnover, side)

        _logger.debug(
            "calculate_realized: symbol=%s side=%s qty=%s price=%s avg_cost=%s "
            "turnover=%s gross_pnl=%s fees=%s net_pnl=%s",
            symbol,
            side,
            qty,
            fill_price,
            avg_cost,
            turnover,
            gross_pnl,
            fees.total,
            gross_pnl - fees.total,
        )

        return RealizedPnl(
            symbol=symbol,
            side=side,
            quantity=qty,
            fill_price=fill_price,
            avg_cost=avg_cost,
            turnover=turnover,
            gross_pnl=gross_pnl,
            fees=fees,
        )

    def calculate_unrealized(
        self,
        symbol: str,
        quantity: Decimal,
        avg_cost: Decimal,
        current_price: Decimal,
    ) -> UnrealizedPnl:
        """计算单标的未实现盈亏（浮盈浮亏）。

        Args:
            symbol: 标的代码。
            quantity: 持仓数量（>0 多头, <0 空头, =0 无持仓）。
            avg_cost: 持仓均价。
            current_price: 当前市价。

        Returns:
            UnrealizedPnl: 含毛浮盈亏。

        Note:
            - 多头(quantity>0): gross_pnl = (current_price - avg_cost) × quantity
            - 空头(quantity<0): gross_pnl = (avg_cost - current_price) × |quantity|
            - 零持仓: gross_pnl = 0
        """
        if avg_cost < 0:
            raise InvalidPnlInputError(
                f"avg_cost 不能为负, 实际={avg_cost}",
                details={"symbol": symbol, "avg_cost": str(avg_cost)},
            )
        if current_price < 0:
            raise InvalidPnlInputError(
                f"current_price 不能为负, 实际={current_price}",
                details={"symbol": symbol, "current_price": str(current_price)},
            )

        if quantity == 0:
            gross_pnl = Decimal("0")
        elif quantity > 0:
            # 多头：价格上涨盈利
            gross_pnl = (current_price - avg_cost) * quantity
        else:
            # 空头：价格下跌盈利（反向）
            gross_pnl = (avg_cost - current_price) * (-quantity)

        _logger.debug(
            "calculate_unrealized: symbol=%s qty=%s avg_cost=%s price=%s gross_pnl=%s",
            symbol,
            quantity,
            avg_cost,
            current_price,
            gross_pnl,
        )

        return UnrealizedPnl(
            symbol=symbol,
            quantity=quantity,
            avg_cost=avg_cost,
            current_price=current_price,
            gross_pnl=gross_pnl,
        )

    def calculate_portfolio(
        self,
        fills: list[tuple[Fill, OrderSide, Decimal]],
        positions: list[tuple[str, Decimal, Decimal, Decimal]],
    ) -> PortfolioPnl:
        """计算组合盈亏汇总。

        Args:
            fills: 已实现成交列表，每项为 (fill, side, avg_cost)。
            positions: 持仓列表，每项为 (symbol, quantity, avg_cost, current_price)。

        Returns:
            PortfolioPnl: 含已实现列表、未实现列表及合计属性。
        """
        realized = [self.calculate_realized(fill, side, avg_cost) for (fill, side, avg_cost) in fills]
        unrealized = [
            self.calculate_unrealized(symbol, quantity, avg_cost, current_price)
            for (symbol, quantity, avg_cost, current_price) in positions
        ]
        return PortfolioPnl(realized=realized, unrealized=unrealized)


__all__ = [
    "AShareFeeCalculator",
    "FeeBreakdown",
    "FeeCalculator",
    "FeeConfig",
    "InvalidPnlInputError",
    "PortfolioPnl",
    "PnlCalculator",
    "RealizedPnl",
    "UnrealizedPnl",
]
