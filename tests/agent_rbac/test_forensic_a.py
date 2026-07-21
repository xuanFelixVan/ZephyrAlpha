# [A_test] module_id: MOD-GOV_forensic_a | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_forensic_a
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""跨切面 B 取证审计 A 层——genesis/asymmetric/non-repudiation 测试."""

from __future__ import annotations

from zephyr.security.access_control.asymmetric_audit import AsymmetricAudit
from zephyr.security.access_control.genesis_bootstrap import GenesisBootstrap
from zephyr.security.access_control.non_repudiation import NonRepudiation


class TestForensicA:
    def test_genesis_bootstrap(self):
        genesis = GenesisBootstrap()
        state = genesis.bootstrap()
        assert state.bootstrapped is True
        assert state.bytebuddy_id == "bytebuddy"
        assert "superadmin" in state.system_roles

    def test_genesis_verify_before_bootstrap(self):
        genesis = GenesisBootstrap()
        result = genesis.verify()
        assert result["verified"] is False

    def test_asymmetric_audit_quorum(self):
        audit = AsymmetricAudit()
        audit.require_quorum("delete_database", required_approvers=2)

        r1 = audit.approve("delete_database", "admin_1")
        assert r1["approved"] is False

        r2 = audit.approve("delete_database", "admin_2")
        assert r2["approved"] is True

    def test_asymmetric_audit_duplicate(self):
        audit = AsymmetricAudit()
        audit.require_quorum("danger_op", required_approvers=2)
        audit.approve("danger_op", "admin_1")
        r = audit.approve("danger_op", "admin_1")
        assert r["approved"] is False

    def test_non_repudiation_sign_and_verify(self):
        nr = NonRepudiation()
        entry = nr.sign("create_agent", "bytebuddy")
        result = nr.verify(entry)
        assert result["verified"] is True

    def test_non_repudiation_tampered_fails(self):
        nr = NonRepudiation()
        entry = nr.sign("create_agent", "bytebuddy")
        entry.operation = "delete_agent"
        result = nr.verify(entry)
        assert result["verified"] is False
