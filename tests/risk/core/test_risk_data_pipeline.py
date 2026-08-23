# [BLUEPRINT] MOD-RK-25 | docs/03_modules/MOD-RK-25/ | §test
# [MODULE] tests.risk.core.test_risk_data_pipeline
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.risk_data_pipeline
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_risk_data_pipeline.py
# [A_test] module_id: MOD-RK-25 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-RK-25 单元测试: RiskDataPipeline — 风控数据底座快照装配。

覆盖: assemble_risk_snapshot 纯函数（权重/nav/降级/停牌/异常分支）、
FillsWindowSummary 聚合、sellable 接口位、RiskDataPipeline 编排
（provider 失败 fail-closed / 降级路径）。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.core.risk_data_pipeline",
    reason="risk_data_pipeline not importable",
)

from zephyr.risk.core.risk_data_pipeline import (  # noqa: E402
    RiskDataPipeline,
    RiskDataPipelineError,
    RiskSnapshotInput,
    RiskSnapshot,
    assemble_risk_snapshot,
)
from zephyr.shared.contracts.fill import Fill  # noqa: E402
from zephyr.shared.contracts.market_data import NormalizedMarketData  # noqa: E402
from zephyr.shared.contracts.position import PositionSnapshot  # noqa: E402
from zephyr.shared.contracts.risk_limits import RiskLimits  # noqa: E402

# ── 夹具辅助 ─────────────────────────────────────────────────────────


def _quote(
    symbol: str,
    close: str,
    *,
    suspended: bool = False,
    volume: str = "1000",
) -> NormalizedMarketData:
    return NormalizedMarketData(
        symbol=symbol,
        timestamp=datetime(2026, 8, 21, 15, 0, tzinfo=UTC),
        open=Decimal(close),
        high=Decimal(close),
        low=Decimal(close),
        close=Decimal(close),
        volume=Decimal(volume),
        data_source="stub",
        idempotency_key=f"q-{symbol}",
        is_suspended=suspended,
    )


def _positions(
    holdings: dict[str, str],
    market_values: dict[str, str] | None = None,
    cash: str = "100000",
) -> PositionSnapshot:
    mv = market_values or {}
    return PositionSnapshot(
        portfolio_id="pf-1",
        as_of_timestamp=datetime(2026, 8, 21, 15, 0, tzinfo=UTC),
        idempotency_key="pos-1",
        cash=Decimal(cash),
        holdings={s: Decimal(q) for s, q in holdings.items()},
        market_values={s: Decimal(v) for s, v in mv.items()},
        total_market_value=Decimal(sum(Decimal(v) for v in mv.values()))
        if mv
        else Decimal("0"),
    )


def _limits() -> RiskLimits:
    return RiskLimits(
        as_of_date=datetime(2026, 8, 21, 9, 0, tzinfo=UTC),
        idempotency_key="lim-1",
        max_single_position=0.10,
        max_gross_leverage=1.0,
    )


def _fill(symbol: str, qty: str, price: str, commission: str = "5") -> Fill:
    return Fill(
        fill_id=f"f-{symbol}-{qty}",
        order_id="o-1",
        strategy_id="st-1",
        symbol=symbol,
        fill_price=Decimal(price),
        filled_quantity=Decimal(qty),
        fill_timestamp=datetime(2026, 8, 21, 10, 0, tzinfo=UTC),
        idempotency_key=f"idem-f-{symbol}-{qty}",
        commission=Decimal(commission),
    )


def _input(**overrides) -> RiskSnapshotInput:
    base = dict(
        position_snapshot=_positions(
            {"600519.SH": "100", "000001.SZ": "200"},
            {"600519.SH": "170000", "000001.SZ": "3000"},
            cash="27000",
        ),
        quotes={"600519.SH": _quote("600519.SH", "1700"), "000001.SZ": _quote("000001.SZ", "15")},
        fills=(),
        limits=_limits(),
        as_of=datetime(2026, 8, 21, 15, 30, tzinfo=UTC),
    )
    base.update(overrides)
    return RiskSnapshotInput(**base)


