# [A_test] module_id: MOD-GOV_skill_context_isolation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_context_isolation
# [INVARIANTS] ContextIsolation must prevent cross-skill data leakage in strict mode
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass; exit != 0 = regression
# [TESTS] tests/test_skill_context_isolation.py
# [TTL] task_bound

import copy

from zephyr.autonomy_core.skills.skill_context_isolation import ContextIsolation


class TestContextIsolationInstantiation:
    def test_default_mode_is_strict(self):
        ci = ContextIsolation()
        assert ci.isolation_level == ContextIsolation.ISOLATION_STRICT

    def test_permissive_mode(self):
        ci = ContextIsolation(mode=ContextIsolation.ISOLATION_PERMISSIVE)
        assert ci.isolation_level == "permissive"

    def test_snapshot_mode(self):
        ci = ContextIsolation(mode=ContextIsolation.ISOLATION_SNAPSHOT)
        assert ci.isolation_level == "snapshot"

    def test_internal_state_initialized(self):
        ci = ContextIsolation()
        assert ci._namespaces == {}
        assert ci._snapshots == {}
        assert ci._contamination_log == []


class TestCreateNamespace:
    def test_creates_namespace_for_new_skill(self):
        ci = ContextIsolation()
        ns_key = ci.create_namespace("skill-a")
        assert ns_key == "ns:skill-a"
        assert "ns:skill-a" in ci._namespaces

    def test_idempotent_create(self):
        ci = ContextIsolation()
        key1 = ci.create_namespace("skill-a")
        key2 = ci.create_namespace("skill-a")
        assert key1 == key2
        assert len(ci._namespaces) == 1

    def test_namespace_has_required_fields(self):
        ci = ContextIsolation()
        ci.create_namespace("skill-x")
        ns = ci._namespaces["ns:skill-x"]
        assert "skill_id" in ns
        assert "created_at" in ns
        assert "data" in ns
        assert "tokens_used" in ns
        assert "locked" in ns
        assert ns["skill_id"] == "skill-x"
        assert ns["tokens_used"] == 0
        assert ns["locked"] is False

    def test_multiple_skills_separate_namespaces(self):
        ci = ContextIsolation()
        ci.create_namespace("a")
        ci.create_namespace("b")
        assert len(ci._namespaces) == 2


class TestIsolateExecution:
    def test_basic_isolation_returns_clean_context(self):
        ci = ContextIsolation(mode="strict")
        ctx = {"key1": "value1", "key2": "value2"}
        result = ci.isolate_execution("skill-a", ctx)
        assert result["isolation_level"] == "strict"
        assert result["namespace"] == "ns:skill-a"
        assert result["context"]["key1"] == "value1"

    def test_strict_mode_removes_leaked_skill_keys(self):
        ci = ContextIsolation(mode="strict")
        ci.create_namespace("prev-skill")
        ctx = {"skill_data": "leak", "_prev-skill_secret": "leak", "safe_key": "ok"}
        result = ci.isolate_execution("skill-b", ctx, previous_skill_id="prev-skill")
        assert "skill_data" not in result["context"]
        assert "_prev-skill_secret" not in result["context"]
        assert result["context"]["safe_key"] == "ok"
        assert result["context_cleaned"] is True

    def test_strict_mode_locks_previous_namespace(self):
        ci = ContextIsolation(mode="strict")
        ci.create_namespace("prev-skill")
        ci.isolate_execution("skill-b", {}, previous_skill_id="prev-skill")
        assert ci._namespaces["ns:prev-skill"]["locked"] is True

    def test_contamination_log_recorded_on_leak(self):
        ci = ContextIsolation(mode="strict")
        ci.create_namespace("prev-skill")
        ctx = {"skill_data": "leak"}
        ci.isolate_execution("skill-b", ctx, previous_skill_id="prev-skill")
        assert len(ci._contamination_log) == 1
        assert ci._contamination_log[0]["action"] == "context_cleaned"
        assert "skill_data" in ci._contamination_log[0]["leaked_keys"]

    def test_no_previous_skill_no_cleaning(self):
        ci = ContextIsolation(mode="strict")
        ctx = {"skill_data": "leak"}
        result = ci.isolate_execution("skill-c", ctx)
        assert "skill_data" in result["context"]
        assert result["context_cleaned"] is False

    def test_permissive_mode_does_not_strip_keys(self):
        ci = ContextIsolation(mode="permissive")
        ci.create_namespace("prev-skill")
        ctx = {"skill_data": "leak", "safe_key": "ok"}
        result = ci.isolate_execution("skill-b", ctx, previous_skill_id="prev-skill")
        assert "skill_data" in result["context"]

    def test_empty_context(self):
        ci = ContextIsolation()
        result = ci.isolate_execution("skill-a", {})
        assert result["context"] == {}
        assert result["context_cleaned"] is False

    def test_original_context_not_mutated(self):
        ci = ContextIsolation(mode="strict")
        ci.create_namespace("prev-skill")
        ctx = {"skill_data": "leak", "safe": "keep"}
        original = copy.deepcopy(ctx)
        ci.isolate_execution("skill-b", ctx, previous_skill_id="prev-skill")
        assert ctx == original


