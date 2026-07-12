# [A_test] module_id: SRC-TST-0650 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_cross_session_consistency_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.cross_session_consistency_validator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_cross_session_consistency_validator.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.cross_session_consistency_validator import (
    CrossSessionConsistencyValidator,
)


class TestCrossSessionConsistencyValidatorInstantiation:
    def test_default_params(self):
        csv = CrossSessionConsistencyValidator()
        assert csv.config_hashes == []
        assert csv.max_hashes == 50
        assert csv.threshold_history == {}
        assert csv.jump_threshold_sigma == 2.0


class TestCrossSessionConsistencyValidatorRecordConfig:
    def test_record_returns_hash(self):
        csv = CrossSessionConsistencyValidator()
        h = csv.record_config({"threshold": 0.5}, "session-1")
        assert isinstance(h, str)
        assert len(h) > 0

    def test_record_stores_hash(self):
        csv = CrossSessionConsistencyValidator()
        csv.record_config({"threshold": 0.5}, "session-1")
        assert len(csv.config_hashes) == 1

    def test_record_tracks_numeric_thresholds(self):
        csv = CrossSessionConsistencyValidator()
        csv.record_config({"alpha": 0.2, "beta": 0.8}, "session-1")
        assert "alpha" in csv.threshold_history
        assert "beta" in csv.threshold_history
        assert csv.threshold_history["alpha"] == [0.2]
        assert csv.threshold_history["beta"] == [0.8]

    def test_record_accumulates_history(self):
        csv = CrossSessionConsistencyValidator()
        csv.record_config({"alpha": 0.1}, "s1")
        csv.record_config({"alpha": 0.2}, "s2")
        csv.record_config({"alpha": 0.15}, "s3")
        assert len(csv.threshold_history["alpha"]) == 3

    def test_record_ignores_non_numeric_values(self):
        csv = CrossSessionConsistencyValidator()
        csv.record_config({"name": "test", "threshold": 0.5}, "s1")
        assert "name" not in csv.threshold_history
        assert "threshold" in csv.threshold_history

    def test_record_trims_at_max(self):
        csv = CrossSessionConsistencyValidator(max_hashes=3)
        for i in range(5):
            csv.record_config({"v": float(i)}, f"s{i}")
        assert len(csv.config_hashes) == 3


class TestCrossSessionConsistencyValidatorDetectJumps:
    def test_no_jumps_with_insufficient_data(self):
        csv = CrossSessionConsistencyValidator()
        csv.record_config({"alpha": 0.1}, "s1")
        result = csv.detect_jumps()
        assert result["jumps_detected"] == []

    def test_no_jumps_with_stable_values(self):
        csv = CrossSessionConsistencyValidator()
        for i in range(5):
            csv.record_config({"alpha": 0.5}, f"s{i}")
        result = csv.detect_jumps()
        assert result["jumps_detected"] == []

    def test_detects_jump(self):
        csv = CrossSessionConsistencyValidator(jump_threshold_sigma=2.0)
        for i in range(10):
            csv.record_config({"alpha": 0.5 + i * 0.001}, "s1")
        csv.record_config({"alpha": 5.0}, "s2")
        result = csv.detect_jumps()
        assert "alpha" in result["jumps_detected"]

    def test_jump_details_contain_severity(self):
        csv = CrossSessionConsistencyValidator(jump_threshold_sigma=1.0)
        for _ in range(10):
            csv.record_config({"alpha": 0.5}, "s1")
        csv.record_config({"alpha": 10.0}, "s2")
        result = csv.detect_jumps()
        if result["details"]:
            detail = result["details"]["alpha"]
            assert "severity" in detail
            assert "sigma_deviation" in detail


class TestCrossSessionConsistencyValidatorVerifyHashChain:
    def test_intact_chain_single_entry(self):
        csv = CrossSessionConsistencyValidator()
        csv.record_config({"k": 1}, "s1")
        result = csv.verify_hash_chain()
        assert result["chain_intact"] is True

    def test_intact_chain_multiple_entries(self):
        csv = CrossSessionConsistencyValidator()
        csv.record_config({"k": 1}, "s1")
        csv.record_config({"k": 2}, "s2")
        csv.record_config({"k": 3}, "s3")
        result = csv.verify_hash_chain()
        assert result["chain_intact"] is True
        assert result["length"] == 3

    def test_empty_chain(self):
        csv = CrossSessionConsistencyValidator()
        result = csv.verify_hash_chain()
        assert result["chain_intact"] is True
        assert result["length"] == 0


class TestCrossSessionConsistencyValidatorBoundary:
    def test_empty_config(self):
        csv = CrossSessionConsistencyValidator()
        h = csv.record_config({}, "s1")
        assert isinstance(h, str)

    def test_none_config_raises(self):
        csv = CrossSessionConsistencyValidator()
        with pytest.raises((TypeError, AttributeError)):
            csv.record_config(None, "s1")

    def test_none_session_id(self):
        csv = CrossSessionConsistencyValidator()
        h = csv.record_config({"k": 1}, None)
        assert isinstance(h, str)

    def test_all_non_numeric_config(self):
        csv = CrossSessionConsistencyValidator()
        csv.record_config({"name": "a", "mode": "strict"}, "s1")
        assert csv.threshold_history == {}
