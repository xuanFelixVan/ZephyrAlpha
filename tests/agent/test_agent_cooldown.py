# [A_test] module_id: MOD-GOV_agent_cooldown | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_agent_cooldown
# [INVARIANTS] cooldown DB isolated per test via tmp_path
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.rollback.agent_cooldown import AgentCooldown, CooldownCheck, CooldownEntry


class TestCooldownEntry:
    def test_instantiation(self):
        entry = CooldownEntry(
            agent_session="sess-1",
            file_path="a.py",
            cooldown_until="2026-01-01T00:05:00+00:00",
            reason="post_rollback_cooldown",
        )
        assert entry.agent_session == "sess-1"
        assert entry.file_path == "a.py"
        assert entry.reason == "post_rollback_cooldown"

    def test_default_reason_field(self):
        entry = CooldownEntry(agent_session="s", file_path="f", cooldown_until="t", reason="")
        assert entry.reason == ""


class TestCooldownCheck:
    def test_allowed_when_no_blocked(self):
        cc = CooldownCheck(allowed=True, blocked_files=[], cooldown_remaining_seconds={})
        assert cc.allowed is True
        assert cc.blocked_files == []

    def test_not_allowed_when_blocked(self):
        cc = CooldownCheck(allowed=False, blocked_files=["x.py"], cooldown_remaining_seconds={"x.py": 120})
        assert cc.allowed is False
        assert "x.py" in cc.blocked_files


class TestAgentCooldownInstantiation:
    def test_creates_db_dir(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        db_dir = tmp_path / ".zephyr"
        assert db_dir.exists()

    def test_db_file_created(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        db_path = tmp_path / ".zephyr" / "rollback_quarantine.db"
        assert db_path.exists()

    def test_default_project_root(self):
        ac = AgentCooldown()
        assert ac._project_root == Path.cwd()


class TestAgentCooldownQuarantine:
    def test_quarantine_single_file(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        entries = ac.quarantine("sess-1", ["src/main.py"])
        assert len(entries) == 1
        assert entries[0].agent_session == "sess-1"
        assert entries[0].file_path == "src/main.py"
        assert entries[0].reason == "post_rollback_cooldown"

    def test_quarantine_multiple_files(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        entries = ac.quarantine("sess-1", ["a.py", "b.py", "c.py"])
        assert len(entries) == 3
        paths = {e.file_path for e in entries}
        assert paths == {"a.py", "b.py", "c.py"}

    def test_quarantine_custom_reason(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        entries = ac.quarantine("sess-1", ["x.py"], reason="manual_block")
        assert entries[0].reason == "manual_block"

    def test_quarantine_empty_file_list(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        entries = ac.quarantine("sess-1", [])
        assert entries == []


class TestAgentCooldownCheck:
    def test_check_blocked_after_quarantine(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["locked.py"])
        result = ac.check("sess-1", ["locked.py"])
        assert result.allowed is False
        assert "locked.py" in result.blocked_files

    def test_check_allowed_for_unrelated_session(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["locked.py"])
        result = ac.check("sess-2", ["locked.py"])
        assert result.allowed is True

    def test_check_allowed_for_unrelated_file(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["locked.py"])
        result = ac.check("sess-1", ["other.py"])
        assert result.allowed is True

    def test_check_empty_file_list(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        result = ac.check("sess-1", [])
        assert result.allowed is True
        assert result.blocked_files == []

    def test_check_cooldown_remaining_seconds(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py"])
        result = ac.check("sess-1", ["a.py"])
        assert "a.py" in result.cooldown_remaining_seconds
        assert result.cooldown_remaining_seconds["a.py"] > 0


class TestAgentCooldownIsQuarantined:
    def test_is_quarantined_true(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py"])
        assert ac.is_quarantined("sess-1", "a.py") is True

    def test_is_quarantined_false(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py"])
        assert ac.is_quarantined("sess-1", "b.py") is False

    def test_is_quarantined_different_session(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py"])
        assert ac.is_quarantined("sess-2", "a.py") is False


class TestAgentCooldownLiftQuarantine:
    def test_lift_specific_files(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py", "b.py"])
        count = ac.lift_quarantine("sess-1", ["a.py"])
        assert count == 1
        assert ac.is_quarantined("sess-1", "a.py") is False
        assert ac.is_quarantined("sess-1", "b.py") is True

    def test_lift_all_for_session(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py", "b.py", "c.py"])
        count = ac.lift_quarantine("sess-1")
        assert count == 3
        assert ac.is_quarantined("sess-1", "a.py") is False

    def test_lift_nonexistent_returns_zero(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        count = ac.lift_quarantine("ghost-session", ["x.py"])
        assert count == 0

    def test_lift_empty_file_list_removes_all(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py"])
        count = ac.lift_quarantine("sess-1", [])
        assert count == 1


class TestAgentCooldownGetActiveQuarantines:
    def test_get_active_after_quarantine(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py", "b.py"])
        active = ac.get_active_quarantines("sess-1")
        assert len(active) == 2
        paths = {e.file_path for e in active}
        assert paths == {"a.py", "b.py"}

    def test_get_active_empty(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        active = ac.get_active_quarantines("sess-1")
        assert active == []

    def test_get_active_after_lift(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py"])
        ac.lift_quarantine("sess-1", ["a.py"])
        active = ac.get_active_quarantines("sess-1")
        assert active == []

    def test_get_active_isolates_sessions(self, tmp_path):
        ac = AgentCooldown(project_root=tmp_path)
        ac.quarantine("sess-1", ["a.py"])
        ac.quarantine("sess-2", ["b.py"])
        active1 = ac.get_active_quarantines("sess-1")
        active2 = ac.get_active_quarantines("sess-2")
        assert len(active1) == 1
        assert len(active2) == 1
        assert active1[0].file_path == "a.py"
        assert active2[0].file_path == "b.py"
