# [A_test] module_id: MOD-GOV_l04_risk_management | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/blueprint.md | §test
# [MODULE] zephyr.risk
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l04_risk_management.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

l04 = pytest.importorskip("zephyr.risk", reason="l04-risk-management not importable")

from zephyr.risk.risk_limits import RiskLimitsCalculator
from zephyr.risk.risk_manager import RiskManagerBase
from zephyr.risk.risk_manager_base import (
    PositionLimitCheckerBase,
    RiskCheckResult,
    RiskManagerOrchestratorBase,
    RiskReport,
    StopLossEngineBase,
)
from zephyr.risk.risk_validator import (
    RiskValidator,
    ViolatedConstraint,
    ViolationDetail,
)
from zephyr.risk.stop_loss import (
    StopLossResult,
    detect_ghost_positions,
    evaluate_stop_loss,
    execute_kill_switch_liquidation,
    reset_kill_switch,
    trigger_kill_switch,
)
from zephyr.shared.contracts.risk_limits import RiskLimits


class _ConcreteRiskManager(RiskManagerBase):
    def validate_position(self, symbol, weight, limits):
        if weight > limits.max_single_position:
            from zephyr.trading.trading_contracts.risk.risk_limit_violation_error import (
                RiskLimitViolationError,
            )

            raise RiskLimitViolationError(
                error_id="err-001",
                portfolio_id="test",
                violated_constraint="position_limit",
                violation_detail="weight exceeds limit",
                limit_value=limits.max_single_position,
                actual_value=weight,
                recovery_hint="reduce position",
                idempotency_key="ik-001",
            )
        return True

    def check_portfolio(self, holdings, market_values, limits):
        violations = []
        for sym, val in holdings.items():
            total = sum(market_values.values(), Decimal("0"))
            if total > 0:
                weight = float(val / total)
                if weight > limits.max_single_position:
                    violations.append(f"{sym}: weight {weight:.2%} > limit")
        return violations

    def generate_limits(self, portfolio_id):
        return RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="ik-limits",
            max_single_position=0.10,
            max_gross_leverage=1.5,
        )


class _ConcreteRiskValidator(RiskValidator):
    __validator_id__ = "test_validator"

    def validate_order(self, symbol, target_weight, current_holdings, limits):
        max_pos = limits.get("max_single_position", 0.10) if isinstance(limits, dict) else 0.10
        if target_weight > max_pos:
            return [
                ViolationDetail(
                    constraint=ViolatedConstraint.POSITION_LIMIT,
                    description="exceeds position limit",
                    limit_value=Decimal(str(max_pos)),
                    actual_value=Decimal(str(target_weight)),
                    severity="HALT",
                )
            ]
        return []

    def validate_portfolio(self, holdings, market_values, total_nav, limits):
        return []


class _ConcreteRiskLimitsCalculator(RiskLimitsCalculator):
    __calculator_id__ = "test_calculator"

    def calculate(self, positions, market_values, total_nav, factor_signals=None):
        return RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="ik-calc",
            max_single_position=0.10,
            max_gross_leverage=1.5,
        )


class _ConcreteOrchestrator(RiskManagerOrchestratorBase):
    def pre_trade_check(self, order, limits, positions):
        return RiskCheckResult(
            check_id="chk-1",
            rule_name="position_limit",
            passed=True,
            limit_value=Decimal("0.10"),
            actual_value=Decimal("0.05"),
        )

    def post_trade_check(self, fill, positions):
        return RiskCheckResult(
            check_id="chk-2",
            rule_name="post_trade",
            passed=True,
            limit_value=Decimal("0"),
            actual_value=Decimal("0"),
        )

    def daily_pnl_check(self, daily_pnl, loss_limit):
        passed = daily_pnl >= -loss_limit
        return RiskCheckResult(
            check_id="chk-3",
            rule_name="daily_pnl",
            passed=passed,
            limit_value=loss_limit,
            actual_value=daily_pnl,
        )

    def aggregate_report(self):
        return RiskReport(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="test",
            overall_pass=True,
        )


class _ConcreteStopLossEngine(StopLossEngineBase):
    def evaluate(self, symbol, entry_price, current_price, position_qty, rules):
        stop_pct = Decimal(str(rules.get("stop_pct", 0.05)))
        triggered = current_price <= entry_price * (Decimal("1") - stop_pct)
        return RiskCheckResult(
            check_id="sl-1",
            rule_name="stop_loss",
            passed=not triggered,
            limit_value=entry_price * (Decimal("1") - stop_pct),
            actual_value=current_price,
        )

    def get_stop_price(self, symbol):
        return None


