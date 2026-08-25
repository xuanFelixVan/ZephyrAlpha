# [BLUEPRINT] MOD-TRADING-012 | docs/03_modules/_domain_trading/eod_processor/blueprint.md | §test
# [MODULE] tests.trading.test_eod_processor
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.eod_processor
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_eod_processor.py
# [A_test] module_id: MOD-TRADING-012 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-TRADING-012 单元测试: EOD Processor — D-TRADING-04 日终处理器。

覆盖: 价格快照 OK/INCOMPLETE/ERROR 三态（探针异常/非正价/全缺/未接线）、NAV 与
未实现盈亏 Decimal 算数、CONFIRMED/DRIFT/SKIPPED、风险重估 OK/ERROR/SKIPPED、
alert/audit 委托与吞没、输入校验 Fail-Closed、15:30 调度规格、报告 frozen。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.trading.eod_processor import (
    EodJobSpec,
    EodPosition,
    EodReport,
    InvalidEodInputError,
    build_eod_job_spec,
    run_eod_processor,
)

FIXED_NOW = datetime(2026, 8, 25, 15, 30, tzinfo=UTC)


def _clock() -> datetime:
    return FIXED_NOW


def _pos(symbol: str = "600519.SH", qty: str = "100", cost: str = "1500.00") -> EodPosition:
    return EodPosition(symbol=symbol, quantity=Decimal(qty), avg_cost=Decimal(cost))


def _probe(mapping: dict[str, str]):
    def _p(symbol: str) -> Decimal:
        return Decimal(mapping[symbol])

    return _p


# ── ① 价格快照三态 ──────────────────────────────────────────────


class TestPriceSnapshot:
    def test_all_priced_ok(self) -> None:
        report = run_eod_processor(
            "2026-08-25",
            positions=[_pos()],
            cash=Decimal("50000"),
            price_probe=_probe({"600519.SH": "1600.00"}),
            clock=_clock,
        )
        assert report.snapshot_status == "OK"
        assert report.priced_symbols == ("600519.SH",)
        assert report.unpriced_symbols == ()

    def test_partial_priced_incomplete(self) -> None:
        positions = [_pos("600519.SH"), _pos("000001.SZ", "200", "10.00")]

        def probe(symbol: str) -> Decimal:
            if symbol == "000001.SZ":
                raise RuntimeError("quote down")
            return Decimal("1600.00")

        report = run_eod_processor(
            "2026-08-25", positions=positions, cash=Decimal("0"), price_probe=probe, clock=_clock
        )
        assert report.snapshot_status == "INCOMPLETE"
        assert report.unpriced_symbols == ("000001.SZ",)
        # 未定价按 0 计且如实披露（不臆造价格）
        assert report.market_value == Decimal("100") * Decimal("1600.00")

    def test_all_unpriced_error(self) -> None:
        def probe(symbol: str) -> Decimal:
            raise RuntimeError("quote down")

        report = run_eod_processor(
            "2026-08-25", positions=[_pos()], cash=Decimal("0"), price_probe=probe, clock=_clock
        )
        assert report.snapshot_status == "ERROR"
        assert report.market_value == Decimal("0")
        assert report.nav == Decimal("0")

    def test_non_positive_price_unpriced(self) -> None:
        report = run_eod_processor(
            "2026-08-25",
            positions=[_pos()],
            cash=Decimal("0"),
            price_probe=_probe({"600519.SH": "0"}),
            clock=_clock,
        )
        assert report.snapshot_status == "ERROR"
        assert report.unpriced_symbols == ("600519.SH",)

    def test_probe_unwired_error(self) -> None:
        report = run_eod_processor(
            "2026-08-25", positions=[_pos()], cash=Decimal("1"), price_probe=None, clock=_clock
        )
        assert report.snapshot_status == "ERROR"
        assert report.unpriced_symbols == ("600519.SH",)

    def test_empty_positions_snapshot_ok(self) -> None:
        report = run_eod_processor("2026-08-25", positions=[], cash=Decimal("123.45"), clock=_clock)
        assert report.snapshot_status == "OK"
        assert report.nav == Decimal("123.45")
        assert report.market_value == Decimal("0")


# ── ② NAV/P&L 算数与确认 ────────────────────────────────────────


class TestNavPnl:
    def test_nav_and_unrealized_pnl(self) -> None:
        positions = [_pos("600519.SH", "100", "1500.00"), _pos("000001.SZ", "200", "10.00")]
        probe = _probe({"600519.SH": "1600.00", "000001.SZ": "9.50"})
        report = run_eod_processor(
            "2026-08-25", positions=positions, cash=Decimal("8000"), price_probe=probe, clock=_clock
        )
        # market_value = 100*1600 + 200*9.5 = 160000 + 1900 = 161900
        assert report.market_value == Decimal("161900.00")
        assert report.nav == Decimal("169900.00")
        # pnl = (1600-1500)*100 + (9.5-10)*200 = 10000 - 100 = 9900
        assert report.unrealized_pnl == Decimal("9900.00")

    def test_nav_confirmed_within_tolerance(self) -> None:
        report = run_eod_processor(
            "2026-08-25",
            positions=[_pos()],
            cash=Decimal("0"),
            price_probe=_probe({"600519.SH": "1600.00"}),
            expected_nav=Decimal("160000.50"),
            clock=_clock,
        )
        assert report.nav_status == "CONFIRMED"

    def test_nav_drift_alerts_and_audits(self) -> None:
        alerts: list[tuple[str, str]] = []
        audits: list[str] = []
        report = run_eod_processor(
            "2026-08-25",
            positions=[_pos()],
            cash=Decimal("0"),
            price_probe=_probe({"600519.SH": "1600.00"}),
            expected_nav=Decimal("150000"),
            alert_sink=lambda d, m: alerts.append((d, m)),
            audit_sink=lambda m: audits.append(m),
            clock=_clock,
        )
        assert report.nav_status == "DRIFT"
        assert len(alerts) == 1 and alerts[0][0] == "2026-08-25"
        assert len(audits) == 1 and "DRIFT" in audits[0]

    def test_nav_status_skipped_without_expected(self) -> None:
        report = run_eod_processor(
            "2026-08-25",
            positions=[_pos()],
            cash=Decimal("0"),
            price_probe=_probe({"600519.SH": "1600.00"}),
            clock=_clock,
        )
        assert report.nav_status == "SKIPPED"

    def test_nav_tolerance_boundary_equal_is_confirmed(self) -> None:
        # |nav-expected| == tolerance → 不越界（严格大于才 DRIFT）
        report = run_eod_processor(
            "2026-08-25",
            positions=[_pos()],
            cash=Decimal("0"),
            price_probe=_probe({"600519.SH": "1600.00"}),
            expected_nav=Decimal("160001.00"),
            nav_tolerance=Decimal("1.00"),
            clock=_clock,
        )
        assert report.nav_status == "CONFIRMED"


