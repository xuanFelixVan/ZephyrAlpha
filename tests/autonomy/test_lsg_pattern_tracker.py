# [A_test] module_id: MOD-GOV_lsg_pattern_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_lsg_pattern_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_lsg_pattern_tracker.py
# [TTL] task_bound

import pytest

from zephyr.security.llm_defense.llm_security.lsg_pattern_tracker import (
    LSGPatternTracker,
    LSGRejectionPattern,
)


class TestLSGRejectionPattern:
    def test_instantiation(self):
        rp = LSGRejectionPattern(
            reason_code="TIMEOUT",
            count=1,
            same_pattern_3x=False,
            cross_session_10x=False,
            action_needed="none",
        )
        assert rp.reason_code == "TIMEOUT"
        assert rp.count == 1
        assert rp.same_pattern_3x is False
        assert rp.cross_session_10x is False
        assert rp.action_needed == "none"

    def test_missing_field_raises(self):
        with pytest.raises(TypeError):
            LSGRejectionPattern()


class TestLSGPatternTracker:
    def test_instantiation(self):
        tracker = LSGPatternTracker()
        assert tracker is not None

    def test_track_first_rejection(self):
        tracker = LSGPatternTracker()
        result = tracker.track_rejection("TIMEOUT")
        assert result.count == 1
        assert result.same_pattern_3x is False
        assert result.action_needed == "none"

    def test_track_second_rejection(self):
        tracker = LSGPatternTracker()
        tracker.track_rejection("TIMEOUT")
        result = tracker.track_rejection("TIMEOUT")
        assert result.count == 2
        assert result.action_needed == "retry"

    def test_track_third_rejection_triggers_rebuild(self):
        tracker = LSGPatternTracker()
        tracker.track_rejection("TIMEOUT")
        tracker.track_rejection("TIMEOUT")
        result = tracker.track_rejection("TIMEOUT")
        assert result.count == 3
        assert result.same_pattern_3x is True
        assert result.action_needed == "rebuild"

    def test_track_different_reason_codes(self):
        tracker = LSGPatternTracker()
        r1 = tracker.track_rejection("TIMEOUT")
        r2 = tracker.track_rejection("FORMAT_ERROR")
        assert r1.reason_code == "TIMEOUT"
        assert r2.reason_code == "FORMAT_ERROR"
        assert r1.count == 1
        assert r2.count == 1

    def test_track_many_rejections(self):
        tracker = LSGPatternTracker()
        for _ in range(5):
            tracker.track_rejection("TIMEOUT")
        result = tracker.track_rejection("TIMEOUT")
        assert result.count == 6
        assert result.same_pattern_3x is True
        assert result.action_needed == "rebuild"

    def test_returns_lsg_rejection_pattern(self):
        tracker = LSGPatternTracker()
        result = tracker.track_rejection("ERR")
        assert isinstance(result, LSGRejectionPattern)
