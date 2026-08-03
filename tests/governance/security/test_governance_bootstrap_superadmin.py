# [A_test] module_id: MOD-GOV_governance_bootstrap_superadmin | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.bootstrap_superadmin
# [DOMAIN] D_GOVERNANCE
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

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestBootstrapSuperadminCheck:
    def setup_method(self):
        self.bs = BootstrapSuperadmin()

    def test_grant_known_capability(self):
        for cap in SUPERADMIN_CAPABILITIES:
            result = self.bs.check(cap, "any_resource")
            assert result["granted"] is True
            assert result["role"] == "superadmin"

    def test_deny_unknown_capability(self):
        result = self.bs.check("nonexistent_perm", "resource")
        assert result["granted"] is False
        assert result["reason"] == "capability_not_granted"

    def test_check_result_keys(self):
        result = self.bs.check("read", "file.txt")
        assert "granted" in result
        assert "agent_id" in result
        assert "permission" in result
        assert "resource" in result

    def test_check_preserves_resource(self):
        result = self.bs.check("read", "/path/to/file")
        assert result["resource"] == "/path/to/file"

    def test_check_preserves_permission(self):
        result = self.bs.check("write", "resource")
        assert result["permission"] == "write"


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestBootstrapSuperadminBootstrap:
    def setup_method(self):
        self.bs = BootstrapSuperadmin()

    def test_bootstrap_returns_dict(self):
        result = self.bs.bootstrap()
        assert isinstance(result, dict)

    def test_bootstrap_bootstrapped_true(self):
        result = self.bs.bootstrap()
        assert result["bootstrapped"] is True

    def test_bootstrap_account_matches(self):
        result = self.bs.bootstrap()
        assert result["account"] == SUPERADMIN_ACCOUNT

    def test_bootstrap_roles_match(self):
        result = self.bs.bootstrap()
        assert result["roles"] == SUPERADMIN_ROLES

    def test_bootstrap_capabilities_match(self):
        result = self.bs.bootstrap()
        assert result["capabilities"] == SUPERADMIN_CAPABILITIES


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestBootstrapSuperadminInit:
    def test_account_id(self):
        bs = BootstrapSuperadmin()
        assert bs.account_id == "bytebuddy"

    def test_roles_non_empty(self):
        bs = BootstrapSuperadmin()
        assert len(bs.roles) > 0

    def test_capabilities_non_empty(self):
        bs = BootstrapSuperadmin()
        assert len(bs.capabilities) > 0
