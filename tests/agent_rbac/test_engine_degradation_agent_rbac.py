# [A_test] module_id: MOD-GOV_engine_degradation_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_engine_degradation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试 L0 EngineDegradation — 权限引擎降级策略

覆盖:
  - 崩=blocked 原则
  - 降级源检测（同一Agent触发>=2次→BLOCKED）
  - PartialFailure > 3600s → P0升级
  - 恢复流程 + 完整性验证
  - Owner手动恢复
"""

from zephyr.security.access_control.engine_degradation import (
    DegradationLevel,
    DegradationReason,
    EngineDegradationManager,
    get_engine_degradation_manager,
)


class TestInitialState:
    def test_initial_state_is_normal(self):
        mgr = EngineDegradationManager()
        assert mgr.state.level == DegradationLevel.NORMAL
        assert not mgr.is_blocked
        assert not mgr.is_degraded
        assert not mgr.should_block()


class TestDegradationTrigger:
    def test_immutable_core_fault_triggers_system_unavailable(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.SYSTEM_UNAVAILABLE,
            DegradationReason.IMMUTABLE_CORE_FAULT,
        )
        assert mgr.state.level == DegradationLevel.SYSTEM_UNAVAILABLE
        assert mgr.is_blocked
        assert mgr.should_block()

    def test_rbac_failure_triggers_permission_blocked(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PERMISSION_BLOCKED,
            DegradationReason.RBAC_CONFIG_LOAD_FAILURE,
        )
        assert mgr.state.level == DegradationLevel.PERMISSION_BLOCKED
        assert mgr.is_blocked
        assert mgr.should_block()

    def test_partial_failure_records_start_time(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.ABAC_RULE_EVAL_FAILURE,
        )
        assert mgr.state.level == DegradationLevel.PARTIAL_FAILURE
        assert mgr.state.partial_failure_start is not None
        assert not mgr.is_blocked
        assert mgr.is_degraded


class TestDegradationAttackDetection:
    def test_agent_under_threshold_not_blocked(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.ABAC_RULE_EVAL_FAILURE,
            agent_id="agent-safe",
        )
        assert not mgr.is_agent_degradation_blocked("agent-safe")

    def test_agent_reaches_threshold_blocked(self):
        mgr = EngineDegradationManager()
        for i in range(2):
            mgr.trigger_degradation(
                DegradationLevel.PARTIAL_FAILURE,
                DegradationReason.ABAC_RULE_EVAL_FAILURE,
                agent_id="agent-malicious",
            )
        assert mgr.is_agent_degradation_blocked("agent-malicious")

    def test_agent_not_in_records_returns_false(self):
        mgr = EngineDegradationManager()
        assert not mgr.is_agent_degradation_blocked("nonexistent-agent")

    def test_degration_source_is_tracked(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.INPUT_GUARD_FAILURE,
            agent_id="agent-tracked",
        )
        assert mgr.state.triggered_by_agent == "agent-tracked"


class TestPartialFailureUpgrade:
    def test_partial_failure_not_expired_no_upgrade(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PARTIAL_FAILURE,
            DegradationReason.ABAC_RULE_EVAL_FAILURE,
        )
        assert not mgr.is_partial_failure_upgrade_needed()
        assert mgr.state.level == DegradationLevel.PARTIAL_FAILURE


class TestRecovery:
    def test_owner_force_recover(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.SYSTEM_UNAVAILABLE,
            DegradationReason.IMMUTABLE_CORE_FAULT,
        )
        assert mgr.is_blocked
        mgr.owner_force_recover()
        assert not mgr.is_blocked
        assert mgr.state.level == DegradationLevel.NORMAL

    def test_try_recover_from_blocked_without_core_verification(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.PERMISSION_BLOCKED,
            DegradationReason.RBAC_CONFIG_LOAD_FAILURE,
        )
        recovered = mgr.try_recover()
        assert recovered
        assert not mgr.is_blocked


class TestReset:
    def test_reset_clears_everything(self):
        mgr = EngineDegradationManager()
        mgr.trigger_degradation(
            DegradationLevel.SYSTEM_UNAVAILABLE,
            DegradationReason.IMMUTABLE_CORE_FAULT,
            agent_id="agent-dirty",
        )
        mgr.reset()
        assert mgr.state.level == DegradationLevel.NORMAL
        assert not mgr.is_agent_degradation_blocked("agent-dirty")
        assert not mgr.is_blocked


class TestSingleton:
    def test_get_manager_returns_instance(self):
        m1 = get_engine_degradation_manager()
        m2 = get_engine_degradation_manager()
        assert m1 is m2
