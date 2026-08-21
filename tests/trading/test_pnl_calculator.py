# [BLUEPRINT] MOD-TRADING-002 | docs/03_modules/_domain_trading/pnl_calculator/blueprint.md
# [MODULE] tests.trading.test_pnl_calculator
# [DOMAIN] D_TRADING
# [INVARIANTS] Decimal-only断言; 验证frozen不可变; 费率边界(佣金最低¥5/印花税卖出/过户费双向)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPnlInputError(ZA-TR-0019)
# [TESTS] self
# [A_module] module_id=MOD-TRADING-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-TRADING-002 PnL Calculator 单元测试.

覆盖（blueprint §9）:
  - 已实现盈亏(卖): 毛盈亏/费用/净盈亏
  - 未实现盈亏: 多头盈利/亏损, 空头盈利/亏损, 零持仓
  - A股费率: 佣金最低¥5, 印花税仅卖出, 过户费双向
  - 组合盈亏汇总: total_realized/total_unrealized/total_pnl/total_fees
  - 边界值: 零持仓, 负均价/负市价/非正价拒绝
  - Decimal精度: 结果为Decimal非float
  - frozen不可变: dataclass frozen=True
  - 依赖注入: 自定义FeeCalculator/FeeConfig
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.fill import Fill
from zephyr.trading.pnl_calculator import (
    AShareFeeCalculator,
    FeeBreakdown,
    FeeConfig,
    InvalidPnlInputError,
    PnlCalculator,
)

# ── 辅助构造 ──


def make_fill(
    symbol: str = "600000",
    fill_price: Decimal = Decimal("10"),
    filled_quantity: Decimal = Decimal("100"),
    fill_id: str = "F001",
) -> Fill:
    """构造测试用 Fill（CTR-005）。"""
    return Fill(
        fill_id=fill_id,
        fill_price=fill_price,
        fill_timestamp=datetime.now(UTC),
        filled_quantity=filled_quantity,
        idempotency_key=f"ik-{fill_id}",
        order_id=f"O-{fill_id}",
        strategy_id="S001",
        symbol=symbol,
    )


# ── A股费率计算器测试 ──


class TestAShareFeeCalculator:
    def test_commission_uses_min_when_below_threshold(self) -> None:
        """小单佣金不足¥5时取最低¥5。"""
        calc = AShareFeeCalculator()
        # turnover=100, commission_rate=0.0000854（#233）→ 0.00854 < 5 → 取5
        fees = calc.calculate(Decimal("100"), OrderSide.BUY)
        assert fees.commission == Decimal("5")

    def test_commission_uses_rate_when_above_threshold(self) -> None:
        """大单佣金按费率计算（超过最低¥5）。"""
        calc = AShareFeeCalculator()
        # turnover=100000, 0.0000854（#233）→ 8.54 > 5 → 取8.54
        fees = calc.calculate(Decimal("100000"), OrderSide.BUY)
        assert fees.commission == Decimal("8.54")

    def test_stamp_duty_only_on_sell(self) -> None:
        """印花税仅卖出收取。"""
        calc = AShareFeeCalculator()
        buy_fees = calc.calculate(Decimal("10000"), OrderSide.BUY)
        sell_fees = calc.calculate(Decimal("10000"), OrderSide.SELL)
        assert buy_fees.stamp_duty == Decimal("0")
        # 10000 * 0.0005 = 5
        assert sell_fees.stamp_duty == Decimal("5")

    def test_transfer_fee_both_directions(self) -> None:
        """过户费双向收取。"""
        calc = AShareFeeCalculator()
        buy_fees = calc.calculate(Decimal("10000"), OrderSide.BUY)
        sell_fees = calc.calculate(Decimal("10000"), OrderSide.SELL)
        # 10000 * 0.00001 = 0.1
        assert buy_fees.transfer_fee == Decimal("0.1")
        assert sell_fees.transfer_fee == Decimal("0.1")

    def test_fee_breakdown_total(self) -> None:
        """FeeBreakdown.total = 佣金+印花税+过户费。"""
        calc = AShareFeeCalculator()
        fees = calc.calculate(Decimal("100000"), OrderSide.SELL)
        # commission=8.54（#233）, stamp_duty=50, transfer_fee=1
        assert fees.total == Decimal("59.54")

    def test_custom_fee_config(self) -> None:
        """自定义 FeeConfig 生效。"""
        custom_cfg = FeeConfig(
            commission_rate=Decimal("0.001"),  # 0.1%
            commission_min=Decimal("1"),
            stamp_duty_rate=Decimal("0.001"),  # 0.1%
            transfer_fee_rate=Decimal("0"),
        )
        calc = AShareFeeCalculator(custom_cfg)
        fees = calc.calculate(Decimal("10000"), OrderSide.SELL)
        # commission=10000*0.001=10, stamp_duty=10, transfer_fee=0
        assert fees.commission == Decimal("10")
        assert fees.stamp_duty == Decimal("10")
        assert fees.transfer_fee == Decimal("0")
        assert fees.total == Decimal("20")


