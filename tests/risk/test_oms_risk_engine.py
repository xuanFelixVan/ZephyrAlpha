# [A_test] module_id: SRC-TST-1329 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-414 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_oms_risk_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.financial_governance.oms_risk_engine import (
    AtTradeCheck,
    OMSRiskEngine,
    OrderState,
    PostTradeMetrics,
    PreTradeCheck,
    RiskLayer,
    is_terminal,
    valid_transitions,
)


class TestRiskLayer:
    def test_enum_values(self):
        assert RiskLayer.PRE_TRADE == "PRE_TRADE"
        assert RiskLayer.AT_TRADE == "AT_TRADE"
        assert RiskLayer.POST_TRADE == "POST_TRADE"


class TestOrderState:
    def test_enum_values(self):
        assert OrderState.PENDING == "PENDING"
        assert OrderState.ACK == "ACK"
        assert OrderState.FILLED == "FILLED"
        assert OrderState.REJECTED == "REJECTED"
        assert OrderState.CANCELLED == "CANCELLED"
        assert OrderState.PARTIAL_FILL == "PARTIAL_FILL"


class TestIsTerminal:
    def test_filled_is_terminal(self):
        assert is_terminal(OrderState.FILLED) is True

    def test_rejected_is_terminal(self):
        assert is_terminal(OrderState.REJECTED) is True

    def test_cancelled_is_terminal(self):
        assert is_terminal(OrderState.CANCELLED) is True

    def test_pending_is_not_terminal(self):
        assert is_terminal(OrderState.PENDING) is False

    def test_ack_is_not_terminal(self):
        assert is_terminal(OrderState.ACK) is False

    def test_partial_fill_is_not_terminal(self):
        assert is_terminal(OrderState.PARTIAL_FILL) is False


class TestValidTransitions:
    def test_pending_to_ack(self):
        assert valid_transitions(OrderState.PENDING, OrderState.ACK) is True

    def test_pending_to_rejected(self):
        assert valid_transitions(OrderState.PENDING, OrderState.REJECTED) is True

    def test_pending_to_filled_invalid(self):
        assert valid_transitions(OrderState.PENDING, OrderState.FILLED) is False

    def test_ack_to_partial_fill(self):
        assert valid_transitions(OrderState.ACK, OrderState.PARTIAL_FILL) is True

    def test_ack_to_filled(self):
        assert valid_transitions(OrderState.ACK, OrderState.FILLED) is True

    def test_ack_to_cancelled(self):
        assert valid_transitions(OrderState.ACK, OrderState.CANCELLED) is True

    def test_filled_to_any_invalid(self):
        assert valid_transitions(OrderState.FILLED, OrderState.PENDING) is False


class TestPreTradeCheck:
    def test_all_pass_true(self):
        check = PreTradeCheck()
        assert check.all_pass() is True

    def test_all_pass_false_when_position_cap_fails(self):
        check = PreTradeCheck(position_cap_ok=False)
        assert check.all_pass() is False

    def test_all_pass_false_when_risk_exposure_fails(self):
        check = PreTradeCheck(risk_exposure_ok=False)
        assert check.all_pass() is False

    def test_all_pass_false_when_funds_fails(self):
        check = PreTradeCheck(funds_sufficient_ok=False)
        assert check.all_pass() is False

    def test_all_pass_false_when_circuit_breaker_fails(self):
        check = PreTradeCheck(circuit_breaker_ok=False)
        assert check.all_pass() is False


class TestAtTradeCheck:
    def test_all_pass_default(self):
        check = AtTradeCheck()
        assert check.all_pass() is True

    def test_all_pass_false_on_deviation(self):
        check = AtTradeCheck(price_deviation_bps=6000)
        assert check.all_pass() is False

    def test_all_pass_false_on_frequency(self):
        check = AtTradeCheck(order_frequency_l1s=15)
        assert check.all_pass() is False


class TestOMSRiskEngine:
    def test_pre_trade_check_pass(self):
        engine = OMSRiskEngine()
        check = PreTradeCheck()
        result = engine.pre_trade_check(check)
        assert result.passed is True
        assert result.layer == RiskLayer.PRE_TRADE

    def test_pre_trade_check_fail(self):
        engine = OMSRiskEngine()
        check = PreTradeCheck(position_cap_ok=False)
        result = engine.pre_trade_check(check)
        assert result.passed is False
        assert "Pre-trade" in result.reason

    def test_at_trade_check_pass(self):
        engine = OMSRiskEngine()
        check = AtTradeCheck()
        result = engine.at_trade_check(check)
        assert result.passed is True
        assert result.layer == RiskLayer.AT_TRADE

    def test_at_trade_check_fail(self):
        engine = OMSRiskEngine()
        check = AtTradeCheck(price_deviation_bps=6000)
        result = engine.at_trade_check(check)
        assert result.passed is False
        assert "At-trade" in result.reason

    def test_post_trade_evaluate(self):
        engine = OMSRiskEngine()
        metrics = PostTradeMetrics(tca_slippage_bps=1.5, cumulative_slippage_bps=3.0)
        engine.post_trade_evaluate(metrics)


class TestPostTradeMetrics:
    def test_default_values(self):
        m = PostTradeMetrics()
        assert m.pnl_attribution == {}
        assert m.tca_slippage_bps == 0.0
        assert m.cumulative_slippage_bps == 0.0

    def test_custom_values(self):
        m = PostTradeMetrics(pnl_attribution={"alpha": 100.0}, tca_slippage_bps=2.5)
        assert m.pnl_attribution["alpha"] == 100.0
        assert m.tca_slippage_bps == 2.5