class _ConcretePositionLimitChecker(PositionLimitCheckerBase):
    def check_single_position(self, symbol, weight, limit):
        passed = weight <= limit
        return RiskCheckResult(
            check_id="plc-1",
            rule_name="single_position",
            passed=passed,
            limit_value=Decimal(str(limit)),
            actual_value=Decimal(str(weight)),
        )

    def check_sector_concentration(self, sector, weight, limit):
        passed = weight <= limit
        return RiskCheckResult(
            check_id="plc-2",
            rule_name="sector_concentration",
            passed=passed,
            limit_value=Decimal(str(limit)),
            actual_value=Decimal(str(weight)),
        )

    def check_gross_leverage(self, current_leverage, limit):
        passed = current_leverage <= limit
        return RiskCheckResult(
            check_id="plc-3",
            rule_name="gross_leverage",
            passed=passed,
            limit_value=Decimal(str(limit)),
            actual_value=Decimal(str(current_leverage)),
        )


class TestRiskCheckResult:
    def test_creation_defaults(self):
        r = RiskCheckResult(
            check_id="c1",
            rule_name="r1",
            passed=True,
            limit_value=Decimal("0.1"),
            actual_value=Decimal("0.05"),
        )
        assert r.check_id == "c1"
        assert r.passed is True
        assert r.severity == "info"

    def test_frozen_immutability(self):
        r = RiskCheckResult(
            check_id="c1",
            rule_name="r1",
            passed=True,
            limit_value=Decimal("0.1"),
            actual_value=Decimal("0.05"),
        )
        with pytest.raises(AttributeError):
            r.passed = False

    def test_custom_severity(self):
        r = RiskCheckResult(
            check_id="c1",
            rule_name="r1",
            passed=False,
            limit_value=Decimal("0.1"),
            actual_value=Decimal("0.2"),
            severity="HALT",
        )
        assert r.severity == "HALT"


class TestRiskReport:
    def test_empty_checks_no_failures(self):
        report = RiskReport(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="p1",
        )
        assert report.failed_checks == []
        assert report.overall_pass is True
        assert report.kill_switch_active is False

    def test_failed_checks_property(self):
        checks = [
            RiskCheckResult(
                check_id="1", rule_name="r", passed=True, limit_value=Decimal("0"), actual_value=Decimal("0")
            ),
            RiskCheckResult(
                check_id="2", rule_name="r", passed=False, limit_value=Decimal("0.1"), actual_value=Decimal("0.2")
            ),
        ]
        report = RiskReport(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="p1",
            checks=checks,
            overall_pass=False,
        )
        assert len(report.failed_checks) == 1
        assert report.failed_checks[0].check_id == "2"

    def test_frozen_immutability(self):
        report = RiskReport(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="p1",
        )
        with pytest.raises(AttributeError):
            report.portfolio_id = "other"


class TestViolationDetail:
    def test_creation_defaults(self):
        v = ViolationDetail(
            constraint="position_limit",
            description="exceeds",
            limit_value=Decimal("0.1"),
            actual_value=Decimal("0.2"),
        )
        assert v.severity == "HALT"

    def test_warning_severity(self):
        v = ViolationDetail(
            constraint="sector_concentration",
            description="high",
            limit_value=Decimal("0.3"),
            actual_value=Decimal("0.35"),
            severity="WARNING",
        )
        assert v.severity == "WARNING"

    def test_frozen(self):
        v = ViolationDetail(
            constraint="c",
            description="d",
            limit_value=Decimal("0"),
            actual_value=Decimal("0"),
        )
        with pytest.raises(AttributeError):
            v.constraint = "other"


class TestViolatedConstraint:
    def test_values(self):
        assert ViolatedConstraint.POSITION_LIMIT == "position_limit"
        assert ViolatedConstraint.LEVERAGE_LIMIT == "leverage_limit"
        assert ViolatedConstraint.VAR_BREACH == "var_breach"
        assert ViolatedConstraint.DRAWDOWN_TRIGGER == "drawdown_trigger"
        assert ViolatedConstraint.SECTOR_CONCENTRATION == "sector_concentration"
        assert ViolatedConstraint.CONCENTRATION_LIMIT == "concentration_limit"