# ── 纯函数装配 ───────────────────────────────────────────────────────


class TestAssembleRiskSnapshot:
    def test_nav_and_weights(self):
        snap = assemble_risk_snapshot(_input())
        # nav = 27000 + 170000 + 3000 = 200000
        assert snap.nav == Decimal("200000")
        assert snap.total_market_value == Decimal("173000")
        views = {p.symbol: p for p in snap.positions}
        assert views["600519.SH"].weight == pytest.approx(0.85)
        assert views["000001.SZ"].weight == pytest.approx(0.015)
        assert not snap.degraded
        assert snap.missing_price_symbols == ()

    def test_gross_leverage(self):
        snap = assemble_risk_snapshot(_input())
        assert snap.gross_leverage == pytest.approx(173000 / 200000)

    def test_missing_price_marks_degraded(self):
        quotes = {"600519.SH": _quote("600519.SH", "1700")}
        snap = assemble_risk_snapshot(_input(quotes=quotes))
        assert snap.degraded
        assert snap.missing_price_symbols == ("000001.SZ",)
        views = {p.symbol: p for p in snap.positions}
        assert views["000001.SZ"].price_available is False
        assert views["000001.SZ"].market_value is None
        assert views["000001.SZ"].weight is None
        # nav 仅按可得市价计算: 27000 + 170000
        assert snap.nav == Decimal("197000")

    def test_suspended_held_symbol_flagged(self):
        quotes = {
            "600519.SH": _quote("600519.SH", "1700", suspended=True),
            "000001.SZ": _quote("000001.SZ", "15"),
        }
        snap = assemble_risk_snapshot(_input(quotes=quotes))
        assert snap.suspended_held_symbols == ("600519.SH",)

    def test_sellable_quantities_interface_slot(self):
        snap = assemble_risk_snapshot(
            _input(sellable_quantities={"600519.SH": Decimal("60")}),
        )
        views = {p.symbol: p for p in snap.positions}
        assert views["600519.SH"].sellable_quantity == Decimal("60")
        assert views["000001.SZ"].sellable_quantity is None

    def test_nav_non_positive_raises(self):
        snap_input = _input(
            position_snapshot=_positions({}, {}, cash="0"),
            quotes={},
        )
        with pytest.raises(RiskDataPipelineError):
            assemble_risk_snapshot(snap_input)

    def test_negative_quantity_raises(self):
        snap_input = _input(
            position_snapshot=_positions({"600519.SH": "-100"}, cash="100000"),
        )
        with pytest.raises(RiskDataPipelineError):
            assemble_risk_snapshot(snap_input)

    def test_limits_none_marks_degraded(self):
        snap = assemble_risk_snapshot(_input(limits=None))
        assert snap.degraded
        assert snap.limits is None
        assert any("limits" in w for w in snap.data_warnings)

    def test_empty_portfolio_cash_only(self):
        snap = assemble_risk_snapshot(
            _input(position_snapshot=_positions({}, {}, cash="50000"), quotes={}),
        )
        assert snap.nav == Decimal("50000")
        assert snap.positions == ()
        assert snap.gross_leverage == 0.0
        assert not snap.degraded

    def test_snapshot_id_stable_when_provided(self):
        snap = assemble_risk_snapshot(_input(snapshot_id="snap-fixed"))
        assert snap.snapshot_id == "snap-fixed"

    def test_snapshot_immutable(self):
        snap = assemble_risk_snapshot(_input())
        with pytest.raises(AttributeError):
            snap.nav = Decimal("1")  # type: ignore[misc]


# ── 成交窗口聚合 ─────────────────────────────────────────────────────


