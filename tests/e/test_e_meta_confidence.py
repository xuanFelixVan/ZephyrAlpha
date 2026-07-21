# [A_test] module_id: MOD-GOV_e_meta_confidence | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_meta_confidence
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

import pytest

from zephyr.governance.intelligence_governance.meta_confidence import MetaConfidence


class TestMetaConfidenceInit:
    def test_empty_history(self):
        mc = MetaConfidence()
        assert mc._history == []


class TestSelfAssess:
    def test_full_confidence(self):
        mc = MetaConfidence()
        score = mc.self_assess(1.0, 5, 1.0)
        assert pytest.approx(score) == 1.0

    def test_partial_confidence(self):
        mc = MetaConfidence()
        score = mc.self_assess(0.5, 3, 0.5)
        expected = 0.5 * 0.5 + min(1.0, 3 / 5.0) * 0.3 + 0.5 * 0.2
        assert pytest.approx(score) == expected

    def test_evidence_capped(self):
        mc = MetaConfidence()
        score = mc.self_assess(0.5, 10, 1.0)
        ev_score = min(1.0, 10 / 5.0)
        assert ev_score == 1.0

    def test_zero_inputs(self):
        mc = MetaConfidence()
        score = mc.self_assess(0.0, 0, 0.0)
        assert pytest.approx(score) == 0.0


class TestCalibrate:
    def test_adds_to_history(self):
        mc = MetaConfidence()
        mc.calibrate(0.8, True)
        assert len(mc._history) == 1

    def test_multiple_calibrations(self):
        mc = MetaConfidence()
        mc.calibrate(0.9, True)
        mc.calibrate(0.3, False)
        assert len(mc._history) == 2


class TestCalibrationError:
    def test_empty_history_zero(self):
        mc = MetaConfidence()
        assert mc.calibration_error() == 0.0

    def test_perfect_prediction_zero_error(self):
        mc = MetaConfidence()
        mc.calibrate(1.0, True)
        mc.calibrate(0.0, False)
        assert mc.calibration_error() == 0.0

    def test_wrong_predictions(self):
        mc = MetaConfidence()
        mc.calibrate(0.0, True)
        mc.calibrate(1.0, False)
        assert mc.calibration_error() == 1.0