class TestRiskManagerBase:
    def test_concrete_validate_position_pass(self):
        mgr = _ConcreteRiskManager()
        limits = RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="ik",
            max_single_position=0.10,
        )
        assert mgr.validate_position("AAPL", 0.05, limits) is True

    def test_concrete_validate_position_fail(self):
        mgr = _ConcreteRiskManager()
        limits = RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="ik",
            max_single_position=0.10,
        )
        from zephyr.trading.trading_contracts.risk.risk_limit_violation_error import (
            RiskLimitViolationError,
        )

        with pytest.raises(RiskLimitViolationError):
            mgr.validate_position("AAPL", 0.20, limits)

    def test_check_portfolio_no_violations(self):
        mgr = _ConcreteRiskManager()
        limits = RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="ik",
            max_single_position=0.50,
        )
        holdings = {"AAPL": Decimal("50"), "GOOG": Decimal("50")}
        market_values = {"AAPL": Decimal("50"), "GOOG": Decimal("50")}
        assert mgr.check_portfolio(holdings, market_values, limits) == []

    def test_snapshot_raises_not_implemented(self):
        mgr = _ConcreteRiskManager()
        with pytest.raises(NotImplementedError):
            mgr.snapshot("p1")

    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            RiskManagerBase()


class TestRiskValidator:
    def test_validate_order_pass(self):
        v = _ConcreteRiskValidator()
        result = v.validate_order("AAPL", 0.05, {}, {"max_single_position": 0.10})
        assert result == []

    def test_validate_order_halt(self):
        v = _ConcreteRiskValidator()
        result = v.validate_order("AAPL", 0.20, {}, {"max_single_position": 0.10})
        assert len(result) == 1
        assert result[0].severity == "HALT"

    def test_is_kill_switch_triggered_with_halt(self):
        violations = [
            ViolationDetail(
                constraint="c",
                description="d",
                limit_value=Decimal("0"),
                actual_value=Decimal("0"),
                severity="HALT",
            )
        ]
        assert RiskValidator.is_kill_switch_triggered(violations) is True

    def test_is_kill_switch_triggered_with_warning_only(self):
        violations = [
            ViolationDetail(
                constraint="c",
                description="d",
                limit_value=Decimal("0"),
                actual_value=Decimal("0"),
                severity="WARNING",
            )
        ]
        assert RiskValidator.is_kill_switch_triggered(violations) is False

    def test_is_kill_switch_triggered_empty(self):
        assert RiskValidator.is_kill_switch_triggered([]) is False

    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            RiskValidator()


class TestRiskLimitsCalculator:
    def test_calculate_returns_risk_limits(self):
        calc = _ConcreteRiskLimitsCalculator()
        limits = calc.calculate({}, {}, Decimal("1000000"))
        assert isinstance(limits, RiskLimits)
        assert limits.max_single_position == 0.10

    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            RiskLimitsCalculator()


class TestRiskManagerOrchestratorBase:
    def test_pre_trade_check_pass(self):
        o = _ConcreteOrchestrator()
        result = o.pre_trade_check(None, None, None)
        assert result.passed is True

    def test_daily_pnl_check_pass(self):
        o = _ConcreteOrchestrator()
        result = o.daily_pnl_check(Decimal("-100"), Decimal("1000"))
        assert result.passed is True

    def test_daily_pnl_check_fail(self):
        o = _ConcreteOrchestrator()
        result = o.daily_pnl_check(Decimal("-2000"), Decimal("1000"))
        assert result.passed is False

    def test_aggregate_report(self):
        o = _ConcreteOrchestrator()
        report = o.aggregate_report()
        assert isinstance(report, RiskReport)
        assert report.overall_pass is True


class TestStopLossEngineBase:
    def test_evaluate_triggered(self):
        e = _ConcreteStopLossEngine()
        result = e.evaluate("AAPL", Decimal("100"), Decimal("90"), Decimal("100"), {"stop_pct": 0.05})
        assert result.passed is False

    def test_evaluate_not_triggered(self):
        e = _ConcreteStopLossEngine()
        result = e.evaluate("AAPL", Decimal("100"), Decimal("97"), Decimal("100"), {"stop_pct": 0.05})
        assert result.passed is True

    def test_get_stop_price_none(self):
        e = _ConcreteStopLossEngine()
        assert e.get_stop_price("AAPL") is None


