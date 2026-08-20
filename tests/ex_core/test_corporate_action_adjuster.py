# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TESTS] tests/ex_core/test_corporate_action_adjuster.py
# [TTL] task_bound
# 对应: src/zephyr/ex_core/corporate_action_adjuster.py
# 覆盖: gap 15 除权除息处理（参考价/持仓调整/涨跌停重算）
"""CorporateActionAdjuster 单元测试（40_execution_broker §决策⑯ gap 15）。"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from zephyr.ex_core.corporate_action_adjuster import (
    CorporateAction,
    CorporateActionAdjuster,
    CorporateActionAdjusterError,
    CorporateActionType,
    compute_ex_dividend_price,
)


def _make_action(
    symbol: str = "600000.SH",
    cash: Decimal = Decimal("0"),
    stock_ratio: Decimal = Decimal("0"),
    record_close: Decimal = Decimal("10.00"),
) -> CorporateAction:
    return CorporateAction(
        symbol=symbol,
        ex_date=date(2026, 8, 10),
        record_date=date(2026, 8, 7),
        cash_dividend_per_share=cash,
        stock_dividend_ratio=stock_ratio,
        record_close=record_close,
    )


# ───────────────────────── 公司行动类型 ─────────────────────────


class TestActionType:
    """公司行动类型判断。"""

    def test_cash_dividend_only(self):
        action = _make_action(cash=Decimal("0.50"))
        assert action.action_type is CorporateActionType.CASH_DIVIDEND

    def test_stock_dividend_only(self):
        action = _make_action(stock_ratio=Decimal("0.1"))
        assert action.action_type is CorporateActionType.STOCK_DIVIDEND

    def test_cash_and_stock(self):
        action = _make_action(cash=Decimal("0.50"), stock_ratio=Decimal("0.1"))
        assert action.action_type is CorporateActionType.CASH_AND_STOCK

    def test_none(self):
        action = _make_action()
        assert action.action_type is CorporateActionType.NONE


# ───────────────────────── 除权除息参考价 ─────────────────────────


class TestExDividendPrice:
    """除权除息参考价计算。"""

    def test_cash_dividend_only(self):
        """仅现金分红：参考价 = 收盘价 - 现金红利。"""
        action = _make_action(cash=Decimal("0.50"), record_close=Decimal("10.00"))
        price = compute_ex_dividend_price(action)
        assert price == Decimal("9.50")

    def test_stock_dividend_only(self):
        """仅送股：参考价 = 收盘价 / (1 + 送转比例)。"""
        action = _make_action(stock_ratio=Decimal("0.1"), record_close=Decimal("10.00"))
        price = compute_ex_dividend_price(action)
        # 10 / 1.1 = 9.0909... → 9.09
        assert price == Decimal("9.09")

    def test_cash_and_stock(self):
        """现金分红 + 送股：参考价 = (收盘价 - 现金红利) / (1 + 送转比例)。"""
        action = _make_action(
            cash=Decimal("0.50"),
            stock_ratio=Decimal("0.1"),
            record_close=Decimal("10.00"),
        )
        price = compute_ex_dividend_price(action)
        # (10 - 0.5) / 1.1 = 9.5/1.1 = 8.6363... → 8.64
        assert price == Decimal("8.64")

    def test_invalid_record_close_raises(self):
        """登记日收盘价无效 → 抛错。"""
        action = _make_action(cash=Decimal("0.50"), record_close=Decimal("0"))
        with pytest.raises(CorporateActionAdjusterError):
            compute_ex_dividend_price(action)


# ───────────────────────── 调整前收盘价 ─────────────────────────


class TestAdjustedPrevClose:
    """调整前收盘价。"""

    def test_no_action_returns_original(self):
        """无除权除息 → 返回原始前收盘价。"""
        adjuster = CorporateActionAdjuster()
        result = adjuster.get_adjusted_prev_close("600000.SH", Decimal("10.00"))
        assert result == Decimal("10.00")

    def test_with_action_returns_ex_price(self):
        """有除权除息 → 返回除权除息参考价。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action(cash=Decimal("0.50")))
        result = adjuster.get_adjusted_prev_close("600000.SH", Decimal("10.00"))
        assert result == Decimal("9.50")


# ───────────────────────── 调整涨跌停价 ─────────────────────────


