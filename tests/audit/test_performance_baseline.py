# [A_test] module_id: SRC-TST-1365 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [MODULE] tests.test_performance_baseline
# [INVARIANTS] PERFORMANCE_BASELINE_immutable;E2E_MAX_MS=500;validate_e2e_budget_check
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_performance_baseline.py
# [TTL] task_bound

import pytest

from zephyr.gov_drift.detector_core.performance_baseline import (
    E2E_BUDGET_BREAKDOWN,
    E2E_MAX_MS,
    PERFORMANCE_BASELINE,
    LatencySegment,
    get_segment,
    validate_e2e,
)


class TestLatencySegment:
    def test_creation(self):
        seg = LatencySegment(name="test_seg", max_ms=100, description="test")
        assert seg.name == "test_seg"
        assert seg.max_ms == 100
        assert seg.description == "test"

    def test_frozen(self):
        seg = LatencySegment(name="a", max_ms=50, description="b")
        with pytest.raises(AttributeError):
            seg.max_ms = 200

    def test_equality(self):
        a = LatencySegment(name="x", max_ms=10, description="d")
        b = LatencySegment(name="x", max_ms=10, description="d")
        assert a == b


class TestPerformanceBaseline:
    def test_baseline_not_empty(self):
        assert len(PERFORMANCE_BASELINE) > 0

    def test_all_segments_have_valid_max_ms(self):
        for seg in PERFORMANCE_BASELINE:
            assert seg.max_ms > 0
            assert isinstance(seg.max_ms, int)

    def test_e2e_max_ms_value(self):
        assert E2E_MAX_MS == 500

    def test_budget_breakdown_sums_within_e2e(self):
        total = sum(E2E_BUDGET_BREAKDOWN.values())
        assert total <= E2E_MAX_MS

    def test_budget_breakdown_keys_match_segments(self):
        segment_names = {seg.name for seg in PERFORMANCE_BASELINE}
        budget_keys = set(E2E_BUDGET_BREAKDOWN.keys())
        assert segment_names.issubset(budget_keys)


class TestGetSegment:
    def test_existing_segment(self):
        seg = get_segment("market_to_signal")
        assert seg is not None
        assert seg.name == "market_to_signal"
        assert seg.max_ms == 200

    def test_nonexistent_segment(self):
        assert get_segment("nonexistent") is None

    def test_empty_name(self):
        assert get_segment("") is None

    def test_all_baseline_segments_findable(self):
        for seg in PERFORMANCE_BASELINE:
            found = get_segment(seg.name)
            assert found is not None
            assert found.name == seg.name


class TestValidateE2E:
    def test_valid_within_budget(self):
        segments = {"market_to_signal": 150, "signal_to_risk": 5, "risk_to_order": 30}
        ok, msg = validate_e2e(segments)
        assert ok is True
        assert "PASS" in msg

    def test_exceeds_e2e_total(self):
        segments = {"market_to_signal": 400, "signal_to_risk": 50, "risk_to_order": 100}
        ok, msg = validate_e2e(segments)
        assert ok is False
        assert "E2E" in msg

    def test_segment_exceeds_own_max(self):
        segments = {"market_to_signal": 250}
        ok, msg = validate_e2e(segments)
        assert ok is False
        assert "market_to_signal" in msg

    def test_empty_dict(self):
        ok, msg = validate_e2e({})
        assert ok is True
        assert "PASS" in msg

    def test_unknown_segment_name_passes(self):
        segments = {"unknown_segment": 10}
        ok, msg = validate_e2e(segments)
        assert ok is True

    def test_exact_at_segment_limit(self):
        segments = {"market_to_signal": 200, "signal_to_risk": 10, "risk_to_order": 50}
        ok, msg = validate_e2e(segments)
        assert ok is True