class TestPositionLimitCheckerBase:
    def test_single_position_pass(self):
        c = _ConcretePositionLimitChecker()
        r = c.check_single_position("AAPL", 0.05, 0.10)
        assert r.passed is True

    def test_single_position_fail(self):
        c = _ConcretePositionLimitChecker()
        r = c.check_single_position("AAPL", 0.15, 0.10)
        assert r.passed is False

    def test_sector_concentration_pass(self):
        c = _ConcretePositionLimitChecker()
        r = c.check_sector_concentration("tech", 0.25, 0.30)
        assert r.passed is True

    def test_gross_leverage_fail(self):
        c = _ConcretePositionLimitChecker()
        r = c.check_gross_leverage(2.0, 1.5)
        assert r.passed is False


class TestEvaluateStopLoss:
    def test_fixed_pct_triggered(self):
        pos = {"entry_price": 100, "qty": 100}
        assert evaluate_stop_loss(pos, 90, {"method": "fixed_pct", "stop_loss_pct": 0.05}) is True

    def test_fixed_pct_not_triggered(self):
        pos = {"entry_price": 100, "qty": 100}
        assert evaluate_stop_loss(pos, 97, {"method": "fixed_pct", "stop_loss_pct": 0.05}) is False

    def test_trailing_triggered(self):
        pos = {"entry_price": 100, "qty": 100, "highest_since_entry": 120}
        assert evaluate_stop_loss(pos, 113, {"method": "trailing", "trailing_pct": 0.05}) is True

    def test_trailing_not_triggered(self):
        pos = {"entry_price": 100, "qty": 100, "highest_since_entry": 110}
        assert evaluate_stop_loss(pos, 107, {"method": "trailing", "trailing_pct": 0.05}) is False

    def test_zero_entry_price(self):
        pos = {"entry_price": 0, "qty": 100}
        assert evaluate_stop_loss(pos, 50, {"method": "fixed_pct"}) is False

    def test_unknown_method_defaults(self):
        pos = {"entry_price": 100, "qty": 100}
        assert evaluate_stop_loss(pos, 90, {"method": "unknown_method"}) is True

    def test_time_based_triggered(self):
        from datetime import timedelta

        entry = datetime.now(UTC) - timedelta(days=30)
        pos = {"entry_price": 100, "qty": 100, "entry_date": entry}
        assert evaluate_stop_loss(pos, 100, {"method": "time_based", "max_hold_days": 20}) is True

    def test_time_based_no_entry_date(self):
        pos = {"entry_price": 100, "qty": 100}
        assert evaluate_stop_loss(pos, 100, {"method": "time_based", "max_hold_days": 20}) is False

    def test_volatility_triggered(self):
        pos = {"entry_price": 100, "qty": 100}
        assert (
            evaluate_stop_loss(pos, 94, {"method": "volatility", "current_volatility": 0.02, "vol_multiplier": 2.0})
            is True
        )

    def test_empty_position(self):
        assert evaluate_stop_loss({}, 100, {}) is False


class TestTriggerKillSwitch:
    def test_returns_dict(self):
        result = trigger_kill_switch("test reason")
        assert result["status"] == "triggered"
        assert result["reason"] == "test reason"
        assert result["requires_manual_reset"] is True

    def test_scope_all(self):
        result = trigger_kill_switch("reason", scope="all")
        assert result["scope"] == "all"

    def test_scope_symbol(self):
        result = trigger_kill_switch("reason", scope="symbol")
        assert result["scope"] == "symbol"

    def test_has_event_id(self):
        result = trigger_kill_switch("reason")
        assert "event_id" in result
        assert len(result["event_id"]) > 0


class TestResetKillSwitch:
    def test_reset_success(self):
        result = reset_kill_switch(
            {
                "confirmed_by": "admin",
                "override_reason": "verified safe",
            }
        )
        assert result is True

    def test_reset_empty_confirmation(self):
        result = reset_kill_switch({})
        assert result is True


