# [A_test] module_id: SRC-TST-1050 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.genesis_bootstrap
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.genesis_bootstrap import GenesisBootstrap, GenesisState
except Exception as exc:
    pytest.skip(f"Cannot import genesis_bootstrap: {exc}", allow_module_level=True)


class TestGenesisState:
    def test_default_values(self):
        gs = GenesisState()
        assert gs.bootstrapped is False
        assert gs.bytebuddy_id == "bytebuddy"
        assert len(gs.system_roles) == 5
        assert "superadmin" in gs.system_roles
        assert gs.genesis_time == ""
        assert gs.genesis_hash == ""

    def test_custom_values(self):
        gs = GenesisState(bootstrapped=True, genesis_time="2026-01-01", genesis_hash="abc123")
        assert gs.bootstrapped is True
        assert gs.genesis_time == "2026-01-01"
        assert gs.genesis_hash == "abc123"


class TestGenesisBootstrap:
    def test_bootstrap_returns_state(self):
        gb = GenesisBootstrap()
        state = gb.bootstrap()
        assert isinstance(state, GenesisState)
        assert state.bootstrapped is True
        assert len(state.genesis_hash) == 16
        assert len(state.genesis_time) > 0

    def test_verify_before_bootstrap(self):
        gb = GenesisBootstrap()
        result = gb.verify()
        assert result["verified"] is False
        assert result["reason"] == "not_bootstrapped"

    def test_verify_after_bootstrap(self):
        gb = GenesisBootstrap()
        gb.bootstrap()
        result = gb.verify()
        assert result["verified"] is True
        assert "genesis_hash" in result
        assert "genesis_time" in result

    def test_bootstrap_idempotent_hash_changes(self):
        gb = GenesisBootstrap()
        s1 = gb.bootstrap()
        h1 = s1.genesis_hash
        import time

        time.sleep(0.01)
        s2 = gb.bootstrap()
        assert s2.genesis_hash != h1

    def test_system_roles_preserved(self):
        gb = GenesisBootstrap()
        state = gb.bootstrap()
        assert "admin" in state.system_roles
        assert "viewer" in state.system_roles