# ── 已实现盈亏测试 ──


class TestRealizedPnl:
    def test_sell_realized_pnl_basic(self) -> None:
        """卖出已实现盈亏: 毛盈亏-费用=净盈亏。"""
        calc = PnlCalculator()
        fill = make_fill(fill_price=Decimal("11"), filled_quantity=Decimal("100"))
        result = calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("10"))
        # turnover=1100, gross=(11-10)*100=100
        # commission=max(1100*0.0000854,5)=max(0.09394,5)=5（#233）
        # stamp_duty=1100*0.0005=0.55, transfer_fee=1100*0.00001=0.011
        # fees=5.561, net=100-5.561=94.439
        assert result.symbol == "600000"
        assert result.side == OrderSide.SELL
        assert result.quantity == Decimal("100")
        assert result.fill_price == Decimal("11")
        assert result.avg_cost == Decimal("10")
        assert result.turnover == Decimal("1100")
        assert result.gross_pnl == Decimal("100")
        assert result.fees.commission == Decimal("5")
        assert result.fees.stamp_duty == Decimal("0.55")
        assert result.fees.transfer_fee == Decimal("0.011")
        assert result.fees.total == Decimal("5.561")
        assert result.net_pnl == Decimal("94.439")

    def test_sell_realized_pnl_large_turnover(self) -> None:
        """大单卖出: 佣金按费率计算(超最低¥5)。"""
        calc = PnlCalculator()
        fill = make_fill(fill_price=Decimal("100"), filled_quantity=Decimal("1000"))
        result = calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("90"))
        # turnover=100000, gross=(100-90)*1000=10000
        # commission=max(8.54,5)=8.54（#233）, stamp_duty=50, transfer_fee=1 → fees=59.54
        # net=10000-59.54=9940.46
        assert result.gross_pnl == Decimal("10000")
        assert result.fees.commission == Decimal("8.54")
        assert result.fees.total == Decimal("59.54")
        assert result.net_pnl == Decimal("9940.46")

    def test_sell_realized_pnl_loss(self) -> None:
        """亏损卖出: 毛盈亏为负。"""
        calc = PnlCalculator()
        fill = make_fill(fill_price=Decimal("9"), filled_quantity=Decimal("100"))
        result = calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("10"))
        # gross=(9-10)*100=-100, turnover=900
        # commission=max(900*0.0000854,5)=max(0.07686,5)=5（#233）
        # stamp_duty=900*0.0005=0.45, transfer_fee=900*0.00001=0.009
        # fees=5.459, net=-100-5.459=-105.459
        assert result.gross_pnl == Decimal("-100")
        assert result.fees.total == Decimal("5.459")
        assert result.net_pnl == Decimal("-105.459")

    def test_buy_realized_pnl_gross_zero(self) -> None:
        """买入不计已实现盈亏(毛盈亏=0), 但费用仍计入。"""
        calc = PnlCalculator()
        fill = make_fill(fill_price=Decimal("10"), filled_quantity=Decimal("100"))
        result = calc.calculate_realized(fill, OrderSide.BUY, avg_cost=Decimal("10"))
        # gross=0, turnover=1000
        # commission=max(0.0854,5)=5（#233）, stamp_duty=0(BUY), transfer_fee=0.01
        # fees=5.01, net=0-5.01=-5.01
        assert result.gross_pnl == Decimal("0")
        assert result.fees.stamp_duty == Decimal("0")
        assert result.fees.total == Decimal("5.01")
        assert result.net_pnl == Decimal("-5.01")

    def test_sell_breakeven_gross_zero(self) -> None:
        """平价卖出: 毛盈亏=0, 仍有费用。"""
        calc = PnlCalculator()
        fill = make_fill(fill_price=Decimal("10"), filled_quantity=Decimal("100"))
        result = calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("10"))
        assert result.gross_pnl == Decimal("0")
        # SELL 有印花税
        assert result.fees.stamp_duty == Decimal("0.5")

    def test_invalid_negative_avg_cost(self) -> None:
        """负均价拒绝。"""
        calc = PnlCalculator()
        fill = make_fill()
        with pytest.raises(InvalidPnlInputError) as exc_info:
            calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("-1"))
        assert exc_info.value.error_code == "ZA-TR-0019"
        assert "avg_cost" in exc_info.value.message

    def test_invalid_zero_fill_price(self) -> None:
        """非正成交价拒绝。"""
        calc = PnlCalculator()
        fill = make_fill(fill_price=Decimal("0"))
        with pytest.raises(InvalidPnlInputError):
            calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("10"))

    def test_invalid_zero_quantity(self) -> None:
        """非正成交数量拒绝。"""
        calc = PnlCalculator()
        fill = make_fill(filled_quantity=Decimal("0"))
        with pytest.raises(InvalidPnlInputError):
            calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("10"))


