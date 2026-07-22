# [A_test] module_id: MOD-GOV_objective_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_objective_tracker
# [INVARIANTS] 目标漂移检测不可跳过;余弦相似度阈值不可手动覆盖
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_objective_tracker.py
# [TTL] task_bound

from zephyr.governance.observability_governance.objective_tracker import ObjectiveTracker


class TestObjectiveTrackerInit:
    def test_instantiation(self):
        ot = ObjectiveTracker()
        assert ot._objectives == {}
        assert ot._versions == {}

    def test_multiple_instances_independent(self):
        ot1 = ObjectiveTracker()
        ot2 = ObjectiveTracker()
        ot1.set_objective("agent_a", "obj1")
        assert "agent_a" not in ot2._objectives


class TestSetObjective:
    def test_set_first_objective(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "optimize latency")
        assert ot._objectives["agent_1"] == ["optimize latency"]
        assert ot._versions["agent_1"] == 1

    def test_set_multiple_objectives_same_agent(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "obj_a")
        ot.set_objective("agent_1", "obj_b")
        assert ot._objectives["agent_1"] == ["obj_a", "obj_b"]
        assert ot._versions["agent_1"] == 2

    def test_set_objectives_different_agents(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "obj_a")
        ot.set_objective("agent_2", "obj_b")
        assert ot._objectives["agent_1"] == ["obj_a"]
        assert ot._objectives["agent_2"] == ["obj_b"]
        assert ot._versions["agent_1"] == 1
        assert ot._versions["agent_2"] == 1

    def test_version_increments_per_set(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "v1")
        ot.set_objective("agent_1", "v2")
        ot.set_objective("agent_1", "v3")
        assert ot._versions["agent_1"] == 3


class TestDetectDrift:
    def test_no_drift_single_objective(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "obj_a")
        assert ot.detect_drift("agent_1") is False

    def test_drift_detected_with_multiple_objectives(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "obj_a")
        ot.set_objective("agent_1", "obj_b")
        assert ot.detect_drift("agent_1") is True

    def test_no_drift_unknown_agent(self):
        ot = ObjectiveTracker()
        assert ot.detect_drift("unknown_agent") is False

    def test_drift_after_rollback_to_single(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "obj_a")
        ot.set_objective("agent_1", "obj_b")
        ot.rollback("agent_1")
        assert ot.detect_drift("agent_1") is False


class TestRollback:
    def test_rollback_removes_last_objective(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "obj_a")
        ot.set_objective("agent_1", "obj_b")
        result = ot.rollback("agent_1")
        assert result == "obj_a"
        assert ot._objectives["agent_1"] == ["obj_a"]

    def test_rollback_decrements_version(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "obj_a")
        ot.set_objective("agent_1", "obj_b")
        ot.rollback("agent_1")
        assert ot._versions["agent_1"] == 1

    def test_rollback_single_objective_returns_same(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "obj_a")
        result = ot.rollback("agent_1")
        assert result == "obj_a"
        assert ot._objectives["agent_1"] == ["obj_a"]

    def test_rollback_unknown_agent_returns_empty(self):
        ot = ObjectiveTracker()
        result = ot.rollback("unknown_agent")
        assert result == ""

    def test_rollback_multiple_times(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "v1")
        ot.set_objective("agent_1", "v2")
        ot.set_objective("agent_1", "v3")
        assert ot.rollback("agent_1") == "v2"
        assert ot.rollback("agent_1") == "v1"
        assert ot._versions["agent_1"] == 1

    def test_rollback_version_stays_at_one_for_single_obj(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "obj_a")
        ot.rollback("agent_1")
        ot.rollback("agent_1")
        assert ot._versions["agent_1"] == 1


class TestBoundary:
    def test_empty_objective_string(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "")
        assert ot._objectives["agent_1"] == [""]
        assert ot.detect_drift("agent_1") is False

    def test_none_agent_id_accepted_as_key(self):
        ot = ObjectiveTracker()
        ot.set_objective(None, "obj")
        assert ot._objectives[None] == ["obj"]

    def test_unicode_objective(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "优化延迟")
        assert ot._objectives["agent_1"] == ["优化延迟"]

    def test_very_long_objective(self):
        ot = ObjectiveTracker()
        long_obj = "x" * 10000
        ot.set_objective("agent_1", long_obj)
        assert ot._objectives["agent_1"] == [long_obj]

    def test_duplicate_objectives_count_as_drift(self):
        ot = ObjectiveTracker()
        ot.set_objective("agent_1", "same")
        ot.set_objective("agent_1", "same")
        assert ot.detect_drift("agent_1") is True
