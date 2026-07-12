# [A_test] module_id: SRC-TST-0263 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_action_efficacy_decay_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_action_efficacy_decay_detector.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.detectors.action_efficacy_decay_detector import (
    ActionEfficacyDecayDetector,
    ActionEfficacyRecord,
)


class TestActionEfficacyRecord:
    def test_default_construction(self):
        rec = ActionEfficacyRecord(action_type="repair")
        assert rec.action_type == "repair"
        assert rec.outcomes == []
        assert rec.max_outcomes == 50

    def test_custom_max_outcomes(self):
        rec = ActionEfficacyRecord(action_type="restart", max_outcomes=10)
        assert rec.max_outcomes == 10

    def test_outcomes_list_independent(self):
        rec_a = ActionEfficacyRecord(action_type="a")
        rec_b = ActionEfficacyRecord(action_type="b")
        rec_a.outcomes.append(1.0)
        assert rec_b.outcomes == []


class TestActionEfficacyDecayDetectorInstantiation:
    def test_default_construction(self):
        det = ActionEfficacyDecayDetector()
        assert det.records == {}
        assert det.decay_threshold == -0.02
        assert det.min_samples == 10

    def test_custom_params(self):
        det = ActionEfficacyDecayDetector(decay_threshold=-0.05, min_samples=5)
        assert det.decay_threshold == -0.05
        assert det.min_samples == 5


class TestRecordOutcome:
    def test_creates_new_record(self):
        det = ActionEfficacyDecayDetector()
        det.record_outcome("repair", True)
        assert "repair" in det.records
        assert det.records["repair"].outcomes == [1.0]

    def test_appends_to_existing(self):
        det = ActionEfficacyDecayDetector()
        det.record_outcome("repair", True)
        det.record_outcome("repair", False)
        assert det.records["repair"].outcomes == [1.0, 0.0]

    def test_truncates_at_max_outcomes(self):
        det = ActionEfficacyDecayDetector()
        for i in range(55):
            det.record_outcome("repair", i % 2 == 0)
        assert len(det.records["repair"].outcomes) == 50

    def test_multiple_action_types(self):
        det = ActionEfficacyDecayDetector()
        det.record_outcome("repair", True)
        det.record_outcome("restart", False)
        assert len(det.records) == 2


class TestDetectDecay:
    def test_insufficient_samples(self):
        det = ActionEfficacyDecayDetector(min_samples=10)
        for _ in range(5):
            det.record_outcome("repair", True)
        findings = det.detect_decay()
        assert "repair" not in findings

    def test_no_decay_stable_action(self):
        det = ActionEfficacyDecayDetector(min_samples=5)
        for _ in range(15):
            det.record_outcome("repair", True)
        findings = det.detect_decay()
        assert "repair" in findings
        assert findings["repair"]["is_decaying"] is False

    def test_decay_detected(self):
        det = ActionEfficacyDecayDetector(min_samples=5)
        for _ in range(10):
            det.record_outcome("repair", True)
        for _ in range(10):
            det.record_outcome("repair", False)
        findings = det.detect_decay()
        assert "repair" in findings
        assert findings["repair"]["is_decaying"] is True

    def test_empty_records(self):
        det = ActionEfficacyDecayDetector()
        findings = det.detect_decay()
        assert findings == {}

    def test_findings_fields(self):
        det = ActionEfficacyDecayDetector(min_samples=5)
        for _ in range(12):
            det.record_outcome("repair", True)
        findings = det.detect_decay()
        f = findings["repair"]
        assert "ewma_current" in f
        assert "slope" in f
        assert "is_decaying" in f
        assert "sample_count" in f


class TestGetDecayingActions:
    def test_returns_only_decaying(self):
        det = ActionEfficacyDecayDetector(min_samples=5)
        for _ in range(10):
            det.record_outcome("repair", True)
        for _ in range(10):
            det.record_outcome("repair", False)
        for _ in range(15):
            det.record_outcome("restart", True)
        result = det.get_decaying_actions()
        assert "repair" in result
        assert "restart" not in result

    def test_none_decaying(self):
        det = ActionEfficacyDecayDetector(min_samples=5)
        for _ in range(15):
            det.record_outcome("repair", True)
        assert det.get_decaying_actions() == []


class TestComputeEwma:
    def test_empty_input(self):
        assert ActionEfficacyDecayDetector._compute_ewma([]) == []

    def test_single_value(self):
        result = ActionEfficacyDecayDetector._compute_ewma([5.0])
        assert result == [5.0]

    def test_multi_value(self):
        result = ActionEfficacyDecayDetector._compute_ewma([1.0, 2.0, 3.0], alpha=0.5)
        assert len(result) == 3
        assert result[0] == 1.0
        assert result[1] == pytest.approx(0.5 * 2.0 + 0.5 * 1.0)
        assert result[2] == pytest.approx(0.5 * 3.0 + 0.5 * result[1])


class TestComputeSlope:
    def test_single_value(self):
        assert ActionEfficacyDecayDetector._compute_slope([1.0]) == 0.0

    def test_constant_values(self):
        assert ActionEfficacyDecayDetector._compute_slope([5.0, 5.0, 5.0]) == 0.0

    def test_increasing_trend(self):
        slope = ActionEfficacyDecayDetector._compute_slope([1.0, 2.0, 3.0, 4.0, 5.0])
        assert slope > 0.0

    def test_decreasing_trend(self):
        slope = ActionEfficacyDecayDetector._compute_slope([5.0, 4.0, 3.0, 2.0, 1.0])
        assert slope < 0.0
