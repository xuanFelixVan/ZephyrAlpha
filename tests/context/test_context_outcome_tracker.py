# [A_test] module_id: MOD-GOV_context_outcome_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_context_outcome_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_context_outcome_tracker.py -q
# [TTL] task_bound
from __future__ import annotations

import pytest

from zephyr.autonomy_core.context.context_outcome_tracker import (
    ContextOutcomeLink,
    ContextOutcomeTracker,
)


class TestContextOutcomeLink:
    def test_default_values(self):
        link = ContextOutcomeLink(
            context_block_id="CB-001",
            agent_actions=["act_a"],
            action_successes=[True],
        )
        assert link.success_rate == 0.0
        assert link.suspect is False

    def test_custom_values(self):
        link = ContextOutcomeLink(
            context_block_id="CB-002",
            agent_actions=["act_a", "act_b"],
            action_successes=[True, False],
            success_rate=0.5,
            suspect=True,
        )
        assert link.success_rate == 0.5
        assert link.suspect is True


class TestContextOutcomeTrackerInit:
    def test_instantiation(self):
        tracker = ContextOutcomeTracker()
        assert tracker.links == {}


class TestContextOutcomeTrackerRecord:
    def test_record_all_success(self):
        tracker = ContextOutcomeTracker()
        link = tracker.record("CB-010", ["a1", "a2"], [True, True])
        assert link.context_block_id == "CB-010"
        assert link.agent_actions == ["a1", "a2"]
        assert link.action_successes == [True, True]
        assert link.success_rate == 1.0
        assert link.suspect is False

    def test_record_mixed_success(self):
        tracker = ContextOutcomeTracker()
        link = tracker.record("CB-011", ["a1", "a2", "a3"], [True, False, True])
        assert link.success_rate == pytest.approx(0.667, abs=0.01)
        assert link.suspect is False

    def test_record_low_success_marks_suspect(self):
        tracker = ContextOutcomeTracker()
        link = tracker.record("CB-012", ["a1", "a2"], [False, False])
        assert link.success_rate == 0.0
        assert link.suspect is True

    def test_record_overwrites_existing(self):
        tracker = ContextOutcomeTracker()
        tracker.record("CB-020", ["a1"], [True])
        link2 = tracker.record("CB-020", ["a1", "a2"], [True, False])
        assert tracker.links["CB-020"] is link2
        assert link2.success_rate == 0.5

    def test_record_empty_actions(self):
        tracker = ContextOutcomeTracker()
        link = tracker.record("CB-030", [], [])
        assert link.success_rate == 0.0
        assert link.suspect is True

    def test_record_exactly_half_success(self):
        tracker = ContextOutcomeTracker()
        link = tracker.record("CB-040", ["a1", "a2"], [True, False])
        assert link.success_rate == 0.5
        assert link.suspect is False

    def test_record_single_failure(self):
        tracker = ContextOutcomeTracker()
        link = tracker.record("CB-050", ["a1"], [False])
        assert link.success_rate == 0.0
        assert link.suspect is True

    def test_success_rate_rounded_to_three_decimals(self):
        tracker = ContextOutcomeTracker()
        link = tracker.record("CB-060", ["a1", "a2", "a3"], [True, True, False])
        assert link.success_rate == round(2 / 3, 3)


class TestContextOutcomeTrackerLowSuccessKe:
    def test_no_suspects(self):
        tracker = ContextOutcomeTracker()
        tracker.record("CB-100", ["a1"], [True])
        assert tracker.low_success_ke() == []

    def test_one_suspect(self):
        tracker = ContextOutcomeTracker()
        tracker.record("CB-101", ["a1"], [False])
        result = tracker.low_success_ke()
        assert result == ["CB-101"]

    def test_mixed_records(self):
        tracker = ContextOutcomeTracker()
        tracker.record("CB-200", ["a1"], [True])
        tracker.record("CB-201", ["a1"], [False])
        tracker.record("CB-202", ["a1", "a2"], [False, False])
        result = tracker.low_success_ke()
        assert "CB-200" not in result
        assert "CB-201" in result
        assert "CB-202" in result

    def test_all_suspects(self):
        tracker = ContextOutcomeTracker()
        tracker.record("CB-300", ["a1"], [False])
        tracker.record("CB-301", ["a1", "a2"], [False, False])
        result = tracker.low_success_ke()
        assert len(result) == 2