class TestSnapshotRestore:
    def test_snapshot_and_restore_roundtrip(self):
        ci = ContextIsolation()
        ci.create_namespace("skill-a")
        ci._namespaces["ns:skill-a"]["data"] = {"x": 1}
        snap_id = ci.snapshot("skill-a")
        assert snap_id.startswith("snap:skill-a:")

        ci._namespaces["ns:skill-a"]["data"] = {"x": 999}
        restored = ci.restore(snap_id)
        assert restored is not None
        assert restored["data"]["x"] == 1

    def test_restore_nonexistent_snapshot_returns_none(self):
        ci = ContextIsolation()
        result = ci.restore("snap:nonexistent:12345")
        assert result is None

    def test_snapshot_of_uncreated_skill(self):
        ci = ContextIsolation()
        snap_id = ci.snapshot("never-created")
        restored = ci.restore(snap_id)
        assert restored is not None
        assert restored["skill_id"] == "never-created"

    def test_restore_creates_namespace_if_missing(self):
        ci = ContextIsolation()
        ci.create_namespace("skill-a")
        ci._namespaces["ns:skill-a"]["data"] = {"val": 42}
        snap_id = ci.snapshot("skill-a")
        del ci._namespaces["ns:skill-a"]
        restored = ci.restore(snap_id)
        assert "ns:skill-a" in ci._namespaces
        assert restored["data"]["val"] == 42


class TestCheckContamination:
    def test_clean_context_no_contamination(self):
        ci = ContextIsolation()
        ci.create_namespace("skill-a")
        result = ci.check_contamination("skill-a", {"safe_key": "ok"})
        assert result["contaminated"] is False
        assert result["foreign_keys"] == []
        assert result["contamination_count"] == 0

    def test_contaminated_context_detected(self):
        ci = ContextIsolation()
        ci.create_namespace("skill-a")
        result = ci.check_contamination("skill-a", {"skill_other_var": "leak"})
        assert result["contaminated"] is True
        assert "skill_other_var" in result["foreign_keys"]
        assert result["contamination_count"] == 1

    def test_own_skill_prefix_not_contamination(self):
        ci = ContextIsolation()
        ci.create_namespace("my-skill")
        result = ci.check_contamination("my-skill", {"skill_my_skill_data": "own"})
        assert result["contaminated"] is False

    def test_empty_context_no_contamination(self):
        ci = ContextIsolation()
        result = ci.check_contamination("skill-a", {})
        assert result["contaminated"] is False

    def test_nonexistent_skill_namespace(self):
        ci = ContextIsolation()
        result = ci.check_contamination("unknown-skill", {"skill_foreign": "leak"})
        assert result["contaminated"] is True
