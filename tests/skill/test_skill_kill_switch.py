# [A_test] module_id: MOD-GOV_skill_kill_switch | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_kill_switch
# [INVARIANTS] must clear class-level _killed dict between tests; is_killed depends on cooldown timing
# [MODIFY-GUARD] skill_kill_switch.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] all tests must pass independently; class state cleared in fixture
# [TESTS] pytest tests/test_skill_kill_switch.py -q
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

from zephyr.autonomy_core.skills.skill_kill_switch import SkillKillSwitch
from zephyr.autonomy_core.skills.skill_model import SkillStatus


@pytest.fixture(autouse=True)
def _clean_killed():
    SkillKillSwitch.clear_all()
    yield
    SkillKillSwitch.clear_all()


class TestSkillKillSwitchInstantiation:
    def test_class_has_killed_dict(self):
        assert hasattr(SkillKillSwitch, "_killed")
        assert isinstance(SkillKillSwitch.killed, dict)

    def test_class_has_fail_threshold(self):
        assert SkillKillSwitch._FAIL_THRESHOLD == 3

    def test_class_has_cooldown(self):
        assert SkillKillSwitch._COOLDOWN_S == 300.0

    def test_fresh_state_empty(self):
        assert SkillKillSwitch.killed == {}


class TestKill:
    def test_kill_adds_to_killed(self):
        result = SkillKillSwitch.kill("sk-1", "test reason")
        assert result["action"] == "killed"
        assert result["skill_id"] == "sk-1"
        assert result["status"] == SkillStatus.DEPRECATED.value
        assert "sk-1" in SkillKillSwitch.killed

    def test_kill_with_manual_trigger(self):
        result = SkillKillSwitch.kill("sk-2", "manual kill", trigger="manual")
        assert result["trigger"] == "manual"

    def test_kill_with_circuit_breaker_trigger(self):
        result = SkillKillSwitch.kill("sk-3", "auto", trigger="circuit_breaker")
        assert result["trigger"] == "circuit_breaker"

    def test_kill_default_trigger_is_manual(self):
        result = SkillKillSwitch.kill("sk-4", "reason")
        assert result["trigger"] == "manual"

    def test_kill_overwrites_previous(self):
        SkillKillSwitch.kill("sk-5", "first")
        result = SkillKillSwitch.kill("sk-5", "second")
        assert result["reason"] == "second"

    def test_kill_records_timestamp(self):
        before = time.time()
        SkillKillSwitch.kill("sk-6", "reason")
        after = time.time()
        entry = SkillKillSwitch.killed["sk-6"]
        assert before <= entry["killed_at"] <= after


class TestRevive:
    def test_revive_removes_from_killed(self):
        SkillKillSwitch.kill("sk-1", "reason")
        result = SkillKillSwitch.revive("sk-1")
        assert result["action"] == "revived"
        assert result["status"] == SkillStatus.ACTIVE.value
        assert "sk-1" not in SkillKillSwitch.killed

    def test_revive_not_killed_skill(self):
        result = SkillKillSwitch.revive("sk-unknown")
        assert result["action"] == "not_killed"

    def test_revive_after_kill_restores_active(self):
        SkillKillSwitch.kill("sk-2", "error")
        result = SkillKillSwitch.revive("sk-2")
        assert result["status"] == SkillStatus.ACTIVE.value


class TestIsKilled:
    def test_killed_skill_is_killed(self):
        SkillKillSwitch.kill("sk-1", "reason")
        assert SkillKillSwitch.is_killed("sk-1") is True

    def test_unknown_skill_not_killed(self):
        assert SkillKillSwitch.is_killed("sk-unknown") is False

    def test_revived_skill_not_killed(self):
        SkillKillSwitch.kill("sk-2", "reason")
        SkillKillSwitch.revive("sk-2")
        assert SkillKillSwitch.is_killed("sk-2") is False

    def test_expired_cooldown_not_killed(self):
        SkillKillSwitch.kill("sk-3", "reason")
        SkillKillSwitch.killed["sk-3"]["killed_at"] = time.time() - 600
        assert SkillKillSwitch.is_killed("sk-3") is False


class TestAutoKillOnErrors:
    def test_below_threshold_returns_none(self):
        result = SkillKillSwitch.auto_kill_on_errors("sk-1", error_count=2)
        assert result is None

    def test_at_threshold_kills(self):
        result = SkillKillSwitch.auto_kill_on_errors("sk-2", error_count=3)
        assert result is not None
        assert result["action"] == "killed"
        assert result["trigger"] == "circuit_breaker"

    def test_above_threshold_kills(self):
        result = SkillKillSwitch.auto_kill_on_errors("sk-3", error_count=10)
        assert result is not None
        assert result["action"] == "killed"

    def test_zero_errors_returns_none(self):
        result = SkillKillSwitch.auto_kill_on_errors("sk-4", error_count=0)
        assert result is None

    def test_auto_kill_reason_contains_threshold(self):
        result = SkillKillSwitch.auto_kill_on_errors("sk-5", error_count=5)
        assert "5 consecutive errors" in result["reason"]
        assert str(SkillKillSwitch._FAIL_THRESHOLD) in result["reason"]


class TestListKilled:
    def test_empty_when_none_killed(self):
        result = SkillKillSwitch.list_killed()
        assert result == []

    def test_lists_killed_skills(self):
        SkillKillSwitch.kill("sk-a", "reason a")
        SkillKillSwitch.kill("sk-b", "reason b")
        result = SkillKillSwitch.list_killed()
        skill_ids = [e["skill_id"] for e in result]
        assert "sk-a" in skill_ids
        assert "sk-b" in skill_ids

    def test_excludes_expired(self):
        SkillKillSwitch.kill("sk-old", "old")
        SkillKillSwitch.killed["sk-old"]["killed_at"] = time.time() - 600
        result = SkillKillSwitch.list_killed()
        skill_ids = [e["skill_id"] for e in result]
        assert "sk-old" not in skill_ids

    def test_includes_fresh_killed(self):
        SkillKillSwitch.kill("sk-fresh", "fresh")
        result = SkillKillSwitch.list_killed()
        assert len(result) >= 1
        assert result[0]["skill_id"] == "sk-fresh"


class TestClearAll:
    def test_clear_all_empties_killed(self):
        SkillKillSwitch.kill("sk-1", "r1")
        SkillKillSwitch.kill("sk-2", "r2")
        SkillKillSwitch.clear_all()
        assert SkillKillSwitch.killed == {}