class TestFillsWindowSummary:
    def test_aggregation(self):
        fills = (
            _fill("600519.SH", "100", "1700", commission="85"),
            _fill("000001.SZ", "200", "15", commission="5"),
        )
        snap = assemble_risk_snapshot(_input(fills=fills))
        summary = snap.fills_summary
        assert summary.fill_count == 2
        assert summary.total_notional == Decimal("173000")
        assert summary.total_commission == Decimal("90")
        assert summary.symbols == ("000001.SZ", "600519.SH")

    def test_empty_fills(self):
        snap = assemble_risk_snapshot(_input(fills=()))
        assert snap.fills_summary.fill_count == 0
        assert snap.fills_summary.total_notional == Decimal("0")
        assert snap.fills_summary.symbols == ()


# ── 管道编排 ─────────────────────────────────────────────────────────


class _StubPositionProvider:
    def __init__(self, snapshot: PositionSnapshot | None = None, exc: Exception | None = None):
        self._snapshot = snapshot
        self._exc = exc

    def get_position_snapshot(self) -> PositionSnapshot:
        if self._exc is not None:
            raise self._exc
        assert self._snapshot is not None
        return self._snapshot


class _StubMarketDataProvider:
    def __init__(self, quotes: dict[str, NormalizedMarketData]):
        self._quotes = quotes
        self.requested: list[tuple[str, ...]] = []

    def get_latest_quotes(self, symbols):
        symbols = tuple(symbols)
        self.requested.append(symbols)
        return {s: self._quotes[s] for s in symbols if s in self._quotes}


class _StubFillProvider:
    def __init__(self, fills=(), exc: Exception | None = None):
        self._fills = tuple(fills)
        self._exc = exc

    def get_fills_since(self, start: datetime):
        if self._exc is not None:
            raise self._exc
        return self._fills


class _StubLimitsProvider:
    def __init__(self, limits: RiskLimits | None = None, exc: Exception | None = None):
        self._limits = limits
        self._exc = exc

    def get_current_limits(self) -> RiskLimits:
        if self._exc is not None:
            raise self._exc
        assert self._limits is not None
        return self._limits


class TestRiskDataPipeline:
    def _pipeline(self, **overrides) -> RiskDataPipeline:
        kwargs = dict(
            position_provider=_StubPositionProvider(
                _positions({"600519.SH": "100"}, {"600519.SH": "170000"}, cash="30000"),
            ),
            market_data_provider=_StubMarketDataProvider({"600519.SH": _quote("600519.SH", "1700")}),
            fill_provider=_StubFillProvider(),
            limits_provider=_StubLimitsProvider(_limits()),
        )
        kwargs.update(overrides)
        return RiskDataPipeline(**kwargs)

    def test_build_snapshot_happy_path(self):
        pipe = self._pipeline()
        snap = pipe.build_snapshot(as_of=datetime(2026, 8, 21, 15, 30, tzinfo=UTC))
        assert isinstance(snap, RiskSnapshot)
        assert snap.nav == Decimal("200000")
        assert not snap.degraded

    def test_position_provider_failure_propagates_fail_closed(self):
        pipe = self._pipeline(position_provider=_StubPositionProvider(exc=RuntimeError("db down")))
        with pytest.raises(RiskDataPipelineError):
            pipe.build_snapshot()

    def test_limits_provider_failure_degrades_not_raises(self):
        pipe = self._pipeline(limits_provider=_StubLimitsProvider(exc=RuntimeError("no limits")))
        snap = pipe.build_snapshot()
        assert snap.degraded
        assert snap.limits is None

    def test_fill_provider_failure_degrades_not_raises(self):
        pipe = self._pipeline(fill_provider=_StubFillProvider(exc=RuntimeError("no fills")))
        snap = pipe.build_snapshot()
        assert snap.degraded
        assert snap.fills_summary.fill_count == 0

    def test_market_data_failure_marks_all_missing(self):
        class _FailingMarket:
            def get_latest_quotes(self, symbols):
                raise RuntimeError("quote source down")

        pipe = self._pipeline(market_data_provider=_FailingMarket())
        snap = pipe.build_snapshot()
        assert snap.degraded
        assert snap.missing_price_symbols == ("600519.SH",)