# ── 未实现盈亏测试 ──


class TestUnrealizedPnl:
    def test_long_position_profit(self) -> None:
        """多头浮盈。"""
        calc = PnlCalculator()
        result = calc.calculate_unrealized("600000", Decimal("100"), Decimal("10"), Decimal("11"))
        # (11-10)*100=100
        assert result.gross_pnl == Decimal("100")
        assert result.quantity == Decimal("100")

    def test_long_position_loss(self) -> None:
        """多头浮亏。"""
        calc = PnlCalculator()
        result = calc.calculate_unrealized("600000", Decimal("100"), Decimal("10"), Decimal("9"))
        # (9-10)*100=-100
        assert result.gross_pnl == Decimal("-100")

    def test_short_position_profit(self) -> None:
        """空头浮盈(价格下跌盈利, 反向)。"""
        calc = PnlCalculator()
        result = calc.calculate_unrealized("600000", Decimal("-100"), Decimal("10"), Decimal("9"))
        # (10-9)*100=100
        assert result.gross_pnl == Decimal("100")

    def test_short_position_loss(self) -> None:
        """空头浮亏(价格上涨亏损, 反向)。"""
        calc = PnlCalculator()
        result = calc.calculate_unrealized("600000", Decimal("-100"), Decimal("10"), Decimal("11"))
        # (10-11)*100=-100
        assert result.gross_pnl == Decimal("-100")

    def test_zero_position(self) -> None:
        """零持仓浮盈亏=0。"""
        calc = PnlCalculator()
        result = calc.calculate_unrealized("600000", Decimal("0"), Decimal("10"), Decimal("11"))
        assert result.gross_pnl == Decimal("0")

    def test_breakeven_price_equals_cost(self) -> None:
        """市价=成本价, 浮盈亏=0。"""
        calc = PnlCalculator()
        result = calc.calculate_unrealized("600000", Decimal("100"), Decimal("10"), Decimal("10"))
        assert result.gross_pnl == Decimal("0")

    def test_invalid_negative_avg_cost(self) -> None:
        """负均价拒绝。"""
        calc = PnlCalculator()
        with pytest.raises(InvalidPnlInputError):
            calc.calculate_unrealized("600000", Decimal("100"), Decimal("-1"), Decimal("11"))

    def test_invalid_negative_current_price(self) -> None:
        """负市价拒绝。"""
        calc = PnlCalculator()
        with pytest.raises(InvalidPnlInputError):
            calc.calculate_unrealized("600000", Decimal("100"), Decimal("10"), Decimal("-1"))


# ── 组合盈亏汇总测试 ──


class TestPortfolioPnl:
    def test_portfolio_aggregation(self) -> None:
        """组合汇总: total_realized + total_unrealized = total_pnl。"""
        calc = PnlCalculator()
        fills = [
            # 卖出1: price=11,qty=100,cost=10 → gross=100, fees=5.561, net=94.439
            (make_fill(fill_price=Decimal("11"), fill_id="F1"), OrderSide.SELL, Decimal("10")),
            # 卖出2: price=100,qty=1000,cost=90 → gross=10000, fees=59.54（#233）, net=9940.46
            (
                make_fill(fill_price=Decimal("100"), filled_quantity=Decimal("1000"), fill_id="F2"),
                OrderSide.SELL,
                Decimal("90"),
            ),
        ]
        positions = [
            # 持仓1: qty=100,cost=10,price=11 → unrealized=100
            ("600000", Decimal("100"), Decimal("10"), Decimal("11")),
            # 持仓2: qty=200,cost=20,price=18 → unrealized=(18-20)*200=-400
            ("000001", Decimal("200"), Decimal("20"), Decimal("18")),
        ]
        portfolio = calc.calculate_portfolio(fills, positions)

        assert len(portfolio.realized) == 2
        assert len(portfolio.unrealized) == 2
        # total_realized = 94.439 + 9940.46 = 10034.899（#233 重算）
        assert portfolio.total_realized == Decimal("10034.899")
        # total_unrealized = 100 + (-400) = -300
        assert portfolio.total_unrealized == Decimal("-300")
        # total_pnl = 10034.899 + (-300) = 9734.899
        assert portfolio.total_pnl == Decimal("9734.899")
        # total_fees = 5.561 + 59.54 = 65.101
        assert portfolio.total_fees == Decimal("65.101")

    def test_portfolio_empty(self) -> None:
        """空组合: 全部合计=0。"""
        calc = PnlCalculator()
        portfolio = calc.calculate_portfolio([], [])
        assert portfolio.total_realized == Decimal("0")
        assert portfolio.total_unrealized == Decimal("0")
        assert portfolio.total_pnl == Decimal("0")
        assert portfolio.total_fees == Decimal("0")

    def test_portfolio_fees_only_when_all_buys(self) -> None:
        """全买入: 毛盈亏=0, 仅费用。"""
        calc = PnlCalculator()
        fills = [
            (make_fill(fill_price=Decimal("10"), fill_id="F1"), OrderSide.BUY, Decimal("10")),
        ]
        positions = []
        portfolio = calc.calculate_portfolio(fills, positions)
        assert portfolio.total_realized == Decimal("-5.01")  # 仅费用
        assert portfolio.total_fees == Decimal("5.01")


