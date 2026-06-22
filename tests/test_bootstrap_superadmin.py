# [A_test] module_id: SRC-TST-0448 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.bootstrap_superadmin
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
    from zephyr.security.access_control.bootstrap_superadmin import (
        SUPERADMIN_ACCOUNT,
        SUPERADMIN_CAPABILITIES,
        SUPERADMIN_ROLES,
        BootstrapSuperadmin,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestBootstrapSuperadminInit:
    def test_default_account_id(self):
        obj = BootstrapSuperadmin()
        assert obj.account_id == SUPERADMIN_ACCOUNT

    def test_default_roles(self):
        obj = BootstrapSuperadmin()
        assert obj.roles == SUPERADMIN_ROLES

    def test_default_capabilities(self):
        obj = BootstrapSuperadmin()
        assert obj.capabilities == SUPERADMIN_CAPABILITIES

    def test_roles_is_list(self):
        obj = BootstrapSuperadmin()
        assert isinstance(obj.roles, list)

    def test_capabilities_is_list(self):
        obj = BootstrapSuperadmin()
        assert isinstance(obj.capabilities, list)


class TestBootstrapSuperadminCheck:
    def test_check_granted_capability(self):
        obj = BootstrapSuperadmin()
        result = obj.check("read", "/data/file")
        assert result["granted"] is True
        assert result["permission"] == "read"
        assert result["resource"] == "/data/file"
        assert result["role"] == "superadmin"

    def test_check_denied_capability(self):
        obj = BootstrapSuperadmin()
        result = obj.check("nuke", "/system")
        assert result["granted"] is False
        assert result["reason"] == "capability_not_granted"

    def test_check_empty_permission(self):
        obj = BootstrapSuperadmin()
        result = obj.check("", "/any")
        assert result["granted"] is False

    def test_check_each_capability(self):
        obj = BootstrapSuperadmin()
        for cap in SUPERADMIN_CAPABILITIES:
            result = obj.check(cap, "/res")
            assert result["granted"] is True

    def test_check_returns_agent_id(self):
        obj = BootstrapSuperadmin()
        result = obj.check("read", "/x")
        assert result["agent_id"] == SUPERADMIN_ACCOUNT


class TestBootstrapSuperadminBootstrap:
    def test_bootstrap_returns_true(self):
        obj = BootstrapSuperadmin()
        result = obj.bootstrap()
        assert result["bootstrapped"] is True

    def test_bootstrap_contains_roles(self):
        obj = BootstrapSuperadmin()
        result = obj.bootstrap()
        assert result["roles"] == SUPERADMIN_ROLES

    def test_bootstrap_contains_capabilities(self):
        obj = BootstrapSuperadmin()
        result = obj.bootstrap()
        assert result["capabilities"] == SUPERADMIN_CAPABILITIES

    def test_bootstrap_contains_account(self):
        obj = BootstrapSuperadmin()
        result = obj.bootstrap()
        assert result["account"] == SUPERADMIN_ACCOUNT
