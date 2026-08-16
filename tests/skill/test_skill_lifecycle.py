# [A_test] module_id: MOD-GOV_skill_lifecycle | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_lifecycle
# [INVARIANTS] SkillLifecycle transitions must respect guards
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] guard rejection returns allowed=False
# [TESTS] tests/test_skill_lifecycle.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_lifecycle import SkillLifecycle, Transition
from zephyr.autonomy_core.skills.skill_model import SkillStatus


class TestTransitionInstantiation:
    def test_transition_creation(self):
        t = Transition("draft", "active", "approved")
        assert t.from_status == "draft"
        assert t.to_status == "active"
        assert t.reason == "approved"
        assert isinstance(t.timestamp, float)

    def test_transition_custom_timestamp(self):
        t = Transition("draft", "active", "test", timestamp=1000.0)
        assert t.timestamp == 1000.0

    def test_transition_to_dict(self):
        t = Transition("draft", "active", "test", timestamp=1000.0)
        d = t.to_dict()
        assert d["from"] == "draft"
        assert d["to"] == "active"
        assert d["reason"] == "test"
        assert d["timestamp"] == 1000.0


class TestSkillLifecycleInstantiation:
    def test_default_instantiation(self):
        lc = SkillLifecycle()
        assert isinstance(lc.states, dict)
        assert isinstance(lc.guards, dict)
        assert callable(lc.history)
        assert len(lc.states) == 0

    def test_register_default_active(self):
        lc = SkillLifecycle()
        lc.register("skill-1")
        assert lc.current_status("skill-1") == SkillStatus.ACTIVE.value

    def test_register_custom_status(self):
        lc = SkillLifecycle()
        lc.register("skill-2", SkillStatus.DRAFT.value)
        assert lc.current_status("skill-2") == SkillStatus.DRAFT.value

    def test_current_status_unregistered_is_draft(self):
        lc = SkillLifecycle()
        assert lc.current_status("unknown") == SkillStatus.DRAFT.value


class TestTransition:
    def test_valid_transition_draft_to_active(self):
        lc = SkillLifecycle()
        lc.register("s1", SkillStatus.DRAFT.value)
        result = lc.transition("s1", SkillStatus.ACTIVE.value, "approved")
        assert result["allowed"] is True
        assert result["from"] == SkillStatus.DRAFT.value
        assert result["to"] == SkillStatus.ACTIVE.value

    def test_valid_transition_active_to_deprecated(self):
        lc = SkillLifecycle()
        lc.register("s2", SkillStatus.ACTIVE.value)
        result = lc.transition("s2", SkillStatus.DEPRECATED.value, "obsolete")
        assert result["allowed"] is True

    def test_transition_records_history(self):
        lc = SkillLifecycle()
        lc.register("s3", SkillStatus.DRAFT.value)
        lc.transition("s3", SkillStatus.ACTIVE.value, "go")
        hist = lc.history("s3")
        assert len(hist) == 1
        assert hist[0]["from"] == SkillStatus.DRAFT.value

    def test_guard_rejects_transition(self):
        lc = SkillLifecycle()
        lc.register("s4", SkillStatus.DRAFT.value)
        lc.add_guard("s4", lambda sid, to: False)
        result = lc.transition("s4", SkillStatus.ACTIVE.value, "blocked")
        assert result["allowed"] is False
        assert "Guard" in result["reason"]

    def test_guard_allows_transition(self):
        lc = SkillLifecycle()
        lc.register("s5", SkillStatus.DRAFT.value)
        lc.add_guard("s5", lambda sid, to: True)
        result = lc.transition("s5", SkillStatus.ACTIVE.value, "allowed")
        assert result["allowed"] is True

    def test_unregistered_skill_transitions_from_draft(self):
        lc = SkillLifecycle()
        result = lc.transition("new-skill", SkillStatus.ACTIVE.value, "auto")
        assert result["from"] == SkillStatus.DRAFT.value


class TestHistory:
    def test_history_empty(self):
        lc = SkillLifecycle()
        assert lc.history("unknown") == []

    def test_history_limit(self):
        lc = SkillLifecycle()
        lc.register("s6", SkillStatus.DRAFT.value)
        for i in range(25):
            lc.transition("s6", SkillStatus.ACTIVE.value if i % 2 == 0 else SkillStatus.DRAFT.value, f"step-{i}")
        hist = lc.history("s6", limit=5)
        assert len(hist) <= 5


class TestRollback:
    def test_rollback_insufficient_history(self):
        lc = SkillLifecycle()
        lc.register("s7", SkillStatus.DRAFT.value)
        result = lc.rollback("s7")
        assert result["rolled_back"] is False

    def test_rollback_with_history(self):
        lc = SkillLifecycle()
        lc.register("s8", SkillStatus.DRAFT.value)
        lc.transition("s8", SkillStatus.ACTIVE.value, "promote")
        lc.transition("s8", SkillStatus.DEPRECATED.value, "deprecate")
        result = lc.rollback("s8")
        assert result["allowed"] is True

    def test_rollback_no_history_for_unknown(self):
        lc = SkillLifecycle()
        result = lc.rollback("unknown")
        assert result["rolled_back"] is False


class TestBatchTransition:
    def test_batch_transition(self):
        lc = SkillLifecycle()
        lc.register("b1", SkillStatus.DRAFT.value)
        lc.register("b2", SkillStatus.DRAFT.value)
        result = lc.batch_transition(["b1", "b2"], SkillStatus.ACTIVE.value, "batch")
        assert result["total"] == 2
        assert result["succeeded"] == 2

    def test_batch_transition_empty_list(self):
        lc = SkillLifecycle()
        result = lc.batch_transition([], SkillStatus.ACTIVE.value, "empty")
        assert result["total"] == 0
        assert result["succeeded"] == 0


class TestAllStatuses:
    def test_all_statuses(self):
        lc = SkillLifecycle()
        lc.register("a1", SkillStatus.DRAFT.value)
        lc.register("a2", SkillStatus.ACTIVE.value)
        statuses = lc.all_statuses()
        assert statuses["a1"] == SkillStatus.DRAFT.value
        assert statuses["a2"] == SkillStatus.ACTIVE.value
        assert len(statuses) == 2
