# [A_test] module_id: MOD-GOV_data_pipeline_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_data_pipeline_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_data_pipeline_guard.py -q
# [TTL] task_bound

from __future__ import annotations

import hashlib

from zephyr.governance.data_governance.data_pipeline_guard import DataPipelineGuard


class TestDataPipelineGuardInstantiation:
    def test_creates_instance_without_args(self):
        guard = DataPipelineGuard()
        assert isinstance(guard, DataPipelineGuard)

    def test_multiple_instances_are_independent(self):
        g1 = DataPipelineGuard()
        g2 = DataPipelineGuard()
        assert g1 is not g2


class TestValidateSchema:
    def test_returns_missing_columns(self):
        guard = DataPipelineGuard()
        actual = ["id", "name", "email"]
        expected = ["id", "name", "email", "phone"]
        result = guard.validate_schema(actual, expected)
        assert "phone" in result

    def test_no_missing_columns_returns_empty(self):
        guard = DataPipelineGuard()
        actual = ["id", "name", "email"]
        expected = ["id", "name"]
        result = guard.validate_schema(actual, expected)
        assert result == []

    def test_all_columns_missing(self):
        guard = DataPipelineGuard()
        actual = []
        expected = ["id", "name"]
        result = guard.validate_schema(actual, expected)
        assert set(result) == {"id", "name"}

    def test_both_empty_returns_empty(self):
        guard = DataPipelineGuard()
        result = guard.validate_schema([], [])
        assert result == []

    def test_extra_actual_columns_not_reported(self):
        guard = DataPipelineGuard()
        actual = ["id", "name", "extra"]
        expected = ["id", "name"]
        result = guard.validate_schema(actual, expected)
        assert result == []

    def test_identical_columns_returns_empty(self):
        guard = DataPipelineGuard()
        cols = ["id", "name", "email"]
        result = guard.validate_schema(cols, cols)
        assert result == []


class TestVerifyChecksum:
    def test_correct_checksum_passes(self):
        guard = DataPipelineGuard()
        data = "hello world"
        expected = hashlib.sha256(data.encode()).hexdigest()[:8]
        assert guard.verify_checksum(data, expected) is True

    def test_incorrect_checksum_fails(self):
        guard = DataPipelineGuard()
        assert guard.verify_checksum("hello world", "deadbeef") is False

    def test_empty_data_with_correct_checksum(self):
        guard = DataPipelineGuard()
        data = ""
        expected = hashlib.sha256(data.encode()).hexdigest()[:8]
        assert guard.verify_checksum(data, expected) is True

    def test_checksum_is_case_sensitive(self):
        guard = DataPipelineGuard()
        data = "test"
        expected = hashlib.sha256(data.encode()).hexdigest()[:8]
        assert guard.verify_checksum(data, expected.upper()) is False

    def test_unicode_data_checksum(self):
        guard = DataPipelineGuard()
        data = "你好世界"
        expected = hashlib.sha256(data.encode()).hexdigest()[:8]
        assert guard.verify_checksum(data, expected) is True


class TestCheckRowCount:
    def test_exact_match_passes(self):
        guard = DataPipelineGuard()
        assert guard.check_row_count(100, 100) is True

    def test_within_tolerance_passes(self):
        guard = DataPipelineGuard()
        assert guard.check_row_count(97, 100) is True
        assert guard.check_row_count(103, 100) is True

    def test_outside_tolerance_fails(self):
        guard = DataPipelineGuard()
        assert guard.check_row_count(90, 100) is False
        assert guard.check_row_count(110, 100) is False

    def test_zero_expected_zero_actual_passes(self):
        guard = DataPipelineGuard()
        assert guard.check_row_count(0, 0) is True

    def test_zero_expected_nonzero_actual_fails(self):
        guard = DataPipelineGuard()
        assert guard.check_row_count(5, 0) is False

    def test_custom_tolerance(self):
        guard = DataPipelineGuard()
        assert guard.check_row_count(90, 100, tolerance_pct=10) is True
        assert guard.check_row_count(85, 100, tolerance_pct=10) is False

    def test_boundary_at_exact_tolerance(self):
        guard = DataPipelineGuard()
        assert guard.check_row_count(95, 100, tolerance_pct=5) is True
        assert guard.check_row_count(105, 100, tolerance_pct=5) is True

    def test_large_row_counts(self):
        guard = DataPipelineGuard()
        assert guard.check_row_count(1_000_000, 1_000_000) is True
        assert guard.check_row_count(950_000, 1_000_000, tolerance_pct=1) is False
