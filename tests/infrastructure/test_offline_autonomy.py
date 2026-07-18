# [A_test] module_id: SRC-TST-1327 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-412 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_offline_autonomy
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.offline_autonomy import AutonomyState, OfflineMode


class TestOfflineMode:
    def test_enum_values(self):
        assert OfflineMode.AUTO == "AUTO"
        assert OfflineMode.SEMIAUTO_MANUAL == "SEMIAUTO_MANUAL"
        assert OfflineMode.ONLINE == "ONLINE"

    def test_enum_members_count(self):
        assert len(OfflineMode) == 3


class TestAutonomyState:
    def test_initial_mode_is_online(self):
        state = AutonomyState()
        assert state.mode == OfflineMode.ONLINE

    def test_transition_to_auto_on_disconnect(self):
        state = AutonomyState()
        result = state.transition(connected=False)
        assert result == OfflineMode.AUTO
        assert state.mode == OfflineMode.AUTO

    def test_transition_stays_online_on_connect(self):
        state = AutonomyState()
        state.transition(connected=False)
        result = state.transition(connected=True)
        assert result == OfflineMode.ONLINE
        assert state.mode == OfflineMode.ONLINE

    def test_transition_auto_to_auto_on_disconnect(self):
        state = AutonomyState()
        state.transition(connected=False)
        result = state.transition(connected=False)
        assert result == OfflineMode.AUTO

    def test_cache_command(self):
        state = AutonomyState()
        state.cache_command("deploy")
        assert state.has_cached_commands() is True

    def test_no_cached_commands_initially(self):
        state = AutonomyState()
        assert state.has_cached_commands() is False

    def test_cache_cleared_on_reconnect(self):
        state = AutonomyState()
        state.transition(connected=False)
        state.cache_command("deploy")
        state.transition(connected=True)
        assert state.has_cached_commands() is False

    def test_multiple_cached_commands(self):
        state = AutonomyState()
        state.transition(connected=False)
        state.cache_command("cmd1")
        state.cache_command("cmd2")
        state.cache_command("cmd3")
        assert state.has_cached_commands() is True