# ── ③ 风险重估三态 ──────────────────────────────────────────────


class TestRiskReassessment:
    def test_risk_ok(self) -> None:
        calls: list[tuple[str, Decimal]] = []
        report = run_eod_processor(
            "2026-08-25",
            positions=[],
            cash=Decimal("1"),
            risk_reassess_fn=lambda d, nav: calls.append((d, nav)),
            clock=_clock,
        )
        assert report.risk_status == "OK"
        assert calls == [("2026-08-25", Decimal("1"))]

    def test_risk_error_captured_not_raised(self) -> None:
        alerts: list[tuple[str, str]] = []

        def boom(d: str, nav: Decimal) -> None:
            raise RuntimeError("risk engine down")

        report = run_eod_processor(
            "2026-08-25",
            positions=[],
            cash=Decimal("1"),
            risk_reassess_fn=boom,
            alert_sink=lambda d, m: alerts.append((d, m)),
            clock=_clock,
        )
        assert report.risk_status == "ERROR"
        assert any("risk" in e.lower() or "重估" in e for e in report.errors)
        assert len(alerts) == 1

    def test_risk_skipped_when_unwired(self) -> None:
        report = run_eod_processor("2026-08-25", positions=[], cash=Decimal("1"), clock=_clock)
        assert report.risk_status == "SKIPPED"


# ── ④ 委托吞没与输入校验 ────────────────────────────────────────


class TestDelegationAndValidation:
    def test_alert_sink_exception_swallowed(self) -> None:
        def bad_sink(d: str, m: str) -> None:
            raise RuntimeError("sink down")

        report = run_eod_processor(
            "2026-08-25",
            positions=[_pos()],
            cash=Decimal("0"),
            price_probe=_probe({"600519.SH": "1600.00"}),
            expected_nav=Decimal("1"),
            alert_sink=bad_sink,
            clock=_clock,
        )
        assert report.nav_status == "DRIFT"  # 主链不被告警出口拖死

    def test_audit_sink_exception_swallowed(self) -> None:
        def bad_sink(m: str) -> None:
            raise RuntimeError("sink down")

        report = run_eod_processor(
            "2026-08-25",
            positions=[_pos()],
            cash=Decimal("0"),
            price_probe=_probe({"600519.SH": "1600.00"}),
            expected_nav=Decimal("1"),
            audit_sink=bad_sink,
            clock=_clock,
        )
        assert report.nav_status == "DRIFT"

    def test_empty_trade_date_rejected(self) -> None:
        with pytest.raises(InvalidEodInputError):
            run_eod_processor("", positions=[], cash=Decimal("0"), clock=_clock)

    def test_non_decimal_cash_rejected(self) -> None:
        with pytest.raises(InvalidEodInputError):
            run_eod_processor("2026-08-25", positions=[], cash=1.5, clock=_clock)  # type: ignore[arg-type]

    def test_bad_position_rejected(self) -> None:
        with pytest.raises(InvalidEodInputError):
            EodPosition(symbol="", quantity=Decimal("1"), avg_cost=Decimal("1"))
        with pytest.raises(InvalidEodInputError):
            EodPosition(symbol="X", quantity=Decimal("1"), avg_cost=Decimal("-0.5"))

    def test_report_frozen(self) -> None:
        report = run_eod_processor("2026-08-25", positions=[], cash=Decimal("0"), clock=_clock)
        assert isinstance(report, EodReport)
        with pytest.raises(Exception):  # frozen dataclass
            report.nav = Decimal("9")  # type: ignore[misc]

    def test_captured_at_uses_injected_clock(self) -> None:
        report = run_eod_processor("2026-08-25", positions=[], cash=Decimal("0"), clock=_clock)
        assert report.captured_at == FIXED_NOW


# ── ⑤ 15:30 调度规格 ────────────────────────────────────────────


class TestJobSpec:
    def test_job_spec_shape(self) -> None:
        spec = build_eod_job_spec()
        assert isinstance(spec, EodJobSpec)
        assert spec.job_id == "eod_processor_daily"
        assert spec.cron_expression == "30 15 * * *"  # 与 post_settlement_pipeline 同 15:30 窗口
        assert spec.trading_day_only is True
        assert spec.entrypoint == "zephyr.trading.eod_processor.run_eod_processor"
        assert spec.schema_version == "1.0"
