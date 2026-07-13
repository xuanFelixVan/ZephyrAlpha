# [A_test] module_id: SRC-TST-0611 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_context_window_contamination_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_context_window_contamination_detector.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.detectors.drift.context_window_contamination_detector import (
    ContextWindowContaminationDetector,
    TokenSource,
)


class TestTokenSource:
    def test_enum_values(self):
        assert TokenSource.CURRENT_SESSION.value == "CURRENT_SESSION"
        assert TokenSource.RESUME_FROM_PRIOR.value == "RESUME_FROM_PRIOR"
        assert TokenSource.RAG_RETRIEVAL.value == "RAG_RETRIEVAL"
        assert TokenSource.SYSTEM_PROMPT.value == "SYSTEM_PROMPT"
        assert TokenSource.HALLUCINATED_REFERENCE.value == "HALLUCINATED_REFERENCE"

    def test_enum_count(self):
        assert len(TokenSource) == 5


class TestContextWindowContaminationDetectorInstantiation:
    def test_default_construction(self):
        det = ContextWindowContaminationDetector()
        assert det.max_stale_ratio == 0.30
        assert det.max_cross_session_carryover == 0.15
        assert det.max_hallucinated_ratio == 0.05
        assert det.total_tokens == 0
        assert det.contamination_events == []

    def test_custom_params(self):
        det = ContextWindowContaminationDetector(
            max_stale_ratio=0.5,
            max_cross_session_carryover=0.2,
            max_hallucinated_ratio=0.1,
        )
        assert det.max_stale_ratio == 0.5
        assert det.max_cross_session_carryover == 0.2
        assert det.max_hallucinated_ratio == 0.1

    def test_token_sources_initialized(self):
        det = ContextWindowContaminationDetector()
        for source in TokenSource:
            assert source.value in det.token_sources
            assert det.token_sources[source.value] == 0


class TestRecordTokens:
    def test_record_current_session(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 100)
        assert det.token_sources[TokenSource.CURRENT_SESSION.value] == 100
        assert det.total_tokens == 100

    def test_record_multiple_sources(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 100)
        det.record_tokens(TokenSource.RAG_RETRIEVAL, 50)
        assert det.total_tokens == 150

    def test_record_accumulates(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 100)
        det.record_tokens(TokenSource.CURRENT_SESSION, 50)
        assert det.token_sources[TokenSource.CURRENT_SESSION.value] == 150
        assert det.total_tokens == 150

    def test_record_zero_tokens(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 0)
        assert det.total_tokens == 0


class TestDetectContamination:
    def test_no_tokens_returns_clean(self):
        det = ContextWindowContaminationDetector()
        result = det.detect_contamination()
        assert result["contaminated"] is False
        assert result["confidence"] == 0.0

    def test_clean_session(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 800)
        det.record_tokens(TokenSource.SYSTEM_PROMPT, 200)
        result = det.detect_contamination()
        assert result["contaminated"] is False
        assert result["recommendation"] == "continue"

    def test_stale_context_detected(self):
        det = ContextWindowContaminationDetector(max_stale_ratio=0.30)
        det.record_tokens(TokenSource.CURRENT_SESSION, 500)
        det.record_tokens(TokenSource.RESUME_FROM_PRIOR, 500)
        result = det.detect_contamination()
        assert result["contaminated"] is True
        assert result["recommendation"] == "context_refresh"

    def test_hallucinated_reference_detected(self):
        det = ContextWindowContaminationDetector(max_hallucinated_ratio=0.05)
        det.record_tokens(TokenSource.CURRENT_SESSION, 900)
        det.record_tokens(TokenSource.HALLUCINATED_REFERENCE, 100)
        result = det.detect_contamination()
        assert result["contaminated"] is True

    def test_contamination_event_recorded(self):
        det = ContextWindowContaminationDetector(max_stale_ratio=0.30)
        det.record_tokens(TokenSource.CURRENT_SESSION, 500)
        det.record_tokens(TokenSource.RESUME_FROM_PRIOR, 500)
        det.detect_contamination()
        assert len(det.contamination_events) == 1

    def test_no_contamination_event_when_clean(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 1000)
        det.detect_contamination()
        assert len(det.contamination_events) == 0

    def test_result_fields(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 1000)
        result = det.detect_contamination()
        assert "contaminated" in result
        assert "flags" in result
        assert "stale_ratio" in result
        assert "carryover_ratio" in result
        assert "hallucinated_ratio" in result
        assert "recommendation" in result


class TestGetProvenanceSummary:
    def test_empty_summary(self):
        det = ContextWindowContaminationDetector()
        summary = det.get_provenance_summary()
        assert summary["total_tokens"] == 0
        assert summary["contamination_count"] == 0

    def test_summary_with_data(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 800)
        det.record_tokens(TokenSource.RAG_RETRIEVAL, 200)
        summary = det.get_provenance_summary()
        assert summary["total_tokens"] == 1000
        assert summary["sources"][TokenSource.CURRENT_SESSION.value] == 800
        assert summary["sources"][TokenSource.RAG_RETRIEVAL.value] == 200

    def test_summary_after_contamination(self):
        det = ContextWindowContaminationDetector(max_stale_ratio=0.30)
        det.record_tokens(TokenSource.CURRENT_SESSION, 500)
        det.record_tokens(TokenSource.RESUME_FROM_PRIOR, 500)
        det.detect_contamination()
        summary = det.get_provenance_summary()
        assert summary["contamination_count"] == 1


class TestResetWindow:
    def test_reset_clears_tokens(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 1000)
        det.reset_window()
        assert det.total_tokens == 0
        for source in TokenSource:
            assert det.token_sources[source.value] == 0

    def test_reset_preserves_contamination_events(self):
        det = ContextWindowContaminationDetector(max_stale_ratio=0.30)
        det.record_tokens(TokenSource.CURRENT_SESSION, 500)
        det.record_tokens(TokenSource.RESUME_FROM_PRIOR, 500)
        det.detect_contamination()
        event_count = len(det.contamination_events)
        det.reset_window()
        assert len(det.contamination_events) == event_count

    def test_reset_then_record(self):
        det = ContextWindowContaminationDetector()
        det.record_tokens(TokenSource.CURRENT_SESSION, 1000)
        det.reset_window()
        det.record_tokens(TokenSource.CURRENT_SESSION, 500)
        assert det.total_tokens == 500
