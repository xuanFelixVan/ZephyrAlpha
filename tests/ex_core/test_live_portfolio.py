# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_live_portfolio
# [DOMAIN] D_EX_CORE
# [INVARIANTS] RiskSnapshot契约注入; 快照失败Fail-Closed不出视图; 缺价持仓不补零; 只读服务不改链路状态
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LivePortfolioError
# [TESTS] self
# [TTL] permanent
"""实盘组合服务测试（MOD-L06-001，阶段9 执行链路批）。"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.services.live_portfolio import (
    LivePortfolioError,
    LivePortfolioService,
)
from zephyr.risk.core.risk_data_pipeline import (
    FillsWindowSummary,
    PositionRiskView,
    RiskSnapshot,
)

_AS_OF = datetime(2026, 8, 23, 10, 0, tzinfo=UTC)


def _snapshot(
    *,
    cash: Decimal = Decimal("50000"),
    positions: tuple[PositionRiskView, ...] = (),
    total_market_value: Decimal = Decimal("0"),
    degraded: bool = False,
    warnings: tuple[str, ...] = (),
    missing: tuple[str, ...] = (),
) -> RiskSnapshot:
    nav = cash + total_market_value
    return RiskSnapshot(
        snapshot_id="rs-test",
        as_of=_AS_OF,
        portfolio_id="pf-live",
        cash=cash,
        nav=nav,
        total_market_value=total_market_value,
        gross_leverage=float(total_market_value / nav) if nav > 0 else 0.0,
        positions=positions,
        fills_summary=FillsWindowSummary(
            window_start=_AS_OF,
            window_end=_AS_OF,
            fill_count=0,
            total_notional=Decimal("0"),
            total_commission=Decimal("0"),
            symbols=(),
        ),
        limits=None,
        missing_price_symbols=missing,
        suspended_held_symbols=(),
        degraded=degraded,
        data_warnings=warnings,
    )


class TestCurrentView:
    def test_view_fields_from_snapshot(self):
        pos = PositionRiskView(
            symbol="600000.SH",
            quantity=Decimal("1000"),
            price_available=True,
            last_price=Decimal("10"),
            market_value=Decimal("10000"),
            weight=0.2,
            sellable_quantity=Decimal("1000"),
        )
        service = LivePortfolioService(lambda: _snapshot(positions=(pos,), total_market_value=Decimal("10000")))
        view = service.current_view()
        assert view.portfolio_id == "pf-live"
        assert view.nav == Decimal("60000")
        assert view.cash == Decimal("50000")
        assert len(view.positions) == 1
        assert view.positions[0].symbol == "600000.SH"
        assert view.positions[0].market_value == Decimal("10000")
        assert view.degraded is False

    def test_missing_price_not_zero_filled(self):
        pos = PositionRiskView(
            symbol="300001.SZ",
            quantity=Decimal("500"),
            price_available=False,
        )
        service = LivePortfolioService(
            lambda: _snapshot(
                positions=(pos,),
                degraded=True,
                warnings=("missing_prices:300001.SZ",),
                missing=("300001.SZ",),
            )
        )
        view = service.current_view()
        assert view.positions[0].market_value is None  # 缺价不补零
        assert view.positions[0].weight is None
        assert view.degraded is True
        assert view.missing_price_symbols == ("300001.SZ",)

    def test_snapshot_failure_fail_closed(self):
        def _boom():
            raise RuntimeError("position provider offline")

        service = LivePortfolioService(_boom)
        with pytest.raises(LivePortfolioError) as exc_info:
            service.current_view()
        assert exc_info.value.error_code == "ZA-EX-0021"


class TestQueries:
    def test_available_cash(self):
        service = LivePortfolioService(lambda: _snapshot(cash=Decimal("12345.67")))
        assert service.available_cash() == Decimal("12345.67")

    def test_position_of_hit_and_miss(self):
        pos = PositionRiskView(
            symbol="600000.SH",
            quantity=Decimal("1000"),
            price_available=True,
            last_price=Decimal("10"),
            market_value=Decimal("10000"),
            weight=0.2,
        )
        service = LivePortfolioService(lambda: _snapshot(positions=(pos,), total_market_value=Decimal("10000")))
        assert service.position_of("600000.SH").quantity == Decimal("1000")
        assert service.position_of("000001.SZ") is None  # 未持仓≠持仓为0

    def test_available_cash_fail_closed(self):
        def _boom():
            raise RuntimeError("offline")

        service = LivePortfolioService(_boom)
        with pytest.raises(LivePortfolioError):
            service.available_cash()
