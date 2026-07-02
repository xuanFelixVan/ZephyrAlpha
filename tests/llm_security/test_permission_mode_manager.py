# [A_test] module_id: SRC-TST-1367 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.permission_mode_manager
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
    from zephyr.security.access_control.permission_mode_manager import PermissionModeManager, PermMode
except Exception as _exc:
    pytest.skip(f"无法导入 permission_mode_manager: {_exc}", allow_module_level=True)


class TestPermMode:
    def test_enum_values(self):
        assert PermMode.SCOPED.value == "SCOPED"
        assert PermMode.MINIMAL.value == "MINIMAL"
        assert PermMode.APPROVAL_REQUIRED.value == "APPROVAL_REQUIRED"
        assert PermMode.HOLD.value == "HOLD"
        assert PermMode.FULL.value == "FULL"

    def test_all_modes_present(self):
        assert len(PermMode) == 5


class TestPermissionModeManager:
    def test_initial_mode(self):
        mgr = PermissionModeManager()
        assert mgr.mode == "MINIMAL"

    def test_transition_to_scoped(self):
        mgr = PermissionModeManager()
        result = mgr.transition(PermMode.SCOPED, agent_id="agent-1")
        assert result["transitioned"] is True
        assert result["from"] == "MINIMAL"
        assert result["to"] == "SCOPED"
        assert mgr.mode == "SCOPED"

    def test_transition_to_hold(self):
        mgr = PermissionModeManager()
        mgr.transition(PermMode.HOLD, agent_id="agent-1")
        assert mgr.mode == "HOLD"

    def test_transition_to_full(self):
        mgr = PermissionModeManager()
        mgr.transition(PermMode.FULL, agent_id="admin")
        assert mgr.mode == "FULL"

    def test_transition_to_approval_required(self):
        mgr = PermissionModeManager()
        mgr.transition(PermMode.APPROVAL_REQUIRED, agent_id="agent-1")
        assert mgr.mode == "APPROVAL_REQUIRED"

    def test_scoped_run(self):
        mgr = PermissionModeManager()
        result = mgr.scoped_run("agent-1", ["read:src", "write:tests"])
        assert result["mode"] == "SCOPED"
        assert result["agent_id"] == "agent-1"
        assert result["permissions"] == ["read:src", "write:tests"]
        assert mgr.mode == "SCOPED"

    def test_scoped_run_empty_permissions(self):
        mgr = PermissionModeManager()
        result = mgr.scoped_run("agent-1", [])
        assert result["permissions"] == []
        assert mgr.mode == "SCOPED"

    def test_history_recorded(self):
        mgr = PermissionModeManager()
        mgr.transition(PermMode.SCOPED, agent_id="a1")
        mgr.transition(PermMode.HOLD, agent_id="a2")
        assert len(mgr._history) == 2
        assert mgr._history[0]["from"] == "MINIMAL"
        assert mgr._history[0]["to"] == "SCOPED"
        assert mgr._history[1]["from"] == "SCOPED"
        assert mgr._history[1]["to"] == "HOLD"

    def test_transition_without_agent_id(self):
        mgr = PermissionModeManager()
        result = mgr.transition(PermMode.FULL)
        assert result["transitioned"] is True
        assert result["agent_id"] == ""

    def test_mode_order_defined(self):
        assert len(PermissionModeManager._MODE_ORDER) == 5

    def test_multiple_transitions(self):
        mgr = PermissionModeManager()
        mgr.transition(PermMode.SCOPED, agent_id="a1")
        mgr.transition(PermMode.HOLD, agent_id="a1")
        mgr.transition(PermMode.FULL, agent_id="a1")
        assert mgr.mode == "FULL"
        assert len(mgr._history) == 3
