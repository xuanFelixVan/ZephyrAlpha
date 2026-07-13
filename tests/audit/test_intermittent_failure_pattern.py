# [A_test] module_id: SRC-TST-1147 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_intermittent_failure_pattern
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_intermittent_failure_pattern.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.detectors.anomaly.intermittent_failure_pattern import (
    IntermittentFailurePattern,
    PatternConfidence,
)


class TestPatternConfidence:
    def test_enum_values(self):
        assert PatternConfidence.NONE.value == "NONE"
        assert PatternConfidence.LOW.value == "LOW"
        assert PatternConfidence.MEDIUM.value == "MEDIUM"
        assert PatternConfidence.HIGH.value == "HIGH"


class TestIntermittentFailurePattern:
    def test_default_construction(self):
        det = IntermittentFailurePattern()
        assert det.min_occurrences == 5
        assert det.condition_correlation_threshold == 0.70
        assert det.context_window_days == 7
        assert det.failure_contexts == {}
        assert det.discovered_patterns == []

    def test_custom_construction(self):
        det = IntermittentFailurePattern(
            min_occurrences=3,
            condition_correlation_threshold=0.5,
            context_window_days=14,
        )
        assert det.min_occurrences == 3
        assert det.condition_correlation_threshold == 0.5
        assert det.context_window_days == 14

    def test_record_failure_creates_entry(self):
        det = IntermittentFailurePattern()
        det.record_failure("timeout", {"load": "high"})
        assert "timeout" in det.failure_contexts
        assert len(det.failure_contexts["timeout"]) == 1

    def test_record_failure_multiple_entries(self):
        det = IntermittentFailurePattern()
        for _ in range(3):
            det.record_failure("timeout", {"load": "high"})
        assert len(det.failure_contexts["timeout"]) == 3

    def test_analyze_pattern_insufficient_occurrences(self):
        det = IntermittentFailurePattern(min_occurrences=5)
        for _ in range(3):
            det.record_failure("timeout", {"load": "high"})
        result = det.analyze_pattern("timeout")
        assert result["pattern_found"] is False
        assert result["confidence"] == PatternConfidence.NONE.value
        assert result["reason"] == "insufficient_occurrences"

    def test_analyze_pattern_no_strong_correlations(self):
        det = IntermittentFailurePattern(min_occurrences=3, condition_correlation_threshold=0.70)
        contexts = [
            {"load": "high"},
            {"load": "medium"},
            {"load": "low"},
            {"load": "high"},
            {"load": "medium"},
        ]
        for ctx in contexts:
            det.record_failure("timeout", ctx)
        result = det.analyze_pattern("timeout")
        assert result["pattern_found"] is False

    def test_analyze_pattern_with_strong_correlation(self):
        det = IntermittentFailurePattern(min_occurrences=3, condition_correlation_threshold=0.70)
        for _ in range(8):
            det.record_failure("timeout", {"load": "high", "region": "us-east"})
        for _ in range(2):
            det.record_failure("timeout", {"load": "low", "region": "eu-west"})
        result = det.analyze_pattern("timeout")
        assert result["pattern_found"] is True
        assert result["occurrences"] == 10

    def test_analyze_pattern_high_confidence(self):
        det = IntermittentFailurePattern(min_occurrences=3, condition_correlation_threshold=0.70)
        for _ in range(9):
            det.record_failure("timeout", {"load": "high"})
        det.record_failure("timeout", {"load": "low"})
        result = det.analyze_pattern("timeout")
        assert result["confidence"] == PatternConfidence.HIGH.value
        assert result["recommendation"] == "reproduce_with_exact_conditions"

    def test_analyze_pattern_medium_confidence(self):
        det = IntermittentFailurePattern(min_occurrences=3, condition_correlation_threshold=0.70)
        for _ in range(8):
            det.record_failure("timeout", {"load": "high"})
        for _ in range(2):
            det.record_failure("timeout", {"load": "low"})
        result = det.analyze_pattern("timeout")
        assert result["confidence"] in (
            PatternConfidence.MEDIUM.value,
            PatternConfidence.HIGH.value,
        )

    def test_analyze_pattern_unknown_failure_type(self):
        det = IntermittentFailurePattern()
        result = det.analyze_pattern("nonexistent")
        assert result["pattern_found"] is False

    def test_analyze_all_patterns(self):
        det = IntermittentFailurePattern(min_occurrences=3, condition_correlation_threshold=0.70)
        for _ in range(8):
            det.record_failure("timeout", {"load": "high"})
        for _ in range(2):
            det.record_failure("timeout", {"load": "low"})
        results = det.analyze_all_patterns()
        assert isinstance(results, list)
        if results:
            assert results[0]["pattern_found"] is True

    def test_get_temporal_clustering_empty(self):
        det = IntermittentFailurePattern()
        result = det.get_temporal_clustering("nonexistent")
        assert result["clustered"] is False

    def test_get_temporal_clustering_single_event(self):
        det = IntermittentFailurePattern()
        det.record_failure("timeout", {"load": "high"})
        result = det.get_temporal_clustering("timeout")
        assert result["clustered"] is False

    def test_get_temporal_clustering_bursty(self):
        det = IntermittentFailurePattern()
        now = time.time()
        for i in range(10):
            det.failure_contexts.setdefault("timeout", []).append({"ts": now + i * 0.01, "load": "high"})
        for i in range(10):
            det.failure_contexts["timeout"].append({"ts": now + 1000 + i * 0.01, "load": "high"})
        result = det.get_temporal_clustering("timeout")
        assert "total_occurrences" in result
        assert result["total_occurrences"] == 20

    def test_get_all_discovered_patterns(self):
        det = IntermittentFailurePattern(min_occurrences=3, condition_correlation_threshold=0.70)
        for _ in range(8):
            det.record_failure("timeout", {"load": "high"})
        for _ in range(2):
            det.record_failure("timeout", {"load": "low"})
        det.analyze_pattern("timeout")
        patterns = det.get_all_discovered_patterns()
        assert isinstance(patterns, list)

    def test_overall_pattern_discovery_rate_empty(self):
        det = IntermittentFailurePattern()
        assert det.overall_pattern_discovery_rate() == 1.0

    def test_overall_pattern_discovery_rate(self):
        det = IntermittentFailurePattern(min_occurrences=3, condition_correlation_threshold=0.70)
        for _ in range(8):
            det.record_failure("timeout", {"load": "high"})
        for _ in range(2):
            det.record_failure("timeout", {"load": "low"})
        det.record_failure("other_error", {"load": "low"})
        det.analyze_pattern("timeout")
        rate = det.overall_pattern_discovery_rate()
        assert 0.0 <= rate <= 1.0
