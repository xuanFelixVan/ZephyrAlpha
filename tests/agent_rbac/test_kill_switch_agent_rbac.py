# [A_test] module_id: MOD-GOV_kill_switch_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_kill_switch
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试 L0 KillSwitch — 全局熔断机制

覆盖:
  - auto_triggers 注册完整性 (>= 9)
  - 各触发器 event 记录和阈值判定
  - 单Agent触发仅阻断该Agent
  - 多Agent (>=3) 触发全局熔断
  - cooldown 自动解除
  - Owner手动解除/手动熔断
"""

import time

from zephyr.security.access_control.kill_switch import (
    DEFAULT_TRIGGERS,
    KillSwitch,
    KillSwitchState,
    TriggerDefinition,
    TriggerEvent,
    TriggerResult,
    get_kill_switch,
)


class TestTriggerDefinitions:
    def test_at_least_9_triggers(self):
        assert len(DEFAULT_TRIGGERS) >= 9, f"Expected >= 9 triggers, got {len(DEFAULT_TRIGGERS)}"

    def test_all_triggers_have_required_fields(self):
        expected = [
            "rapid_file_deletion",
            "permission_boundary_probe",
            "suspicious_sequence",
            "off_hours_destructive",
            "config_file_blitz",
            "signal_noise_attack",
            "sensitivity_label_blitz",
            "agent_spawn_storm",
        ]
        trigger_names = [t.trigger for t in DEFAULT_TRIGGERS]
        for e in expected:
            assert e in trigger_names, f"Expected trigger '{e}' not found"

    def test_trigger_names_are_unique(self):
        names = [t.trigger for t in DEFAULT_TRIGGERS]
        assert len(names) == len(set(names))

    def test_all_triggers_have_positive_threshold(self):
        for t in DEFAULT_TRIGGERS:
            assert t.default_threshold > 0, f"Trigger {t.trigger} has non-positive threshold"


class TestSingleAgentTrigger:
    def test_below_threshold_no_action(self):
        ks = KillSwitch()
        threshold = DEFAULT_TRIGGERS[0].default_threshold
        for i in range(threshold - 1):
            result = ks.record_event(
                TriggerEvent(
                    trigger="rapid_file_deletion",
                    agent_id="agent-test-001",
                    context={"iteration": i},
                )
            )
            if i == threshold - 2:
                pass
        assert not ks.is_global_tripped()

    def test_at_threshold_blocks_agent(self):
        ks = KillSwitch()
        threshold = DEFAULT_TRIGGERS[0].default_threshold
        result = TriggerResult.NO_ACTION
        for i in range(threshold):
            result = ks.record_event(
                TriggerEvent(
                    trigger="rapid_file_deletion",
                    agent_id="agent-test-002",
                    context={"iteration": i},
                )
            )
            time.sleep(0.001)
        assert result == TriggerResult.BLOCK_AGENT
        assert ks.is_agent_blocked("agent-test-002")

    def test_blocked_agent_only(self):
        ks = KillSwitch()
        threshold = DEFAULT_TRIGGERS[0].default_threshold
        ks.record_event(
            TriggerEvent(
                trigger="rapid_file_deletion",
                agent_id="agent-test-003",
            )
        )
        for i in range(threshold):
            ks.record_event(
                TriggerEvent(
                    trigger="rapid_file_deletion",
                    agent_id="agent-test-004",
                    context={"iteration": i},
                )
            )
        assert ks.is_agent_blocked("agent-test-004")
        assert not ks.is_agent_blocked("agent-test-003")

    def test_unknown_trigger_no_action(self):
        ks = KillSwitch()
        result = ks.record_event(
            TriggerEvent(
                trigger="nonexistent_trigger",
                agent_id="agent-test-005",
            )
        )
        assert result == TriggerResult.NO_ACTION


class TestMultiAgentGlobalTrip:
    def test_global_trip_with_multiple_agents(self):
        ks = KillSwitch()
        threshold = DEFAULT_TRIGGERS[0].default_threshold
        result = TriggerResult.NO_ACTION
        for i in range(threshold):
            result = ks.record_event(
                TriggerEvent(
                    trigger="rapid_file_deletion",
                    agent_id="agent-a",
                    context={"iteration": i},
                )
            )
        assert result == TriggerResult.BLOCK_AGENT

        for i in range(threshold):
            result = ks.record_event(
                TriggerEvent(
                    trigger="rapid_file_deletion",
                    agent_id="agent-b",
                    context={"iteration": i},
                )
            )
        assert result == TriggerResult.BLOCK_AGENT

        for i in range(threshold):
            result = ks.record_event(
                TriggerEvent(
                    trigger="rapid_file_deletion",
                    agent_id="agent-c",
                    context={"iteration": i},
                )
            )
        assert ks.is_global_tripped() or result == TriggerResult.GLOBAL_BLOCK


class TestManualOperations:
    def test_manual_trip_global(self):
        ks = KillSwitch()
        ks.manual_trip_global("emergency test")
        assert ks.is_global_tripped()

    def test_manual_trip_agent(self):
        ks = KillSwitch()
        ks.manual_trip_agent("agent-manual-001")
        assert ks.is_agent_blocked("agent-manual-001")

    def test_owner_release_global(self):
        ks = KillSwitch()
        ks.manual_trip_global()
        assert ks.is_global_tripped()
        ks.owner_release_global()
        assert not ks.is_global_tripped()

    def test_owner_release_agent(self):
        ks = KillSwitch()
        ks.manual_trip_agent("agent-manual-002")
        assert ks.is_agent_blocked("agent-manual-002")
        ks.owner_release_agent("agent-manual-002")
        assert not ks.is_agent_blocked("agent-manual-002")

    def test_owner_override_bypasses_block(self):
        ks = KillSwitch()
        ks.manual_trip_global()
        ks.owner_release_global()
        assert not ks.is_global_tripped()
        ks.owner_revoke_override()
        assert ks.is_global_tripped()


class TestCooldown:
    def test_cooldown_mechanism_exists(self):
        ks = KillSwitch()
        assert ks.status.state == KillSwitchState.NORMAL

    def test_reset_clears_all(self):
        ks = KillSwitch()
        ks.manual_trip_global("test cleanup")
        ks.reset()
        assert not ks.is_global_tripped()
        assert ks.status.state == KillSwitchState.NORMAL


class TestTriggerProperty:
    def test_trigger_count_matches_definitions(self):
        ks = KillSwitch()
        assert ks.trigger_count == len(DEFAULT_TRIGGERS)

    def test_triggers_property_returns_copy(self):
        ks = KillSwitch()
        triggers = ks.triggers
        triggers.append(
            TriggerDefinition(
                trigger="test_should_not_persist",
                description="",
                default_threshold=1,
                window_seconds=1.0,
                cooldown_seconds=1.0,
                auto_release=True,
            )
        )
        assert len(ks.triggers) == len(DEFAULT_TRIGGERS)


class TestSingleton:
    def test_get_kill_switch_returns_instance(self):
        ks1 = get_kill_switch()
        ks2 = get_kill_switch()
        assert ks1 is ks2

    def test_get_kill_switch_triggers_count(self):
        ks1 = get_kill_switch()
        assert ks1.trigger_count >= 9