# ── Decimal精度 + frozen不可变 ──


class TestInvariants:
    def test_all_amounts_are_decimal(self) -> None:
        """所有金额结果为 Decimal, 无 float 污染。"""
        calc = PnlCalculator()
        fill = make_fill(fill_price=Decimal("11"), filled_quantity=Decimal("100"))
        realized = calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("10"))
        unrealized = calc.calculate_unrealized("600000", Decimal("100"), Decimal("10"), Decimal("11"))
        assert isinstance(realized.gross_pnl, Decimal)
        assert isinstance(realized.turnover, Decimal)
        assert isinstance(realized.fees.commission, Decimal)
        assert isinstance(realized.fees.stamp_duty, Decimal)
        assert isinstance(realized.fees.transfer_fee, Decimal)
        assert isinstance(realized.fees.total, Decimal)
        assert isinstance(realized.net_pnl, Decimal)
        assert isinstance(unrealized.gross_pnl, Decimal)

    def test_realized_pnl_is_frozen(self) -> None:
        """RealizedPnl 不可变。"""
        calc = PnlCalculator()
        fill = make_fill()
        result = calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("10"))
        with pytest.raises(Exception):
            result.gross_pnl = Decimal("999")  # type: ignore[misc]

    def test_fee_breakdown_is_frozen(self) -> None:
        """FeeBreakdown 不可变。"""
        calc = AShareFeeCalculator()
        fees = calc.calculate(Decimal("10000"), OrderSide.SELL)
        with pytest.raises(Exception):
            fees.commission = Decimal("999")  # type: ignore[misc]

    def test_fee_config_is_frozen(self) -> None:
        """FeeConfig 不可变。"""
        cfg = FeeConfig()
        with pytest.raises(Exception):
            cfg.commission_rate = Decimal("0.5")  # type: ignore[misc]

    def test_net_pnl_equals_gross_minus_fees(self) -> None:
        """不变量: net_pnl = gross_pnl - fees.total 恒成立。"""
        calc = PnlCalculator()
        for price, cost in [
            (Decimal("11"), Decimal("10")),
            (Decimal("9"), Decimal("10")),
            (Decimal("10"), Decimal("10")),
            (Decimal("100"), Decimal("90")),
        ]:
            fill = make_fill(fill_price=price, filled_quantity=Decimal("100"))
            result = calc.calculate_realized(fill, OrderSide.SELL, avg_cost=cost)
            assert result.net_pnl == result.gross_pnl - result.fees.total


# ── 依赖注入测试 ──


class TestDependencyInjection:
    def test_custom_fee_calculator_injection(self) -> None:
        """注入自定义 FeeCalculator, 验证被使用。"""

        class ZeroFeeCalculator:
            """零费用计算器(测试用)。"""

            def calculate(self, turnover: Decimal, side: OrderSide) -> FeeBreakdown:
                return FeeBreakdown(
                    commission=Decimal("0"),
                    stamp_duty=Decimal("0"),
                    transfer_fee=Decimal("0"),
                )

        calc = PnlCalculator(fee_calculator=ZeroFeeCalculator())
        fill = make_fill(fill_price=Decimal("11"), filled_quantity=Decimal("100"))
        result = calc.calculate_realized(fill, OrderSide.SELL, avg_cost=Decimal("10"))
        # gross=100, fees=0, net=100
        assert result.fees.total == Decimal("0")
        assert result.net_pnl == Decimal("100")

    def test_default_fee_calculator_is_ashare(self) -> None:
        """默认使用 AShareFeeCalculator。"""
        calc = PnlCalculator()
        assert isinstance(calc._fee_calculator, AShareFeeCalculator)

    def test_fee_calculator_protocol_satisfied(self) -> None:
        """AShareFeeCalculator 满足 FeeCalculator Protocol。"""
        from zephyr.trading.pnl_calculator import FeeCalculator

        calc = AShareFeeCalculator()
        assert isinstance(calc, FeeCalculator)
