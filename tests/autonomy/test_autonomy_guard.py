# [A_test] module_id: SRC-TST-0388 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_autonomy_guard
# [INVARIANTS] 3 autonomy levels; get_allowed_actions returns list; can_autonomously returns bool
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] unknown level returns empty list; can_autonomously returns False for unknown level
# [TESTS] test_autonomy_guard.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.governance.autonomy_guard import AutonomyGuard


class TestAutonomyGuard:
    @pytest.fixture()
    def guard(self):
        return AutonomyGuard()

    def test_autonomy_levels_exist(self, guard):
        assert "level1" in guard.AUTONOMY_LEVELS
        assert "level2" in guard.AUTONOMY_LEVELS
        assert "level3" in guard.AUTONOMY_LEVELS

    def test_level1_actions(self, guard):
        actions = guard.get_allowed_actions("level1")
        assert "health_check" in actions
        assert "metrics_collect" in actions
        assert "dlq_replay" in actions

    def test_level2_actions(self, guard):
        actions = guard.get_allowed_actions("level2")
        assert "auto_mitigate_p2" in actions
        assert "restart_unhealthy" in actions

    def test_level3_actions(self, guard):
        actions = guard.get_allowed_actions("level3")
        assert "rollback_deploy" in actions
        assert "repartition_data" in actions

    def test_unknown_level_returns_empty(self, guard):
        actions = guard.get_allowed_actions("level99")
        assert actions == []

    def test_can_autonomously_allowed(self, guard):
        assert guard.can_autonomously("health_check", "level1") is True
        assert guard.can_autonomously("auto_mitigate_p2", "level2") is True
        assert guard.can_autonomously("rollback_deploy", "level3") is True

    def test_can_autonomously_denied(self, guard):
        assert guard.can_autonomously("rollback_deploy", "level1") is False
        assert guard.can_autonomously("health_check", "level99") is False

    def test_can_autonomously_unknown_action(self, guard):
        assert guard.can_autonomously("nonexistent_action", "level1") is False

    def test_can_autonomously_unknown_level(self, guard):
        assert guard.can_autonomously("health_check", "unknown") is False

    def test_level_escalation_privilege(self, guard):
        level1 = guard.get_allowed_actions("level1")
        level2 = guard.get_allowed_actions("level2")
        level3 = guard.get_allowed_actions("level3")
        for action in level1:
            assert action not in level2
            assert action not in level3
        for action in level2:
            assert action not in level3

    def test_get_allowed_actions_returns_list(self, guard):
        result = guard.get_allowed_actions("level1")
        assert isinstance(result, list)