class TestStopLossResult:
    def test_creation_defaults(self):
        r = StopLossResult(triggered=True)
        assert r.triggered is True
        assert r.reason == ""
        assert r.stop_price == Decimal("0")
        assert r.kill_switch_activated is False

    def test_full_creation(self):
        r = StopLossResult(
            triggered=True,
            reason="stop hit",
            stop_price=Decimal("95"),
            method="fixed_pct",
            kill_switch_activated=True,
        )
        assert r.method == "fixed_pct"
        assert r.kill_switch_activated is True


# ─────────────────────────────────────────────────────────────────────────────
# Kill Switch 执行链路 + Ghost Position 检测测试（§3.5.1/§6.11 施工）
# ─────────────────────────────────────────────────────────────────────────────


class _MockBroker:
    """模拟 ExecutionBroker 接口，用于测试 Kill Switch 执行链路。"""

    def __init__(self):
        self.cancelled_orders: list[str] = []
        self.placed_orders: list[dict] = []
        self.cancel_fail_orders: set[str] = set()
        self.place_fail_symbols: set[str] = set()

    def cancel_order(self, order_id: str) -> None:
        if order_id in self.cancel_fail_orders:
            raise ConnectionError(f"cancel failed: {order_id}")
        self.cancelled_orders.append(order_id)

    def place_order(self, symbol: str, direction: str, qty: float, order_type: str) -> None:
        if symbol in self.place_fail_symbols:
            raise ConnectionError(f"place failed: {symbol}")
        self.placed_orders.append({"symbol": symbol, "direction": direction, "qty": qty, "order_type": order_type})


