# [A_test] module_id: MOD-GOV_e_confidence_estimator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_confidence_estimator
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.confidence_estimator import (
    ConfidenceEstimator,
    ConfidenceLevel,
)


class TestConfidenceLevel:
    def test_constants(self):
        assert ConfidenceLevel.HIGH == "high"
        assert ConfidenceLevel.MEDIUM == "medium"
        assert ConfidenceLevel.LOW == "low"

    def test_all_distinct(self):
        values = {ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW}
        assert len(values) == 3


class TestEvaluate:
    def test_high_score_returns_high(self):
        estimator = ConfidenceEstimator()
        result = estimator.evaluate(certainty=0.9, evidence=0.9, risk=0.1)
        assert result == ConfidenceLevel.HIGH

    def test_medium_score_returns_medium(self):
        estimator = ConfidenceEstimator()
        result = estimator.evaluate(certainty=0.5, evidence=0.5, risk=0.5)
        assert result == ConfidenceLevel.MEDIUM

    def test_low_score_returns_low(self):
        estimator = ConfidenceEstimator()
        result = estimator.evaluate(certainty=0.2, evidence=0.2, risk=0.9)
        assert result == ConfidenceLevel.LOW

    def test_boundary_exactly_0_7_returns_high(self):
        estimator = ConfidenceEstimator()
        result = estimator.evaluate(certainty=0.5, evidence=1.0, risk=0.4)
        assert result == ConfidenceLevel.HIGH

    def test_boundary_exactly_0_4_returns_medium(self):
        estimator = ConfidenceEstimator()
        result = estimator.evaluate(certainty=1.0, evidence=0.0, risk=1.0)
        assert result == ConfidenceLevel.MEDIUM

    def test_boundary_below_0_4_returns_low(self):
        estimator = ConfidenceEstimator()
        result = estimator.evaluate(certainty=0.999, evidence=0.0, risk=1.0)
        assert result == ConfidenceLevel.LOW

    def test_extreme_all_one_returns_high(self):
        estimator = ConfidenceEstimator()
        result = estimator.evaluate(certainty=1.0, evidence=1.0, risk=1.0)
        assert result == ConfidenceLevel.HIGH

    def test_extreme_all_zero_returns_low(self):
        estimator = ConfidenceEstimator()
        result = estimator.evaluate(certainty=0.0, evidence=0.0, risk=0.0)
        assert result == ConfidenceLevel.LOW

    def test_formula_consistency(self):
        estimator = ConfidenceEstimator()
        c, e, r = 0.6, 0.8, 0.3
        result = estimator.evaluate(certainty=c, evidence=e, risk=r)
        expected_score = c * 0.4 + e * 0.35 + (1.0 - r) * 0.25
        if expected_score >= 0.7:
            assert result == ConfidenceLevel.HIGH
        elif expected_score >= 0.4:
            assert result == ConfidenceLevel.MEDIUM
        else:
            assert result == ConfidenceLevel.LOW


class TestShouldAutoExecute:
    def test_high_and_low_risk_returns_true(self):
        estimator = ConfidenceEstimator()
        result = estimator.should_auto_execute(certainty=0.9, evidence=0.9, risk=0.1)
        assert result is True

    def test_high_and_high_risk_returns_false(self):
        estimator = ConfidenceEstimator()
        result = estimator.should_auto_execute(certainty=0.9, evidence=0.9, risk=0.3)
        assert result is False

    def test_medium_and_low_risk_returns_false(self):
        estimator = ConfidenceEstimator()
        result = estimator.should_auto_execute(certainty=0.5, evidence=0.5, risk=0.2)
        assert result is False

    def test_low_returns_false(self):
        estimator = ConfidenceEstimator()
        result = estimator.should_auto_execute(certainty=0.0, evidence=0.0, risk=0.0)
        assert result is False

    def test_risk_boundary_below_0_3_with_high_returns_true(self):
        estimator = ConfidenceEstimator()
        result = estimator.should_auto_execute(certainty=0.9, evidence=0.9, risk=0.299)
        assert result is True
