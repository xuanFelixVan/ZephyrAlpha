# [A_test] module_id: MOD-GOV_confidence_estimator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_confidence_estimator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_confidence_estimator.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.confidence_estimator import ConfidenceEstimator, ConfidenceLevel


class TestConfidenceLevel:
    def test_high_value(self):
        assert ConfidenceLevel.HIGH == "high"

    def test_medium_value(self):
        assert ConfidenceLevel.MEDIUM == "medium"

    def test_low_value(self):
        assert ConfidenceLevel.LOW == "low"


class TestConfidenceEstimatorInstantiation:
    def test_create_instance(self):
        est = ConfidenceEstimator()
        assert est is not None

    def test_has_evaluate_method(self):
        est = ConfidenceEstimator()
        assert callable(getattr(est, "evaluate", None))

    def test_has_should_auto_execute_method(self):
        est = ConfidenceEstimator()
        assert callable(getattr(est, "should_auto_execute", None))


class TestEvaluate:
    def test_high_confidence(self):
        est = ConfidenceEstimator()
        result = est.evaluate(certainty=1.0, evidence=1.0, risk=0.0)
        assert result == ConfidenceLevel.HIGH

    def test_medium_confidence(self):
        est = ConfidenceEstimator()
        result = est.evaluate(certainty=0.5, evidence=0.5, risk=0.5)
        assert result == ConfidenceLevel.MEDIUM

    def test_low_confidence(self):
        est = ConfidenceEstimator()
        result = est.evaluate(certainty=0.0, evidence=0.0, risk=1.0)
        assert result == ConfidenceLevel.LOW

    def test_score_formula_certainty_weight(self):
        est = ConfidenceEstimator()
        result_high_certainty = est.evaluate(certainty=1.0, evidence=0.0, risk=0.0)
        assert result_high_certainty == ConfidenceLevel.MEDIUM

    def test_boundary_score_exactly_0_7(self):
        est = ConfidenceEstimator()
        score = 0.7 * 0.4 + 0.7 * 0.35 + (1.0 - 0.7) * 0.25
        result = est.evaluate(certainty=0.7, evidence=0.7, risk=0.3)
        assert result == ConfidenceLevel.HIGH

    def test_boundary_score_just_below_0_7(self):
        est = ConfidenceEstimator()
        result = est.evaluate(certainty=0.69, evidence=0.69, risk=0.31)
        assert result == ConfidenceLevel.MEDIUM

    def test_boundary_score_exactly_0_4(self):
        est = ConfidenceEstimator()
        result = est.evaluate(certainty=0.4, evidence=0.4, risk=0.6)
        assert result == ConfidenceLevel.MEDIUM

    def test_boundary_score_just_below_0_4(self):
        est = ConfidenceEstimator()
        result = est.evaluate(certainty=0.39, evidence=0.39, risk=0.61)
        assert result == ConfidenceLevel.LOW

    def test_all_zeros(self):
        est = ConfidenceEstimator()
        result = est.evaluate(certainty=0.0, evidence=0.0, risk=0.0)
        assert result == ConfidenceLevel.LOW

    def test_all_ones(self):
        est = ConfidenceEstimator()
        result = est.evaluate(certainty=1.0, evidence=1.0, risk=1.0)
        assert result == ConfidenceLevel.HIGH

    def test_risk_dominates(self):
        est = ConfidenceEstimator()
        result = est.evaluate(certainty=0.3, evidence=0.3, risk=0.99)
        assert result == ConfidenceLevel.LOW


class TestShouldAutoExecute:
    def test_auto_execute_when_high_and_low_risk(self):
        est = ConfidenceEstimator()
        assert est.should_auto_execute(certainty=1.0, evidence=1.0, risk=0.1) is True

    def test_no_auto_execute_when_medium(self):
        est = ConfidenceEstimator()
        assert est.should_auto_execute(certainty=0.5, evidence=0.5, risk=0.1) is False

    def test_no_auto_execute_when_high_risk(self):
        est = ConfidenceEstimator()
        assert est.should_auto_execute(certainty=1.0, evidence=1.0, risk=0.5) is False

    def test_boundary_risk_exactly_0_3(self):
        est = ConfidenceEstimator()
        assert est.should_auto_execute(certainty=1.0, evidence=1.0, risk=0.3) is False

    def test_boundary_risk_just_below_0_3(self):
        est = ConfidenceEstimator()
        assert est.should_auto_execute(certainty=1.0, evidence=1.0, risk=0.29) is True

    def test_no_auto_execute_low_confidence(self):
        est = ConfidenceEstimator()
        assert est.should_auto_execute(certainty=0.0, evidence=0.0, risk=0.0) is False
