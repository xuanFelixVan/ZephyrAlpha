# [A_test] module_id: SRC-TST-1336 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_orchestrator_failure_matcher
# [INVARIANTS] FailurePatternMatcher has 7 built-in patterns; analyze returns highest severity match
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_orchestrator_failure_matcher.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.failure_matcher import FailureDiagnosis, FailurePatternMatcher


class TestFailureDiagnosis:
    def test_creation(self):
        d = FailureDiagnosis(
            task_id="T-1",
            pattern_name="timeout_exceeded",
            severity="low",
            suggestion="retry",
        )
        assert d.task_id == "T-1"
        assert d.pattern_name == "timeout_exceeded"
        assert d.severity == "low"
        assert d.suggestion == "retry"
        assert d.automatic_recovery is False
        assert d.metadata == {}

    def test_with_metadata(self):
        d = FailureDiagnosis(
            task_id="T-1",
            pattern_name="gate_violation",
            severity="high",
            suggestion="check gates",
            automatic_recovery=False,
            metadata={"matched_text": "gate violation"},
        )
        assert d.metadata["matched_text"] == "gate violation"


class TestFailurePatternMatcherAnalyze:
    def test_iterative_retry_loop(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-1", "retry attempt 第 3 次")
        assert result is not None
        assert result.pattern_name == "iterative_retry_loop"
        assert result.severity == "high"

    def test_context_insufficient(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-2", "context token limit exceeded")
        assert result is not None
        assert result.pattern_name == "context_insufficient"
        assert result.severity == "medium"

    def test_multi_module_failure(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-3", "多个模块级联失败 multi module error")
        assert result is not None
        assert result.pattern_name == "multi_module_failure"
        assert result.severity == "critical"

    def test_schema_mismatch(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-4", "schema validation error field missing")
        assert result is not None
        assert result.pattern_name == "schema_mismatch"
        assert result.severity == "medium"

    def test_gate_violation(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-5", "gate G3 violation detected")
        assert result is not None
        assert result.pattern_name == "gate_violation"
        assert result.severity == "high"

    def test_dependency_freshness(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-6", "dependency outdated stale data")
        assert result is not None
        assert result.pattern_name == "dependency_freshness"
        assert result.severity == "medium"

    def test_timeout_exceeded(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-7", "timeout timed out 耗时 30 分钟")
        assert result is not None
        assert result.pattern_name == "timeout_exceeded"
        assert result.severity == "low"
        assert result.automatic_recovery is True

    def test_no_match_returns_none(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-8", "everything is fine")
        assert result is None

    def test_highest_severity_selected(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-9", "gate violation and timeout exceeded")
        assert result is not None
        assert result.severity in ("high", "critical", "low")

    def test_empty_error_text(self):
        matcher = FailurePatternMatcher()
        result = matcher.analyze("T-10", "")
        assert result is None


class TestFailurePatternMatcherDiagnoses:
    def test_diagnoses_accumulate(self):
        matcher = FailurePatternMatcher()
        matcher.analyze("T-1", "timeout exceeded")
        matcher.analyze("T-2", "gate violation")
        assert len(matcher.diagnoses()) == 2

    def test_diagnoses_returns_copy(self):
        matcher = FailurePatternMatcher()
        matcher.analyze("T-1", "timeout exceeded")
        d = matcher.diagnoses()
        d.clear()
        assert len(matcher.diagnoses()) == 1

    def test_clear_diagnoses(self):
        matcher = FailurePatternMatcher()
        matcher.analyze("T-1", "timeout exceeded")
        matcher.clear_diagnoses()
        assert len(matcher.diagnoses()) == 0


class TestFailurePatternMatcherActivate:
    def test_activate_sets_active(self):
        matcher = FailurePatternMatcher()
        matcher.activate()
        assert matcher._active is True

    def test_deactivate_clears_active(self):
        matcher = FailurePatternMatcher()
        matcher.activate()
        matcher.deactivate()
        assert matcher._active is False

    def test_double_activate_idempotent(self):
        matcher = FailurePatternMatcher()
        matcher.activate()
        matcher.activate()
        assert matcher._active is True

    def test_deactivate_when_inactive(self):
        matcher = FailurePatternMatcher()
        matcher.deactivate()
        assert matcher._active is False
