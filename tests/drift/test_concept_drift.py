# [A_test] module_id: SRC-TST-0559 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_concept_drift
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_concept_drift.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.detectors.drift.concept_drift import ConceptDrift


class TestConceptDriftInstantiation:
    def test_default_construction(self):
        cd = ConceptDrift()
        assert cd.drift_detected is False

    def test_custom_drift_detected(self):
        cd = ConceptDrift(drift_detected=True)
        assert cd.drift_detected is True


class TestCheck:
    def test_returns_float(self):
        cd = ConceptDrift()
        result = cd.check([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert isinstance(result, float)

    def test_returns_zero(self):
        cd = ConceptDrift()
        result = cd.check([1.0, 2.0], [3.0, 4.0])
        assert result == 0.0

    def test_empty_distributions(self):
        cd = ConceptDrift()
        result = cd.check([], [])
        assert result == 0.0

    def test_single_value_distributions(self):
        cd = ConceptDrift()
        result = cd.check([1.0], [2.0])
        assert result == 0.0

    def test_does_not_modify_drift_detected(self):
        cd = ConceptDrift()
        cd.check([1.0, 2.0], [10.0, 20.0])
        assert cd.drift_detected is False

    def test_drift_detected_attribute_mutable(self):
        cd = ConceptDrift()
        cd.drift_detected = True
        assert cd.drift_detected is True