class TestAdjustedLimitPrices:
    """调整涨跌停价。"""

    def test_no_action_uses_original(self):
        """无除权除息 → 用原始前收盘价算涨跌停。"""
        adjuster = CorporateActionAdjuster()
        up, down = adjuster.get_adjusted_limit_prices("600000.SH", Decimal("10.00"))
        assert up == Decimal("11.00")
        assert down == Decimal("9.00")

    def test_with_action_uses_adjusted(self):
        """有除权除息 → 用调整后的前收盘价算涨跌停。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action(cash=Decimal("0.50")))
        up, down = adjuster.get_adjusted_limit_prices("600000.SH", Decimal("10.00"))
        # 调整后前收盘 = 9.50，涨跌停 = 9.50 ± 10%
        assert up == Decimal("10.45")
        assert down == Decimal("8.55")

    def test_custom_price_limit_pct(self):
        """自定义涨跌幅（ST 5%）。"""
        adjuster = CorporateActionAdjuster()
        up, down = adjuster.get_adjusted_limit_prices(
            "600000.SH",
            Decimal("10.00"),
            price_limit_pct=Decimal("0.05"),
        )
        assert up == Decimal("10.50")
        assert down == Decimal("9.50")


# ───────────────────────── 持仓调整 ─────────────────────────


class TestAdjustPosition:
    """持仓调整（送股 + 成本摊薄 + 现金红利）。"""

    def test_no_action_returns_none(self):
        """无除权除息 → 返回 None。"""
        adjuster = CorporateActionAdjuster()
        result = adjuster.adjust_position("600000.SH", Decimal("1000"), Decimal("10.00"))
        assert result is None

    def test_stock_dividend_increases_qty(self):
        """送股增加股数。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action(stock_ratio=Decimal("0.1")))
        result = adjuster.adjust_position("600000.SH", Decimal("1000"), Decimal("10.00"))

        assert result is not None
        # 1000 × (1 + 0.1) = 1100
        assert result.new_position_qty == Decimal("1100")

    def test_cash_dividend_doesnt_change_qty(self):
        """现金分红不改变股数。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action(cash=Decimal("0.50")))
        result = adjuster.adjust_position("600000.SH", Decimal("1000"), Decimal("10.00"))

        assert result is not None
        assert result.new_position_qty == Decimal("1000")

    def test_cash_dividend_received(self):
        """现金红利总额计算。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action(cash=Decimal("0.50")))
        result = adjuster.adjust_position("600000.SH", Decimal("1000"), Decimal("10.00"))

        # 1000 股 × 0.5 元 = 500 元
        assert result.cash_dividend_received == Decimal("500")

    def test_avg_cost_diluted_after_stock_dividend(self):
        """送股后持仓成本摊薄。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action(stock_ratio=Decimal("0.1")))
        result = adjuster.adjust_position("600000.SH", Decimal("1000"), Decimal("10.00"))

        # 总成本 = 1000 × 10 = 10000，新股数 = 1100
        # new_avg_cost = 10000 / 1100 = 9.0909 → 9.0909
        assert result.new_avg_cost == Decimal("9.0909")

    def test_avg_cost_diluted_after_cash_and_stock(self):
        """现金分红 + 送股后成本摊薄。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(
            _make_action(
                cash=Decimal("0.50"),
                stock_ratio=Decimal("0.1"),
            )
        )
        result = adjuster.adjust_position("600000.SH", Decimal("1000"), Decimal("10.00"))

        # 总成本 = 1000 × 10 = 10000，现金红利 = 500
        # new_total_cost = 10000 - 500 = 9500，新股数 = 1100
        # new_avg_cost = 9500 / 1100 = 8.6363 → 8.6364
        assert result.new_avg_cost == Decimal("8.6364")
        assert result.cash_dividend_received == Decimal("500")

    def test_new_prev_close_in_result(self):
        """调整结果包含新前收盘价。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action(cash=Decimal("0.50")))
        result = adjuster.adjust_position("600000.SH", Decimal("1000"), Decimal("10.00"))

        assert result.new_prev_close == Decimal("9.50")


# ───────────────────────── 注册与查询 ─────────────────────────


class TestRegisterAndQuery:
    """注册与查询。"""

    def test_register_and_has_action(self):
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action(cash=Decimal("0.50")))

        assert adjuster.has_action("600000.SH") is True
        assert adjuster.has_action("000001.SZ") is False

    def test_batch_register(self):
        adjuster = CorporateActionAdjuster()
        actions = [
            _make_action(symbol="600000.SH", cash=Decimal("0.50")),
            _make_action(symbol="000001.SZ", stock_ratio=Decimal("0.1")),
        ]
        adjuster.batch_register(actions)

        assert adjuster.has_action("600000.SH") is True
        assert adjuster.has_action("000001.SZ") is True

    def test_none_action_not_registered(self):
        """NONE 类型不注册。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action())  # 无分红无送转

        assert adjuster.has_action("600000.SH") is False

    def test_symbols_with_actions(self):
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_make_action(symbol="600000.SH", cash=Decimal("0.50")))
        adjuster.register_action(_make_action(symbol="000001.SZ", stock_ratio=Decimal("0.1")))

        syms = adjuster.symbols_with_actions()
        assert set(syms) == {"600000.SH", "000001.SZ"}

    def test_get_action(self):
        adjuster = CorporateActionAdjuster()
        action = _make_action(cash=Decimal("0.50"))
        adjuster.register_action(action)

        got = adjuster.get_action("600000.SH")
        assert got is not None
        assert got.cash_dividend_per_share == Decimal("0.50")
