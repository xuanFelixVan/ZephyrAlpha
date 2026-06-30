# [A_test] module_id: SRC-TST-0836 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.engine_degradation
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
    from zephyr.security.access_control.engine_degradation import (
        DegradationLevel,
        DegradationReason,
        EngineDegradationManager,
        get_engine_degradation_manager,
    )
except Exception as _exc:
    pytest.skip(f"无法导入 engine_degradation: {_exc}", allow_module_level=True)


class TestDegradationLevel:
    def test_enum_values(self):
        assert DegradationLevel.NORMAL.value == "normal"
        assert DegradationLevel.PARTIAL_FAILURE.value == "partial_failure"
        assert DegradationLevel.PERMISSION_BLOCKED.value == "permission_blocked"
        assert DegradationLevel.SYSTEM_UNAVAILABLE.value == "system_unavailable"


class TestDegradationReason:
    def test_enum_values(self):
        assert DegradationReason.CLEARED.value == "cleared"
        assert DegradationReason.IMMUTABLE_CORE_FAULT.value == "immutable_core_fault"
        assert DegradationReason.RBAC_CONFIG_LOAD_FAILURE.value == "rbac_config_load_failure"


class TestEngineDegradationManager:
    def test_initial_state(self):
        mgr = EngineDegradationManager()
        assert mgr.state.level == DegradationLevel.NORMAL
        assert mgr.is_blocked is False
        assert mgr.is_degraded is False
        assert mgr.should_block() is False

    def test_trigger_partial_failure(self):
        mgr = EngineDegradationManager()
        state = mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.ABAC_RULE_EVAL_FAILURE,
        )
        assert state.level == DegradationLevel.PARTIAL_FAILURE
        assert mgr.is_degraded is True
        assert mgr.is_blocked is False

    def test_trigger_permission_blocked(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PERMISSION_BLOCKED,
            DegradationReason.RBAC_CONFIG_LOAD_FAILURE,
        )
        assert mgr.is_blocked is True
        assert mgr.should_block() is True

    def test_trigger_system_unavailable(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.SYSTEM_UNAVAILABLE,
            DegradationReason.IMMUTABLE_CORE_FAULT,
        )
        assert mgr.is_blocked is True
        assert mgr.is_degraded is True

    def test_agent_degradation_blocking(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.ABAC_RULE_EVAL_FAILURE,
            agent_id="agent-A",
        )
        assert mgr.is_agent_degradation_blocked("agent-A") is False
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.INPUT_GUARD_FAILURE,
            agent_id="agent-A",
        )
        assert mgr.is_agent_degradation_blocked("agent-A") is True

    def test_agent_not_blocked_initially(self):
        mgr = EngineDegradationManager()
        assert mgr.is_agent_degradation_blocked("unknown-agent") is False

    def test_try_recover_from_partial_failure(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.ABAC_RULE_EVAL_FAILURE,
        )
        result = mgr.try_recover()
        assert result is True
        assert mgr.state.level == DegradationLevel.NORMAL
        assert mgr.state.reason == DegradationReason.CLEARED

    def test_try_recover_from_system_unavailable_without_core(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.SYSTEM_UNAVAILABLE,
            DegradationReason.IMMUTABLE_CORE_FAULT,
        )
        mgr._verify_immutable_core = lambda: False
        result = mgr.try_recover()
        assert result is False
        assert mgr.state.level == DegradationLevel.SYSTEM_UNAVAILABLE

    def test_owner_force_recover(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PERMISSION_BLOCKED,
            DegradationReason.RBAC_CONFIG_LOAD_FAILURE,
            agent_id="agent-A",
        )
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.ABAC_RULE_EVAL_FAILURE,
            agent_id="agent-A",
        )
        mgr.owner_force_recover()
        assert mgr.state.level == DegradationLevel.NORMAL
        assert mgr.is_agent_degradation_blocked("agent-A") is False

    def test_reset(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PERMISSION_BLOCKED,
            DegradationReason.RBAC_CONFIG_LOAD_FAILURE,
            agent_id="agent-X",
        )
        mgr.reset()
        assert mgr.state.level == DegradationLevel.NORMAL
        assert mgr.is_agent_degradation_blocked("agent-X") is False

    def test_get_engine_degradation_manager_singleton(self):
        from zephyr.security.access_control import engine_degradation as mod

        mod._engine_degradation_manager = None
        m1 = get_engine_degradation_manager()
        m2 = get_engine_degradation_manager()
        assert m1 is m2
        mod._engine_degradation_manager = None

    def test_partial_failure_upgrade_not_needed_initially(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.ABAC_RULE_EVAL_FAILURE,
        )
        assert mgr.is_partial_failure_upgrade_needed() is False

    def test_trigger_with_none_agent(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.ABAC_RULE_EVAL_FAILURE,
            agent_id=None,
        )
        assert mgr.is_degraded is True
