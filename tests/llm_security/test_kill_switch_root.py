# [A_test] module_id: SRC-TST-1187 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.kill_switch
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


from zephyr.security.access_control.kill_switch import (
    DEFAULT_TRIGGERS,
    KillSwitch,
    KillSwitchState,
    KillSwitchStatus,
    TriggerDefinition,
    TriggerEvent,
    TriggerResult,
    get_kill_switch,
)


class TestKillSwitchState:
    def test_enum_values(self):
        assert KillSwitchState.NORMAL.value == "normal"
        assert KillSwitchState.SINGLE_AGENT_TRIPPED.value == "single_agent_tripped"
        assert KillSwitchState.GLOBAL_TRIPPED.value == "global_tripped"
        assert KillSwitchState.COOLDOWN.value == "cooldown"

    def test_enum_members(self):
        members = list(KillSwitchState)
        assert len(members) == 4


class TestTriggerResult:
    def test_enum_values(self):
        assert TriggerResult.NO_ACTION.value == "no_action"
        assert TriggerResult.WARNING.value == "warning"
        assert TriggerResult.BLOCK_AGENT.value == "block_agent"
        assert TriggerResult.GLOBAL_BLOCK.value == "global_block"

    def test_enum_members(self):
        members = list(TriggerResult)
        assert len(members) == 4


class TestTriggerDefinition:
    def test_creation(self):
        td = TriggerDefinition(
            trigger="test_trigger",
            description="test desc",
            default_threshold=5,
            window_seconds=60.0,
            cooldown_seconds=30.0,
            auto_release=True,
        )
        assert td.trigger == "test_trigger"
        assert td.default_threshold == 5
        assert td.auto_release is True

    def test_default_fields(self):
        td = TriggerDefinition(
            trigger="t",
            description="d",
            default_threshold=1,
            window_seconds=1.0,
            cooldown_seconds=1.0,
            auto_release=False,
        )
        assert td.trigger == "t"
        assert td.auto_release is False


class TestTriggerEvent:
    def test_creation_with_defaults(self):
        event = TriggerEvent(trigger="test", agent_id="agent-1")
        assert event.trigger == "test"
        assert event.agent_id == "agent-1"
        assert event.timestamp > 0
        assert event.context == {}

    def test_creation_with_explicit_values(self):
        event = TriggerEvent(
            trigger="t",
            agent_id="a",
            timestamp=1000.0,
            context={"key": "val"},
        )
        assert event.timestamp == 1000.0
        assert event.context == {"key": "val"}


class TestKillSwitchStatus:
    def test_defaults(self):
        status = KillSwitchStatus()
        assert status.state == KillSwitchState.NORMAL
        assert status.tripped_triggers == []
        assert status.tripped_agents == set()
        assert status.tripped_at == 0.0
        assert status.cooldown_until == 0.0
        assert status.global_tripped is False
        assert status.owner_override is False

    def test_custom_values(self):
        status = KillSwitchStatus(
            state=KillSwitchState.GLOBAL_TRIPPED,
            global_tripped=True,
        )
        assert status.state == KillSwitchState.GLOBAL_TRIPPED
        assert status.global_tripped is True


