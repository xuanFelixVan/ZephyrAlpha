# [A_test] module_id: SRC-TST-1316 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.novel_attack_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.guards.novel_attack_guard import NovelAttackGuard

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestNovelAttackGuard:
    def setup_method(self):
        self.guard = NovelAttackGuard()

    def test_profile_action_normal(self):
        result = self.guard.profile_action("agent-1", "read")
        assert result["suspicion_score"] == 0.0
        assert result["suspicious"] is False

    def test_profile_action_novel(self):
        result = self.guard.profile_action("agent-1", "exploit_buffer_overflow")
        assert result["suspicion_score"] > 0.0
        assert result["suspicious"] is False

    def test_profile_action_suspicious_threshold(self):
        self.guard.profile_action("agent-1", "novel_1")
        self.guard.profile_action("agent-1", "novel_2")
        self.guard.profile_action("agent-1", "novel_3")
        self.guard.profile_action("agent-1", "novel_4")
        result = self.guard.profile_action("agent-1", "novel_5")
        assert result["suspicious"] is True
        assert result["suspicion_score"] >= 2.0

    def test_profile_action_max_suspicion_cap(self):
        for i in range(20):
            self.guard.profile_action("agent-1", f"novel_{i}")
        result = self.guard.profile_action("agent-1", "novel_20")
        assert result["suspicion_score"] <= 5.0

    def test_profile_action_different_agents_independent(self):
        self.guard.profile_action("agent-1", "novel_action")
        result2 = self.guard.profile_action("agent-2", "read")
        assert result2["suspicion_score"] == 0.0

    def test_normal_patterns_not_suspicious(self):
        for action in ("read", "write", "execute", "query", "list", "get", "check"):
            guard = NovelAttackGuard()
            result = guard.profile_action("agent-1", action)
            assert result["suspicion_score"] == 0.0

    def test_profile_created_on_first_action(self):
        result = self.guard.profile_action("new-agent", "read")
        assert "new-agent" in self.guard._profiles
        assert self.guard._profiles["new-agent"].normal_action_count == 1

    def test_empty_agent_id(self):
        result = self.guard.profile_action("", "read")
        assert result["agent_id"] == ""
