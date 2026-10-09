# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_portfolio
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_portfolio.py
# [TTL] permanent
"""portfolio 单元测试（52号 四核心模块零单测清偿，AI-WAVE2C-001）。

覆盖: 买卖记账黄金数（扣款/摊薄成本/已实现盈亏/现金回款一致性）、
A股T+1锁定、现金不足/无持仓/超持仓异常、市值与NAV更新、
停牌缺价结转最后已知价（幻视回撤防线）、净值序列/交易日志。
纯内存合成成交夹具，不触网不触库。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.backtest.core.portfolio import (
    BacktestFill,
    Portfolio,
    PortfolioError,
    Position,
)

SYM = "000001.SZ"
D1 = "2024-01-15"
D2 = "2024-01-16"
D3 = "2024-01-17"
D4 = "2024-01-18"


def _fill(
    side: str,
    qty: str,
    price: str,
    date: str = D1,
    commission: str = "5",
    symbol: str = SYM,
) -> BacktestFill:
    """构造合成成交记录夹具。"""
    return BacktestFill(
        date=date,
        symbol=symbol,
        side=side,
        quantity=Decimal(qty),
        price=Decimal(price),
        commission=Decimal(commission),
    )


class TestBacktestFill:
    """BacktestFill.total_cost 口径（price 已含滑点，不得双计滑点）。"""

    def test_buy_total_cost_golden(self):
        f = _fill("BUY", "100", "10.00")
        assert f.total_cost == Decimal("1005")

    def test_sell_total_cost_golden(self):
        f = _fill("SELL", "100", "12.00", date=D3)
        assert f.total_cost == Decimal("1195")


class TestPortfolioInit:
    """初始化契约。"""

    def test_zero_capital_raises(self):
        with pytest.raises(PortfolioError):
            Portfolio(initial_capital=Decimal("0"))

    def test_negative_capital_raises(self):
        with pytest.raises(PortfolioError):
            Portfolio(initial_capital=Decimal("-1000"))

    def test_initial_state(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        assert p.cash == Decimal("100000")
        assert p.initial_capital == Decimal("100000")
        assert p.positions == {}
        assert p.trades_count == 0
        # 初始净值已记录
        nav = p.nav_series
        assert len(nav) == 1
        assert nav.iloc[0] == 100000.0

    def test_error_code(self):
        err = PortfolioError("boom")
        assert err.error_code == "ZA-BT-0003"
        err2 = PortfolioError("boom", error_code="ZA-CUSTOM-1")
        assert err2.error_code == "ZA-CUSTOM-1"


class TestBuyBookkeeping:
    """买入记账（扣款/加仓/摊薄成本黄金数）。"""

    def test_buy_golden(self):
        """BUY 100股@10.00 佣金5: 现金-1005, 均价10.05（含佣金）。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        assert p.cash == Decimal("98995")
        pos = p.get_position(SYM)
        assert pos is not None
        assert pos.quantity == Decimal("100")
        assert pos.avg_cost == Decimal("10.05")
        assert pos.buy_date == D1
        assert pos.realized_pnl == Decimal("0")

    def test_buy_twice_average_cost_dilution(self):
        """两次买入摊薄: (1005 + 1100 + 5) / 200 = 10.55。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        p.apply_fill(_fill("BUY", "100", "11.00", date=D2))
        assert p.cash == Decimal("97890")
        pos = p.get_position(SYM)
        assert pos is not None
        assert pos.quantity == Decimal("200")
        assert pos.avg_cost == Decimal("10.55")
        assert pos.buy_date == D2

    def test_buy_insufficient_cash_raises(self):
        """现金不足: 需1005 仅有1000 → PortfolioError, 状态不变。"""
        p = Portfolio(initial_capital=Decimal("1000"))
        with pytest.raises(PortfolioError):
            p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        assert p.cash == Decimal("1000")
        assert p.get_position(SYM) is None

    def test_buy_exact_cash_boundary(self):
        """边界: 现金恰好等于总成本 → 成交, 现金归零。"""
        p = Portfolio(initial_capital=Decimal("1005"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        assert p.cash == Decimal("0")
        pos = p.get_position(SYM)
        assert pos is not None
        assert pos.quantity == Decimal("100")

    def test_buy_updates_last_price(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        # 缺价日按最后已知价(买入价10.00)估值
        nav = p.update_market_value(D2, {})
        assert nav == pytest.approx(98995.0 + 1000.0)


class TestSellBookkeeping:
    """卖出记账（回款/已实现盈亏/T+1）。"""

    def _portfolio_with_200_shares(self) -> Portfolio:
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        p.apply_fill(_fill("BUY", "100", "11.00", date=D2))
        return p

    def test_sell_golden(self):
        """SELL 100股@12.00 佣金5: 已实现=(12-10.55)*100-5=140, 现金+1195。"""
        p = self._portfolio_with_200_shares()
        p.apply_fill(_fill("SELL", "100", "12.00", date=D3))
        assert p.cash == Decimal("99085")
        pos = p.get_position(SYM)
        assert pos is not None
        assert pos.quantity == Decimal("100")
        assert pos.realized_pnl == Decimal("140")
        assert pos.avg_cost == Decimal("10.55")

    def test_sell_all_resets_avg_cost(self):
        """清仓后 avg_cost 重置为0, 已实现累计280。"""
        p = self._portfolio_with_200_shares()
        p.apply_fill(_fill("SELL", "100", "12.00", date=D3))
        p.apply_fill(_fill("SELL", "100", "12.00", date=D4))
        assert p.cash == Decimal("100280")
        pos = p.get_position(SYM)
        assert pos is not None
        assert pos.quantity == Decimal("0")
        assert pos.avg_cost == Decimal("0")
        assert pos.realized_pnl == Decimal("280")

    def test_t_plus_1_lock(self):
        """T+1: 买入当天卖出 → PortfolioError。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        with pytest.raises(PortfolioError):
            p.apply_fill(_fill("SELL", "100", "10.50", date=D1))

    def test_t_plus_1_lock_state_unchanged(self):
        """T+1拦截后持仓/现金不变（异常隔离）。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        with pytest.raises(PortfolioError):
            p.apply_fill(_fill("SELL", "100", "10.50", date=D1))
        assert p.cash == Decimal("98995")
        pos = p.get_position(SYM)
        assert pos is not None
        assert pos.quantity == Decimal("100")

    def test_allow_t_plus_0_override(self):
        """allow_t_plus_1=True → 当日可卖（T+0 模式）。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        p.apply_fill(_fill("SELL", "100", "10.50", date=D1), allow_t_plus_1=True)
        pos = p.get_position(SYM)
        assert pos is not None
        assert pos.quantity == Decimal("0")
        # 已实现 = (10.50-10.05)*100 - 5 = 40
        assert pos.realized_pnl == Decimal("40")

    def test_next_day_sell_allowed(self):
        """T+1: 次日卖出正常。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        p.apply_fill(_fill("SELL", "100", "10.50", date=D2))
        pos = p.get_position(SYM)
        assert pos is not None
        assert pos.quantity == Decimal("0")

    def test_sell_without_position_raises(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        with pytest.raises(PortfolioError):
            p.apply_fill(_fill("SELL", "100", "10.00", date=D1))

    def test_sell_exceeding_position_raises(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        with pytest.raises(PortfolioError):
            p.apply_fill(_fill("SELL", "200", "10.50", date=D2))
        # 状态不变
        pos = p.get_position(SYM)
        assert pos is not None
        assert pos.quantity == Decimal("100")

    def test_invalid_side_raises(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        with pytest.raises(PortfolioError):
            p.apply_fill(_fill("HOLD", "100", "10.00", date=D1))


class TestMarketValueAndNav:
    """市值/NAV更新 + 停牌缺价结转（幻视回撤防线）。"""

    def test_update_market_value_golden(self):
        """NAV = 现金 + 持仓市值: 98995 + 100*10.50 = 100045。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        nav = p.update_market_value(D1, {SYM: Decimal("10.50")})
        assert nav == pytest.approx(100045.0)

    def test_missing_price_carries_last_known(self):
        """停牌日（prices 无该标的）→ 按最后已知价估值, NAV 不幻视回撤。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        nav1 = p.update_market_value(D1, {SYM: Decimal("10.50")})
        nav2 = p.update_market_value(D2, {})
        assert nav2 == pytest.approx(nav1)

    def test_zero_price_carries_last_known(self):
        """价格为0（脏数据）→ 不按0估值, 结转最后已知价。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        p.update_market_value(D1, {SYM: Decimal("10.50")})
        nav = p.update_market_value(D2, {SYM: Decimal("0")})
        assert nav == pytest.approx(100045.0)

    def test_price_remembered_from_update(self):
        """update 登记的有效价成为新的结转价。"""
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        p.update_market_value(D1, {SYM: Decimal("11.00")})
        nav = p.update_market_value(D2, {})
        assert nav == pytest.approx(98995.0 + 1100.0)

    def test_total_market_value_and_nav(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        mv = p.total_market_value({SYM: Decimal("10.50")})
        assert mv == Decimal("1050.00")
        assert p.total_nav({SYM: Decimal("10.50")}) == Decimal("100045.00")

    def test_empty_portfolio_market_value_zero(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        assert p.total_market_value({SYM: Decimal("10.00")}) == Decimal("0")
        assert p.total_nav({}) == Decimal("100000")


class TestNavSeriesAndLogs:
    """净值序列 / 交易日志 / 持仓视图。"""

    def test_nav_series_accumulates(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        p.update_market_value(D1, {SYM: Decimal("10.00")})
        p.update_market_value(D2, {SYM: Decimal("11.00")})
        nav = p.nav_series
        assert len(nav) == 3  # 初始 + 2次更新
        assert nav.iloc[0] == 100000.0
        assert nav.iloc[1] == pytest.approx(98995.0 + 1000.0)
        assert nav.iloc[2] == pytest.approx(98995.0 + 1100.0)

    def test_trades_log_and_count(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        p.apply_fill(_fill("SELL", "100", "10.50", date=D2))
        assert p.trades_count == 2
        log = p.trades_log
        assert log[0]["side"] == "BUY"
        assert log[0]["symbol"] == SYM
        assert log[0]["quantity"] == 100.0
        assert log[0]["total_cost"] == 1005.0
        assert log[1]["side"] == "SELL"

    def test_positions_property_returns_copy(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        view = p.positions
        view["HACK.SZ"] = Position(symbol="HACK.SZ")
        assert p.get_position("HACK.SZ") is None
        assert SYM in p.positions

    def test_trades_log_returns_copy(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        p.apply_fill(_fill("BUY", "100", "10.00", date=D1))
        view = p.trades_log
        view.clear()
        assert p.trades_count == 1

    def test_get_position_unknown_returns_none(self):
        p = Portfolio(initial_capital=Decimal("100000"))
        assert p.get_position("999999.SH") is None
