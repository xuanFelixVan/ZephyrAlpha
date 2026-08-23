# [BLUEPRINT] MOD-EX-024 | docs/03_modules/MOD-EX-024/ | §test
# [MODULE] tests.ex_core.test_pre_execution_checker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.pre_execution_checker
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_pre_execution_checker.py
# [A_test] module_id: MOD-EX-024 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-EX-024 单元测试: PreExecutionChecker — 执行前检查器。

覆盖: 熔断闸门/交易时段闸门(L-003)/快照装配/否决引擎四级检查,
各环节 fail-closed 降级(探针异常按熔断处理/时段异常按非交易时段/
快照失败拒单), 短路语义(熔断激活不建快照), 报告契约。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.ex_core.pre_execution_checker",
    reason="pre_execution_checker not importable",
)

from zephyr.ex_core.pre_execution_checker import (  # noqa: E402
    PreExecutionChecker,
    is_ashare_trading_window,
)
from zephyr.risk.core.risk_data_pipeline import (  # noqa: E402
    RiskDataPipelineError,
    RiskSnapshotInput,
    assemble_risk_snapshot,
)
from zephyr.risk.core.risk_veto_engine import OrderRiskRequest  # noqa: E402
from zephyr.shared.contracts.enums.order_enums import OrderSide  # noqa: E402
from zephyr.shared.contracts.market_data import NormalizedMarketData  # noqa: E402
from zephyr.shared.contracts.position import PositionSnapshot  # noqa: E402
from zephyr.shared.contracts.risk_limits import RiskLimits  # noqa: E402

_NOW = datetime(2026, 8, 21, 10, 0, tzinfo=UTC)  # 周五 10:00 UTC? → 见窗口测试注释

# ── 夹具 ─────────────────────────────────────────────────────────────


def _clean_snapshot():
    pos = PositionSnapshot(
        portfolio_id="pf-1",
        as_of_timestamp=_NOW,
        idempotency_key="pos-1",
        cash=Decimal("100000"),
        holdings={"600519.SH": Decimal("10")},
        market_values={},
        total_market_value=Decimal("0"),
    )
    quote = NormalizedMarketData(
        symbol="600519.SH", timestamp=_NOW,
        open=Decimal("1700"), high=Decimal("1700"),
        low=Decimal("1700"), close=Decimal("1700"),
        volume=Decimal("1000"), data_source="stub", idempotency_key="q-1",
    )
    limits = RiskLimits(
        as_of_date=_NOW, idempotency_key="lim-1",
        max_single_position=0.50, max_gross_leverage=1.0,
    )
    return assemble_risk_snapshot(
        RiskSnapshotInput(
            position_snapshot=pos, quotes={"600519.SH": quote},
            fills=(), limits=limits, as_of=_NOW,
        )
    )


def _request(quantity: str = "1", side: OrderSide = OrderSide.BUY) -> OrderRiskRequest:
    return OrderRiskRequest(
        symbol="600519.SH", side=side, quantity=Decimal(quantity),
        price=Decimal("1700"), strategy_id="st-1",
    )


class _StubSnapshotBuilder:
    """snapshot_builder 协议桩：计数 + 可配置异常。"""

    def __init__(self, snapshot=None, exc: Exception | None = None):
        self._snapshot = snapshot
        self._exc = exc
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self._exc is not None:
            raise self._exc
        return self._snapshot


def _checker(**overrides) -> tuple[PreExecutionChecker, _StubSnapshotBuilder]:
    builder = overrides.pop("snapshot_builder", _StubSnapshotBuilder(_clean_snapshot()))
    kwargs = dict(
        snapshot_builder=builder,
        kill_switch_probe=lambda: False,
        session_window_probe=lambda now: True,
    )
    kwargs.update(overrides)
    return PreExecutionChecker(**kwargs), builder


# ── 放行路径 ─────────────────────────────────────────────────────────


class TestAllowPath:
    def test_clean_buy_allowed(self):
        checker, _ = _checker()
        report = checker.check(_request())
        assert report.allowed
        assert report.blocks == ()

    def test_report_carries_ids(self):
        checker, _ = _checker()
        req = _request()
        report = checker.check(req)
        assert report.request_id == req.request_id
        assert report.snapshot_id is not None

    def test_report_immutable(self):
        checker, _ = _checker()
        report = checker.check(_request())
        with pytest.raises(AttributeError):
            report.allowed = False  # type: ignore[misc]


# ── 熔断闸门 ─────────────────────────────────────────────────────────


