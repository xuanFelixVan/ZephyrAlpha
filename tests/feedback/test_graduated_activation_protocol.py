# [A_test] module_id: SRC-TST-1079 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_graduated_activation_protocol
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.graduated_activation_protocol
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_graduated_activation_protocol.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.graduated_activation_protocol import (
    GraduatedActivationProtocol,
)


class TestGraduatedActivationProtocolInstantiation:
    def test_default_instantiation(self):
        obj = GraduatedActivationProtocol()
        assert obj is not None
        assert obj.rules == {}

    def test_custom_thresholds(self):
        obj = GraduatedActivationProtocol(
            canary_success_threshold=0.99,
            beta_success_threshold=0.95,
            min_samples_per_stage=50,
        )
        assert obj.canary_success_threshold == pytest.approx(0.99)
        assert obj.min_samples_per_stage == 50

    def test_is_dataclass(self):
        obj = GraduatedActivationProtocol()
        assert hasattr(obj, "__dataclass_fields__")


class TestGraduatedActivationProtocolRegisterRule:
    def test_register_new_rule(self):
        gap = GraduatedActivationProtocol()
        result = gap.register_rule(rule_id="rule_1")
        assert result["rule_id"] == "rule_1"
        assert result["stage"] == "CANARY"
        assert "rule_1" in gap.rules

    def test_register_multiple_rules(self):
        gap = GraduatedActivationProtocol()
        gap.register_rule(rule_id="r1")
        gap.register_rule(rule_id="r2")
        assert len(gap.rules) == 2

    def test_register_rule_returns_monitor_action(self):
        gap = GraduatedActivationProtocol()
        result = gap.register_rule(rule_id="r1")
        assert result["action"] == "monitor_canary_only"


class TestGraduatedActivationProtocolRecordOutcome:
    def test_record_success(self):
        gap = GraduatedActivationProtocol()
        gap.register_rule(rule_id="r1")
        gap.record_outcome(rule_id="r1", success=True)
        assert gap.rules["r1"]["success_count"] == 1
        assert gap.rules["r1"]["total_applications"] == 1

    def test_record_failure(self):
        gap = GraduatedActivationProtocol()
        gap.register_rule(rule_id="r1")
        gap.record_outcome(rule_id="r1", success=False)
        assert gap.rules["r1"]["failure_count"] == 1

    def test_record_unknown_rule(self):
        gap = GraduatedActivationProtocol()
        gap.record_outcome(rule_id="nonexistent", success=True)
        assert len(gap.rules) == 0


class TestGraduatedActivationProtocolEvaluatePromotion:
    def test_evaluate_unknown_rule(self):
        gap = GraduatedActivationProtocol()
        result = gap.evaluate_promotion(rule_id="nonexistent")
        assert result["decision"] == "HOLD"
        assert result["reason"] == "unknown_rule"

    def test_evaluate_insufficient_samples(self):
        gap = GraduatedActivationProtocol(min_samples_per_stage=100)
        gap.register_rule(rule_id="r1")
        for _ in range(50):
            gap.record_outcome(rule_id="r1", success=True)
        result = gap.evaluate_promotion(rule_id="r1")
        assert result["decision"] == "HOLD"
        assert "insufficient_samples" in result["reason"]


class TestGraduatedActivationProtocolGetters:
    def test_get_active_canary_rules(self):
        gap = GraduatedActivationProtocol()
        gap.register_rule(rule_id="r1")
        gap.register_rule(rule_id="r2")
        canary = gap.get_active_canary_rules()
        assert "r1" in canary
        assert "r2" in canary

    def test_get_stable_rules_empty(self):
        gap = GraduatedActivationProtocol()
        gap.register_rule(rule_id="r1")
        assert gap.get_stable_rules() == []

    def test_get_rollback_count(self):
        gap = GraduatedActivationProtocol()
        assert gap.get_rollback_count() == 0


class TestGraduatedActivationProtocolBoundaries:
    def test_empty_rules_getters(self):
        gap = GraduatedActivationProtocol()
        assert gap.get_active_canary_rules() == []
        assert gap.get_stable_rules() == []
        assert gap.get_rollback_count() == 0

    def test_many_outcomes(self):
        gap = GraduatedActivationProtocol(min_samples_per_stage=10)
        gap.register_rule(rule_id="r1")
        for _ in range(200):
            gap.record_outcome(rule_id="r1", success=True)
        assert gap.rules["r1"]["success_count"] == 200
