# [A_test] module_id: MOD-GOV_meta_confidence | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_meta_confidence
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_meta_confidence.py -q
# [TTL] task_bound

from zephyr.governance.intelligence_governance.meta_confidence import MetaConfidence


class TestMetaConfidenceInstantiation:
    def test_creates_instance_with_empty_history(self):
        mc = MetaConfidence()
        assert isinstance(mc, MetaConfidence)
        assert mc.history == []


class TestSelfAssess:
    def test_returns_weighted_combination(self):
        mc = MetaConfidence()
        result = mc.self_assess(confidence=1.0, evidence_count=5, domain_familiarity=1.0)
        expected = 1.0 * 0.5 + min(1.0, 5.0 / 5.0) * 0.3 + 1.0 * 0.2
        assert abs(result - expected) < 1e-9

    def test_zero_confidence(self):
        mc = MetaConfidence()
        result = mc.self_assess(confidence=0.0, evidence_count=5, domain_familiarity=1.0)
        expected = 0.0 * 0.5 + 1.0 * 0.3 + 1.0 * 0.2
        assert abs(result - expected) < 1e-9

    def test_zero_evidence(self):
        mc = MetaConfidence()
        result = mc.self_assess(confidence=1.0, evidence_count=0, domain_familiarity=1.0)
        expected = 1.0 * 0.5 + 0.0 * 0.3 + 1.0 * 0.2
        assert abs(result - expected) < 1e-9

    def test_zero_domain_familiarity(self):
        mc = MetaConfidence()
        result = mc.self_assess(confidence=1.0, evidence_count=5, domain_familiarity=0.0)
        expected = 1.0 * 0.5 + 1.0 * 0.3 + 0.0 * 0.2
        assert abs(result - expected) < 1e-9

    def test_evidence_score_capped_at_one(self):
        mc = MetaConfidence()
        result_high = mc.self_assess(confidence=0.5, evidence_count=100, domain_familiarity=0.5)
        result_cap = mc.self_assess(confidence=0.5, evidence_count=5, domain_familiarity=0.5)
        assert abs(result_high - result_cap) < 1e-9

    def test_all_zeros(self):
        mc = MetaConfidence()
        result = mc.self_assess(confidence=0.0, evidence_count=0, domain_familiarity=0.0)
        assert result == 0.0


class TestCalibrate:
    def test_calibrate_appends_to_history(self):
        mc = MetaConfidence()
        mc.calibrate(0.8, True)
        assert len(mc.history) == 1

    def test_calibrate_stores_prediction_and_correctness(self):
        mc = MetaConfidence()
        mc.calibrate(0.7, False)
        entry = mc.history[0]
        assert entry[0] == 0.7
        assert entry[2] is False

    def test_multiple_calibrations(self):
        mc = MetaConfidence()
        mc.calibrate(0.9, True)
        mc.calibrate(0.6, False)
        mc.calibrate(0.8, True)
        assert len(mc.history) == 3


class TestCalibrationError:
    def test_calibration_error_empty_history(self):
        mc = MetaConfidence()
        assert mc.calibration_error() == 0.0

    def test_perfect_calibration(self):
        mc = MetaConfidence()
        mc.calibrate(1.0, True)
        mc.calibrate(0.0, False)
        assert mc.calibration_error() == 0.0

    def test_worst_calibration(self):
        mc = MetaConfidence()
        mc.calibrate(0.0, True)
        mc.calibrate(1.0, False)
        assert mc.calibration_error() == 1.0

    def test_partial_calibration_error(self):
        mc = MetaConfidence()
        mc.calibrate(0.8, True)
        mc.calibrate(0.3, False)
        error = mc.calibration_error()
        expected = (abs(0.8 - 1.0) + abs(0.3 - 0.0)) / 2.0
        assert abs(error - expected) < 1e-9


class TestBoundary:
    def test_self_assess_with_negative_confidence(self):
        mc = MetaConfidence()
        result = mc.self_assess(confidence=-0.5, evidence_count=3, domain_familiarity=0.5)
        expected = -0.5 * 0.5 + min(1.0, 3.0 / 5.0) * 0.3 + 0.5 * 0.2
        assert abs(result - expected) < 1e-9

    def test_self_assess_with_confidence_above_one(self):
        mc = MetaConfidence()
        result = mc.self_assess(confidence=2.0, evidence_count=3, domain_familiarity=0.5)
        expected = 2.0 * 0.5 + min(1.0, 3.0 / 5.0) * 0.3 + 0.5 * 0.2
        assert abs(result - expected) < 1e-9

    def test_large_evidence_count(self):
        mc = MetaConfidence()
        result = mc.self_assess(confidence=0.5, evidence_count=999999, domain_familiarity=0.5)
        result_cap = mc.self_assess(confidence=0.5, evidence_count=5, domain_familiarity=0.5)
        assert abs(result - result_cap) < 1e-9
