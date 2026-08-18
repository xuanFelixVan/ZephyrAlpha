# [A_test] module_id: MOD-GOV_integration_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""集成 + 契约验证测试."""

from __future__ import annotations

from zephyr.security.access_control.integration import IntegrationManager
from zephyr.security.access_control.verifiers.contract_verifier import ContractVerifier


class TestIntegration:
    def test_register_all_systems(self):
        mgr = IntegrationManager()
        integrations = mgr.register_all()
        assert len(integrations) == 17

    def test_health_check(self):
        mgr = IntegrationManager()
        mgr.register_all()
        status = mgr.health_check()
        assert status["total_systems"] == 17

    def test_verify_contracts(self):
        mgr = IntegrationManager()
        mgr.register_all()
        contracts = mgr.verify_contracts()
        assert all(contracts.values())


class TestContractVerification:
    def test_verify_all_contracts(self):
        verifier = ContractVerifier()
        results = verifier.verify_all()
        assert len(results) == 4
        for c in ["G-CT-001", "G-CT-004", "G-CT-007", "G-CT-008"]:
            assert c in results

    def test_gct001_identity_contract(self):
        verifier = ContractVerifier()
        identity = type("Identity", (), {"agent_id": "test", "maturity": "MATURE"})()
        result = verifier.verify_gct001(identity)
        assert result.compliant is True

    def test_gct004_decision_contract(self):
        verifier = ContractVerifier()
        decision = type("Decision", (), {"blocked_layer": "L2", "rule_id": "rule_01"})()
        result = verifier.verify_gct004(decision)
        assert result.compliant is True
