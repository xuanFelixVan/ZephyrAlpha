# [A_test] module_id: MOD-GOV_governance_budget_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_governance_budget_tracker
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] track_cost must return dict with budget_consumed=True
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TypeError on wrong arg types
# [TESTS] tests/test_governance_budget_tracker.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.budget_tracker import RollbackBudgetTracker


class TestRollbackBudgetTrackerInstantiation:
    def test_can_instantiate(self):
        tracker = RollbackBudgetTracker()
        assert tracker is not None

    def test_is_instance_of_correct_class(self):
        tracker = RollbackBudgetTracker()
        assert isinstance(tracker, RollbackBudgetTracker)


class TestTrackCost:
    def test_track_cost_returns_dict(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("agent-1", "rb-001", 0.5)
        assert isinstance(result, dict)

    def test_track_cost_returns_correct_keys(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("agent-1", "rb-001", 0.5)
        expected_keys = {"agent_id", "rollback_id", "cost", "budget_consumed"}
        assert expected_keys.issubset(set(result.keys()))

    def test_track_cost_returns_budget_consumed_true(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("agent-1", "rb-001", 0.5)
        assert result["budget_consumed"] is True

    def test_track_cost_preserves_agent_id(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("my-agent", "rb-002", 1.0)
        assert result["agent_id"] == "my-agent"

    def test_track_cost_preserves_rollback_id(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("agent-1", "rb-003", 2.5)
        assert result["rollback_id"] == "rb-003"

    def test_track_cost_preserves_cost_value(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("agent-1", "rb-004", 3.14)
        assert result["cost"] == 3.14


class TestTrackCostBoundaryCases:
    def test_track_cost_zero_cost(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("agent-1", "rb-005", 0.0)
        assert result["cost"] == 0.0
        assert result["budget_consumed"] is True

    def test_track_cost_negative_cost(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("agent-1", "rb-006", -1.0)
        assert result["cost"] == -1.0

    def test_track_cost_very_large_cost(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("agent-1", "rb-007", 1e9)
        assert result["cost"] == 1e9

    def test_track_cost_empty_agent_id(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("", "rb-008", 0.5)
        assert result["agent_id"] == ""

    def test_track_cost_empty_rollback_id(self):
        tracker = RollbackBudgetTracker()
        result = tracker.track_cost("agent-1", "", 0.5)
        assert result["rollback_id"] == ""

    def test_track_cost_multiple_calls_independent(self):
        tracker = RollbackBudgetTracker()
        r1 = tracker.track_cost("agent-a", "rb-a", 1.0)
        r2 = tracker.track_cost("agent-b", "rb-b", 2.0)
        assert r1["agent_id"] == "agent-a"
        assert r1["cost"] == 1.0
        assert r2["agent_id"] == "agent-b"
        assert r2["cost"] == 2.0
