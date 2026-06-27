# [A_test] module_id: SRC-TST-0893 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.false_completion_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.false_completion_detector import CompletionClaim, FalseCompletionDetector
except Exception as exc:
    pytest.skip(f"Cannot import false_completion_detector: {exc}", allow_module_level=True)


class TestCompletionClaim:
    def test_default_timestamp(self):
        c = CompletionClaim(agent_id="a1", claimed_output="done", actual_output="done")
        assert c.agent_id == "a1"
        assert c.claimed_output == "done"
        assert c.actual_output == "done"
        assert c.timestamp > 0

    def test_mismatch_fields(self):
        c = CompletionClaim(agent_id="a2", claimed_output="100 lines", actual_output="")
        assert c.claimed_output != c.actual_output


class TestFalseCompletionDetector:
    def test_record_claim_matching(self):
        det = FalseCompletionDetector()
        result = det.record_claim("a1", "output", "output")
        assert result is True

    def test_record_claim_mismatch(self):
        det = FalseCompletionDetector()
        result = det.record_claim("a1", "output", "different")
        assert result is False

    def test_check_false_completion_normal(self):
        det = FalseCompletionDetector()
        result = det.check_false_completion("a1", expected_size=100, actual_size=80)
        assert result["agent_id"] == "a1"
        assert result["expected_size"] == 100
        assert result["actual_size"] == 80
        assert result["ratio"] == 0.8
        assert result["suspicious"] is False

    def test_check_false_completion_suspicious(self):
        det = FalseCompletionDetector()
        result = det.check_false_completion("a1", expected_size=100, actual_size=5)
        assert result["ratio"] < 0.1
        assert result["suspicious"] is True

    def test_check_false_completion_zero_actual(self):
        det = FalseCompletionDetector()
        result = det.check_false_completion("a1", expected_size=100, actual_size=0)
        assert result["suspicious"] is True

    def test_check_false_completion_zero_expected(self):
        det = FalseCompletionDetector()
        result = det.check_false_completion("a1", expected_size=0, actual_size=0)
        assert result["ratio"] == 0.0

    def test_is_over_threshold_false(self):
        det = FalseCompletionDetector()
        assert det.is_over_threshold() is False

    def test_is_over_threshold_true(self):
        det = FalseCompletionDetector()
        det.record_claim("a1", "x", "y1")
        det.record_claim("a2", "x", "y2")
        det.record_claim("a3", "x", "y3")
        assert det.is_over_threshold() is True

    def test_reset(self):
        det = FalseCompletionDetector()
        det.record_claim("a1", "x", "y")
        det.reset()
        assert det.is_over_threshold() is False

    def test_multiple_mismatches_accumulate(self):
        det = FalseCompletionDetector()
        det.record_claim("a1", "a", "b")
        det.record_claim("a2", "c", "c")
        assert det.is_over_threshold() is False
        det.record_claim("a3", "d", "e")
        det.record_claim("a4", "f", "g")
        assert det.is_over_threshold() is True