class TestExecuteKillSwitchLiquidation:
    """§3.5.1 L1 代码层：Kill Switch 平仓/撤单执行链路测试。"""

    def test_scope_all_with_positions_and_orders(self):
        broker = _MockBroker()
        positions = {"600000.SH": 1000, "000001.SZ": 2000}
        open_orders = {"ord-001": {"symbol": "600000.SH"}, "ord-002": {"symbol": "000001.SZ"}}
        result = execute_kill_switch_liquidation(broker, positions, open_orders, scope="all")
        assert result["all_success"] is True
        assert len(result["cancelled_orders"]) == 2
        assert len(result["liquidation_orders"]) == 2
        assert len(result["cancel_errors"]) == 0
        assert len(result["liquidation_errors"]) == 0
        assert "event_id" in result
        assert result["scope"] == "all"

    def test_scope_position_only(self):
        broker = _MockBroker()
        positions = {"600000.SH": 1000}
        open_orders = {"ord-001": {"symbol": "600000.SH"}}
        result = execute_kill_switch_liquidation(broker, positions, open_orders, scope="position")
        assert result["all_success"] is True
        assert len(result["cancelled_orders"]) == 0
        assert len(result["liquidation_orders"]) == 1

    def test_scope_order_only(self):
        broker = _MockBroker()
        positions = {"600000.SH": 1000}
        open_orders = {"ord-001": {"symbol": "600000.SH"}}
        result = execute_kill_switch_liquidation(broker, positions, open_orders, scope="order")
        assert result["all_success"] is True
        assert len(result["cancelled_orders"]) == 1
        assert len(result["liquidation_orders"]) == 0

    def test_empty_positions_and_orders(self):
        broker = _MockBroker()
        result = execute_kill_switch_liquidation(broker, {}, {}, scope="all")
        assert result["all_success"] is True
        assert len(result["cancelled_orders"]) == 0
        assert len(result["liquidation_orders"]) == 0

    def test_cancel_failure_marks_not_all_success(self):
        broker = _MockBroker()
        broker.cancel_fail_orders.add("ord-bad")
        open_orders = {"ord-ok": {"symbol": "600000.SH"}, "ord-bad": {"symbol": "000001.SZ"}}
        result = execute_kill_switch_liquidation(broker, {}, open_orders, scope="order")
        assert result["all_success"] is False
        assert len(result["cancelled_orders"]) == 1
        assert len(result["cancel_errors"]) == 1
        assert result["cancel_errors"][0][0] == "ord-bad"

    def test_liquidate_failure_marks_not_all_success(self):
        broker = _MockBroker()
        broker.place_fail_symbols.add("600000.SH")
        positions = {"600000.SH": 1000, "000001.SZ": 2000}
        result = execute_kill_switch_liquidation(broker, positions, {}, scope="position")
        assert result["all_success"] is False
        assert len(result["liquidation_orders"]) == 1
        assert len(result["liquidation_errors"]) == 1
        assert result["liquidation_errors"][0][0] == "600000.SH"

    def test_short_position_direction(self):
        broker = _MockBroker()
        positions = {"600000.SH": -500}
        result = execute_kill_switch_liquidation(broker, positions, {}, scope="position")
        assert result["all_success"] is True
        assert broker.placed_orders[0]["direction"] == "BUY"
        assert broker.placed_orders[0]["qty"] == 500

    def test_long_position_direction(self):
        broker = _MockBroker()
        positions = {"600000.SH": 1000}
        result = execute_kill_switch_liquidation(broker, positions, {}, scope="position")
        assert result["all_success"] is True
        assert broker.placed_orders[0]["direction"] == "SELL"
        assert broker.placed_orders[0]["qty"] == 1000

    def test_zero_qty_positions_skipped(self):
        broker = _MockBroker()
        positions = {"600000.SH": 0, "000001.SZ": 100}
        result = execute_kill_switch_liquidation(broker, positions, {}, scope="position")
        assert result["all_success"] is True
        assert len(result["liquidation_orders"]) == 1

    def test_batching_15_per_second(self):
        broker = _MockBroker()
        # 20 个持仓，15 笔/秒限频，应分 2 批
        positions = {f"6000{i:02d}.SH": 100 for i in range(20)}
        result = execute_kill_switch_liquidation(broker, positions, {}, scope="position")
        assert result["all_success"] is True
        assert len(result["liquidation_orders"]) == 20
        # 总耗时 ≥ 1 秒（第二批等了 1 秒）
        assert result["total_time_seconds"] >= 1.0

    def test_custom_max_orders_per_second(self):
        broker = _MockBroker()
        positions = {f"6000{i:02d}.SH": 100 for i in range(10)}
        result = execute_kill_switch_liquidation(broker, positions, {}, scope="position", max_orders_per_second=5)
        assert result["all_success"] is True
        assert len(result["liquidation_orders"]) == 10
        # 10 个持仓 5 笔/秒 = 2 批，第二批等 1 秒
        assert result["total_time_seconds"] >= 1.0

    def test_none_open_orders(self):
        broker = _MockBroker()
        positions = {"600000.SH": 1000}
        result = execute_kill_switch_liquidation(broker, positions, None, scope="all")
        assert result["all_success"] is True
        assert len(result["liquidation_orders"]) == 1

    def test_invalid_scope_raises(self):
        broker = _MockBroker()
        with pytest.raises(ValueError, match="非法 scope"):
            execute_kill_switch_liquidation(broker, {}, {}, scope="invalid")

    def test_zero_max_orders_raises(self):
        broker = _MockBroker()
        with pytest.raises(ValueError, match="必须 > 0"):
            execute_kill_switch_liquidation(broker, {}, {}, max_orders_per_second=0)

    def test_negative_max_orders_raises(self):
        broker = _MockBroker()
        with pytest.raises(ValueError, match="必须 > 0"):
            execute_kill_switch_liquidation(broker, {}, {}, max_orders_per_second=-1)


class TestDetectGhostPositions:
    """§3.5.1 Ghost Position 检测测试。"""

    def test_no_ghost_when_all_match(self):
        broker_holdings = {"600000.SH": {"qty": 1000}, "000001.SZ": {"qty": 2000}}
        strategy_state = {"600000.SH": "OPEN", "000001.SZ": "OPEN"}
        ghosts = detect_ghost_positions(broker_holdings, strategy_state, "OPEN")
        assert len(ghosts) == 0

    def test_ghost_strategy_closed_but_broker_holds(self):
        broker_holdings = {"600000.SH": {"qty": 1000}}
        strategy_state = {"600000.SH": "CLOSED"}
        ghosts = detect_ghost_positions(broker_holdings, strategy_state, "OPEN")
        assert len(ghosts) == 1
        assert ghosts[0][0] == "600000.SH"
        assert ghosts[0][2] == "strategy_closed_but_broker_holds"

    def test_ghost_kill_switch_closed_but_position_remains(self):
        broker_holdings = {"600000.SH": {"qty": 1000}, "000001.SZ": {"qty": 2000}}
        strategy_state = {"600000.SH": "OPEN", "000001.SZ": "OPEN"}
        ghosts = detect_ghost_positions(broker_holdings, strategy_state, "CLOSED")
        assert len(ghosts) == 2
        types = {g[2] for g in ghosts}
        assert "kill_switch_closed_but_position_remains" in types

    def test_ghost_both_types_no_duplicate(self):
        broker_holdings = {"600000.SH": {"qty": 1000}}
        strategy_state = {"600000.SH": "CLOSED"}
        ghosts = detect_ghost_positions(broker_holdings, strategy_state, "CLOSED")
        assert len(ghosts) == 1
        assert ghosts[0][2] == "strategy_closed_but_broker_holds"

    def test_no_ghost_when_kill_switch_closed_and_no_positions(self):
        broker_holdings = {"600000.SH": {"qty": 0}}
        strategy_state = {"600000.SH": "CLOSED"}
        ghosts = detect_ghost_positions(broker_holdings, strategy_state, "CLOSED")
        assert len(ghosts) == 0

    def test_empty_broker_holdings(self):
        ghosts = detect_ghost_positions({}, {}, "CLOSED")
        assert len(ghosts) == 0

    def test_zero_qty_not_ghost(self):
        broker_holdings = {"600000.SH": {"qty": 0}}
        strategy_state = {"600000.SH": "CLOSED"}
        ghosts = detect_ghost_positions(broker_holdings, strategy_state, "OPEN")
        assert len(ghosts) == 0