class TestKillSwitch:
    def test_init_default_triggers(self):
        ks = KillSwitch()
        assert ks.trigger_count == 13
        assert len(ks.triggers) == 13

    def test_init_custom_triggers(self):
        custom = [
            TriggerDefinition(
                trigger="custom",
                description="custom trigger",
                default_threshold=1,
                window_seconds=10.0,
                cooldown_seconds=5.0,
                auto_release=True,
            )
        ]
        ks = KillSwitch(triggers=custom)
        assert ks.trigger_count == 1
        assert ks.triggers[0].trigger == "custom"

    def test_initial_status(self):
        ks = KillSwitch()
        assert ks.status.state == KillSwitchState.NORMAL
        assert ks.status.global_tripped is False
        assert ks.status.owner_override is False

    def test_is_global_tripped_initially_false(self):
        ks = KillSwitch()
        assert ks.is_global_tripped() is False

    def test_is_agent_blocked_initially_false(self):
        ks = KillSwitch()
        assert ks.is_agent_blocked("agent-1") is False

    def test_record_event_unknown_trigger(self):
        ks = KillSwitch()
        event = TriggerEvent(trigger="nonexistent", agent_id="agent-1")
        result = ks.record_event(event)
        assert result == TriggerResult.NO_ACTION

    def test_record_event_below_threshold_returns_warning(self):
        ks = KillSwitch(
            triggers=[
                TriggerDefinition(
                    trigger="rapid_file_deletion",
                    description="test",
                    default_threshold=3,
                    window_seconds=60.0,
                    cooldown_seconds=30.0,
                    auto_release=True,
                )
            ]
        )
        event = TriggerEvent(trigger="rapid_file_deletion", agent_id="agent-1")
        result = ks.record_event(event)
        assert result == TriggerResult.WARNING

    def test_record_event_at_threshold_blocks_agent(self):
        ks = KillSwitch(
            triggers=[
                TriggerDefinition(
                    trigger="rapid_file_deletion",
                    description="test",
                    default_threshold=3,
                    window_seconds=60.0,
                    cooldown_seconds=30.0,
                    auto_release=True,
                )
            ]
        )
        for _ in range(3):
            event = TriggerEvent(trigger="rapid_file_deletion", agent_id="agent-1")
            ks.record_event(event)
        assert ks.is_agent_blocked("agent-1") is True
        assert "agent-1" in ks.status.tripped_agents

    def test_manual_trip_global(self):
        ks = KillSwitch()
        ks.manual_trip_global(reason="test emergency")
        assert ks.is_global_tripped() is True
        assert ks.status.state == KillSwitchState.GLOBAL_TRIPPED
        assert ks.status.global_tripped is True
        assert any("manual" in t for t in ks.status.tripped_triggers)

    def test_manual_trip_agent(self):
        ks = KillSwitch()
        ks.manual_trip_agent("agent-1")
        assert ks.is_agent_blocked("agent-1") is True
        assert "agent-1" in ks.status.tripped_agents

    def test_owner_release_global(self):
        ks = KillSwitch()
        ks.manual_trip_global()
        assert ks.is_global_tripped() is True
        ks.owner_release_global()
        assert ks.is_global_tripped() is False
        assert ks.status.owner_override is True
        assert ks.status.state == KillSwitchState.NORMAL

    def test_owner_release_agent(self):
        ks = KillSwitch()
        ks.manual_trip_agent("agent-1")
        assert ks.is_agent_blocked("agent-1") is True
        ks.owner_release_agent("agent-1")
        assert ks.is_agent_blocked("agent-1") is False

    def test_owner_revoke_override(self):
        ks = KillSwitch()
        ks.manual_trip_global()
        ks.owner_release_global()
        assert ks.status.owner_override is True
        ks.owner_revoke_override()
        assert ks.status.owner_override is False
        assert ks.status.state == KillSwitchState.GLOBAL_TRIPPED

    def test_reset(self):
        ks = KillSwitch()
        ks.manual_trip_global()
        ks.manual_trip_agent("agent-1")
        ks.reset()
        assert ks.status.state == KillSwitchState.NORMAL
        assert ks.status.global_tripped is False
        assert ks.status.owner_override is False
        assert ks.status.tripped_agents == set()
        assert ks.status.tripped_triggers == []

    def test_is_agent_blocked_when_global_tripped(self):
        ks = KillSwitch()
        ks.manual_trip_global()
        assert ks.is_agent_blocked("any-agent") is True

    def test_is_global_tripped_with_owner_override(self):
        ks = KillSwitch()
        ks.manual_trip_global()
        ks.owner_release_global()
        assert ks.is_global_tripped() is False

    def test_is_agent_blocked_with_owner_override(self):
        ks = KillSwitch()
        ks.manual_trip_agent("agent-1")
        ks.owner_release_global()
        assert ks.is_agent_blocked("agent-1") is False

    def test_manual_trip_global_no_reason(self):
        ks = KillSwitch()
        ks.manual_trip_global()
        assert any("manual" in t for t in ks.status.tripped_triggers)

    def test_multi_agent_triggers_global_block(self):
        ks = KillSwitch(
            triggers=[
                TriggerDefinition(
                    trigger="rapid_file_deletion",
                    description="test",
                    default_threshold=1,
                    window_seconds=60.0,
                    cooldown_seconds=30.0,
                    auto_release=True,
                )
            ]
        )
        for agent_id in ["agent-1", "agent-2", "agent-3"]:
            event = TriggerEvent(trigger="rapid_file_deletion", agent_id=agent_id)
            result = ks.record_event(event)
        assert ks.is_global_tripped() is True

    def test_triggers_property_returns_copy(self):
        ks = KillSwitch()
        t1 = ks.triggers
        t2 = ks.triggers
        assert t1 is not t2

    def test_none_triggers_uses_defaults(self):
        ks = KillSwitch(triggers=None)
        assert ks.trigger_count == 13
        event = TriggerEvent(trigger="anything", agent_id="agent-1")
        assert ks.record_event(event) == TriggerResult.NO_ACTION


class TestGetKillSwitch:
    def test_singleton(self):
        from zephyr.security.access_control import kill_switch as ks_mod

        ks_mod._kill_switch_instance = None
        ks1 = get_kill_switch()
        ks2 = get_kill_switch()
        assert ks1 is ks2
        ks_mod._kill_switch_instance = None

    def test_returns_kill_switch_instance(self):
        from zephyr.security.access_control import kill_switch as ks_mod

        ks_mod._kill_switch_instance = None
        ks = get_kill_switch()
        assert isinstance(ks, KillSwitch)
        ks_mod._kill_switch_instance = None


class TestDefaultTriggers:
    def test_count(self):
        assert len(DEFAULT_TRIGGERS) == 13

    def test_all_have_required_fields(self):
        for td in DEFAULT_TRIGGERS:
            assert td.trigger
            assert td.description
            assert td.default_threshold >= 1
            assert td.window_seconds > 0
            assert td.cooldown_seconds > 0
            assert isinstance(td.auto_release, bool)

    def test_trigger_names_unique(self):
        names = [td.trigger for td in DEFAULT_TRIGGERS]
        assert len(names) == len(set(names))
