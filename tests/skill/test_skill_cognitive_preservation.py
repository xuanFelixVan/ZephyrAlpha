# [A_test] module_id: MOD-GOV_skill_cognitive_preservation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_cognitive_preservation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_cognitive_preservation.py
# [TTL] task_bound

from __future__ import annotations

import time
from unittest.mock import patch

from zephyr.autonomy_core.skills.skill_cognitive_preservation import (
    CognitiveSnapshot,
    SkillCognitivePreservation,
)


class TestCognitiveSnapshotInit:
    def test_instantiation_with_timestamp(self):
        ts = 1700000000.0
        snap = CognitiveSnapshot(skill_id="sk-1", state={"key": "val"}, timestamp=ts)
        assert snap.skill_id == "sk-1"
        assert snap.state == {"key": "val"}
        assert snap.timestamp == ts

    def test_instantiation_without_timestamp_uses_current_time(self):
        before = time.time()
        snap = CognitiveSnapshot(skill_id="sk-2", state={"a": 1})
        after = time.time()
        assert before <= snap.timestamp <= after

    def test_version_from_state(self):
        snap = CognitiveSnapshot(skill_id="sk-3", state={"_version": 5})
        assert snap.version == 5

    def test_version_defaults_to_one(self):
        snap = CognitiveSnapshot(skill_id="sk-4", state={})
        assert snap.version == 1

    def test_to_dict(self):
        ts = 1700000000.0
        snap = CognitiveSnapshot(skill_id="sk-5", state={"x": 10, "_version": 2}, timestamp=ts)
        d = snap.to_dict()
        assert d["skill_id"] == "sk-5"
        assert d["state"] == {"x": 10, "_version": 2}
        assert d["timestamp"] == ts
        assert d["version"] == 2


class TestSkillCognitivePreservationInit:
    def test_instantiation_creates_empty_memory(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
            assert scp.memory == {}

    def test_max_snapshots_constant(self):
        assert SkillCognitivePreservation.MAX_SNAPSHOTS_PER_SKILL == 20


class TestSave:
    def test_save_returns_version_and_persisted(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            result = scp.save("sk-a", {"data": "hello"})
        assert result["skill_id"] == "sk-a"
        assert result["version"] == 1
        assert result["persisted"] is True

    def test_save_increments_version_when_state_carries_version(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            r1 = scp.save("sk-b", {"data": "first"})
            saved_state = scp.memory["sk-b"].state
            r2 = scp.save("sk-b", dict(saved_state, data="second"))
        assert r1["version"] == 1
        assert r2["version"] == 2

    def test_save_with_existing_version_increments(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            result = scp.save("sk-c", {"_version": 3, "data": "x"})
        assert result["version"] == 4

    def test_save_empty_state(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            result = scp.save("sk-d", {})
        assert result["persisted"] is True
        assert result["version"] == 1

    def test_save_stores_in_memory(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            scp.save("sk-e", {"val": 42})
        assert "sk-e" in scp.memory
        assert scp.memory["sk-e"].state["val"] == 42


class TestRestore:
    def test_restore_existing_skill(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            scp.save("sk-f", {"data": "hello"})
        result = scp.restore("sk-f")
        assert result["found"] is True
        assert result["skill_id"] == "sk-f"
        assert result["state"]["data"] == "hello"

    def test_restore_nonexistent_skill(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        result = scp.restore("nonexistent")
        assert result["found"] is False
        assert result["state"] == {}

    def test_restore_returns_version(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            scp.save("sk-g", {"data": "v1"})
            saved_state = scp.memory["sk-g"].state
            scp.save("sk-g", dict(saved_state, data="v2"))
        result = scp.restore("sk-g")
        assert result["version"] == 2


class TestMerge:
    def test_merge_into_existing(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            scp.save("sk-h", {"a": 1, "b": 2})
            result = scp.merge("sk-h", {"b": 99, "c": 3})
        assert result["persisted"] is True
        state = scp.memory["sk-h"].state
        assert state["a"] == 1
        assert state["b"] == 99
        assert state["c"] == 3

    def test_merge_into_nonexistent_creates_new(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            result = scp.merge("sk-i", {"x": 10})
        assert result["persisted"] is True
        assert scp.memory["sk-i"].state["x"] == 10

    def test_merge_empty_delta(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            scp.save("sk-j", {"a": 1})
            result = scp.merge("sk-j", {})
        assert result["persisted"] is True
        assert scp.memory["sk-j"].state["a"] == 1


class TestListSkills:
    def test_list_skills_empty(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        assert scp.list_skills() == []

    def test_list_skills_returns_saved(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            scp.save("sk-k", {"data": "a"})
            scp.save("sk-l", {"data": "b"})
        skills = scp.list_skills()
        ids = [s["skill_id"] for s in skills]
        assert "sk-k" in ids
        assert "sk-l" in ids


class TestWarmResumeContext:
    def test_warm_resume_with_existing_skill(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            scp.save("sk-m", {"key1": "value1"})
        ctx = scp.warm_resume_context(["sk-m"])
        assert "sk-m" in ctx
        assert "key1" in ctx

    def test_warm_resume_with_nonexistent_skill(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        ctx = scp.warm_resume_context(["nonexistent"])
        assert ctx == ""

    def test_warm_resume_empty_list(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        ctx = scp.warm_resume_context([])
        assert ctx == ""

    def test_warm_resume_skips_internal_keys(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            scp.save("sk-n", {"public_key": "visible", "_version": 5, "_saved_at": 123})
        ctx = scp.warm_resume_context(["sk-n"])
        assert "public_key" in ctx
        assert "_version" not in ctx
        assert "_saved_at" not in ctx


class TestForget:
    def test_forget_removes_skill(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "persist_snapshot"), patch.object(scp, "prune_old_snapshots"):
            scp.save("sk-o", {"data": "x"})
        with patch.object(scp, "delete_snapshots"):
            scp.forget("sk-o")
        assert "sk-o" not in scp.memory

    def test_forget_nonexistent_no_error(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "delete_snapshots"):
            scp.forget("nonexistent")

    def test_forget_empty_skill_id(self):
        with patch.object(SkillCognitivePreservation, "load_all"):
            scp = SkillCognitivePreservation()
        with patch.object(scp, "delete_snapshots"):
            scp.forget("")