class TestDefaultRiskValidatorGhostDetection:
    """DefaultRiskValidator.detect_ghost_positions 实例方法测试。"""

    def test_detect_ghost_no_active_kill_switch(self):
        from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator

        validator = DefaultRiskValidator(kill_switch_active=False)
        broker_holdings = {"600000.SH": {"qty": 1000}}
        strategy_state = {"600000.SH": "CLOSED"}
        ghosts = validator.detect_ghost_positions(broker_holdings, strategy_state)
        assert len(ghosts) == 1
        assert ghosts[0][2] == "strategy_closed_but_broker_holds"

    def test_detect_ghost_active_kill_switch(self):
        from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator

        validator = DefaultRiskValidator(kill_switch_active=True)
        broker_holdings = {"600000.SH": {"qty": 1000}, "000001.SZ": {"qty": 500}}
        strategy_state = {"600000.SH": "OPEN", "000001.SZ": "OPEN"}
        ghosts = validator.detect_ghost_positions(broker_holdings, strategy_state)
        assert len(ghosts) == 2
        types = {g[2] for g in ghosts}
        assert "kill_switch_active_but_position_remains" in types

    def test_detect_ghost_active_kill_switch_no_positions(self):
        from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator

        validator = DefaultRiskValidator(kill_switch_active=True)
        broker_holdings = {"600000.SH": {"qty": 0}}
        strategy_state = {"600000.SH": "OPEN"}
        ghosts = validator.detect_ghost_positions(broker_holdings, strategy_state)
        assert len(ghosts) == 0

    def test_detect_ghost_no_duplicate_when_both_conditions(self):
        from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator

        validator = DefaultRiskValidator(kill_switch_active=True)
        broker_holdings = {"600000.SH": {"qty": 1000}}
        strategy_state = {"600000.SH": "CLOSED"}
        ghosts = validator.detect_ghost_positions(broker_holdings, strategy_state)
        assert len(ghosts) == 1
        assert ghosts[0][2] == "strategy_closed_but_broker_holds"


class TestDefaultRiskValidatorResetWithConfirmation:
    """DefaultRiskValidator.reset_kill_switch 确认校验测试。"""

    def test_reset_with_confirmation(self):
        from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator

        validator = DefaultRiskValidator(kill_switch_active=True)
        assert validator.kill_switch_active is True
        validator.reset_kill_switch({"confirmed_by": "admin", "holdings_verified_zero": True})
        assert validator.kill_switch_active is False

    def test_reset_with_ghost_risk_warning(self):
        from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator

        validator = DefaultRiskValidator(kill_switch_active=True)
        # holdings_verified_zero=False 时仍重置，但记录告警日志
        validator.reset_kill_switch({"confirmed_by": "admin", "holdings_verified_zero": False})
        assert validator.kill_switch_active is False

    def test_reset_without_confirmation(self):
        from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator

        validator = DefaultRiskValidator(kill_switch_active=True)
        # 向后兼容：不传 confirmation 也能重置
        validator.reset_kill_switch()
        assert validator.kill_switch_active is False
