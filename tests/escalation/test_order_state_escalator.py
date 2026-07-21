# [A_test] module_id: MOD-GOV_order_state_escalator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_order_state_escalator
# [INVARIANTS] 订单状态机升级不可跳过;超时必须触发升级
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_order_state_escalator.py
# [TTL] task_bound

from zephyr.governance.escalation.order_state_escalator import OrderStateEscalator


class TestOrderStateEscalatorInit:
    def test_instantiation(self):
        ose = OrderStateEscalator()
        assert "pending" in ose.VALID_TRANSITIONS
        assert "submitted" in ose.VALID_TRANSITIONS
        assert "partial" in ose.VALID_TRANSITIONS

    def test_valid_transitions_structure(self):
        ose = OrderStateEscalator()
        assert ose.VALID_TRANSITIONS["pending"] == ["submitted", "cancelled"]
        assert ose.VALID_TRANSITIONS["submitted"] == ["filled", "partial", "rejected"]
        assert ose.VALID_TRANSITIONS["partial"] == ["filled", "cancelled"]


class TestValidateTransition:
    def test_pending_to_submitted(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("pending", "submitted") is True

    def test_pending_to_cancelled(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("pending", "cancelled") is True

    def test_pending_to_filled_invalid(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("pending", "filled") is False

    def test_submitted_to_filled(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("submitted", "filled") is True

    def test_submitted_to_partial(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("submitted", "partial") is True

    def test_submitted_to_rejected(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("submitted", "rejected") is True

    def test_submitted_to_pending_invalid(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("submitted", "pending") is False

    def test_partial_to_filled(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("partial", "filled") is True

    def test_partial_to_cancelled(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("partial", "cancelled") is True

    def test_partial_to_submitted_invalid(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("partial", "submitted") is False

    def test_terminal_state_no_transitions(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("filled", "pending") is False
        assert ose.validate_transition("cancelled", "pending") is False
        assert ose.validate_transition("rejected", "pending") is False

    def test_unknown_from_state(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("unknown_state", "pending") is False

    def test_unknown_to_state(self):
        ose = OrderStateEscalator()
        assert ose.validate_transition("pending", "unknown_state") is False


class TestEscalateIfSuspicious:
    def test_pending_over_threshold(self):
        ose = OrderStateEscalator()
        assert ose.escalate_if_suspicious("pending", 60.0, threshold_s=30.0) is True

    def test_pending_at_threshold(self):
        ose = OrderStateEscalator()
        assert ose.escalate_if_suspicious("pending", 30.0, threshold_s=30.0) is False

    def test_pending_below_threshold(self):
        ose = OrderStateEscalator()
        assert ose.escalate_if_suspicious("pending", 10.0, threshold_s=30.0) is False

    def test_non_pending_over_threshold(self):
        ose = OrderStateEscalator()
        assert ose.escalate_if_suspicious("submitted", 60.0, threshold_s=30.0) is False

    def test_filled_over_threshold(self):
        ose = OrderStateEscalator()
        assert ose.escalate_if_suspicious("filled", 999.0, threshold_s=30.0) is False

    def test_default_threshold(self):
        ose = OrderStateEscalator()
        assert ose.escalate_if_suspicious("pending", 31.0) is True
        assert ose.escalate_if_suspicious("pending", 29.0) is False

    def test_zero_duration(self):
        ose = OrderStateEscalator()
        assert ose.escalate_if_suspicious("pending", 0.0) is False

    def test_negative_duration(self):
        ose = OrderStateEscalator()
        assert ose.escalate_if_suspicious("pending", -10.0) is False

    def test_custom_threshold_zero(self):
        ose = OrderStateEscalator()
        assert ose.escalate_if_suspicious("pending", 0.1, threshold_s=0.0) is True