class TestKillSwitchGate:
    def test_kill_switch_active_blocks_all(self):
        checker, builder = _checker(kill_switch_probe=lambda: True)
        report = checker.check(_request())
        assert not report.allowed
        codes = [b.reason_code for b in report.blocks]
        assert "KILL_SWITCH_ACTIVE" in codes
        assert builder.calls == 0  # 短路: 熔断激活不建快照

    def test_kill_switch_probe_error_fail_closed(self):
        def _boom():
            raise RuntimeError("state store down")

        checker, _ = _checker(kill_switch_probe=_boom)
        report = checker.check(_request())
        assert not report.allowed
        codes = [b.reason_code for b in report.blocks]
        assert "KILL_SWITCH_PROBE_ERROR" in codes


# ── 交易时段闸门 (L-003) ─────────────────────────────────────────────


class TestSessionWindowGate:
    def test_outside_window_blocked(self):
        checker, _ = _checker(session_window_probe=lambda now: False)
        report = checker.check(_request())
        assert not report.allowed
        codes = [b.reason_code for b in report.blocks]
        assert "OUTSIDE_TRADING_WINDOW" in codes

    def test_window_probe_error_fail_closed(self):
        def _boom(now):
            raise RuntimeError("calendar down")

        checker, _ = _checker(session_window_probe=_boom)
        report = checker.check(_request())
        assert not report.allowed
        codes = [b.reason_code for b in report.blocks]
        assert "SESSION_WINDOW_PROBE_ERROR" in codes


# ── 快照与否决 ───────────────────────────────────────────────────────


class TestSnapshotAndVeto:
    def test_snapshot_failure_blocks(self):
        builder = _StubSnapshotBuilder(
            exc=RiskDataPipelineError("持仓真源不可用", details={}),
        )
        checker, _ = _checker(snapshot_builder=builder)
        report = checker.check(_request())
        assert not report.allowed
        codes = [b.reason_code for b in report.blocks]
        assert "SNAPSHOT_UNAVAILABLE" in codes
        assert report.snapshot_id is None

    def test_veto_blocks_mapped(self):
        # 超限买入 → 否决引擎产出 SINGLE_POSITION_LIMIT
        pos = PositionSnapshot(
            portfolio_id="pf-1", as_of_timestamp=_NOW, idempotency_key="pos-1",
            cash=Decimal("10000"), holdings={"600519.SH": Decimal("100")},
            market_values={}, total_market_value=Decimal("0"),
        )
        quote = NormalizedMarketData(
            symbol="600519.SH", timestamp=_NOW,
            open=Decimal("1700"), high=Decimal("1700"),
            low=Decimal("1700"), close=Decimal("1700"),
            volume=Decimal("1000"), data_source="stub", idempotency_key="q-1",
        )
        limits = RiskLimits(
            as_of_date=_NOW, idempotency_key="lim-1",
            max_single_position=0.10, max_gross_leverage=1.0,
        )
        snap = assemble_risk_snapshot(
            RiskSnapshotInput(
                position_snapshot=pos, quotes={"600519.SH": quote},
                fills=(), limits=limits, as_of=_NOW,
            )
        )
        checker, _ = _checker(snapshot_builder=_StubSnapshotBuilder(snap))
        report = checker.check(_request(quantity="10"))
        assert not report.allowed
        codes = [b.reason_code for b in report.blocks]
        assert "SINGLE_POSITION_LIMIT" in codes
        assert report.veto_decision is not None


# ── A 股交易时段默认实现 ─────────────────────────────────────────────


class TestAshareTradingWindow:
    def test_morning_session(self):
        # 2026-08-21 是周五; 10:00 北京时间在 09:30-11:30 窗口内
        assert is_ashare_trading_window(datetime(2026, 8, 21, 10, 0)) is True

    def test_lunch_break_closed(self):
        assert is_ashare_trading_window(datetime(2026, 8, 21, 12, 0)) is False

    def test_afternoon_session(self):
        assert is_ashare_trading_window(datetime(2026, 8, 21, 14, 0)) is True

    def test_before_open(self):
        assert is_ashare_trading_window(datetime(2026, 8, 21, 9, 0)) is False

    def test_after_close(self):
        assert is_ashare_trading_window(datetime(2026, 8, 21, 15, 30)) is False

    def test_weekend_closed(self):
        # 2026-08-22 周六
        assert is_ashare_trading_window(datetime(2026, 8, 22, 10, 0)) is False
