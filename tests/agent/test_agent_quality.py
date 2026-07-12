# [A_test] module_id: SRC-TST-0290 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_agent_quality
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_agent_quality.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.quality.agent_quality import AgentQualityTracker


class TestAgentQualityTrackerInstantiation:
    def test_default_construction(self):
        tracker = AgentQualityTracker()
        assert tracker is not None

    def test_initial_state_empty(self):
        tracker = AgentQualityTracker()
        assert tracker.average_score("nonexistent") == 0.0


class TestAgentQualityTrackerRecord:
    def test_record_single_score(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 0.9)
        assert tracker.average_score("agent-1") == 0.9

    def test_record_multiple_scores_same_agent(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 0.8)
        tracker.record("agent-1", 1.0)
        assert tracker.average_score("agent-1") == pytest.approx(0.9)

    def test_record_multiple_agents(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 0.9)
        tracker.record("agent-2", 0.5)
        assert tracker.average_score("agent-1") == 0.9
        assert tracker.average_score("agent-2") == 0.5

    def test_record_zero_score(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 0.0)
        assert tracker.average_score("agent-1") == 0.0

    def test_record_perfect_score(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 1.0)
        assert tracker.average_score("agent-1") == 1.0


class TestAgentQualityTrackerAverageScore:
    def test_average_unknown_agent(self):
        tracker = AgentQualityTracker()
        assert tracker.average_score("unknown") == 0.0

    def test_average_with_many_records(self):
        tracker = AgentQualityTracker()
        scores = [0.5, 0.7, 0.9, 1.0, 0.3]
        for s in scores:
            tracker.record("agent-1", s)
        expected = sum(scores) / len(scores)
        assert tracker.average_score("agent-1") == pytest.approx(expected)


class TestAgentQualityTrackerShouldEscalate:
    def test_escalate_when_below_threshold(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 0.5)
        assert tracker.should_escalate("agent-1") is True

    def test_no_escalate_when_above_threshold(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 0.8)
        assert tracker.should_escalate("agent-1") is False

    def test_escalate_at_exact_threshold(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 0.6)
        assert tracker.should_escalate("agent-1") is False

    def test_escalate_unknown_agent(self):
        tracker = AgentQualityTracker()
        assert tracker.should_escalate("unknown") is True

    def test_escalate_with_mixed_scores(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 0.2)
        tracker.record("agent-1", 0.3)
        tracker.record("agent-1", 1.0)
        assert tracker.should_escalate("agent-1") is True

    def test_no_escalate_with_good_average(self):
        tracker = AgentQualityTracker()
        tracker.record("agent-1", 0.7)
        tracker.record("agent-1", 0.8)
        tracker.record("agent-1", 0.9)
        assert tracker.should_escalate("agent-1") is False
