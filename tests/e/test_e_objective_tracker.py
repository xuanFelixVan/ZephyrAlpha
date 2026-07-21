# [A_test] module_id: MOD-GOV_e_objective_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_objective_tracker
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.observability_governance.objective_tracker import ObjectiveTracker


class TestObjectiveTracker:
    def test_set_objective_stores(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent-1", "maximize profit")
        assert ot._objectives["agent-1"] == ["maximize profit"]
        assert ot._versions["agent-1"] == 1

    def test_detect_drift_no_drift(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent-1", "obj-a")
        assert ot.detect_drift("agent-1") is False

    def test_detect_drift_with_change(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent-1", "obj-a")
        ot.set_objective("agent-1", "obj-b")
        assert ot.detect_drift("agent-1") is True

    def test_detect_drift_unknown_agent(self):
        ot = ObjectiveTracker()
        assert ot.detect_drift("unknown") is False

    def test_rollback_removes_latest(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent-1", "obj-a")
        ot.set_objective("agent-1", "obj-b")
        result = ot.rollback("agent-1")
        assert result == "obj-a"
        assert ot._objectives["agent-1"] == ["obj-a"]

    def test_rollback_single_objective(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent-1", "obj-a")
        result = ot.rollback("agent-1")
        assert result == "obj-a"

    def test_rollback_empty_returns_empty(self):
        ot = ObjectiveTracker()
        result = ot.rollback("unknown")
        assert result == ""

    def test_version_tracking(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent-1", "v1")
        ot.set_objective("agent-1", "v2")
        ot.set_objective("agent-1", "v3")
        assert ot._versions["agent-1"] == 3
