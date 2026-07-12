# [A_test] module_id: SRC-TST-1587 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_session_learner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_session_learner.py -q
# [TTL] task_bound
from __future__ import annotations

import pytest

from zephyr.feedback_loop.session_learner import LearningEvent, SessionLearner


class TestLearningEvent:
    def test_fields_assigned(self):
        event = LearningEvent(ke_id="KE-1", cited=True, success=True, timestamp="2026-01-01")
        assert event.ke_id == "KE-1"
        assert event.cited is True
        assert event.success is True
        assert event.timestamp == "2026-01-01"

    def test_timestamp_default_empty(self):
        event = LearningEvent(ke_id="KE-1", cited=False, success=False, timestamp="")
        assert event.timestamp == ""


class TestSessionLearnerInstantiation:
    def test_can_instantiate(self):
        learner = SessionLearner()
        assert learner is not None

    def test_default_weight_for_unknown_ke(self):
        learner = SessionLearner()
        assert learner.get_weight("KE-UNKNOWN") == 0.5


class TestRecord:
    def test_cited_and_success_increases_weight(self):
        learner = SessionLearner()
        learner.record("KE-1", cited=True, success=True)
        assert learner.get_weight("KE-1") == pytest.approx(0.6)

    def test_not_cited_decreases_weight(self):
        learner = SessionLearner()
        learner.record("KE-1", cited=False, success=False)
        assert learner.get_weight("KE-1") == pytest.approx(0.45)

    def test_cited_but_not_success_no_change(self):
        learner = SessionLearner()
        learner.record("KE-1", cited=True, success=False)
        assert learner.get_weight("KE-1") == pytest.approx(0.5)

    def test_repeated_success_accumulates(self):
        learner = SessionLearner()
        for _ in range(5):
            learner.record("KE-1", cited=True, success=True)
        assert learner.get_weight("KE-1") == pytest.approx(1.0)

    def test_weight_capped_at_one(self):
        learner = SessionLearner()
        for _ in range(10):
            learner.record("KE-1", cited=True, success=True)
        assert learner.get_weight("KE-1") == pytest.approx(1.0)

    def test_weight_floored_at_zero(self):
        learner = SessionLearner()
        for _ in range(20):
            learner.record("KE-1", cited=False, success=False)
        assert learner.get_weight("KE-1") == pytest.approx(0.0)

    def test_multiple_ke_ids_tracked_independently(self):
        learner = SessionLearner()
        learner.record("KE-A", cited=True, success=True)
        learner.record("KE-B", cited=False, success=False)
        assert learner.get_weight("KE-A") == pytest.approx(0.6)
        assert learner.get_weight("KE-B") == pytest.approx(0.45)

    def test_record_with_timestamp(self):
        learner = SessionLearner()
        learner.record("KE-1", cited=True, success=True, timestamp="2026-05-23T10:00:00")
        assert learner.get_weight("KE-1") == pytest.approx(0.6)


class TestGetWeight:
    def test_unknown_ke_returns_default(self):
        learner = SessionLearner()
        assert learner.get_weight("NONEXISTENT") == 0.5

    def test_weight_after_mixed_events(self):
        learner = SessionLearner()
        learner.record("KE-1", cited=True, success=True)
        learner.record("KE-1", cited=False, success=False)
        learner.record("KE-1", cited=True, success=True)
        expected = 0.5 + 0.1 - 0.05 + 0.1
        assert learner.get_weight("KE-1") == pytest.approx(expected)
